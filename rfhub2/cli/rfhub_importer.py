import os
import re
from robot.libdocpkg import LibraryDocumentation
import robot.libraries
from typing import Tuple, Dict, List

from .api_client import Client
from rfhub2.model import Collection, Keyword


RESOURCE_PATTERNS = {".robot", ".txt", ".tsv", ".resource"}
ALL_PATTERNS = (RESOURCE_PATTERNS | {".xml", ".py"})
EXCLUDED_LIBRARIES = {"remote", "reserved", "dialogs", "dialogs_jy", "dialogs_py", "dialogs_ipy"}


class RfhubImporter(object):

    def __init__(self, paths: Tuple[str, ...], no_installed_keywords: bool, client: Client) -> None:
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
            self._traverse_paths(path)
        if not self.no_installed_keywords:
            libdir = os.path.dirname(robot.libraries.__file__)
            for item in os.listdir(libdir):
                if not self._should_ignore(item):
                    self.add(os.path.join(libdir, item))

    def _traverse_paths(self, path: str) -> None:
        """
        Traverses through paths and adds libraries to rfhub.
        Helper function for add_collections.
        """
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                if self._is_library_with_init(full_path):
                    self.add(full_path)
                else:
                    self._traverse_paths(full_path)
            elif os.path.isfile(full_path) and self._is_robot_keyword_file(full_path):
                self.add(full_path)

    def add(self, path: str) -> None:
        """
        Adds library with keywords to rfhub.
        """

        libdoc = LibraryDocumentation(path)
        serialised_keywords = self._serialise_keywords(libdoc)
        serialised_libdoc = self._serialise_libdoc(libdoc, path)
        coll_req = self.client.add_collection(serialised_libdoc)
        if coll_req['name'] == serialised_libdoc['name']:
            collection_id = coll_req['id']
            for keyword in serialised_keywords:
                keyword['collection_id'] = collection_id
                self.client.add_keyword(keyword)
            print(f'{libdoc.name} library with {len(serialised_keywords)} keywords loaded.')
        else:
            print(f'{libdoc.name} library was not loaded!')

    def _serialise_libdoc(self, libdoc, path: str) -> Collection:
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

    def _serialise_keywords(self, libdoc) -> Keyword:
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
    def _is_library_with_init(path: str) -> bool:
        return os.path.isfile(os.path.join(path, '__init__.py')) and \
            len(LibraryDocumentation(path).keywords) > 0

    def _is_robot_keyword_file(self, file: str) -> bool:
        return self._is_library_file(file) or \
               self._is_libdoc_file(file) or \
               self._is_resource_file(file)

    @staticmethod
    def _is_library_file(file: str) -> bool:
        return file.endswith(".py") and not file.endswith("__init__.py")

    @staticmethod
    def _is_libdoc_file(file: str) -> bool:
        """Return true if an xml file looks like a libdoc file"""
        # inefficient since we end up reading the file twice,
        # but it's fast enough for our purposes, and prevents
        # us from doing a full parse of files that are obviously
        # not libdoc files
        if file.lower().endswith(".xml"):
            with open(file, "r") as f:
                # read the first few lines; if we don't see
                # what looks like libdoc data, return false
                data = f.read(200)
                index = data.lower().find("<keywordspec ")
                if index > 0:
                    return True
        return False

    @staticmethod
    def _should_ignore(file: str) -> bool:
        """Return True if a given library name should be ignored
        This is necessary because not all files we find in the library
        folder are libraries.
        """
        filename = os.path.splitext(file)[0].lower()
        return (filename.startswith("deprecated") or
                filename.startswith("_") or
                filename in EXCLUDED_LIBRARIES)

    @staticmethod
    def _is_resource_file(file: str) -> bool:
        """Return true if the file has a keyword table but not a testcase table"""
        # inefficient since we end up reading the file twice,
        # but it's fast enough for our purposes, and prevents
        # us from doing a full parse of files that are obviously
        # not robot files

        if re.search(r'__init__.(txt|robot|html|tsv)$', file):
            # These are initialize files, not resource files
            return False

        found_keyword_table = False
        if os.path.splitext(file)[1].lower() in RESOURCE_PATTERNS:
            with open(file, "r") as f:
                data = f.read()
                for match in re.finditer(r'^\*+\s*(Test Cases?|(?:User )?Keywords?)',
                                         data, re.MULTILINE | re.IGNORECASE):
                    if re.match(r'Test Cases?', match.group(1), re.IGNORECASE):
                        # if there's a test case table, it's not a keyword file
                        return False

                    if (not found_keyword_table and
                            re.match(r'(User )?Keywords?', match.group(1), re.IGNORECASE)):
                        found_keyword_table = True
        return found_keyword_table
