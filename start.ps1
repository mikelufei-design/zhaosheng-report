Write-Host "招生智能体系统 正在启动..." -ForegroundColor Green
$python = "C:\Users\唐先生\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$workdir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $workdir
Write-Host "打开浏览器访问: http://127.0.0.1:8080" -ForegroundColor Cyan
& $python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload --log-level info
