# QA Test Skills 批量发布脚本 (Windows PowerShell)
# 将所有48个skills发布到ClawHub

Write-Host "=== QA Test Skills 批量发布脚本 ===" -ForegroundColor Cyan
Write-Host ""

# 检查clawhub CLI是否安装
if (-not (Get-Command clawhub -ErrorAction SilentlyContinue)) {
    Write-Host "❌ clawhub CLI 未安装" -ForegroundColor Red
    Write-Host "请先安装: npm i -g clawhub" -ForegroundColor Yellow
    exit 1
}

# 检查是否已登录
Write-Host "检查登录状态..."
$loginCheck = clawhub whoami 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 未登录ClawHub" -ForegroundColor Red
    Write-Host "请先登录: clawhub login" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ 已登录ClawHub" -ForegroundColor Green
Write-Host ""

# 发布元skill
Write-Host "发布元skill: qa-test-skills" -ForegroundColor Yellow
clawhub skill publish ./skills/qa-test-skills --slug qa-test-skills --version 1.3.0
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ qa-test-skills 发布成功" -ForegroundColor Green
} else {
    Write-Host "❌ qa-test-skills 发布失败" -ForegroundColor Red
}
Write-Host ""

# 批量发布所有skills
Write-Host "批量发布所有skills..." -ForegroundColor Yellow
Write-Host ""

$skills = Get-ChildItem -Path ./skills -Directory
$successCount = 0
$failCount = 0

foreach ($skillDir in $skills) {
    $skillName = $skillDir.Name
    
    # 跳过元skill（已发布）
    if ($skillName -eq "qa-test-skills") {
        continue
    }
    
    # 跳过非技能目录
    if (-not (Test-Path "$($skillDir.FullName)/SKILL.md")) {
        Write-Host "⚠️  跳过 $skillName (没有SKILL.md文件)" -ForegroundColor Yellow
        continue
    }
    
    Write-Host "发布: $skillName" -ForegroundColor Cyan
    clawhub skill publish $skillDir.FullName --slug $skillName --version 1.3.0
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ $skillName 发布成功" -ForegroundColor Green
        $successCount++
    } else {
        Write-Host "❌ $skillName 发布失败" -ForegroundColor Red
        $failCount++
    }
    Write-Host ""
    
    # 每次发布后等待2秒，避免触发限流
    Start-Sleep -Seconds 2
}

Write-Host "=== 批量发布完成 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "发布结果:" -ForegroundColor Yellow
Write-Host "✅ 成功: $successCount 个" -ForegroundColor Green
Write-Host "❌ 失败: $failCount 个" -ForegroundColor Red
Write-Host ""
Write-Host "总共发布: $($successCount + $failCount + 1) 个skills (1个元skill + $($successCount + $failCount)个技能)" -ForegroundColor Cyan
Write-Host ""
Write-Host "用户可以通过以下方式安装:" -ForegroundColor Yellow
Write-Host "1. 安装元skill: clawhub install @kokxi/qa-test-skills" -ForegroundColor White
Write-Host "2. 查看README获取完整安装说明" -ForegroundColor White