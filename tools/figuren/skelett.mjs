// Setzt eine in Blender gebaute Figur auf das Original-Skelett der Quaternius-Figuren,
// damit alle Animationen aus assets/characters/quaternius/animationen/ual.glb passen.
//
// Blender dreht beim Import die Knochen etwas anders als im Original. Die Animationen
// speichern aber Drehungen relativ zu den Original-Knochen. Deshalb übernimmt dieses Skript
// Lage und Drehung jedes Knochens und die Bindungsmatrizen aus der Original-Datei.
// Die Punkte der Figur bleiben unverändert (beide Dateien nutzen denselben Raum, Füße auf 0).
//
//   cd tools/figuren && npm install
//   node skelett.mjs <blender-export.glb> <original-mit-skelett.gltf|glb> <ziel.glb>
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { prune, dedup, textureCompress } from '@gltf-transform/functions';
import sharp from 'sharp';
import { statSync } from 'node:fs';

const [SRC, REF, OUT] = process.argv.slice(2);
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const doc = await io.read(SRC);
const ref = await io.read(REF);

const refSkin = ref.getRoot().listSkins()[0];
const refJoints = refSkin.listJoints();
const refIbm = refSkin.getInverseBindMatrices().getArray();
const byName = new Map(refJoints.map((j, i) => [j.getName(), { node: j, ibm: refIbm.slice(i * 16, i * 16 + 16) }]));

for (const skin of doc.getRoot().listSkins()) {
  const joints = skin.listJoints();
  const ibm = skin.getInverseBindMatrices();
  const arr = ibm.getArray().slice();
  joints.forEach((j, i) => {
    const r = byName.get(j.getName());
    if (!r) throw new Error('Knochen fehlt im Original: ' + j.getName());
    j.setTranslation(r.node.getTranslation()).setRotation(r.node.getRotation()).setScale(r.node.getScale());
    arr.set(r.ibm, i * 16);
  });
  ibm.setArray(arr);
  const missing = refJoints.filter(j => !joints.some(k => k.getName() === j.getName())).map(j => j.getName());
  if (missing.length) console.log('Hinweis: Knochen nur im Original:', missing.join(', '));
}
// Der Armature-Knoten aus Blender bleibt ohne eigene Drehung
for (const n of doc.getRoot().listNodes()) if (n.getName() === 'Armature') n.setTranslation([0, 0, 0]).setRotation([0, 0, 0, 1]).setScale([1, 1, 1]);

// Haarsträhnen, Brauen, Wimpern: Durchsicht mit harter Kante (schnell, keine Sortierfehler)
for (const m of doc.getRoot().listMaterials()) {
  if (m.getName().startsWith('MASK_')) m.setAlphaMode('MASK').setAlphaCutoff(0.4).setDoubleSided(true);
  else m.setAlphaMode('OPAQUE');
}
const mask = new Set(doc.getRoot().listMaterials().filter(m => m.getAlphaMode() === 'MASK').map(m => m.getBaseColorTexture()).filter(Boolean));
for (const t of doc.getRoot().listTextures()) if (mask.has(t)) t.setName('MASK_' + t.getName().replace(/^MASK_/, ''));
await doc.transform(
  prune({ keepLeaves: true }),
  dedup(),
  textureCompress({ encoder: sharp, targetFormat: 'jpeg', resize: [1024, 1024], quality: 85, pattern: /^(?!MASK_)/ }),
  textureCompress({ encoder: sharp, targetFormat: 'png', resize: [512, 512], pattern: /^MASK_/ }),
);
await io.write(OUT, doc);
let tris = 0;
for (const m of doc.getRoot().listMeshes()) for (const p of m.listPrimitives()) tris += p.getIndices().getCount() / 3;
console.log(`${OUT}: ${tris} Dreiecke, ${(statSync(OUT).size / 1e6).toFixed(2)} MB, Meshes: ${doc.getRoot().listMeshes().map(m => m.getName()).join(', ')}`);
