@echo off
chcp 65001 >nul
echo ========================================
echo   QA Test Skills - Install All Skills
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

echo Starting installation...
echo.

:: Install meta skill
echo Installing meta skill: qa-test-skills
clawhub install @kokxi/qa-test-skills
if %errorlevel% equ 0 (
    echo [OK] qa-test-skills installed
) else (
    echo [FAIL] qa-test-skills install failed
)
echo.

:: Install all skills
echo Installing all skills...
echo.

set success=0
set fail=0

for %%s in (
    qa-test-workflow
    qa-requirement-review
    qa-req-deconstruction
    qa-risk-intuition
    qa-heuristic-checklist
    qa-scenario-tree
    qa-boundary-deep-dive
    qa-combination-strategy
    qa-state-transition
    qa-domain-modeling
    qa-ai-context-engineering
    qa-ai-prompt-strategy
    qa-ai-output-critique
    qa-ai-blindspot-compensation
    qa-output-validation
    qa-test-reporting
    qa-agent-testing
    qa-expert-review
    qa-api-testing
    qa-mobile-testing
    qa-specialized-testing
    qa-code-review-for-test
    qa-test-strategy-design
    qa-release-risk-governance
    qa-quality-metrics
    qa-test-case-design
    qa-input-validation
    qa-test-estimation
    qa-exploratory-testing
    qa-tech-debt-management
    qa-test-automation-arch
    qa-ci-cd-testing
    qa-tech-selection
    qa-test-env-data
    qa-test-data-engineering
    qa-testability-advocacy
    qa-shift-left
    qa-shift-right
    qa-defect-lifecycle
    qa-bug-reporting
    qa-bug-root-cause-analysis
    qa-execution-observation
    qa-retrospective
    qa-stakeholder-communication
    qa-team-coaching
    qa-test-leadership
    qa-critical-thinking
    qa-question-framework
) do (
    echo Installing: %%s
    clawhub install @kokxi/%%s
    if !errorlevel! equ 0 (
        echo [OK] %%s installed
        set /a success+=1
    ) else (
        echo [FAIL] %%s install failed
        set /a fail+=1
    )
    echo.
    timeout /t 1 /nobreak >nul
)

echo ========================================
echo   Installation Complete
echo ========================================
echo.
echo Results:
echo   Success: %success%
echo   Failed: %fail%
echo   Total: %success% + %fail%
echo.
echo Usage:
echo   1. Use main workflow: Please help me test this project: [requirement doc path]
echo   2. Use single skill: Help me analyze boundary: [scenario description]
echo.
pause