import math
import os
from pathlib import Path

import pygame

WIDTH, HEIGHT = 960, 540
FPS = 60
GRAVITY = 0.6
PLAYER_SPEED = 4.4
PLAYER_JUMP = -12.5
GROUND_Y = HEIGHT - 80

ASSET_DIR = Path(__file__).resolve().parent / "asset"
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}


class Platform:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)


class Enemy:
    def __init__(self, x, y, w=36, h=36, speed=1.5):
        self.rect = pygame.Rect(x, y, w, h)
        self.vx = speed

    def update(self, platforms):
        self.rect.x += int(self.vx)
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vx > 0:
                    self.rect.right = p.rect.left
                else:
                    self.rect.left = p.rect.right
                self.vx *= -1
                break


class Player:
    def __init__(self, x, y, sprite):
        self.rect = pygame.Rect(x, y, 36, 48)
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.facing_left = False
        self.sprite = sprite

    def update(self, keys, platforms):
        move = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move += 1

        self.vx = move * PLAYER_SPEED
        if move < 0:
            self.facing_left = True
        elif move > 0:
            self.facing_left = False

        if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.on_ground:
            self.vy = PLAYER_JUMP
            self.on_ground = False

        self.vy += GRAVITY
        if self.vy > 14:
            self.vy = 14

        self.rect.x += int(self.vx)
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vx > 0:
                    self.rect.right = p.rect.left
                elif self.vx < 0:
                    self.rect.left = p.rect.right

        self.rect.y += int(self.vy)
        self.on_ground = False
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vy > 0:
                    self.rect.bottom = p.rect.top
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0:
                    self.rect.top = p.rect.bottom
                    self.vy = 0

    def draw(self, screen, camera_x):
        target = self.rect.move(-camera_x, 0)
        sprite = pygame.transform.flip(self.sprite, self.facing_left, False)
        sprite = pygame.transform.smoothscale(sprite, (self.rect.width, self.rect.height))
        screen.blit(sprite, target)



def near_pink(color, tolerance=70):
    r, g, b = color[:3]
    return abs(r - 255) <= tolerance and g <= tolerance and abs(b - 255) <= tolerance


def apply_pink_transparency(surface, tolerance=70):
    surface = surface.convert_alpha()
    w, h = surface.get_size()
    cleaned = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        for x in range(w):
            c = surface.get_at((x, y))
            if near_pink(c, tolerance):
                cleaned.set_at((x, y), (0, 0, 0, 0))
            else:
                cleaned.set_at((x, y), c)
    return cleaned


def list_images(asset_dir):
    if not asset_dir.exists():
        return []
    files = []
    for p in asset_dir.iterdir():
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS:
            files.append(p)
    return files


def choose_assets(image_paths):
    if not image_paths:
        return None, None

    lower_map = {p: p.name.lower() for p in image_paths}
    bg_keywords = ("background", "bg", "sky")
    sp_keywords = ("sprite", "player", "mario", "character", "hero")

    bg = next((p for p in image_paths if any(k in lower_map[p] for k in bg_keywords)), None)
    sp = next((p for p in image_paths if any(k in lower_map[p] for k in sp_keywords)), None)

    if bg and sp:
        return bg, sp

    scored = sorted(
        image_paths,
        key=lambda p: os.path.getsize(p),
        reverse=True,
    )

    if not bg:
        bg = scored[0]

    if not sp:
        for p in reversed(scored):
            if p != bg:
                sp = p
                break
        if sp is None:
            sp = bg

    return bg, sp


def load_assets():
    image_paths = list_images(ASSET_DIR)
    bg_path, sprite_path = choose_assets(image_paths)

    if bg_path:
        background = pygame.image.load(str(bg_path)).convert()
    else:
        background = pygame.Surface((WIDTH, HEIGHT))
        background.fill((117, 193, 255))
        for i in range(12):
            pygame.draw.circle(background, (255, 255, 255), (80 + i * 80, 80 + (i % 3) * 15), 30)

    if sprite_path:
        sprite = pygame.image.load(str(sprite_path))
        sprite = apply_pink_transparency(sprite)
    else:
        sprite = pygame.Surface((32, 40), pygame.SRCALPHA)
        sprite.fill((205, 42, 42))
        pygame.draw.rect(sprite, (24, 24, 140), pygame.Rect(4, 20, 24, 18))

    return background, sprite, bg_path, sprite_path


def build_level():
    platforms = [
        Platform(-400, GROUND_Y, 5200, 120),
        Platform(280, GROUND_Y - 90, 130, 20),
        Platform(470, GROUND_Y - 155, 110, 20),
        Platform(700, GROUND_Y - 220, 110, 20),
        Platform(980, GROUND_Y - 70, 170, 20),
        Platform(1290, GROUND_Y - 120, 160, 20),
        Platform(1620, GROUND_Y - 175, 120, 20),
        Platform(1940, GROUND_Y - 95, 180, 20),
        Platform(2350, GROUND_Y - 165, 160, 20),
        Platform(2700, GROUND_Y - 230, 130, 20),
    ]

    enemies = [
        Enemy(860, GROUND_Y - 36),
        Enemy(1760, GROUND_Y - 36, speed=2.0),
        Enemy(2440, GROUND_Y - 36, speed=1.8),
    ]

    return platforms, enemies


def draw_background(screen, background, camera_x):
    bg_w, bg_h = background.get_size()
    scaled_h = HEIGHT
    scaled_w = int(bg_w * (scaled_h / bg_h)) if bg_h else WIDTH
    scaled = pygame.transform.smoothscale(background, (max(scaled_w, 1), scaled_h))

    parallax_x = int(camera_x * 0.35)
    start_x = -(parallax_x % scaled.get_width())

    x = start_x
    while x < WIDTH:
        screen.blit(scaled, (x, 0))
        x += scaled.get_width()


def main():
    pygame.init()
    pygame.display.set_caption("Mario-Style Platformer")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 22)

    background, sprite, bg_path, sprite_path = load_assets()
    platforms, enemies = build_level()
    player = Player(70, GROUND_Y - 150, sprite)

    camera_x = 0
    coins_collected = 0
    running = True

    coin_positions = [
        pygame.Rect(320, GROUND_Y - 120, 16, 16),
        pygame.Rect(505, GROUND_Y - 185, 16, 16),
        pygame.Rect(730, GROUND_Y - 250, 16, 16),
        pygame.Rect(1320, GROUND_Y - 150, 16, 16),
        pygame.Rect(1660, GROUND_Y - 205, 16, 16),
        pygame.Rect(2380, GROUND_Y - 195, 16, 16),
    ]

    status_lines = []
    if bg_path:
        status_lines.append(f"Background: {bg_path.name}")
    else:
        status_lines.append("Background: fallback")
    if sprite_path:
        status_lines.append(f"Sprite: {sprite_path.name} (pink removed)")
    else:
        status_lines.append("Sprite: fallback")

    while running:
        dt = clock.tick(FPS)
        _ = dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                player = Player(70, GROUND_Y - 150, sprite)
                platforms, enemies = build_level()
                coin_positions = [
                    pygame.Rect(320, GROUND_Y - 120, 16, 16),
                    pygame.Rect(505, GROUND_Y - 185, 16, 16),
                    pygame.Rect(730, GROUND_Y - 250, 16, 16),
                    pygame.Rect(1320, GROUND_Y - 150, 16, 16),
                    pygame.Rect(1660, GROUND_Y - 205, 16, 16),
                    pygame.Rect(2380, GROUND_Y - 195, 16, 16),
                ]
                coins_collected = 0

        keys = pygame.key.get_pressed()
        player.update(keys, platforms)

        for e in enemies:
            e.update(platforms)
            if player.rect.colliderect(e.rect):
                player.rect.topleft = (70, GROUND_Y - 150)
                player.vx = 0
                player.vy = 0

        for coin in coin_positions[:]:
            if player.rect.colliderect(coin):
                coin_positions.remove(coin)
                coins_collected += 1

        if player.rect.top > HEIGHT + 200:
            player.rect.topleft = (70, GROUND_Y - 150)
            player.vx = 0
            player.vy = 0

        world_end = 3200
        target_camera = player.rect.centerx - WIDTH // 3
        camera_x = max(0, min(target_camera, world_end - WIDTH))

        draw_background(screen, background, camera_x)

        for p in platforms:
            r = p.rect.move(-camera_x, 0)
            pygame.draw.rect(screen, (178, 112, 52), r)
            pygame.draw.rect(screen, (116, 73, 34), r, 2)

        for coin in coin_positions:
            r = coin.move(-camera_x, 0)
            pygame.draw.ellipse(screen, (245, 204, 18), r)
            pygame.draw.ellipse(screen, (175, 130, 8), r, 2)

        for e in enemies:
            r = e.rect.move(-camera_x, 0)
            pygame.draw.ellipse(screen, (117, 76, 42), r)
            pygame.draw.rect(screen, (40, 25, 10), (r.x + 6, r.y + 22, 8, 4))
            pygame.draw.rect(screen, (40, 25, 10), (r.x + 22, r.y + 22, 8, 4))

        player.draw(screen, camera_x)

        hud = font.render(f"Coins: {coins_collected}   Arrows/WASD + Space to jump   R = reset", True, (0, 0, 0))
        screen.blit(hud, (18, 12))

        for i, line in enumerate(status_lines):
            s = font.render(line, True, (25, 25, 25))
            screen.blit(s, (18, 38 + i * 22))

        if not coin_positions:
            msg = font.render("Level Clear!", True, (6, 91, 31))
            screen.blit(msg, (WIDTH - 160, 12))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
