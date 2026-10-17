#!/bin/sh
# Baut eigene Figuren neu: Rezept (tools/blender/figuren/<name>.py), Export mit gebackenen Details,
# Original-Skelett. Ergebnis: assets/characters/eigene/<name>.glb
# Voraussetzungen (einmalig):
#   python3 -m venv ~/bvenv && ~/bvenv/bin/pip install bpy pillow scipy   (Blender als Python-Modul)
#   cd tools/figuren && npm install
#   Quaternius-Quelldateien in $QUATERNIUS (Aufbau: base/, hair/, textures/ – siehe assets/characters/eigene/README.md)
# Aufruf: QUATERNIUS=~/quaternius sh tools/blender/bauen.sh [name ...]   (ohne Namen: alle Figuren)
set -e
HIER=$(cd "$(dirname "$0")" && pwd)
PY=${BPY:-$HOME/bvenv/bin/python}
export ARBEIT=${ARBEIT:-$HIER/arbeit}
NAMEN="$*"
[ -z "$NAMEN" ] && NAMEN=$(cd "$HIER/figuren" && ls *.py | sed 's/\.py$//')
for N in $NAMEN; do
  echo "== $N"
  $PY "$HIER/figuren/$N.py"
  $PY "$HIER/export.py" "$ARBEIT/$N/figur.blend" "$ARBEIT/$N/blender.glb"
  BASE=$(cat "$ARBEIT/$N/base")
  (cd "$HIER/../figuren" && node skelett.mjs "$ARBEIT/$N/blender.glb" "$QUATERNIUS/base/Superhero_${BASE}_FullBody.gltf" "../../assets/characters/eigene/$N.glb")
done
