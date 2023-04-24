@echo off

setlocal

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

echo Deactivating virtual environment...
deactivate

echo Done.
