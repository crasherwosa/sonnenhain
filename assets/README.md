# Assets

Hier liegen alle Modelle und später Sounds und Bilder.

| Ordner | Inhalt |
| --- | --- |
| `characters/` | Spielfiguren und NPCs mit Skelett und Animationen |
| `environment/` | Gebäude, Pflanzen, Felsen, Requisiten |

## Export-Regeln für Blender

- Format: **glTF Binary (`.glb`)**, eine Datei pro Figur bzw. Objektgruppe.
- Maßstab: 1 Blender-Einheit = 1 Meter. Figuren ca. 1,5–1,8 m hoch, Füße auf Höhe 0.
- Blickrichtung nach vorne (in Blender −Y; der glTF-Export rechnet das um).
- Alle Transformationen anwenden (*Object → Apply → All Transforms*).
- Animationen benennen: `Idle`, `Run`, `Attack`, `Cast`, `Dodge`, `Hit`, `Death`.
- Höchstens ca. 15.000 Dreiecke pro Figur (Ausnahme: Spielfiguren mit echten Proportionen bis ca. 30.000), Texturen höchstens 2048 × 2048 Pixel.
- Dateigröße pro Figur möglichst unter 5 MB.
- Dateinamen klein und ohne Leerzeichen, z. B. `ritter.glb`, `mira.glb`.

## Lizenzen

Bei jedem fremden Modell die Lizenz und Quelle hier eintragen.

| Datei | Quelle | Lizenz |
| --- | --- | --- |
| `characters/kaykit/` | KayKit Adventurers 2.0 und Character Animations 1.1, Kay Lousberg | CC0 |
| `characters/eigene/` | Eigene Figuren aus Blender; Körper, Gesicht, Augen, Brauen, Wimpern, Frisuren und Grundhaut aus MakeHuman (makehuman.org, Systemdateien), Skelett aus Quaternius Universal Base Characters | CC0 (MakeHuman, Quaternius), eigene Arbeit |
| `characters/quaternius/` | Universal Base Characters, Modular Character Outfits – Fantasy, Universal Animation Library 1 und 2 (je Standard-Fassung), Quaternius | CC0 |
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
