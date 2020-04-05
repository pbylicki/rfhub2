*** Settings ***
Resource          ../resources/keywords.resource
Resource          ../resources/e2e_keywords.resource
Resource          ../resources/variables.resource
Suite Setup       Open Browser With App On Mainpage
Suite Teardown    Close Browser
