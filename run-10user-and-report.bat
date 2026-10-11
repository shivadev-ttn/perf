@echo off
setlocal

cd /d "C:\Users\Shiva Dev\Downloads\FH - Load Testing"

set JMETER_HOME=C:\apache-jmeter-5.6.3
set JTL=results\run-result.jtl
set REPORT=reports\run-10user
set REPORT_TITLE=FH Stage API - 10 Users
set TEMPLATE_DIR=%CD%\report-template

if not exist results mkdir results
if not exist reports mkdir reports

echo.
echo IMPORTANT: Enable only "02 - 10 Users" thread group in FH - Stage.jmx before running.
echo.

if exist "%JTL%" del /q "%JTL%"

echo [1/2] Running load test...
call "%JMETER_HOME%\bin\jmeter.bat" -n -t "FH - Stage.jmx" -l "%JTL%"
if errorlevel 1 (
    echo.
    echo Test run failed. HTML report not generated.
    pause
    exit /b 1
)

if not exist "%JTL%" (
    echo.
    echo JTL file not found: %JTL%
    pause
    exit /b 1
)

if exist "%REPORT%" rmdir /s /q "%REPORT%"

echo [2/2] Generating HTML report...
call "%JMETER_HOME%\bin\jmeter.bat" -g "%JTL%" -o "%REPORT%" -Jjmeter.reportgenerator.report_title="%REPORT_TITLE%" -Jjmeter.reportgenerator.exporter.html.property.template_dir="%TEMPLATE_DIR%"
if errorlevel 1 (
    echo.
    echo HTML report generation failed.
    pause
    exit /b 1
)

echo.
echo Done.
echo Report title: %REPORT_TITLE%
echo JTL: %JTL%
echo Report: %REPORT%\index.html
pause
