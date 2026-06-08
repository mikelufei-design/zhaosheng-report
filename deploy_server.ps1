# ========================================================
#  招生智能体系统 - Windows Server 部署脚本
#  在腾讯云 Web 终端 (PowerShell) 中运行
# ========================================================

Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "  招生智能体系统 - 服务器部署" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

$projectDir = "C:\zhaosheng-agent"
Write-Host "[1/5] 创建项目目录: $projectDir" -ForegroundColor Yellow

# 创建目录
if (-not (Test-Path $projectDir)) {
    New-Item -ItemType Directory -Path $projectDir -Force | Out-Null
}

Set-Location $projectDir

# 检测 Python
Write-Host "[2/5] 检测 Python..." -ForegroundColor Yellow
$pythonPath = "python"
try {
    $ver = & $pythonPath --version 2>&1
    Write-Host "  Python 版本: $ver" -ForegroundColor Green
} catch {
    Write-Host "  未找到 Python，请从 https://www.python.org/downloads/ 安装 Python 3.10+"
    Write-Host "  安装时记得勾选 'Add Python to PATH'"
    exit 1
}

# 创建 requirements.txt
Write-Host "[3/5] 准备依赖文件..." -ForegroundColor Yellow
@"
fastapi>=0.100.0
uvicorn>=0.20.0
pandas>=2.0.0
openpyxl>=3.1.0
jinja2>=3.1.0
python-multipart>=0.0.6
"@ | Out-File -FilePath "$projectDir\requirements.txt" -Encoding utf8

# 安装依赖
Write-Host "[4/5] 安装 Python 依赖..." -ForegroundColor Yellow
& $pythonPath -m pip install -r "$projectDir\requirements.txt" -i https://pypi.tuna.tsinghua.edu.cn/simple

# 打开防火墙端口
Write-Host "[5/5] 配置 Windows 防火墙..." -ForegroundColor Yellow
try {
    New-NetFirewallRule -DisplayName "招生智能体系统(5000)" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow -ErrorAction SilentlyContinue
    Write-Host "  防火墙端口 5000 已开放" -ForegroundColor Green
} catch {
    Write-Host "  防火墙配置失败（可能需要管理员权限）" -ForegroundColor Red
}

Write-Host ""
Write-Host "========  部署准备完成！=========" -ForegroundColor Green
Write-Host "接下来请将项目文件放入: $projectDir" -ForegroundColor Cyan
Write-Host "然后运行: cd $projectDir && python -m uvicorn app:app --host 0.0.0.0 --port 5000 --log-level info" -ForegroundColor White
Write-Host ""
Write-Host "或者使用后台运行脚本: start_prod.ps1" -ForegroundColor Cyan
