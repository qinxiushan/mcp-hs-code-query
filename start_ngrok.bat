@echo off
chcp 65001 >nul
echo ========================================
echo HS 编码查询 API - ngrok 启动脚本
echo ========================================
echo.

REM 检查 ngrok 是否安装
where ngrok >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 ngrok
    echo.
    echo 请先安装 ngrok:
    echo 1. 访问 https://ngrok.com/download
    echo 2. 下载并解压 ngrok.exe
    echo 3. 将 ngrok.exe 添加到系统 PATH 或放到当前目录
    echo.
    pause
    exit /b 1
)

echo [1/3] 启动 API 服务...
start "HS Code API" python api_server.py

echo [2/3] 等待 API 服务启动...
timeout /t 5 /nobreak >nul

echo [3/3] 启动 ngrok 内网穿透...
echo.
echo ========================================
echo ngrok 隧道启动中...
echo ========================================
echo.
echo 公网地址将显示在下方窗口中
echo ngrok 控制面板: http://localhost:4040
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

ngrok http 8000

pause
