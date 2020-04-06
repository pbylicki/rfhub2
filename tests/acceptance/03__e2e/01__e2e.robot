# *** Settings ***
# Library       String
# Resource      ../resources/keywords.resource
# Resource      ../resources/e2e_keywords.resource
# Resource      ../resources/variables.resource
# Test Setup    Navigate To Main Page

# *** Variables ***
# @{expected_libraries}    LibWithEmptyInit1    LibWithEmptyInit2    LibWithInit      SingleClassLib
# ...                      Test Libdoc File     test_res_lib_dir     test_resource    test_robot
# @{expected_keywords}     Overview    Single Class Lib Method 1    Single Class Lib Method 2    Single Class Lib Method 3

# *** Test Cases ***
# Populated App Should Show Number Of Collections
    # Run Cli Package With Options    --no-installed-keywords ${CURDIR}/../../fixtures/initial
    # Collections Count On Main Page Should Be 8

# First Page Table Should Contain Proper Libraries Data
    # [Documentation]    This test bases on 
    # ...    'Populated App Should Show Number Of Collections'
    # ...    to shorten execution time.
    # [Template]    Table Should Contain Library Data
    # LibWithEmptyInit1       library     2.1.0       2
    # LibWithEmptyInit2       library     1.0.0       2
    # LibWithInit             library     6.6.6       4
    # SingleClassLib          library     1.2.3       3
    # Test Libdoc File        library     3.2.0       1
    # test_res_lib_dir        resource    ${EMPTY}    2
    # test_resource           resource    ${EMPTY}    2    
    # test_robot              resource    ${EMPTY}    4

# Left Panel Should Contain Expected Libraries Library
    # [Documentation]    This test bases on 
    # ...    'Populated App Should Show Number Of Collections'
    # ...    to shorten execution time.
    # Left Panel Should Contain Every Library

# Left Panel Should Contain Library Keywords In Alphabetical Order After Click
    # [Documentation]    This test bases on 
    # ...    'Populated App Should Show Number Of Collections'
    # ...    to shorten execution time.
    # [Tags]    rfhub2-46    regression
    # Open ${single_class_lib} In Left Panel
    # Left Panel For Single Library Should Contain Expected Keywords    @{expected_keywords}

# Left Panel Keywords Should Navigate To Library Details And Show Correct Data
    # [Documentation]    This test bases on 
    # ...    'Populated App Should Show Number Of Collections'
    # ...    to shorten execution time.
    # [Tags]    rfhub2-155
    # Sleep    1s    #Let the page load on travis
    # Open ${lib_with_init} In Left Panel
    # Click ${lib_with_init_2_method_1} In Left Panel
    # Library title Should Be LibWithInit
    # Library version Should Be version: 6.6.6
    # Library scope Should Be scope: global
    # Library overview Should Be This is a docstring that should be imported as overview
    # Library ext_docs Should Be Here goes some docs that should appear on rfhub2 if init is parametrised
    # Library keywords Should Be Keywords (4)

# Main Page Libraries Should Navigate To Library Details
    # [Documentation]    This test bases on 
    # ...    'Populated App Should Show Number Of Collections'
    # ...    to shorten execution time.
    # Wait Until Element Is Visible    ${test_libdoc_file}
    # Click Element    ${test_libdoc_file}
    # Wait Until Element Is Visible    ${detail_view_library_version}
    # Library title Should Be Test Libdoc File
    # Library version Should Be version: 3.2.0
    # Library scope Should Be scope: global
    # Library overview Should Be Documentation for library Test Libdoc File.
    # Library keywords Should Be Keywords (1)

# Search Should Return Expected Results
    # [Documentation]    This test bases on 
    # ...    'Populated App Should Show Number Of Collections'
    # ...    to shorten execution time.
    # [Tags]    rfhub2-161    tags
    # [Template]    Search For Method Should Return Expected Values
    # Method 3    1    Single Class Lib Method 3    ${EMPTY}    SingleClassLib    Docstring for single_class_lib_method_3 with two params
    # Keyword*Doub    1    Keyword With Args With Double Quotation Mark    ${EMPTY}    test_robot    Keyword With Args With Double Quotation Mark
    # name:Some    1    Someone Shall Pass    ${EMPTY}    ${EMPTY}    Test Libdoc File
    # Some in:Te    1   Someone Shall Pass    ${EMPTY}    ${EMPTY}    Test Libdoc File
    # name:Sh in:Te   1    Someone Shall Pass    ${EMPTY}    ${EMPTY}    Test Libdoc File
    # tags:tag_1   1    Single Class Lib Method 1    ${EMPTY}    SingleClassLib    Docstring for single_class_lib_method_1
    # tags:tag in:Single   1    Single Class Lib Method 1    ${EMPTY}    SingleClassLib    Docstring for single_class_lib_method_1

