# QA Test Skills 鎵归噺鍙戝竷鑴氭湰 (Windows PowerShell)
# 灏嗘墍鏈?8涓猻kills鍙戝竷鍒癈lawHub

Write-Host "=== QA Test Skills 鎵归噺鍙戝竷鑴氭湰 ===" -ForegroundColor Cyan
Write-Host ""

# 妫€鏌lawhub CLI鏄惁瀹夎
if (-not (Get-Command clawhub -ErrorAction SilentlyContinue)) {
    Write-Host "鉂?clawhub CLI 鏈畨瑁? -ForegroundColor Red
    Write-Host "璇峰厛瀹夎: npm i -g clawhub" -ForegroundColor Yellow
    exit 1
}

# 妫€鏌ユ槸鍚﹀凡鐧诲綍
Write-Host "妫€鏌ョ櫥褰曠姸鎬?.."
$loginCheck = clawhub whoami 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "鉂?鏈櫥褰旵lawHub" -ForegroundColor Red
    Write-Host "璇峰厛鐧诲綍: clawhub login" -ForegroundColor Yellow
    exit 1
}

Write-Host "鉁?宸茬櫥褰旵lawHub" -ForegroundColor Green
Write-Host ""

# 鍙戝竷鍏僺kill
Write-Host "鍙戝竷鍏僺kill: qa-test-skills" -ForegroundColor Yellow
clawhub skill publish ./skills/qa-test-skills --slug qa-test-skills --version 1.3.0
if ($LASTEXITCODE -eq 0) {
    Write-Host "鉁?qa-test-skills 鍙戝竷鎴愬姛" -ForegroundColor Green
} else {
    Write-Host "鉂?qa-test-skills 鍙戝竷澶辫触" -ForegroundColor Red
}
Write-Host ""

# 鎵归噺鍙戝竷鎵€鏈塻kills
Write-Host "鎵归噺鍙戝竷鎵€鏈塻kills..." -ForegroundColor Yellow
Write-Host ""

$skills = Get-ChildItem -Path ./skills -Directory
$successCount = 0
$failCount = 0

foreach ($skillDir in $skills) {
    $skillName = $skillDir.Name
    
    # 璺宠繃鍏僺kill锛堝凡鍙戝竷锛?    if ($skillName -eq "qa-test-skills") {
        continue
    }
    
    # 璺宠繃闈炴妧鑳界洰褰?    if (-not (Test-Path "$($skillDir.FullName)/SKILL.md")) {
        Write-Host "鈿狅笍  璺宠繃 $skillName (娌℃湁SKILL.md鏂囦欢)" -ForegroundColor Yellow
        continue
    }
    
    Write-Host "鍙戝竷: $skillName" -ForegroundColor Cyan
    clawhub skill publish $skillDir.FullName --slug $skillName --version 1.3.0
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "鉁?$skillName 鍙戝竷鎴愬姛" -ForegroundColor Green
        $successCount++
    } else {
        Write-Host "鉂?$skillName 鍙戝竷澶辫触" -ForegroundColor Red
        $failCount++
    }
    Write-Host ""
    
    # 姣忔鍙戝竷鍚庣瓑寰?绉掞紝閬垮厤瑙﹀彂闄愭祦
    Start-Sleep -Seconds 2
}

Write-Host "=== 鎵归噺鍙戝竷瀹屾垚 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "鍙戝竷缁撴灉:" -ForegroundColor Yellow
Write-Host "鉁?鎴愬姛: $successCount 涓? -ForegroundColor Green
Write-Host "鉂?澶辫触: $failCount 涓? -ForegroundColor Red
Write-Host ""
Write-Host "鎬诲叡鍙戝竷: $($successCount + $failCount + 1) 涓猻kills (1涓厓skill + $($successCount + $failCount)涓妧鑳?" -ForegroundColor Cyan
Write-Host ""
Write-Host "鐢ㄦ埛鍙互閫氳繃浠ヤ笅鏂瑰紡瀹夎:" -ForegroundColor Yellow
Write-Host "1. 瀹夎鍏僺kill: clawhub install @kokxi/qa-test-skills" -ForegroundColor White
Write-Host "2. 鏌ョ湅README鑾峰彇瀹屾暣瀹夎璇存槑" -ForegroundColor White