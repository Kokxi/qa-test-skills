@echo off
chcp 65001 >nul
setlocal

REM Usage: publish-all.bat <version>   (default: 1.8.0)
set "VER=%~1"
if "%VER%"=="" set "VER=1.8.0"

echo Publishing all skills with version %VER% ...
echo.

call clawhub skill publish ./skills/qa-test-skills --slug qa-test-skills --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-agent-testing --slug qa-agent-testing --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-ai-blindspot-compensation --slug qa-ai-blindspot-compensation --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-ai-context-engineering --slug qa-ai-context-engineering --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-ai-output-critique --slug qa-ai-output-critique --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-ai-prompt-strategy --slug qa-ai-prompt-strategy --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-api-testing --slug qa-api-testing --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-boundary-deep-dive --slug qa-boundary-deep-dive --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-bug-lifecycle --slug qa-bug-lifecycle --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-bug-reporting --slug qa-bug-reporting --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-bug-root-cause-analysis --slug qa-bug-root-cause-analysis --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-ci-cd-testing --slug qa-ci-cd-testing --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-code-review-for-test --slug qa-code-review-for-test --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-combination-strategy --slug qa-combination-strategy --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-critical-thinking --slug qa-critical-thinking --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-domain-modeling --slug qa-domain-modeling --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-execution-observation --slug qa-execution-observation --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-expert-review --slug qa-expert-review --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-exploratory-testing --slug qa-exploratory-testing --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-heuristic-checklist --slug qa-heuristic-checklist --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-input-validation --slug qa-input-validation --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-mobile-testing --slug qa-mobile-testing --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-output-validation --slug qa-output-validation --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-quality-metrics --slug qa-quality-metrics --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-question-framework --slug qa-question-framework --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-regression-testing --slug qa-regression-testing --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-release-risk-governance --slug qa-release-risk-governance --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-req-deconstruction --slug qa-req-deconstruction --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-requirement-review --slug qa-requirement-review --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-retrospective --slug qa-retrospective --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-risk-intuition --slug qa-risk-intuition --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-scenario-tree --slug qa-scenario-tree --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-shift-left --slug qa-shift-left --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-shift-right --slug qa-shift-right --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-specialized-testing --slug qa-specialized-testing --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-stakeholder-communication --slug qa-stakeholder-communication --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-state-transition --slug qa-state-transition --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-team-coaching --slug qa-team-coaching --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-tech-debt-management --slug qa-tech-debt-management --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-tech-selection --slug qa-tech-selection --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-test-automation-arch --slug qa-test-automation-arch --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-test-case-design --slug qa-test-case-design --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-test-data-engineering --slug qa-test-data-engineering --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-test-env-data --slug qa-test-env-data --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-test-estimation --slug qa-test-estimation --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-test-leadership --slug qa-test-leadership --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-test-reporting --slug qa-test-reporting --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-test-strategy-design --slug qa-test-strategy-design --version %VER%
timeout /t 2 /nobreak >nul

call clawhub skill publish ./skills/qa-testability-advocacy --slug qa-testability-advocacy --version %VER%
timeout /t 2 /nobreak >nul

echo.
echo All skills published with version %VER%!
endlocal
pause
