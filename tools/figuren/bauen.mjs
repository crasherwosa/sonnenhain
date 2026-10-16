// Setzt Quaternius-Figuren (CC0) zu je einer schlanken .glb zusammen
// und baut eine gemeinsame Animationsdatei (assets/characters/quaternius/).
//
// Nur nötig, wenn Figuren neu gebaut werden sollen. Das Spiel selbst braucht kein npm.
//   cd tools/figuren && npm install
//   node bauen.mjs <quellordner> ../../assets/characters/quaternius
// <quellordner> enthält die Quaternius-Dateien im Aufbau von
// assets/characters/quaternius/README.md (outfits/, base/, hair/, textures/, gaits.glb, animations.glb).
//
// Was passiert: Kleidung + Kopf/Haut des Grundkörpers + Haare werden auf ein Skelett gelegt,
// verdeckte Haut wird entfernt, Dreiecke werden reduziert, Texturen auf 1024 px (Normalen 512 px)
// als JPEG verkleinert. Die Abenteurerin bekommt weiße statt grüner Stoffteile.
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { prune, dedup, weld, simplify, resample, mergeDocuments, unpartition } from '@gltf-transform/functions';
import { MeshoptSimplifier } from 'meshoptimizer';
import sharp from 'sharp';
import * as THREE from 'three';
import { MeshBVH } from 'three-mesh-bvh';
import { mkdirSync, statSync } from 'node:fs';
import { join } from 'node:path';

const [SRC, OUT] = process.argv.slice(2);
mkdirSync(join(OUT, 'figuren'), { recursive: true });
mkdirSync(join(OUT, 'animationen'), { recursive: true });
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
await MeshoptSimplifier.ready;

const CHARACTERS = {
  abenteurerin: { outfit: 'outfits/Female_Ranger.gltf', body: 'base/Superhero_Female_FullBody.gltf', hair: ['hair/Hair_Long.gltf'], optional: ['Female_Ranger_Head_Hood'], recolor: { material: 'MI_Ranger', color: [240, 233, 216] } },
  abenteurer:   { outfit: 'outfits/Male_Ranger.gltf',   body: 'base/Superhero_Male_FullBody.gltf',   hair: ['hair/Hair_SimpleParted.gltf', 'hair/Hair_Beard.gltf'], optional: ['Male_Ranger_Head_Hood'] },
  baeuerin:     { outfit: 'outfits/Female_Peasant.gltf', body: 'base/Superhero_Female_FullBody.gltf', hair: ['hair/Hair_Buns.gltf'], optional: [] },
};

// --- Hilfen ---------------------------------------------------------------
function triangles(prim){
  const pos = prim.getAttribute('POSITION').getArray();
  const idx = prim.getIndices().getArray();
  return { pos, idx };
}
function bvhFrom(meshes){
  const all = [];
  for (const m of meshes) for (const p of m.listPrimitives()) {
    const { pos, idx } = triangles(p);
    for (let i = 0; i < idx.length; i++) { const v = idx[i] * 3; all.push(pos[v], pos[v + 1], pos[v + 2]); }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(all, 3));
  g.boundsTree = new MeshBVH(g);
  return g;
}
// Entfernt Körperdreiecke, die vollständig von Kleidung verdeckt sind
function removeCovered(prim, coverGeo){
  const pos = prim.getAttribute('POSITION').getArray();
  const nrm = prim.getAttribute('NORMAL').getArray();
  const n = pos.length / 3;
  const covered = new Uint8Array(n);
  const ray = new THREE.Ray(), o = new THREE.Vector3(), d = new THREE.Vector3();
  const mesh = new THREE.Mesh(coverGeo, new THREE.MeshBasicMaterial({ side: THREE.DoubleSide }));
  const rc = new THREE.Raycaster(); rc.firstHitOnly = true;
  for (let i = 0; i < n; i++) {
    d.set(nrm[i * 3], nrm[i * 3 + 1], nrm[i * 3 + 2]).normalize();
    // Kleidung außen (bis 10 cm) oder knapp innerhalb der Haut (bis 3 cm) gilt als verdeckt
    o.set(pos[i * 3], pos[i * 3 + 1], pos[i * 3 + 2]).addScaledVector(d, -0.03);
    ray.set(o, d);
    const hit = coverGeo.boundsTree.raycastFirst(ray, THREE.DoubleSide);
    if (hit && hit.distance < 0.13) covered[i] = 1;
  }
  const idx = prim.getIndices().getArray();
  const keep = [];
  for (let i = 0; i < idx.length; i += 3)
    if (!(covered[idx[i]] && covered[idx[i + 1]] && covered[idx[i + 2]])) keep.push(idx[i], idx[i + 1], idx[i + 2]);
  const before = idx.length / 3;
  prim.getIndices().setArray(new Uint32Array(keep));
  return [before, keep.length / 3];
}
async function shrinkTextures(doc){
  for (const tex of doc.getRoot().listTextures()) {
    const slots = new Set(tex.listParents().flatMap(p => p.propertyType === 'Material' ? doc.getGraph().listParentEdges(tex).filter(e => e.getParent() === p).map(e => e.getName()) : []));
    const isNormal = slots.has('normalTexture');
    const size = isNormal ? 512 : 1024;
    const img = sharp(Buffer.from(tex.getImage())).resize(size, size, { fit: 'fill' }).removeAlpha();
    const buf = await img.jpeg({ quality: isNormal ? 88 : 84, mozjpeg: true }).toBuffer();
    tex.setImage(new Uint8Array(buf)).setMimeType('image/jpeg');
    const uri = tex.getURI(); if (uri) tex.setURI(uri.replace(/\.png$/i, '.jpg'));
  }
}
// Färbt grüne Stoffteile in eine andere Farbe um (Leder und Metall bleiben)
async function recolor(doc, { material, color }){
  const mat = doc.getRoot().listMaterials().find(m => m.getName() === material);
  const tex = mat.getBaseColorTexture();
  const { data, info } = await sharp(Buffer.from(tex.getImage())).resize(1024, 1024, { fit: 'fill' }).removeAlpha().raw().toBuffer({ resolveWithObject: true });
  const smooth = (a, b, x) => { const t = Math.max(0, Math.min(1, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
  for (let i = 0; i < data.length; i += 3) {
    const r = data[i] / 255, g = data[i + 1] / 255, b = data[i + 2] / 255;
    const mx = Math.max(r, g, b), mn = Math.min(r, g, b), sat = mx > 0 ? (mx - mn) / mx : 0;
    let h = 0;
    if (mx !== mn) h = mx === r ? ((g - b) / (mx - mn)) % 6 : mx === g ? (b - r) / (mx - mn) + 2 : (r - g) / (mx - mn) + 4;
    h = (h * 60 + 360) % 360;
    const w = smooth(55, 75, h) * (1 - smooth(165, 185, h)) * smooth(0.18, 0.35, sat);
    if (w <= 0) continue;
    const shade = 0.66 + 0.34 * Math.min(1, mx / 0.55);
    for (let c = 0; c < 3; c++) data[i + c] = Math.round(data[i + c] * (1 - w) + color[c] * shade * w);
  }
  const png = await sharp(data, { raw: { width: info.width, height: info.height, channels: 3 } }).png().toBuffer();
  tex.setImage(new Uint8Array(png)).setMimeType('image/png');
}
function simplifyMaterials(doc){
  for (const m of doc.getRoot().listMaterials()) {
    const mr = m.getMetallicRoughnessTexture(); if (mr) m.setMetallicRoughnessTexture(null);
    m.setMetallicFactor(0).setRoughnessFactor(0.85).setDoubleSided(false);
  }
}
function skinOf(doc){ return doc.getRoot().listSkins()[0]; }
function jointNames(skin){ return skin.listJoints().map(j => j.getName()); }

// --- Figuren --------------------------------------------------------------
for (const [name, def] of Object.entries(CHARACTERS)) {
  const doc = await io.read(join(SRC, def.outfit));
  const mainSkin = doc.getRoot().listSkins()[0];
  const names = jointNames(mainSkin);
  const outfitMeshes = doc.getRoot().listMeshes();
  const cover = bvhFrom(outfitMeshes.filter(m => !def.optional.includes(m.getName())));

  // Körper: nur unverdeckte Teile behalten
  const bodyDoc = await io.read(join(SRC, def.body));
  for (const m of bodyDoc.getRoot().listMeshes()) {
    if (/^Super|^Body/i.test(m.getName()) || m.listPrimitives()[0].getIndices().getCount() > 20000) {
      for (const p of m.listPrimitives()) { const [a, b] = removeCovered(p, cover); console.log(`${name}: Körper ${a} -> ${b} Dreiecke`); }
      m.setName('Body');
    }
  }
  const parts = [bodyDoc];
  for (const h of def.hair) {
    const hd = await io.read(join(SRC, h));
    const base = h.split('/').pop().replace('.gltf', '');
    hd.getRoot().listNodes().forEach(n => { if (n.getMesh()) { n.setName(base); n.getMesh().setName(base); } });
    parts.push(hd);
  }
  bodyDoc.getRoot().listNodes().forEach(n => { if (n.getMesh()) { const nm = /^Super/i.test(n.getName()) ? 'Body' : n.getName(); n.setName(nm); n.getMesh().setName(nm); } });

  for (const part of parts) {
    const ps = skinOf(part);
    if (jointNames(ps).join() !== names.join()) throw new Error('Skelett passt nicht: ' + name);
    const map = mergeDocuments(doc, part);
    // Alle übernommenen Meshes auf das Skelett der Kleidung umhängen
    const newSkin = map.get(ps);
    for (const node of doc.getRoot().listNodes()) if (node.getSkin() === newSkin) node.setSkin(mainSkin);
    // überzählige Szene, Armature und Skin entfernen
    const scenes = doc.getRoot().listScenes();
    const extra = scenes[scenes.length - 1];
    const mainScene = scenes[0];
    for (const child of extra.listChildren()) {
      child.traverse(n => { if (n.getMesh()) { n.setSkin(mainSkin); mainScene.addChild(n); } });
    }
    extra.dispose();
    newSkin.dispose();
  }
  // Mesh-Knoten an die Wurzel der Szene, damit nichts doppelt transformiert wird
  const mainScene = doc.getRoot().listScenes()[0];
  for (const node of doc.getRoot().listNodes()) if (node.getMesh() && node.getParentNode()) { node.getParentNode().removeChild(node); mainScene.addChild(node); }

  simplifyMaterials(doc);
  await doc.transform(
    prune({ keepLeaves: true }),
    dedup(),
    weld(),
    simplify({ simplifier: MeshoptSimplifier, ratio: 0.55, error: 0.0008, lockBorder: true }),
    prune({ keepLeaves: true }),
    unpartition(),
  );
  if (def.recolor) await recolor(doc, def.recolor);
  await shrinkTextures(doc);
  await doc.transform(dedup());
  let tris = 0;
  for (const m of doc.getRoot().listMeshes()) for (const p of m.listPrimitives()) tris += p.getIndices().getCount() / 3;
  const file = join(OUT, 'figuren', name + '.glb');
  await io.write(file, doc);
  console.log(`${name}: ${tris} Dreiecke, ${(statSync(file).size / 1e6).toFixed(2)} MB, Meshes: ${doc.getRoot().listMeshes().map(m => m.getName()).join(', ')}`);
}

// --- Animationen ----------------------------------------------------------
const CLIPS = {
  'gaits.glb': ['Idle_Loop', 'Idle_Talking_Loop', 'Walk_Loop', 'Jog_Fwd_Loop', 'Sprint_Loop', 'Jump_Start', 'Jump_Loop', 'Jump_Land', 'Roll', 'Death01', 'Hit_Chest', 'Hit_Head', 'Spell_Simple_Shoot', 'Spell_Simple_Enter', 'Spell_Simple_Idle_Loop', 'Sword_Attack', 'Sword_Idle', 'Interact'],
  'animations.glb': ['Sword_Regular_A', 'Sword_Regular_B', 'Sword_Regular_C', 'Sword_Heavy_Combo', 'Sword_Dash', 'Sword_Block', 'Idle_Shield_Loop', 'Shield_OneShot', 'Hit_Knockback', 'OverhandThrow', 'Farm_Watering', 'Farm_Harvest', 'Idle_FoldArms_Loop', 'Yes'],
};
const anim = await io.read(join(SRC, 'gaits.glb'));
{
  const other = await io.read(join(SRC, 'animations.glb'));
  // Animationen der zweiten Datei auf die Knochen der ersten umleiten
  const byName = new Map(anim.getRoot().listNodes().map(n => [n.getName(), n]));
  const map = mergeDocuments(anim, other);
  for (const a of anim.getRoot().listAnimations()) for (const c of a.listChannels()) {
    const t = c.getTargetNode(); const mine = byName.get(t.getName());
    if (mine && mine !== t) c.setTargetNode(mine);
  }
  const scenes = anim.getRoot().listScenes(); scenes.slice(1).forEach(s => { s.listChildren().forEach(c => c.traverse(n => n.dispose())); s.dispose(); });
  void map;
}
const wanted = new Set(Object.values(CLIPS).flat());
const seen = new Set();
for (const a of anim.getRoot().listAnimations()) {
  if (!wanted.has(a.getName()) || seen.has(a.getName())) { a.listChannels().forEach(c => c.dispose()); a.listSamplers().forEach(x => x.dispose()); a.dispose(); continue; }
  seen.add(a.getName());
  for (const c of a.listChannels()) {
    const path = c.getTargetPath(), bone = c.getTargetNode().getName();
    // nur Drehungen übertragen; Verschiebung nur für das Becken (Körperhöhe, Sprünge)
    if (path === 'scale' || /_leaf_/.test(bone) || (path === 'translation' && bone !== 'pelvis')) { const s = c.getSampler(); c.dispose(); s.dispose(); }
  }
}
for (const m of anim.getRoot().listMeshes()) m.dispose();
for (const n of anim.getRoot().listNodes()) n.setMesh(null).setSkin(null);
for (const s of anim.getRoot().listSkins()) s.dispose();
await anim.transform(resample({ tolerance: 0.0008 }), prune({ keepLeaves: true }), dedup(), unpartition());
// Drehungen als 16-Bit-Zahlen speichern (halbe Dateigröße, kein sichtbarer Unterschied)
for (const a of anim.getRoot().listAnimations()) for (const c of a.listChannels()) {
  if (c.getTargetPath() !== 'rotation') continue;
  const out = c.getSampler().getOutput();
  if (out.getComponentType() !== 5126) continue;
  const src = out.getArray(), q = new Int16Array(src.length);
  for (let i = 0; i < src.length; i++) q[i] = Math.round(Math.max(-1, Math.min(1, src[i])) * 32767);
  out.setArray(q).setNormalized(true);
}
for (const acc of anim.getRoot().listAccessors()) if (acc.listParents().filter(p => p.propertyType !== 'Root' && !p.isDisposed()).length === 0) acc.dispose();
await anim.transform(dedup(), prune());
const afile = join(OUT, 'animationen', 'ual.glb');
await io.write(afile, anim);
console.log(`Animationen: ${anim.getRoot().listAnimations().length} Clips (${[...seen].join(', ')}), ${(statSync(afile).size / 1e6).toFixed(2)} MB`);
const missing = [...wanted].filter(x => !seen.has(x)); if (missing.length) console.log('FEHLEN:', missing);
