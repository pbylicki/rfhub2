from pathlib import Path
import robot.libraries

from rfhub2.cli.keywords.keywords_importer import CollectionUpdateWithKeywords
from rfhub2.model import Collection, CollectionUpdate, KeywordUpdate, NestedKeyword

FIXTURE_PATH = Path.cwd() / "tests" / "fixtures" / "initial"
STATISTICS_PATH = FIXTURE_PATH / ".." / "statistics"
EXPECTED_LIBDOC = {
    "doc": "Documentation for library ``Test Libdoc File``.",
    "doc_format": "ROBOT",
    "name": "Test Libdoc File",
    "scope": "GLOBAL",
    "type": "library",
    "version": "3.2.0",
    "keywords": [{"name": "Someone Shall Pass", "args": '["who"]', "doc": ""}],
}
EXPECTED_INIT_DOC = """\n\nHere goes some docs that should appear on rfhub2 if init is parametrised
\nThe library import:
\nExamples:
| Library    LibWithInit   dummy=../one               # add one dummy
| Library    LibWithInit   path=../one,/global        # add two dummies"""
EXPECTED_KEYWORDS = [
    KeywordUpdate(
        args="",
        doc="This keyword was imported from file\n"
        "with .resource extension, available since RFWK 3.1",
        name="Keyword 1 Imported From Resource File",
        tags=["first_tag"],
    ),
    KeywordUpdate(
        args='["arg_1", "arg_2"]',
        doc="This keyword was imported from file\n"
        "with .resource extension, available since RFWK 3.1",
        name="Keyword 2 Imported From Resource File",
        tags=["first_tag", "second_tag"],
    ),
]
EXPECTED_TRAVERSE_PATHS_INIT = {FIXTURE_PATH / "LibWithInit"}
EXPECTED_TRAVERSE_PATHS_NO_INIT = {
    FIXTURE_PATH / "LibsWithEmptyInit" / "LibWithEmptyInit1.py",
    FIXTURE_PATH / "LibsWithEmptyInit" / "LibWithEmptyInit2.py",
}
EXPECTED_GET_LIBRARIES = (
    EXPECTED_TRAVERSE_PATHS_INIT
    | EXPECTED_TRAVERSE_PATHS_NO_INIT
    | {
        FIXTURE_PATH / "SingleClassLib" / "SingleClassLib.py",
        FIXTURE_PATH / "test_libdoc_file.xml",
        FIXTURE_PATH / "test_resource.resource",
        FIXTURE_PATH / "test_robot.robot",
        FIXTURE_PATH / "arg_parse.py",
        FIXTURE_PATH / "data_error.py",
        FIXTURE_PATH / "LibWithInit" / "test_res_lib_dir.resource",
    }
)
EXPECTED_GET_EXECUTION_PATHS = {
    STATISTICS_PATH / "output.xml",
    STATISTICS_PATH / "subdir" / "output.xml",
}
EXPECTED_COLLECTION = CollectionUpdate(
    doc="Overview that should be imported for SingleClassLib.",
    doc_format="ROBOT",
    name="SingleClassLib",
    path=str(FIXTURE_PATH / "SingleClassLib" / "SingleClassLib.py"),
    scope="TEST",
    type="LIBRARY",
    version="1.2.3",
)

EXPECTED_COLLECTION_KEYWORDS_1_1 = KeywordUpdate(
    args="",
    doc="Docstring for single_class_lib_method_1",
    name="Single Class Lib Method 1",
    tags=["tag_1", "tag_2"],
)
EXPECTED_COLLECTION_KEYWORDS_1_2 = KeywordUpdate(
    args="",
    doc="Docstring for single_class_lib_method_2",
    name="Single Class Lib Method 2",
    tags=[],
)
EXPECTED_COLLECTION_KEYWORDS_1_3 = KeywordUpdate(
    args='["param_1", "param_2"]',
    doc="Docstring for single_class_lib_method_3 with two params",
    name="Single Class Lib Method 3",
    tags=[],
)
EXPECTED_COLLECTION_KEYWORDS_1 = [
    EXPECTED_COLLECTION_KEYWORDS_1_1,
    EXPECTED_COLLECTION_KEYWORDS_1_2,
    EXPECTED_COLLECTION_KEYWORDS_1_3,
]
EXISTING_COLLECTION_KEYWORDS = [
    NestedKeyword(**{**EXPECTED_COLLECTION_KEYWORDS_1_3.dict(), "id": 1})
]
EXISTING_COLLECTION = Collection(
    **{
        **EXPECTED_COLLECTION.dict(),
        "id": 1,
        "keywords": [
            NestedKeyword(**{**EXPECTED_COLLECTION_KEYWORDS_1_3.dict(), "id": 1})
        ],
    }
)
EXPECTED_COLLECTION_2 = CollectionUpdate(
    doc="Documentation for library ``Test Libdoc File``.",
    doc_format="ROBOT",
    name="Test Libdoc File",
    path=str(FIXTURE_PATH / "test_libdoc_file.xml"),
    scope="GLOBAL",
    type="LIBRARY",
    version="3.2.0",
)
EXPECTED_COLLECTION_KEYWORDS_2_1 = KeywordUpdate(
    args='["who"]', doc="", name="Someone Shall Pass", tags=[]
)
EXPECTED_COLLECTION_KEYWORDS_2 = [EXPECTED_COLLECTION_KEYWORDS_2_1]
EXISTING_COLLECTION_2 = Collection(
    **{
        **EXPECTED_COLLECTION_2.dict(),
        "id": 1,
        "keywords": [
            NestedKeyword(**{**EXPECTED_COLLECTION_KEYWORDS_2_1.dict(), "id": 1})
        ],
    }
)
EXPECTED_ADD_COLLECTIONS = [{"name": "Test Libdoc File", "keywords": 1}]
EXPECTED_UPDATE_COLLECTIONS = [
    {"name": "a", "keywords": 1},
    {"name": "b", "keywords": 1},
    {"name": "c", "keywords": 1},
    {"name": "d", "keywords": 1},
    {"name": "e", "keywords": 1},
]
KEYWORDS_1 = [
    {
        "args": "",
        "doc": "Docstring for single_class_lib_method_1",
        "name": "Single Class Lib Method 1",
    },
    {
        "args": "",
        "doc": "Docstring for single_class_lib_method_2",
        "name": "Single Class Lib Method 2",
    },
    {
        "args": '["param_1", "param_2"]',
        "doc": "Docstring for single_class_lib_method_3 with two params",
        "name": "Single Class Lib Method 3",
    },
]
KEYWORDS_2 = [{"args": '["who"]', "doc": "", "name": "Someone Shall Pass"}]
KEYWORDS_EXTENDED = [
    {
        "args": "",
        "doc": "Docstring for single_class_lib_method_1",
        "name": "Single Class Lib Method 1",
        "id": 15,
        "synopsis": "Docstring for lib_with_empty_init_1_method_1",
        "html_doc": "<p>Docstring for lib_with_empty_init_1_method_1</p>",
        "arg_string": "",
    },
    {
        "args": "",
        "doc": "Docstring for single_class_lib_method_2",
        "name": "Single Class Lib Method 2",
        "id": 16,
        "synopsis": "Docstring for lib_with_empty_init_1_method_1",
        "html_doc": "<p>Docstring for lib_with_empty_init_1_method_1</p>",
        "arg_string": "",
    },
    {
        "args": '["param_1", "param_2"]',
        "doc": "Docstring for single_class_lib_method_3 with two params",
        "name": "Single Class Lib Method 3",
        "id": 17,
        "synopsis": "Docstring for lib_with_empty_init_1_method_1",
        "html_doc": "<p>Docstring for lib_with_empty_init_1_method_1</p>",
        "arg_string": "",
    },
]

EXPECTED_BUILT_IN_LIBS = {
    Path(robot.libraries.__file__).parent / "BuiltIn.py",
    Path(robot.libraries.__file__).parent / "Collections.py",
    Path(robot.libraries.__file__).parent / "DateTime.py",
    Path(robot.libraries.__file__).parent / "Easter.py",
    Path(robot.libraries.__file__).parent / "OperatingSystem.py",
    Path(robot.libraries.__file__).parent / "Process.py",
    Path(robot.libraries.__file__).parent / "Screenshot.py",
    Path(robot.libraries.__file__).parent / "String.py",
    Path(robot.libraries.__file__).parent / "Telnet.py",
    Path(robot.libraries.__file__).parent / "XML.py",
}
EXPECTED_COLLECTION_WITH_KW_1 = CollectionUpdateWithKeywords(
    EXPECTED_COLLECTION, EXPECTED_COLLECTION_KEYWORDS_1
)
EXPECTED_COLLECTION_WITH_KW_2 = CollectionUpdateWithKeywords(
    EXPECTED_COLLECTION_2, EXPECTED_COLLECTION_KEYWORDS_2
)
