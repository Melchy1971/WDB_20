# Mail Knowledge Platform

Lokales Full-Stack-System zur Extraktion und Speicherung von Wissen aus E-Mails und Dokumenten.

**Stack:** React 18 + TypeScript + Vite · FastAPI · Neo4j · Ollama

---

## Projektstruktur

```
WDB_20-1/
├── backend/                  # FastAPI-Backend
│   ├── main.py               # App-Einstiegspunkt + uvicorn
│   ├── requirements.txt
│   ├── .env / .env.example
│   └── app/
│       ├── adapters/         # Neo4j, Ollama
│       ├── api/
│       │   ├── router.py
│       │   └── routes/       # health, sources, persist
│       ├── core/             # Konfiguration
│       ├── models/           # Pydantic-Modelle
│       └── services/         # FileService, PersistService, DocumentParserService
├── frontend/                 # React-Frontend
│   ├── src/
│   │   ├── api/              # client, sourcesApi, persistApi, systemApi
│   │   ├── components/
│   │   │   ├── documents/    # DocumentCard, PreviewBox
│   │   │   ├── layout/       # AppLayout, SidebarNav
│   │   │   ├── sources/      # FolderScanForm
│   │   │   └── status/       # StatusCard, StatusBanner
│   │   ├── pages/            # SystemStatusPage, SourcesPage, FolderScanPage
│   │   └── types/            # document.ts, system.ts
├── data/sample_docs/         # Testdokumente (.txt, .eml)
├── docs/                     # Architektur- und Setup-Dokumentation
├── scripts/                  # Start- und Setup-Skripte
└── tests/                    # Platzhalter für Integrationstests
```

---

## Voraussetzungen

- Python 3.11+
- Node.js 18+
- Neo4j (lokal oder Aura)
- Ollama (lokal, `http://localhost:11434`)

---

## Setup

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # Werte anpassen
```

`.env` konfigurieren:

```
APP_ENV=dev
API_HOST=127.0.0.1
API_PORT=8000

NEO4J_URI=neo4j+s://<your-aura-id>.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=...

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
```

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env
```

---

## Starten

```bash
# Backend (aus backend/)
uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Frontend (aus frontend/)
npm run dev
```

Oder per Skript:

```powershell
.\scripts\start_backend.ps1
.\scripts\start_frontend.ps1
```

---

## API-Endpoints

| Methode | Pfad | Beschreibung |
|---------|------|--------------|
| `GET` | `/health` | Systemstatus (API, Neo4j, Ollama) |
| `POST` | `/sources/folder/scan` | Ordner scannen → Dokumente parsen |
| `POST` | `/persist/document` | Dokument in Neo4j speichern |

### Unterstützte Dateiformate

`.txt` · `.pdf` · `.docx` · `.eml`

---

## Implementierungsstand

| Feature | Status |
|---------|--------|
| System Health Check | ✅ fertig |
| Ordner scannen & parsen | ✅ fertig |
| Dokument in Neo4j speichern | ✅ fertig |
| Quellenverwaltung (CRUD) | ⏳ Backend ausstehend |
| Themenextraktion (NLP) | ⏳ geplant |

---

## Tests

```bash
cd backend
pytest tests/
```
