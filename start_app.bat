@echo off
set "FLUTTER_BIN=C:\Users\user\Desktop\flutter\bin"
set "PATH=%FLUTTER_BIN%;%PATH%"

echo Starting Bridge...
start cmd /c "node mcp_bridge.js"

echo Starting Docker...
docker-compose up -d

echo Syncing Flutter...
cd frontend
call flutter.bat pub get
cd ..

echo Launching App...
cd frontend
start flutter.bat run -d chrome

pause
