@echo off
echo Starting RealEstate Django Server...
echo.

echo Checking Django setup...
python quick_check.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ All checks passed! Starting server...
    echo.
    echo 🌐 Admin Panel will be available at: http://127.0.0.1:8000/admin-panel/
    echo 🔐 Login credentials: admin / admin123
    echo.
    python manage.py runserver
) else (
    echo.
    echo ❌ Setup check failed. Please review the errors above.
    pause
)
