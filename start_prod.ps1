# ========================================================
#  招生智能体系统 - 生产环境启动脚本
#  在 PowerShell 中运行此脚本启动后台服务
# ========================================================

$projectDir = "C:\zhaosheng-agent"
$logFile = "$projectDir\server.log"

Write-Host "招生智能体系统 正在启动..." -ForegroundColor Green
Write-Host "项目目录: $projectDir" -ForegroundColor Cyan
Write-Host "访问地址: http://服务器IP:5000" -ForegroundColor Cyan
Write-Host "日志文件: $logFile" -ForegroundColor Cyan
Write-Host ""

# 切换到项目目录
Set-Location $projectDir

# 确保日志目录存在
$null = New-Item -ItemType Directory -Path (Split-Path $logFile -Parent) -Force -ErrorAction SilentlyContinue

# 启动服务（后台运行）
$startInfo = New-Object System.Diagnostics.ProcessStartInfo
$startInfo.FileName = "python"
$startInfo.Arguments = "-m uvicorn app:app --host 0.0.0.0 --port 5000 --log-level info"
$startInfo.WorkingDirectory = $projectDir
$startInfo.RedirectStandardOutput = $true
$startInfo.RedirectStandardError = $true
$startInfo.UseShellExecute = $false
$startInfo.CreateNoWindow = $true

$process = New-Object System.Diagnostics.Process
$process.StartInfo = $startInfo
$process.Start() | Out-Null

# 等待几秒确认启动
Start-Sleep -Seconds 3
if (-not $process.HasExited) {
    Write-Host "✅ 服务已成功启动！进程ID: $($process.Id)" -ForegroundColor Green
    Write-Host "   访问地址: http://服务器IP:5000" -ForegroundColor White
    Write-Host "   停止服务: taskkill /F /PID $($process.Id)" -ForegroundColor Gray
} else {
    Write-Host "❌ 服务启动失败" -ForegroundColor Red
    $stderr = $process.StandardError.ReadToEnd()
    Write-Host $stderr
}
