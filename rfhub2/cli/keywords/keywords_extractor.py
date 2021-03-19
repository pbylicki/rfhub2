from dataclasses import dataclass
from importlib.util import find_spec
from pathlib import Path
import re
from robot.errors import DataError
from robot.libdocpkg import LibraryDocumentation
from robot.libdocpkg.model import LibraryDoc
import robot.libraries
from robot.model import Tags
from typing import List, Optional, Set, Tuple, Union

from rfhub2.model import CollectionUpdate, KeywordUpdate

RESOURCE_PATTERNS = {".robot", ".txt", ".tsv", ".resource"}
ALL_PATTERNS = RESOURCE_PATTERNS | {".xml", ".py"}

INIT_FILES = {"__init__.txt", "__init__.robot", "__init__.html", "__init__.tsv"}

EXCLUDED_LIBRARIES = {
    "remote.py",
    "reserved.py",
    "dialogs.py",
    "dialogs_jy.py",
    "dialogs_py.py",
    "dialogs_ipy.py",
    "setup.py",
}


@dataclass
class CollectionUpdateWithKeywords:
    collection: CollectionUpdate
    keywords: List[KeywordUpdate]


class KeywordsExtractor:
    def __init__(
        self, paths: Tuple[Union[Path, str], ...], no_installed_keywords: bool
    ) -> None:
        self.paths = paths
        self.no_installed_keywords = no_installed_keywords

    def get_libraries_paths(self) -> Set[Path]:
        """
        Traverses all given paths and returns set with paths
        pointing to libraries to import to app.
        :return: Set of Paths object pointing to libraries to import
        """
        libraries_paths = set()
        for path in self.paths:
            path = self.get_library_path_from_name(path)
            if path:
                libraries_paths.update(self._traverse_paths(Path(path)))
        if not self.no_installed_keywords:
            libdir = Path(robot.libraries.__file__).parent
            libraries_paths.update(self._traverse_paths(Path(libdir)))
        return libraries_paths

    def get_library_path_from_name(self, path: Union[Path, str]) -> Optional[str]:
        """
        Helper function to recognize if given value is path or name.
        Name needs to be converted to full path and passed to Libdoc.
        """
        if Path(path).exists():
            return str(path)
        elif isinstance(path, str):
            try:
                return find_spec(path).submodule_search_locations[0]
            except AttributeError as e:
                print(
                    f"Collection {path} was neither valid path nor valid module name."
                )
                return None

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
                return not KeywordsExtractor._has_test_case_table(
                    data
                ) and KeywordsExtractor._has_keyword_table(data)
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
