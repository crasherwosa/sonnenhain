# Eigene Figuren und Waffen

Alle Spielfiguren und ihre Waffen bauen wir selbst in Blender, im Stil von Guild Wars 3 (siehe `docs/style.md`).
Grundlage ist ein realistischer Körper aus MakeHuman (CC0) mit fein modelliertem Gesicht, echten Augen, Brauen und
Wimpern. Er wird genau auf das Skelett der Quaternius Universal Base Characters (CC0) gesetzt, deshalb passen alle
Animationen aus `../quaternius/animationen/ual.glb`. Kleidung, Rüstung, Waffen und die gemalten Texturen sind eigene Arbeit.

| Datei | Klasse | Farben | Inhalt |
| --- | --- | --- | --- |
| `sternenweberin.glb` | Magierin | Creme und Türkis | Blonde Abenteurerin nach dem Referenzbild: Oberteil mit türkiser Borte, Lederkorsett, gravierte Goldschulter, Stoffbahnen vorne und hinten, Armschienen mit Goldband, Stiefel mit Stulpen, Goldreif mit Stein |
| `klingenwaechter.glb` | Krieger | Rot und Gold | Von Hand in Blender gebaut (Mac, nach GW3-Vorbild): dicke, geschichtete rote Platten mit goldenen Kanten und Ranken, große Schulterstücke, dunkle Gürtel mit Türkisschnalle, Plattenschurz, rote Stoffbahn, Beinschienen, Bart. Ca. 22.000 Dreiecke, eigene Farb-, Relief- und Metalltextur |
| `waldlaeufer.glb` | Waldläufer | Grün und Leder | Kapuze, Schulterumhang mit Goldborte, Lederweste mit Nieten, Köcher mit Pfeilen, Armschienen, hohe Stiefel, Bart |
| `schattenklinge.glb` | Schurkin | Violett und Silber | Kapuze mit Umhang, Gesichtstuch, Lederwams, Silberschulter, Armschienen mit Silberbändern, Dolchscheiden, viele Riemen |
| `baerenherz.glb` | Barbar | Fell und Eisen | Bärenfellumhang, Ledergeschirr, Eisenschulter und -armschienen, Lederschurz mit Eisenplatten, lange rote Haare, Vollbart |
| `mira.glb` | Bäuerin (NPC) | Leinen und Grün | Leinenbluse, geschnürtes grünes Mieder, langer Rock, Schürze mit Borte, Haarband, Dutt |
| `waffen/*.glb` | – | – | Schwert, Schild, Stab, Bogen, Dolch, Zweihandaxt: schlank, mit Bronze-, Gold- oder Silberbeschlägen |
| `alle-figuren.jpg` | – | – | Vorher und jetzt im Vergleich |

Jede Figur hat höchstens ca. 15.000 Dreiecke (der von Hand gebaute Klingenwächter ca. 22.000, Grenze 25.000) und Texturen von höchstens 1024 × 1024 Pixeln (iPhone), jede Waffe unter
1.000 Dreiecke. Teile (Meshes) einer Figur: `Body` (Haut, Augen), `Strands` (Frisur, Brauen und Wimpern aus dünnen
Flächen mit Durchsicht), `Outfit` (Kleidung und Rüstung), bei manchen `Hair` (Bart, Strähnen) und `Headgear` (Reif);
einzeln ausblendbar über `hide` in `client/figuren.js`.

## So entstehen die Figuren

Alles läuft als Python-Skript in Blender, ohne Klicken. Das geht auf dem Mac genauso wie in einer Claude-Sitzung in der
Cloud (dort als Python-Modul `bpy`, ohne Bildschirm).

0. Körper: `tools/blender/makehuman.py` formt den MakeHuman-Menschen (Frau oder Mann, Muskeln, Gewicht, Gesichtszüge),
   bringt ihn in die Grundhaltung (Arme waagrecht) und schiebt jedes Gelenk genau auf das Quaternius-Skelett. Die
   Bewegungsgewichte kommen vom Quaternius-Körper. Die Haut wird neu abgewickelt (das Gesicht bekommt viel Platz in der
   Textur) und wie gemalt eingefärbt: weiche Schatten in Augenhöhlen, an Nase und Lippen, leicht rötlich.
1. Rezept: `tools/blender/figuren/<name>.py` beschreibt eine Figur in wenigen Zeilen (Farben, Kleidungsstücke, Rüstungsteile,
   Haare). Die Bausteine stehen in `tools/blender/figurlib.py`: Kleidung wird aus der Körperoberfläche ausgeschnitten und
   erbt so die Bewegungsgewichte; Platten werden geglättet und gewölbt; dazu Stoffbahnen, Umhänge, Röcke, Kapuzen, Riemen,
   Taschen, Schulterstücke, Reife und Haarsträhnen. Maße stehen im Raum des Frauenkörpers und werden für den Männerkörper
   über die Gelenkpunkte umgerechnet.
2. Haut: `tools/blender/textures.py` färbt die MakeHuman-Haut auf den Hautton der Figur um (und Haare, Brauen, Wimpern).
3. Export: `tools/blender/export.py` fasst die Teile zusammen und backt die gemalten Details in Texturen
   (`tools/blender/details.py`): Stoffgewebe mit Mustern am Saum, Ledermaserung mit Nähten und abgenutzten Kanten,
   graviertes Metall mit polierten Kanten und Beschlägen, Fell, Haarsträhnen. Danach wird auf ca. 15.000 Dreiecke
   vereinfacht (Gesicht und kleine Teile bleiben fein) und es werden weiche Schatten in die Punktfarben gerechnet.
4. Skelett: `tools/figuren/skelett.mjs` setzt die Figur auf das Original-Skelett, damit die Animationen exakt passen.

Alles auf einmal: `QUATERNIUS=<quellordner> sh tools/blender/bauen.sh` (alle Figuren) oder mit Namen, z. B.
`sh tools/blender/bauen.sh mira`. Waffen: `python tools/blender/waffen.py [schwert schild stab bogen dolch axt]`.
Der Quellordner braucht `base/`, `hair/` und `textures/` aus den Quaternius-Paketen (kostenlos bei itch.io, oder die
Kopie, die in `../quaternius/README.md` beschrieben ist). Dazu MakeHuman: `MAKEHUMAN` zeigt auf `makehuman/data` aus
`git clone --depth 1 https://github.com/makehumancommunity/makehuman`, `MAKEHUMAN_ASSETS` auf `package/public/data` aus
dem npm-Paket `makehuman-data-v1` (`npm pack makehuman-data-v1`, enthält Haut, Augen, Brauen, Wimpern, Frisuren).

Neue Farben oder Teile: im Rezept der Figur ändern und neu bauen. Eine neue Figur: ein Rezept kopieren, anpassen und in
`client/figuren.js` eintragen.

## Lizenz

Körper, Gesicht, Augen, Brauen, Wimpern, Frisuren (long01, short02, ponytail01) und Grundhaut: MakeHuman-Systemdateien, CC0.
Skelett und einzelne Bärte und Frisuren: Quaternius, CC0. Alles andere: eigene Arbeit für Sonnenhain.
