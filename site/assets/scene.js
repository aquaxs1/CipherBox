/*
 * CipherBox — a glass vault.
 *
 * A few documents float inside. Click or tap the vault and it locks: the text
 * on the pages turns into cipher, the pages pull together, the shackle closes
 * and the two rings of ciphertext light up. Click again and it opens.
 * Left alone, it locks and unlocks by itself every few seconds.
 */
export default function scene(stage) {
  const { THREE, frame } = stage;
  stage.lights();
  stage.environment();

  const root = new THREE.Group();
  frame.add(root);
  root.add(stage.halo(stage.accent, 8, 0.32));

  /* ------------------------------------------------------------ vault */

  const SIZE = 2.5;
  const box = new THREE.BoxGeometry(SIZE, SIZE, SIZE);
  const glass = new THREE.Mesh(box, stage.mat.glass(stage.accent, { opacity: 0.09 }));
  const edges = stage.edges(box, stage.accentHi, 0.85);
  root.add(glass, edges);

  // Corner brackets, so the cube reads as a made thing and not a wireframe.
  const bracket = new THREE.BoxGeometry(0.34, 0.05, 0.05);
  const bracketMat = stage.mat.metal(stage.accentHi, { emissive: stage.accent, emissiveIntensity: 0.6 });
  for (const sx of [-1, 1]) {
    for (const sy of [-1, 1]) {
      for (const sz of [-1, 1]) {
        const corner = new THREE.Vector3(sx, sy, sz).multiplyScalar(SIZE / 2);
        for (const axis of ['x', 'y', 'z']) {
          const bar = new THREE.Mesh(bracket, bracketMat);
          if (axis === 'y') bar.rotation.z = Math.PI / 2;
          if (axis === 'z') bar.rotation.y = Math.PI / 2;
          bar.position.copy(corner);
          bar.position[axis] -= Math.sign(corner[axis]) * 0.17;
          root.add(bar);
        }
      }
    }
  }

  /* -------------------------------------------------------- documents */

  const hex = '0123456789ABCDEF';
  const pageGeometry = stage.slab(1.02, 1.34, 0.035, 0.07);
  const pages = [];

  const plain = (g, w, h) => {
    g.fillStyle = '#1b2440';
    g.fillRect(w * 0.12, h * 0.1, w * 0.42, h * 0.05);
    g.fillStyle = '#8a94b4';
    for (let i = 0; i < 9; i += 1) {
      g.fillRect(w * 0.12, h * (0.22 + i * 0.075), w * (0.46 + ((i * 37) % 30) / 100), h * 0.028);
    }
  };
  const cipher = (g, w, h) => {
    g.fillStyle = `#${stage.accent.getHexString()}`;
    g.font = stage.font.mono(Math.round(h * 0.062));
    g.textBaseline = 'top';
    for (let row = 0; row < 11; row += 1) {
      let line = '';
      for (let i = 0; i < 12; i += 1) line += hex[(row * 7 + i * 13 + ((row * i) % 5)) % 16] + (i % 2 ? ' ' : '');
      g.fillText(line, w * 0.1, h * (0.09 + row * 0.078));
    }
  };

  for (let i = 0; i < 5; i += 1) {
    const page = new THREE.Group();
    const paper = new THREE.Mesh(pageGeometry, stage.mat.solid(0xeef2ff, { roughness: 0.7 }));
    const readable = stage.plate(1.02, 1.34, plain);
    const locked = stage.plate(1.02, 1.34, cipher);
    readable.position.z = 0.02;
    locked.position.z = 0.021;
    locked.material.opacity = 0;
    page.add(paper, readable, locked);
    root.add(page);
    pages.push({ page, paper, readable, locked, seed: i * 1.7 + 0.3 });
  }

  /* -------------------------------------------------------------- lock */

  const lock = new THREE.Group();
  lock.position.set(0, -0.05, SIZE / 2 + 0.02);
  const body = new THREE.Mesh(stage.slab(0.62, 0.5, 0.16, 0.1), stage.mat.metal(0xdfe6ff, { roughness: 0.3 }));
  const shackle = new THREE.Mesh(new THREE.TorusGeometry(0.19, 0.045, 14, 32, Math.PI), stage.mat.metal(0xdfe6ff, { roughness: 0.25 }));
  shackle.position.set(0, 0.25, 0);
  const keyhole = new THREE.Mesh(new THREE.CircleGeometry(0.07, 24), new THREE.MeshBasicMaterial({ color: 0x0a1026 }));
  keyhole.position.set(0, 0.04, 0.085);
  const slot = new THREE.Mesh(new THREE.PlaneGeometry(0.05, 0.16), new THREE.MeshBasicMaterial({ color: 0x0a1026 }));
  slot.position.set(0, -0.06, 0.085);
  lock.add(body, shackle, keyhole, slot);
  root.add(lock);

  /* ------------------------------------------------------------- rings */

  const band = () => {
    const c = document.createElement('canvas');
    c.width = 2048;
    c.height = 64;
    const g = c.getContext('2d');
    const draw = () => {
      g.clearRect(0, 0, c.width, c.height);
      g.fillStyle = '#fff';
      g.font = stage.font.mono(34);
      g.textBaseline = 'middle';
      let x = 0;
      let n = 0;
      while (x < c.width) {
        const word = hex[(n * 5) % 16] + hex[(n * 11 + 3) % 16];
        g.globalAlpha = 0.35 + ((n * 7) % 10) / 15;
        g.fillText(word, x, 34);
        x += 62;
        n += 1;
      }
    };
    draw();
    const texture = new THREE.CanvasTexture(c);
    texture.wrapS = THREE.RepeatWrapping;
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(() => {
        draw();
        texture.needsUpdate = true;
      });
    }
    return texture;
  };

  const rings = [];
  for (const [radius, tilt, speed] of [
    [2.55, 0.42, 0.22],
    [2.95, -0.3, -0.16],
  ]) {
    const ring = new THREE.Mesh(
      new THREE.CylinderGeometry(radius, radius, 0.26, 96, 1, true),
      new THREE.MeshBasicMaterial({
        map: band(),
        color: stage.accentHi,
        transparent: true,
        opacity: 0.3,
        side: THREE.DoubleSide,
        blending: THREE.AdditiveBlending,
        depthWrite: false,
      }),
    );
    const holder = new THREE.Group();
    holder.rotation.x = tilt;
    holder.rotation.z = tilt * 0.6;
    holder.add(ring);
    root.add(holder);
    rings.push({ ring, speed });
  }

  stage.dust({ count: 220, radius: 6.5, color: stage.accentHi, opacity: 0.55 });

  /* --------------------------------------------------------- behaviour */

  let target = 0;
  let amount = 0;
  let touched = -100;

  stage.onClick(() => {
    target = target ? 0 : 1;
    touched = stage.time;
  });

  stage.onFrame((time, delta) => {
    // Nobody clicked for a while: run the demonstration.
    if (time - touched > 9) target = Math.floor(time / 4.2) % 2;

    amount += (target - amount) * Math.min(1, delta * 3.2);
    const eased = amount * amount * (3 - 2 * amount);

    root.rotation.y = 0.6 + time * 0.14 + stage.yaw;
    root.rotation.x = 0.26 + stage.pitch + Math.sin(time * 0.5) * 0.03;
    root.position.y = Math.sin(time * 0.8) * 0.06;

    pages.forEach((p, i) => {
      const k = i - 2;
      // Open: fanned out and drifting. Locked: one tight stack.
      const openX = k * 0.36;
      const openZ = k * 0.3 + Math.sin(time * 0.7 + p.seed) * 0.06;
      const openY = Math.sin(time * 0.9 + p.seed) * 0.1;
      p.page.position.set(openX * (1 - eased), openY * (1 - eased), openZ * (1 - eased) + k * 0.06 * eased);
      p.page.rotation.y = (k * -0.16 + Math.sin(time * 0.6 + p.seed) * 0.05) * (1 - eased);
      p.page.rotation.z = Math.sin(time * 0.5 + p.seed) * 0.05 * (1 - eased);
      p.page.scale.setScalar(1 - eased * 0.12);
      p.readable.material.opacity = 1 - eased;
      p.locked.material.opacity = eased;
      p.paper.material.color.setRGB(0.93 - eased * 0.82, 0.95 - eased * 0.8, 1 - eased * 0.68);
    });

    shackle.position.y = 0.25 + (1 - eased) * 0.14;
    shackle.rotation.y = (1 - eased) * 0.9;
    edges.material.opacity = 0.45 + eased * 0.5;
    glass.material.opacity = 0.06 + eased * 0.1;
    for (const r of rings) {
      r.ring.rotation.y = time * r.speed * (0.6 + eased * 1.6);
      r.ring.material.opacity = 0.14 + eased * 0.5;
    }
  });
}
