python -m venv env
env\scripts\activate.bat
python -m pip install -r requirements.txt
python reversi\mypackage\cppState\setup.py install
python reversi\mypackage\cppNode\setup.py install