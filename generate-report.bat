@echo off
setlocal

cd /d "C:\Users\Shiva Dev\Downloads\FH - Load Testing"

set JMETER_HOME=C:\apache-jmeter-5.6.3
set JTL=results\run-result.jtl
set TEMPLATE_DIR=%CD%\report-template

if "%~1"=="" (
    echo Usage: generate-report.bat [report-folder] [report-title]
    echo Example: generate-report.bat run-1user "FH Stage API - 1 User Baseline"
    pause
    exit /b 1
)

set REPORT=reports\%~1

if "%~2"=="" (
    set REPORT_TITLE=FH Stage API - %~1
) else (
    set REPORT_TITLE=%~2
)

if not exist "%JTL%" (
    echo JTL file not found: %JTL%
    echo Run a test first.
    pause
    exit /b 1
)

if exist "%REPORT%" rmdir /s /q "%REPORT%"

echo Generating HTML report...
echo Title: %REPORT_TITLE%
call "%JMETER_HOME%\bin\jmeter.bat" -g "%JTL%" -o "%REPORT%" -Jjmeter.reportgenerator.report_title="%REPORT_TITLE%" -Jjmeter.reportgenerator.exporter.html.property.template_dir="%TEMPLATE_DIR%"
if errorlevel 1 (
    echo HTML report generation failed.
    pause
    exit /b 1
)

echo Done. Open %REPORT%\index.html
pause
