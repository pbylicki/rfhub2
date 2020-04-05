*** Settings ***
Library        String
Resource       ../resources/keywords.resource
Resource       ../resources/e2e_keywords.resource
Resource       ../resources/variables.resource
Suite Setup    Test Setup For Collections Update
Test Setup     Navigate To Main Page

*** Test Cases ***
First Page Table After Update Should Contain Proper Libraries Data
    [Documentation]    This test bases on 
    ...    'Populated App Should Show Number Of Collections'
    ...    to shorten execution time.
    [Tags]    rfhub2-64    update
    [Template]    Table Should Contain Library Data
    LibWithEmptyInit1        library     2.1.0       2
    LibWithEmptyInit2        library     1.0.0       2
    LibWithInit              library     6.6.6       4
    SingleClassLib           library     1.2.8       4
    Test Libdoc File         library     3.2.1       1
    Test Libdoc File Copy    library     3.2.1       1
    test_resource            resource    ${EMPTY}    2
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
    Library scope Should Be scope: test case
    Library overview Should Be Overview that should be imported for SingleClassLib.
    Library keywords Should Be Keywords (4)

*** Keywords ***
Test Setup For Collections Update
    Run Cli Package Without Installed Keywords
    Backup And Switch Initial With Updated Fixtures
    Run Cli Package With Options    
    ...    --load-mode=update --no-installed-keywords ${INITIAL_FIXTURES}
    Navigate To Main Page
    Collections Count On Main Page Should Be 7
