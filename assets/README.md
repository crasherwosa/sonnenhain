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
| `characters/eigene/` | Eigene Figuren aus Blender; Grundkörper und Hauttextur aus Quaternius Universal Base Characters | CC0 (Grundkörper), eigene Arbeit |
| `characters/quaternius/` | Universal Base Characters, Modular Character Outfits – Fantasy, Universal Animation Library 1 und 2 (je Standard-Fassung), Quaternius | CC0 |
