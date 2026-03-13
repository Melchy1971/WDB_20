# Mail Knowledge Platform

Lokales Full-Stack-System zur Analyse von lokalen Dokumenten und PST-E-Mail-Archiven mit FastAPI, React und Neo4j als externer Zielinfrastruktur.

**Stack:** React 18 + TypeScript + Vite · FastAPI · Neo4j · Ollama / DNAbot

---

## Projektstruktur

```text
WDB_20-1/
|-- backend/
|   |-- main.py
|   |-- requirements.txt
|   |-- .env / .env.example
|   `-- app/
|       |-- adapters/         # neo4j_adapter, ollama_adapter, dnabot_adapter
|       |-- api/
|       |   |-- router.py
|       |   `-- routes/       # health, sources, filesystem, import_jobs, import_runs, persist, settings
|       |-- core/             # config
|       |-- models/           # source, document, import, analysis, settings, tree
|       `-- services/         # scanning, PST, import, analysis, persistence
|-- frontend/
|   `-- src/
|       |-- api/              # client, sources, persist, import, analysis, filesystem, settings
|       |-- components/       # layout, status, documents, sources
|       |-- pages/            # system, quellen, datenimport, PST-scan/import, analyse
|       `-- types/
|-- data/                     # lokale JSON-/Zwischenspeicher
|-- docs/
|-- scripts/
`-- sample_docs/
```

---

## Voraussetzungen

- Python 3.11+
- Node.js 18+
- Neo4j Aura oder Self-Managed Neo4j
- Ollama lokal (`http://localhost:11434`) oder DNAbot

---

## Setup

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Beispiel fuer `backend/.env`:

```env
APP_ENV=local
API_HOST=127.0.0.1
API_PORT=8000

NEO4J_URI=neo4j+s://<your-aura-id>.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=...
NEO4J_DATABASE=neo4j

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_HEALTH_PATH=/api/tags
```

### Frontend

```bash
cd frontend
npm install
```

---

## Starten

```bash
# Backend
cd backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Frontend
cd frontend
npm run dev
```

Oder unter Windows per Skript:

```powershell
.\scripts\start_backend.ps1
.\scripts\start_frontend.ps1
```

---

## Navigation

Die Navigation wird lokal in `App.tsx` per App-State gesteuert.

| Seite | Status | Beschreibung |
|---|---|---|
| System Status | aktiv | API-, Neo4j- und Ollama-Status |
| Datenimport (Ordner) | aktiv | lokale Ordner scannen, Dokumente analysieren und nach Neo4j persistieren |
| KI-Einstellungen | aktiv | AI-Provider konfigurieren |
| Quellenverwaltung | aktiv | lokale Ordnerquellen anlegen, bearbeiten, aktivieren |
| PST-Scan & Import | aktiv | PST-Dateien einbinden und PST-Strukturscan starten |
| PST-Strukturscan | aktiv | PST-Struktur laden und Knoten fuer Import auswaehlen |
| PST-Import vorbereiten | aktiv | Auswahl pruefen und Import-Job starten |
| PST-Import Ergebnis | aktiv | ImportRun, E-Mails, Attachments und Body anzeigen |
| Themenreview | vorbereitet | UI-Platzhalter |
| KI-Analyse | teilweise | Analyse fuer ImportRuns abrufen |

---

## Zentrale API-Endpunkte

| Methode | Pfad | Beschreibung |
|---|---|---|
| `GET` | `/health` | Systemstatus |
| `GET` | `/sources` | Quellen auflisten |
| `POST` | `/sources` | lokale Ordnerquelle anlegen |
| `POST` | `/sources/pst` | PST-Quelle anlegen |
| `POST` | `/sources/select` | aktive Quelle setzen |
| `PATCH` | `/sources/{source_id}/path` | Quellpfad aktualisieren |
| `GET` | `/sources/{source_id}/tree` | PST-Struktur laden |
| `GET` | `/sources/{source_id}/selection` | PST-Auswahl laden |
| `POST` | `/sources/{source_id}/selection` | PST-Auswahl speichern |
| `GET` | `/sources/{source_id}/import-preview` | PST-Import-Vorschau laden |
| `POST` | `/sources/{source_id}/import-jobs` | PST-Import starten |
| `GET` | `/import-jobs/{job_id}` | Import-Job-Status laden |
| `GET` | `/import-runs/{import_run_id}` | ImportRun laden |
| `POST` | `/import-runs/{import_run_id}/analysis` | Analyse starten |
| `GET` | `/import-runs/{import_run_id}/analysis` | Analyse abrufen |
| `POST` | `/sources/{source_id}/scan` | lokale Quelle scannen |
| `POST` | `/sources/scan-analysis/{scan_id}` | Scan analysieren |
| `POST` | `/persist/document` | Dokument nach Neo4j persistieren |
| `GET` | `/filesystem/browse` | Dateisystem fuer PST-Auswahl durchsuchen |
| `GET` | `/settings/ai-provider` | aktiven AI-Provider laden |
| `POST` | `/settings/ai-provider` | aktiven AI-Provider setzen |

---

## Aktueller Funktionsumfang

### Lokale Dokumente
- rekursives Scannen lokaler Ordner
- Parsing von `.txt`, `.pdf`, `.docx`, `.eml`
- KI-Analyse gescannter Dokumente
- manuelle Persistierung einzelner Dokumente nach Neo4j

### PST
- PST-Datei als Quelle registrieren
- PST-Strukturscan ohne Laden aller Inhalte
- Auswahl von Ordnern fuer den Import
- Import-Job mit ImportRun-Ergebnisansicht
- Anzeige importierter E-Mails, Bodies und Attachment-Metadaten
- Rohpersistierung des PST-Imports nach Neo4j

### KI / Analyse
- Provider-Abstraktion fuer Ollama und DNAbot
- Analyse von ImportRuns
- Analyseergebnisse aktuell noch nicht dauerhaft in Neo4j gespeichert

---

## Frontend-Architektur

### Wichtige App-States in `App.tsx`

| State | Beschreibung |
|---|---|
| `activePage` | aktive Seite |
| `selectedSourceId` | aktuell ausgewaehlte Quelle |
| `selectedSourceType` | Typ der aktuell ausgewaehlten Quelle |
| `selectedImportRunId` | aktuell geoeffneter ImportRun |

### Relevante Frontend-API-Module

| Datei | Zweck |
|---|---|
| `api/sourcesApi.ts` | Quellenverwaltung, Aktivierung, Scan, Tree |
| `api/sourceSelectionApi.ts` | PST-Knotenauswahl |
| `api/importPreviewApi.ts` | PST-Import-Vorschau |
| `api/importJobsApi.ts` | PST-Import-Jobs |
| `api/importRunsApi.ts` | ImportRun laden |
| `api/analysisApi.ts` | ImportRun-Analyse |
| `api/persistApi.ts` | Dokumentpersistierung |
| `api/filesystemApi.ts` | Dateisystem-Browser fuer PST-Auswahl |
| `api/aiSettingsApi.ts` | Provider-Einstellungen |

---

## Sicherheits- und Architekturregeln

- kein direkter Frontend-Zugriff auf Neo4j
- keine Neo4j-Credentials im Frontend
- kein direkter Frontend-Zugriff auf Ollama
- alle Integrationen laufen ueber das Backend
- `text_content` lokaler Dokumente wird nicht ans Frontend geliefert
- Rohdaten und fachliche Analyse sind getrennte Persistenzstufen

---

## Bekannte Grenzen

- Analyseergebnisse von ImportRuns werden aktuell noch nicht dauerhaft in Neo4j persistiert
- Job-, Import- und Analyse-Status sind noch nicht restart-sicher persistiert
- PST-Import und Dokumentanalyse setzen eine erreichbare externe Neo4j-Instanz voraus

---

## Tests

```bash
cd backend
pytest tests/
```
