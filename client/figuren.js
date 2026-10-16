/* =========================================================
   Figuren: KayKit-Abenteurer (Kay Lousberg, CC0) mit Animationen.
   Alle Figuren nutzen das Skelett „Rig_Medium“, deshalb passen alle
   Animationen aus assets/characters/kaykit/animationen/ auf jede Figur.
   ========================================================= */
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { clone as cloneSkinned } from 'three/addons/utils/SkeletonUtils.js';

const BASE = new URL('../assets/characters/kaykit/', import.meta.url).href;

// Nur die Animationspakete, die das Spiel wirklich braucht
const ANIM_PACKS = ['Rig_Medium_General', 'Rig_Medium_MovementBasic', 'Rig_Medium_MovementAdvanced', 'Rig_Medium_CombatMelee', 'Rig_Medium_CombatRanged', 'Rig_Medium_Simulation'];

/* Welche Figur, welche Waffen und welche Angriffe zu einer Klasse gehören.
   hand: 'r' = rechte Hand, 'l' = linke Hand. tip: wo Zauber und Geschosse starten. */
export const FIGURES = {
  mage:      { model: 'Mage', items: [['staff', 'r']], tip: 'r', idle: 'Idle_A', attack: ['Ranged_Magic_Shoot', 'Ranged_Magic_Spellcasting'] },
  warrior:   { model: 'Knight', items: [['sword_1handed', 'r'], ['shield_badge_color', 'l']], tip: 'r', idle: 'Idle_A', attack: ['Melee_1H_Attack_Chop', 'Melee_1H_Attack_Slice_Diagonal'] },
  ranger:    { model: 'Ranger', items: [['bow_withString', 'l']], tip: 'l', idle: 'Ranged_Bow_Idle', attack: ['Ranged_Bow_Release', 'Ranged_Bow_Release_Up'] },
  rogue:     { model: 'Rogue_Hooded', items: [['dagger', 'r'], ['dagger', 'l']], tip: 'r', idle: 'Idle_A', attack: ['Melee_Dualwield_Attack_Stab', 'Melee_Dualwield_Attack_Slice'] },
  barbarian: { model: 'Barbarian', items: [['axe_2handed', 'r']], tip: 'r', idle: 'Melee_2H_Idle', attack: ['Melee_2H_Attack_Chop', 'Melee_2H_Attack_Slice'] },
  // Mira, die Bäuerin: Schurkin ohne Kapuze und Umhang
  mira:      { model: 'Rogue', items: [], hide: ['Rogue_Cape'], tip: 'r', idle: 'Idle_B', attack: [] },
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

/* Lädt die Figuren der gewählten Klasse plus Mira und alle benötigten Animationen. */
export async function loadFigures(keys, onProgress){
  const models = [...new Set(keys.map(k => FIGURES[k].model))];
  const items = [...new Set(keys.flatMap(k => FIGURES[k].items.map(i => i[0])))];
  const urls = [
    ...models.map(m => BASE + 'figuren/' + m + '.glb'),
    ...items.map(i => BASE + 'zubehoer/' + i + '.gltf'),
    ...ANIM_PACKS.map(a => BASE + 'animationen/' + a + '.glb'),
  ];
  let done = 0;
  const res = await Promise.all(urls.map(u => load(u).then(g => { done++; if (onProgress) onProgress(done / urls.length); return g; })));
  const lib = { models: {}, items: {}, clips: {} };
  models.forEach((m, i) => { lib.models[m] = res[i]; });
  items.forEach((it, i) => { lib.items[it] = res[models.length + i]; });
  for (const g of res.slice(models.length + items.length))
    for (const c of g.animations) if (c.name !== 'T-Pose' && !lib.clips[c.name]) lib.clips[c.name] = c;
  return lib;
}

/* Eine spielbare Figur: Modell, Waffen, Animationsmischer und eine kleine Zustandssteuerung. */
export function createFigure(lib, key){
  const def = FIGURES[key];
  const root = cloneSkinned(lib.models[def.model].scene);
  root.traverse(o => {
    if (!o.isMesh) return;
    o.castShadow = true; o.receiveShadow = true;
    if (o.isSkinnedMesh) o.frustumCulled = false; // Begrenzung stammt aus der Grundhaltung, Animationen ragen heraus
    if (def.hide && def.hide.includes(o.name)) o.visible = false;
  });
  const hand = { r: findBone(root, 'handslot.r'), l: findBone(root, 'handslot.l') };
  let tip = null;
  for (const [name, side] of def.items) {
    const w = lib.items[name].scene.clone();
    w.traverse(o => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = false; } });
    hand[side].add(w);
    if (side === def.tip && !tip) {
      const box = new THREE.Box3().setFromObject(lib.items[name].scene);
      tip = new THREE.Object3D();
      tip.position.set(0, name.startsWith('bow') ? (box.min.y + box.max.y) / 2 : box.max.y * 0.92, 0);
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
    const k = name + '|' + part;
    if (!actions[k]) { const c = clipPart(lib, name, part); if (!c) return null; actions[k] = mixer.clipAction(c); }
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
    group, root, tip, mixer, def,
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

// Knochen von Hüfte und Beinen (Namen ohne Punkte, so wie der Lader sie ablegt)
const LOWER = new Set(['root', 'hips', 'upperlegl', 'lowerlegl', 'footl', 'toesl', 'upperlegr', 'lowerlegr', 'footr', 'toesr']);
function clipPart(lib, name, part){
  const c = lib.clips[name];
  if (!c || part === 'full') return c || null;
  lib.parts = lib.parts || {};
  const k = name + '|' + part;
  if (!lib.parts[k]) {
    const tracks = c.tracks.filter(t => LOWER.has(t.name.slice(0, t.name.lastIndexOf('.')).replace(/\./g, '')) === (part === 'lo'));
    lib.parts[k] = new THREE.AnimationClip(k, c.duration, tracks);
  }
  return lib.parts[k];
}

/* Wählt die passende Grundbewegung aus Tempo und Bodenkontakt. */
export function locomotion(fig, { speed = 0, air = false, idle } = {}){
  if (air) fig.setBase('Jump_Idle');
  else if (speed > 4.2) fig.setBase('Running_A', Math.max(0.8, speed / 7.6));
  else if (speed > 0.6) fig.setBase('Walking_A', Math.max(0.7, speed / 3));
  else fig.setBase(idle || fig.def.idle);
}
