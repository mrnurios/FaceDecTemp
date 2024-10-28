@echo off

REM Check if venv folder exists
IF EXIST venv (
    echo Virtual environment exists.

) ELSE (
    echo Creating virtual environment...
    python -m venv venv
)

REM Checking packages
call venv\Scripts\activate
pip install -r reqs.txt

REM Run pip install command in the virtual environment console
python prototype.py
