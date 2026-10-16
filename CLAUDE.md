# Sonnenhain – Regeln für Claude

Diese Datei liest jede Claude-Sitzung zuerst. Sie beschreibt, wie das Projekt aufgebaut ist und wie hier gearbeitet wird.

## Projekt in einem Satz

Sonnenhain ist ein stilisiertes Fantasy-Rollenspiel im Browser, inspiriert von Guild Wars 2 (Kampf mit Fertigkeitenleiste, Ausweichrolle, Herz-Aufgaben), mit freundlicher, heller Welt. Ziel ist später ein Mehrspieler-Modus.

## Zusammenarbeit

- Der Projektinhaber ist kein Programmierer. Er arbeitet oft am Handy. Antworten auf Deutsch, in einfacher Sprache, ohne Fachjargon. Fachbegriffe kurz erklären.
- Eine Aufgabe pro Chat. Der Wissensstand liegt in diesem Repository (`docs/`, `content/`), nicht im Chatverlauf.
- Größere Änderungen vor dem Umsetzen kurz ankündigen. Nach dem Umsetzen: testen, Vorschau geben, erst dann ins Repository.
- Modelle entstehen in Blender (Claude Desktop + BlenderMCP auf dem Mac des Inhabers) und kommen als `.glb` nach `assets/`. Diese Sitzungen hier können Blender nicht steuern.

## Aufbau

| Ordner | Inhalt |
| --- | --- |
| `client/` | Das Spiel. Statische Dateien, kein Build-Schritt. `client/index.html` ist der Einstieg. |
| `client/figuren.js` | Lädt die Figuren (Quaternius mit echten Proportionen, KayKit für später), hängt Waffen an und steuert die Animationen. Welche Klasse welche Figur, Haarfarbe, Waffe und Angriffe hat, steht oben in der Datei. |
| `client/figuren.html` | Figurenschau: alle Klassen nebeneinander, Bewegungen per Knopf. Zum Prüfen neuer Figuren und Waffen. |
| `client/vendor/three/` | three.js r160, lokal mitgeliefert (nur die benötigten Dateien). Nicht verändern. |
| `assets/` | Modelle (`.glb`), später Sounds und Bilder. Regeln in `assets/README.md`. |
| `content/` | Spielinhalte als JSON: Quests, Dialoge, Gegnerwerte. Format in `content/README.md`. |
| `docs/` | Spieldesign, Lore, Stil, Fahrplan, Arbeitsweise. |
| `prototype/` | Archivierte Prototyp-Versionen zum Nachschlagen. Nicht weiterentwickeln. |
| `server/` | Später: Mehrspieler-Server (Node.js, WebSockets). |
| `tools/` | Hilfsskripte: lokaler Server, automatischer Rauchtest, `figuren/bauen.mjs` zum Zusammensetzen der Quaternius-Figuren. |

## Technische Regeln

- Kein Build-Schritt, kein npm im Client. ES-Module mit Importmap auf `./vendor/three/…`. So läuft das Spiel direkt von GitHub Pages oder jedem einfachen Webserver.
- three.js-Version bleibt r160, bis bewusst aktualisiert wird.
- Inhalte (Quests, Dialoge, Werte) gehören in `content/` als Daten, nicht in den Code.
- Leistung vor Effekten: Ziel sind flüssige 60 fps auf einem Mac und spielbare Bildraten auf einem aktuellen iPhone. Jeder neue Effekt muss abschaltbar sein und in die Grafikstufen passen.
- Firefox, Safari (auch iOS) und Chrome müssen funktionieren. Keine riesigen Shader mit verschachtelten Schleifen (Firefox/Windows hängen sonst beim Kompilieren).
- Texturen werden derzeit beim Start erzeugt (Web Worker mit Fallback auf den Hauptthread). Später sollen sie als fertige Bilddateien mitgeliefert werden.

## Testen

- Lokal starten: `tools/serve.sh` und dann `http://localhost:8765/client/` öffnen.
- Rauchtest ohne Grafikkarte: `node tools/smoketest.mjs` (benötigt Playwright mit Chromium). Startet das Spiel, wartet auf den Weltaufbau, meldet Konsolenfehler und legt Screenshots in `tools/out/` ab.
- Vor jedem Hochladen: Rauchtest muss ohne Fehler durchlaufen.

## Commits

- Kleine, verständliche Commits mit deutscher Beschreibung, was sich für den Spieler ändert.
- Keine Passwörter, Schlüssel oder Serverzugänge ins Repository. Dafür später GitHub Secrets.

## Aktueller Stand

Siehe `docs/roadmap.md`.
