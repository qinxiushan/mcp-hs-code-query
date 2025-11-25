@echo off
chcp 65001 >nul
REM ========================================
REM  MCP HS Code Query - Quick Publish Guide
REM  Token configured - Ready to publish!
REM ========================================

echo.
echo ========================================================
echo    MCP HS Code Query - Publish to PyPI
echo    Token configured [OK]
echo ========================================================
echo.

:menu
echo Please select an option:
echo.
echo [1] Test Server Functions
echo [2] Build Package (Required first time)
echo [3] Publish to TestPyPI (Test environment - Recommended)
echo [4] Publish to PyPI (Production - Available worldwide)
echo [5] Clean Build Files
echo [6] Exit
echo.

set /p choice="Enter option [1-6]: "

if "%choice%"=="1" goto test
if "%choice%"=="2" goto build
if "%choice%"=="3" goto publish_test
if "%choice%"=="4" goto publish_prod
if "%choice%"=="5" goto clean
if "%choice%"=="6" goto end
echo Invalid option, please try again
goto menu

:test
echo.
echo ========================================
echo  Testing MCP Server Functions
echo ========================================
echo.
python test_mcp_server.py
echo.
pause
goto menu

:build
echo.
echo ========================================
echo  Step 1/4: Clean old files
echo ========================================
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist mcp_hs_code_query.egg-info rmdir /s /q mcp_hs_code_query.egg-info
echo [OK] Cleanup complete

echo.
echo ========================================
echo  Step 2/4: Install build tools
echo ========================================
pip install --upgrade build twine
echo [OK] Tools installed

echo.
echo ========================================
echo  Step 3/4: Build package
echo ========================================
python -m build
echo [OK] Build complete

echo.
echo ========================================
echo  Step 4/4: Check package
echo ========================================
twine check dist/*
echo [OK] Check complete

echo.
echo ========================================================
echo  SUCCESS! Package built successfully!
echo ========================================================
echo.
echo Generated files:
dir /b dist
echo.
echo Next step: Choose [3] to publish to TestPyPI first, or [4] for production PyPI
echo.
pause
goto menu

:publish_test
echo.
echo ========================================
echo  Publish to TestPyPI (Test environment)
echo ========================================
echo.
echo Note: This is a test environment, safe to experiment
echo.
set /p confirm="Continue? [y/n]: "
if /i "%confirm%" NEQ "y" goto menu

echo.
echo Uploading to TestPyPI...
twine upload --repository testpypi dist/*

if errorlevel 1 (
    echo.
    echo [ERROR] Upload failed! Please check error messages
    echo.
    pause
    goto menu
)

echo.
echo ========================================================
echo  SUCCESS! Published to TestPyPI!
echo ========================================================
echo.
echo Test installation:
echo   pip install --index-url https://test.pypi.org/simple/ mcp-hs-code-query
echo.
echo If tests pass, choose [4] to publish to production PyPI
echo.
pause
goto menu

:publish_prod
echo.
echo ========================================
echo  Publish to Production PyPI
echo ========================================
echo.
echo WARNING: 
echo   - Published packages are visible worldwide
echo   - Cannot delete published versions
echo   - Can only update by publishing new versions
echo.
set /p confirm1="Confirm publishing to production PyPI? Type 'yes': "
if /i "%confirm1%" NEQ "yes" goto menu

echo.
echo Final confirmation: Current version is 1.0.0
set /p confirm2="Confirm publishing version 1.0.0? [yes/no]: "
if /i "%confirm2%" NEQ "yes" goto menu

echo.
echo Uploading to PyPI...
echo.
twine upload dist/*

if errorlevel 1 (
    echo.
    echo [ERROR] Upload failed! Please check error messages
    echo.
    pause
    goto menu
)

echo.
echo ========================================================
echo.
echo           SUCCESS! Published to PyPI!
echo.
echo ========================================================
echo.
echo Congratulations! Your MCP server is now published!
echo.
echo ========================================
echo  Users can now use it with:
echo ========================================
echo.
echo Method 1: Using uvx (no installation needed)
echo   uvx mcp-hs-code-query
echo.
echo Method 2: Install and use
echo   pip install mcp-hs-code-query
echo   mcp-hs-code-query
echo.
echo Method 3: Configure in Claude Desktop
echo   {
echo     "mcpServers": {
echo       "hs-code-query": {
echo         "command": "uvx",
echo         "args": ["mcp-hs-code-query"]
echo       }
echo     }
echo   }
echo.
echo ========================================
echo  View your package:
echo ========================================
echo   https://pypi.org/project/mcp-hs-code-query/
echo.
echo ========================================
echo  Recommended next steps:
echo ========================================
echo   1. Check your package page on PyPI
echo   2. Create GitHub repository and push code
echo   3. Create GitHub Release (v1.0.0)
echo   4. Share on social media
echo   5. Add to MCP server list
echo.
pause
goto menu

:clean
echo.
echo Cleaning build files...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist mcp_hs_code_query.egg-info rmdir /s /q mcp_hs_code_query.egg-info
echo [OK] Cleanup complete
echo.
pause
goto menu

:end
echo.
echo Thank you! Goodbye!
echo.
timeout /t 2 >nul
exit /b 0
