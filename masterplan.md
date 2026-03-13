# Masterplan: WDB_20-1

## Letzte Aktualisierung
- Datum: 2026-03-13
- Zielarchitektur auf externe Neo4j-Zielinfrastruktur korrigiert
- Masterplan mit aktuellem Implementierungsstand abgeglichen
- PST-Quellenverwaltung, Validierung und ImportRun-Anzeige im Status Quo ergaenzt

## 1. Projektvision
Entwicklung einer lokalen Wissens- und Analyseplattform zur Ingestion, Analyse und graphbasierten Speicherung unstrukturierter Datenquellen wie lokaler Dokumente und PST-E-Mail-Archive. Ziel ist es, isolierte Daten kontrolliert in einen durchsuchbaren, verknuepften Wissensgraphen zu ueberfuehren, unterstuetzt durch lokale oder externe KI-Provider.

## 2. Korrigierte Zielarchitektur
Neo4j ist keine lokale Entwicklerdatenbank als Zielbetrieb, sondern externe Zielinfrastruktur.

```text
React Frontend (lokal)
        |
        v
FastAPI Backend (lokal oder App-Server)
        |
        v
Neo4j Aura oder Self-Managed Neo4j Server
```

Architekturregeln:
- kein Frontend-zu-Neo4j-Zugriff
- keine Neo4j-Credentials im Frontend
- kein Frontend-zu-Ollama-Zugriff
- alle Integrationen ausschliesslich ueber das Backend
- Rohdaten nie ueberschreiben
- freigegebene Analyseergebnisse getrennt persistieren

## 3. Architektur & Tech Stack
- Frontend: React, Vite, TypeScript, CSS
- Backend: Python, FastAPI
- Datenbank: Neo4j Aura oder Self-Managed Neo4j
- KI: Ollama lokal, optional DnaBot
- Parsing: libratom (PST), pypdf, python-docx, email (EML)
- Persistenz intern: aktuell In-Memory Stores plus JSON fuer Sources; spaeter SQLite oder aehnliche lokale Persistenz fuer Jobs und Status
- Entwicklungsumgebung: VS Code, Codex, weitere Review-/Prompt-Tools nach Bedarf

## 4. Domänenobjekte
Aktuell bzw. fachlich vorgesehen:
- SourceSystem / Source
- ImportRun
- Folder
- Email
- Document
- Attachment
- Topic
- Entity
- AnalysisResult
- MergedCase

## 5. Hauptpipeline
1. Quelle registrieren
2. Struktur scannen
3. Inhalte parsen
4. Inhalte normalisieren
5. KI-Analyse ausfuehren
6. Themen clustern
7. Review im Frontend
8. Freigegebene Ergebnisse nach Neo4j schreiben

## 6. Status Quo (Ist-Zustand)

### System & Infrastruktur
- [x] FastAPI-Backend vorhanden
- [x] React-/Vite-Frontend vorhanden
- [x] Health-/Status-Pfad im System vorhanden
- [x] Neo4j-Zielarchitektur ist backendseitig gekapselt
- [x] Frontend greift nicht direkt auf Neo4j oder Ollama zu

### Source Management
- [x] Registry fuer Quellen in `data/sources.json`
- [x] UI fuer Auflistung, Hinzufuegen und Aktivieren von Quellen
- [x] Validierung absoluter PST-Pfade beim Anlegen
- [x] Ungueltige PST-Quellen werden im UI markiert
- [x] Aktivierung ungueltiger PST-Quellen ist im Frontend und Backend blockiert
- [x] Bearbeiten gespeicherter Source-Pfade implementiert

### PST Ingestion Pipeline
- [x] PST-Struktur-Analyse ohne Inhaltsladen (`pst_parser_service`)
- [x] Auswahl spezifischer Unterordner fuer den Import
- [x] Import-Job fuer Extraktion von E-Mails und Attachments
- [x] ImportRun-Ergebnisansicht mit Polling bis Abschluss
- [x] Neo4j-Rohpersistenz fuer ImportRun, E-Mails und Attachments
- [x] Anzeige von E-Mail-Body und Attachment-Metadaten im ImportRun-Ergebnis

### Document Scanning (Local)
- [x] Rekursives Scannen lokaler Ordner
- [x] Extraktion von Text und Metadaten aus PDF, DOCX, TXT und EML
- [x] Manuelles Speichern einzelner Dokumente nach Neo4j

### AI Analysis
- [x] Grundgeruest fuer Analyse von ImportRuns (`analysis_service`)
- [x] Provider-Abstraktion fuer Ollama und DnaBot
- [x] Analyse kann fuer ImportRuns gestartet und abgefragt werden
- [ ] Analyseergebnisse werden noch nicht in Neo4j persistiert

## 7. Gap-Analyse gegenüber Masterplan v2
Aus `masterplan_v2.md` uebernommen bzw. korrigiert:
- Neo4j ist als externe Zielinfrastruktur modelliert, nicht als Frontend- oder lokale Direktintegration
- Frontend/Backend/Datenbank-Verantwortlichkeiten werden strikt getrennt
- Rohimport und fachliche Auswertung sind getrennte Persistenzstufen
- Setup- und Zielarchitektur wurden in produktionsnaeherer Form beschrieben

Nicht 1:1 uebernommen:
- Die sehr fruehe Setup-Anleitung aus `masterplan_v2.md` wurde nicht vollstaendig als operative Schritt-fuer-Schritt-Installationsanleitung uebernommen, weil das Projekt bereits existiert
- Stattdessen wurde der aktuelle Implementierungsstand in den Masterplan integriert

## 8. Roadmap

### Phase 1: Persistenz & Stabilitaet
- [ ] Job- und Import-Status von In-Memory auf dauerhafte Persistenz umstellen
- [ ] Analyse-Ergebnisse dauerhaft speichern
- [ ] Robusteres Error Handling bei defekten Dateien und PST-Sonderfaellen
- [ ] Encoding-Bereinigung in verbliebenen UI-/Backend-Texten systematisch abschliessen

### Phase 2: Knowledge Graph Enrichment
- [ ] Analyseergebnisse nach Neo4j schreiben, getrennt von Rohdaten
- [ ] Entitaeten und Relationen modellieren, z. B. `(:Email)-[:MENTIONS]->(:Person)`
- [ ] Entity Linking fuer Dubletten und Identitaetszusammenfuehrung
- [ ] Themen-/Clusterbildung fuer E-Mails und Dokumente
- [ ] Review- und Freigabe-Workflow fuer fachliche Ergebnisse schaerfen

### Phase 3: Search & Retrieval
- [ ] Embeddings fuer E-Mail-Bodies und Dokumententexte erzeugen
- [ ] Search API fuer semantische Suche bereitstellen
- [ ] Chat-/RAG-Interface im Frontend aufsetzen

## 9. Offene Tasks (Backlog)

### Backend
- [ ] `analysis_service.py`: Persistenzschritt fuer Analyseergebnisse nach Neo4j implementieren
- [ ] `settings_service.py`: Provider-Einstellung dauerhaft speichern
- [ ] `pst_import_service.py`: Performance fuer grosse PST-Dateien pruefen und ggf. Streaming-Ansatz vorbereiten
- [ ] `import_job_service.py`: echte asynchrone Job-Ausfuehrung mit belastbarer Statuspersistenz vorbereiten
- [ ] Source-Validierung um Existenzpruefungen und ggf. lesbaren Zugriff erweitern

### Frontend
- [ ] Analysis View fuer ImportRun-Ergebnisse ausbauen
- [ ] Settings Page fuer Provider-Umschaltung vervollstaendigen
- [ ] Graph-Visualisierung fuer freigegebene Beziehungen vorbereiten
- [ ] Quellenverwaltung um bessere Inline-Validierung und UX fuer lokale Pfade erweitern

## 10. Neo4j-Datenmodell

### Aktuell / Rohdaten
- `RawImportRun`
- `RawImportedEmail`
- `RawImportedAttachment`
- `Document`

### Geplant / Enrichment
- `SourceSystem`
- `Folder`
- `Email`
- `Attachment`
- `Topic`
- `Entity`
- `AnalysisResult`
- `MergedCase`
- moegliche Spezialisierungen wie `Person`, `Organization`, `Keyword`, `Summary`

## 11. Ergebnisdefinition naechster belastbarer Stand
Der naechste belastbare Projektstand ist erreicht, wenn:
- PST- und lokale Quellen stabil verwaltet werden
- Import- und Analyse-Status Neustarts ueberleben
- Analyseergebnisse getrennt von Rohdaten in Neo4j geschrieben werden
- Frontend nur ueber Backend-APIs arbeitet
- keine direkte Kopplung Frontend <-> Neo4j existiert
- keine direkte Kopplung Frontend <-> Ollama existiert
- Review und Freigabe fachlicher Ergebnisse nachvollziehbar moeglich sind
