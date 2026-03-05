const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");
const leftHud = document.getElementById("leftHud");

const W = canvas.width;
const H = canvas.height;
const GROUND_Y = H - 80;
const GRAVITY = 0.6;
const SPEED = 4.4;
const JUMP = -12.5;
const WORLD_END = 3200;

const keys = {
  left: false,
  right: false,
  jump: false,
};

const touchMap = {
  leftBtn: "left",
  rightBtn: "right",
  jumpBtn: "jump",
};

for (const [id, key] of Object.entries(touchMap)) {
  const btn = document.getElementById(id);
  const setDown = (v) => {
    keys[key] = v;
    btn.classList.toggle("active", v);
  };
  btn.addEventListener("touchstart", (e) => { e.preventDefault(); setDown(true); }, { passive: false });
  btn.addEventListener("touchend", () => setDown(false));
  btn.addEventListener("mousedown", () => setDown(true));
  btn.addEventListener("mouseup", () => setDown(false));
  btn.addEventListener("mouseleave", () => setDown(false));
}

document.addEventListener("keydown", (e) => {
  const k = e.key.toLowerCase();
  if (k === "arrowleft" || k === "a") keys.left = true;
  if (k === "arrowright" || k === "d") keys.right = true;
  if (k === "arrowup" || k === "w" || k === " ") keys.jump = true;
  if (k === "r") reset();
});

document.addEventListener("keyup", (e) => {
  const k = e.key.toLowerCase();
  if (k === "arrowleft" || k === "a") keys.left = false;
  if (k === "arrowright" || k === "d") keys.right = false;
  if (k === "arrowup" || k === "w" || k === " ") keys.jump = false;
});

function makePlatforms() {
  return [
    { x: -400, y: GROUND_Y, w: 5200, h: 120 },
    { x: 280, y: GROUND_Y - 90, w: 130, h: 20 },
    { x: 470, y: GROUND_Y - 155, w: 110, h: 20 },
    { x: 700, y: GROUND_Y - 220, w: 110, h: 20 },
    { x: 980, y: GROUND_Y - 70, w: 170, h: 20 },
    { x: 1290, y: GROUND_Y - 120, w: 160, h: 20 },
    { x: 1620, y: GROUND_Y - 175, w: 120, h: 20 },
    { x: 1940, y: GROUND_Y - 95, w: 180, h: 20 },
    { x: 2350, y: GROUND_Y - 165, w: 160, h: 20 },
    { x: 2700, y: GROUND_Y - 230, w: 130, h: 20 },
  ];
}

function makeEnemies() {
  return [
    { x: 860, y: GROUND_Y - 36, w: 36, h: 36, vx: 1.5 },
    { x: 1760, y: GROUND_Y - 36, w: 36, h: 36, vx: 2.0 },
    { x: 2440, y: GROUND_Y - 36, w: 36, h: 36, vx: 1.8 },
  ];
}

function makeCoins() {
  return [
    { x: 320, y: GROUND_Y - 120, w: 16, h: 16 },
    { x: 505, y: GROUND_Y - 185, w: 16, h: 16 },
    { x: 730, y: GROUND_Y - 250, w: 16, h: 16 },
    { x: 1320, y: GROUND_Y - 150, w: 16, h: 16 },
    { x: 1660, y: GROUND_Y - 205, w: 16, h: 16 },
    { x: 2380, y: GROUND_Y - 195, w: 16, h: 16 },
  ];
}

function overlap(a, b) {
  return a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
}

function removePink(img, tolerance = 70) {
  const off = document.createElement("canvas");
  off.width = img.width;
  off.height = img.height;
  const c = off.getContext("2d");
  c.drawImage(img, 0, 0);
  const frame = c.getImageData(0, 0, off.width, off.height);
  const d = frame.data;

  for (let i = 0; i < d.length; i += 4) {
    const r = d[i];
    const g = d[i + 1];
    const b = d[i + 2];
    const isPink = Math.abs(r - 255) <= tolerance && g <= tolerance && Math.abs(b - 255) <= tolerance;
    if (isPink) d[i + 3] = 0;
  }
  c.putImageData(frame, 0, 0);
  return off;
}

function loadImage(src, fallbackPainter) {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => resolve({ ok: true, img });
    img.onerror = () => {
      const off = document.createElement("canvas");
      off.width = 256;
      off.height = 256;
      const c = off.getContext("2d");
      fallbackPainter(c, off.width, off.height);
      resolve({ ok: false, img: off });
    };
    img.src = src;
  });
}

let player, cameraX, platforms, enemies, coins, score;
let backgroundImg, spriteImg, bgStatus, spStatus;

function reset() {
  player = { x: 70, y: GROUND_Y - 150, w: 36, h: 48, vx: 0, vy: 0, onGround: false, left: false };
  cameraX = 0;
  platforms = makePlatforms();
  enemies = makeEnemies();
  coins = makeCoins();
  score = 0;
}

function moveWithCollisions(entity, list, axis) {
  for (const p of list) {
    if (!overlap(entity, p)) continue;
    if (axis === "x") {
      if (entity.vx > 0) entity.x = p.x - entity.w;
      else if (entity.vx < 0) entity.x = p.x + p.w;
      entity.vx = 0;
    } else {
      if (entity.vy > 0) {
        entity.y = p.y - entity.h;
        entity.vy = 0;
        entity.onGround = true;
      } else if (entity.vy < 0) {
        entity.y = p.y + p.h;
        entity.vy = 0;
      }
    }
  }
}

function update() {
  let move = 0;
  if (keys.left) move -= 1;
  if (keys.right) move += 1;

  player.vx = move * SPEED;
  if (move < 0) player.left = true;
  if (move > 0) player.left = false;

  if (keys.jump && player.onGround) {
    player.vy = JUMP;
    player.onGround = false;
  }

  player.vy += GRAVITY;
  if (player.vy > 14) player.vy = 14;

  player.x += player.vx;
  moveWithCollisions(player, platforms, "x");

  player.y += player.vy;
  player.onGround = false;
  moveWithCollisions(player, platforms, "y");

  for (const e of enemies) {
    e.x += e.vx;
    let bounced = false;
    for (const p of platforms) {
      if (!overlap(e, p)) continue;
      if (e.vx > 0) e.x = p.x - e.w;
      else e.x = p.x + p.w;
      e.vx *= -1;
      bounced = true;
      break;
    }
    if (!bounced && (e.x < 0 || e.x > WORLD_END - e.w)) e.vx *= -1;

    if (overlap(player, e)) {
      player.x = 70;
      player.y = GROUND_Y - 150;
      player.vx = 0;
      player.vy = 0;
    }
  }

  coins = coins.filter((c) => {
    if (overlap(player, c)) {
      score += 1;
      return false;
    }
    return true;
  });

  if (player.y > H + 220) {
    player.x = 70;
    player.y = GROUND_Y - 150;
    player.vx = 0;
    player.vy = 0;
  }

  cameraX = Math.max(0, Math.min(player.x + player.w / 2 - W / 3, WORLD_END - W));
}

function drawBackground() {
  const bgW = backgroundImg.width;
  const bgH = backgroundImg.height;
  const scale = H / bgH;
  const drawW = bgW * scale;
  const parallax = (cameraX * 0.35) % drawW;
  let x = -parallax;
  while (x < W) {
    ctx.drawImage(backgroundImg, x, 0, drawW, H);
    x += drawW;
  }
}

function draw() {
  drawBackground();

  for (const p of platforms) {
    const x = p.x - cameraX;
    ctx.fillStyle = "#b27034";
    ctx.fillRect(x, p.y, p.w, p.h);
    ctx.strokeStyle = "#744922";
    ctx.lineWidth = 2;
    ctx.strokeRect(x, p.y, p.w, p.h);
  }

  for (const c of coins) {
    const x = c.x - cameraX;
    ctx.fillStyle = "#f5cc12";
    ctx.beginPath();
    ctx.ellipse(x + c.w / 2, c.y + c.h / 2, c.w / 2, c.h / 2, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = "#af8208";
    ctx.stroke();
  }

  for (const e of enemies) {
    const x = e.x - cameraX;
    ctx.fillStyle = "#754c2a";
    ctx.beginPath();
    ctx.ellipse(x + e.w / 2, e.y + e.h / 2, e.w / 2, e.h / 2, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "#28190a";
    ctx.fillRect(x + 6, e.y + 22, 8, 4);
    ctx.fillRect(x + 22, e.y + 22, 8, 4);
  }

  const px = player.x - cameraX;
  ctx.save();
  if (player.left) {
    ctx.translate(px + player.w / 2, player.y + player.h / 2);
    ctx.scale(-1, 1);
    ctx.drawImage(spriteImg, -player.w / 2, -player.h / 2, player.w, player.h);
  } else {
    ctx.drawImage(spriteImg, px, player.y, player.w, player.h);
  }
  ctx.restore();

  if (coins.length === 0) {
    ctx.fillStyle = "#0a5b1f";
    ctx.font = "bold 28px Trebuchet MS";
    ctx.fillText("Level Clear!", W - 185, 38);
  }

  leftHud.textContent = `Coins: ${score} | ${bgStatus} | ${spStatus}`;
}

async function start() {
  const bg = await loadImage("asset/background.png", (c, w, h) => {
    c.fillStyle = "#75c1ff";
    c.fillRect(0, 0, w, h);
    c.fillStyle = "#fff";
    for (let i = 0; i < 8; i++) c.beginPath(), c.arc(20 + i * 30, 40 + (i % 2) * 8, 12, 0, Math.PI * 2), c.fill();
  });

  const sp = await loadImage("asset/sprite.png", (c, w, h) => {
    c.clearRect(0, 0, w, h);
    c.fillStyle = "#cd2a2a";
    c.fillRect(90, 70, 80, 100);
    c.fillStyle = "#18188c";
    c.fillRect(85, 130, 90, 85);
  });

  backgroundImg = bg.img;
  spriteImg = removePink(sp.img);
  bgStatus = bg.ok ? "background.png" : "fallback background";
  spStatus = sp.ok ? "sprite.png pink removed" : "fallback sprite";

  reset();

  const tick = () => {
    update();
    draw();
    requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}

start();
