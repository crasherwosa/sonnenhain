# KayKit-Figuren

Quelle: Kay Lousberg, www.kaylousberg.com – Lizenz CC0 (frei nutzbar, auch kommerziell). Lizenztexte liegen in diesem Ordner.

| Ordner | Inhalt | Herkunft |
| --- | --- | --- |
| `figuren/` | Barbar, Ritter, Magierin, Waldläuferin, Schurke (auch mit Kapuze) als `.glb`, dazu ihre Farbtexturen | KayKit Adventurers 2.0 (Free) |
| `zubehoer/` | Waffen, Schilde, Köcher, Pfeile, Becher als `.gltf` + `.bin`, Texturen | KayKit Adventurers 2.0 (Free) |
| `animationen/` | Animationen für das mittlere Skelett (Rig_Medium): Bewegung, Kampf nah und fern, Allgemein, Spezial, Werkzeuge, Simulation | KayKit Character Animations 1.1 |

Alle Figuren nutzen das Skelett `Rig_Medium`, daher passen alle Animationen auf alle Figuren.

`uebersicht.png` zeigt den Inhalt des Pakets.

## Im Spiel verwendet

| Klasse im Spiel | Figur | Waffen |
| --- | --- | --- |
| Sternenweberin (Magierin) | `Mage.glb` | `staff` |
| Klingenwächter (Ritter) | `Knight.glb` | `sword_1handed`, `shield_badge_color` |
| Waldläufer | `Ranger.glb` | `bow_withString` |
| Schattenklinge (Schurkin) | `Rogue_Hooded.glb` | zwei `dagger` |
| Bärenherz (Barbar) | `Barbarian.glb` | `axe_2handed` |
| Mira (Bäuerin) | `Rogue.glb` ohne Umhang | – |

Geladen werden nur die Animationspakete General, MovementBasic, MovementAdvanced, CombatMelee, CombatRanged und Simulation. Die Zuordnung steht in `client/figuren.js`.
