@echo off
chcp 65001 >nul
echo ========================================
echo   QA Test Skills - Publish All Skills
echo ========================================
echo.

:: Check if clawhub is installed
where clawhub >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] clawhub CLI not installed
    echo Please install: npm i -g clawhub
    pause
    exit /b 1
)

:: Check login status
echo Checking login status...
clawhub whoami >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Not logged in to ClawHub
    echo Please login first: clawhub login
    pause
    exit /b 1
)

echo [OK] Logged in to ClawHub
echo.

:: Publish meta skill
echo Publishing meta skill: qa-test-skills
clawhub skill publish ./skills/qa-test-skills --slug qa-test-skills --version 1.3.0
if %errorlevel% equ 0 (
    echo [OK] qa-test-skills published successfully
) else (
    echo [FAIL] qa-test-skills publish failed
)
echo.

:: Publish all skills
echo Publishing all skills...
echo.

set success=0
set fail=0

for /d %%i in (skills\*) do (
    set "skillname=%%~nxi"
    if "!skillname!"=="qa-test-skills" goto :skip
    if not exist "%%i\SKILL.md" goto :skip
    
    echo Publishing: !skillname!
    clawhub skill publish "%%i" --slug "!skillname!" --version 1.3.0
    if !errorlevel! equ 0 (
        echo [OK] !skillname! published
        set /a success+=1
    ) else (
        echo [FAIL] !skillname! publish failed
        set /a fail+=1
    )
    echo.
    timeout /t 2 /nobreak >nul
    
    :skip
)

echo ========================================
echo   Publish Complete
echo ========================================
echo.
echo Results:
echo   Success: %success%
echo   Failed: %fail%
echo   Total: %success% + %fail% + 1 (meta skill)
echo.
echo Users can install with:
echo   clawhub install @kokxi/qa-test-skills
echo.
pause