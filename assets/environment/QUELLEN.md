# Quellen und Lizenzen – Umgebung

Alle 17 Umgebungsmodelle aus `docs/blender-umgebung.md`. Fremde Bestandteile stammen ausschließlich von Poly Haven und stehen unter CC0 (gemeinfrei, keine Namensnennung nötig, hier trotzdem vermerkt). Alles andere (Formen, Blätter-, Nadel- und Efeu-Texturen, Moos) ist eigene Arbeit, per Skript in Blender erzeugt.

Die Tabelle „Lizenzen“ kann so in `assets/README.md` übernommen werden.

## Lizenzen

| Datei | Quelle | Lizenz |
| --- | --- | --- |
| `environment/baeume/laubbaum-1.glb` | Form (Stamm, Äste, Blattkarten) und Blätter-Textur: eigene Arbeit. Rinde: „Jolcham Oak Bark 01“ von Charlotte Baglioni, Poly Haven (https://polyhaven.com/a/jolcham_oak_bark_01), auf 512 × 1024 verkleinert, weicher und wärmer gefärbt | Rinde CC0, Rest eigene Arbeit |
| `environment/baeume/laubbaum-2.glb` | wie `laubbaum-1.glb` (gleiche Rinde und Blätter-Textur, eigene Form) | Rinde CC0, Rest eigene Arbeit |
| `environment/baeume/laubbaum-3.glb` | wie `laubbaum-1.glb` (gleiche Rinde und Blätter-Textur, eigene Form) | Rinde CC0, Rest eigene Arbeit |
| `environment/baeume/kiefer-1.glb` | Form (Stamm, Äste, Nadelkarten) und Nadel-Textur: eigene Arbeit. Rinde: „Pine Bark“ von Dimitrios Savva, Poly Haven (https://polyhaven.com/a/pine_bark), auf 512 × 512 verkleinert, weicher und wärmer gefärbt | Rinde CC0, Rest eigene Arbeit |
| `environment/baeume/kiefer-2.glb` | wie `kiefer-1.glb` (gleiche Rinde und Nadel-Textur, eigene Form) | Rinde CC0, Rest eigene Arbeit |
| `environment/baeume/busch-1.glb` | Form eigene Arbeit; Texturen wie `laubbaum-1.glb` | Rinde CC0, Rest eigene Arbeit |
| `environment/baeume/busch-2.glb` | Form eigene Arbeit; Texturen wie `kiefer-1.glb` | Rinde CC0, Rest eigene Arbeit |
| `environment/felsen/fels-1.glb` | „Boulder 01“ von Rico Cilliers, Poly Haven (https://polyhaven.com/a/boulder_01): auf 2,4 m vergrößert, vereinfacht, unten abgeflacht; Farbe, Normal Map und Rauheit vom Original gebacken, Moos eigene Arbeit | CC0 |
| `environment/felsen/fels-2.glb` | „Rock 07“ von Jenelle van Heerden, Poly Haven (https://polyhaven.com/a/rock_07): aufgestellt, auf 2,5 m vergrößert, vereinfacht, unten abgeflacht, aufgehellt; Farbe, Normal Map und Rauheit vom Original gebacken, Moos eigene Arbeit | CC0 |
| `environment/felsen/fels-3.glb` | „Namaqualand Boulder 03“ von Jenelle van Heerden und Dario Barresi, Poly Haven (https://polyhaven.com/a/namaqualand_boulder_03): auf 3,5 m vergrößert, vereinfacht, unten abgeflacht, weniger orange; Farbe, Normal Map und Rauheit vom Original gebacken, Moos eigene Arbeit | CC0 |
| `environment/felsen/fels-4.glb` | „Namaqualand Boulder 05“ von Jenelle van Heerden und Dario Barresi, Poly Haven (https://polyhaven.com/a/namaqualand_boulder_05): auf 2,1 m vergrößert, vereinfacht, unten abgeflacht; Farbe, Normal Map und Rauheit vom Original gebacken, Moos eigene Arbeit | CC0 |
| `environment/felsen/klippe-1.glb` | Form eigene Arbeit (geschichtete Felsplatten). Oberfläche: Textur „Cliff Side“ von James Ray Cock, Jenelle van Heerden und Dario Barresi, Poly Haven (https://polyhaven.com/a/cliff_side), mit Farbschwankung und Moos (eigene Arbeit) gebacken | Textur CC0, Rest eigene Arbeit |
| `environment/felsen/klippe-2.glb` | Form eigene Arbeit (Felssäulen). Oberfläche: Textur „Marble Cliff 04“ von Amal Kumar, Poly Haven (https://polyhaven.com/a/marble_cliff_04), mit Farbschwankung und Moos (eigene Arbeit) gebacken | Textur CC0, Rest eigene Arbeit |
| `environment/ruinen/bogen.glb` | Form eigene Arbeit (Steinblöcke). Steinoberfläche: Textur „Sandstone Cracks“ von Rob Tuytel, Poly Haven (https://polyhaven.com/a/sandstone_cracks), aufgehellt, mit Verwitterung und Moos (eigene Arbeit) gebacken. Efeu-Textur eigene Arbeit | Textur CC0, Rest eigene Arbeit |
| `environment/ruinen/saeule.glb` | wie `bogen.glb` (eigene Form, gleiche Sandstein-Textur, Efeu eigene Arbeit) | Textur CC0, Rest eigene Arbeit |
| `environment/ruinen/turm.glb` | wie `bogen.glb` (eigene Form, gleiche Sandstein-Textur, Efeu eigene Arbeit) | Textur CC0, Rest eigene Arbeit |
| `environment/ruinen/schrein.glb` | wie `bogen.glb` (eigene Form, gleiche Sandstein-Textur, Efeu eigene Arbeit) | Textur CC0, Rest eigene Arbeit |

## Kenndaten

Geprüft nach dem Export: alle Dateien unter der Dreieck-Grenze und unter 2 MB, Texturen höchstens 1024 × 1024, Fuß auf Höhe 0, Ursprung unten in der Mitte (bei Bäumen am Stammfuß), ein Objekt pro Datei, nur Principled BSDF mit Farbe, Normal Map und Rauheit, Blätter, Nadeln und Efeu mit Alpha Clip (glTF „MASK“, beidseitig sichtbar).

| Datei | Höhe (Grundfläche) | Dreiecke | Grenze | Größe | Texturen |
| --- | --- | --- | --- | --- | --- |
| `baeume/laubbaum-1.glb` | 9,6 m | 4 774 | 5 000 | 1,6 MB | Rinde 512 × 1024 (Farbe, Normal, Rauheit), Blätter-Atlas 1024 × 1024 (Farbe mit Alpha, Normal) |
| `baeume/laubbaum-2.glb` | 10,9 m | 4 792 | 5 000 | 1,6 MB | wie `laubbaum-1.glb` |
| `baeume/laubbaum-3.glb` | 9,4 m | 4 774 | 5 000 | 1,6 MB | wie `laubbaum-1.glb` |
| `baeume/kiefer-1.glb` | 14,8 m | 2 880 | 3 000 | 1,6 MB | Rinde 512 × 512 (Farbe, Normal, Rauheit), Nadel-Atlas 1024 × 1024 (Farbe mit Alpha, Normal) |
| `baeume/kiefer-2.glb` | 11,9 m | 2 880 | 3 000 | 1,6 MB | wie `kiefer-1.glb` |
| `baeume/busch-1.glb` | 1,65 m | 1 176 | 1 200 | 1,5 MB | wie `laubbaum-1.glb` |
| `baeume/busch-2.glb` | 1,9 m | 1 176 | 1 200 | 1,5 MB | wie `kiefer-1.glb` |
| `felsen/fels-1.glb` | 1,06 m (2,3 × 1,7 m) | 1 832 | 2 000 | 0,96 MB | Farbe 1024 × 1024, Normal 1024 × 1024, Rauheit 512 × 512 |
| `felsen/fels-2.glb` | 2,35 m (1,3 × 1,1 m) | 1 936 | 2 000 | 0,52 MB | wie `fels-1.glb` |
| `felsen/fels-3.glb` | 1,56 m (3,5 × 2,75 m) | 1 823 | 2 000 | 0,61 MB | wie `fels-1.glb` |
| `felsen/fels-4.glb` | 0,66 m (2,1 × 1,1 m) | 1 784 | 2 000 | 0,82 MB | wie `fels-1.glb` |
| `felsen/klippe-1.glb` | 9,2 m (12,6 × 6,7 m) | 3 948 | 4 000 | 0,79 MB | wie `fels-1.glb` |
| `felsen/klippe-2.glb` | 12,9 m (11,6 × 7,3 m) | 3 949 | 4 000 | 0,98 MB | wie `fels-1.glb` |
| `ruinen/bogen.glb` | 5,7 m (6,1 × 2,9 m) | 1 974 | 6 000 | 1,7 MB | Stein: Farbe/Normal 1024, Rauheit 512; Efeu-Atlas 1024 × 1024 (Farbe mit Alpha, Normal) |
| `ruinen/saeule.glb` | 4,1 m (4,2 × 2,5 m) | 3 100 | 6 000 | 1,8 MB | wie `bogen.glb` |
| `ruinen/turm.glb` | 8,25 m (6,9 × 5,6 m mit Trümmern) | 1 792 | 6 000 | 1,6 MB | wie `bogen.glb` |
| `ruinen/schrein.glb` | 4,7 m (6,3 × 4,7 m) | 2 736 | 6 000 | 1,7 MB | wie `bogen.glb` |

## Hinweise für den Code-Chat

- **Gemeinsame Texturen:** Laubbäume und Busch 1 teilen sich Rinde und Blätter-Atlas, Kiefern und Busch 2 teilen sich Rinde und Nadel-Atlas, alle Ruinen teilen sich den Efeu-Atlas. Wenn der Code diese Materialien zwischen den Modellen wiederverwendet, sinkt der Speicherbedarf deutlich.
- **Blätter im Gegenlicht:** Die Modelle haben nur Farbe, Normal Map und Rauheit. Das Durchleuchten der Blätter im Gegenlicht muss der Shader im Spiel liefern (siehe `docs/style.md`).
- **Blattnormalen:** Die Blattkarten haben geglättete, nach außen zeigende Normalen (Krone wirkt wie ein weicher Körper, nicht wie einzelne Flächen). Beim Laden nicht neu berechnen lassen.
- **Felsen und Ruinen** sind unten flach abgeschnitten und dürfen ein paar Zentimeter in den Boden gesetzt werden. Klippe 1 und 2 sind rundum geschlossen.
- **Efeu** sitzt nur auf der Vorderseite. Das ist dieselbe Blickrichtung wie bei den Figuren (in Blender −Y, im glTF +Z). Die Vorderseite sollte also zum Weg zeigen.
- **Bäume** haben den Ursprung am Stammfuß. Die Krone steht teilweise schief darüber, das ist gewollt.
