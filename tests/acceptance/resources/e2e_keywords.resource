*** Settings ***
Library    SeleniumLibrary

*** Keywords ***   
Open Browser With App On Mainpage
    Open Browser    url=localhost:8000    browser=gc
    Maximize Browser Window

Navigate To Main Page
    Go To    localhost:8000

Collections Count On Main Page Should Be ${n}
    Reload Page
    Run Keyword If    '${n}'!='0'    Wait Until Element Is Visible    ${main_page_table}
    Element Text Should Be    ${main_page_collection_number}    Collections (${n})

Table Should Contain Library Data
    [Arguments]    @{Library_data}
    Wait Until Element Is Visible    ${main_page_table}
    ${list_len}    Get Length    ${Library_data}
    FOR    ${i}    IN RANGE    1    ${list_len}
        Table Column Should Contain    ${main_page_table}    ${i}    ${Library_data}[${i-1}]
    END

Left Panel Should Contain Every Library
    [Arguments]    @{Library_data}
    Wait Until Element Is Visible    ${main_page_table}
    ${list_len}    Get Length    ${expected_libraries}
    FOR    ${i}    IN RANGE    1    ${list_len}
        Element Text Should Be    ${left_panel_list}/li[${i}]/div/span    ${expected_libraries}[${i-1}]
    END

Open ${library} In Left Panel
    ${is_visible}    Run Keyword And Return Status     Element Should Not Be Visible    ${hamburger}
    Run Keyword Unless    ${is_visible}    Click Element    ${hamburger}
    Wait Until Element Is Visible    ${library}
    Click Element    ${library}
    Wait Until Element Is Visible    //*[contains(text(),'Overview')]

Left Panel For Single Library Should Contain Expected Keywords
    [Arguments]    @{keywords}
    ${list_len}    Get Length    ${keywords}
    FOR    ${i}    IN RANGE    1    ${list_len}
        Run Keyword And Continue On Failure    Element Text Should Be    ${single_class_lib_items}/a[${i+1}]/div/div    ${keywords}[${i}]
    END

Click Element When Visible
    [Arguments]    ${element}
    Wait Until Element Is Visible    ${element}
    Click Element    ${element}

Click ${keyword} In Left Panel
    Click Element When Visible    ${keyword}
    Wait Until Element Is Visible    ${detail_view_library_version}

Library ${field} Should Be ${value}
    Wait Until Element Is Visible    ${detail_view_library_${field}}    0.5s
    Element Text Should Be    ${detail_view_library_${field}}    ${value}

Search For Method Should Return Expected Values
    [Arguments]    ${method}    ${results_count}    @{results_data}
    Search For    ${method}
    Search Results Count Should Be ${results_count}
    Table Should Contain Library Data    @{results_data}

Tags Should Be Displayed For Collection
    [Arguments]    ${collection}    @{tags}
    Open ${${collection}} In Left Panel
    Click ${${collection}_keyword_1} In Left Panel
    Check If Tags Are Displayed Correctly    main    @{tags}

Tags Should Be Displayed For Search Results
    [Arguments]    ${search_string}    @{tags}
    Search For    ${search_string}
    Check If Tags Are Displayed Correctly    search    @{tags}

Check If Tags Are Displayed Correctly
    [Arguments]    ${table}    @{tags}
    ${tags_count}    Get Length    ${tags}
    Wait Until Element Is Visible    ${${table}_page_table_tag_column}/div    5s
    Element ${${table}_page_table_tag_column}/div Count Should Be ${tags_count}
    FOR    ${i}    ${tag}    IN ENUMERATE    @{tags}
        Element Text Should Be    ${${table}_page_table_tag_column}/div[${i+1}]/span    ${tag}
    END

Search For
    [Arguments]    ${text}
    Navigate To Main Page
    Input Text    ${search_field}    ${text}
    Reload Page
    Sleep    0.5s    #selenium be too fast
    # proper way which is not stable
    # Set Selenium Speed    0.2s
    # @{chars}    Split String To Characters    ${text}
    # FOR    ${char}    IN    @{chars}
        # Press Keys    ${search_field}    ${char}
    # END
    # Set Selenium Speed    0

Element ${element} Count Should Be ${n}
    ${count}    Get Element Count    ${element}
    Should Be Equal As Integers    ${count}    ${n}    Element count should be ${n} but is ${count}

Search Results Count Should Be ${n}
    Element ${search_result_table} Count Should Be ${n}
