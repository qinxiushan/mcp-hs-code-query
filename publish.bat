@echo off
REM HS Code Query MCP Server - 发布辅助脚本

echo ========================================
echo  MCP HS Code Query - 发布辅助工具
echo ========================================
echo.

:menu
echo 请选择操作:
echo 1. 安装构建工具
echo 2. 本地构建测试
echo 3. 发布到 TestPyPI (测试)
echo 4. 发布到正式 PyPI
echo 5. 清理构建文件
echo 6. 退出
echo.

set /p choice="请输入选项 (1-6): "

if "%choice%"=="1" goto install_tools
if "%choice%"=="2" goto build_test
if "%choice%"=="3" goto publish_test
if "%choice%"=="4" goto publish_prod
if "%choice%"=="5" goto clean
if "%choice%"=="6" goto end
goto menu

:install_tools
echo.
echo [步骤1] 安装构建工具...
pip install build twine
echo.
echo 安装完成！
pause
goto menu

:build_test
echo.
echo [步骤2] 清理旧文件...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist mcp_hs_code_query.egg-info rmdir /s /q mcp_hs_code_query.egg-info

echo.
echo [步骤2] 构建包...
python -m build

echo.
echo [步骤2] 检查包...
twine check dist/*

echo.
echo 构建完成！文件位于 dist/ 目录
echo.
echo 测试安装:
echo   pip install dist\mcp_hs_code_query-1.0.0-py3-none-any.whl
echo.
echo 测试 uvx:
echo   uvx --from dist\mcp_hs_code_query-1.0.0-py3-none-any.whl mcp-hs-code-query
echo.
pause
goto menu

:publish_test
echo.
echo [步骤3] 发布到 TestPyPI...
echo.
echo 注意: 需要在 https://test.pypi.org/ 注册账号
echo       并配置 .pypirc 文件
echo.
set /p confirm="确认继续? (y/n): "
if /i "%confirm%" NEQ "y" goto menu

twine upload --repository testpypi dist/*

echo.
echo 发布成功！
echo.
echo 测试安装:
echo   pip install --index-url https://test.pypi.org/simple/ mcp-hs-code-query
echo.
pause
goto menu

:publish_prod
echo.
echo [步骤4] 发布到正式 PyPI
echo.
echo ⚠️  警告: 这将发布到正式 PyPI，无法撤销！
echo.
set /p version="请确认版本号 (当前: 1.0.0): "
set /p confirm="确认发布到 PyPI? (yes/no): "
if /i "%confirm%" NEQ "yes" goto menu

echo.
echo 正在上传...
twine upload dist/*

echo.
echo ========================================
echo  🎉 发布成功！
echo ========================================
echo.
echo 其他用户现在可以通过以下方式使用:
echo   uvx mcp-hs-code-query
echo.
echo 或安装:
echo   pip install mcp-hs-code-query
echo.
echo 请在 GitHub 创建 Release 并打标签:
echo   git tag v1.0.0
echo   git push origin v1.0.0
echo.
pause
goto menu

:clean
echo.
echo [清理] 删除构建文件...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist mcp_hs_code_query.egg-info rmdir /s /q mcp_hs_code_query.egg-info
echo 清理完成！
echo.
pause
goto menu

:end
echo.
echo 感谢使用！
exit /b 0
