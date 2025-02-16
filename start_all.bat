@echo off
setlocal enabledelayedexpansion

REM 配置参数
set "PROJECT_DIR=%~dp0"
set "PYTHON_VERSION=3.11.9"
set "VENV_DIR=%PROJECT_DIR%.venv"
set "REQUIREMENTS=%PROJECT_DIR%requirements.txt"
set "PYTHON_INSTALL_DIR=%PROJECT_DIR%Python%PYTHON_VERSION%"
set "PYTHON_EXE="
set "MAIN_SCRIPT=%PROJECT_DIR%auto_resume_submission_script_for_boss.py"
set "CHROMEDRIVER_DIR=%PROJECT_DIR%/chromedriver-win64"

REM 检查系统PATH中的Python是否可用
python --version >nul 2>&1
if not errorlevel 1 (
    echo [INFO] Found Python in system PATH.
    for /f "delims=" %%P in ('where python') do (
        set "SYSTEM_PYTHON=%%P"
        goto :check_venv
    )
)

:check_venv
REM 检查虚拟环境是否存在
if exist "%VENV_DIR%\pyvenv.cfg" (
    echo [INFO] Virtual environment already exists at: %VENV_DIR%
    goto :install_dependencies
)

REM 创建虚拟环境
echo [INFO] Creating virtual environment...
if defined SYSTEM_PYTHON (
    "%SYSTEM_PYTHON%" -m venv "%VENV_DIR%"
) else if exist "%PYTHON_INSTALL_DIR%\python.exe" (
    "%PYTHON_INSTALL_DIR%\python.exe" -m venv "%VENV_DIR%"
) else (
    echo [ERROR] No valid Python found for venv creation
    exit /b 1
)
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    exit /b 1
)

:install_dependencies
REM 安装依赖
echo [INFO] Installing dependencies...
"%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip --no-warn-script-location
if errorlevel 1 (
    echo [ERROR] Failed to upgrade pip
    exit /b 1
)

if exist "%REQUIREMENTS%" (
    "%VENV_DIR%\Scripts\python.exe" -m pip install -r "%REQUIREMENTS%" --no-warn-script-location -i https://pypi.tuna.tsinghua.edu.cn/simple
    if errorlevel 1 (
        echo [ERROR] Failed to install requirements
        exit /b 1
    )
) else (
    echo [ERROR] requirements.txt not found
    exit /b 1
)

REM 检查ChromeDriver=====================================================================

REM 获取Chrome版本号
for /f "tokens=3 delims= " %%i in ('reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version') do set chromeVersion=%%i
echo Chrome version: !chromeVersion!
REM 检查Chrome是否安装以及版本号是否符合要求
if "!chromeVersion!" == "" (
    echo Chrome is not installed or the version cannot be detected.
    pause
    exit /b 1
)


if not exist "%CHROMEDRIVER_DIR%\chromedriver.exe" (

    echo chromedriver.exe not found, downloading latest version from Google official site...
    rem 获取ChromeDriver版本号对应url
    
    set win64_url=https://storage.googleapis.com/chrome-for-testing-public/%chromeVersion%/win64/chromedriver-win64.zip

    rem 下载对应的ChromeDriver
    powershell -Command "Invoke-WebRequest -Uri '!win64_url!' -OutFile '!PROJECT_DIR!\chromedriver.zip'"

    echo 下载完成！
    if exist "%PROJECT_DIR%\chromedriver.zip" (
        REM 解压并清理
        powershell -Command "Expand-Archive -Path '!PROJECT_DIR!\chromedriver.zip' -DestinationPath '!PROJECT_DIR!' -Force" 
        
    REM 验证是否下载成功
        if not exist "%CHROMEDRIVER_DIR%\chromedriver.exe" (
            echo ChromeDriver download failed,Check if the compressed file is damaged. If it is not damaged, decompress it by yourself and run it again
            pause
            exit /b 1
        )
    ) else (
        echo Failed to download ChromeDriver,Try upgrading Chrome to the latest version
        pause
        exit /b 1
    )
    del "%PROJECT_DIR%\chromedriver.zip"
    echo If it is the first time installing chromedriver automatically and there is an error where the driver cannot be found when starting the py file, you can try running this startup program again directly
) else (
    echo chromedriver.exe already exists in the project directory.
)
    

REM 启动部分 ==============================================
if not exist "%MAIN_SCRIPT%" (
    echo [ERROR] Main script '%MAIN_SCRIPT%' not found
    pause
    exit /b 1
)

echo [INFO] Starting application...
"%VENV_DIR%\Scripts\python.exe" "%MAIN_SCRIPT%"
if errorlevel 1 (
    echo [ERROR] Application exited with error code !errorlevel!
    pause
    exit /b 1
)

REM ========================================================

echo [SUCCESS] Environment setup and application execution completed
exit /b 0

:install_python
REM 下载并安装Python（保持原有安装逻辑不变）
echo [INFO] Downloading Python %PYTHON_VERSION%...
set "PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-amd64.exe"
set "INSTALLER_PATH=%PROJECT_DIR%python_installer.exe"

powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%INSTALLER_PATH%'"
if errorlevel 1 (
    echo [ERROR] Failed to download Python installer
    exit /b 1
)

echo [INFO] Installing Python to %PYTHON_INSTALL_DIR%...
start /wait "" "%INSTALLER_PATH%" /quiet InstallAllUsers=0 TargetDir="%PYTHON_INSTALL_DIR%" Include_launcher=0 PrependPath=0
del "%INSTALLER_PATH%"

if not exist "%PYTHON_INSTALL_DIR%\python.exe" (
    echo [ERROR] Python installation failed
    exit /b 1
)
set "PYTHON_EXE=%PYTHON_INSTALL_DIR%\python.exe"
goto :check_venv