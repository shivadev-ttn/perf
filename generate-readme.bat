@echo off
setlocal

cd /d "%~dp0"

set CSV=%~dp0Aggregate_Report.csv
set JMX=%~dp0FH - Stage.jmx
set SCRIPT=%~dp0scripts\generate-load-test-readme.py

if not exist "%CSV%" (
    echo Aggregate_Report.csv not found in:
    echo %~dp0
    echo Export Aggregate Report from JMeter first.
    pause
    exit /b 1
)

if not exist "%JMX%" (
    echo FH - Stage.jmx not found in:
    echo %~dp0
    pause
    exit /b 1
)

if not exist "%SCRIPT%" (
    echo Script not found: %SCRIPT%
    pause
    exit /b 1
)

echo Generating README from Aggregate Report...
python "%SCRIPT%" "%CSV%" "%JMX%"
if errorlevel 1 (
    echo README generation failed.
    pause
    exit /b 1
)

echo Done.
pause
