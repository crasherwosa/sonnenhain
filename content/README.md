# Spielinhalte

Inhalte liegen als JSON-Dateien vor, damit sie ohne Programmierung ergänzt werden können, auch vom späteren Quest-Agenten.

## Quests (`quests/`)

Eine Datei pro Quest. Das Format ist in `schema/quest.schema.json` festgelegt.

| Feld | Bedeutung |
| --- | --- |
| `id` | Eindeutiger Name, klein mit Bindestrichen |
| `type` | `heart` (Herz-Aufgabe mit Fortschrittsbalken) oder `story` (Abfolge von Schritten) |
| `title` | Titel im Spiel |
| `region` | Region aus `docs/lore.md` |
| `giver` | Auftraggeber (NPC) |
| `summary` | Ein Satz für die Aufgabenliste |
| `dialogue` | Texte des Auftraggebers: `intro`, `progress`, `done` |
| `objectives` | Tätigkeiten mit Fortschrittspunkten |
| `rewards` | Erfahrung und später Gegenstände |

Ziele (`objectives`):

| `kind` | Bedeutung | Weitere Felder |
| --- | --- | --- |
| `defeat` | Gegner besiegen | `target`: `slime`, `shroom`, `champ` |
| `collect` | Gegenstand aufsammeln | `target`: z. B. `sunblossom` |
| `talk` | Mit jemandem sprechen | `target`: NPC-Name |

`points` ist der Beitrag pro Aktion zum Herz-Fortschritt (zusammen 100 = fertig).
