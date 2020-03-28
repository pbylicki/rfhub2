*** Settings ***
Documentation    File with .robot extension with two test keywords

*** Keywords ***
Keyword 1 Imported From Robot File
    [Documentation]   This keyword was imported from file
    ...    with .robot extension
    [Tags]    first_tag    second_tag
    Log    This keyword was imported from file with .resource extension, available since RFWK 3.1

Keyword 2 Imported From Robot File
    [Documentation]   This keyword was imported from file
    ...    with .robot extension
    [Arguments]    ${arg_1}    ${arg_2}
    [Tags]    first_tag    second_tag    third_tag
    Log    This keyword was imported from file with .resource extension, available since RFWK 3.1

Keyword With Args With Single Quotation Mark
    [Documentation]    Keyword With Args With Single Quotation Mark
    [Arguments]    ${ok_argument}    ${not_ok_argument}=Kill.${app.replace('-', '_')}
    [Tags]    third_tag    fouth_tag
    Log    I'm Keyword With Args With Single Quotation Mark

Keyword With Args With Double Quotation Mark
    [Documentation]    Keyword With Args With Double Quotation Mark
    [Arguments]    ${ok_argument}    ${not_ok_argument}=Kill.${app.replace("-", "_")}
    [Tags]    fouth_tag    fifth_tag
    Log    I'm Keyword With Args With Double Quotation Mark
