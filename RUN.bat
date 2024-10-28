@echo off

REM Check if venv folder exists
IF EXIST venv (
    echo Virtual environment exists.

) ELSE (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating Virtual Environment
call venv\Scripts\activate

REM Checking packages
FOR /F "usebackq tokens=*" %%i IN (reqs.txt) DO (
    pip show %%i >nul 2>&1
    IF ERRORLEVEL 1 (
        echo Installing package %%i...
        pip install %%i
    )
)

REM Run pip install command in the virtual environment console
python prototype.py
