# Sonnenhain

Ein stilisiertes Fantasy-Rollenspiel im Browser, inspiriert von Guild Wars 2. Helle Welt, freundliche Kreaturen, Kampf mit Fertigkeitenleiste und Ausweichrolle, Herz-Aufgaben. Später mit Mehrspieler-Modus.

## Spielen

Lokal: `tools/serve.sh` ausführen und `http://localhost:8765/client/` im Browser öffnen.

Steuerung am PC: WASD laufen, Maus ziehen für die Kamera, 1–5 Fertigkeiten, Tab Ziel wählen, Shift ausweichen, Leertaste springen, F interagieren. Am Handy: links laufen, rechts wischen für die Kamera, Gegner antippen.

## Projekt

| Ordner | Inhalt |
| --- | --- |
| `client/` | Das Spiel (läuft ohne Build-Schritt) |
| `assets/` | 3D-Modelle aus Blender (`.glb`) |
| `content/` | Quests und andere Spielinhalte als Daten |
| `docs/` | Spieldesign, Lore, Stil, Fahrplan, Arbeitsweise |
| `prototype/` | Archivierte Prototypen |
| `server/` | Später: Mehrspieler-Server |
| `tools/` | Lokaler Server und automatischer Test |

Wie wir arbeiten, steht in `docs/workflow.md`. Regeln für Claude stehen in `CLAUDE.md`.

## Lizenzen

- three.js: MIT-Lizenz, siehe `client/vendor/three/LICENSE`.
- KayKit-Figuren und Animationen: CC0, von Kay Lousberg (www.kaylousberg.com), siehe `assets/characters/kaykit/`.
- Quaternius-Figuren und Animationen: CC0, von Quaternius (www.quaternius.com), siehe `assets/characters/quaternius/`.
- three.js-Zusatzdateien `GLTFLoader.js` und `SkeletonUtils.js` (r160) zum Laden der Figuren, ebenfalls MIT-Lizenz.
