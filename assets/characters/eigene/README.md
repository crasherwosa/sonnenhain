# Eigene Figuren

Figuren, die wir selbst in Blender bauen. Grundlage ist der Körper samt Skelett aus den
Quaternius Universal Base Characters (CC0). Kleidung, Haare, Ausrüstung, Hautfarbe und
Schattierung sind eigene Arbeit. Weil das Skelett gleich bleibt, passen alle Animationen aus
`../quaternius/animationen/ual.glb`.

| Datei | Inhalt | Dreiecke | Größe |
| --- | --- | --- | --- |
| `abenteurerin.glb` | Blonde Abenteurerin nach dem Referenzbild: weißes Oberteil mit Lederkorsett, weiße Hose mit türkiser Stoffbahn mit Goldborte, Gürtel mit Schnalle und Taschen, Brustriemen, Schulterstück links, Armschienen, fingerlose Handschuhe, Stiefel mit Stoffstulpen, lange Haare, Stirnband mit Brille | ca. 15.600 | 1,3 MB |
| `vergleich.jpg` | Referenzbild, Blender-Bilder und Spielansicht nebeneinander | – | – |
| `vergleich-details.jpg` | Spielansicht vor und nach den gemalten Details | – | – |

Teile (Meshes) in `abenteurerin.glb`, einzeln ausblendbar über `hide` in `client/figuren.js`:
`Body` (Haut, Augen, Brauen), `Outfit` (alle Kleidung), `Hair` (Haare), `Headgear` (Stirnband und Brille).

## So entsteht die Figur

Alles läuft als Python-Skript in Blender, ohne Klicken. Das geht auf dem Mac genauso wie in einer
Claude-Sitzung in der Cloud (dort als Python-Modul `bpy`, ohne Bildschirm).

1. `tools/blender/textures.py` macht aus der Quaternius-Hauttextur eine hellere, saubere Haut ohne Unterwäsche.
2. `tools/blender/build.py` lädt den Grundkörper und baut die Kleidung: Jedes Kleidungsstück wird aus der
   Körperoberfläche ausgeschnitten, geglättet, nach außen geschoben und bekommt eine Kante. So erbt es die
   Bewegungsgewichte des Körpers und bewegt sich sauber mit. Riemen, Schnalle, Taschen, Schulterstück, Stirnband,
   Brille und die langen Haarsträhnen entstehen aus einfachen Formen. Verdeckte Haut wird entfernt.
3. `tools/blender/export.py` fasst alles zu vier Teilen zusammen, berechnet weiche Schatten in Falten und unter
   Riemen (als Punktfarben, kostet im Spiel nichts) und backt die gemalten Details in Texturen
   (`tools/blender/details.py`): Leinengewebe, Ledermaserung, Steppnähte am Rand, abgenutzte Lederkanten,
   Goldborte, Haarsträhnen. Die Muster entstehen als Shader in Blender und werden pro Teil in ein Farbbild
   und ein Reliefbild gebacken. Im Spiel kostet das nur zwei Bilder statt einfarbiger Flächen.
   Augen sind gegenüber dem Grundkörper etwa 16 % größer (in `build.py` oben, `EYE_SCALE`).
   Fürs iPhone wird danach vereinfacht (Ziel ca. 15.000 Dreiecke, Texturen höchstens 1024 Pixel, siehe
   Stil-Anweisung): der Körper vorab, wobei das Gesicht fein bleibt; Kleidung und Haare erst nach dem Backen,
   damit die Details auf dem feinen Netz entstehen.
4. `tools/figuren/skelett.mjs` setzt die Figur auf das Original-Skelett, damit die Animationen exakt passen.

Alles auf einmal: `QUATERNIUS=<quellordner> sh tools/blender/bauen.sh` (Voraussetzungen stehen oben im Skript).
Der Quellordner braucht `base/`, `hair/` und `textures/` aus den Quaternius-Paketen (kostenlos bei itch.io,
oder die Kopie, die in `../quaternius/README.md` beschrieben ist).

Neue Farben, Teile oder Formen: in `tools/blender/build.py` ändern (Farben stehen oben in `C`) und neu bauen.

## Lizenz

Grundkörper und Hauttextur: Quaternius, CC0. Alles andere: eigene Arbeit für Sonnenhain.
