from dataclasses import dataclass
from pathlib import Path
import re
from robot.errors import DataError
from robot.libdocpkg import LibraryDocumentation
from robot.libdocpkg.model import LibraryDoc
import robot.libraries
from robot.model import Tags
from typing import Dict, List, Set, Tuple

from .api_client import Client
from rfhub2.model import (
    Collection,
    CollectionUpdate,
    KeywordCreate,
    KeywordUpdate,
    NestedKeyword,
)


RESOURCE_PATTERNS = {".robot", ".txt", ".tsv", ".resource"}
ALL_PATTERNS = RESOURCE_PATTERNS | {".xml", ".py"}
EXCLUDED_LIBRARIES = {
    "remote.py",
    "reserved.py",
    "dialogs.py",
    "dialogs_jy.py",
    "dialogs_py.py",
    "dialogs_ipy.py",
    "setup.py",
}
INIT_FILES = {"__init__.txt", "__init__.robot", "__init__.html", "__init__.tsv"}


@dataclass
class CollectionUpdateWithKeywords:
    collection: CollectionUpdate
    keywords: List[KeywordUpdate]


class KeywordsImporter(object):
    def __init__(
        self,
        client: Client,
        paths: Tuple[Path, ...],
        no_installed_keywords: bool,
        load_mode: str,
    ) -> None:
        self.client = client
        self.paths = paths
        self.no_installed_keywords = no_installed_keywords
        self.load_mode = load_mode

    def delete_all_collections(self) -> Set[int]:
        """
        Deletes all existing collections.
        """
        collections_id = set()
        while len(self.client.get_collections()) > 0:
            collections_id.update(self._delete_collections())
        return collections_id

    def get_all_collections(self) -> List[Collection]:
        """Gets all collections from application"""
        collections = self.client.get_collections(0, 999999)
        return self._convert_json_to_collection(collections)

    def _delete_collections(self) -> Set[int]:
        """
        Helper method to delete all existing callections.
        """
        collections = self.client.get_collections()
        collections_id = {collection["id"] for collection in collections}
        for id in collections_id:
            self.client.delete_collection(id)
        return collections_id

    def import_data(self) -> Tuple[int, int]:
        """
        Wrapper for import_libraries and import_statistics to unify modules.
        :return: Number of libraries and keyword loaded
        """
        return self.import_libraries()

    def import_libraries(self) -> Tuple[int, int]:
        """
        Import libraries to application from paths specified when invoking client.
        :return: Number of libraries and keywords loaded
        """
        libraries_paths = self.get_libraries_paths()
        collections = self.create_collections(libraries_paths)
        if self.load_mode == "append":
            loaded_collections = self.add_collections(collections)
        elif self.load_mode == "insert":
            self.delete_all_collections()
            loaded_collections = self.add_collections(collections)
        else:
            existing_collections = self.get_all_collections()
            loaded_collections = self.update_collections(
                existing_collections, collections
            )
            self.delete_outdated_collections(existing_collections, collections)
        return len(loaded_collections), sum(d["keywords"] for d in loaded_collections)

    def get_libraries_paths(self) -> Set[Path]:
        """
        Traverses all given paths and returns set with paths
        pointing to libraries to import to app.
        :return: Set of Paths object pointing to libraries to import
        """
        libraries_paths = set()
        for path in self.paths:
            libraries_paths.update(self._traverse_paths(Path(path)))
        if not self.no_installed_keywords:
            libdir = Path(robot.libraries.__file__).parent
            libraries_paths.update(self._traverse_paths(Path(libdir)))
        return libraries_paths

    def _traverse_paths(self, path: Path) -> Set[Path]:
        """
        Traverses through paths and adds libraries to rfhub.
        Helper function for get_library_paths.
        """
        valid_lib_paths = set()
        if self._is_library_with_init(path):
            valid_lib_paths.add(path)
        else:
            for item in path.iterdir():
                if item.is_dir():
                    if self._is_library_with_init(item):
                        valid_lib_paths.add(item)
                        if self._robot_files_candidates(item):
                            valid_lib_paths.update(self._get_valid_robot_files(path))
                    else:
                        valid_lib_paths.update(self._traverse_paths(item))
                elif (
                    item.is_file()
                    and self._is_robot_keyword_file(item)
                    and not self._should_ignore(item)
                ):
                    valid_lib_paths.add(item)
        return valid_lib_paths

    def create_collections(
        self, paths: Set[Path]
    ) -> List[CollectionUpdateWithKeywords]:
        """
        Creates list of Collection objects from set of provided paths.
        :param paths: set of paths
        :return: list of Collection objects
        """
        collections = []
        for path in paths:
            try:
                collection_with_keywords = self.create_collection(path)
                collections.append(collection_with_keywords)
            except (DataError, SystemExit) as ex:
                print(
                    f"Failed to create collection from path {path}\n"
                    f"{type(ex).__name__}, {ex.args}"
                )
        return sorted(collections, key=lambda i: i.collection.name)

    def create_collection(self, path: Path) -> CollectionUpdateWithKeywords:
        """
        Creates CollectionUpdateWithKeywords object from provided path.
        :param path: Path
        :return: CollectionUpdateWithKeywords object
        """
        libdoc = LibraryDocumentation(str(path))
        return CollectionUpdateWithKeywords(
            self._serialise_libdoc(libdoc, str(path)), self._serialise_keywords(libdoc)
        )

    def update_collections(
        self,
        existing_collections: List[Collection],
        new_collections: List[CollectionUpdateWithKeywords],
    ) -> List[Dict[str, int]]:
        """
        Updates collections already existing in app.
        :param existing_collections: List of existing collections object
        :param new_collections: List of new collections object
        :return: list of dictionaries with collection name and number of keywords.
        """
        collections_to_update = self._get_collections_to_update(
            existing_collections, new_collections
        )
        collections_to_insert = self._get_new_collections(
            existing_collections, new_collections
        )
        return self.add_collections(collections_to_update + collections_to_insert)

    def delete_outdated_collections(
        self,
        existing_collections: List[Collection],
        new_collections: List[CollectionUpdateWithKeywords],
    ) -> Set[int]:
        """Deletes outdated collections"""
        collections_to_delete = self._get_outdated_collections_ids(
            existing_collections, new_collections
        ) | self._get_obsolete_collections_ids(existing_collections, new_collections)
        for collection in collections_to_delete:
            self.client.delete_collection(collection)
        return collections_to_delete

    def add_collections(
        self, collections: List[CollectionUpdateWithKeywords]
    ) -> List[Dict[str, int]]:
        """
        Adds collections and keywords from provided list to app.
        :param collections: List of collections object
        :return: list of dictionaries with collection name and number of keywords.
        """
        loaded_collections = []
        for collection in collections:
            coll_req = self.client.add_collection(collection.collection)
            if coll_req[0] != 201:
                print(coll_req[1]["detail"])
                raise StopIteration
            collection_id = coll_req[1]["id"]
            for keyword in collection.keywords:
                keyword = KeywordCreate(
                    **{**keyword.dict(), "collection_id": collection_id}
                )
                self.client.add_keyword(keyword)
            loaded_collections.append(
                {
                    "name": collection.collection.name,
                    "keywords": len(collection.keywords),
                }
            )
            print(
                f"{collection.collection.name} library with {len(collection.keywords)} keywords loaded."
            )
        return loaded_collections

    def _serialise_libdoc(self, libdoc: LibraryDoc, path: str) -> CollectionUpdate:
        """
        Serialises LibraryDoc object to CollectionUpdate object.
        :param libdoc: LibraryDoc input object
        :param path: library path
        :return: CollectionUpdate object
        """
        return CollectionUpdate(
            name=libdoc.name,
            type=libdoc.type,
            version=libdoc.version,
            scope=libdoc.scope,
            # named_args=libdoc.named_args, # we have not used this one, yet
            path=path,
            doc=libdoc.doc + self._extract_doc_from_libdoc_inits(libdoc.inits),
            doc_format=libdoc._setter__doc_format,
        )

    def _serialise_keywords(self, libdoc: LibraryDoc) -> List[KeywordUpdate]:
        """
        Serialises keywords to KeywordUpdate object.
        :param :LibraryDoc input object
        :return: KeywordUpdate object
        """
        return [
            KeywordUpdate(
                name=keyword.name,
                args=self._serialise_args(keyword.args),
                tags=self._serialise_tags(keyword.tags),
                doc=keyword.doc,
            )
            for keyword in libdoc.keywords
        ]

    def _serialise_args(self, args: List[str]) -> str:
        return (
            str([str(item).replace("'", "").replace('"', "") for item in args]).replace(
                "'", '"'
            )
            if args
            else ""
        )

    def _serialise_tags(self, tags: Tags) -> List[str]:
        return list(tags._tags)

    def _extract_doc_from_libdoc_inits(self, inits: List) -> str:
        return "\n" + "\n" + "\n".join([d.doc for d in inits]) if len(inits) > 0 else ""

    def _robot_files_candidates(self, path: Path) -> bool:
        return (
            len(
                [file for file in path.glob("**/*") if file.suffix in RESOURCE_PATTERNS]
            )
            > 0
        )

    def _get_valid_robot_files(self, path: Path) -> Set[Path]:
        return {
            file
            for file in path.glob("**/*")
            if (self._is_libdoc_file(file) or self._is_resource_file(file))
        }

    @staticmethod
    def _is_library_with_init(path: Path) -> bool:
        return (path / "__init__.py").is_file() and len(
            LibraryDocumentation(str(path)).keywords
        ) > 0

    def _is_robot_keyword_file(self, file: Path) -> bool:
        return (
            self._is_library_file(file)
            or self._is_libdoc_file(file)
            or self._is_resource_file(file)
        )

    @staticmethod
    def _is_library_file(file: Path) -> bool:
        return file.suffix == ".py" and file.name != "__init__.py"

    @staticmethod
    def _is_libdoc_file(file: Path) -> bool:
        """Return true if an xml file looks like a libdoc file"""
        # inefficient since we end up reading the file twice,
        # but it's fast enough for our purposes, and prevents
        # us from doing a full parse of files that are obviously
        # not libdoc files
        if file.suffix == ".xml":
            with open(file, "r", encoding="utf-8", errors="ignore") as f:
                # read the first few lines; if we don't see
                # what looks like libdoc data, return false
                data = f.read(200)
                return "<keywordspec " in data.lower()
        return False

    @staticmethod
    def _should_ignore(file: Path) -> bool:
        """Return True if a given library name should be ignored
        This is necessary because not all files we find in the library
        folder are libraries.
        """
        filename = file.name.lower()
        return (
            filename.startswith("deprecated")
            or filename.startswith("_")
            or filename in EXCLUDED_LIBRARIES
        )

    @staticmethod
    def _is_resource_file(file: Path) -> bool:
        """Returns true if the file has a keyword table but not a testcase table."""
        # inefficient since we end up reading the file twice,
        # but it's fast enough for our purposes, and prevents
        # us from doing a full parse of files that are obviously
        # not robot files

        if file.name not in INIT_FILES and file.suffix in RESOURCE_PATTERNS:
            with open(file, "r", encoding="utf-8", errors="ignore") as f:
                data = f.read()
                return not KeywordsImporter._has_test_case_table(
                    data
                ) and KeywordsImporter._has_keyword_table(data)
        return False

    @staticmethod
    def _has_keyword_table(data: str) -> bool:
        """Returns true if file has keyword or user keyword table"""
        return (
            re.search(
                r"^\*+\s*((?:User )?Keywords?)", data, re.MULTILINE | re.IGNORECASE
            )
            is not None
        )

    @staticmethod
    def _has_test_case_table(data: str) -> bool:
        """Returns true if file has keyword or user keyword table"""
        return (
            re.search(r"^\*+\s*(Test Cases?)", data, re.MULTILINE | re.IGNORECASE)
            is not None
        )

    @staticmethod
    def _get_obsolete_collections_ids(
        existing_collections: List[Collection],
        new_collections: List[CollectionUpdateWithKeywords],
    ) -> Set[int]:
        """Returns set of collection ids that were found in application but not in paths"""
        new_collections_paths = {
            new_collection.collection.path for new_collection in new_collections
        }
        return {
            existing_collection.id
            for existing_collection in existing_collections
            if existing_collection.path not in new_collections_paths
        }

    @staticmethod
    def _get_outdated_collections_ids(
        existing_collections: List[Collection],
        new_collections: List[CollectionUpdateWithKeywords],
    ) -> Set[int]:
        """Returns set of collection ids that were found in application but are outdated"""
        outdated_collections = set()
        if len(existing_collections) > 0:
            for new_collection in new_collections:
                for existing_collection in existing_collections:
                    if KeywordsImporter._collection_path_and_name_match(
                        new_collection.collection, existing_collection
                    ) and KeywordsImporter._library_or_resource_changed(
                        new_collection, existing_collection
                    ):
                        outdated_collections.add(existing_collection.id)
        return outdated_collections

    @staticmethod
    def _get_collections_to_update(
        existing_collections: List[Collection],
        new_collections: List[CollectionUpdateWithKeywords],
    ) -> List[CollectionUpdateWithKeywords]:
        """Returns list of collections to update that were found in paths and application"""
        collections_to_update = []
        if len(existing_collections) >= 0:
            for new_collection in new_collections:
                for existing_collection in existing_collections:
                    if KeywordsImporter._collection_path_and_name_match(
                        new_collection.collection, existing_collection
                    ) and KeywordsImporter._library_or_resource_changed(
                        new_collection, existing_collection
                    ):
                        collections_to_update.append(new_collection)
        return collections_to_update

    @staticmethod
    def _get_new_collections(
        existing_collections: List[Collection],
        new_collections: List[CollectionUpdateWithKeywords],
    ) -> List[CollectionUpdateWithKeywords]:
        """Returns list of collections to insert that were found in paths but not in application"""
        existing_collections_paths = {
            existing_collection.path for existing_collection in existing_collections
        }
        return [
            new_collection
            for new_collection in new_collections
            if new_collection.collection.path not in existing_collections_paths
        ]

    @staticmethod
    def _collection_path_and_name_match(
        new_collection: CollectionUpdate, existing_collection: Collection
    ) -> bool:
        return (
            new_collection.name == existing_collection.name
            and new_collection.path == existing_collection.path
        )

    @staticmethod
    def _library_or_resource_changed(
        new_collection: CollectionUpdateWithKeywords, existing_collection: Collection
    ) -> bool:
        if new_collection.collection.type.lower() == "library":
            return new_collection.collection.version != existing_collection.version
        else:
            return (
                any(
                    keyword not in new_collection.keywords
                    for keyword in KeywordsImporter._convert_keywords_to_keywords_update(
                        existing_collection.keywords
                    )
                )
                or any(
                    keyword
                    not in KeywordsImporter._convert_keywords_to_keywords_update(
                        existing_collection.keywords
                    )
                    for keyword in new_collection.keywords
                )
                or KeywordsImporter._library_or_resource_doc_changed(
                    new_collection.collection, existing_collection
                )
            )

    @staticmethod
    def _convert_keywords_to_keywords_update(
        keywords: List[NestedKeyword]
    ) -> List[KeywordUpdate]:
        """Convert list of Keywords object to List of KeywordUpdate object"""
        return [
            KeywordUpdate(
                name=keyword.name, doc=keyword.doc, args=keyword.args, tags=keyword.tags
            )
            for keyword in keywords
        ]

    @staticmethod
    def _convert_json_to_collection(collections: Dict) -> List[Collection]:
        for collection in collections:
            collection["keywords"] = [
                NestedKeyword(**keyword) for keyword in collection["keywords"]
            ]
        return [Collection(**collection) for collection in collections]

    @staticmethod
    def _library_or_resource_doc_changed(
        new_collection: CollectionUpdate, existing_collection: Collection
    ) -> bool:
        """Returns true if collection overall documentation has changed.
        Does not check for keywords changes"""
        reduced_existing_collection = CollectionUpdate(
            name=existing_collection.name,
            type=existing_collection.type,
            version=existing_collection.version,
            scope=existing_collection.scope,
            args=existing_collection.named_args,
            path=existing_collection.path,
            doc=existing_collection.doc,
            doc_format=existing_collection.doc_format,
        )
        return new_collection != reduced_existing_collection
