*** Settings ***
Library           String
Resource          resources/keywords.resource
Resource          resources/e2e_keywords.resource
Resource          resources/variables.resource
Suite Setup       Open Browser With App On Mainpage
Suite Teardown    Close Browser
Test Setup        Navigate To Main Page
Force Tags        e2e

*** Variables ***
@{expected_libraries}    LibWithEmptyInit1    LibWithEmptyInit2    LibWithInit      SingleClassLib
...                      Test Libdoc File     test_res_lib_dir     test_resource    test_robot
@{expected_keywords}     Overview    Single Class Lib Method 1    Single Class Lib Method 2    Single Class Lib Method 3

*** Test Cases ***
Populated App Should Show Number Of Collections
    Run Cli Package With Options    --load-mode=insert --no-installed-keywords ${CURDIR}/../fixtures/initial
    Collections Count On Main Page Should Be 8

First Page Table Should Contain Proper Libraries Data
    [Documentation]    This test bases on 
    ...    'Populated App Should Show Number Of Collections'
    ...    to shorten execution time.
    [Template]    Table Should Contain Library Data
    LibWithEmptyInit1       LIBRARY     2.1.0       2
    LibWithEmptyInit2       LIBRARY     1.0.0       2
    LibWithInit             LIBRARY     6.6.6       4
    SingleClassLib          LIBRARY     1.2.3       3
    Test Libdoc File        LIBRARY     3.2.0       1
    test_res_lib_dir        RESOURCE    ${EMPTY}    2
    test_resource           RESOURCE    ${EMPTY}    2
    test_robot              RESOURCE    ${EMPTY}    4

Left Panel Should Contain Expected Libraries
    [Documentation]    This test bases on 
    ...    'Populated App Should Show Number Of Collections'
    ...    to shorten execution time.
    Left Panel Should Contain Every Library

Left Panel Should Contain Library Keywords In Alphabetical Order After Click
    [Documentation]    This test bases on 
    ...    'Populated App Should Show Number Of Collections'
    ...    to shorten execution time.
    [Tags]    rfhub2-46    regression
    Open ${single_class_lib} In Left Panel
    Left Panel For Single Library Should Contain Expected Keywords    @{expected_keywords}

Left Panel Keywords Should Navigate To Library Details And Show Correct Data
    [Documentation]    This test bases on 
    ...    'Populated App Should Show Number Of Collections'
    ...    to shorten execution time.
    [Tags]    rfhub2-155
    Sleep    2s    #Let the page load on travis
    Open ${lib_with_init} In Left Panel
    Click ${lib_with_init_2_method_1} In Left Panel
    Library title Should Be LibWithInit
    Library version Should Be version: 6.6.6
    Library scope Should Be scope: GLOBAL
    Library overview Should Be This is a docstring that should be imported as overview
    Library ext_docs Should Be Here goes some docs that should appear on rfhub2 if init is parametrised
    Library keywords Should Be Keywords (4)

Main Page Libraries Should Navigate To Library Details
    [Documentation]    This test bases on 
    ...    'Populated App Should Show Number Of Collections'
    ...    to shorten execution time.
    Click Element When Visible    ${test_libdoc_file}
    Wait Until Element Is Visible    ${detail_view_library_version}
    Library title Should Be Test Libdoc File
    Library version Should Be version: 3.2.0
    Library scope Should Be scope: GLOBAL
    Library overview Should Be Documentation for library Test Libdoc File.
    Library keywords Should Be Keywords (1)

Search Should Return Expected Results
    [Documentation]    This test bases on 
    ...    'Populated App Should Show Number Of Collections'
    ...    to shorten execution time.
    [Tags]    rfhub2-161    tags
    [Template]    Search For Method Should Return Expected Values
    Method 3    1    Single Class Lib Method 3    ${EMPTY}    SingleClassLib    Docstring for single_class_lib_method_3 with two params
    Keyword*Doub    1    Keyword With Args With Double Quotation Mark    ${EMPTY}    test_robot    Keyword With Args With Double Quotation Mark
    name:Some    1    Someone Shall Pass    ${EMPTY}    ${EMPTY}    Test Libdoc File
    Some in:Te    1   Someone Shall Pass    ${EMPTY}    ${EMPTY}    Test Libdoc File
    name:Sh in:Te   1    Someone Shall Pass    ${EMPTY}    ${EMPTY}    Test Libdoc File
    tags:tag_1   1    Single Class Lib Method 1    ${EMPTY}    SingleClassLib    Docstring for single_class_lib_method_1
    tags:tag in:Single   1    Single Class Lib Method 1    ${EMPTY}    SingleClassLib    Docstring for single_class_lib_method_1

Tags Should Be Displayed On Collection Details
    [Documentation]    This test bases on 
    ...    'Populated App Should Show Number Of Collections'
    ...    to shorten execution time.
    [Tags]    rfhub2-161    tags
    [Template]    Tags Should Be Displayed For Collection
    test_robot        first_tag    second_tag
    SingleClassLib    tag_1        tag_2

Tags Should Be Displayed On Search Results
    [Documentation]    This test bases on 
    ...    'Populated App Should Show Number Of Collections'
    ...    to shorten execution time.
    [Tags]    rfhub2-161    tags
    [Template]    Tags Should Be Displayed For Search Results
    tags:first_tag        first_tag
    tags:tag in:Single    tag_1    tag_2

First Page Table After Update Should Contain Proper Libraries Data
    [Documentation]    This test bases on 
    ...    'Populated App Should Show Number Of Collections'
    ...    to shorten execution time.
    [Tags]    rfhub2-64    update
    [Setup]    Test Setup For Collections Update
    [Template]    Table Should Contain Library Data
    LibWithEmptyInit1        LIBRARY     2.1.0       2
    LibWithEmptyInit2        LIBRARY     1.0.0       2
    LibWithInit              LIBRARY     6.6.6       4
    SingleClassLib           LIBRARY     1.2.8       4
    Test Libdoc File         LIBRARY     3.2.1       1
    Test Libdoc File Copy    LIBRARY     3.2.1       1
    test_resource            RESOURCE    ${EMPTY}    2
    [Teardown]    Restore Initial Fixtures

Single Class Library Details Should Be Updated On Frontend
    [Documentation]    This test bases on 
    ...    'First Page Table After Update Should Contain Proper Libraries Data'
    ...    to shorten execution time.
    [Tags]    rfhub2-64    update
    Open ${single_class_lib} In Left Panel
    Click ${overview} In Left Panel
    Click Element    ${single_class_lib}
    Wait Until Element Is Visible    ${detail_view_library_version}
    Library title Should Be SingleClassLib
    Library version Should Be version: 1.2.8
    Library scope Should Be scope: TEST
    Library overview Should Be Overview that should be imported for SingleClassLib.
    Library keywords Should Be Keywords (4)

App Should Display Libraries With Times Used Statistics
    [Documentation]    App Should Display Libraries With Times Used Statistics
    [Setup]    Test Setup For Collections Statistics
    [Template]    Table Should Contain Library Data  
    e2e_keywords       RESOURCE	   ${EMPTY}    17	  114
    keywords	       RESOURCE	   ${EMPTY}    15	  67

App Should Display Keywords Statistics For Single Libary
    [Documentation]    App Should Display Keywords Statistics For Single Libary
    ...    this tests is dependant on 'App Should Display Libraries 
    ...    With Times Used Statistics' to shorter execution time
    Click Element When Visible    ${e2e_keywords_file}
    Wait Until Element Is Visible    ${detail_view_library_version}
    Sleep    2s
    Row 2 In Column 1 Of Table ${detail_view_library_table} Should Contain Check If Tags Are Displayed Correctly
    Row 2 In Column 5 Of Table ${detail_view_library_table} Should Contain 4
    Row 2 In Column 6 Of Table ${detail_view_library_table} Should Contain 106 ms

*** Keywords ***
Test Setup For Collections Update
    Run Cli Package Without Installed Keywords
    Backup And Switch Initial With Updated Fixtures
    Run Cli Package With Options    
    ...    --load-mode=update --no-installed-keywords ${INITIAL_FIXTURES}
    Navigate To Main Page
    Collections Count On Main Page Should Be 7

Test Setup For Collections Statistics
    Run Cli Package With Options    --load-mode=insert --no-installed-keywords ${STATISTICS_PATH} ${CURDIR}/resources
    Run Cli Package With Options    --load-mode=insert -m statistics ${STATISTICS_PATH}
    Navigate To Main Page
    Sleep    1s
    Collections Count On Main Page Should Be 2

Row ${m} In Column ${n} Of Table ${table} Should Contain ${value}
    Table Cell Should Contain    ${table}    ${m}    ${n}    ${value}

