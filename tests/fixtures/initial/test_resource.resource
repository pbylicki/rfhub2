*** Settings ***
Documentation    File with .resource extension with two test keywords

*** Keywords ***
Keyword 1 Imported From Resource File
    [Tags]    first_tag
    [Documentation]   This keyword was imported from file
    ...    with .resource extension, available since RFWK 3.1
    Log    This keyword was imported from file with .resource extension, available since RFWK 3.1

Keyword 2 Imported From Resource File
    [Tags]    first_tag    second_tag
    [Documentation]   This keyword was imported from file
    ...    with .resource extension, available since RFWK 3.1
    [Arguments]    ${arg_1}    ${arg_2}
    Log    This keyword was imported from file with .resource extension, available since RFWK 3.1
