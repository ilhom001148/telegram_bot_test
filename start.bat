@echo off
echo ==========================================
echo UyQur Bot Tizimi Ishga Tushirilmoqda...
echo ==========================================

echo.
echo [1/3] FastAPI (Admin Panel Backend) yoqilmoqda...
start "FastAPI Server" cmd /k ".\.venv\Scripts\activate && uvicorn api.main:app --reload"

echo [2/3] React (Vite) Admin Panel yoqilmoqda...
start "React Admin Panel" cmd /c "cd admin-panel && npm run dev"

timeout /t 5 /nobreak > nul
echo Brauzerda admin panel ochilmoqda...
start http://localhost:5173

echo [3/3] Telegram Bot yoqilmoqda bu oynani yopmang...
.\.venv\Scripts\activate && python -m bot.main
