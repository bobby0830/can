# Flutter 應用程式安裝與打包指南

由於您的環境尚未安裝 Flutter SDK，請按照以下步驟進行配置與打包。

## 1. 安裝 Flutter SDK
1. 從 [Flutter 官網](https://docs.flutter.dev/get-started/install/windows) 下載最新版的 Windows SDK。
2. 將下載的 `.zip` 檔案解壓縮到路徑（例如：`C:\src\flutter`）。
3. **重要：** 將 `flutter\bin` 目錄完整路徑加入到系統環境變數的 `Path` 中。
4. 打開終端機執行 `flutter doctor` 確認安裝狀態。

## 2. 初始化專案
在安裝完 SDK 後，於 `frontend` 目錄執行：
```powershell
cd frontend
flutter pub get
```

## 3. 封裝應用程式 (Packaging)

### 打包為 Android APK
如果您已安裝 Android Studio 並配置好 SDK：
```powershell
flutter build apk --release
```
生成的檔案位於：`build/app/outputs/flutter-apk/app-release.apk`

### 打包為 Windows 桌面應用
```powershell
flutter build windows
```
生成的檔案位於：`build/windows/runner/Release/`

## 4. 測試
執行前端單元測試：
```powershell
flutter test
```

---
**備註：** 
- 確保在執行前端前，後端 Flask 伺服器已啟動（可以使用 `docker-compose up` 或 `python backend/app.py`）。
- 測試 API 連線時，若在模擬器執行，請將 `api_service.dart` 中的 `localhost` 改為 `10.0.2.2`。








