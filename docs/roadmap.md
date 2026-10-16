# Fahrplan

Stand: 16.10.2026

## Erledigt

- Prototyp v10 im Browser: Gelände, Wasser mit Spiegelung, Bäume, Wiese, Hof, Ruinen, Kampf mit 5 Fertigkeiten, Ausweichen, Gegner (Glibber, Pilzlinge, Goldglibber), Herz-Aufgabe bei Mira, Grafikstufen, Handy-Steuerung.
- Repository angelegt, Prototyp als Startpunkt übernommen (`client/`), three.js lokal mitgeliefert.
- KayKit-Figuren, Zubehör und Animationen in `assets/characters/kaykit/` abgelegt.
- KayKit-Figuren im Spiel: fünf Klassen (Magierin, Ritter, Waldläufer, Schurkin mit Kapuze, Barbar „Bärenherz“) mit Waffen und Animationen für Stehen, Gehen, Laufen, Springen, Ausweichen, Angriffe, Zauber, Treffer und Tod. Angriffe im Laufen bewegen nur den Oberkörper. Mira ist jetzt ebenfalls eine KayKit-Figur und winkt. Selbstgebaute Code-Figuren, Malfilter und Umrisslinien sind entfernt; die Welt lädt schneller, weil vier Figuren-Texturen nicht mehr erzeugt werden. Code in `client/figuren.js`.

## Als Nächstes

1. **Aufräumen und Leistung:** `client/index.html` in Module aufteilen (Welt, Spieler, Kampf, Gegner, Quests, Oberfläche). Grafikstufen neu abstimmen, damit es am Mac und iPhone flüssig läuft.
2. **Quests aus Daten:** Herz-Aufgabe aus `content/quests/` laden statt fest im Code.
3. **Lore:** Weltgeschichte, Regionen und erste Kapitel in `docs/lore.md` ausarbeiten.
4. **Klassen-Fertigkeiten:** je Klasse eigene Fertigkeiten (Schwert, Bogen, Dolche, Axt, Magie). Die Angriffs-Animationen je Klasse sind schon da (`client/figuren.js`).
5. **Gegner als KayKit-Figuren:** z. B. KayKit Skeletons; die Skelett-Animationen liegen bereits in `Rig_Medium_Special.glb`.

## Später

- Mehrspieler-Server (`server/`, Node.js + WebSockets) auf einem kleinen Hetzner-Server, automatische Veröffentlichung über GitHub Actions.
- Quest-Agent: geplante Claude-Sitzung, die neue Quests als Änderungsvorschlag anlegt.
- Eigene Figuren aus Blender, Umgebungsmodelle, Sounds und Musik.
- Texturen als fertige Bilddateien statt Erzeugung beim Start.
