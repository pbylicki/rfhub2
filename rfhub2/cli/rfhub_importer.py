from pathlib import Path
import re
from robot.libdocpkg import LibraryDocumentation
import robot.libraries
from typing import Tuple

from .api_client import Client
from rfhub2.model import Collection, Keyword


RESOURCE_PATTERNS = {'.robot', '.txt', '.tsv', '.resource'}
ALL_PATTERNS = (RESOURCE_PATTERNS | {'.xml', '.py'})
EXCLUDED_LIBRARIES = {'remote.py', 'reserved.py', 'dialogs.py', 'dialogs_jy.py', 'dialogs_py.py', 'dialogs_ipy.py'}
INIT_FILES = {'__init__.txt', '__init__.robot', '__init__.html', '__init__.tsv'}


class RfhubImporter(object):

    def __init__(self, paths: Tuple[Path, ...], no_installed_keywords: bool, client: Client) -> None:
        self.paths = paths
        self.no_installed_keywords = no_installed_keywords
        self.client = client

    def delete_collections(self) -> None:
        """
        Deletes all existing collections.
        """
        self.client.check_communication_with_app()
        collections = self.client.get_collections()
        collections_id = {collection['id'] for collection in collections}
        for id in collections_id:
            self.client.delete_collection(id)

    def add_collections(self) -> None:
        """
        Adds collections to rfhub.
        """

        self.client.check_communication_with_app()
        for path in self.paths:
            self._traverse_paths(Path(path))
        if not self.no_installed_keywords:
            libdir = Path(robot.libraries.__file__).parent
            for item in Path.iterdir(libdir):
                if not self._should_ignore(item):
                    self.add(item)

    def _traverse_paths(self, path: Path) -> None:
        """
        Traverses through paths and adds libraries to rfhub.
        Helper function for add_collections.
        """
        for item in path.iterdir():
            if item.is_dir():
                if self._is_library_with_init(item):
                    self.add(item)
                else:
                    self._traverse_paths(item)
            elif item.is_file() and self._is_robot_keyword_file(item):
                self.add(item)

    def add(self, path: Path) -> None:
        """
        Adds library with keywords to rfhub.
        """

        libdoc = LibraryDocumentation(str(path))
        serialised_keywords = self._serialise_keywords(libdoc)
        serialised_libdoc = self._serialise_libdoc(libdoc, str(path))
        coll_req = self.client.add_collection(serialised_libdoc)
        if coll_req['name'] == serialised_libdoc['name']:
            collection_id = coll_req['id']
            for keyword in serialised_keywords:
                keyword['collection_id'] = collection_id
                self.client.add_keyword(keyword)
            print(f'{libdoc.name} library with {len(serialised_keywords)} keywords loaded.')
        else:
            print(f'{libdoc.name} library was not loaded!')

    def _serialise_libdoc(self, libdoc: LibraryDocumentation, path: str) -> Collection:
        """
        Serialises libdoc object to Collection object.
        :param libdoc: libdoc input object
        :param path: library path
        :return: Collection object
        """

        lib_dict = libdoc.__dict__
        lib_dict['doc_format'] = lib_dict.pop('_setter__doc_format')
        for key in ('_setter__keywords', 'inits', 'named_args'):
            lib_dict.pop(key)
        lib_dict['path'] = path
        return lib_dict

    def _serialise_keywords(self, libdoc: LibraryDocumentation) -> Keyword:
        """
        Serialises keywords to Keyword object.
        :param :libdoc input object
        :return: Keyword object
        """

        keywords = [keyword.__dict__ for keyword in libdoc.keywords]
        for keyword in keywords:
            keyword.pop('tags')
            if keyword["args"]:
                keyword["args"] = str([str(item) for item in keyword["args"]]).replace("\'", "\"")
            else:
                keyword["args"] = ""
        return keywords

    @staticmethod
    def _is_library_with_init(path: Path) -> bool:
        return (path / '__init__.py').is_file() and \
           len(LibraryDocumentation(str(path)).keywords) > 0

    def _is_robot_keyword_file(self, file: Path) -> bool:
        return self._is_library_file(file) or \
               self._is_libdoc_file(file) or \
               self._is_resource_file(file)

    @staticmethod
    def _is_library_file(file: Path) -> bool:
        return file.suffix == '.py' and file.name != "__init__.py"

    @staticmethod
    def _is_libdoc_file(file: Path) -> bool:
        """Return true if an xml file looks like a libdoc file"""
        # inefficient since we end up reading the file twice,
        # but it's fast enough for our purposes, and prevents
        # us from doing a full parse of files that are obviously
        # not libdoc files
        if file.suffix == '.xml':
            with open(file, "r") as f:
                # read the first few lines; if we don't see
                # what looks like libdoc data, return false
                data = f.read(200)
                index = data.lower().find("<keywordspec ")
                return index > 0
        return False

    @staticmethod
    def _should_ignore(file: Path) -> bool:
        """Return True if a given library name should be ignored
        This is necessary because not all files we find in the library
        folder are libraries.
        """
        filename = file.name.lower()
        return filename.startswith("deprecated") or \
               filename.startswith("_") or \
               filename in EXCLUDED_LIBRARIES

    @staticmethod
    def _is_resource_file(file: Path) -> bool:
        """Returns true if the file has a keyword table but not a testcase table."""
        # inefficient since we end up reading the file twice,
        # but it's fast enough for our purposes, and prevents
        # us from doing a full parse of files that are obviously
        # not robot files

        if file.name not in INIT_FILES and file.suffix in RESOURCE_PATTERNS:
            with open(file, "r") as f:
                data = f.read()
                return not RfhubImporter._has_test_case_table(data) and \
                    RfhubImporter._has_keyword_table(data)
        return False

    @staticmethod
    def _has_keyword_table(data: str) -> bool:
        """Returns true if file has keyword or user keyword table"""
        return re.search(r'^\*+\s*((?:User )?Keywords?)', data, re.MULTILINE | re.IGNORECASE) is not None

    @staticmethod
    def _has_test_case_table(data: str) -> bool:
        """Returns true if file has keyword or user keyword table"""
        return re.search(r'^\*+\s*(Test Cases?)', data, re.MULTILINE | re.IGNORECASE) is not None
