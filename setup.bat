@echo off
echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing required packages from requirements.txt...
pip install -r requirements.txt

echo Installing SSL certificates...
python -m certifi

echo Verifying installation...
pip list

echo Setup completed successfully.
pause
