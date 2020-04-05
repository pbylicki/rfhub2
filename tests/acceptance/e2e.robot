*** Settings ***
Suite Setup       Open Browser With App On Mainpage
Suite Teardown    Close Browser
Test Setup        Navigate To Main Page
Library           String
Resource          resources/keywords.resource
Resource          resources/variables.resource

*** Variables ***
@{expected_libraries}    LibWithEmptyInit1    LibWithEmptyInit2    LibWithInit      SingleClassLib
...                      Test Libdoc File     test_res_lib_dir     test_resource    test_robot
@{expected_keywords}     Overview    Single Class Lib Method 1    Single Class Lib Method 2    Single Class Lib Method 3

*** Test Cases ***
Populated App Should Show Number Of Collections
    Run Cli Package With Options    --no-installed-keywords ${CURDIR}/../fixtures/initial
    Collections Count On Main Page Should Be 8

First Page Table Should Contain Proper Libraries Data
    [Documentation]    This test bases on 
    ...    'Populated App Should Show Number Of Collections'
    ...    to shorten execution time.
    [Template]    Table Should Contain Library Data
    LibWithEmptyInit1       library     2.1.0       2
    LibWithEmptyInit2       library     1.0.0       2
    LibWithInit             library     6.6.6       4
    SingleClassLib          library     1.2.3       3
    Test Libdoc File        library     3.2.0       1
    test_res_lib_dir        resource    ${EMPTY}    2
    test_resource           resource    ${EMPTY}    2    
    test_robot              resource    ${EMPTY}    4

Left Panel Should Contain Expected Libraries Library
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
    Sleep    1s    #Let the page load on travis
    Open ${lib_with_init} In Left Panel
    Click ${lib_with_init_2_method_1} In Left Panel
    Library title Should Be LibWithInit
    Library version Should Be version: 6.6.6
    Library scope Should Be scope: global
    Library overview Should Be This is a docstring that should be imported as overview
    Library ext_docs Should Be Here goes some docs that should appear on rfhub2 if init is parametrised
    Library keywords Should Be Keywords (4)

Main Page Libraries Should Navigate To Library Details
    [Documentation]    This test bases on 
    ...    'Populated App Should Show Number Of Collections'
    ...    to shorten execution time.
    Wait Until Element Is Visible    ${test_libdoc_file}
    Click Element    ${test_libdoc_file}
    Wait Until Element Is Visible    ${detail_view_library_version}
    Library title Should Be Test Libdoc File
    Library version Should Be version: 3.2.0
    Library scope Should Be scope: global
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

Tags Should Be Dispalyed On Collection Details
    [Documentation]    This test bases on 
    ...    'Populated App Should Show Number Of Collections'
    ...    to shorten execution time.
    [Tags]    rfhub2-161    tags
    [Template]    Tags Should Be Displayed For Collection
    test_robot        first_tag    second_tag
    SingleClassLib    tag_1        tag_2

Tags Should Be Dispalyed On Search Results
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
    [Setup]    Run Keywords    Test Setup For Collections Update    AND    Sleep    1s    #For travis builds
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
Table Should Contain Library Data
    [Arguments]    @{Library_data}
    Wait Until Element Is Visible    ${main_page_table}
    ${list_len}    Get Length    ${Library_data}
    FOR    ${i}    IN RANGE    1    ${list_len}
        Table Column Should Contain    ${main_page_table}    ${i}    ${Library_data}[${i-1}]
    END

Left Panel Should Contain Every Library
    [Arguments]    @{Library_data}
    Wait Until Element Is Visible    ${main_page_table}
    ${list_len}    Get Length    ${expected_libraries}
    FOR    ${i}    IN RANGE    1    ${list_len}
        Element Text Should Be    ${left_panel_list}/li[${i}]/div/span    ${expected_libraries}[${i-1}]
    END

Open ${library} In Left Panel
    ${is_visible}    Run Keyword And Return Status     Element Should Not Be Visible    ${hamburger}
    Run Keyword Unless    ${is_visible}    Click Element    ${hamburger}
    Wait Until Element Is Visible    ${library}
    Click Element    ${library}
    Wait Until Element Is Visible    //*[contains(text(),'Overview')]

Left Panel For Single Library Should Contain Expected Keywords
    [Arguments]    @{keywords}
    ${list_len}    Get Length    ${keywords}
    FOR    ${i}    IN RANGE    1    ${list_len}
        Run Keyword And Continue On Failure    Element Text Should Be    ${single_class_lib_items}/a[${i+1}]/div/div    @{keywords}[${i}]
    END

Click ${keyword} In Left Panel
    Click Element    ${keyword}
    Wait Until Element Is Visible    ${detail_view_library_version}

Library ${field} Should Be ${value}
    Element Text Should Be    ${detail_view_library_${field}}    ${value}

Search For Method Should Return Expected Values
    [Arguments]    ${method}    ${results_count}    @{results_data}
    Search For    ${method}
    Search Results Count Should Be ${results_count}
    Table Should Contain Library Data    @{results_data}

Tags Should Be Displayed For Collection
    [Arguments]    ${collection}    @{tags}
    Open ${${collection}} In Left Panel
    Click ${${collection}_keyword_1} In Left Panel
    Check If Tags Are Displayed Correctly    main    @{tags}

Tags Should Be Displayed For Search Results
    [Arguments]    ${search_string}    @{tags}
    Search For    ${search_string}
    Check If Tags Are Displayed Correctly    search    @{tags}

Check If Tags Are Displayed Correctly
    [Arguments]    ${table}    @{tags}
    ${tags_count}    Get Length    ${tags}
    Element ${${table}_page_table_tag_column}/div Count Should Be ${tags_count}
    FOR    ${i}    ${tag}    IN ENUMERATE    @{tags}
        Element Text Should Be    ${${table}_page_table_tag_column}/div[${i+1}]/span    ${tag}
    END

Search For
    [Arguments]    ${text}
    Navigate To Main Page
    Input Text    ${search_field}    ${text}
    Reload Page
    Sleep    0.5s    #selenium be too fast
    # proper way which is not stable
    # Set Selenium Speed    0.2s
    # @{chars}    Split String To Characters    ${text}
    # FOR    ${char}    IN    @{chars}
        # Press Keys    ${search_field}    ${char}
    # END
    # Set Selenium Speed    0

Element ${element} Count Should Be ${n}
    ${count}    Get Element Count    ${element}
    Should Be Equal As Integers    ${count}    ${n}    Element count should be ${n} but is ${count}

Search Results Count Should Be ${n}
    Element ${search_result_table} Count Should Be ${n}

Test Setup For Collections Update
    Run Cli Package Without Installed Keywords
    Backup And Switch Initial With Updated Fixtures
    Run Cli Package With Options    
    ...    --load-mode=update --no-installed-keywords ${INITIAL_FIXTURES}
    Navigate To Main Page
    Collections Count On Main Page Should Be 7
