*** Settings ***
Resource          resources/keywords.resource

*** Test Cases ***
Cli Should Populate App With Keywords From Provided Paths Only
    [Documentation]    Cli Should Populate App With Keywords From Provided Paths Only
    Start Cli Package With Options    --no-installed-keywords ${CURDIR}/../fixtures
    Output Should Contain
    ...    LibWithInit library with 4 keywords loaded.
    ...    Test Libdoc File library with 1 keywords loaded.
    ...    LibWithEmptyInit1 library with 2 keywords loaded.
    ...    test_resource library with 2 keywords loaded.
    ...    SingleClassLib library with 3 keywords loaded.
    ...    LibWithEmptyInit2 library with 2 keywords loaded.
    ...    test_robot library with 4 keywords loaded.
    ...    Successfully loaded 7 collections with 18 keywords.
    Api Should Have With 7 Collections And 18 Keywords

Cli Should Populate App With Installed Keywords
    [Documentation]    Cli Should Populate App With Installed Keywords
    Start Cli Package
    Output Should Contain
    ...    Collections library with 43 keywords loaded.
    ...    XML library with 37 keywords loaded.
    ...    Easter library with 1 keywords loaded.
    ...    Process library with 15 keywords loaded.
    ...    String library with 31 keywords loaded.
    ...    DateTime library with 8 keywords loaded.
    ...    OperatingSystem library with 56 keywords loaded.
    ...    Screenshot library with 3 keywords loaded.
    ...    BuiltIn library with 104 keywords loaded.
    ...    Telnet library with 20 keywords loaded.
    ...    Successfully loaded 10 collections with 318 keywords.
    Api Should Have With 10 Collections And 100 Keywords

Cli Should Preserve All Keywords When Paths And No Db Flush Set
    [Documentation]    Cli Should Preserve All Keywords When Paths And No Db Flush Set
    ...                This test is dependant on one above:
    ...                'Cli Should Populate App With Installed Keywords'
    Start Cli Package With Options    --no-db-flush --no-installed-keywords
    Output Should Contain
    ...    Successfully loaded 0 collections with 0 keywords.
    Api Should Have With 10 Collections And 100 Keywords

Cli Should Delete All Keywords When Paths And No Installed Keywords Set
    [Documentation]    Cli Should Delete All Keywords When Paths And No Installed Keywords Set
    Start Cli Package With Options    --no-installed-keywords
    Output Should Contain
    ...    Successfully loaded 0 collections with 0 keywords.
    Api Should Have With 0 Collections And 0 Keywords

Cli Should Return Unauthorised When Wrong User Given
    [Documentation]    Cli Should Return Unauthorised When Wrong User Given
    Start Cli Package With Options    -u wrong_user
    Output Should Contain    Unauthorized to perform this action

Cli Should Return Unauthorised When Wrong Password Given
    [Documentation]    Cli Should Return Unauthorised When Wrong Password Given
    Start Cli Package With Options    -p wrong_pass
    Output Should Contain    Unauthorized to perform this action

Cli Should Return Connection Error When Wrong Url Given
    [Documentation]    Cli Should Return Connection Error When Wrong Url Given
    Start Cli Package With Options    -a 123.456.789.123:666
    Should Contain    ${output}    No connection adapters were found

*** Keywords ***
Api Should Have With ${n} Collections And ${m} Keywords
    collections Endpoint Should Have ${n} Items
    keywords Endpoint Should Have ${m} Items