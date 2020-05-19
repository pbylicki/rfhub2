*** Settings ***
Documentation    This suite contains test cases for smoke tests for IDQP project.

*** Test Cases ***
IDQP Should Produce Results When Run
    [Documentation]    IDQP App should produce expected results, as specified i ticket IDQP-123
    [Tags]    IDQP-123
    Log    IDQP app starting
    Log    IDQP app ending

IDQP Should Exit With Random RC on Whim
    [Documentation]    IDQP App should exit with random rc, as mentioned ticket IDQP-486
    [Tags]    IDQP-486
    Log    IDQP app starting
    Comment    IDQP app failing flamboyantly
