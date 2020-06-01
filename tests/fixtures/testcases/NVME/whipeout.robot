*** Settings ***
Documentation    This is a documentation for whipeout from NVME directory.
Default Tags     NVME-2280

*** Test Cases ***
Whipeout All
    [Documentation]    This TC clean up all SSD clean.
    Comment    rm -rf .

Dummy Empty Test
    [Documentation]    Dummy Empty Test