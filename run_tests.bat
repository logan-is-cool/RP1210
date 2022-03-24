@ECHO OFF
ECHO ..............................................................................................
ECHO :                  Welcome to the RP1210.py automatic-ish test suite!                        :
ECHO ..............................................................................................
ECHO Preparing...
REM ECHO Checking pytest installation...
REM py -m pip install -U -q pytest
REM py -m pip install -U -q pytest-cov
ECHO Preparing test directory...
ECHO Removing old source code from Test directory...
rmdir /s /q Test\RP1210
ECHO Copying source code into Test directory...
xcopy /v /s /y /q RP1210 Test\RP1210\
cd Test\test-files\ini-files
ECHO Done!
ECHO ..............................................................................................
ECHO Disconnect all RP1210 adapters before continuing.
pause
for %%f in (*.ini) do (

    if "%%~xf"==".ini" pytest -l -v -ra --tb=long --cov=RP1210 --cov-branch --cov-report term-missing --apiname %%~nf ..\..\test_genericVendor.py

)
ECHO Done
pause