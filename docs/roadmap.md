# Fahrplan

Stand: 16.10.2026

## Erledigt

- Prototyp v10 im Browser: Gelände, Wasser mit Spiegelung, Bäume, Wiese, Hof, Ruinen, Kampf mit 5 Fertigkeiten, Ausweichen, Gegner (Glibber, Pilzlinge, Goldglibber), Herz-Aufgabe bei Mira, Grafikstufen, Handy-Steuerung.
- Repository angelegt, Prototyp als Startpunkt übernommen (`client/`), three.js lokal mitgeliefert.
- KayKit-Figuren, Zubehör und Animationen in `assets/characters/kaykit/` abgelegt.
- KayKit-Figuren im Spiel: fünf Klassen (Magierin, Ritter, Waldläufer, Schurkin mit Kapuze, Barbar „Bärenherz“) mit Waffen und Animationen für Stehen, Gehen, Laufen, Springen, Ausweichen, Angriffe, Zauber, Treffer und Tod. Angriffe im Laufen bewegen nur den Oberkörper. Mira ist jetzt ebenfalls eine KayKit-Figur und winkt. Selbstgebaute Code-Figuren, Malfilter und Umrisslinien sind entfernt; die Welt lädt schneller, weil vier Figuren-Texturen nicht mehr erzeugt werden. Code in `client/figuren.js`.

- Figuren mit echten Proportionen: Quaternius-Figuren (CC0) im Stil des Referenzbilds. Die Sternenweberin ist eine blonde Abenteurerin in Weiß und Leder, die anderen Klassen unterscheiden sich durch Kapuze, Haare, Bart und Waffen. Mira ist eine Bäuerin. 32 Animationen aus der Universal Animation Library (Gehen, Joggen, Rennen, Rolle, Schwertkombos, Zauber, Treffer, Tod). `client/figuren.js` kann jetzt zwei Figurenarten (Quaternius und KayKit). Neue Figurenschau `client/figuren.html`, Bauskript `tools/figuren/bauen.mjs`.

- Umgebung im Stil von Guild Wars 2: gemalte Haufenwolken, bläulicher Dunst in der Ferne, wärmeres Licht mit bläulichen Schatten, hellere Wiesen mit goldenen Flecken. Neues Unterholz (Farne, hohe Grasbüschel, Baumstümpfe, liegende Stämme), Schilf und Seerosen an den Seen, türkisfarbenes Wasser mit Schaumrand. Sanfter Wind in Gras und Bäumen, Baumkronen bleiben auch in der Ferne dicht. Dichte, Sichtweite und Wind folgen den Grafikstufen. Code in `client/umgebung.js`, Vorher/Nachher-Bilder mit `tools/ansichten.mjs`.
- Umgebung nach der Stil-Anweisung (Vorbild Guild Wars 3): Tageszeit „Goldene Stunde“ (tiefe Sonne, rosa-fliederfarbener Himmel, lange Schatten) als neue Grundeinstellung, „Mittag“ wählbar auf dem Startbildschirm. Flache Nebelbänder über Wiesen und See, fliederfarbener Dunst, höheres Gras mit leuchtenden Spitzen im Gegenlicht, Blumen in blau-lila Gruppen mit roten und orangen Tupfern, Pollen, die im Gegenlicht aufleuchten, feines Filmkorn.

- Umgebungsmodelle aus Blender im Spiel: drei Laubbäume, zwei Kiefern, zwei Büsche, vier Felsbrocken, zwei Klippen sowie Bogen, Säulen, Schrein und Turmruine (Poly-Haven-Texturen, CC0). Sie ersetzen die einfachen Formen aus dem Code; Blätter wehen im Wind und leuchten im Gegenlicht. Code in `client/modelle.js`.

## Als Nächstes

1. **Aufräumen und Leistung:** `client/index.html` in Module aufteilen (Welt, Spieler, Kampf, Gegner, Quests, Oberfläche). Grafikstufen neu abstimmen, damit es am Mac und iPhone flüssig läuft.
2. **Quests aus Daten:** Herz-Aufgabe aus `content/quests/` laden statt fest im Code.
3. **Lore:** Weltgeschichte, Regionen und erste Kapitel in `docs/lore.md` ausarbeiten.
4. **Klassen-Fertigkeiten:** je Klasse eigene Fertigkeiten (Schwert, Bogen, Dolche, Axt, Magie). Die Angriffs-Animationen je Klasse sind schon da (`client/figuren.js`).
5. **Schlankere Waffen und mehr Outfits:** die KayKit-Waffen passen nur ungefähr zu den neuen Figuren. Eigene Waffen in Blender bauen oder die Quaternius-Source-Fassung (mehr Outfits, ca. 20 USD) kaufen. Eigene Bogen- und Magie-Animationen fehlen noch.
6. **Gegner als KayKit-Figuren:** z. B. KayKit Skeletons; die Skelett-Animationen liegen bereits in `Rig_Medium_Special.glb`.

## Später

- Mehrspieler-Server (`server/`, Node.js + WebSockets) auf einem kleinen Hetzner-Server, automatische Veröffentlichung über GitHub Actions.
- Quest-Agent: geplante Claude-Sitzung, die neue Quests als Änderungsvorschlag anlegt.
- Eigene Figuren aus Blender, Umgebungsmodelle, Sounds und Musik.
- Texturen als fertige Bilddateien statt Erzeugung beim Start.
