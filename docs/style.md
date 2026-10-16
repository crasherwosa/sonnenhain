# Stilleitfaden

## Grafik

- **Stilisiert mit echten Proportionen.** Vorbild: Guild Wars 2, Fortnite, das Referenzbild der Abenteurerin (helle Kleidung, Lederriemen, lange Haare). Figuren sind normal proportioniert (kein Großkopf-Stil), Gesichter und Formen sind aber vereinfacht und freundlich, Texturen gemalt statt fotografisch.
- **Hell und freundlich**, aber nicht kindlich: gedeckte, natürliche Grundfarben (Grüntöne, Erde, Stein), kräftige Akzente nur für Wichtiges (Magie, Beute, Gefahr).
- **Lesbarkeit vor Detail:** Silhouetten müssen aus der Kameraentfernung (ca. 8–12 m) klar erkennbar sein.

## Umgebung

- **Vorbild Guild Wars 2:** warmes Sonnenlicht, leicht bläuliche Schatten, kräftige aber natürliche Grüntöne, goldene Flecken in den Wiesen („Goldwiesen“).
- **Tiefe durch Dunst:** Was weit weg ist, wird blasser und bläulich. So wirken Berge groß und fern.
- **Himmel:** gemalte Haufenwolken hoch über den Bergen, dazu feine Schleierwolken. Keine Kugelwolken.
- **Dichte Pflanzen in Schichten:** Bäume, darunter Büsche, Farne und hohe Grasbüschel, am Boden Gras und Blumen. Am Ufer Schilf und Seerosen.
- **Wasser:** am Ufer hell und türkis mit Schaumrand, in der Tiefe dunkelblau.
- **Bewegung:** sanfter Wind in Gras, Farnen und Baumkronen (in der Grafikstufe „Mittel“ aus).
- Alles wird im Code erzeugt (`client/umgebung.js` und `client/index.html`), es gibt keine fremden Dateien. Später können Modelle aus Blender einzelne Teile ersetzen.

## Figuren

- **Spielfiguren und Menschen:** Quaternius-Figuren (Universal Base Characters + Modular Character Outfits, CC0) mit echten Proportionen, ca. 1,70–1,80 m groß. Details in `assets/characters/quaternius/README.md`.
- **Kleidung:** helle Stoffe (Weiß, Creme, gedecktes Grün) mit braunem Leder, Riemen, Schnallen und Armschienen. Metall sparsam (Schulterstück, Beschläge).
- **Haare:** kräftige, natürliche Farben (Blond, Braun, Rot, Dunkelbraun), über die Materialfarbe im Spiel einstellbar.
- **Waffen:** die KayKit-Waffen bleiben vorerst; sie sind etwas klobiger als die Figuren. Später durch schlankere Waffen ersetzen.
- **Gegner und Kreaturen** dürfen verspielter sein (Glibber, Pilzlinge, später KayKit-Skelette).

## Modelle

- Gemalte, weiche Texturen statt Fototexturen. Höchstens 1024 × 1024 Pixel pro Figurentextur.
- Animationen kommen aus der Universal Animation Library (gleiches Skelett für alle Figuren).
- Technische Regeln in `assets/README.md`.

## Benutzeroberfläche

- Schriften: Marcellus SC für Titel, Nunito für Text.
- Dunkle, halbtransparente Glasflächen mit goldenem Rand.
- Alle Texte auf Deutsch.

## Sprache im Spiel

- Freundlich, leicht verschmitzt, nie zynisch.
- Namen auf Deutsch und bildhaft (Goldwiesen, Sonnenhof, Glibber, Pilzling).
