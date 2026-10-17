/* =========================================================
   Figuren mit Skelett und Animationen. Zwei Figurenarten („Rigs“):
   - ual:    Quaternius-Figuren mit echten Proportionen (CC0), Animationen aus der
             Universal Animation Library (assets/characters/quaternius/).
   - kaykit: KayKit-Abenteurer (Kay Lousberg, CC0), Skelett „Rig_Medium“
             (assets/characters/kaykit/). Bleibt für spätere Gegner und NPCs.
   Alle Figuren einer Art teilen dasselbe Skelett, deshalb passen alle
   Animationen dieser Art auf jede ihrer Figuren.
   ========================================================= */
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { clone as cloneSkinned } from 'three/addons/utils/SkeletonUtils.js';

const ASSETS = new URL('../assets/characters/', import.meta.url).href;
const ITEMS = ASSETS + 'kaykit/zubehoer/';
// Eigene Waffen (tools/blender/waffen.py) liegen in eigene/waffen/, KayKit-Zubehör in kaykit/zubehoer/
const itemUrl = n => n.startsWith('eigene/') ? ASSETS + n + '.glb' : ITEMS + n + '.gltf';

/* Pro Figurenart: Ordner, Animationspakete, Handknochen, Knochen von Hüfte und Beinen
   (für Angriffe im Laufen) und Übersetzung der allgemeinen Bewegungsnamen. */
const RIGS = {
  ual: {
    base: ASSETS + 'quaternius/',
    packs: ['ual'],
    hand: { r: 'hand_r', l: 'hand_l' },
    // Lage der Waffe in der Hand: Position (m), Drehung (Grad), Größe
    // shift: Waffe entlang ihres Griffs verschieben (Anteil ihrer Länge), z. B. Stab in der Mitte greifen
    grip: { r: { pos: [0.03, 0.08, 0], rot: [90, 0, 0], scale: 0.5 }, l: { pos: [-0.03, 0.08, 0], rot: [90, 0, 0], scale: 0.5 } },
    itemGrip: {
      shield_badge_color: { pos: [-0.07, 0.06, 0], rot: [90, -90, 0] },
      staff: { rot: [135, 0, 0], shift: 0.42 },
      // eigene Waffen sind in echter Größe gebaut (Meter), Griff im Ursprung
      'eigene/waffen/schwert': { scale: 1 }, 'eigene/waffen/dolch': { scale: 1 }, 'eigene/waffen/axt': { scale: 1 },
      'eigene/waffen/bogen': { scale: 1 }, 'eigene/waffen/stab': { rot: [135, 0, 0], scale: 1 },
      'eigene/waffen/schild': { pos: [-0.07, 0.06, 0], rot: [90, -90, 0], scale: 1 },
    },
    lower: ['root', 'pelvis', 'thigh_l', 'calf_l', 'foot_l', 'ball_l', 'thigh_r', 'calf_r', 'foot_r', 'ball_r'],
    // speed: Tempo in m/s, bei dem die Animation mit normaler Geschwindigkeit läuft
    walk: { clip: 'Walk_Loop', speed: 1.2 }, jog: { clip: 'Jog_Fwd_Loop', speed: 3.2 }, run: { clip: 'Sprint_Loop', speed: 5.4 },
    names: {
      Idle_A: 'Idle_Loop', Idle_B: 'Idle_Loop', Walking_A: 'Walk_Loop', Running_A: 'Sprint_Loop', Jump_Idle: 'Jump_Loop',
      Hit_A: 'Hit_Chest', Dodge_Forward: 'Roll', Dodge_Backward: 'Roll', Death_A: 'Death01', Waving: 'Yes',
      Ranged_Magic_Shoot: 'Spell_Simple_Shoot', Ranged_Magic_Spellcasting: 'Spell_Simple_Shoot',
      Ranged_Magic_Raise: 'Spell_Simple_Shoot', Ranged_Magic_Summon: 'Spell_Simple_Shoot',
    },
  },
  kaykit: {
    base: ASSETS + 'kaykit/',
    packs: ['Rig_Medium_General', 'Rig_Medium_MovementBasic', 'Rig_Medium_MovementAdvanced', 'Rig_Medium_CombatMelee', 'Rig_Medium_CombatRanged', 'Rig_Medium_Simulation'],
    hand: { r: 'handslot.r', l: 'handslot.l' },
    grip: null, itemGrip: {},
    lower: ['root', 'hips', 'upperlegl', 'lowerlegl', 'footl', 'toesl', 'upperlegr', 'lowerlegr', 'footr', 'toesr'],
    walk: { clip: 'Walking_A', speed: 3 }, run: { clip: 'Running_A', speed: 7.6 },
    names: {},
  },
};
for (const r of Object.values(RIGS)) r.lower = new Set(r.lower);

/* Welche Figur, welche Waffen und welche Angriffe zu einer Klasse gehören.
   hide: Teile der Figur, die ausgeblendet werden (Kapuze, Bart, Haare).
   hand: 'r' = rechte Hand, 'l' = linke Hand. tip: wo Zauber und Geschosse starten. */
export const FIGURES = {
  // Alle Spielfiguren sind eigene Blender-Figuren (tools/blender/figuren/), Waffen aus tools/blender/waffen.py
  // Sternenweberin: blonde Magierin in Creme und Türkis mit Stab
  mage:      { rig: 'ual', file: 'eigene/sternenweberin.glb', hide: [], colors: {}, items: [['eigene/waffen/stab', 'r']], tip: 'r', idle: 'Idle_Loop', attack: ['Spell_Simple_Shoot', 'Spell_Simple_Shoot'] },
  // Klingenwächter: Krieger in Rot und Bronze mit Plattenrüstung, Schwert und Schild
  warrior:   { rig: 'ual', file: 'eigene/klingenwaechter.glb', hide: [], colors: {}, items: [['eigene/waffen/schwert', 'r'], ['eigene/waffen/schild', 'l']], tip: 'r', idle: 'Sword_Idle', attack: ['Sword_Regular_A', 'Sword_Regular_B'] },
  // Waldläufer: Grün und Leder, Kapuze, Köcher und Bogen
  ranger:    { rig: 'ual', file: 'eigene/waldlaeufer.glb', hide: [], colors: {}, items: [['eigene/waffen/bogen', 'l']], tip: 'l', idle: 'Idle_Loop', attack: ['Spell_Simple_Shoot', 'OverhandThrow'] },
  // Schattenklinge: Violett und Silber, Kapuze, Gesichtstuch und zwei Dolche
  rogue:     { rig: 'ual', file: 'eigene/schattenklinge.glb', hide: [], colors: {}, items: [['eigene/waffen/dolch', 'r'], ['eigene/waffen/dolch', 'l']], tip: 'r', idle: 'Sword_Idle', attack: ['Sword_Regular_C', 'Sword_Regular_B'] },
  // Bärenherz: Fell und Eisen, bärtig, mit Zweihandaxt
  barbarian: { rig: 'ual', file: 'eigene/baerenherz.glb', hide: [], colors: {}, items: [['eigene/waffen/axt', 'r']], tip: 'r', idle: 'Sword_Idle', attack: ['Sword_Heavy_Combo', 'Sword_Attack'] },
  // Mira, die Bäuerin: Leinen und Grün
  mira:      { rig: 'ual', file: 'eigene/mira.glb', hide: [], colors: {}, items: [], tip: 'r', idle: 'Idle_FoldArms_Loop', greet: 'Idle_Talking_Loop', attack: [] },
};
// Zauber ohne Waffenschlag (Fertigkeiten 3–5: Blütenregen, Heilquelle, Windstoß)
const SPELL = { 0: 'Ranged_Magic_Shoot', 1: 'Ranged_Magic_Shoot', 2: 'Ranged_Magic_Spellcasting', 3: 'Ranged_Magic_Raise', 4: 'Ranged_Magic_Summon' };

const loader = new GLTFLoader();
const cache = new Map();
function load(url){
  if (!cache.has(url)) cache.set(url, loader.loadAsync(url));
  return cache.get(url);
}
const findBone = (root, name) => root.getObjectByName(name) || root.getObjectByName(name.replace(/\./g, ''));
// file: eigene Figur außerhalb des Figurenordners der Figurenart (z. B. 'eigene/sternenweberin.glb')
const modelUrl = def => def.file ? ASSETS + def.file : RIGS[def.rig].base + 'figuren/' + def.model + '.glb';

/* Lädt die Figuren der gewählten Klassen und alle benötigten Animationen. */
export async function loadFigures(keys, onProgress){
  const defs = keys.map(k => FIGURES[k]);
  const models = [...new Set(defs.map(modelUrl))];
  const items = [...new Set(defs.flatMap(d => d.items.map(i => i[0])))];
  const rigs = [...new Set(defs.map(d => d.rig))];
  const packs = rigs.flatMap(r => RIGS[r].packs.map(p => [r, RIGS[r].base + 'animationen/' + p + '.glb']));
  const urls = [...models, ...items.map(itemUrl), ...packs.map(p => p[1])];
  let done = 0;
  const res = await Promise.all(urls.map(u => load(u).then(g => { done++; if (onProgress) onProgress(done / urls.length); return g; })));
  const lib = { models: {}, items: {}, clips: {}, rest: {}, parts: {} };
  models.forEach((m, i) => { lib.models[m] = res[i]; });
  items.forEach((it, i) => { lib.items[it] = res[models.length + i]; });
  packs.forEach(([rig], i) => {
    const g = res[models.length + items.length + i];
    const clips = lib.clips[rig] = lib.clips[rig] || {};
    for (const c of g.animations) if (!/T-?Pose/i.test(c.name) && !clips[c.name]) clips[c.name] = c;
    const pelvis = g.scene.getObjectByName('pelvis');
    if (pelvis && !lib.rest[rig]) lib.rest[rig] = pelvis.position.clone();
  });
  return lib;
}

/* Eine spielbare Figur: Modell, Waffen, Animationsmischer und eine kleine Zustandssteuerung. */
export function createFigure(lib, key){
  const def = FIGURES[key];
  const rig = RIGS[def.rig];
  const root = cloneSkinned(lib.models[modelUrl(def)].scene);
  root.traverse(o => {
    if (!o.isMesh) return;
    o.castShadow = true; o.receiveShadow = true;
    if (o.isSkinnedMesh) o.frustumCulled = false; // Begrenzung stammt aus der Grundhaltung, Animationen ragen heraus
    if (def.hide && def.hide.includes(o.name)) o.visible = false;
    // Farbe einzelner Materialien (z. B. Haarfarbe); Material wird dafür kopiert
    const tint = def.colors && def.colors[o.material.name];
    if (tint !== undefined) { o.material = o.material.clone(); o.material.color.set(tint); }
  });
  // Unterschiedliche Beckenhöhe zwischen Animationsvorlage und Figur ausgleichen
  const pelvis = root.getObjectByName('pelvis'), rest = lib.rest[def.rig];
  const hipScale = pelvis && rest ? pelvis.position.length() / rest.length() : 1;
  const hand = { r: findBone(root, rig.hand.r), l: findBone(root, rig.hand.l) };
  let tip = null;
  for (const [name, side] of def.items) {
    const w = lib.items[name].scene.clone();
    w.traverse(o => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = false; } });
    let holder = w;
    if (rig.grip) {
      // Halterung, damit die Waffe in der Hand der Figur richtig liegt
      const g = { ...rig.grip[side], ...(rig.itemGrip[name] || {}), ...((def.grip || {})[name] || {}) };
      if (g.shift) { const b = new THREE.Box3().setFromObject(lib.items[name].scene); w.position.y = -g.shift * (b.max.y - b.min.y); }
      holder = new THREE.Group();
      holder.position.fromArray(g.pos);
      holder.rotation.set(...g.rot.map(THREE.MathUtils.degToRad));
      holder.scale.setScalar(g.scale);
      holder.add(w);
    }
    hand[side].add(holder);
    if (side === def.tip && !tip) {
      const box = new THREE.Box3().setFromObject(lib.items[name].scene);
      tip = new THREE.Object3D();
      tip.position.set(0, /bow|bogen/.test(name) ? (box.min.y + box.max.y) / 2 : box.max.y * 0.92, 0);
      w.add(tip);
    }
  }
  if (!tip) { tip = new THREE.Object3D(); tip.position.set(0, 0.1, 0); hand[def.tip].add(tip); }

  const group = new THREE.Group();
  group.add(root);

  const mixer = new THREE.AnimationMixer(root);
  const actions = {};
  // part: 'full' = ganzer Körper, 'lo' = Hüfte und Beine, 'up' = Oberkörper, Arme, Kopf
  const act = (name, part = 'full') => {
    name = rig.names[name] || name;
    const k = name + '|' + part;
    if (!actions[k]) { const c = clipPart(lib, def.rig, name, part, hipScale); if (!c) return null; actions[k] = mixer.clipAction(c); }
    return actions[k];
  };
  const FADE = 0.18;
  let lo = null, up = null, once = null, onceUpper = false, locked = false, wantBase = def.idle, wantSpeed = 1;

  function start(a, speed, from, fade, loop){
    a.reset(); a.setEffectiveWeight(1); a.timeScale = speed;
    if (loop) a.setLoop(THREE.LoopRepeat, Infinity); else { a.setLoop(THREE.LoopOnce, 1); a.clampWhenFinished = true; }
    a.play();
    if (from && from !== a) a.crossFadeFrom(from, fade, false);
    return a;
  }
  // Grundbewegung (Stehen, Gehen, Laufen, Springen). Beine wechseln sofort,
  // der Oberkörper erst, wenn ein laufender Angriff fertig ist.
  function setBase(name, speed = 1){
    if (!act(name)) return;
    wantBase = name; wantSpeed = speed;
    if (once && !onceUpper) return;
    const nlo = act(name, 'lo'), nup = act(name, 'up');
    if (nlo === lo) { lo.timeScale = speed; if (up === nup) up.timeScale = speed; return; }
    lo = start(nlo, speed, lo, FADE, true);
    if (!once) up = start(nup, speed, up, FADE, true);
  }
  // Einmalige Bewegung (Angriff, Ausweichen, Treffer). duration: gewünschte Dauer in Sekunden.
  // upper: nur Oberkörper, damit die Beine beim Laufen weiterlaufen.
  function play(name, { duration = 0, hold = false, upper = false } = {}){
    if (locked || !act(name)) return 0;
    if (once && !onceUpper) upper = false;
    const a = act(name, upper ? 'up' : 'full');
    const len = a.getClip().duration, speed = duration > 0 ? len / duration : 1;
    const fade = Math.min(FADE, (duration || len) * 0.3);
    if (upper) start(a, speed, once || up, fade, false);
    else { start(a, speed, once || up, fade, false); if (lo && lo !== a) lo.fadeOut(fade); }
    once = a; onceUpper = upper; locked = hold;
    return len / speed;
  }
  mixer.addEventListener('finished', e => {
    if (e.action !== once || locked) return;
    const wasUpper = onceUpper;
    once = null; onceUpper = false;
    const nlo = act(wantBase, 'lo'), nup = act(wantBase, 'up');
    if (!wasUpper) { lo = start(nlo, wantSpeed, null, FADE, true); lo.fadeIn(FADE); }
    up = start(nup, wantSpeed, e.action, FADE, true);
    if (lo && lo.getClip().duration === up.getClip().duration) up.time = lo.time; // Arme und Beine im Takt
  });

  return {
    group, root, tip, mixer, def, rig,
    setBase,
    play,
    // Fertigkeit i (0–4): 1 und 2 mit der Waffe, 3–5 als Zauber
    attack(i, duration, moving){ return play((i < 2 && def.attack[i]) || SPELL[i] || SPELL[2], { duration, upper: moving }); },
    die(){ play('Death_A', { hold: true }); },
    revive(){ locked = false; once = null; onceUpper = false; lo = up = null; mixer.stopAllAction(); setBase(def.idle); },
    get busy(){ return !!once; },
    update(dt){ mixer.update(dt); },
  };
}

/* Teilt eine Animation in Beine ('lo') und Oberkörper ('up'). hipScale passt die
   Beckenhöhe an die Größe der Figur an. */
function clipPart(lib, rigName, name, part, hipScale = 1){
  const c = (lib.clips[rigName] || {})[name];
  if (!c) return null;
  const hs = Math.round(hipScale * 1000) / 1000;
  const k = rigName + '|' + name + '|' + part + '|' + hs;
  if (!lib.parts[k]) {
    const lower = RIGS[rigName].lower;
    const bone = t => t.name.slice(0, t.name.lastIndexOf('.')).replace(/\./g, '');
    let tracks = part === 'full' ? c.tracks : c.tracks.filter(t => lower.has(bone(t)) === (part === 'lo'));
    if (hs !== 1) tracks = tracks.map(t => {
      if (!/\.position$/.test(t.name) || bone(t) !== 'pelvis') return t;
      const n = t.clone(); for (let i = 0; i < n.values.length; i++) n.values[i] *= hs; return n;
    });
    lib.parts[k] = new THREE.AnimationClip(k, c.duration, tracks);
  }
  return lib.parts[k];
}

/* Wählt die passende Grundbewegung aus Tempo und Bodenkontakt.
   Die Abspielgeschwindigkeit folgt dem Tempo, damit die Füße nicht rutschen. */
export function locomotion(fig, { speed = 0, air = false, idle } = {}){
  const r = fig.rig;
  if (air) fig.setBase('Jump_Idle');
  else if (speed > 4.2) fig.setBase(r.run.clip, Math.min(2.2, Math.max(0.8, speed / r.run.speed)));
  else if (r.jog && speed > 2) fig.setBase(r.jog.clip, Math.min(1.6, Math.max(0.7, speed / r.jog.speed)));
  else if (speed > 0.6) fig.setBase(r.walk.clip, Math.min(2, Math.max(0.7, speed / r.walk.speed)));
  else fig.setBase(idle || fig.def.idle);
}
