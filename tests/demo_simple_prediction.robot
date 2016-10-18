*** Settings ***
Library           nsnqtlib.py

*** Variables ***
${STOCKNAME}               600518

*** Keywords ***

*** Test Cases ***
Make a new prediction
    show me the money    ${STOCKNAME}

