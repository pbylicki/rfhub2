*** Settings ***
Documentation    File with .robot extension with two test keywords

*** Keywords ***
Keyword 1 Imported From Robot File
    [Documentation]   This keyword was imported from file
    ...    with .robot extension
    Log    This keyword was imported from file with .resource extension, available since RFWK 3.1

Keyword 2 Imported From Robot File
    [Documentation]   This keyword was imported from file
    ...    with .robot extension
    [Arguments]    ${arg_1}    ${arg_2}
    Log    This keyword was imported from file with .resource extension, available since RFWK 3.1