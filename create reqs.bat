@echo off

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

echo Generating requirements.txt file...
pip freeze > requirements.txt

echo Deactivating virtual environment...
deactivate

echo Done.
