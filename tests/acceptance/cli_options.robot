*** Settings ***
Library        OperatingSystem
Resource       resources/keywords.resource
Suite Setup    Run Package With Help Option

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
    ...    Specifies rfhub2 user to authenticate on
    ...    endpoints that requires that. Default value
    ...    is rfhub.

Documentation For Password Should Be Displayed Properly
    [Documentation]    Documentation For Password Should Be Displayed Properly
    Output Should Contain
    ...    -p, --password TEXT
    ...    Specifies rfhub2 password to authenticate on
    ...    endpoints that requires that. Default value
    ...    is rfhub.

Documentation For No Installed Keywords Should Be Displayed Properly
    [Documentation]    Documentation For No Installed Keywords Should Be Displayed Properly
    Output Should Contain
    ...    --no-installed-keywords
    ...    Flag specifying if package should skip
    ...    loading commonly installed libraries, such
    ...    as such as BuiltIn, Collections, DateTime
    ...    etc.

Documentation For Mode Should Be Displayed Properly
    [Documentation]    Documentation For Mode Should Be Displayed Properly
    Output Should Contain
    ...    -m, --mode [insert|append|update]
    ...    Choice parameter specifying in what mode
    ...    package should run:
    ...    - `insert` - default
    ...    value, removes all existing collections from
    ...    app and add ones found in paths
    ...    - `append`
    ...    - adds collections found in paths without
    ...    removal of existing ones
    ...    - `update` -
    ...    removes collections not found in paths, adds
    ...    new ones and updates existing ones.

Documentation For Help Should Be Displayed Properly
    [Documentation]    Documentation For Help Should Be Displayed Properly
    Output Should Contain
    ...    --help
    ...    Show this message and exit.

*** Keywords ***
Run Package With Help Option
    Run Cli Package With Options    --help
