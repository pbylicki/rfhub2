*** Settings ***
Documentation    __init__.robot extension with one test keyword
Suite Setup      Keyword 1 Not Imported From Robot Init File

*** Keywords ***
Keyword 1 Not Imported From Robot Init File
    [Documentation]   This keyword was not imported from robot init file
    Log    This keyword was not imported from robot init file
