# Arbeitsweise

## Zwei Werkstätten

| | Modelle | Spiel |
| --- | --- | --- |
| Wo | Claude Desktop auf dem Mac, verbunden mit Blender | Claude-Chat (Handy oder Mac), verbunden mit diesem Repository |
| Ergebnis | `.glb`-Dateien in `assets/` | Neue Version des Spiels |

Die `.glb`-Dateien sind die Brücke zwischen beiden.

## Ablauf einer Aufgabe

1. Neuen Chat starten, mit einem Satz sagen, worum es geht. Beispiel: „Arbeite am Repo `crasherwosa/sonnenhain` weiter: Baue die Ritter-Animationen ein.“
2. Claude liest `CLAUDE.md` und die Dokumente, setzt die Aufgabe um, testet und schickt eine Vorschau.
3. Prüfen. Passt es: „übernehmen“. Sonst sagen, was anders sein soll.
4. Claude speichert die Änderung im Repository.

## Freigaben am Handy

Die GitHub-App zeigt jede Änderung. Vorschläge (Pull Requests) lassen sich dort mit einem Tipp annehmen.

## Sicherheit

- Keine Passwörter oder Schlüssel in den Chat oder ins Repository.
- Serverzugänge kommen später verschlüsselt in die GitHub-Einstellungen (Secrets).
