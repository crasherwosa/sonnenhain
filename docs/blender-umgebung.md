# Umgebung aus Blender

Anleitung für den Blender-Chat (Claude Desktop + BlenderMCP am Mac). Ziel: Bäume, Felsen, Klippen und Ruinen im Stil von `docs/style.md` („stilisierter Realismus“ wie Guild Wars 3), die die einfachen Formen aus dem Code ersetzen.

## Stil

- Echte, kräftige Formen: verdrehte Stämme, kantige Felsen, Moos oben auf Steinen und Kanten.
- Farben etwas kräftiger und weicher als in echt, wie gemalt. Keine Foto-Unruhe, keine harten Kontraste in der Textur.
- Blätter als Büschel aus Blattkarten (Flächen mit Blattbild und Transparenz), nicht als Kugeln.
- Aus 10 m Entfernung muss die Silhouette klar lesbar sein.

## Quellen

1. Zuerst Poly Haven (über BlenderMCP direkt nutzbar, alles CC0). Passende Modelle und Texturen (Rinde, Moos, Fels) übernehmen und bei Bedarf umfärben.
2. Wenn nichts passt: selbst bauen, Bäume z. B. mit dem mitgelieferten Blender-Add-on „Sapling Tree Gen“.
3. Nur CC0. Quelle jeder Datei in `assets/README.md` (Tabelle „Lizenzen“) eintragen.

## Liste, nach Wichtigkeit

| Nr. | Datei | Was | Höchstens Dreiecke |
| --- | --- | --- | --- |
| 1 | `baeume/laubbaum-1.glb` bis `-3.glb` | Große Charakterbäume, 7–12 m, verdrehter Stamm, Krone aus Blattbüscheln | 5 000 |
| 2 | `baeume/kiefer-1.glb`, `-2.glb` | Kiefern oder Tannen, 10–16 m | 3 000 |
| 3 | `baeume/busch-1.glb`, `-2.glb` | Büsche, 1–2 m | 1 200 |
| 4 | `felsen/fels-1.glb` bis `-4.glb` | Felsbrocken 1–4 m, Moos oben | 2 000 |
| 5 | `felsen/klippe-1.glb`, `-2.glb` | Klippenstücke 8–15 m, Moos auf den Kanten | 4 000 |
| 6 | `ruinen/bogen.glb`, `saeule.glb`, `turm.glb`, `schrein.glb` | Verwitterte helle Steinruinen mit Moos und Efeu | 6 000 |

## Technische Regeln

- Export als glTF Binary (`.glb`), eine Datei pro Objekt, Ablage unter `assets/environment/…` wie in der Tabelle.
- 1 Blender-Einheit = 1 Meter. Ursprung (Origin) unten in der Mitte, Fuß auf Höhe 0. Alle Transformationen anwenden.
- Materialien nur „Principled BSDF“ mit Farbe, Normal Map und Rauheit (Roughness). Blätter: Alpha „Clip“, nicht „Blend“.
- Texturen höchstens 1024 × 1024 Pixel, als JPG oder PNG im `.glb` eingebettet. Mehrere Objekte dürfen sich eine Textur teilen.
- Dateigröße pro Modell möglichst unter 2 MB.
- Vor dem Export ein Vorschaubild rendern (Gegenlicht, tiefe Sonne), damit man den Stil prüfen kann.

## Danach

Die `.glb`-Dateien im Sonnenhain-Projekt hochladen (im Thread „Umgebung optimieren“). Der Code-Chat baut sie ins Spiel ein und ersetzt die alten Formen.
