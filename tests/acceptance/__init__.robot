*** Settings ***
Resource          resources/keywords.resource
Suite Setup       Start Rfhub2
Suite Teardown    Stop Rfhub2

*** Variables ***
${DB_URI}    ${EMPTY}