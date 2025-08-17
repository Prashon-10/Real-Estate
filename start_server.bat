@echo off
echo Starting Real Estate Django Server...
cd /d "e:\Projects_College\VI Project\RealEstate\real_estate_app"
echo.
echo ✅ Fixed template syntax error (mul filter)
echo ✅ Fixed favorites deletion functionality  
echo ✅ Updated currency display to Rupees
echo ✅ Created simplified favorites template as backup
echo.
echo Starting server on http://127.0.0.1:8000/
echo.
python manage.py runserver
pause
