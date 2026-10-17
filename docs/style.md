# Stilleitfaden

## Grafik

- **Ziel: stilisierter Realismus wie Guild Wars 3.** Formen, Licht und Materialien wirken echt und hochwertig, Farben sind aber kräftiger und weicher als in der Wirklichkeit, wie ein gemaltes Bild. Kein Comic, kein Großkopf-Stil, aber auch keine Fotos.
- **Licht malt die Stimmung.** Jede Szene hat eine klare Lichtrichtung: warme Sonne (Gold, Pfirsich) gegen kühle Schatten und Ferne (Blau, Flieder). Gegenlicht ist der Lieblingsblick: Gras und Blätter leuchten an den Spitzen auf.
- **Tiefe in Schichten.** Vordergrund kräftig und dunkler, Mitte satt, Hintergrund blass und bläulich im Dunst. Zwischen den Schichten liegen Nebelbänder.
- **Lesbarkeit vor Detail:** Silhouetten müssen aus der Kameraentfernung (ca. 8–12 m) klar erkennbar sein. Viel Detail aus der Nähe, ruhige große Formen aus der Ferne.
- **Kräftige Akzente nur für Wichtiges:** Magie und Kreaturen leuchten türkis oder gold, Beute golden, Gefahr rot.

## Umgebung

Erkenntnisse aus den Guild-Wars-3-Bildern und was daraus für Sonnenhain folgt:

1. **Himmel:** große, weiche, plastisch geformte Haufenwolken mit hellen Sonnenrändern. Abends ein Farbverlauf von Pfirsich über Rosa zu Flieder und Blau. Es gibt zwei Tageszeiten-Stimmungen: „Mittag“ (klar, hell) und „Goldene Stunde“ (tiefe Sonne, Rosa-Himmel).
2. **Dunst und Nebel:** dichter, leuchtender Dunst in der Ferne, dazu flache Nebelbänder in Tälern und über dem Wasser. Die Sonne strahlt sichtbar durch den Dunst (Lichtstrahlen).
3. **Gras:** dicht und hoch, mit unterschiedlich langen Halmen. Unten dunkelgrün, oben gelbgrün; im Gegenlicht leuchten die Spitzen. Dazwischen Wildblumen in Gruppen, nicht einzeln verstreut: Blau und Lila als Hauptfarbe, Rot und Orange als kleine Farbtupfer.
4. **Bäume:** wenige, dafür große Charakterbäume mit verdrehten, geformten Stämmen und Kronen aus klar erkennbaren Blattbüscheln (keine Kugeln). Dazu kleinere Bäume und Büsche als Füllung.
5. **Felsen und Klippen:** große, kantige Formen mit Moos oben und auf den Kanten. Felsen sind nie glatte Kugeln oder Würfel.
6. **Leben in der Luft:** schwebende Pollen, Lichtflocken und einzelne fallende Blätter, besonders im Gegenlicht.
7. **Wasser:** klar und türkis am Ufer, spiegelt den Himmel, mit weichem Schaumrand. Im Abendlicht spiegelt es Rosa und Gold.
8. **Bildabschluss:** ganz leichtes Filmkorn, Bloom (weiches Leuchten um helle Stellen) und in „Ultra“ eine leichte Unschärfe weit hinten.

**Was im Code geht und was aus Blender kommen muss:**

- **Im Code (`client/umgebung.js`, `client/index.html`):** Licht, Himmelsfarben, Dunst, Nebelbänder, Gras im Gegenlicht, Blumengruppen, Pollen, Wind, Wasser, Filmkorn.
- **Aus Blender (am Mac, freie CC0-Modelle, Quelle in `assets/README.md`):** Charakterbäume, Felsen und Klippen, Ruinen und Gebäude. Diese Teile ersetzen nach und nach die einfachen Formen aus dem Code. Ziel pro Modell: höchstens ca. 5 000 Dreiecke für Bäume, 2 000 für Felsen, Texturen höchstens 1024 × 1024 Pixel.

## Figuren

Erkenntnisse aus den Guild-Wars-3-Bildern:

- **Proportionen:** echt, ca. 1,70–1,85 m, schlanke Hände, normal große Köpfe. Helden wirken heldenhaft durch Haltung und Rüstung, nicht durch Übertreibung.
- **Gesichter:** halbrealistisch: echte Gesichtsformen, klare Augen, leicht weichgezeichnete Haut. Ausdrucksstark, aber nicht puppenhaft.
- **Rüstung in Lagen:** jede Klasse trägt mehrere Schichten übereinander, zum Beispiel Stoffhemd, darüber Lederwams, darüber Metallteile. Gürtel, Riemen, Taschen und Tücher brechen die Flächen auf.
- **Materialien klar unterscheidbar:** Metall glänzt und hat eingravierte Muster, Leder ist matt mit Nähten, Stoff hat Muster am Saum. Gold- und Bronzebeschläge als Schmuck.
- **Farben pro Klasse:** eine Hauptfarbe und eine Schmuckfarbe, zum Beispiel Krieger Rot und Bronze, Waldläufer Grün und Leder, Magierin Creme und Türkis. Helle Stoffe bleiben das Markenzeichen von Sonnenhain.
- **Haare:** kräftige, natürliche Farben (Blond, Braun, Rot, Dunkelbraun) mit erkennbaren Strähnen statt einem einzigen Block.
- **Waffen:** schlank und verziert, im gleichen Stil wie die Rüstung. Die klobigen KayKit-Waffen werden ersetzt.
- **Kreaturen und Reittiere:** fantastisch, mit leuchtenden türkisen Mustern (Magie). Kleine Gegner dürfen verspielter sein (Glibber, Pilzlinge), bleiben aber im gleichen Licht- und Materialstil.
- **Weg dorthin:** Die Quaternius-Figuren bleiben die Grundlage (Körper und Animationen). In Blender bekommen sie mehr Rüstungsteile, gemalte Texturen mit Gravuren und Mustern und bessere Haare. Das macht der Chat „Eigene Figur in Blender“.

## Modelle

- Gemalte Texturen mit echtem Materialgefühl (Metall glänzt, Leder matt) statt Fotos. Höchstens 1024 × 1024 Pixel pro Figurentextur.
- Figuren höchstens ca. 15 000 Dreiecke, damit das iPhone flüssig bleibt.
- Animationen kommen aus der Universal Animation Library (gleiches Skelett für alle Figuren).
- Technische Regeln in `assets/README.md`.

## Leistung

- „Ultra“ (Mac): alles an, inklusive Nebelbänder, Lichtstrahlen und Unschärfe in der Ferne.
- „Hoch“: Nebel, Pollen und Gegenlicht an, keine Unschärfe.
- „Mittel“ (iPhone): weniger Gras und Pollen, kein Wind, einfacher Dunst. Die Stimmung (Farben, Licht) bleibt gleich.

## Benutzeroberfläche

- Schriften: Marcellus SC für Titel, Nunito für Text.
- Dunkle, halbtransparente Glasflächen mit goldenem Rand.
- Alle Texte auf Deutsch.

## Sprache im Spiel

- Freundlich, leicht verschmitzt, nie zynisch.
- Namen auf Deutsch und bildhaft (Goldwiesen, Sonnenhof, Glibber, Pilzling).
