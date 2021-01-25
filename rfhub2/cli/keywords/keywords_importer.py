from pathlib import Path
from typing import Dict, List, Set, Tuple

from rfhub2.cli.api_client import Client
from rfhub2.cli.keywords.keywords_extractor import (
    CollectionUpdateWithKeywords,
    KeywordsExtractor,
)
from rfhub2.model import (
    Collection,
    CollectionUpdate,
    KeywordCreate,
    KeywordUpdate,
    NestedKeyword,
)


class KeywordsImporter:
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
        keywords_extractor = KeywordsExtractor(self.paths, self.no_installed_keywords)
        libraries_paths = keywords_extractor.get_libraries_paths()
        collections = keywords_extractor.create_collections(libraries_paths)
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
            if self.load_mode == "merge":
                self.delete_outdated_collections(
                    existing_collections, collections, remove_not_matched=False
                )
            else:
                self.delete_outdated_collections(existing_collections, collections)
        return len(loaded_collections), sum(d["keywords"] for d in loaded_collections)

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
        remove_not_matched: bool = True,
    ) -> Set[int]:
        """Deletes outdated collections
        :param existing_collections: List of existing collections
        :param new_collections: List of new collections
        :param remove_not_matched: removes not_matched collection paths as well
        :return Set of deleted collections_id
        """
        collections_to_delete = self._get_outdated_collections_ids(
            existing_collections, new_collections
        )
        if remove_not_matched:
            collections_to_delete |= self._get_obsolete_collections_ids(
                existing_collections, new_collections
            )
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
