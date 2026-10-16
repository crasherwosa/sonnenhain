# Fahrplan

Stand: 16.10.2026

## Erledigt

- Prototyp v10 im Browser: Gelände, Wasser mit Spiegelung, Bäume, Wiese, Hof, Ruinen, Kampf mit 5 Fertigkeiten, Ausweichen, Gegner (Glibber, Pilzlinge, Goldglibber), Herz-Aufgabe bei Mira, Grafikstufen, Handy-Steuerung.
- Repository angelegt, Prototyp als Startpunkt übernommen (`client/`), three.js lokal mitgeliefert.
- KayKit-Figuren, Zubehör und Animationen in `assets/characters/kaykit/` abgelegt.

## Als Nächstes

1. **Figuren:** KayKit-Adventurers einbauen (Ritter, Barbar, Schurke, Magierin, Waldläuferin) mit Animationen. Selbstgebaute Code-Figuren, Malfilter und Umrisslinien entfernen.
2. **Aufräumen und Leistung:** `client/index.html` in Module aufteilen (Welt, Spieler, Kampf, Gegner, Quests, Oberfläche). Grafikstufen neu abstimmen, damit es am Mac und iPhone flüssig läuft.
3. **Quests aus Daten:** Herz-Aufgabe aus `content/quests/` laden statt fest im Code.
4. **Lore:** Weltgeschichte, Regionen und erste Kapitel in `docs/lore.md` ausarbeiten.
5. **Klassen-Fertigkeiten:** je Klasse eigene Fertigkeiten (Schwert, Bogen, Dolche, Magie).

## Später

- Mehrspieler-Server (`server/`, Node.js + WebSockets) auf einem kleinen Hetzner-Server, automatische Veröffentlichung über GitHub Actions.
- Quest-Agent: geplante Claude-Sitzung, die neue Quests als Änderungsvorschlag anlegt.
- Eigene Figuren aus Blender, Umgebungsmodelle, Sounds und Musik.
- Texturen als fertige Bilddateien statt Erzeugung beim Start.
