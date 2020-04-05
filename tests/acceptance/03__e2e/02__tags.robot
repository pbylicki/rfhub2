*** Settings ***
Library     String
Resource    ../resources/keywords.resource
Resource    ../resources/e2e_keywords.resource
Resource    ../resources/variables.resource

*** Test Cases ***
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