@echo off
echo Starting Skylark BI Agent Development Environment...

echo Starting Backend...
start "Skylark BI - Backend" cmd /c "cd backend && .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000"

echo Starting Frontend...
start "Skylark BI - Frontend" cmd /c "cd frontend && npm run dev"

echo Both services have been started in separate windows!
echo Backend Health Check: http://localhost:8000/api/v1/health
echo Frontend Application: http://localhost:3000
