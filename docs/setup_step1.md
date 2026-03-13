# Setup Schritt 1 (Windows, lokal ohne Docker)

Diese Anleitung richtet ein lokales Entwicklungs-Setup mit FastAPI im Ordner `backend` und React + Vite im Ordner `frontend` ein.

## 1) Python installieren

1. Lade Python 3.11+ fuer Windows herunter und installiere es:
   - https://www.python.org/downloads/windows/
2. Aktiviere im Installer unbedingt **"Add python.exe to PATH"**.
3. Pruefe die Installation in PowerShell:

```powershell
python --version
```

## 2) Virtuelle Umgebung fuer das Backend anlegen

Im Projekt-Root ausfuehren:

```powershell
cd .\mail-knowledge-platform
python -m venv .\backend\.venv
```

## 3) Backend-Abhaengigkeiten installieren

```powershell
.\backend\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r .\backend\requirements.txt
```

## 4) Node.js installieren (falls noch nicht vorhanden)

1. Lade die aktuelle LTS-Version herunter und installiere sie:
   - https://nodejs.org/
2. Pruefe die Installation in PowerShell:

```powershell
node --version
npm --version
```

## 5) Frontend-Module installieren

```powershell
cd .\frontend
npm install
cd ..
```

## 6) `.env.example` nach `.env` kopieren

Falls noch keine `.env` existiert, im Projekt-Root ausfuehren:

```powershell
Copy-Item .\.env.example .\.env
```

## 7) Backend starten

Im Projekt-Root:

```powershell
.\scripts\start_backend.ps1
```

Backend laeuft danach auf `http://127.0.0.1:8000`.

## 8) Frontend starten

In einer **zweiten** PowerShell im Projekt-Root:

```powershell
.\scripts\start_frontend.ps1
```

Frontend laeuft standardmaessig auf `http://127.0.0.1:5173`.

## 9) Health-Check pruefen

In einer dritten PowerShell:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/health
```

Erwartete Antwort ist ein JSON mit einem erfolgreichen Status.
