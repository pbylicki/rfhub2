# from pathlib import Path
import robot.libraries
from robot.errors import DataError
from robot.libdocpkg import LibraryDocumentation
from requests import session, post
from rfhub2.config import APP_INTERFACE, APP_PORT, BASIC_AUTH_USER, BASIC_AUTH_PASSWORD
import os
import re

RESOURCE_PATTERNS = {".robot", ".txt", ".tsv", ".resource"}
ALL_PATTERNS = (RESOURCE_PATTERNS | {".xml", ".py"})
PROTOCOL = 'http://'
API_V1 = 'api/v1'


class LibraryPopulation(object):

    def __init__(self, paths, no_installed_keywords):
        self.paths = paths
        self.auth = (BASIC_AUTH_USER, BASIC_AUTH_PASSWORD)
        self.no_installed_keywords = no_installed_keywords

    def add_collections(self) -> None:
        """
        Traverses through paths and adds libraries to rfhub.
        :return:
        """

        def traverse_paths(path):
            for item in os.listdir(path):
                full_path = os.path.join(path, item)
                if os.path.isdir(full_path):
                    if self._is_library_with_init(full_path):
                        self.add(full_path)
                    else:
                        traverse_paths(full_path)
                elif os.path.isfile(full_path) and self._is_robot_file(full_path):
                    self.add(full_path)

        for path in self.paths:
            traverse_paths(path)
        if not self.no_installed_keywords:
            libdir = os.path.dirname(robot.libraries.__file__)
            for item in os.listdir(libdir):
                if not self._should_ignore(item):
                    self.add(os.path.join(libdir, item))

    def add(self, path) -> None:
        """
        Adds library with keywords to rfhub.
        :return:
        """

        def _serialise_libdoc() -> None:
            """
            Serialises libdoc object to dict object.
            :param libdoc: libdoc input object
            :param path: library path
            :return: json object with parameters needed for request post method
            """

            def _libdoc_to_dict():
                lib_dict = libdoc.__dict__
                lib_dict['doc_format'] = lib_dict.pop('_setter__doc_format')
                for key in ('_setter__keywords', 'inits', 'named_args'):
                    lib_dict.pop(key)
                return lib_dict

            lib_dict = _libdoc_to_dict()
            lib_dict['path'] = path
            return lib_dict

        def _serialise_keywords():
            keywords = [keyword.__dict__ for keyword in libdoc.keywords]
            for keyword in keywords:
                keyword.pop('tags')
                if keyword["args"]:
                    keyword["args"] = str([str(item) for item in keyword["args"]]).replace("\'", "\"")
                else:
                    keyword["args"] = ""
            return keywords

        libdoc = LibraryDocumentation(path)
        serialised_keywords = _serialise_keywords()
        serialised_libdoc = _serialise_libdoc()
        s = session()
        coll_req = self._post_request(s, 'collections', serialised_libdoc)
        if coll_req.status_code == 201:
            print(f'{libdoc.name} library was loaded.')
            for keyword in serialised_keywords:
                collection_id = coll_req.json()["id"]
                keyword["collection_id"] = collection_id
                kwd_req = self._post_request(s, 'keywords', keyword)
        else:
            print(f'{libdoc.name} library was not loaded.')

    @staticmethod
    def _is_library_with_init(path) -> bool:
        return os.path.isfile(os.path.join(path, '__init__.py')) and \
            len(LibraryDocumentation(path).keywords) > 0

    def _is_robot_file(self, file) -> bool:
        return self._is_library_file(file) or \
               self._is_libdoc_file(file) or \
               self._is_resource_file(file)

    @staticmethod
    def _is_library_file(file) -> bool:
        return file.endswith(".py") and not file.endswith("__init__.py")

    @staticmethod
    def _is_libdoc_file(file) -> bool:
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
    def _should_ignore(name) -> bool:
        """Return True if a given library name should be ignored
        This is necessary because not all files we find in the library
        folder are libraries. I wish there was a public robot API
        for "give me a list of installed libraries"...
        """
        filename, _ = os.path.splitext(name)
        _name = filename.lower()
        return (_name.startswith("deprecated") or
                _name.startswith("_") or
                _name in ("remote", "reserved", "dialogs", "dialogs_jy", "dialogs_py", "dialogs_ipy"))

    @staticmethod
    def _is_resource_file(file) -> bool:
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

    def _post_request(self, session, endpoint, data):
        """
        Posts request to collections or keywords endpoint
        """
        request = session.post(url=f'{PROTOCOL}{APP_INTERFACE}:{APP_PORT}/{API_V1}/{endpoint}/',
                           auth=self.auth, json=data,
                           headers={"Content-Type": "application/json", "accept": "application/json"})
        return request
