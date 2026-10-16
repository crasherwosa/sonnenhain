#!/bin/sh
# Baut die eigene Abenteurerin komplett neu: Hauttextur, Blender-Modell, Export, Original-Skelett.
# Voraussetzungen (einmalig):
#   python3 -m venv ~/bvenv && ~/bvenv/bin/pip install bpy pillow scipy   (Blender als Python-Modul)
#   cd tools/figuren && npm install
#   Quaternius-Quelldateien in $QUATERNIUS (Aufbau: base/, hair/, textures/ – siehe assets/characters/eigene/README.md)
# Aufruf: QUATERNIUS=~/quaternius sh tools/blender/bauen.sh [render]
set -e
HIER=$(cd "$(dirname "$0")" && pwd)
PY=${BPY:-$HOME/bvenv/bin/python}
export ARBEIT=${ARBEIT:-$HIER/arbeit}
$PY "$HIER/textures.py"
$PY "$HIER/build.py" $1
$PY "$HIER/export.py" "$ARBEIT/blender.glb"
cd "$HIER/../figuren"
node skelett.mjs "$ARBEIT/blender.glb" "$QUATERNIUS/base/Superhero_Female_FullBody.gltf" ../../assets/characters/eigene/abenteurerin.glb
