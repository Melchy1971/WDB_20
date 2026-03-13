# Mail Knowledge Platform

Lokales Full-Stack-System zur Extraktion und Speicherung von Wissen aus E-Mails und Dokumenten.

**Stack:** React 18 + TypeScript + Vite · FastAPI · Neo4j · Ollama / DNAbot

---

## Projektstruktur

```
WDB_20-1/
|-- backend/                  # FastAPI-Backend
|   |-- main.py               # App-Einstiegspunkt + CORS + uvicorn
|   |-- requirements.txt
|   |-- .env / .env.example
|   `-- app/
|       |-- adapters/         # neo4j_adapter, ollama_adapter
|       |-- api/
|       |   |-- router.py     # zentrale Router-Aggregation
|       |   `-- routes/       # health, sources, persist
|       |-- core/             # config (pydantic-settings)
|       |-- models/           # document_models, system_models, source_models
|       `-- services/         # FileService, PersistService,
|                             # DocumentParserService, scan_store
|-- frontend/                 # React-Frontend
|   `-- src/
|       |-- api/              # client, sourcesApi, persistApi,
|       |   |                # systemApi, topicsApi (stub), aiSettingsApi (stub)
|       |-- components/
|       |   |-- documents/    # DocumentCard, DocumentList, PreviewBox
|       |   |-- layout/       # AppLayout, SidebarNav
|       |   `-- status/       # StatusCard, StatusBanner
|       |-- pages/            # SystemStatusPage, SourcesPage, FolderScanPage,
|       |   |                # KiSettingsPage, TopicsReviewPage (stub),
|       |   |                # PstImportPage (stub), AnalysisPage (stub)
|       `-- types/            # document.ts, system.ts, navigation.ts, ai.ts
|-- data/sample_docs/         # Testdokumente (.txt, .eml)
|-- docs/                     # Architektur- und Setup-Dokumentation
|-- scripts/                  # Start- und Setup-Skripte
`-- sample_docs/              # zusaetzliche Beispieldokumente
```

---

## Voraussetzungen

- Python 3.11+
- Node.js 18+
- Neo4j (lokal oder Aura)
- Ollama (lokal, `http://localhost:11434`) **oder** DNAbot

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

```env
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

### Schnellstart (Windows / PowerShell)

```powershell
# im Projektroot
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Terminal 1: Backend
.\scripts\start_backend.ps1

# Terminal 2: Frontend
.\scripts\start_frontend.ps1
```

### Troubleshooting (kurz)

- Fehler `Virtuelle Umgebung nicht gefunden`: im Ordner `backend` zuerst `python -m venv .venv` und danach `pip install -r requirements.txt` ausfuehren.
- Fehler bei `npm run dev` (z. B. fehlende Pakete): im Ordner `frontend` einmal `npm install` ausfuehren.

---

## Navigation

Die Sidebar-Navigation schaltet zwischen Seiten per lokalem App-State (kein react-router-dom).

| Seite | Status | Beschreibung |
|---|---|---|
| System Status | aktiv | API-, Neo4j- und Ollama-Verbindungsstatus |
| Dokumentscan | aktiv | Ordner scannen, Dokumente in Neo4j speichern |
| KI-Einstellungen | aktiv | Provider-Auswahl: Local Ollama / DNAbot |
| Quellenverwaltung | teilweise | Ordnerpfad festlegen, Quellen aktivieren |
| Themenreview | geplant | - |
| PST-Import | umgesetzt | PST-Struktur, Auswahl, ImportRun und Vorschau |
| KI-Analyse | teilweise | Analyse fuer ImportRuns vorhanden |

---

## API-Endpunkte (Backend)

| Methode | Pfad | Beschreibung |
|---------|------|--------------|
| `GET` | `/health` | Systemstatus (API, Neo4j, Ollama) |
| `POST` | `/sources/folder/scan` | Ordner scannen -> Dokumente parsen |
| `POST` | `/persist/document` | Dokument per content_hash in Neo4j speichern |

### Unterstuetzte Dateiformate

`.txt` · `.pdf` · `.docx` · `.eml`

### Sicherheitskonzept

- `text_content` wird nie ans Frontend geliefert (nur `preview_text`)
- Persistierung erfolgt ID-basiert (`content_hash`), kein Volltext ueber die API
- Dateigroesse begrenzt auf 10 MB pro Datei
- Parse-Fehler pro Datei isoliert (kein Abbruch des gesamten Scans)

---

## Frontend-Architektur

### UI-Styleguide (Design Tokens)

- Alle visuellen Zustaende laufen zentral ueber `frontend/src/styles/theme.css` und `frontend/src/index.css`.
- In `frontend/src/components/**` und `frontend/src/pages/**` werden keine harten Farbwerte verwendet.
- Komponenten nutzen ausschliesslich semantische Klassen; Farb- und State-Definitionen erfolgen ueber CSS-Tokens (`var(--tk-...)`).
- Neue Styles folgen dem Prinzip: **Token zuerst**, keine direkten Hex-/RGB-/HSL-Werte in Einzelkomponenten.

### State-Management

| State | Ort | Beschreibung |
|---|---|---|
| `activePage` | `App.tsx` | aktive Seite (Union-Type `AppPage`) |
| `selectedFolderPath` | `App.tsx` | gemeinsamer Pfad fuer Quellenverwaltung und Dokumentscan |
| `activeProvider` | `App.tsx` | KI-Provider (`"ollama"` | `"dnabot"`) |

### Typen

| Datei | Inhalt |
|---|---|
| `types/document.ts` | `DocumentScanItem`, `DocumentListResponse`, `FolderSourceRequest`, `PersistDocumentCommand`, `PersistDocumentResponse` |
| `types/navigation.ts` | `AppPage` Union-Type |
| `types/ai.ts` | `AiProvider` (inkl. `"none"`), `ActiveAiProvider` |
| `types/system.ts` | `HealthResponse` |

### API-Stubs (noch ohne Backend)

| Datei | Geplante Endpunkte |
|---|---|
| `api/topicsApi.ts` | `GET/POST /topics` |
| `api/aiSettingsApi.ts` | `GET/POST /settings/ai-provider` |

---

## Implementierungsstand

| Feature | Status |
|---------|--------|
| System Health Check | fertig |
| Ordner scannen & parsen (.txt, .pdf, .docx, .eml) | fertig |
| Dokument in Neo4j speichern (ID-basiert) | fertig |
| KI-Provider-Auswahl (Ollama / DNAbot) | Frontend fertig, Backend teilweise |
| Quellenverwaltung inklusive PST-Pfadvalidierung | umgesetzt |
| PST-Import mit ImportRun-Anzeige | umgesetzt |
| Themenextraktion (NLP) | geplant |
| KI-Analyse mit Graph-Persistenz | teilweise |

---

## Tests

```bash
cd backend
pytest tests/
```
