@echo off
chcp 65001 >nul
echo ========================================
echo  GitHub Repository Setup
echo ========================================
echo.

REM 检查是否已经是 Git 仓库
if exist .git (
    echo [INFO] Git repository already initialized
    goto :add_remote
)

echo [Step 1/5] Initializing Git repository...
git init
if errorlevel 1 (
    echo [ERROR] Failed to initialize Git repository
    pause
    exit /b 1
)
echo [OK] Repository initialized

:add_remote
echo.
echo [Step 2/5] Configure Git user
set /p username="Enter your name: "
set /p email="Enter your email: "
git config user.name "%username%"
git config user.email "%email%"
echo [OK] User configured

echo.
echo [Step 3/5] Adding files...
git add .
if errorlevel 1 (
    echo [ERROR] Failed to add files
    pause
    exit /b 1
)
echo [OK] Files added

echo.
echo [Step 4/5] Creating initial commit...
git commit -m "Initial commit: MCP HS Code Query Server v1.0.0"
if errorlevel 1 (
    echo [ERROR] Failed to commit
    pause
    exit /b 1
)
echo [OK] Commit created

echo.
echo ========================================
echo  Next Steps:
echo ========================================
echo.
echo 1. Create repository on GitHub:
echo    - Go to https://github.com/new
echo    - Repository name: mcp-hs-code-query
echo    - Description: MCP server for intelligent HS code queries
echo    - Make it Public
echo    - DO NOT initialize with README/license/.gitignore
echo    - Click "Create repository"
echo.
echo 2. After creating, run these commands:
echo    (Replace YOUR_USERNAME with your GitHub username)
echo.
echo    git remote add origin https://github.com/YOUR_USERNAME/mcp-hs-code-query.git
echo    git branch -M main
echo    git push -u origin main
echo.
echo 3. Create a tag and push:
echo    git tag v1.0.0
echo    git push origin v1.0.0
echo.
echo 4. On GitHub, create a Release with tag v1.0.0
echo.
echo ========================================
echo.
pause

:menu
echo.
echo What would you like to do?
echo [1] Add remote repository
echo [2] Push to GitHub
echo [3] Create and push tag v1.0.0
echo [4] Exit
echo.
set /p choice="Enter option [1-4]: "

if "%choice%"=="1" goto add_remote_url
if "%choice%"=="2" goto push
if "%choice%"=="3" goto create_tag
if "%choice%"=="4" goto end
goto menu

:add_remote_url
echo.
set /p github_username="Enter your GitHub username: "
echo.
echo Adding remote: https://github.com/%github_username%/mcp-hs-code-query.git
git remote add origin https://github.com/%github_username%/mcp-hs-code-query.git
if errorlevel 1 (
    echo [WARNING] Remote might already exist, trying to update...
    git remote set-url origin https://github.com/%github_username%/mcp-hs-code-query.git
)
echo [OK] Remote configured
goto menu

:push
echo.
echo Pushing to GitHub...
git branch -M main
git push -u origin main
if errorlevel 1 (
    echo [ERROR] Push failed. Make sure:
    echo   1. You created the repository on GitHub
    echo   2. You have the correct credentials
    echo   3. The remote URL is correct
    pause
    goto menu
)
echo.
echo [SUCCESS] Code pushed to GitHub!
goto menu

:create_tag
echo.
echo Creating tag v1.0.0...
git tag v1.0.0
git push origin v1.0.0
if errorlevel 1 (
    echo [ERROR] Failed to push tag
    pause
    goto menu
)
echo.
echo [SUCCESS] Tag v1.0.0 created and pushed!
echo.
echo Next: Go to GitHub and create a Release with this tag
echo https://github.com/YOUR_USERNAME/mcp-hs-code-query/releases/new
goto menu

:end
echo.
echo All done! Your repository is ready.
echo.
echo Next steps:
echo 1. Visit: https://github.com/YOUR_USERNAME/mcp-hs-code-query
echo 2. Create a Release with tag v1.0.0
echo 3. Add PYPI_API_TOKEN to GitHub Secrets
echo.
pause
exit /b 0
