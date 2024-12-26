@echo off
:main_loop
cls
echo.
echo Type 'U' to start the process or 'exit' to quit.
set /p user_input="Enter your choice: "

if /i "%user_input%"=="u" (
    cls
    @echo off
    set /p file_path="Enter the file path: WITH  ' '   : "
    set /p root_path="Enter the root path (default is 'root\'): "
    if "%root_path%"=="" set root_path=root\\

    python FINAL_SINGLE_SERVER.py "%file_path%" "%root_path%"
    python server_html_creater.py

    :: Open the output.html file in the default browser
    start "" "output.html"

    pause
    goto main_loop
) else if /i "%user_input%"=="exit" (
    echo Exiting the program...
    timeout /t 2 >nul
    exit /b
) else (
    echo Invalid input. Please try again.
    timeout /t 2 >nul
    goto main_loop
)
