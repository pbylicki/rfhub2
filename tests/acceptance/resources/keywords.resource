*** Settings ***
Library    SeleniumLibrary
Library    OperatingSystem
Library    Process
Library    RequestsLibrary
Library    Collections

*** Keywords ***
Start Rfhub2
    [Arguments]    @{options}
    [Documentation]
    ...    Starts rfhub2 on the port given in the variable \${PORT}
    ...    As a side effect this creates a suite variable named \${rfhub process},
    ...    which is used by the 'Stop rfhub2' keyword.
    Remove File    ${DB_PATH}
    ${rfhub2_process}    Start Process    ${ACTIVATE_VENV} ${DB_URI} rfhub2
    ...    shell=True    stdout=api_logs.log    stderr=stderr_logs.log
    Set Suite Variable    ${rfhub2_process}
    Wait Until Keyword Succeeds    20 seconds    0.5 second
    ...    Verify URL Is Reachable    /api/v1/health

Stop Rfhub2
    [Documentation]
    ...    Stops the rfhub2 process created by "Start Rfhub2"
    Terminate Process    ${rfhub2_process}
    ${result}    Get Process Result
    Log    rfhub2 stderr: ${result.stderr} \nstdout: ${result.stdout}    DEBUG

Run Cli Package With Options
    [Arguments]    ${options}
    [Documentation]
    ...    Attempt to run the rfhub2-cli package with the given options
    ...    The stdout of the process will be in a test suite
    ...    variable named \${output}
    ${output}    Run    ${ACTIVATE_VENV} rfhub2-cli -a http://${HOST}:8000 ${options}
    Set Suite Variable    ${output}

Run Cli Package
    [Documentation]
    ...    Attempt to run the rfhub2-cli package with the default options
    ...    The stdout of the process will be in a test suite
    ...    variable named \${output}
    ${output}    Run    ${ACTIVATE_VENV} rfhub2-cli -a http://${HOST}:8000
    Set Suite Variable    ${output}

Output Should Contain
    [Arguments]    @{patterns}
    [Documentation]
    ...    Fail if the output from the previous command doesn't contain the given string
    ...    This keyword assumes the output of the command is in
    ...    a test suite variable named \${output}
    ${ns}    Create Dictionary    output=${output}
    ${clean_output}    Evaluate    " ".join(l.strip() for l in output.splitlines())    namespace=${ns}
    FOR    ${pattern}    IN    @{patterns}
        Run keyword if    '''${pattern}''' not in '''${clean_output}'''
        ...    Fail    Output did not contain '${pattern}'. \n${clean_output}
    END

Verify URL Is Reachable
    # This could be useful in more places than just API tests.
    # Maybe it should be moved to a different file...
    [Arguments]    ${URL}    ${PORT}=8000
    [Documentation]    Fail if the given URL doesn't return a status code of 200.
    Create Session    tmp    http://${HOST}:${PORT}
    ${response}    GET On Session    tmp    ${url}
    Should Be Equal As Integers    ${response.status_code}    200

${endpoint} Endpoint Should Have ${n} Items
    ${response}    Get Request For Endpoint    endpoint=${endpoint}
    Length Should Be    ${response}    ${n}

Get Request For Endpoint
    [Arguments]    ${endpoint}    ${params}=None
    Create Session    tmp    http://${HOST}:8000/api/v1
    ${response}    GET On Session    tmp    ${endpoint}/    params=${params}
    Should Be Equal As Integers    ${response.status_code}    200
    [Return]    ${response.json()}

Delete All Statistics
    ${auth}    Create List    rfhub    rfhub
    Create Session    tmp    http://${HOST}:8000/api/v1    auth=${auth}
    ${response}    DELETE On Session    tmp    statistics/keywords/all/
    Should Be Equal As Integers    ${response.status_code}    204

Run Cli Package Without Installed Keywords
    Run Cli Package With Options    --load-mode=insert --no-installed-keywords ${INITIAL_FIXTURES}

Backup And Switch Initial With Updated Fixtures
    Move Directory      ${INITIAL_FIXTURES}     ${BACKUP_FIXTURES}
    Copy Directory      ${UPDATED_FIXTURES}     ${INITIAL_FIXTURES}

Backup And Switch Initial With Merged Fixtures
    Move Directory      ${INITIAL_FIXTURES}     ${BACKUP_FIXTURES}
    Copy Directory      ${MERGED_FIXTURES}      ${INITIAL_FIXTURES}

Backup And Switch Initial With Include_Exclude Fixtures
    Move Directory      ${INITIAL_FIXTURES}     ${BACKUP_FIXTURES}
    Copy Directory      ${INCLUDE_EXCLUDE_FIXTURES}    ${INITIAL_FIXTURES}

Switch Merged With Merged_2 Fixtures
    Remove Directory    ${INITIAL_FIXTURES}     recursive=True
    Copy Directory      ${MERGED_2_FIXTURES}    ${INITIAL_FIXTURES}

Restore Initial Fixtures
    Remove Directory    ${INITIAL_FIXTURES}     recursive=True
    Copy Directory      ${BACKUP_FIXTURES}      ${INITIAL_FIXTURES}
    Remove Directory    ${BACKUP_FIXTURES}      recursive=True
