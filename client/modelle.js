// Umgebungsmodelle aus Blender (assets/environment/): Bäume, Büsche, Felsen, Klippen und Ruinen.
// Lädt die .glb-Dateien, legt gleiche Materialien (z. B. Rinde und Blätter) zusammen und
// bereitet sie für InstancedMesh vor. Wind, Gegenlicht und Wolkenschatten kommen im Spiel per Shader dazu.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const BASE = '../assets/environment/';
export const MODELLE = {
  laubbaum: ['baeume/laubbaum-1', 'baeume/laubbaum-2', 'baeume/laubbaum-3'],
  kiefer: ['baeume/kiefer-1', 'baeume/kiefer-2'],
  busch: ['baeume/busch-1', 'baeume/busch-2'],
  fels: ['felsen/fels-1', 'felsen/fels-2', 'felsen/fels-3', 'felsen/fels-4'],
  klippe: ['felsen/klippe-1', 'felsen/klippe-2'],
  bogen: ['ruinen/bogen'], saeule: ['ruinen/saeule'], schrein: ['ruinen/schrein'], turm: ['ruinen/turm'],
};
// Materialien mit Transparenz (Blätter, Nadeln, Efeu)
const isFoliage = m => m.alphaTest > 0 || m.transparent;

/* Lädt alle Modelle. Ergebnis: { laubbaum: [modell, …], … }, ein Modell ist { parts: [{ geometry, material }], size, radius }. */
export async function loadEnvModels(onProgress){
  const loader = new GLTFLoader(), shared = new Map();
  const names = Object.values(MODELLE).flat();
  let done = 0;
  const loaded = await Promise.all(names.map(n => loader.loadAsync(BASE + n + '.glb').then(g => { done++; if (onProgress) onProgress(done / names.length); return [n, g]; })));
  const byName = new Map(loaded);
  const out = {};
  for (const [kind, list] of Object.entries(MODELLE)) out[kind] = list.map(n => toModel(byName.get(n).scene, shared));
  return out;
}

function toModel(root, shared){
  root.updateMatrixWorld(true);
  const parts = [], box = new THREE.Box3();
  root.traverse(o => {
    if (!o.isMesh) return;
    const geometry = o.geometry.clone().applyMatrix4(o.matrixWorld);
    // Gleiche Materialien aus verschiedenen Dateien nur einmal behalten (spart Grafikspeicher)
    let material = o.material;
    if (shared.has(material.name)) { disposeMaterial(material); material = shared.get(material.name); }
    else {
      shared.set(material.name, material);
      if (isFoliage(material)) { material.alphaTest = 0.45; material.transparent = false; material.side = THREE.DoubleSide; }
      for (const t of [material.map, material.normalMap, material.roughnessMap]) if (t) t.anisotropy = 4;
    }
    geometry.computeBoundingBox(); box.union(geometry.boundingBox);
    parts.push({ geometry, material, foliage: isFoliage(material) });
  });
  const size = box.getSize(new THREE.Vector3());
  return { parts, size, radius: Math.max(size.x, size.z) / 2, box };
}

function disposeMaterial(m){
  for (const t of [m.map, m.normalMap, m.roughnessMap, m.metalnessMap, m.aoMap]) if (t) t.dispose();
  m.dispose();
}
