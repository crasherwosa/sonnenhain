# Eigene Figuren und Waffen

Alle Spielfiguren und ihre Waffen bauen wir selbst in Blender, im Stil von Guild Wars 3 (siehe `docs/style.md`).
Grundlage ist der Körper samt Skelett aus den Quaternius Universal Base Characters (CC0, Frau und Mann).
Kleidung, Rüstung, Haare, Hautfarbe, Waffen und alle Texturen sind eigene Arbeit. Weil das Skelett gleich bleibt,
passen alle Animationen aus `../quaternius/animationen/ual.glb`.

| Datei | Klasse | Farben | Inhalt |
| --- | --- | --- | --- |
| `sternenweberin.glb` | Magierin | Creme und Türkis | Blonde Abenteurerin nach dem Referenzbild: Oberteil mit türkiser Borte, Lederkorsett, gravierte Goldschulter, Stoffbahnen vorne und hinten, Armschienen mit Goldband, Stiefel mit Stulpen, Goldreif mit Stein |
| `klingenwaechter.glb` | Krieger | Rot und Bronze | Roter Wams, gravierter Brustpanzer, Schulterplatten, Armschienen, Plattenschurz, Beinschienen, roter Waffenrock mit Bronzeborte, Bart |
| `waldlaeufer.glb` | Waldläufer | Grün und Leder | Kapuze, Schulterumhang mit Goldborte, Lederweste mit Nieten, Köcher mit Pfeilen, Armschienen, hohe Stiefel, Bart |
| `schattenklinge.glb` | Schurkin | Violett und Silber | Kapuze mit Umhang, Gesichtstuch, Lederwams, Silberschulter, Armschienen mit Silberbändern, Dolchscheiden, viele Riemen |
| `baerenherz.glb` | Barbar | Fell und Eisen | Bärenfellumhang, Ledergeschirr, Eisenschulter und -armschienen, Lederschurz mit Eisenplatten, lange rote Haare, Vollbart |
| `mira.glb` | Bäuerin (NPC) | Leinen und Grün | Leinenbluse, geschnürtes grünes Mieder, langer Rock, Schürze mit Borte, Haarband, Dutt |
| `waffen/*.glb` | – | – | Schwert, Schild, Stab, Bogen, Dolch, Zweihandaxt: schlank, mit Bronze-, Gold- oder Silberbeschlägen |
| `alle-figuren.jpg` | – | – | Vorher und jetzt im Vergleich |

Jede Figur hat höchstens ca. 15.000 Dreiecke und Texturen von höchstens 1024 × 1024 Pixeln (iPhone), jede Waffe unter
1.000 Dreiecke. Teile (Meshes) einer Figur: `Body` (Haut, Augen, Brauen), `Outfit` (Kleidung und Rüstung), `Hair`
(Haare und Bart), bei manchen `Headgear` (Reif); einzeln ausblendbar über `hide` in `client/figuren.js`.

## So entstehen die Figuren

Alles läuft als Python-Skript in Blender, ohne Klicken. Das geht auf dem Mac genauso wie in einer Claude-Sitzung in der
Cloud (dort als Python-Modul `bpy`, ohne Bildschirm).

1. Rezept: `tools/blender/figuren/<name>.py` beschreibt eine Figur in wenigen Zeilen (Farben, Kleidungsstücke, Rüstungsteile,
   Haare). Die Bausteine stehen in `tools/blender/figurlib.py`: Kleidung wird aus der Körperoberfläche ausgeschnitten und
   erbt so die Bewegungsgewichte; Platten werden geglättet und gewölbt; dazu Stoffbahnen, Umhänge, Röcke, Kapuzen, Riemen,
   Taschen, Schulterstücke, Reife und Haarsträhnen. Maße stehen im Raum des Frauenkörpers und werden für den Männerkörper
   über die Gelenkpunkte umgerechnet.
2. Haut: `tools/blender/textures.py` macht aus der Quaternius-Hauttextur eine saubere Haut ohne Unterwäsche, im Hautton der Figur.
3. Export: `tools/blender/export.py` fasst die Teile zusammen und backt die gemalten Details in Texturen
   (`tools/blender/details.py`): Stoffgewebe mit Mustern am Saum, Ledermaserung mit Nähten und abgenutzten Kanten,
   graviertes Metall mit polierten Kanten und Beschlägen, Fell, Haarsträhnen. Danach wird auf ca. 15.000 Dreiecke
   vereinfacht (Gesicht und kleine Teile bleiben fein) und es werden weiche Schatten in die Punktfarben gerechnet.
4. Skelett: `tools/figuren/skelett.mjs` setzt die Figur auf das Original-Skelett, damit die Animationen exakt passen.

Alles auf einmal: `QUATERNIUS=<quellordner> sh tools/blender/bauen.sh` (alle Figuren) oder mit Namen, z. B.
`sh tools/blender/bauen.sh mira`. Waffen: `python tools/blender/waffen.py [schwert schild stab bogen dolch axt]`.
Der Quellordner braucht `base/`, `hair/` und `textures/` aus den Quaternius-Paketen (kostenlos bei itch.io, oder die
Kopie, die in `../quaternius/README.md` beschrieben ist).

Neue Farben oder Teile: im Rezept der Figur ändern und neu bauen. Eine neue Figur: ein Rezept kopieren, anpassen und in
`client/figuren.js` eintragen.

## Lizenz

Grundkörper und Hauttextur: Quaternius, CC0. Alles andere: eigene Arbeit für Sonnenhain.
