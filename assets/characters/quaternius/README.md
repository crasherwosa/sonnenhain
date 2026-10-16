# Quaternius-Figuren

Figuren mit echten Körperproportionen, stilisiert, von Quaternius (www.quaternius.com). Lizenz **CC0** (frei nutzbar, auch kommerziell, ohne Namensnennung). Lizenztexte liegen in diesem Ordner.

## Herkunft

| Paket | Original | Lizenz |
| --- | --- | --- |
| Universal Base Characters (Standard, kostenlos) | https://quaternius.itch.io/universal-base-characters | CC0 |
| Modular Character Outfits – Fantasy (Standard, kostenlos) | https://quaternius.itch.io/modular-character-outfits-fantasy | CC0 |
| Universal Animation Library 1 und 2 (Standard, kostenlos) | https://quaternius.itch.io/universal-animation-library | CC0 |

itch.io war aus der Claude-Umgebung nicht erreichbar. Die unveränderten Standard-Dateien stammen deshalb aus einer öffentlichen Kopie im Repository `OpenAgentsInc/openagents` (Ordner `assets/verse/characters/quaternius`, Stand `e6783578b3900f0d60dd0d5f9033ab26e9371c74`), dort mit SHA-256-Prüfsummen und den Original-Lizenztexten abgelegt. Wer will, kann die Originale kostenlos bei itch.io laden und mit `tools/figuren/bauen.mjs` neu bauen.

## Inhalt

| Datei | Inhalt | Dreiecke | Größe |
| --- | --- | --- | --- |
| `figuren/abenteurerin.glb` | Waldläuferin-Outfit in Weiß und Leder, Kopf des Grundkörpers, lange Haare, Kapuze (ausblendbar) | ca. 27.500 | 2,1 MB |
| `figuren/abenteurer.glb` | Waldläufer-Outfit in Grün und Leder, Kopf, Scheitel und Bart (beides ausblendbar), Kapuze | ca. 27.700 | 2,1 MB |
| `figuren/baeuerin.glb` | Bäuerin-Outfit, Kopf, Haarknoten | ca. 17.700 | 1,3 MB |
| `animationen/ual.glb` | 32 Animationen: Stehen, Gehen, Joggen, Rennen, Springen, Rolle, Schwertangriffe, Zauber, Treffer, Tod, Gießen, Ernten u. a. | – | 0,6 MB |

Alle Figuren nutzen dasselbe Skelett (65 Knochen, Namen wie `pelvis`, `hand_r`), deshalb passt jede Animation auf jede Figur.

Gebaut mit `tools/figuren/bauen.mjs`: Kleidung, Kopf und Haare liegen auf einem Skelett, verdeckte Haut ist entfernt, Texturen sind auf 1024 Pixel verkleinert.

## Im Spiel verwendet

| Klasse im Spiel | Figur | Ausgeblendet | Waffen (KayKit) |
| --- | --- | --- | --- |
| Sternenweberin | `abenteurerin` (blond) | Kapuze | `staff` |
| Klingenwächter | `abenteurer` | Kapuze, Bart | `sword_1handed`, `shield_badge_color` |
| Waldläufer | `abenteurer` mit Kapuze | Haare | `bow_withString` |
| Schattenklinge | `abenteurerin` mit Kapuze (dunkle Haare) | – | zwei `dagger` |
| Bärenherz | `abenteurer` mit rotem Bart | Kapuze, Haare | `axe_2handed` |
| Mira | `baeuerin` | – | – |

Die Zuordnung, Haarfarben und die Lage der Waffen in der Hand stehen oben in `client/figuren.js`.

## Grenzen der kostenlosen Fassung

- Nur zwei Outfits (Waldläufer, Bäuerin) je Mann und Frau. Die Source-Fassung (ca. 20 USD) hätte 12 Outfits, mehr Frisuren und Gesichter.
- Keine eigenen Bogen- und Magie-Animationen. Bogen und Zauber nutzen „Spell_Simple_Shoot“.
- Keine Winke-Animation. Mira erzählt stattdessen mit Gesten.
