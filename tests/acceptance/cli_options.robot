*** Settings ***
Library        OperatingSystem
Resource       resources/keywords.resource
Suite Setup    Start Package With Help Option

*** Test Cases ***
Documentation For Whole Package Should Be Displayed Properly
    [Documentation]    Documentation For Whole Package Should Be Displayed Properly
    Output Should Contain
    ...    Package to populate rfhub2 with robot framework keywords from libraries
    ...    and resource files.

Documentation For AppUrl Should Be Displayed Properly
    [Documentation]    Documentation For AppUrl Should Be Displayed Properly
    Output Should Contain
    ...    -a, --app-url TEXT
    ...    Specifies IP, URI or host of rfhub2 web
    ...    application. Default value is
    ...    http://localhost:8000.

Documentation For User Should Be Displayed Properly
    [Documentation]    Documentation For User Should Be Displayed Properly
    Output Should Contain
    ...    -u, --user TEXT
    ...    Specifies rfhub2 user to authenticate on endpoints
    ...    that requires that. Default value is rfhub.

Documentation For Password Should Be Displayed Properly
    [Documentation]    Documentation For Password Should Be Displayed Properly
    Output Should Contain
    ...    -p, --password TEXT
    ...    Specifies rfhub2 password to authenticate on
    ...    endpoints that requires that. Default value is
    ...    rfhub.

Documentation For No Installed Keywords Should Be Displayed Properly
    [Documentation]    Documentation For No Installed Keywords Should Be Displayed Properly
    Output Should Contain
    ...    --no-installed-keywords
    ...    Flag specifying if package should skip loading
    ...    commonly installed libraries, such as such as
    ...    BuiltIn, Collections, DateTime etc.

Documentation For No DB Flush Should Be Displayed Properly
    [Documentation]    Documentation For No DB Flush Should Be Displayed Properly
    Output Should Contain
    ...    --no-db-flush
    ...    Flag specifying if package should delete from
    ...    rfhub2 all existing libraries.
    ...    BuiltIn, Collections, DateTime etc.

Documentation For Help Should Be Displayed Properly
    [Documentation]    Documentation For Help Should Be Displayed Properly
    Output Should Contain
    ...    --help
    ...    Show this message and exit.

*** Keywords ***
Start Package With Help Option
    Start Cli Package With Options    --help
