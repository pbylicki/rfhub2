from typing import Tuple, Dict, List
import robot.libraries
from robot.libdocpkg import LibraryDocumentation
from requests import session, post, get, delete, exceptions
import os
import re

RESOURCE_PATTERNS = {".robot", ".txt", ".tsv", ".resource"}
ALL_PATTERNS = (RESOURCE_PATTERNS | {".xml", ".py"})
EXCLUDED_LIBRARIES = {"remote", "reserved", "dialogs", "dialogs_jy", "dialogs_py", "dialogs_ipy"}
PROTOCOL = 'http://'
API_V1 = 'api/v1'
TEST_COLLECTION = {"name": "a", "type": "a", "version": "a", "scope": "a",
                   "named_args": "a", "path": "a", "doc": "a", "doc_format": "a"}


class AppPopulation(object):

    def __init__(self, app_interface: str, port: str, user: str, password: str,
                 paths: Tuple[str, ...], no_installed_keywords: bool) -> None:
        self.app_interface = app_interface
        self.port = port
        self.paths = paths
        self.auth = (user, password)
        self.no_installed_keywords = no_installed_keywords
        self.session = session()

    def healthcheck_app(self) -> None:
        try:
            self._get_request(None)
        except exceptions.RequestException:
            print(f'Connection to application at {PROTOCOL}{self.app_interface}:{self.port}/ refused!\n'
                  f'Check parameters for app-interace and port.')
            exit(1)
        req_check_auth = self._post_request('collections', TEST_COLLECTION)
        if req_check_auth.status_code == 201:
            self._delete_request('collections', req_check_auth.json()["id"])
        else:
            print(f'{req_check_auth.reason}! Check used credentials.')
            exit(1)

    def delete_collections(self) -> None:
        """
        Deletes all existing collections.
        """
        collections = self._get_request('collections')
        collections_id = {collection['id'] for collection in collections.json()}
        for id in collections_id:
            self._delete_request('collections', id)

    def add_collections(self) -> None:
        """
        Traverses through paths and adds libraries to rfhub.
        """

        def traverse_paths(path: str) -> None:
            for item in os.listdir(path):
                full_path = os.path.join(path, item)
                if os.path.isdir(full_path):
                    if self._is_library_with_init(full_path):
                        self.add(full_path)
                    else:
                        traverse_paths(full_path)
                elif os.path.isfile(full_path) and self._is_robot_keyword_file(full_path):
                    self.add(full_path)

        for path in self.paths:
            traverse_paths(path)
        if not self.no_installed_keywords:
            libdir = os.path.dirname(robot.libraries.__file__)
            for item in os.listdir(libdir):
                if not self._should_ignore(item):
                    self.add(os.path.join(libdir, item))

    def add(self, path: str) -> None:
        """
        Adds library with keywords to rfhub.
        :return:
        """

        def _serialise_libdoc() -> Dict:
            """
            Serialises libdoc object to dict object.
            :param libdoc: libdoc input object
            :param path: library path
            :return: json object with parameters needed for request post method
            """

            lib_dict = libdoc.__dict__
            lib_dict['doc_format'] = lib_dict.pop('_setter__doc_format')
            for key in ('_setter__keywords', 'inits', 'named_args'):
                lib_dict.pop(key)
            lib_dict['path'] = path
            return lib_dict

        def _serialise_keywords() -> List[Dict[str, str]]:
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
        coll_req = self._post_request('collections', serialised_libdoc)
        if coll_req.status_code == 201:
            for keyword in serialised_keywords:
                collection_id = coll_req.json()["id"]
                keyword["collection_id"] = collection_id
                kwd_req = self._post_request('keywords', keyword)
            print(f'{libdoc.name} library with {len(serialised_keywords)} keywords loaded.')
        else:
            print(f'{libdoc.name} library was not loaded!')

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

    def _post_request(self, endpoint: str, data: Dict) -> post:
        """
        Sends post request to collections or keywords endpoint.
        """
        request = self.session.post(url=f'{PROTOCOL}{self.app_interface}:{self.port}/{API_V1}/{endpoint}/',
                                    auth=self.auth, json=data,
                                    headers={"Content-Type": "application/json", "accept": "application/json"})
        return request

    def _delete_request(self, endpoint: str, id: int) -> delete:
        """
        Sends delete request to collections or keywords endpoint with item id.
        """
        request = self.session.delete(url=f'{PROTOCOL}{self.app_interface}:{self.port}/{API_V1}/{endpoint}/{id}/',
                                      auth=self.auth, headers={"accept": "application/json"})
        return request

    def _get_request(self, endpoint: str) -> get:
        """
        Sends get request from given endpoint.
        """
        request = self.session.get(url=f'{PROTOCOL}{self.app_interface}:{self.port}/{API_V1}/{endpoint}',
                                   headers={"accept": "application/json"})
        return request
