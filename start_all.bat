@echo off
setlocal enabledelayedexpansion

REM 配置参数
set "PROJECT_DIR=%~dp0"
set "PYTHON_VERSION=3.11.9"
set "PYTHON_DIR=%PROJECT_DIR%python"
set "PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-embed-amd64.zip"
set "REQUIREMENTS=%PROJECT_DIR%requirements.txt"
set "CHROMEDRIVER_DIR=%PROJECT_DIR%/chromedriver-win64"

REM 检查本地Python环境
if not exist "%PYTHON_DIR%\python.exe" (
    echo Deploying isolated Python environment...
    
    REM 创建并进入工作目录
    if not exist "%PYTHON_DIR%" mkdir "%PYTHON_DIR%"
    cd /d "%PYTHON_DIR%"
    
    REM 下载嵌入式Python
    echo Download Python Embedded Version...
    powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; try { Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_DIR%\python.zip' -ErrorAction Stop } catch { Write-Error $_; exit 1 }"
    if errorlevel 1 (
        echo Error: Python download failed
        pause
        exit /b 1
    )

    REM 验证下载文件完整性
    if not exist "%PYTHON_DIR%\python.zip" (
        echo Error: Python ZIP file not found after download
        pause
        exit /b 1
    )
    
    REM 解压文件
    echo Extract files...
    powershell -Command "try { Expand-Archive -Path '%PYTHON_DIR%\python.zip' -DestinationPath '%PYTHON_DIR%' -Force } catch { Write-Error $_; exit 1 }"
    if errorlevel 1 (
        echo Error: Failed to extract Python ZIP
        echo Possible reasons: Corrupted download or invalid ZIP format
        pause
        exit /b 1
    )
    del /q "%PYTHON_DIR%\python.zip" 2>nul
    
    REM 配置运行环境
    echo Configure Python environment...
    copy "python._pth" "python._pth.bak" >nul
    (
        echo python311.zip
        echo .
        echo Lib\site-packages
        echo import site
    ) > "python._pth"
    
    REM 安装包管理器（示例：添加错误处理）
    echo Initialize pip,It may take a long time...
    curl -sSL -o get-pip.py https://bootstrap.pypa.io/get-pip.py
    if errorlevel 1 (
        echo Error: Failed to download get-pip.py
        pause
        exit /b 1
    )
    python.exe get-pip.py --no-warn-script-location
    if errorlevel 1 (
        echo Error: pip installation failed
        pause
        exit /b 1
    )
)

REM 修改python._pth文件
set "file=%PYTHON_DIR%\python311._pth"

:: 检查文件是否存在
if not exist "%file%" (
    echo The file '%file%' does not exist!
    pause
    exit /b
)

:: 创建一个临时文件
set "tempFile=%temp%\temp_pth.txt"

:: 初始化标志变量，标记是否已修改
set modified=false

:: 逐行读取文件，修改最后一行
for /f "delims=" %%A in (%file%) do (
    set line=%%A
    if "!line!"=="#import site" (
        echo import site >> %tempFile%
        set modified=true
    ) else (
        echo !line! >> %tempFile%
    )
)

:: 如果文件末尾的 "#import site" 已被修改
if !modified! == true (
    echo The file has been modified.
    move /y %tempFile% %file%
) else (
    echo The '# import site' was not found in the file or the file has not been modified.
    del %tempFile%
)

REM 设置临时环境变量
set "PATH=%PYTHON_DIR%;%PYTHON_DIR%\Scripts;%PATH%"

REM 安装项目依赖
if exist "%REQUIREMENTS%" (
    echo Installing dependency libraries...
    python -m pip install --upgrade pip --no-warn-script-location -i https://pypi.tuna.tsinghua.edu.cn/simple
    python -m pip install -r "%REQUIREMENTS%" --no-warn-script-location -i https://pypi.tuna.tsinghua.edu.cn/simple
    if errorlevel 1 (
        echo Error: Dependency installation failed
        pause
        exit /b 1
    )
) else (
    echo Error: Required. txt not found
    pause
    exit /b 1
)

REM 检查ChromeDriver

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
    

REM 运行Python主程序
echo Starting application...
python "%PROJECT_DIR%\auto_resume_submission_script_for_boss.py"

endlocal
pause

