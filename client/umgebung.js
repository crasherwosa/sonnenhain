// Umgebung: gemalte Haufenwolken, Unterholz (Farne, Grasbüschel, Schilf), Seerosen, Baumstümpfe und Wind.
// Alles wird beim Start im Code erzeugt (keine fremden Dateien). Dichte, Sichtweite und Wind folgen den Grafikstufen.
import * as THREE from 'three';

const V3 = THREE.Vector3;
const clamp = (v, a, b) => v < a ? a : v > b ? b : v;
const lerp = (a, b, t) => a + (b - a) * t;
function mulberry32(a){ return function(){ a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }

/* Wind for instanced plants: sways with height above the plant's foot, slow gusts roll across the meadow.
   Needs the uniforms uTime and uWind, and `ip` (instance position) declared before it. */
export const WIND_GLSL = `
  float wGust = 0.55 + 0.45 * sin(dot(ip.xz, vec2(0.09, 0.06)) - uTime * 1.25);
  float wH = max(position.y, 0.0);
  transformed.x += (sin(uTime * 1.6 + ip.x * 0.45 + ip.z * 0.3) * 0.7 + 0.3) * wH * wH * 0.05 * uWind * wGust;
  transformed.z += sin(uTime * 1.3 + ip.z * 0.5 + 1.7) * wH * wH * 0.035 * uWind * wGust;`;

/* ---------- Painted textures (canvas) ---------- */
function canvas(w, h){ const c = document.createElement('canvas'); c.width = w; c.height = h; return c; }
function toTex(cv, aniso, srgb = true){ const t = new THREE.CanvasTexture(cv); if (srgb) t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = aniso; return t; }

// Fern frond: rachis with alternating, serrated leaflets, lighter toward the tip
function makeFernTex(S){
  const W = S / 2, cv = canvas(W, S), x = cv.getContext('2d'), rnd = mulberry32(91);
  const cx = W / 2, y0 = S * 0.985, y1 = S * 0.02, N = 30;
  x.lineCap = 'round'; x.lineJoin = 'round';
  for (let i = 2; i < N; i++) {
    const t = i / N, py = lerp(y0, y1, t), px = cx + Math.sin(t * 3) * W * 0.015;
    const len = W * 0.47 * Math.pow(Math.sin(Math.PI * (0.12 + 0.88 * t)), 0.7) * (1 - t * 0.3);
    for (const sd of [-1, 1]) {
      const a = 0.32 + t * 0.45 + (rnd() - 0.5) * 0.08, ex = px + sd * Math.cos(a) * len, ey = py - Math.sin(a) * len - (sd > 0 ? W * 0.012 : 0);
      const segs = Math.max(4, Math.round(len / (W * 0.035))), wid = W * 0.034 * (0.8 + 0.4 * (1 - t));
      const hue = 92 + rnd() * 14 + t * 8, sat = 42 + rnd() * 12, li = 24 + t * 16 + rnd() * 6;
      const g = x.createLinearGradient(px, py, ex, ey);
      g.addColorStop(0, `hsl(${hue},${sat}%,${li * 0.8}%)`); g.addColorStop(1, `hsl(${hue + 8},${sat + 6}%,${li * 1.25}%)`);
      x.fillStyle = g;
      x.beginPath(); x.moveTo(px, py);
      const nx = -(ey - py) / len, ny = (ex - px) / len;
      for (let k = 0; k <= segs; k++) { const s = k / segs, w = wid * Math.pow(1 - s, 0.7) * (0.72 + 0.28 * Math.abs(Math.sin(s * segs * Math.PI))); x.lineTo(lerp(px, ex, s) + nx * w, lerp(py, ey, s) + ny * w); }
      for (let k = segs; k >= 0; k--) { const s = k / segs, w = wid * Math.pow(1 - s, 0.7) * (0.72 + 0.28 * Math.abs(Math.sin(s * segs * Math.PI + 1.3))); x.lineTo(lerp(px, ex, s) - nx * w, lerp(py, ey, s) - ny * w); }
      x.closePath(); x.fill();
      x.strokeStyle = `hsla(${hue},${sat}%,${li * 1.5}%,0.55)`; x.lineWidth = W * 0.004;
      x.beginPath(); x.moveTo(px, py); x.lineTo(lerp(px, ex, 0.9), lerp(py, ey, 0.9)); x.stroke();
    }
  }
  x.strokeStyle = '#4b5a22'; x.lineWidth = W * 0.014;
  x.beginPath(); x.moveTo(cx, y0); for (let i = 1; i <= 20; i++) { const t = i / 20; x.lineTo(cx + Math.sin(t * 3) * W * 0.015, lerp(y0, y1, t)); } x.stroke();
  return cv;
}
// Grass clump: tapered blades from dark roots to sunny tips, a few seed stalks
function makeClumpTex(S){
  const cv = canvas(S, S), x = cv.getContext('2d'), rnd = mulberry32(17);
  const blade = (bx, h, bend, w, hue, li) => {
    const tx = bx + bend, ty = S - h, g = x.createLinearGradient(0, S, 0, ty);
    g.addColorStop(0, `hsl(${hue},45%,${li * 0.45}%)`); g.addColorStop(0.6, `hsl(${hue},48%,${li}%)`); g.addColorStop(1, `hsl(${hue + 10},52%,${li * 1.3}%)`);
    x.fillStyle = g; x.beginPath(); x.moveTo(bx - w, S);
    x.quadraticCurveTo(bx - w * 0.6 + bend * 0.25, S - h * 0.55, tx, ty);
    x.quadraticCurveTo(bx + w * 0.6 + bend * 0.25, S - h * 0.55, bx + w, S); x.closePath(); x.fill();
  };
  for (let i = 0; i < 90; i++) {
    const t = i / 90, bx = S * (0.5 + (rnd() - 0.5) * 0.7 * (0.4 + 0.6 * rnd()));
    const h = S * (0.45 + rnd() * 0.5) * (1 - Math.abs(bx / S - 0.5) * 0.9), bend = (bx - S / 2) * (0.5 + rnd()) + (rnd() - 0.5) * S * 0.15;
    blade(bx, h, bend, S * (0.008 + rnd() * 0.008), 70 + rnd() * 28, 26 + t * 22 + rnd() * 8);
  }
  for (let i = 0; i < 5; i++) {
    const bx = S * (0.3 + rnd() * 0.4), h = S * (0.75 + rnd() * 0.22), tx = bx + (rnd() - 0.5) * S * 0.2, ty = S - h;
    x.strokeStyle = 'hsl(48,40%,62%)'; x.lineWidth = S * 0.004; x.beginPath(); x.moveTo(bx, S); x.quadraticCurveTo(bx, S - h * 0.5, tx, ty); x.stroke();
    x.fillStyle = 'hsl(45,48%,70%)';
    for (let k = 0; k < 7; k++) { x.beginPath(); x.ellipse(tx + (rnd() - 0.5) * S * 0.02, ty + k * S * 0.012, S * 0.006, S * 0.012, (rnd() - 0.5), 0, 6.283); x.fill(); }
  }
  return cv;
}
// Reeds: tall straight blades and a few cattails
function makeReedTex(S){
  const cv = canvas(S / 2, S), W = S / 2, x = cv.getContext('2d'), rnd = mulberry32(5);
  for (let i = 0; i < 40; i++) {
    const bx = W * (0.15 + rnd() * 0.7), h = S * (0.55 + rnd() * 0.43), tx = bx + (rnd() - 0.5) * W * 0.25, w = W * (0.012 + rnd() * 0.01), li = 26 + rnd() * 22;
    const g = x.createLinearGradient(0, S, 0, S - h); g.addColorStop(0, `hsl(85,35%,${li * 0.5}%)`); g.addColorStop(1, `hsl(${70 + rnd() * 15},45%,${li * 1.25}%)`);
    x.fillStyle = g; x.beginPath(); x.moveTo(bx - w, S); x.quadraticCurveTo(bx, S - h * 0.6, tx, S - h); x.quadraticCurveTo(bx + w * 0.5, S - h * 0.6, bx + w, S); x.fill();
  }
  for (let i = 0; i < 4; i++) {
    const bx = W * (0.25 + rnd() * 0.5), h = S * (0.7 + rnd() * 0.25);
    x.strokeStyle = 'hsl(80,30%,35%)'; x.lineWidth = W * 0.012; x.beginPath(); x.moveTo(bx, S); x.lineTo(bx, S - h); x.stroke();
    const g = x.createLinearGradient(bx - W * 0.03, 0, bx + W * 0.03, 0); g.addColorStop(0, '#3e2412'); g.addColorStop(0.45, '#7a4a26'); g.addColorStop(1, '#3a2010');
    x.fillStyle = g; x.beginPath(); x.ellipse(bx, S - h + S * 0.07, W * 0.03, S * 0.06, 0, 0, 6.283); x.fill();
  }
  return cv;
}
// Cumulus clouds: 2 x 2 atlas. Red = sunlit amount (tops bright, bellies shaded), alpha = cloud mask.
function makeCloudAtlas(S){
  const W = S, H = S / 2, cw = W / 2, ch = H / 2, A = canvas(W, H), L = canvas(W, H), xa = A.getContext('2d'), xl = L.getContext('2d'), rnd = mulberry32(404);
  xl.fillStyle = '#000'; xl.fillRect(0, 0, W, H);
  for (let cell = 0; cell < 4; cell++) {
    const ox = (cell % 2) * cw, oy = Math.floor(cell / 2) * ch, flat = cell === 3, base = oy + ch * (flat ? 0.68 : 0.8);
    const n = flat ? 34 : 46;
    for (let i = 0; i < n; i++) {
      const u = 0.1 + rnd() * 0.8, hump = Math.pow(Math.sin(Math.PI * u), flat ? 2.2 : 1.1);
      const r = ch * (flat ? 0.16 : 0.24) * (0.45 + 0.75 * hump) * (0.7 + rnd() * 0.5);
      const px = ox + cw * u, py = Math.min(base - r * 0.35, base - hump * ch * (flat ? 0.18 : 0.42) * rnd() - r * 0.2);
      let g = xa.createRadialGradient(px, py, r * 0.35, px, py, r);
      g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(0.7, 'rgba(255,255,255,0.75)'); g.addColorStop(1, 'rgba(255,255,255,0)');
      xa.fillStyle = g; xa.beginPath(); xa.arc(px, py, r, 0, 6.283); xa.fill();
      g = xl.createRadialGradient(px - r * 0.15, py - r * 0.45, r * 0.05, px, py - r * 0.2, r * 0.95);
      g.addColorStop(0, 'rgba(255,255,255,0.95)'); g.addColorStop(0.6, 'rgba(255,255,255,0.35)'); g.addColorStop(1, 'rgba(255,255,255,0)');
      xl.fillStyle = g; xl.beginPath(); xl.arc(px, py, r, 0, 6.283); xl.fill();
    }
  }
  const da = xa.getImageData(0, 0, W, H).data, out = xl.getImageData(0, 0, W, H), dl = out.data;
  for (let i = 0; i < dl.length; i += 4) {
    const y = (i / 4 / W | 0) % ch / ch;
    const lit = clamp(dl[i] / 255 * 1.15 + (0.55 - y) * 0.5, 0, 1);
    dl[i] = dl[i + 1] = dl[i + 2] = Math.round(lit * 255); dl[i + 3] = Math.round(Math.pow(da[i + 3] / 255, 1.25) * 255);
  }
  xl.putImageData(out, 0, 0);
  return L;
}

/* ---------- Geometry helpers ---------- */
class Builder {
  constructor(){ this.p = []; this.n = []; this.u = []; this.a = []; this.i = []; }
  v(p, n, u, v, a){ this.p.push(p.x, p.y, p.z); this.n.push(n.x, n.y, n.z); this.u.push(u, v); this.a.push(a); return this.p.length / 3 - 1; }
  geo(){
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(this.p, 3));
    g.setAttribute('normal', new THREE.Float32BufferAttribute(this.n, 3));
    g.setAttribute('uv', new THREE.Float32BufferAttribute(this.u, 2));
    g.setAttribute('ao', new THREE.Float32BufferAttribute(this.a, 1));
    g.setIndex(this.i); g.computeBoundingSphere();
    return g;
  }
}
// An arching, slightly folded leaf card from the plant's foot outward (fern frond, grass blade card, reed card)
function frond(B, az, L, w, el, droop, fold, aoBase, segs = 4){
  const dir = new V3(Math.cos(az), 0, Math.sin(az)), side = new V3(-dir.z, 0, dir.x), up = new V3(0, 1, 0);
  const nrm = up.clone().multiplyScalar(0.8).addScaledVector(dir, 0.45).normalize();
  const rows = [];
  for (let s = 0; s <= segs; s++) {
    const t = s / segs, c = dir.clone().multiplyScalar(L * t * Math.cos(el)).addScaledVector(up, L * (t * Math.sin(el) - droop * t * t));
    const a = lerp(aoBase, 1, t);
    rows.push([
      B.v(c.clone().addScaledVector(side, -w / 2).addScaledVector(up, -fold * w), nrm, 0, t, a),
      B.v(c, nrm, 0.5, t, a),
      B.v(c.clone().addScaledVector(side, w / 2).addScaledVector(up, -fold * w), nrm, 1, t, a),
    ]);
  }
  for (let s = 0; s < segs; s++) for (let k = 0; k < 2; k++) {
    const a = rows[s][k], b = rows[s][k + 1], c = rows[s + 1][k], d = rows[s + 1][k + 1];
    B.i.push(a, b, c, c, b, d);
  }
}
function fernGeo(seed){
  const rnd = mulberry32(seed), B = new Builder(), n = 7 + Math.floor(rnd() * 3);
  for (let k = 0; k < n; k++) { const L = 0.75 + rnd() * 0.45; frond(B, k / n * 6.283 + rnd() * 0.5, L, L * 0.5, 0.95 + rnd() * 0.3, 0.6 + rnd() * 0.25, 0.12, 0.35); }
  return B.geo();
}
function clumpGeo(seed){
  const rnd = mulberry32(seed), B = new Builder();
  for (let k = 0; k < 5; k++) frond(B, k / 5 * 6.283 + rnd() * 0.4, 0.75 + rnd() * 0.25, 0.75, 1.32 + rnd() * 0.15, 0.22, 0.0, 0.45, 3);
  return B.geo();
}
function reedGeo(seed){
  const rnd = mulberry32(seed), B = new Builder();
  for (let k = 0; k < 4; k++) frond(B, k / 4 * 3.1416 + rnd() * 0.5, 1.6 + rnd() * 0.5, 0.8, 1.5, 0.04, 0.0, 0.5, 2);
  return B.geo();
}
// Small five-petal blossom, cupped, with a golden centre (vertex colours)
export function blossomGeo(r = 0.085){
  const g = new THREE.CircleGeometry(r, 30), p = g.attributes.position, col = new Float32Array(p.count * 3);
  for (let i = 0; i < p.count; i++) {
    const x = p.getX(i), y = p.getY(i), d = Math.hypot(x, y);
    if (d < 1e-6) { col.set([1.0, 0.78, 0.25], i * 3); continue; }
    const a = Math.atan2(y, x), k = 0.5 + 0.5 * Math.pow(Math.abs(Math.cos(a * 2.5)), 0.6);
    p.setXYZ(i, x * k, y * k, d * 0.18);
    col.set([1, 1, 1], i * 3);
  }
  g.setAttribute('color', new THREE.BufferAttribute(col, 3));
  g.rotateX(-Math.PI / 2); g.computeVertexNormals();
  return g;
}

/* ---------- Materials ---------- */
function plantMat(map, ctx, translucency = 0.8){
  const m = new THREE.MeshStandardMaterial({ map, alphaTest: 0.5, alphaToCoverage: true, side: THREE.DoubleSide, roughness: 0.8 });
  m.onBeforeCompile = sh => {
    Object.assign(sh.uniforms, { uTime: ctx.shared.uTime, uWind: ctx.shared.uWind, uPlantFar: ctx.shared.uPlantFar, tCloud: { value: ctx.TEX.cloud } });
    sh.vertexShader = 'attribute float ao; uniform float uTime, uWind, uPlantFar; varying float vAO; varying vec3 vLW;\n' + sh.vertexShader.replace('#include <begin_vertex>', `#include <begin_vertex>
      vec3 ip = vec3(instanceMatrix[3][0], instanceMatrix[3][1], instanceMatrix[3][2]);
      ${WIND_GLSL}
      transformed *= 1.0 - smoothstep(uPlantFar * 0.7, uPlantFar, distance(ip.xz, cameraPosition.xz));
      vAO = ao; vLW = (modelMatrix * instanceMatrix * vec4(transformed, 1.0)).xyz;`);
    sh.fragmentShader = 'uniform sampler2D tCloud; uniform float uTime; varying float vAO; varying vec3 vLW;\n' + ctx.CLOUD_GLSL + sh.fragmentShader
      .replace('#include <map_fragment>', ctx.MIP_ALPHA_GLSL)
      .replace('#include <color_fragment>', `#include <color_fragment>
        diffuseColor.rgb *= vAO * cloudSh(vLW.xz);`)
      .replace('#include <normal_fragment_begin>', `#include <normal_fragment_begin>
        normal = normalize(vNormal);`)
      .replace('#include <emissivemap_fragment>', `#include <emissivemap_fragment>
        totalEmissiveRadiance += diffuseColor.rgb * pow(max(dot(normalize(vLW - cameraPosition), ${ctx.SUNV}), 0.0), 4.0) * ${translucency.toFixed(2)} * vAO;`);
  };
  m.customProgramCacheKey = () => 'plant' + translucency;
  return m;
}

/* ---------- Scattering into chunks, so whole chunks outside the view distance are skipped ---------- */
const CHUNK = 40;
function scatter(geo, mat, items, opts = {}){
  const buckets = new Map();
  for (const it of items) { const k = Math.floor(it.x / CHUNK) + ',' + Math.floor(it.z / CHUNK); if (!buckets.has(k)) buckets.set(k, []); buckets.get(k).push(it); }
  const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler(), s = new V3(), p = new V3(), c = new THREE.Color(), meshes = [];
  for (const [k, list] of buckets) {
    const mesh = new THREE.InstancedMesh(geo, mat, list.length);
    list.forEach((it, i) => {
      q.setFromEuler(e.set(it.tx || 0, it.rot, it.tz || 0)); s.set(it.s, it.sy || it.s, it.s);
      mesh.setMatrixAt(i, m4.compose(p.set(it.x, it.y, it.z), q, s)); mesh.setColorAt(i, c.setRGB(it.c[0], it.c[1], it.c[2]));
    });
    mesh.computeBoundingSphere();
    const [cx, cz] = k.split(',').map(Number);
    Object.assign(mesh.userData, { cx: (cx + 0.5) * CHUNK, cz: (cz + 0.5) * CHUNK, n: list.length, far: opts.far || 1 });
    mesh.receiveShadow = true; mesh.castShadow = !!opts.cast;
    if (opts.depth) mesh.customDepthMaterial = opts.depth;
    meshes.push(mesh);
  }
  return meshes;
}

/* =========================================================
   Undergrowth, shore plants, lily pads, stumps and logs
   ========================================================= */
export function buildUndergrowth(ctx){
  const { scene, getH, pathAt, slopeAt, forestAt, noise, LAKES, isTouch, MAXANISO } = ctx;
  const S = isTouch ? 512 : 1024;
  const fernTex = toTex(makeFernTex(S), MAXANISO), clumpTex = toTex(makeClumpTex(S / 2), MAXANISO), reedTex = toTex(makeReedTex(S), MAXANISO);
  const fernMat = plantMat(fernTex, ctx, 0.9), clumpMat = plantMat(clumpTex, ctx, 1.0), reedMat = plantMat(reedTex, ctx, 0.6);
  const blocked = (x, z) => (x > -15.5 && x < -3.5 && z > 4.5 && z < 13.5) || (x > 2.8 && x < 16 && z > 5 && z < 15) || Math.hypot(x - 13, z + 9) < 3.5 || Math.hypot(x + 2.3, z + 4.7) < 2.5 ||
    Math.hypot(x + 60, z - 36) < 10.5 || Math.hypot(x + 102, z + 50) < 7 || Math.hypot(x - 84, z - 66) < 5;
  const all = [];
  const add = list => { for (const m of list) { scene.add(m); all.push(m); } return list; };
  const mult = isTouch ? 0.55 : 1;

  // Ferns: under trees and in shady hollows
  { const rnd = mulberry32(2101), items = [], N = Math.round(7000 * mult); let tries = 0;
    while (items.length < N && tries < N * 30) { tries++;
      const x = (rnd() * 2 - 1) * 178, z = (rnd() * 2 - 1) * 178, f = forestAt(x, z);
      if (f < 0.06 && !(noise(x * 0.05 + 40, z * 0.05) > 0.5 && rnd() < 0.3)) continue;
      const h = getH(x, z), r = Math.hypot(x, z);
      if (h < 0.7 || h > 30 || r < 18 || r > 182 || slopeAt(x, z) > 0.45 || pathAt(x, z) < 2.6 || blocked(x, z)) continue;
      const v = 0.8 + rnd() * 0.35, yel = rnd() < 0.15 ? 0.18 : 0;
      items.push({ x, y: h - 0.05, z, rot: rnd() * 6.283, s: 0.95 + rnd() * 0.7 + f * 0.4, c: [v * (0.84 + yel), v * (0.9 + yel * 0.4), v * (0.68 - yel)] });
    }
    const geos = [11, 12, 13].map(fernGeo);
    geos.forEach((g, k) => add(scatter(g, fernMat, items.filter((_, i) => i % 3 === k))));
  }
  // Grass clumps: forest edges, around rocks and in loose meadow patches
  { const rnd = mulberry32(2202), items = [], N = Math.round(5000 * mult); let tries = 0;
    while (items.length < N && tries < N * 30) { tries++;
      const x = (rnd() * 2 - 1) * 175, z = (rnd() * 2 - 1) * 175, f = forestAt(x, z);
      const edge = f > 0.02 && f < 0.55, patch = noise(x * 0.035 - 12, z * 0.035 + 5) > 0.35;
      if (!edge && !(patch && rnd() < 0.55) && rnd() > 0.06) continue;
      const h = getH(x, z), r = Math.hypot(x, z), pd = pathAt(x, z);
      if (h < 0.4 || h > 28 || r < 14 || r > 180 || slopeAt(x, z) > 0.42 || pd < 2.1 || blocked(x, z)) continue;
      const v = 0.82 + rnd() * 0.3, dry = rnd() < 0.25 ? 1 : 0;
      items.push({ x, y: h - 0.04, z, rot: rnd() * 6.283, s: 0.85 + rnd() * 0.6, sy: 0.7 + rnd() * 0.6, c: dry ? [v * 1.18, v * 1.05, v * 0.6] : [v * 0.95, v * 1.02, v * 0.78] });
    }
    const geos = [21, 22].map(clumpGeo);
    geos.forEach((g, k) => add(scatter(g, clumpMat, items.filter((_, i) => i % 2 === k))));
  }
  // Reeds along the lake shores
  { const rnd = mulberry32(2303), items = [];
    for (const L of LAKES) {
      const spots = Math.round(L.r * 2.2 * mult);
      for (let k = 0; k < spots * 6; k++) {
        if (items.length > 900) break;
        const a = rnd() * 6.283, d = L.r * (0.25 + rnd() * 0.85), sx = L.x + Math.cos(a) * d, sz = L.z + Math.sin(a) * d, sh = getH(sx, sz);
        if (sh < -0.7 || sh > 0.25) continue;
        const n = 2 + Math.floor(rnd() * 5);
        for (let j = 0; j < n; j++) {
          const x = sx + (rnd() - 0.5) * 2.4, z = sz + (rnd() - 0.5) * 2.4, h = getH(x, z);
          if (h < -0.8 || h > 0.4 || pathAt(x, z) < 2.5) continue;
          const v = 0.85 + rnd() * 0.3;
          items.push({ x, y: Math.min(h, 0) - 0.05, z, rot: rnd() * 6.283, s: 0.7 + rnd() * 0.5, c: [v, v * 1.02, v * 0.85] });
        }
        k += 5;
      }
    }
    add(scatter(reedGeo(31), reedMat, items));
  }
  // Lily pads with a few pink blossoms
  { const rnd = mulberry32(2404), pads = [], flowers = [];
    for (const L of LAKES) {
      const N = Math.round(L.r * 4 * mult);
      for (let k = 0, tries = 0; k < N && tries < N * 20; tries++) {
        const a = rnd() * 6.283, d = L.r * Math.sqrt(rnd()) * 0.85, cx = L.x + Math.cos(a) * d, cz = L.z + Math.sin(a) * d, h = getH(cx, cz);
        if (h > -0.45 || h < -3.2) continue;
        const n = 1 + Math.floor(rnd() * 5);
        for (let j = 0; j < n; j++, k++) {
          const x = cx + (rnd() - 0.5) * 2.2, z = cz + (rnd() - 0.5) * 2.2;
          if (getH(x, z) > -0.35) continue;
          const v = 0.8 + rnd() * 0.35, s = 0.6 + rnd() * 0.7;
          pads.push({ x, y: 0.025 + rnd() * 0.01, z, rot: rnd() * 6.283, s, c: [v * 0.95, v, v * 0.8] });
          if (rnd() < 0.12) flowers.push({ x: x + 0.05, y: 0.07, z: z + 0.03, rot: rnd() * 6.283, s: 1.3 + rnd() * 0.5, c: rnd() < 0.7 ? [1.0, 0.62, 0.78] : [1.0, 0.97, 0.9] });
        }
      }
    }
    const padGeo = new THREE.CircleGeometry(0.34, 16, 0.22, Math.PI * 2 - 0.44).rotateX(-Math.PI / 2);
    const padMat = new THREE.MeshStandardMaterial({ color: 0x4f8a34, roughness: 0.42, metalness: 0 });
    add(scatter(padGeo, padMat, pads));
    const lotus = blossomGeo(0.1);
    add(scatter(lotus, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.6, side: THREE.DoubleSide, emissive: 0x402030, emissiveIntensity: 0.3 }), flowers));
  }
  // Stumps and fallen logs in the woods
  { const rnd = mulberry32(2505), stumps = [], logs = [];
    for (let tries = 0; tries < 9000 && (stumps.length < 70 || logs.length < 45); tries++) {
      const x = (rnd() * 2 - 1) * 170, z = (rnd() * 2 - 1) * 170, f = forestAt(x, z), h = getH(x, z);
      if (f < 0.12 || h < 1 || h > 28 || slopeAt(x, z) > 0.3 || pathAt(x, z) < 4 || blocked(x, z) || Math.hypot(x, z) < 24) continue;
      const v = 0.8 + rnd() * 0.3;
      if (rnd() < 0.6 && stumps.length < 70) { const s = 0.8 + rnd() * 0.6; stumps.push({ x, y: h - 0.1, z, rot: rnd() * 6.283, s, c: [v, v, v] }); ctx.colliders.push({ x, z, r: 0.4 * s }); }
      else if (logs.length < 45) {
        const rot = rnd() * 6.283, dx = Math.cos(rot) * 1.6, dz = -Math.sin(rot) * 1.6;
        const h1 = getH(x - dx, z - dz), h2 = getH(x + dx, z + dz);
        if (Math.abs(h1 - h2) > 0.8) continue;
        logs.push({ x, y: (h1 + h2) / 2 + 0.12, z, rot, tz: Math.atan2(h2 - h1, 3.2), s: 0.8 + rnd() * 0.4, c: [v, v * 0.97, v * 0.92] });
      }
    }
    const fixUV = (g, rep, len) => { const uv = g.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * rep, uv.getY(i) * len); return g; };
    const stumpGeo = fixUV(new THREE.CylinderGeometry(0.34, 0.5, 0.7, 12, 1), 2, 0.6).translate(0, 0.3, 0);
    const logGeo = fixUV(new THREE.CylinderGeometry(0.28, 0.33, 3.4, 12, 1, false), 2, 3).rotateZ(Math.PI / 2);
    const bark = new THREE.MeshStandardMaterial({ map: ctx.TEX.bark.a, normalMap: ctx.TEX.bark.n, normalScale: new THREE.Vector2(1.5, 1.5), roughness: 0.95, color: 0xd8d0c4 });
    add(scatter(stumpGeo, bark, stumps, { cast: true }));
    add(scatter(logGeo, bark, logs, { cast: true }));
  }

  let density = 1;
  return {
    meshes: all,
    setQuality(q){ density = q.plants; for (const m of all) m.count = Math.max(0, Math.floor(m.userData.n * density)); ctx.shared.uPlantFar.value = q.plantFar; ctx.shared.uWind.value = q.wind ? 1 : 0; },
    update(cam){
      const far = ctx.shared.uPlantFar.value + CHUNK * 0.75;
      for (const m of all) m.visible = density > 0 && Math.hypot(m.userData.cx - cam.x, m.userData.cz - cam.z) < far;
    },
  };
}

/* =========================================================
   Painted cumulus clouds: camera-facing cards, lit from above, silver edges toward the sun
   ========================================================= */
export function buildCloudCards(ctx){
  const { scene, sunDir, isTouch, MAXANISO, SKY } = ctx;
  const tex = toTex(makeCloudAtlas(isTouch ? 1024 : 2048), MAXANISO, false);
  const mat = new THREE.ShaderMaterial({
    uniforms: { map: { value: tex }, uSun: { value: sunDir }, uLit: { value: new THREE.Color(1.08, 1.04, 0.98) }, uShade: { value: new THREE.Color(0.6, 0.68, 0.82) }, uHaze: { value: SKY.hor } },
    vertexShader: `varying vec2 vUv; varying vec3 vDir;
      void main(){ vUv = uv;
        vec3 c = (modelMatrix * vec4(0.0, 0.0, 0.0, 1.0)).xyz;
        vec3 right = normalize(vec3(viewMatrix[0][0], 0.0, viewMatrix[2][0]));
        vec3 wp = c + right * position.x * length(modelMatrix[0].xyz) + vec3(0.0, 1.0, 0.0) * position.y * length(modelMatrix[1].xyz);
        vDir = normalize(wp - cameraPosition);
        gl_Position = projectionMatrix * viewMatrix * vec4(wp, 1.0); }`,
    fragmentShader: `uniform sampler2D map; uniform vec3 uSun, uLit, uShade, uHaze; varying vec2 vUv; varying vec3 vDir;
      void main(){ vec4 t = texture2D(map, vUv); if (t.a < 0.01) discard;
        float s = max(dot(vDir, uSun), 0.0);
        vec3 col = mix(uShade, uLit, t.r);
        col += vec3(1.0, 0.86, 0.66) * pow(s, 5.0) * (1.0 - t.a * 0.7) * 0.9;
        col = mix(col, uHaze, smoothstep(0.22, 0.02, vDir.y) * 0.55);
        gl_FragColor = vec4(col, t.a * 0.96); }`,
    transparent: true, depthWrite: false, fog: false, side: THREE.DoubleSide,
  });
  // one card per atlas cell, plus a mirrored copy for variety
  const geos = [0, 1, 2, 3, 4, 5, 6, 7].map(k => {
    const cell = k % 4, flip = k > 3, g = new THREE.PlaneGeometry(1, 1), uv = g.attributes.uv, u0 = (cell % 2) * 0.5, v0 = 0.5 - Math.floor(cell / 2) * 0.5;
    for (let i = 0; i < uv.count; i++) uv.setXY(i, u0 + (flip ? 1 - uv.getX(i) : uv.getX(i)) * 0.5, v0 + uv.getY(i) * 0.5);
    return g;
  });
  const group = new THREE.Group(), rnd = mulberry32(11), N = isTouch ? 16 : 26;
  for (let i = 0; i < N; i++) {
    const a = i / N * 6.283 + rnd() * 0.4, r = 520 + rnd() * 220, cell = Math.floor(rnd() * 4), w = (cell === 3 ? 420 : 260) + rnd() * 180;
    const m = new THREE.Mesh(geos[cell + (rnd() < 0.5 ? 4 : 0)], mat);
    m.position.set(Math.cos(a) * r, 210 + rnd() * 110 + (cell === 3 ? 50 : 0), Math.sin(a) * r);
    m.scale.set(w, w * 0.5, 1);
    m.renderOrder = -5;
    group.add(m);
  }
  scene.add(group);
  return group;
}
