*** Settings ***
Documentation    This Suite contains testcases checking 
...              rfhub2-cli documentation for each option.  
Library          OperatingSystem
Resource         resources/keywords.resource
Suite Setup      Run Package With Help Option

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

Documentation For Load Should Be Displayed Properly
    [Documentation]    Documentation For Mode Should Be Displayed Properly
    [Tags]    rfhub2-67    statistics
    Output Should Contain
    ...    -m, --mode [keywords|statistics]
    ...    Choice parameter specifying what kind of
    ...    data package should add:
    ...    - `keywords` -
    ...    default value, application is working with
    ...    keywords documentation
    ...    - `statistics` -
    ...    application is working with data about
    ...    keywords execution.

Documentation For Load Mode Should Be Displayed Properly
    [Documentation]    Documentation For Load Mode Should Be Displayed Properly
    [Tags]    rfhub2-64    rfhub2-330    update
    Output Should Contain
    ...    -l, --load-mode [merge|insert|append|update]
    ...    Choice parameter specifying in what load
    ...    mode package should run:
    ...    - `merge`  - default value, adds new and
    ...    updates only matched collections, does
    ...    nothing with not matched ones
    ...    - `insert` - removes all existing
    ...    collections from app and add ones found in
    ...    paths
    ...    - `append` - adds collections found in paths
    ...    without removal of existing ones
    ...    - `update` - removes collections not found
    ...    in paths, adds new ones and updates existing
    ...    ones

Documentation For Include Exclude Should Be Displayed Properly
    [Documentation]    Documentation For Include Exclude options Should Be Displayed Properly
    [Tags]    include-exclude
    Output Should Contain
    ...    -i, --include TEXT
    ...    Include all the keywords containing tags
    ...    matching this pattern. This option has the
    ...    same behavior as the --include option of the
    ...    RobotFramework CLI (with the same format).
    ...    By default, all the keywords found are
    ...    included.
    ...    -e, --exclude TEXT
    ...    Exclude all the keywords containing tags
    ...    matching this pattern. This option has the
    ...    same behavior as the --exclude option of the
    ...    RobotFramework CLI (with the same format).
    ...    By default, no keyword is excluded.

Documentation For Help Should Be Displayed Properly
    [Documentation]    Documentation For Help Should Be Displayed Properly
    Output Should Contain
    ...    --help
    ...    Show this message and exit.

*** Keywords ***
Run Package With Help Option
    Run Cli Package With Options    --help
