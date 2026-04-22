"""
PIXEL QUEST: ZOMBIE APOCALYPSE
A 2D top-down zombie apocalypse RPG with detailed pixel art characters.
Mansion → Outside chaos → Save survivors → Find antidote ingredients → Save the world!

Controls:
  WASD / Arrow keys - Move
  SPACE - Swing sword
  E - Interact (doors, NPCs, shop, scientist)
  TAB - Open shop
  I - Inventory
  ESC - Pause / Back
"""

import pygame
import sys
import math
import random
import json
import os
import asyncio

pygame.init()

# ─── CONFIG ─────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 960, 640
TILE = 32
FPS = 60
SAVE_FILE = os.path.join(os.path.dirname(__file__), "pixel_quest_save.json")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
RED = (200, 40, 40)
DARK_RED = (140, 20, 20)
GREEN = (40, 180, 40)
DARK_GREEN = (20, 100, 20)
BLUE = (40, 80, 200)
DARK_BLUE = (20, 50, 140)
YELLOW = (240, 220, 40)
ORANGE = (220, 140, 30)
BROWN = (120, 70, 30)
DARK_BROWN = (80, 45, 15)
LIGHT_BROWN = (160, 110, 60)
SKIN = (230, 180, 130)
DARK_SKIN = (190, 140, 100)
LIGHT_SKIN = (245, 210, 170)
PURPLE = (140, 40, 180)
DARK_PURPLE = (90, 20, 120)
CYAN = (40, 200, 220)
PINK = (220, 100, 140)
ZOMBIE_GREEN = (100, 160, 80)
DARK_ZOMBIE = (60, 110, 50)
LIGHT_ZOMBIE = (140, 190, 110)

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Pixel Quest: Zombie Apocalypse")
clock = pygame.time.Clock()
font_sm = pygame.font.SysFont("consolas", 14)
font_md = pygame.font.SysFont("consolas", 18)
font_lg = pygame.font.SysFont("consolas", 28, bold=True)
font_xl = pygame.font.SysFont("consolas", 42, bold=True)
font_title = pygame.font.SysFont("consolas", 56, bold=True)


# ─── PIXEL ART GENERATOR ───────────────────────────────────────────
def create_surface(w, h):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    return s


def px(surf, x, y, color):
    """Draw a single pixel."""
    if 0 <= x < surf.get_width() and 0 <= y < surf.get_height():
        surf.set_at((x, y), color)


def shade(color, factor=0.7):
    """Darken a color for shadow."""
    return tuple(max(0, int(c * factor)) for c in color[:3])


def highlight(color, factor=1.3):
    """Lighten a color for highlight."""
    return tuple(min(255, int(c * factor)) for c in color[:3])


def draw_pixel_rect(surf, x, y, w, h, color, pseudo_3d=True):
    """Draw a filled rect with optional pseudo-3D shading."""
    for dy in range(h):
        for dx in range(w):
            if pseudo_3d:
                if dy == 0 or dx == 0:
                    px(surf, x + dx, y + dy, highlight(color))
                elif dy == h - 1 or dx == w - 1:
                    px(surf, x + dx, y + dy, shade(color))
                else:
                    px(surf, x + dx, y + dy, color)
            else:
                px(surf, x + dx, y + dy, color)


# ─── CHARACTER SPRITES (Detailed Pixel Art with Pseudo-3D) ─────────
def make_player_sprite(direction=0, frame=0, sword_id=0):
    """
    Create a 24x24 detailed pixel player sprite with pseudo-3D shading.
    direction: 0=down, 1=left, 2=up, 3=right
    frame: walk animation frame 0-3
    """
    s = create_surface(24, 24)
    hair = (60, 30, 10)
    hair_hi = highlight(hair)
    hair_sh = shade(hair)
    shirt = (40, 80, 180)
    shirt_hi = highlight(shirt)
    shirt_sh = shade(shirt)
    pants = (50, 50, 70)
    pants_hi = highlight(pants)
    pants_sh = shade(pants)
    boots = (60, 35, 20)
    belt = YELLOW

    bob = 1 if frame % 2 == 1 else 0

    # Shadow on ground (ellipse)
    for dx in range(-4, 5):
        for dy in range(-1, 2):
            if dx * dx + dy * dy * 4 < 20:
                px(s, 12 + dx, 22 + dy, (0, 0, 0, 60))

    # Boots (slight walk animation)
    left_foot_offset = -1 if frame == 1 else (1 if frame == 3 else 0)
    right_foot_offset = 1 if frame == 1 else (-1 if frame == 3 else 0)
    # Left boot
    draw_pixel_rect(s, 8 + left_foot_offset, 19 - bob, 3, 3, boots)
    # Right boot
    draw_pixel_rect(s, 13 + right_foot_offset, 19 - bob, 3, 3, boots)

    # Pants
    draw_pixel_rect(s, 8, 16 - bob, 8, 4, pants, True)

    # Belt
    for bx in range(8, 16):
        px(s, bx, 15 - bob, belt)

    # Shirt/torso (pseudo-3D: lighter top, darker bottom)
    for ty in range(4):
        for tx in range(10):
            c = shirt_hi if ty < 2 else (shirt if tx > 1 and tx < 8 else shirt_sh)
            if tx == 0 or tx == 9:
                c = shirt_sh
            px(s, 7 + tx, 10 + ty - bob, c)

    # Arms
    arm_swing = frame % 2
    # Left arm
    draw_pixel_rect(s, 5, 10 - bob + arm_swing, 2, 5, SKIN)
    px(s, 5, 10 - bob + arm_swing, LIGHT_SKIN)
    # Right arm
    draw_pixel_rect(s, 17, 10 - bob + (1 - arm_swing), 2, 5, SKIN)
    px(s, 17, 10 - bob + (1 - arm_swing), LIGHT_SKIN)

    # Head (pseudo-3D oval)
    head_pixels = [
        (10, 3), (11, 3), (12, 3), (13, 3),
        (9, 4), (10, 4), (11, 4), (12, 4), (13, 4), (14, 4),
        (9, 5), (10, 5), (11, 5), (12, 5), (13, 5), (14, 5),
        (9, 6), (10, 6), (11, 6), (12, 6), (13, 6), (14, 6),
        (9, 7), (10, 7), (11, 7), (12, 7), (13, 7), (14, 7),
        (10, 8), (11, 8), (12, 8), (13, 8),
    ]
    for hx, hy in head_pixels:
        hy2 = hy - bob
        # Pseudo-3D shading on head
        if hy <= 4:
            px(s, hx, hy2, LIGHT_SKIN)
        elif hx <= 9:
            px(s, hx, hy2, DARK_SKIN)
        elif hx >= 14:
            px(s, hx, hy2, DARK_SKIN)
        else:
            px(s, hx, hy2, SKIN)

    # Hair (on top, pseudo-3D)
    hair_px = [
        (9, 2), (10, 2), (11, 2), (12, 2), (13, 2), (14, 2),
        (9, 3), (14, 3),
    ]
    if direction == 2:  # facing up, more hair visible
        hair_px += [(9, 4), (14, 4), (9, 5), (14, 5),
                    (10, 3), (11, 3), (12, 3), (13, 3)]
    for hx, hy in hair_px:
        c = hair_hi if hy == 2 else (hair if hx < 12 else hair_sh)
        px(s, hx, hy - bob, c)

    # Face details (only when facing down or sides)
    if direction != 2:
        # Eyes
        if direction == 0:  # down
            px(s, 10, 5 - bob, WHITE)
            px(s, 11, 5 - bob, (30, 30, 30))
            px(s, 13, 5 - bob, WHITE)
            px(s, 12, 5 - bob, (30, 30, 30))
            # Mouth
            px(s, 11, 7 - bob, (180, 80, 80))
            px(s, 12, 7 - bob, (180, 80, 80))
        elif direction == 1:  # left
            px(s, 10, 5 - bob, WHITE)
            px(s, 9, 5 - bob, (30, 30, 30))
            px(s, 10, 7 - bob, (180, 80, 80))
        elif direction == 3:  # right
            px(s, 13, 5 - bob, WHITE)
            px(s, 14, 5 - bob, (30, 30, 30))
            px(s, 13, 7 - bob, (180, 80, 80))

    return pygame.transform.scale(s, (48, 48))


def make_zombie_sprite(ztype=0, frame=0, direction=0):
    """
    Detailed pixel zombie with pseudo-3D.
    ztype: 0=normal, 1=fast, 2=tank
    """
    s = create_surface(24, 24)
    if ztype == 0:
        body_c = ZOMBIE_GREEN
        shirt_c = (80, 60, 50)
    elif ztype == 1:
        body_c = (140, 170, 90)
        shirt_c = (100, 40, 40)
    else:
        body_c = (70, 120, 60)
        shirt_c = (50, 50, 50)

    body_hi = highlight(body_c)
    body_sh = shade(body_c)
    shirt_sh = shade(shirt_c)
    bob = 1 if frame % 2 == 1 else 0
    lean = 1 if frame % 4 >= 2 else -1

    # Shadow
    for dx in range(-4, 5):
        for dy in range(-1, 2):
            if dx * dx + dy * dy * 4 < 20:
                px(s, 12 + dx, 22 + dy, (0, 0, 0, 50))

    # Feet (shambling)
    draw_pixel_rect(s, 8 + lean, 19 - bob, 3, 3, DARK_BROWN)
    draw_pixel_rect(s, 13 - lean, 19 - bob, 3, 3, DARK_BROWN)

    # Torn pants
    for ty in range(3):
        for tx in range(8):
            if random.random() > 0.15:
                px(s, 8 + tx, 16 + ty - bob, (50, 50, 40))

    # Torso (torn shirt)
    for ty in range(5):
        for tx in range(10):
            if random.random() > 0.1:
                c = shirt_c if ty < 3 else shirt_sh
                if tx == 0 or tx == 9:
                    c = shirt_sh
                px(s, 7 + tx, 10 + ty - bob, c)

    # Arms (reaching forward, zombie-style)
    arm_ext = 2 if direction == 0 else 0
    draw_pixel_rect(s, 4 + lean, 9 - bob, 3, 5 + arm_ext, body_c)
    px(s, 4 + lean, 9 - bob, body_hi)
    draw_pixel_rect(s, 17 - lean, 10 - bob, 3, 4 + arm_ext, body_c)
    px(s, 17 - lean, 10 - bob, body_hi)
    # Fingers
    px(s, 4 + lean, 14 - bob + arm_ext, body_sh)
    px(s, 5 + lean, 14 - bob + arm_ext, body_sh)

    # Head (decayed, pseudo-3D)
    for hy in range(3, 9):
        for hx in range(9, 15):
            if (hx - 12) ** 2 + (hy - 5.5) ** 2 < 12:
                c = body_hi if hy <= 4 else (body_c if 10 <= hx <= 13 else body_sh)
                px(s, hx, hy - bob, c)

    # Zombie face
    if direction != 2:
        # Glowing red eyes
        px(s, 10, 5 - bob, RED)
        px(s, 11, 5 - bob, DARK_RED)
        px(s, 13, 5 - bob, RED)
        px(s, 12, 5 - bob, DARK_RED)
        # Open mouth
        px(s, 11, 7 - bob, (60, 0, 0))
        px(s, 12, 7 - bob, (60, 0, 0))
        px(s, 11, 8 - bob, DARK_RED)

    # Wound marks
    px(s, 14, 6 - bob, DARK_RED)
    px(s, 8, 12 - bob, DARK_RED)

    # Tank zombie is bigger
    if ztype == 2:
        s = pygame.transform.scale(s, (28, 28))
        s2 = create_surface(24, 24)
        s2.blit(s, (-2, -2))
        return pygame.transform.scale(s2, (56, 56))

    return pygame.transform.scale(s, (48, 48))


def make_survivor_sprite(variant=0):
    """Detailed pixel art survivor NPC."""
    s = create_surface(24, 24)
    # Different survivor looks
    colors = [
        {"shirt": (180, 40, 40), "hair": (40, 30, 20), "skin": SKIN},
        {"shirt": (40, 160, 60), "hair": (200, 180, 50), "skin": (200, 160, 120)},
        {"shirt": (160, 40, 160), "hair": (20, 20, 20), "skin": (180, 130, 90)},
        {"shirt": (40, 140, 180), "hair": (160, 80, 30), "skin": (230, 190, 150)},
    ]
    c = colors[variant % len(colors)]
    shirt = c["shirt"]
    hair = c["hair"]
    skin = c["skin"]

    # Shadow
    for dx in range(-3, 4):
        for dy in range(-1, 2):
            if dx * dx + dy * dy * 4 < 14:
                px(s, 12 + dx, 22 + dy, (0, 0, 0, 50))

    # Shoes
    draw_pixel_rect(s, 9, 19, 2, 3, DARK_BROWN)
    draw_pixel_rect(s, 13, 19, 2, 3, DARK_BROWN)
    # Pants
    draw_pixel_rect(s, 8, 16, 8, 3, (60, 60, 80))
    # Shirt
    draw_pixel_rect(s, 7, 10, 10, 6, shirt, True)
    # Arms
    draw_pixel_rect(s, 5, 11, 2, 4, skin)
    draw_pixel_rect(s, 17, 11, 2, 4, skin)
    # Head
    for hy in range(3, 9):
        for hx in range(9, 15):
            if (hx - 12) ** 2 + (hy - 5.5) ** 2 < 11:
                c2 = highlight(skin) if hy <= 4 else (skin if 10 <= hx <= 13 else shade(skin))
                px(s, hx, hy, c2)
    # Hair
    for hx in range(9, 15):
        px(s, hx, 2, highlight(hair))
        px(s, hx, 3, hair)
    px(s, 9, 3, hair)
    px(s, 14, 3, hair)
    # Eyes
    px(s, 10, 5, WHITE)
    px(s, 11, 5, (30, 30, 30))
    px(s, 13, 5, WHITE)
    px(s, 12, 5, (30, 30, 30))
    # Scared expression - open mouth
    px(s, 11, 7, (200, 80, 80))
    px(s, 12, 7, (200, 80, 80))
    # Exclamation above head
    px(s, 12, 0, YELLOW)
    px(s, 12, 1, YELLOW)
    return pygame.transform.scale(s, (48, 48))


def make_scientist_sprite():
    """Pixel art scientist NPC in lab coat."""
    s = create_surface(24, 24)
    coat = (220, 220, 230)
    coat_sh = shade(coat)

    # Shadow
    for dx in range(-3, 4):
        for dy in range(-1, 2):
            if dx * dx + dy * dy * 4 < 14:
                px(s, 12 + dx, 22 + dy, (0, 0, 0, 50))

    # Shoes
    draw_pixel_rect(s, 9, 20, 2, 2, (30, 30, 30))
    draw_pixel_rect(s, 13, 20, 2, 2, (30, 30, 30))
    # Lab coat (long)
    draw_pixel_rect(s, 7, 10, 10, 10, coat, True)
    for tx in range(10):
        px(s, 7 + tx, 19, coat_sh)
    # Arms in coat
    draw_pixel_rect(s, 5, 11, 2, 5, coat)
    draw_pixel_rect(s, 17, 11, 2, 5, coat)
    # Hands
    px(s, 5, 16, SKIN)
    px(s, 17, 16, SKIN)
    # Head
    for hy in range(3, 9):
        for hx in range(9, 15):
            if (hx - 12) ** 2 + (hy - 5.5) ** 2 < 11:
                c = LIGHT_SKIN if hy <= 4 else (SKIN if 10 <= hx <= 13 else DARK_SKIN)
                px(s, hx, hy, c)
    # Wild white hair
    for hx in range(8, 16):
        px(s, hx, 2, WHITE)
        if hx in (8, 9, 14, 15):
            px(s, hx, 3, WHITE)
            px(s, hx, 4, (220, 220, 220))
    # Glasses
    px(s, 10, 5, (100, 200, 255))
    px(s, 11, 5, DARK_GRAY)
    px(s, 12, 5, DARK_GRAY)
    px(s, 13, 5, (100, 200, 255))
    # Smile
    px(s, 11, 7, (180, 80, 80))
    px(s, 12, 7, (180, 80, 80))
    return pygame.transform.scale(s, (48, 48))


def make_sword_sprite(sword_id=0, angle=0):
    """Pixel art sword with details."""
    s = create_surface(24, 24)
    sword_visuals = {
        0: {"blade": (160, 160, 170), "guard": BROWN, "hilt": DARK_BROWN},
        1: {"blade": (140, 140, 140), "guard": (120, 100, 80), "hilt": DARK_BROWN},
        2: {"blade": (200, 200, 210), "guard": (180, 150, 40), "hilt": BROWN},
        3: {"blade": (210, 215, 220), "guard": (160, 160, 170), "hilt": (80, 60, 40)},
        4: {"blade": (220, 225, 235), "guard": (180, 180, 200), "hilt": (100, 100, 110)},
        5: {"blade": (240, 200, 50), "guard": (200, 160, 30), "hilt": (160, 120, 20)},
        6: {"blade": (150, 220, 255), "guard": (100, 180, 220), "hilt": (60, 120, 160)},
        7: {"blade": (80, 50, 120), "guard": (60, 30, 90), "hilt": (40, 20, 60)},
        8: {"blade": (100, 200, 255), "guard": BLUE, "hilt": DARK_BLUE},
        9: {"blade": (255, 255, 100), "guard": (200, 200, 60), "hilt": (160, 140, 30)},
        10: {"blade": (255, 120, 30), "guard": RED, "hilt": DARK_RED},
        11: {"blade": (180, 0, 0), "guard": (100, 0, 0), "hilt": (40, 0, 0)},
    }
    sw = sword_visuals.get(sword_id, sword_visuals[0])
    blade = sw["blade"]
    guard = sw["guard"]
    hilt = sw["hilt"]

    # Hilt (handle)
    draw_pixel_rect(s, 11, 18, 3, 5, hilt, True)
    # Guard (cross)
    draw_pixel_rect(s, 8, 16, 9, 2, guard, True)
    # Blade
    for by in range(0, 16):
        w = max(1, 5 - by // 4)
        cx = 12 - w // 2
        for bx in range(w):
            c = highlight(blade) if bx == 0 else (shade(blade) if bx == w - 1 else blade)
            if by < 2:
                c = highlight(blade, 1.5)  # tip glow
            px(s, cx + bx, by, c)

    # Special effects for fire/ice/legendary/devil
    if sword_id == 10:  # fire particles
        for _ in range(4):
            fx, fy = random.randint(9, 14), random.randint(0, 8)
            px(s, fx, fy, (255, random.randint(100, 255), 0))
    elif sword_id == 8:  # ice crystals
        for _ in range(3):
            fx, fy = random.randint(9, 14), random.randint(0, 8)
            px(s, fx, fy, (200, 240, 255))
    elif sword_id == 9:  # lightning sparks
        for _ in range(4):
            fx, fy = random.randint(9, 14), random.randint(0, 10)
            px(s, fx, fy, (255, 255, 200))
    elif sword_id == 7:  # shadow wisps
        for _ in range(3):
            fx, fy = random.randint(8, 15), random.randint(0, 10)
            px(s, fx, fy, (120, 80, 180))
    elif sword_id == 11:  # devil flames
        for _ in range(6):
            fx, fy = random.randint(8, 15), random.randint(0, 10)
            px(s, fx, fy, (random.randint(150, 255), 0, 0))
        for _ in range(3):
            fx, fy = random.randint(9, 14), random.randint(0, 6)
            px(s, fx, fy, (255, random.randint(60, 120), 0))

    result = pygame.transform.scale(s, (32, 32))
    if angle != 0:
        result = pygame.transform.rotate(result, angle)
    return result


def make_coin_sprite(frame=0):
    """Spinning coin pixel art."""
    s = create_surface(12, 12)
    # Width changes for spin effect
    widths = [5, 4, 2, 1, 2, 4, 5, 5]
    w = widths[frame % len(widths)]
    cx = 6
    for dy in range(-5, 6):
        for dx in range(-w, w + 1):
            dist = abs(dx) + abs(dy) * 0.5
            if dx * dx / max(w * w, 1) + dy * dy / 25 < 1:
                if dy < -2:
                    px(s, cx + dx, 6 + dy, highlight(YELLOW, 1.4))
                elif dx < 0:
                    px(s, cx + dx, 6 + dy, YELLOW)
                else:
                    px(s, cx + dx, 6 + dy, shade(YELLOW, 0.85))
    # $ symbol
    if w >= 3:
        px(s, 6, 4, ORANGE)
        px(s, 6, 5, ORANGE)
        px(s, 6, 6, ORANGE)
    return pygame.transform.scale(s, (20, 20))


def make_ingredient_sprite(ing_type=0):
    """Pixel art antidote ingredients."""
    s = create_surface(16, 16)
    if ing_type == 0:  # Blue herb
        draw_pixel_rect(s, 7, 10, 2, 5, GREEN)
        for lx in range(5, 11):
            for ly in range(3, 9):
                if (lx - 8) ** 2 + (ly - 6) ** 2 < 8:
                    px(s, lx, ly, (40, 100, 220))
        px(s, 8, 4, (100, 160, 255))
    elif ing_type == 1:  # Red mushroom
        draw_pixel_rect(s, 7, 10, 2, 5, (180, 170, 150))
        for lx in range(4, 12):
            for ly in range(3, 9):
                if (lx - 8) ** 2 + (ly - 6) ** 2 < 12:
                    px(s, lx, ly, RED)
        px(s, 6, 5, WHITE)
        px(s, 10, 6, WHITE)
    elif ing_type == 2:  # Glowing crystal
        for dy in range(10):
            w = max(1, 4 - abs(dy - 5))
            for dx in range(w):
                px(s, 7 + dx, 3 + dy, CYAN)
        px(s, 8, 4, (200, 255, 255))
        px(s, 8, 5, highlight(CYAN, 1.4))
    else:  # zombie blood vial
        draw_pixel_rect(s, 6, 6, 4, 8, (200, 200, 220), True)
        draw_pixel_rect(s, 5, 4, 6, 2, (180, 180, 200), True)
        draw_pixel_rect(s, 7, 8, 2, 4, ZOMBIE_GREEN)
        # Cork
        draw_pixel_rect(s, 7, 3, 2, 2, BROWN)
    return pygame.transform.scale(s, (28, 28))


def make_heart_sprite(full=True):
    s = create_surface(12, 12)
    c = RED if full else DARK_GRAY
    heart = [
        (3, 2), (4, 2), (7, 2), (8, 2),
        (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3),
        (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4),
        (3, 5), (4, 5), (5, 5), (6, 5), (7, 5), (8, 5),
        (4, 6), (5, 6), (6, 6), (7, 6),
        (5, 7), (6, 7),
    ]
    for hx, hy in heart:
        if full and (hx <= 4 and hy <= 3):
            px(s, hx, hy, highlight(c, 1.3))
        else:
            px(s, hx, hy, c)
    return pygame.transform.scale(s, (22, 22))


# ─── TILES ──────────────────────────────────────────────────────────
def make_tile(tile_type):
    """Generate a top-down tile for the world."""
    s = create_surface(TILE, TILE)
    if tile_type == "grass":
        s.fill((60, 140, 50))
        for _ in range(12):
            gx, gy = random.randint(0, 30), random.randint(0, 30)
            px(s, gx, gy, (50, 120, 40))
            px(s, gx + 1, gy, (70, 160, 60))
    elif tile_type == "chaos_grass":
        s.fill((50, 90, 40))
        for _ in range(8):
            gx, gy = random.randint(0, 30), random.randint(0, 30)
            px(s, gx, gy, (80, 60, 40))
        # Dead patches
        for _ in range(3):
            gx, gy = random.randint(2, 28), random.randint(2, 28)
            pygame.draw.circle(s, (70, 60, 40), (gx, gy), 3)
    elif tile_type == "road":
        s.fill((100, 95, 85))
        for _ in range(6):
            gx, gy = random.randint(0, 30), random.randint(0, 30)
            px(s, gx, gy, (80, 75, 65))
    elif tile_type == "wall":
        s.fill((80, 60, 45))
        for y in range(0, TILE, 8):
            for x in range(0, TILE, 16):
                offset = 8 if (y // 8) % 2 else 0
                pygame.draw.rect(s, (90, 70, 55), (x + offset, y, 15, 7))
                pygame.draw.rect(s, (60, 45, 30), (x + offset, y, 15, 7), 1)
    elif tile_type == "floor_wood":
        s.fill((140, 100, 60))
        for y in range(0, TILE, 4):
            pygame.draw.line(s, (120, 85, 50), (0, y), (TILE, y))
        for x in range(0, TILE, 10):
            pygame.draw.line(s, (120, 85, 50), (x, 0), (x, TILE))
    elif tile_type == "floor_tile":
        s.fill((180, 180, 190))
        pygame.draw.rect(s, (160, 160, 170), (0, 0, TILE, TILE), 1)
        pygame.draw.line(s, (160, 160, 170), (TILE // 2, 0), (TILE // 2, TILE))
        pygame.draw.line(s, (160, 160, 170), (0, TILE // 2), (TILE, TILE // 2))
    elif tile_type == "floor_kitchen":
        c1 = (200, 200, 200) if random.random() > 0.5 else (160, 160, 170)
        s.fill(c1)
        pygame.draw.rect(s, (140, 140, 150), (0, 0, TILE, TILE), 1)
    elif tile_type == "carpet":
        s.fill((140, 40, 50))
        pygame.draw.rect(s, (160, 50, 60), (2, 2, TILE - 4, TILE - 4))
        pygame.draw.rect(s, (180, 70, 80), (4, 4, TILE - 8, TILE - 8))
    elif tile_type == "couch":
        # Carpet background
        s.fill((140, 40, 50))
        pygame.draw.rect(s, (160, 50, 60), (2, 2, TILE - 4, TILE - 4))
        # Couch seat (brown leather)
        pygame.draw.rect(s, (100, 55, 25), (2, 6, TILE - 4, TILE - 12))
        pygame.draw.rect(s, (120, 70, 35), (4, 8, TILE - 8, TILE - 16))
        # Backrest
        pygame.draw.rect(s, (80, 40, 15), (2, 2, TILE - 4, 6))
        pygame.draw.rect(s, (90, 50, 20), (4, 3, TILE - 8, 4))
        # Armrests
        pygame.draw.rect(s, (85, 45, 18), (1, 4, 4, TILE - 10))
        pygame.draw.rect(s, (85, 45, 18), (TILE - 5, 4, 4, TILE - 10))
        # Cushion details
        pygame.draw.line(s, (70, 35, 12), (TILE // 2, 8), (TILE // 2, TILE - 8))
        # Highlight on top edge
        pygame.draw.line(s, (140, 85, 40), (4, 3), (TILE - 5, 3))
    elif tile_type == "door":
        s.fill((100, 60, 30))
        pygame.draw.rect(s, (80, 45, 20), (2, 2, TILE - 4, TILE - 4), 2)
        pygame.draw.circle(s, YELLOW, (TILE - 8, TILE // 2), 3)
    elif tile_type == "lab_floor":
        s.fill((200, 210, 210))
        pygame.draw.rect(s, (180, 190, 190), (0, 0, TILE, TILE), 1)
    elif tile_type == "water":
        s.fill((30, 80, 160))
        for _ in range(3):
            wx = random.randint(0, 28)
            pygame.draw.line(s, (60, 120, 200), (wx, 10), (wx + 6, 10))
    elif tile_type == "ruin":
        s.fill((80, 75, 65))
        for _ in range(5):
            rx, ry = random.randint(0, 28), random.randint(0, 28)
            pygame.draw.rect(s, (60, 55, 45), (rx, ry, 4, 4))
    elif tile_type == "mansion_exit":
        s.fill((60, 140, 50))
        pygame.draw.rect(s, YELLOW, (4, 4, TILE - 8, TILE - 8), 2)
    elif tile_type == "mountain":
        s.fill((90, 80, 70))
        # Rocky mountain texture
        for _ in range(6):
            rx, ry = random.randint(0, 28), random.randint(0, 28)
            pygame.draw.rect(s, (70, 60, 50), (rx, ry, 5, 4))
        for _ in range(3):
            rx, ry = random.randint(2, 26), random.randint(2, 26)
            pygame.draw.rect(s, (110, 100, 85), (rx, ry, 3, 3))
    elif tile_type == "mountain_gate":
        s.fill((90, 80, 70))
        pygame.draw.rect(s, (40, 20, 20), (6, 2, TILE - 12, TILE - 4))
        pygame.draw.rect(s, (60, 30, 30), (8, 4, TILE - 16, TILE - 8))
        pygame.draw.rect(s, DARK_RED, (6, 2, TILE - 12, TILE - 4), 1)
    elif tile_type == "dark_hall":
        s.fill((25, 15, 20))
        for _ in range(4):
            rx, ry = random.randint(0, 28), random.randint(0, 28)
            pygame.draw.rect(s, (35, 20, 25), (rx, ry, 4, 4))
        pygame.draw.rect(s, (20, 10, 15), (0, 0, TILE, TILE), 1)
    elif tile_type == "bed":
        s.fill((140, 100, 60))
        pygame.draw.rect(s, (80, 50, 30), (2, 2, TILE - 4, TILE - 4))
        pygame.draw.rect(s, (60, 35, 20), (2, 2, TILE - 4, TILE - 4), 1)
        pygame.draw.rect(s, (200, 200, 220), (4, 4, TILE - 8, TILE - 12))
        pygame.draw.rect(s, (180, 50, 50), (4, TILE // 2 - 2, TILE - 8, TILE // 2))
        pygame.draw.rect(s, (150, 40, 40), (4, TILE // 2 - 2, TILE - 8, TILE // 2), 1)
    elif tile_type == "stove":
        s.fill((60, 60, 65))
        pygame.draw.rect(s, (50, 50, 55), (2, 2, TILE - 4, TILE - 4))
        pygame.draw.rect(s, (40, 40, 45), (2, 2, TILE - 4, TILE - 4), 1)
        pygame.draw.circle(s, (80, 30, 20), (TILE // 3, TILE // 3), 5, 1)
        pygame.draw.circle(s, (80, 30, 20), (2 * TILE // 3, TILE // 3), 5, 1)
        pygame.draw.circle(s, (200, 100, 30), (TILE // 3, TILE // 3), 3)
        pygame.draw.circle(s, (200, 100, 30), (2 * TILE // 3, TILE // 3), 3)
    elif tile_type == "bookshelf":
        s.fill((60, 35, 15))
        pygame.draw.rect(s, (50, 30, 12), (1, 1, TILE - 2, TILE - 2), 1)
        for sy2 in range(4, TILE - 2, 6):
            pygame.draw.line(s, (45, 25, 10), (2, sy2), (TILE - 3, sy2))
            for sx2 in range(4, TILE - 2, 5):
                c = random.choice([(140, 40, 40), (40, 80, 140), (40, 120, 50), (140, 120, 40)])
                pygame.draw.rect(s, c, (sx2, sy2 - 4, 4, 4))
    return s


# Pre-generate tiles
TILE_CACHE = {}


def get_tile(tile_type):
    if tile_type not in TILE_CACHE:
        TILE_CACHE[tile_type] = make_tile(tile_type)
    return TILE_CACHE[tile_type]


# ─── SWORD DATA ─────────────────────────────────────────────────────
SWORDS = {
    0: {"name": "Wooden Sword", "damage": 8, "speed": 1.0, "cost": 0, "color": (160, 130, 80)},
    1: {"name": "Stone Sword", "damage": 12, "speed": 1.0, "cost": 100, "color": (140, 140, 140)},
    2: {"name": "Iron Sword", "damage": 18, "speed": 1.0, "cost": 200, "color": (200, 200, 210)},
    3: {"name": "Steel Sword", "damage": 24, "speed": 1.1, "cost": 300, "color": (210, 215, 220)},
    4: {"name": "Silver Sword", "damage": 30, "speed": 1.1, "cost": 400, "color": (220, 225, 235)},
    5: {"name": "Gold Sword", "damage": 36, "speed": 1.2, "cost": 500, "color": (240, 200, 50)},
    6: {"name": "Crystal Sword", "damage": 42, "speed": 1.2, "cost": 600, "color": (150, 220, 255)},
    7: {"name": "Shadow Blade", "damage": 50, "speed": 1.3, "cost": 700, "color": (80, 50, 120)},
    8: {"name": "Ice Sword", "damage": 58, "speed": 1.3, "cost": 800, "color": (80, 180, 255)},
    9: {"name": "Lightning Blade", "damage": 66, "speed": 1.4, "cost": 900, "color": (255, 255, 100)},
    10: {"name": "Fire Sword", "damage": 80, "speed": 1.5, "cost": 1000, "color": (255, 100, 20)},
    11: {"name": "Devil Sword", "damage": 666, "speed": 1.8, "cost": 6666, "color": (180, 0, 0)},
}

SWORD_UPGRADES = {
    0: {"max_level": 3, "cost_per": 15, "dmg_per": 2},
    1: {"max_level": 3, "cost_per": 20, "dmg_per": 2},
    2: {"max_level": 3, "cost_per": 25, "dmg_per": 3},
    3: {"max_level": 3, "cost_per": 30, "dmg_per": 3},
    4: {"max_level": 3, "cost_per": 35, "dmg_per": 4},
    5: {"max_level": 3, "cost_per": 40, "dmg_per": 4},
    6: {"max_level": 3, "cost_per": 50, "dmg_per": 5},
    7: {"max_level": 3, "cost_per": 60, "dmg_per": 5},
    8: {"max_level": 3, "cost_per": 70, "dmg_per": 6},
    9: {"max_level": 3, "cost_per": 80, "dmg_per": 7},
    10: {"max_level": 5, "cost_per": 100, "dmg_per": 8},
    11: {"max_level": 5, "cost_per": 200, "dmg_per": 15},
}

INGREDIENT_NAMES = ["Blue Herb", "Red Mushroom", "Glowing Crystal", "Zombie Blood Vial"]
INGREDIENT_DESC = [
    "A rare herb that grows near water",
    "Found in dark forest patches",
    "Shimmers in ruined buildings",
    "Extracted from zombie remains",
]


# ─── MAP DEFINITIONS ───────────────────────────────────────────────
# Mansion: 30x22 tile map
# Legend: W=wall, .=wood floor, K=kitchen floor, T=tile floor, C=carpet,
#         D=door, L=lab floor, E=exit, S=shop spot, P=player start, Z=scientist
def create_mansion_map():
    # b=bed, f=stove, k=chef spot, h=training dummy, g=bookshelf
    layout = [
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "Wbb..WKfKKKWWLLLLLWW.gCCCCCCWW",
        "Wbb..WKfKKKDDLLLLLWW.gCCCCCCWW",
        "W....WKkKKKW.LZLLLWW..CCCCCCWW",
        "W..DDWKKKKKW.LLLLLWW..CCCCCCWW",
        "W....W.KKKKWWDDWWWWW..CCCCCCWW",
        "WWWWWWWWDDWWWW....WWWWDDWWWWWW",
        "W.........................TT..",
        "W..........P..............TT..",
        "W.........................TT..",
        "W.........................ST..",
        "W.........................TT..",
        "WWWWWWWWDDWWWWWWWDDWWWWWWWWWWW",
        "WCCCCCCCCWW.hh.hh.WWTTTTTTTTTW",
        "WCcCCCcCCWW.hh.hh.WWTTTTTTTTTW",
        "WCCCCCCCCWDD.....DDWTTTTTTTTTTW",
        "WCcCCCcCCW........WWTTTTTTTTTTW",
        "WCCCCCCCCW........WWTTTTTTTTTTW",
        "WCCCCCCCCWWWWWWWWWWWTTTTTTTTTTW",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
    ]
    return layout


# Outside world: 200x150 tile map (procedural, very big rolling map)
def create_outside_map():
    W, H = 200, 150
    grid = [["chaos_grass"] * W for _ in range(H)]

    # Major roads (cross pattern)
    for y in range(H):
        for x in range(98, 102):
            grid[y][x] = "road"
    for x in range(W):
        for y in range(73, 77):
            grid[y][x] = "road"

    # Additional side roads
    for y in range(H):
        for x in range(48, 52):
            grid[y][x] = "road"
        for x in range(148, 152):
            grid[y][x] = "road"
    for x in range(W):
        for y in range(38, 42):
            grid[y][x] = "road"
        for y in range(108, 112):
            grid[y][x] = "road"

    # Ruined buildings scattered across the big map
    ruins = [
        (10, 10, 8, 6), (60, 15, 10, 7), (140, 12, 9, 6),
        (25, 50, 7, 7), (80, 55, 8, 6), (160, 48, 10, 8),
        (15, 90, 8, 7), (120, 95, 7, 6), (170, 88, 9, 7),
        (35, 120, 8, 6), (90, 130, 10, 7), (155, 125, 8, 8),
        (55, 85, 7, 6), (130, 60, 8, 7), (45, 30, 6, 5),
    ]
    for rx, ry, rw, rh in ruins:
        for dy in range(rh):
            for dx in range(rw):
                ny, nx = ry + dy, rx + dx
                if 0 <= ny < H and 0 <= nx < W:
                    if dy == 0 or dy == rh - 1 or dx == 0 or dx == rw - 1:
                        grid[ny][nx] = "wall"
                    else:
                        grid[ny][nx] = "ruin"
        if ry + rh - 1 < H and rx + rw // 2 < W:
            grid[ry + rh - 1][rx + rw // 2] = "road"

    # Water areas
    water_spots = [(30, 100), (170, 30), (80, 140), (150, 110)]
    for wx, wy in water_spots:
        for dy in range(-5, 6):
            for dx in range(-6, 7):
                if dx * dx + dy * dy < 30 and 0 <= wy + dy < H and 0 <= wx + dx < W:
                    grid[wy + dy][wx + dx] = "water"

    # Mansion entrance on west edge (just outside east wall of mansion)
    for dy in range(5, 15):
        for dx in range(4):
            if dy < H and 29 + dx < W:
                grid[dy][29 + dx] = "road"

    # Mountain at far east with gate (boss area)
    mx, my = 185, 75  # mountain center
    for dy in range(-6, 7):
        for dx in range(-8, 9):
            if dx * dx / 64 + dy * dy / 36 < 1:
                ny, nx = my + dy, mx + dx
                if 0 <= ny < H and 0 <= nx < W:
                    grid[ny][nx] = "mountain"
    # Gate entrance (2 wide)
    grid[my + 6][mx] = "mountain_gate"
    grid[my + 6][mx + 1] = "mountain_gate"
    # Dark hall path behind gate
    for dy in range(7, 15):
        for dx2 in range(-1, 3):
            ny, nx = my + dy, mx + dx2
            if 0 <= ny < H and 0 <= nx < W:
                grid[ny][nx] = "dark_hall"

    return grid


# ─── GAME OBJECTS ───────────────────────────────────────────────────
class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0

    def update(self, target_x, target_y):
        self.x = target_x - SCREEN_W // 2
        self.y = target_y - SCREEN_H // 2

    def apply(self, x, y):
        return x - self.x, y - self.y


class Particle:
    def __init__(self, x, y, color, dx=0, dy=0, life=30, size=3):
        self.x, self.y = x, y
        self.color = color
        self.dx, self.dy = dx, dy
        self.life = life
        self.max_life = life
        self.size = size

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.dy += 0.1  # gravity
        self.life -= 1

    def draw(self, surface, cam):
        if self.life <= 0:
            return
        sx, sy = cam.apply(self.x, self.y)
        alpha = max(0, min(255, int(255 * self.life / self.max_life)))
        r, g, b = self.color[:3]
        sz = max(1, int(self.size * self.life / self.max_life))
        pygame.draw.circle(surface, (r, g, b), (int(sx), int(sy)), sz)


class Coin:
    def __init__(self, x, y, value=1):
        self.x, self.y = x, y
        self.value = value
        self.frame = random.randint(0, 7)
        self.timer = 0
        self.collected = False
        self.bob = 0

    def update(self):
        self.timer += 1
        if self.timer % 6 == 0:
            self.frame = (self.frame + 1) % 8
        self.bob = math.sin(self.timer * 0.1) * 2

    def draw(self, surface, cam):
        if self.collected:
            return
        sx, sy = cam.apply(self.x, self.y + self.bob)
        sprite = make_coin_sprite(self.frame)
        surface.blit(sprite, (sx - 10, sy - 10))


class DroppedIngredient:
    def __init__(self, x, y, ing_type):
        self.x, self.y = x, y
        self.ing_type = ing_type
        self.collected = False
        self.bob_timer = 0

    def update(self):
        self.bob_timer += 1

    def draw(self, surface, cam):
        if self.collected:
            return
        sx, sy = cam.apply(self.x, self.y + math.sin(self.bob_timer * 0.05) * 3)
        sprite = make_ingredient_sprite(self.ing_type)
        surface.blit(sprite, (sx - 14, sy - 14))
        # Glow
        glow_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (255, 255, 200, 40), (20, 20), 18)
        surface.blit(glow_surf, (sx - 20, sy - 20))


class SwordSwing:
    """Animated sword swing effect."""
    def __init__(self, player_x, player_y, direction, sword_id):
        self.px, self.py = player_x, player_y
        self.direction = direction
        self.sword_id = sword_id
        self.frame = 0
        self.max_frames = 12
        self.active = True
        self.hit_entities = set()

    def get_hitbox(self):
        """Return the hitbox rect for the current swing frame."""
        progress = self.frame / self.max_frames
        reach = 40
        if self.direction == 0:   # down
            return pygame.Rect(self.px - 25, self.py + 10, 50, reach)
        elif self.direction == 2:  # up
            return pygame.Rect(self.px - 25, self.py - reach - 10, 50, reach)
        elif self.direction == 1:  # left
            return pygame.Rect(self.px - reach - 10, self.py - 25, reach, 50)
        else:  # right
            return pygame.Rect(self.px + 10, self.py - 25, reach, 50)

    def update(self):
        self.frame += 1
        if self.frame >= self.max_frames:
            self.active = False

    def draw(self, surface, cam):
        if not self.active:
            return
        progress = self.frame / self.max_frames
        sw_data = SWORDS[self.sword_id]
        color = sw_data["color"]

        # Swing arc
        angle_start = -60
        angle_end = 60
        current_angle = angle_start + (angle_end - angle_start) * progress

        cx, cy = cam.apply(self.px, self.py)
        reach = 35

        if self.direction == 0:  # down
            base_angle = 90
        elif self.direction == 2:  # up
            base_angle = 270
        elif self.direction == 1:  # left
            base_angle = 180
        else:  # right
            base_angle = 0

        angle = math.radians(base_angle + current_angle)

        # Sword line
        ex = cx + math.cos(angle) * reach
        ey = cy + math.sin(angle) * reach
        # Trail
        for i in range(3):
            t_angle = math.radians(base_angle + current_angle - (i + 1) * 15)
            tx = cx + math.cos(t_angle) * reach * (1 - i * 0.1)
            ty = cy + math.sin(t_angle) * reach * (1 - i * 0.1)
            alpha = 200 - i * 60
            trail_surf = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            pygame.draw.line(trail_surf, (*color, alpha), (int(cx), int(cy)), (int(tx), int(ty)), 3 - i)
            surface.blit(trail_surf, (0, 0))

        # Main sword line
        pygame.draw.line(surface, highlight(color, 1.4), (int(cx), int(cy)), (int(ex), int(ey)), 4)
        pygame.draw.line(surface, WHITE, (int(cx), int(cy)), (int(ex), int(ey)), 2)

        # Tip sparkle
        sparkle_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
        alpha = int(255 * (1 - progress))
        pygame.draw.circle(sparkle_surf, (*color, alpha), (10, 10), 5)
        surface.blit(sparkle_surf, (int(ex) - 10, int(ey) - 10))

        # Fire/Ice effects
        if self.sword_id == 2:
            for _ in range(2):
                fx = ex + random.uniform(-8, 8)
                fy = ey + random.uniform(-8, 8)
                pygame.draw.circle(surface, (255, random.randint(100, 200), 0),
                                   (int(fx), int(fy)), random.randint(2, 4))
        elif self.sword_id == 3:
            for _ in range(2):
                fx = ex + random.uniform(-8, 8)
                fy = ey + random.uniform(-8, 8)
                pygame.draw.circle(surface, (150, 220, 255),
                                   (int(fx), int(fy)), random.randint(2, 4))
        elif self.sword_id == 4:
            for _ in range(3):
                fx = ex + random.uniform(-10, 10)
                fy = ey + random.uniform(-10, 10)
                pygame.draw.circle(surface, (220, 180, 255),
                                   (int(fx), int(fy)), random.randint(2, 5))


class Player:
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.speed = 3.0
        self.hp = 100
        self.max_hp = 100
        self.coins = 0
        self.direction = 0  # 0=down,1=left,2=up,3=right
        self.frame = 0
        self.frame_timer = 0
        self.moving = False
        self.sword_id = 0
        self.sword_level = 0
        self.attacking = False
        self.attack_cooldown = 0
        self.swing = None
        self.ingredients = [False, False, False, False]
        self.team = []  # survivor indices
        self.has_antidote = False
        self.invuln = 0

    def get_damage(self):
        base = SWORDS[self.sword_id]["damage"]
        upgrade_bonus = self.sword_level * SWORD_UPGRADES[self.sword_id]["dmg_per"]
        # Team damage bonus
        team_bonus = len(self.team) * 2
        return base + upgrade_bonus + team_bonus

    def attack(self):
        if self.attack_cooldown <= 0:
            spd = SWORDS[self.sword_id]["speed"]
            self.attacking = True
            self.attack_cooldown = int(20 / spd)
            self.swing = SwordSwing(self.x, self.y, self.direction, self.sword_id)

    def take_damage(self, dmg):
        if self.invuln > 0:
            return
        self.hp -= dmg
        self.invuln = 30
        if self.hp < 0:
            self.hp = 0

    def update(self, keys, walls):
        self.moving = False
        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -self.speed
            self.direction = 2
            self.moving = True
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = self.speed
            self.direction = 0
            self.moving = True
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -self.speed
            self.direction = 1
            self.moving = True
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = self.speed
            self.direction = 3
            self.moving = True

        # Normalize diagonal
        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707

        # Collision check
        new_x = self.x + dx
        new_y = self.y + dy
        player_rect = pygame.Rect(new_x - 12, new_y - 12, 24, 24)

        can_move_x = True
        can_move_y = True
        test_x = pygame.Rect(new_x - 12, self.y - 12, 24, 24)
        test_y = pygame.Rect(self.x - 12, new_y - 12, 24, 24)

        for wall in walls:
            if test_x.colliderect(wall):
                can_move_x = False
            if test_y.colliderect(wall):
                can_move_y = False

        if can_move_x:
            self.x = new_x
        if can_move_y:
            self.y = new_y

        # Animation
        if self.moving:
            self.frame_timer += 1
            if self.frame_timer >= 8:
                self.frame = (self.frame + 1) % 4
                self.frame_timer = 0
        else:
            self.frame = 0
            self.frame_timer = 0

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.swing:
            self.swing.px, self.swing.py = self.x, self.y
            self.swing.update()
            if not self.swing.active:
                self.swing = None

        if self.invuln > 0:
            self.invuln -= 1

    def draw(self, surface, cam):
        sx, sy = cam.apply(self.x, self.y)
        # Blink when invuln
        if self.invuln > 0 and self.invuln % 4 < 2:
            return
        sprite = make_player_sprite(self.direction, self.frame, self.sword_id)
        surface.blit(sprite, (sx - 24, sy - 30))

        if self.swing:
            self.swing.draw(surface, cam)

    def get_rect(self):
        return pygame.Rect(self.x - 16, self.y - 16, 32, 32)


class Zombie:
    def __init__(self, x, y, ztype=0):
        self.x, self.y = float(x), float(y)
        self.ztype = ztype
        self.frame = random.randint(0, 3)
        self.frame_timer = 0
        self.direction = 0

        if ztype == 0:
            self.hp = 30
            self.max_hp = 30
            self.speed = 1.0
            self.damage = 8
            self.coin_drop = random.randint(1, 3)
        elif ztype == 1:  # fast
            self.hp = 20
            self.max_hp = 20
            self.speed = 2.0
            self.damage = 6
            self.coin_drop = random.randint(2, 4)
        else:  # tank
            self.hp = 80
            self.max_hp = 80
            self.speed = 0.6
            self.damage = 15
            self.coin_drop = random.randint(5, 10)

        self.attack_cd = 0
        self.alive = True
        self.death_timer = 0
        self.knockback_x = 0
        self.knockback_y = 0

    def update(self, player_x, player_y, walls):
        if not self.alive:
            self.death_timer += 1
            return

        # Apply knockback
        if abs(self.knockback_x) > 0.5 or abs(self.knockback_y) > 0.5:
            self.x += self.knockback_x
            self.y += self.knockback_y
            self.knockback_x *= 0.7
            self.knockback_y *= 0.7
            return

        # Move toward player
        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.sqrt(dx * dx + dy * dy) or 1

        if dist < 400:  # aggro range
            mx = (dx / dist) * self.speed
            my = (dy / dist) * self.speed

            # Set direction
            if abs(dx) > abs(dy):
                self.direction = 3 if dx > 0 else 1
            else:
                self.direction = 0 if dy > 0 else 2

            new_x = self.x + mx
            new_y = self.y + my
            can_x, can_y = True, True
            z_rect_x = pygame.Rect(new_x - 12, self.y - 12, 24, 24)
            z_rect_y = pygame.Rect(self.x - 12, new_y - 12, 24, 24)
            for w in walls:
                if z_rect_x.colliderect(w):
                    can_x = False
                if z_rect_y.colliderect(w):
                    can_y = False
            if can_x:
                self.x = new_x
            if can_y:
                self.y = new_y

        # Animation
        self.frame_timer += 1
        if self.frame_timer >= 12:
            self.frame = (self.frame + 1) % 4
            self.frame_timer = 0

        if self.attack_cd > 0:
            self.attack_cd -= 1

    def take_hit(self, dmg, source_x, source_y):
        self.hp -= dmg
        dx = self.x - source_x
        dy = self.y - source_y
        dist = math.sqrt(dx * dx + dy * dy) or 1
        self.knockback_x = (dx / dist) * 8
        self.knockback_y = (dy / dist) * 8
        if self.hp <= 0:
            self.alive = False

    def try_attack(self, player):
        if self.attack_cd <= 0 and self.alive:
            dist = math.sqrt((self.x - player.x) ** 2 + (self.y - player.y) ** 2)
            if dist < 35:
                player.take_damage(self.damage)
                self.attack_cd = 40
                return True
        return False

    def draw(self, surface, cam):
        sx, sy = cam.apply(self.x, self.y)
        if not self.alive:
            if self.death_timer < 30:
                alpha = max(0, 255 - self.death_timer * 8)
                sprite = make_zombie_sprite(self.ztype, self.frame, self.direction)
                sprite.set_alpha(alpha)
                surface.blit(sprite, (sx - 24, sy - 30))
            return
        sprite = make_zombie_sprite(self.ztype, self.frame, self.direction)
        surface.blit(sprite, (sx - 24, sy - 30))
        # HP bar
        if self.hp < self.max_hp:
            bar_w = 30
            bar_h = 4
            ratio = self.hp / self.max_hp
            pygame.draw.rect(surface, DARK_RED, (sx - bar_w // 2, sy - 34, bar_w, bar_h))
            pygame.draw.rect(surface, GREEN, (sx - bar_w // 2, sy - 34, int(bar_w * ratio), bar_h))

    def get_rect(self):
        sz = 32 if self.ztype != 2 else 40
        return pygame.Rect(self.x - sz // 2, self.y - sz // 2, sz, sz)


class Survivor:
    def __init__(self, x, y, variant, name):
        self.x, self.y = float(x), float(y)
        self.variant = variant
        self.name = name
        self.rescued = False
        self.following = False
        self.dialog_shown = False
        self.attack_cd = 0
        self.attack_damage = 12

    def draw(self, surface, cam):
        if self.rescued and not self.following:
            return
        sx, sy = cam.apply(self.x, self.y)
        sprite = make_survivor_sprite(self.variant)
        surface.blit(sprite, (sx - 24, sy - 30))
        # Name tag
        name_surf = font_sm.render(self.name, True, WHITE)
        surface.blit(name_surf, (sx - name_surf.get_width() // 2, sy - 42))
        if not self.rescued:
            # Help indicator
            help_surf = font_sm.render("HELP!", True, RED)
            bob = math.sin(pygame.time.get_ticks() * 0.005) * 3
            surface.blit(help_surf, (sx - help_surf.get_width() // 2, sy - 55 + bob))

    def update(self, player_x, player_y, zombies=None):
        if self.following:
            dx = player_x - self.x
            dy = player_y - self.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 60:
                self.x += (dx / dist) * 2.5
                self.y += (dy / dist) * 2.5

            # Fight nearby zombies
            if self.attack_cd > 0:
                self.attack_cd -= 1
            if zombies and self.attack_cd <= 0:
                for z in zombies:
                    if z.alive:
                        zd = math.sqrt((self.x - z.x) ** 2 + (self.y - z.y) ** 2)
                        if zd < 50:
                            z.take_hit(self.attack_damage, self.x, self.y)
                            self.attack_cd = 45
                            break


class ScientistNPC:
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.sprite = make_scientist_sprite()

    def draw(self, surface, cam):
        sx, sy = cam.apply(self.x, self.y)
        surface.blit(self.sprite, (sx - 24, sy - 30))
        name_surf = font_sm.render("Dr. Elara", True, CYAN)
        surface.blit(name_surf, (sx - name_surf.get_width() // 2, sy - 42))


class ChefNPC:
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self._idle_sprite = None
        self._cook_frames = []
        self.cooking = False
        self.cook_timer = 0
        self.cook_max = 0
        self.cook_frame = 0
        self.cook_frame_timer = 0
        self.meal_ready = None  # (main, dessert) tuple when done
        self._pending = None

    def start_cooking(self, main, dessert):
        self.cooking = True
        self.cook_timer = 180  # 3 seconds at 60fps
        self.cook_max = 180
        self.meal_ready = None
        self._pending = (main, dessert)
        self.cook_frame = 0
        self.cook_frame_timer = 0

    def update(self):
        if self.cooking:
            self.cook_timer -= 1
            self.cook_frame_timer += 1
            if self.cook_frame_timer >= 8:
                self.cook_frame = (self.cook_frame + 1) % 4
                self.cook_frame_timer = 0
            if self.cook_timer <= 0:
                self.cooking = False
                self.meal_ready = self._pending

    def _make_idle_sprite(self):
        s = create_surface(24, 24)
        # Chef hat
        draw_pixel_rect(s, 9, 0, 6, 4, WHITE, True)
        draw_pixel_rect(s, 8, 3, 8, 2, WHITE, True)
        # Head
        for hy in range(5, 9):
            for hx in range(9, 15):
                if (hx - 12) ** 2 + (hy - 6.5) ** 2 < 10:
                    c = LIGHT_SKIN if hy <= 6 else (SKIN if 10 <= hx <= 13 else DARK_SKIN)
                    px(s, hx, hy, c)
        px(s, 10, 6, (30, 30, 30))
        px(s, 13, 6, (30, 30, 30))
        # Mustache
        for mx in range(10, 14):
            px(s, mx, 8, DARK_BROWN)
        # White coat
        draw_pixel_rect(s, 7, 10, 10, 6, WHITE, True)
        draw_pixel_rect(s, 9, 12, 6, 4, (220, 220, 220), True)
        draw_pixel_rect(s, 5, 11, 2, 4, SKIN)
        draw_pixel_rect(s, 17, 11, 2, 4, SKIN)
        draw_pixel_rect(s, 8, 16, 8, 3, (40, 40, 60))
        draw_pixel_rect(s, 9, 19, 2, 2, (30, 30, 30))
        draw_pixel_rect(s, 13, 19, 2, 2, (30, 30, 30))
        return pygame.transform.scale(s, (48, 48))

    def _make_cook_frame(self, frame):
        """Animated cooking: arms move, steam rises, body bobs."""
        s = create_surface(24, 24)
        bob = 1 if frame % 2 == 1 else 0
        arm_l = -2 if frame in (0, 2) else 0
        arm_r = 2 if frame in (1, 3) else 0
        # Chef hat
        draw_pixel_rect(s, 9, 0 - bob, 6, 4, WHITE, True)
        draw_pixel_rect(s, 8, 3 - bob, 8, 2, WHITE, True)
        # Head
        for hy in range(5, 9):
            for hx in range(9, 15):
                if (hx - 12) ** 2 + (hy - 6.5) ** 2 < 10:
                    c2 = LIGHT_SKIN if hy <= 6 else (SKIN if 10 <= hx <= 13 else DARK_SKIN)
                    px(s, hx, hy - bob, c2)
        px(s, 10, 6 - bob, (30, 30, 30))
        px(s, 13, 6 - bob, (30, 30, 30))
        # Mustache
        for mx in range(10, 14):
            px(s, mx, 8 - bob, DARK_BROWN)
        # White coat
        draw_pixel_rect(s, 7, 10 - bob, 10, 6, WHITE, True)
        draw_pixel_rect(s, 9, 12 - bob, 6, 4, (220, 220, 220), True)
        # Animated arms - stirring motion
        draw_pixel_rect(s, 4 + arm_l, 10 - bob, 3, 5, SKIN)
        draw_pixel_rect(s, 17 + arm_r, 10 - bob, 3, 5, SKIN)
        # Frying pan in right hand
        draw_pixel_rect(s, 19 + arm_r, 9 - bob, 4, 2, GRAY)
        draw_pixel_rect(s, 19 + arm_r, 8 - bob, 4, 1, (50, 50, 55))
        # Spoon in left hand
        px(s, 4 + arm_l, 9 - bob, LIGHT_BROWN)
        px(s, 4 + arm_l, 8 - bob, LIGHT_BROWN)
        px(s, 4 + arm_l, 7 - bob, LIGHT_BROWN)
        # Food in pan
        if frame in (1, 2):
            px(s, 20 + arm_r, 7 - bob, ORANGE)
            px(s, 21 + arm_r, 7 - bob, (200, 120, 40))
        # Steam particles above pan
        steam_offsets = [(0, -3), (1, -5), (-1, -4), (2, -6)]
        steam_px = steam_offsets[frame]
        if 0 <= 20 + arm_r + steam_px[0] < 24 and 0 <= 7 - bob + steam_px[1] < 24:
            px(s, 20 + arm_r + steam_px[0], 7 - bob + steam_px[1], (200, 200, 200))
        if 0 <= 21 + arm_r + steam_px[0] < 24 and 0 <= 6 - bob + steam_px[1] < 24:
            px(s, 21 + arm_r + steam_px[0], 6 - bob + steam_px[1], (180, 180, 180))
        # Pants & shoes
        draw_pixel_rect(s, 8, 16 - bob, 8, 3, (40, 40, 60))
        draw_pixel_rect(s, 9, 19, 2, 2, (30, 30, 30))
        draw_pixel_rect(s, 13, 19, 2, 2, (30, 30, 30))
        return pygame.transform.scale(s, (48, 48))

    def draw(self, surface, cam):
        sx, sy = cam.apply(self.x, self.y)

        if self.cooking:
            # Build cook frames on first use
            if not self._cook_frames:
                self._cook_frames = [self._make_cook_frame(i) for i in range(4)]
            sprite = self._cook_frames[self.cook_frame]
            surface.blit(sprite, (sx - 24, sy - 30))

            # Countdown text
            secs_left = max(0, math.ceil(self.cook_timer / 60))
            count_text = font_lg.render(str(secs_left), True, YELLOW)
            surface.blit(count_text, (sx - count_text.get_width() // 2, sy - 70))

            # Cooking progress bar
            bar_w = 40
            bar_h = 6
            bar_x = sx - bar_w // 2
            bar_y = sy - 55
            progress = 1.0 - (self.cook_timer / self.cook_max) if self.cook_max > 0 else 1.0
            pygame.draw.rect(surface, DARK_GRAY, (bar_x, bar_y, bar_w, bar_h))
            bar_color = ORANGE if progress < 0.5 else (YELLOW if progress < 0.9 else GREEN)
            pygame.draw.rect(surface, bar_color, (bar_x, bar_y, int(bar_w * progress), bar_h))
            pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_w, bar_h), 1)

            # Floating steam particles
            t = pygame.time.get_ticks()
            for i in range(3):
                steam_x = sx + 10 + math.sin(t * 0.004 + i * 2) * 6
                steam_y = sy - 35 - (t * 0.03 + i * 8) % 20
                steam_alpha = max(0, 150 - int(((t * 0.03 + i * 8) % 20) * 7))
                steam_s = pygame.Surface((8, 8), pygame.SRCALPHA)
                pygame.draw.circle(steam_s, (220, 220, 220, steam_alpha), (4, 4), 3)
                surface.blit(steam_s, (int(steam_x) - 4, int(steam_y) - 4))

            # Label
            cook_label = font_sm.render("Cooking...", True, YELLOW)
            bob = math.sin(t * 0.008) * 2
            surface.blit(cook_label, (sx - cook_label.get_width() // 2, sy - 82 + bob))
        else:
            if self._idle_sprite is None:
                self._idle_sprite = self._make_idle_sprite()
            surface.blit(self._idle_sprite, (sx - 24, sy - 30))

        # Name tag always shown
        name_surf = font_sm.render("Chef Marco", True, ORANGE)
        surface.blit(name_surf, (sx - name_surf.get_width() // 2, sy - 42))


MEALS = {
    0: {"name": "Grilled Steak", "hp": 40, "desc": "Juicy grilled steak"},
    1: {"name": "Chicken Pasta", "hp": 35, "desc": "Creamy chicken pasta"},
    2: {"name": "Fish & Chips", "hp": 30, "desc": "Crispy battered fish"},
    3: {"name": "Veggie Stew", "hp": 25, "desc": "Hearty vegetable stew"},
    4: {"name": "Mushroom Risotto", "hp": 35, "desc": "Creamy mushroom risotto"},
    5: {"name": "Veggie Burger", "hp": 30, "desc": "Loaded plant-based burger"},
    6: {"name": "Tofu Stir Fry", "hp": 28, "desc": "Crispy tofu with veggies"},
    7: {"name": "Lentil Curry", "hp": 32, "desc": "Spicy red lentil curry"},
}

DESSERTS = {
    0: {"name": "Chocolate Cake", "hp": 20, "desc": "Rich chocolate cake"},
    1: {"name": "Apple Pie", "hp": 15, "desc": "Warm apple pie"},
    2: {"name": "Ice Cream", "hp": 10, "desc": "Vanilla ice cream"},
    3: {"name": "Fruit Salad", "hp": 12, "desc": "Fresh fruit mix"},
    4: {"name": "Mango Sorbet", "hp": 14, "desc": "Tropical mango sorbet"},
    5: {"name": "Berry Smoothie Bowl", "hp": 16, "desc": "Mixed berry bowl"},
    6: {"name": "Coconut Pudding", "hp": 13, "desc": "Creamy coconut pudding"},
}


class ButlerNPC:
    """Butler walks to player to deliver the food from chef."""
    def __init__(self, x, y):
        self.home_x, self.home_y = float(x), float(y)
        self.x, self.y = float(x), float(y)
        self.speed = 2.0
        self._sprite = None
        self.state = "idle"  # idle, delivering, returning
        self.delivery = None  # (main_name, dessert_name, total_hp)
        self.target_x = 0
        self.target_y = 0

    def give_delivery(self, main_name, dessert_name, total_hp, player_x, player_y):
        self.delivery = (main_name, dessert_name, total_hp)
        self.target_x = player_x
        self.target_y = player_y
        self.state = "delivering"

    def _make_sprite(self):
        s = create_surface(24, 24)
        # Bowler hat
        draw_pixel_rect(s, 8, 1, 8, 2, (20, 20, 20), True)
        draw_pixel_rect(s, 10, 0, 4, 2, (20, 20, 20), True)
        # Head
        for hy in range(4, 9):
            for hx in range(9, 15):
                if (hx - 12) ** 2 + (hy - 6) ** 2 < 10:
                    c = LIGHT_SKIN if hy <= 5 else (SKIN if 10 <= hx <= 13 else DARK_SKIN)
                    px(s, hx, hy, c)
        px(s, 10, 6, (30, 30, 30))
        px(s, 13, 6, (30, 30, 30))
        px(s, 11, 7, (180, 80, 80))
        px(s, 12, 7, (180, 80, 80))
        # Black suit
        draw_pixel_rect(s, 7, 10, 10, 6, (25, 25, 30), True)
        # White shirt front
        draw_pixel_rect(s, 10, 10, 4, 5, WHITE, True)
        # Bow tie
        px(s, 11, 10, RED)
        px(s, 12, 10, RED)
        # Arms
        draw_pixel_rect(s, 5, 11, 2, 4, (25, 25, 30))
        draw_pixel_rect(s, 17, 11, 2, 4, (25, 25, 30))
        # White gloved hands
        px(s, 5, 15, WHITE)
        px(s, 17, 15, WHITE)
        # Pants & shoes
        draw_pixel_rect(s, 8, 16, 8, 3, (30, 30, 35))
        draw_pixel_rect(s, 9, 19, 2, 2, (15, 15, 15))
        draw_pixel_rect(s, 13, 19, 2, 2, (15, 15, 15))
        # Tray (when delivering)
        if self.state == "delivering":
            draw_pixel_rect(s, 17, 8, 6, 2, (180, 180, 180), True)
            draw_pixel_rect(s, 18, 5, 4, 3, (200, 100, 50), True)  # plate with food
        return pygame.transform.scale(s, (48, 48))

    def update(self, player_x, player_y):
        if self.state == "delivering":
            self.target_x = player_x
            self.target_y = player_y
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < 40:
                self.state = "arrived"
            elif dist > 0:
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed
        elif self.state == "returning":
            dx = self.home_x - self.x
            dy = self.home_y - self.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < 5:
                self.x, self.y = self.home_x, self.home_y
                self.state = "idle"
            elif dist > 0:
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed

    def draw(self, surface, cam):
        # Regenerate sprite based on state
        self._sprite = self._make_sprite()
        sx, sy = cam.apply(self.x, self.y)
        surface.blit(self._sprite, (sx - 24, sy - 30))
        name_surf = font_sm.render("Butler James", True, (180, 180, 200))
        surface.blit(name_surf, (sx - name_surf.get_width() // 2, sy - 42))
        if self.state == "delivering":
            label = font_sm.render("Delivering...", True, YELLOW)
            surface.blit(label, (sx - label.get_width() // 2, sy - 55))


class TrainingDummy:
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.shake = 0
        self.damage_shown = 0
        self.damage_timer = 0

    def take_hit(self, dmg):
        self.shake = 10
        self.damage_shown = dmg
        self.damage_timer = 60

    def update(self):
        if self.shake > 0:
            self.shake -= 1
        if self.damage_timer > 0:
            self.damage_timer -= 1

    def draw(self, surface, cam):
        sx, sy = cam.apply(self.x, self.y)
        off = random.randint(-2, 2) if self.shake > 0 else 0
        # Wooden post
        pygame.draw.rect(surface, BROWN, (sx - 4 + off, sy - 10, 8, 30))
        pygame.draw.rect(surface, DARK_BROWN, (sx - 4 + off, sy - 10, 8, 30), 1)
        # Cross beam (arms)
        pygame.draw.rect(surface, BROWN, (sx - 16 + off, sy - 5, 32, 6))
        pygame.draw.rect(surface, DARK_BROWN, (sx - 16 + off, sy - 5, 32, 6), 1)
        # Sack head
        pygame.draw.circle(surface, (180, 160, 120), (sx + off, sy - 18), 10)
        pygame.draw.circle(surface, (150, 130, 90), (sx + off, sy - 18), 10, 1)
        # X eyes
        for ex in (-3, 2):
            pygame.draw.line(surface, DARK_BROWN,
                             (sx + ex + off, sy - 21), (sx + ex + 3 + off, sy - 18), 2)
            pygame.draw.line(surface, DARK_BROWN,
                             (sx + ex + 3 + off, sy - 21), (sx + ex + off, sy - 18), 2)
        # Damage popup
        if self.damage_timer > 0:
            dmg_text = font_md.render(str(self.damage_shown), True, YELLOW)
            y_off = -(60 - self.damage_timer) * 0.5
            surface.blit(dmg_text, (sx - dmg_text.get_width() // 2, sy - 40 + y_off))

    def get_rect(self):
        return pygame.Rect(self.x - 16, self.y - 20, 32, 40)


class BossZombie:
    """Giant zombie boss at the end of the dark hall. 12000 HP."""
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.hp = 12000
        self.max_hp = 12000
        self.damage = 25
        self.speed = 0.8
        self.alive = True
        self.frame = 0
        self.frame_timer = 0
        self.attack_cd = 0
        self.phase = 0  # 0=normal, 1=enraged (<50%), 2=desperate (<20%)
        self.shake = 0

    def update(self, player_x, player_y):
        if not self.alive:
            return
        # Phase check
        ratio = self.hp / self.max_hp
        if ratio < 0.2:
            self.phase = 2
            self.speed = 1.5
            self.damage = 35
        elif ratio < 0.5:
            self.phase = 1
            self.speed = 1.2
            self.damage = 30

        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.sqrt(dx * dx + dy * dy) or 1
        self.x += (dx / dist) * self.speed
        self.y += (dy / dist) * self.speed

        self.frame_timer += 1
        if self.frame_timer >= 10:
            self.frame = (self.frame + 1) % 4
            self.frame_timer = 0
        if self.attack_cd > 0:
            self.attack_cd -= 1
        if self.shake > 0:
            self.shake -= 1

    def take_hit(self, dmg, sx, sy):
        self.hp -= dmg
        self.shake = 8
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def try_attack(self, player):
        if self.attack_cd <= 0 and self.alive:
            dist = math.sqrt((self.x - player.x) ** 2 + (self.y - player.y) ** 2)
            if dist < 50:
                player.take_damage(self.damage)
                self.attack_cd = 30
                return True
        return False

    def _make_sprite(self, frame=0):
        """Detailed pixel-art giant zombie boss. 32x32 base scaled to 96x96."""
        s = create_surface(32, 32)
        # Phase-based colors
        if self.phase == 2:
            skin = (140, 40, 40)
            skin_hi = (180, 60, 60)
            skin_sh = (100, 25, 25)
        elif self.phase == 1:
            skin = (120, 100, 60)
            skin_hi = (150, 130, 80)
            skin_sh = (80, 65, 35)
        else:
            skin = (80, 130, 60)
            skin_hi = (110, 160, 85)
            skin_sh = (50, 90, 35)

        bob = 1 if frame % 2 == 1 else 0
        arm_swing = 2 if frame in (1, 3) else -2

        # Ground shadow
        for dx in range(-8, 9):
            for dy in range(-1, 2):
                if dx * dx + dy * dy * 6 < 70:
                    px(s, 16 + dx, 30 + dy, (0, 0, 0, 50))

        # Massive boots
        draw_pixel_rect(s, 8, 27 - bob, 5, 4, (40, 25, 15), True)
        draw_pixel_rect(s, 19, 27 - bob, 5, 4, (40, 25, 15), True)
        # Torn pants
        for ty in range(3):
            for tx in range(14):
                if random.random() > 0.1:
                    px(s, 9 + tx, 23 + ty - bob, (45, 40, 35))
        # Massive torso (wider than normal)
        for ty in range(8):
            for tx in range(16):
                c = skin_hi if ty < 2 else (skin if 2 < tx < 14 else skin_sh)
                if tx == 0 or tx == 15:
                    c = skin_sh
                px(s, 8 + tx, 13 + ty - bob, c)
        # Torn shirt remnants
        for tx in range(12):
            if random.random() > 0.4:
                c = (60, 50, 40) if random.random() > 0.3 else (50, 40, 30)
                px(s, 10 + tx, 14 - bob, c)
                if random.random() > 0.5:
                    px(s, 10 + tx, 15 - bob, c)
        # Exposed ribs/wounds
        px(s, 12, 17 - bob, DARK_RED)
        px(s, 13, 17 - bob, DARK_RED)
        px(s, 18, 16 - bob, DARK_RED)
        px(s, 19, 18 - bob, (100, 20, 20))
        # Giant arms (reaching, zombie style)
        draw_pixel_rect(s, 3 + arm_swing, 12 - bob, 5, 10, skin, True)
        draw_pixel_rect(s, 24 - arm_swing, 13 - bob, 5, 10, skin, True)
        px(s, 3 + arm_swing, 12 - bob, skin_hi)
        px(s, 24 - arm_swing, 13 - bob, skin_hi)
        # Clawed fingers
        px(s, 2 + arm_swing, 22 - bob, skin_sh)
        px(s, 3 + arm_swing, 22 - bob, skin_sh)
        px(s, 4 + arm_swing, 22 - bob, skin_sh)
        px(s, 25 - arm_swing, 23 - bob, skin_sh)
        px(s, 26 - arm_swing, 23 - bob, skin_sh)
        px(s, 27 - arm_swing, 23 - bob, skin_sh)

        # Giant head (pseudo-3D oval)
        for hy in range(2, 12):
            for hx in range(8, 24):
                if (hx - 16) ** 2 / 50 + (hy - 7) ** 2 / 22 < 1:
                    if hy <= 3:
                        c = skin_hi
                    elif hx <= 9:
                        c = skin_sh
                    elif hx >= 22:
                        c = skin_sh
                    else:
                        c = skin
                    px(s, hx, hy - bob, c)
        # Crown/horns (boss indicator)
        if self.phase == 2:
            # Demonic horns
            for i in range(4):
                px(s, 10 - i, 2 - i - bob, (100, 20, 20))
                px(s, 22 + i, 2 - i - bob, (100, 20, 20))
            px(s, 10, 1 - bob, (150, 30, 30))
            px(s, 22, 1 - bob, (150, 30, 30))
        else:
            # Jagged crown
            for hx in range(10, 22):
                px(s, hx, 1 - bob, (160, 140, 40))
            for hx in range(11, 21, 3):
                px(s, hx, 0 - bob, (180, 160, 50))

        # Glowing red eyes (large, menacing)
        eye_glow = (255, 0, 0) if self.phase < 2 else (255, 80, 0)
        eye_inner = (255, 200, 200)
        # Left eye
        px(s, 11, 5 - bob, eye_glow)
        px(s, 12, 5 - bob, eye_glow)
        px(s, 11, 6 - bob, eye_glow)
        px(s, 12, 6 - bob, eye_inner)
        # Right eye
        px(s, 19, 5 - bob, eye_glow)
        px(s, 20, 5 - bob, eye_glow)
        px(s, 20, 6 - bob, eye_glow)
        px(s, 19, 6 - bob, eye_inner)
        # Gaping mouth with teeth
        for mx in range(12, 20):
            px(s, mx, 9 - bob, (40, 0, 0))
            px(s, mx, 10 - bob, (30, 0, 0))
        # Teeth (top)
        for mx in range(12, 20, 2):
            px(s, mx, 9 - bob, (220, 210, 180))
        # Teeth (bottom)
        for mx in range(13, 20, 2):
            px(s, mx, 10 - bob, (200, 190, 160))
        # Blood drip
        px(s, 14, 11 - bob, DARK_RED)
        px(s, 17, 11 - bob, DARK_RED)
        px(s, 14, 12 - bob, (100, 10, 10))
        # Scars/decay across face
        px(s, 21, 4 - bob, DARK_RED)
        px(s, 22, 5 - bob, DARK_RED)
        px(s, 10, 7 - bob, (60, 90, 40))
        px(s, 9, 8 - bob, (50, 80, 35))

        return pygame.transform.scale(s, (96, 96))

    def draw(self, surface, cam):
        if not self.alive:
            return
        sx, sy = cam.apply(self.x, self.y)
        off = random.randint(-3, 3) if self.shake > 0 else 0

        # Draw pixel art sprite
        sprite = self._make_sprite(self.frame)
        surface.blit(sprite, (sx - 48 + off, sy - 60))

        # Aura glow (phase-based)
        aura_s = pygame.Surface((120, 120), pygame.SRCALPHA)
        if self.phase == 2:
            pygame.draw.circle(aura_s, (255, 30, 30, 30), (60, 60), 55)
            pygame.draw.circle(aura_s, (255, 60, 0, 20), (60, 60), 45)
        elif self.phase == 1:
            pygame.draw.circle(aura_s, (200, 150, 30, 25), (60, 60), 50)
        else:
            pygame.draw.circle(aura_s, (60, 180, 60, 15), (60, 60), 45)
        surface.blit(aura_s, (sx - 60 + off, sy - 60))

        # HP bar (big, prominent)
        bar_w = 100
        bar_h = 10
        bar_x = sx - bar_w // 2
        bar_y = sy - 75
        ratio = self.hp / self.max_hp
        pygame.draw.rect(surface, (40, 0, 0), (bar_x, bar_y, bar_w, bar_h))
        bar_color = RED if self.phase == 0 else (ORANGE if self.phase == 1 else (255, 50, 50))
        pygame.draw.rect(surface, bar_color, (bar_x, bar_y, int(bar_w * ratio), bar_h))
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_w, bar_h), 1)
        # Boss name
        name = font_md.render("ZOMBIE KING", True, RED)
        surface.blit(name, (sx - name.get_width() // 2, bar_y - 20))
        hp_text = font_sm.render(f"{self.hp}/{self.max_hp}", True, WHITE)
        surface.blit(hp_text, (sx - hp_text.get_width() // 2, bar_y + bar_h + 2))

    def get_rect(self):
        return pygame.Rect(self.x - 20, self.y - 20, 40, 40)


def make_blacksmith_sprite():
    """Pixel art blacksmith with hammer and apron."""
    s = create_surface(24, 24)
    # Head
    for hy in range(3, 9):
        for hx in range(9, 15):
            if (hx - 12) ** 2 + (hy - 5.5) ** 2 < 11:
                c2 = LIGHT_SKIN if hy <= 4 else (SKIN if 10 <= hx <= 13 else DARK_SKIN)
                px(s, hx, hy, c2)
    # Bald with bandana
    for hx2 in range(9, 15):
        px(s, hx2, 3, RED)
        px(s, hx2, 2, DARK_RED)
    # Eyes
    px(s, 10, 5, (30, 30, 30))
    px(s, 13, 5, (30, 30, 30))
    # Beard
    for bx in range(10, 14):
        px(s, bx, 8, (60, 40, 20))
        px(s, bx, 9, (60, 40, 20))
    # Leather apron body
    draw_pixel_rect(s, 7, 10, 10, 7, (100, 60, 30), True)
    draw_pixel_rect(s, 8, 11, 8, 5, (120, 75, 35), True)
    # Arms (muscular)
    draw_pixel_rect(s, 4, 10, 3, 6, SKIN)
    draw_pixel_rect(s, 17, 10, 3, 6, SKIN)
    # Hammer in right hand
    draw_pixel_rect(s, 19, 7, 2, 6, BROWN)
    draw_pixel_rect(s, 18, 6, 4, 3, GRAY)
    # Pants & boots
    draw_pixel_rect(s, 8, 17, 8, 3, (50, 40, 30))
    draw_pixel_rect(s, 9, 20, 2, 2, (30, 25, 15))
    draw_pixel_rect(s, 13, 20, 2, 2, (30, 25, 15))
    return pygame.transform.scale(s, (48, 48))


# ─── GAME CLASS ─────────────────────────────────────────────────────
class Game:
    def __init__(self):
        self.state = "title"  # title, mansion, outside, shop, dialog, inventory, win, gameover
        self.camera = Camera()
        self.player = Player(0, 0)
        self.particles = []
        self.coins_world = []
        self.zombies = []
        self.survivors = []
        self.ingredients_world = []
        self.scientist = None
        self.swing = None
        self.dialog_text = ""
        self.dialog_options = []
        self.dialog_callback = None
        self.dialog_selection = 0
        self.mansion_map = create_mansion_map()
        self.outside_map = None
        self.mansion_walls = []
        self.outside_walls = []
        self.mansion_doors = []
        self.outside_spawned = False
        self.wave = 1
        self.zombies_killed = 0
        self.world_saved = False
        self.screen_shake = 0
        self.notification = ""
        self.notif_timer = 0
        self.heart_full = make_heart_sprite(True)
        self.heart_empty = make_heart_sprite(False)
        self.chef = None
        self.butler = None
        self.dummies = []
        self.bed_rects = []
        self.mountain_open = False
        self.boss = None
        self.in_boss_fight = False
        self.cutscene_timer = 0
        self.cutscene_active = False
        self.blacksmith_sprite = make_blacksmith_sprite()

        # Pre-cache player sprites
        self.player_sprites = {}
        for d in range(4):
            for f in range(4):
                self.player_sprites[(d, f)] = make_player_sprite(d, f)

        self._build_mansion_collision()
        self._place_mansion_player()

    def _build_mansion_collision(self):
        self.mansion_walls = []
        self.mansion_doors = []
        self.bed_rects = []
        self.dummy_positions = []
        self.chef_pos = None
        for y, row in enumerate(self.mansion_map):
            for x, ch in enumerate(row):
                px_x, px_y = x * TILE, y * TILE
                if ch == 'W' or ch == 'w':
                    self.mansion_walls.append(pygame.Rect(px_x, px_y, TILE, TILE))
                elif ch == 'D':
                    self.mansion_doors.append({"rect": pygame.Rect(px_x, px_y, TILE, TILE),
                                               "x": px_x, "y": px_y, "open": False})
                elif ch == 'b':
                    r = pygame.Rect(px_x, px_y, TILE, TILE)
                    self.mansion_walls.append(r)
                    self.bed_rects.append(r)
                elif ch in ('f', 'g'):
                    self.mansion_walls.append(pygame.Rect(px_x, px_y, TILE, TILE))
                elif ch == 'h':
                    self.dummy_positions.append((px_x + TILE // 2, px_y + TILE // 2))
                elif ch == 'k':
                    self.chef_pos = (px_x + TILE // 2, px_y + TILE // 2)
        # Butler stands in living room
        self.butler_pos = (5 * TILE + TILE // 2, 16 * TILE + TILE // 2)

    def _place_mansion_player(self):
        for y, row in enumerate(self.mansion_map):
            for x, ch in enumerate(row):
                if ch == 'P':
                    self.player.x = x * TILE + TILE // 2
                    self.player.y = y * TILE + TILE // 2
                    return
        # Default
        self.player.x = 8 * TILE
        self.player.y = 8 * TILE

    def _place_team_in_living_room(self):
        """Place rescued survivors on couches in the living room."""
        # Couch tile positions (matching 'c' in map: cols 2,6 at rows 14,16)
        couch_spots = [
            (2 * TILE + TILE // 2, 14 * TILE + TILE // 2),
            (6 * TILE + TILE // 2, 14 * TILE + TILE // 2),
            (2 * TILE + TILE // 2, 16 * TILE + TILE // 2),
            (6 * TILE + TILE // 2, 16 * TILE + TILE // 2),
        ]
        idx = 0
        for surv in self.survivors:
            if surv.rescued:
                surv.following = False  # sit down
                if idx < len(couch_spots):
                    surv.x, surv.y = couch_spots[idx]
                    idx += 1

    def _find_scientist_pos(self):
        for y, row in enumerate(self.mansion_map):
            for x, ch in enumerate(row):
                if ch == 'Z':
                    return x * TILE + TILE // 2, y * TILE + TILE // 2
        return 18 * TILE, 3 * TILE

    def _find_shop_pos(self):
        for y, row in enumerate(self.mansion_map):
            for x, ch in enumerate(row):
                if ch == 'S':
                    return x * TILE + TILE // 2, y * TILE + TILE // 2
        return 26 * TILE, 10 * TILE

    def _find_exits(self):
        # East wall exit: the open gap on the right side (column 29, rows 7-11)
        return [pygame.Rect(29 * TILE, 7 * TILE, TILE, 5 * TILE)]

    def start_game(self):
        self.state = "mansion"
        self.player = Player(0, 0)
        self._build_mansion_collision()
        self._place_mansion_player()
        sx, sy = self._find_scientist_pos()
        self.scientist = ScientistNPC(sx, sy)
        # Chef
        if self.chef_pos:
            self.chef = ChefNPC(*self.chef_pos)
        else:
            self.chef = None
        # Training dummies
        self.dummies = [TrainingDummy(dx, dy) for dx, dy in self.dummy_positions]
        # Butler
        self.butler = ButlerNPC(*self.butler_pos)
        self.zombies = []
        self.survivors = []
        self.coins_world = []
        self.ingredients_world = []
        self.particles = []
        self.outside_spawned = False
        self.wave = 1
        self.zombies_killed = 0
        self.world_saved = False

    def setup_outside(self):
        if self.outside_spawned:
            return
        self.outside_map = create_outside_map()
        self.outside_walls = []
        W, H = 200, 150
        for y in range(H):
            for x in range(W):
                if self.outside_map[y][x] == "wall":
                    self.outside_walls.append(pygame.Rect(x * TILE, y * TILE, TILE, TILE))
                elif self.outside_map[y][x] == "water":
                    self.outside_walls.append(pygame.Rect(x * TILE, y * TILE, TILE, TILE))
                elif self.outside_map[y][x] == "mountain":
                    self.outside_walls.append(pygame.Rect(x * TILE, y * TILE, TILE, TILE))
                elif self.outside_map[y][x] == "mountain_gate":
                    self.outside_walls.append(pygame.Rect(x * TILE, y * TILE, TILE, TILE))
        # Boundary walls
        for x in range(W):
            self.outside_walls.append(pygame.Rect(x * TILE, -TILE, TILE, TILE))
            self.outside_walls.append(pygame.Rect(x * TILE, H * TILE, TILE, TILE))
        for y in range(H):
            self.outside_walls.append(pygame.Rect(-TILE, y * TILE, TILE, TILE))
            self.outside_walls.append(pygame.Rect(W * TILE, y * TILE, TILE, TILE))

        # Spawn zombies (more for bigger map)
        self.zombies = []
        for _ in range(50):
            zx = random.randint(5, W - 5) * TILE
            zy = random.randint(8, H - 5) * TILE
            ztype = random.choices([0, 1, 2], weights=[60, 25, 15])[0]
            self.zombies.append(Zombie(zx, zy, ztype))

        # Spawn survivors spread across big map
        names = ["Marcus", "Lily", "Jake", "Sofia"]
        positions = [(25 * TILE, 100 * TILE), (150 * TILE, 30 * TILE),
                     (15 * TILE, 20 * TILE), (170 * TILE, 120 * TILE)]
        self.survivors = []
        for i, (sx, sy) in enumerate(positions):
            self.survivors.append(Survivor(sx, sy, i, names[i]))

        # Spawn ingredients spread across map
        ing_positions = [(35 * TILE, 105 * TILE), (90 * TILE, 135 * TILE),
                         (145 * TILE, 15 * TILE), (60 * TILE, 40 * TILE)]
        self.ingredients_world = []
        for i, (ix, iy) in enumerate(ing_positions):
            self.ingredients_world.append(DroppedIngredient(ix, iy, i))

        self.outside_spawned = True
        self.player.x = 31 * TILE
        self.player.y = 9 * TILE

    def spawn_zombie_wave(self):
        count = 5 + self.wave * 3
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(300, 600)
            zx = self.player.x + math.cos(angle) * dist
            zy = self.player.y + math.sin(angle) * dist
            zx = max(TILE * 2, min(198 * TILE, zx))
            zy = max(TILE * 2, min(148 * TILE, zy))
            ztype = random.choices([0, 1, 2], weights=[50, 30, 20])[0]
            self.zombies.append(Zombie(zx, zy, ztype))

    def notify(self, text):
        self.notification = text
        self.notif_timer = 180

    def open_dialog(self, text, options=None, callback=None):
        self.dialog_text = text
        self.dialog_options = options or ["OK"]
        self.dialog_callback = callback
        self.dialog_selection = 0
        self.state = "dialog"

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if self.state == "title":
                    if event.key == pygame.K_RETURN:
                        self.start_game()
                    elif event.key == pygame.K_ESCAPE:
                        return False

                elif self.state in ("mansion", "outside"):
                    if event.key == pygame.K_SPACE:
                        self.player.attack()
                    elif event.key == pygame.K_e:
                        self._interact()
                    elif event.key == pygame.K_TAB:
                        if self.state == "mansion":
                            self._open_shop()
                    elif event.key == pygame.K_i:
                        self._open_inventory()
                    elif event.key == pygame.K_1:
                        if self.state == "outside":
                            self.state = "mansion"
                            self._place_mansion_player()
                            self._place_team_in_living_room()
                            self.notify("Teleported home!")
                    elif event.key == pygame.K_ESCAPE:
                        self.state = "title"

                elif self.state == "dialog":
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.dialog_selection = (self.dialog_selection - 1) % len(self.dialog_options)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.dialog_selection = (self.dialog_selection + 1) % len(self.dialog_options)
                    elif event.key in (pygame.K_RETURN, pygame.K_e):
                        cb = self.dialog_callback
                        self.dialog_callback = None
                        if cb:
                            cb(self.dialog_selection)
                        # Only close dialog if callback didn't open a new one
                        if self.state == "dialog" and self.dialog_callback is None:
                            self.state = self._return_state
                    elif event.key == pygame.K_ESCAPE:
                        self.state = self._return_state

                elif self.state == "shop":
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.shop_selection = (self.shop_selection - 1) % self.shop_item_count
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.shop_selection = (self.shop_selection + 1) % self.shop_item_count
                    elif event.key in (pygame.K_RETURN, pygame.K_e):
                        self._shop_buy()
                    elif event.key in (pygame.K_ESCAPE, pygame.K_TAB):
                        self.state = "mansion"

                elif self.state == "inventory":
                    if event.key in (pygame.K_ESCAPE, pygame.K_i):
                        self.state = self._return_state

                elif self.state in ("win", "gameover"):
                    if event.key == pygame.K_RETURN:
                        self.state = "title"

        return True

    def _interact(self):
        pr = self.player.get_rect().inflate(30, 30)

        if self.state == "mansion":
            # Doors
            for door in self.mansion_doors:
                if pr.colliderect(door["rect"]):
                    door["open"] = not door["open"]
                    if door["open"]:
                        if door["rect"] in self.mansion_walls:
                            self.mansion_walls.remove(door["rect"])
                    else:
                        if door["rect"] not in self.mansion_walls:
                            self.mansion_walls.append(door["rect"])

            # Exit
            for ex_rect in self._find_exits():
                if pr.colliderect(ex_rect):
                    self.setup_outside()
                    self.state = "outside"
                    self.notify("The world is in chaos! Find survivors and ingredients!")
                    return

            # Scientist
            if self.scientist:
                dist = math.sqrt((self.player.x - self.scientist.x) ** 2 +
                                 (self.player.y - self.scientist.y) ** 2)
                if dist < 60:
                    self._talk_scientist()
                    return

            # Shop spot
            shop_x, shop_y = self._find_shop_pos()
            if math.sqrt((self.player.x - shop_x) ** 2 + (self.player.y - shop_y) ** 2) < 60:
                self._open_shop()
                return

            # Chef
            if self.chef:
                dist = math.sqrt((self.player.x - self.chef.x) ** 2 +
                                 (self.player.y - self.chef.y) ** 2)
                if dist < 60:
                    self._talk_chef()
                    return

            # Bed - rest to heal
            for bed_rect in self.bed_rects:
                if pr.colliderect(bed_rect.inflate(20, 20)):
                    self.player.hp = self.player.max_hp
                    self.notify("You rested in bed. HP fully restored!")
                    return

        elif self.state == "outside":
            # Survivors
            for surv in self.survivors:
                if not surv.rescued:
                    dist = math.sqrt((self.player.x - surv.x) ** 2 +
                                     (self.player.y - surv.y) ** 2)
                    if dist < 60:
                        surv.rescued = True
                        surv.following = True
                        self.player.team.append(surv.name)
                        self.notify(f"{surv.name} joined your team!")
                        return

            # Ingredients
            for ing in self.ingredients_world:
                if not ing.collected:
                    dist = math.sqrt((self.player.x - ing.x) ** 2 +
                                     (self.player.y - ing.y) ** 2)
                    if dist < 50:
                        ing.collected = True
                        self.player.ingredients[ing.ing_type] = True
                        self.notify(f"Found {INGREDIENT_NAMES[ing.ing_type]}!")
                        return

            # Return to mansion (walk to the entrance road near spawn)
            if self.player.x < 30 * TILE and 5 * TILE < self.player.y < 15 * TILE:
                self.state = "mansion"
                self._place_mansion_player()
                self._place_team_in_living_room()
                self.notify("Returned to mansion")

    def _talk_scientist(self):
        self._return_state = "mansion"
        has_all = all(self.player.ingredients)
        if self.player.has_antidote:
            self.open_dialog(
                "Dr. Elara: The antidote is ready!\n"
                "A mountain to the FAR EAST has opened!\n"
                "Go there with your team to face the\n"
                "Zombie King and save the world!",
                ["I'm ready!"])
        elif has_all:
            def make_antidote(sel):
                if sel == 0:
                    self.player.has_antidote = True
                    self.player.ingredients = [False, False, False, False]
                    self.notify("Dr. Elara created the ANTIDOTE!")
                    self.mountain_open = True
                    self.cutscene_active = True
                    self.cutscene_timer = 240  # 4 second cutscene
                    # Remove mountain gate walls so player can enter
                    self.outside_walls = [w for w in self.outside_walls
                                          if not (185 * TILE <= w.x <= 186 * TILE
                                                  and w.y == 81 * TILE)]
            self.open_dialog(
                "Dr. Elara: You found all the ingredients!\n"
                "I can create the antidote now.\n"
                "Shall I begin?",
                ["Yes, make the antidote!", "Not yet"],
                make_antidote)
        else:
            missing = [INGREDIENT_NAMES[i] for i in range(4) if not self.player.ingredients[i]]
            self.open_dialog(
                "Dr. Elara: I need these ingredients for the antidote:\n" +
                "\n".join(f"  {'[X]' if self.player.ingredients[i] else '[ ]'} {INGREDIENT_NAMES[i]}"
                          for i in range(4)) +
                "\n\nFind them in the outside world!",
                ["I'll find them!"])

    def _talk_chef(self):
        self._return_state = "mansion"
        self._chosen_main = None

        def pick_dessert(sel):
            main = self._chosen_main
            dessert = DESSERTS[sel]
            total_hp = MEALS[main]["hp"] + dessert["hp"]
            self.chef.start_cooking(MEALS[main]["name"], dessert["name"])
            self.notify(f"Chef Marco is cooking {MEALS[main]['name']} + {dessert['name']}!")
            # Butler will deliver once food is ready
            self._pending_meal = (MEALS[main]["name"], dessert["name"], total_hp)

        def pick_main(sel):
            self._chosen_main = sel
            self._return_state = "mansion"
            self.open_dialog(
                "Chef Marco: Excellent! Now pick your dessert:",
                [f"{DESSERTS[i]['name']} - {DESSERTS[i]['desc']} (+{DESSERTS[i]['hp']} HP)"
                 for i in range(len(DESSERTS))],
                pick_dessert)

        self.open_dialog(
            "Chef Marco: Welcome! Let me cook for you.\n"
            "Pick your main course:",
            [f"{MEALS[i]['name']} - {MEALS[i]['desc']} (+{MEALS[i]['hp']} HP)"
             for i in range(len(MEALS))],
            pick_main)

    def _open_shop(self):
        self.state = "shop"
        self.shop_selection = 0
        # Items: buy swords + upgrade current
        self.shop_items = []
        for sid, sdata in SWORDS.items():
            if sid > self.player.sword_id:
                self.shop_items.append(("buy", sid, sdata["name"], sdata["cost"]))
        # Upgrade current
        sup = SWORD_UPGRADES[self.player.sword_id]
        if self.player.sword_level < sup["max_level"]:
            cost = sup["cost_per"] * (self.player.sword_level + 1)
            self.shop_items.append(("upgrade", self.player.sword_id,
                                    f"Upgrade {SWORDS[self.player.sword_id]['name']} (Lv.{self.player.sword_level + 1})",
                                    cost))
        self.shop_item_count = max(1, len(self.shop_items))

    def _shop_buy(self):
        if not self.shop_items:
            return
        item = self.shop_items[self.shop_selection]
        action, sid, name, cost = item
        if self.player.coins >= cost:
            self.player.coins -= cost
            if action == "buy":
                self.player.sword_id = sid
                self.player.sword_level = 0
                self.notify(f"Bought {name}!")
            else:
                self.player.sword_level += 1
                self.notify(f"Upgraded to Lv.{self.player.sword_level}!")
            self._open_shop()  # refresh
        else:
            self.notify("Not enough coins!")

    def _open_inventory(self):
        self._return_state = self.state
        self.state = "inventory"

    def update(self):
        if self.state in ("mansion", "outside"):
            keys = pygame.key.get_pressed()
            walls = self.mansion_walls if self.state == "mansion" else self.outside_walls
            self.player.update(keys, walls)
            self.camera.update(self.player.x, self.player.y)

            # Auto-exit: walk past the east wall of mansion
            if self.state == "mansion":
                if self.player.x > 29 * TILE:
                    self.setup_outside()
                    self.state = "outside"
                    # Team follows you outside
                    for surv in self.survivors:
                        if surv.rescued:
                            surv.following = True
                            surv.x = self.player.x - 30
                            surv.y = self.player.y + random.randint(-20, 20)
                    self.notify("The world is in chaos! Find survivors and ingredients!")

            if self.state == "outside":
                # Update zombies
                for z in self.zombies:
                    z.update(self.player.x, self.player.y, self.outside_walls)
                    z.try_attack(self.player)

                # Sword hit detection
                if self.player.swing and self.player.swing.active:
                    hitbox = self.player.swing.get_hitbox()
                    for z in self.zombies:
                        if z.alive and id(z) not in self.player.swing.hit_entities:
                            if hitbox.colliderect(z.get_rect()):
                                z.take_hit(self.player.get_damage(), self.player.x, self.player.y)
                                self.player.swing.hit_entities.add(id(z))
                                self.screen_shake = 5
                                # Hit particles
                                for _ in range(5):
                                    self.particles.append(Particle(
                                        z.x, z.y, ZOMBIE_GREEN,
                                        random.uniform(-3, 3), random.uniform(-5, 0),
                                        20, 3))
                                if not z.alive:
                                    self.zombies_killed += 1
                                    # Drop coins
                                    for _ in range(z.coin_drop):
                                        cx = z.x + random.uniform(-20, 20)
                                        cy = z.y + random.uniform(-20, 20)
                                        self.coins_world.append(Coin(cx, cy))
                                    # Death particles
                                    for _ in range(12):
                                        self.particles.append(Particle(
                                            z.x, z.y,
                                            (random.randint(60, 140), random.randint(100, 180), random.randint(50, 100)),
                                            random.uniform(-4, 4), random.uniform(-6, 1),
                                            30, 4))
                                    # Chance to drop zombie blood
                                    if not self.player.ingredients[3] and random.random() < 0.05:
                                        self.ingredients_world.append(DroppedIngredient(z.x, z.y, 3))

                # Collect coins
                for coin in self.coins_world:
                    if not coin.collected:
                        dist = math.sqrt((self.player.x - coin.x) ** 2 + (self.player.y - coin.y) ** 2)
                        if dist < 30:
                            coin.collected = True
                            self.player.coins += coin.value
                            self.particles.append(Particle(coin.x, coin.y - 10, YELLOW, 0, -2, 20, 3))

                # Collect ingredients
                for ing in self.ingredients_world:
                    if not ing.collected:
                        dist = math.sqrt((self.player.x - ing.x) ** 2 + (self.player.y - ing.y) ** 2)
                        if dist < 35:
                            ing.collected = True
                            self.player.ingredients[ing.ing_type] = True
                            self.notify(f"Found {INGREDIENT_NAMES[ing.ing_type]}!")

                # Update survivors following
                for surv in self.survivors:
                    if surv.following:
                        surv.update(self.player.x, self.player.y, self.zombies)

                # Update coins & ingredients
                for coin in self.coins_world:
                    coin.update()
                for ing in self.ingredients_world:
                    ing.update()

                # Spawn new waves
                alive_count = sum(1 for z in self.zombies if z.alive)
                if alive_count < 3:
                    self.wave += 1
                    self.spawn_zombie_wave()
                    self.notify(f"Wave {self.wave} incoming!")

                # Check: enter mountain for boss fight
                if self.mountain_open and self.player.has_antidote:
                    if (183 * TILE < self.player.x < 188 * TILE and
                            80 * TILE < self.player.y < 92 * TILE):
                        if not self.in_boss_fight:
                            self.in_boss_fight = True
                            self.boss = BossZombie(186 * TILE, 88 * TILE)
                            self.notify("ZOMBIE KING APPEARS!")

                # Boss fight update
                if self.in_boss_fight and self.boss and self.boss.alive:
                    self.boss.update(self.player.x, self.player.y)
                    self.boss.try_attack(self.player)
                    # Sword hits boss
                    if self.player.swing and self.player.swing.active:
                        hitbox = self.player.swing.get_hitbox()
                        if id(self.boss) not in self.player.swing.hit_entities:
                            if hitbox.colliderect(self.boss.get_rect()):
                                self.boss.take_hit(self.player.get_damage(), self.player.x, self.player.y)
                                self.player.swing.hit_entities.add(id(self.boss))
                                self.screen_shake = 6
                                for _ in range(8):
                                    self.particles.append(Particle(
                                        self.boss.x, self.boss.y, RED,
                                        random.uniform(-4, 4), random.uniform(-6, 1), 25, 4))
                    # Team attacks boss too
                    for surv in self.survivors:
                        if surv.following and surv.attack_cd <= 0:
                            sd = math.sqrt((surv.x - self.boss.x) ** 2 + (surv.y - self.boss.y) ** 2)
                            if sd < 60:
                                self.boss.take_hit(surv.attack_damage, surv.x, surv.y)
                                surv.attack_cd = 45
                    # Boss defeated
                    if not self.boss.alive:
                        self.player.coins += 5000
                        self.notify("ZOMBIE KING DEFEATED! +5000 coins!")
                        self.state = "win"
                        self.world_saved = True

                # Old antidote intersection win removed — boss fight is the new win

                # Clean up dead zombies and collected coins
                self.zombies = [z for z in self.zombies if z.alive or z.death_timer < 60]
                self.coins_world = [c for c in self.coins_world if not c.collected]

            # Mansion: training dummy combat
            if self.state == "mansion":
                # Chef cooking update
                if self.chef:
                    self.chef.update()
                    if self.chef.meal_ready and hasattr(self, '_pending_meal'):
                        main_n, dessert_n, total_hp = self._pending_meal
                        self.butler.give_delivery(main_n, dessert_n, total_hp,
                                                  self.player.x, self.player.y)
                        self.chef.meal_ready = None
                        del self._pending_meal
                        self.notify("Butler James is bringing your food!")

                # Butler update
                if self.butler:
                    self.butler.update(self.player.x, self.player.y)
                    if self.butler.state == "arrived":
                        main_n, dessert_n, total_hp = self.butler.delivery
                        self.player.hp = min(self.player.max_hp, self.player.hp + total_hp)
                        self.notify(f"Served: {main_n} & {dessert_n}! +{total_hp} HP")
                        self.butler.delivery = None
                        self.butler.state = "returning"

                if self.player.swing and self.player.swing.active:
                    hitbox = self.player.swing.get_hitbox()
                    for dummy in self.dummies:
                        if id(dummy) not in self.player.swing.hit_entities:
                            if hitbox.colliderect(dummy.get_rect()):
                                dummy.take_hit(self.player.get_damage())
                                self.player.swing.hit_entities.add(id(dummy))
                                self.screen_shake = 3
                                for _ in range(3):
                                    self.particles.append(Particle(
                                        dummy.x, dummy.y, BROWN,
                                        random.uniform(-2, 2), random.uniform(-3, 0), 15, 2))
                for dummy in self.dummies:
                    dummy.update()

            # Particles
            for p in self.particles:
                p.update()
            self.particles = [p for p in self.particles if p.life > 0]

            # Screen shake
            if self.screen_shake > 0:
                self.screen_shake -= 1

            # Notification
            if self.notif_timer > 0:
                self.notif_timer -= 1

            # Game over
            if self.player.hp <= 0:
                self.state = "gameover"

    def draw(self):
        screen.fill(BLACK)

        if self.state == "title":
            self._draw_title()
        elif self.state in ("mansion", "outside"):
            self._draw_game()
        elif self.state == "shop":
            self._draw_game()
            self._draw_shop()
        elif self.state == "dialog":
            self._draw_game()
            self._draw_dialog()
        elif self.state == "inventory":
            self._draw_game()
            self._draw_inventory()
        elif self.state == "win":
            self._draw_win()
        elif self.state == "gameover":
            self._draw_gameover()

        pygame.display.flip()

        # Cutscene overlay (mountain opening preview)
        if self.cutscene_active:
            self.cutscene_timer -= 1
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))

            t = self.cutscene_timer
            progress = 1.0 - (t / 240)

            # Mountain silhouette
            mountain_color = (70, 60, 50)
            pts = [(SCREEN_W // 2 - 200, 450), (SCREEN_W // 2, 120),
                   (SCREEN_W // 2 + 200, 450)]
            pygame.draw.polygon(screen, mountain_color, pts)
            pygame.draw.polygon(screen, (90, 80, 65), pts, 3)

            # Gate opening animation
            gate_w = int(80 * progress)
            gate_x = SCREEN_W // 2 - gate_w // 2
            gate_y = 350
            # Dark interior
            pygame.draw.rect(screen, (20, 5, 10), (gate_x, gate_y, gate_w, 100))
            # Gate frame
            pygame.draw.rect(screen, DARK_RED, (gate_x, gate_y, gate_w, 100), 2)
            # Red glow inside
            glow_s = pygame.Surface((gate_w, 100), pygame.SRCALPHA)
            for gi in range(5):
                ga = max(0, 60 - gi * 12)
                pygame.draw.rect(glow_s, (180, 30, 30, ga),
                                 (gi * 3, gi * 3, gate_w - gi * 6, 100 - gi * 6))
            screen.blit(glow_s, (gate_x, gate_y))

            # Dark hall path
            if progress > 0.5:
                path_alpha = int(255 * (progress - 0.5) * 2)
                path_s = pygame.Surface((60, 200), pygame.SRCALPHA)
                path_s.fill((25, 10, 15, min(200, path_alpha)))
                screen.blit(path_s, (SCREEN_W // 2 - 30, 450))

            # Text
            if progress < 0.3:
                txt = font_lg.render("The mountain trembles...", True, (200, 150, 100))
            elif progress < 0.6:
                txt = font_lg.render("A dark passage reveals itself...", True, RED)
            else:
                txt = font_lg.render("The Zombie King awaits!", True, (255, 50, 50))
            txt.set_alpha(min(255, int(255 * min(1, progress * 3))))
            screen.blit(txt, (SCREEN_W // 2 - txt.get_width() // 2, 50))

            pygame.display.flip()

            if self.cutscene_timer <= 0:
                self.cutscene_active = False

    def _draw_title(self):
        # Animated background
        t = pygame.time.get_ticks() / 1000
        for y in range(0, SCREEN_H, TILE):
            for x in range(0, SCREEN_W, TILE):
                v = int(20 + 10 * math.sin(x * 0.02 + t) * math.cos(y * 0.02 + t))
                screen.fill((v, v + 10, v), (x, y, TILE, TILE))

        # Title
        title1 = font_title.render("PIXEL QUEST", True, YELLOW)
        title2 = font_lg.render("ZOMBIE APOCALYPSE", True, RED)
        screen.blit(title1, (SCREEN_W // 2 - title1.get_width() // 2, 140))
        screen.blit(title2, (SCREEN_W // 2 - title2.get_width() // 2, 210))

        # Decorative zombies
        for i in range(3):
            z_sprite = make_zombie_sprite(i, int(t * 2) % 4)
            screen.blit(z_sprite, (200 + i * 180, 280))

        # Player
        p_sprite = make_player_sprite(0, int(t * 3) % 4)
        screen.blit(p_sprite, (SCREEN_W // 2 - 24, 290))

        # Sword display
        for sid in range(5):
            sw_sprite = make_sword_sprite(sid)
            screen.blit(sw_sprite, (280 + sid * 80, 370))

        # Start prompt
        blink = int(t * 2) % 2
        if blink:
            start = font_md.render("Press ENTER to start", True, WHITE)
            screen.blit(start, (SCREEN_W // 2 - start.get_width() // 2, 440))

        # Controls
        controls = [
            "WASD/Arrows - Move    SPACE - Attack    E - Interact",
            "TAB - Shop    I - Inventory    1 - Teleport Home"
        ]
        for i, line in enumerate(controls):
            ctrl = font_sm.render(line, True, GRAY)
            screen.blit(ctrl, (SCREEN_W // 2 - ctrl.get_width() // 2, 500 + i * 20))

    def _draw_game(self):
        # Apply screen shake
        shake_x = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake else 0
        shake_y = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake else 0

        game_surface = pygame.Surface((SCREEN_W, SCREEN_H))
        game_surface.fill(BLACK)

        if self.state in ("mansion", "shop", "dialog", "inventory") and not (
                self.state in ("dialog", "inventory", "shop") and hasattr(self, '_return_state') and self._return_state == "outside"):
            self._draw_mansion(game_surface)
        else:
            self._draw_outside(game_surface)

        screen.blit(game_surface, (shake_x, shake_y))
        self._draw_hud()

    def _draw_mansion(self, surface):
        cam = self.camera
        tile_map = {
            'W': "wall", '.': "floor_wood", 'K': "floor_kitchen", 'T': "floor_tile",
            'C': "carpet", 'D': "door", 'L': "lab_floor", 'E': "mansion_exit",
            'P': "floor_wood", 'Z': "lab_floor", 'S': "floor_tile",
            'b': "bed", 'f': "stove", 'g': "bookshelf", 'h': "floor_tile",
            'k': "floor_kitchen", 't': "floor_tile", 'w': "wall", 'c': "couch",
        }

        # Draw tiles
        start_tx = max(0, int(cam.x // TILE) - 1)
        end_tx = min(30, int((cam.x + SCREEN_W) // TILE) + 2)
        start_ty = max(0, int(cam.y // TILE) - 1)
        end_ty = min(20, int((cam.y + SCREEN_H) // TILE) + 2)

        for ty in range(start_ty, end_ty):
            row = self.mansion_map[ty]
            for tx in range(start_tx, end_tx):
                if tx < len(row):
                    ch = row[tx]
                    tile_type = tile_map.get(ch, "floor_wood")
                    # Check if door is open
                    if ch == 'D':
                        for door in self.mansion_doors:
                            if door["x"] == tx * TILE and door["y"] == ty * TILE:
                                if door["open"]:
                                    tile_type = "floor_wood"
                                break
                    tile_surf = get_tile(tile_type)
                    sx, sy = cam.apply(tx * TILE, ty * TILE)
                    surface.blit(tile_surf, (sx, sy))

        # Room labels
        room_labels = [
            (2, 3, "Bedroom"), (8, 4, "Kitchen"), (17, 2, "Laboratory"),
            (24, 2, "Armory"), (14, 8, "Main Hall"), (4, 15, "Living Room"),
            (13, 15, "Training Room"), (24, 15, "Storage"),
        ]
        for lx, ly, name in room_labels:
            sx, sy = cam.apply(lx * TILE, ly * TILE)
            label = font_sm.render(name, True, (180, 180, 180))
            surface.blit(label, (sx, sy))

        # Scientist
        if self.scientist:
            self.scientist.draw(surface, cam)

        # Chef
        if self.chef:
            self.chef.draw(surface, cam)

        # Butler
        if self.butler:
            self.butler.draw(surface, cam)

        # Training dummies
        for dummy in self.dummies:
            dummy.draw(surface, cam)

        # Rescued survivors sitting in living room
        for surv in self.survivors:
            if surv.rescued and not surv.following:
                surv.draw(surface, cam)

        # Blacksmith shop indicator
        shop_x, shop_y = self._find_shop_pos()
        sx, sy = cam.apply(shop_x, shop_y)
        # Draw blacksmith sprite
        surface.blit(self.blacksmith_sprite, (sx - 24, sy - 30))
        bs_name = font_sm.render("Blacksmith", True, ORANGE)
        surface.blit(bs_name, (sx - bs_name.get_width() // 2, sy - 42))
        shop_label = font_sm.render("[FORGE - TAB]", True, YELLOW)
        bob = math.sin(pygame.time.get_ticks() * 0.003) * 3
        surface.blit(shop_label, (sx - shop_label.get_width() // 2, sy - 55 + bob))

        # Exit markers
        for ex_rect in self._find_exits():
            sx, sy = cam.apply(ex_rect.centerx, ex_rect.y)
            ex_label = font_sm.render("EXIT (walk through)", True, YELLOW)
            bob = math.sin(pygame.time.get_ticks() * 0.004) * 3
            surface.blit(ex_label, (sx - ex_label.get_width() // 2, sy - 20 + bob))

        # Player
        self.player.draw(surface, cam)

        # Particles
        for p in self.particles:
            p.draw(surface, cam)

    def _draw_outside(self, surface):
        cam = self.camera
        if not self.outside_map:
            return

        # Draw tiles
        start_tx = max(0, int(cam.x // TILE) - 1)
        end_tx = min(200, int((cam.x + SCREEN_W) // TILE) + 2)
        start_ty = max(0, int(cam.y // TILE) - 1)
        end_ty = min(150, int((cam.y + SCREEN_H) // TILE) + 2)

        for ty in range(start_ty, end_ty):
            for tx in range(start_tx, end_tx):
                tile_type = self.outside_map[ty][tx]
                tile_surf = get_tile(tile_type)
                sx, sy = cam.apply(tx * TILE, ty * TILE)
                surface.blit(tile_surf, (sx, sy))

        # Entrance back to mansion
        sx, sy = cam.apply(30 * TILE, 9 * TILE)
        ent_label = font_sm.render("MANSION [walk left]", True, CYAN)
        surface.blit(ent_label, (sx - ent_label.get_width() // 2, sy - 30))

        # Draw ingredients
        for ing in self.ingredients_world:
            ing.draw(surface, cam)

        # Draw coins
        for coin in self.coins_world:
            coin.draw(surface, cam)

        # Draw all entities sorted by Y for depth
        entities = []
        entities.append(("player", self.player.y, self.player))
        for z in self.zombies:
            if z.alive or z.death_timer < 60:
                entities.append(("zombie", z.y, z))
        for surv in self.survivors:
            if not surv.rescued or surv.following:
                entities.append(("survivor", surv.y, surv))

        entities.sort(key=lambda e: e[1])

        for etype, _, entity in entities:
            entity.draw(surface, cam)

        # Boss
        if self.boss and self.boss.alive:
            self.boss.draw(surface, cam)

        # Mountain label
        if self.mountain_open:
            mx_s, my_s = cam.apply(185 * TILE, 69 * TILE)
            m_label = font_lg.render("ZOMBIE KING'S LAIR", True, RED)
            bob = math.sin(pygame.time.get_ticks() * 0.003) * 3
            surface.blit(m_label, (mx_s - m_label.get_width() // 2, my_s + bob))
        elif self.player.has_antidote is False and self.outside_spawned:
            mx_s, my_s = cam.apply(185 * TILE, 69 * TILE)
            m_label = font_sm.render("Sealed Mountain", True, GRAY)
            surface.blit(m_label, (mx_s - m_label.get_width() // 2, my_s))

        # Particles
        for p in self.particles:
            p.draw(surface, cam)

        # Darkness overlay at edges (atmosphere)
        vignette = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        for i in range(20):
            alpha = max(0, 40 - i * 2)
            pygame.draw.rect(vignette, (0, 0, 0, alpha), (i * 2, i * 2,
                             SCREEN_W - i * 4, SCREEN_H - i * 4), 3)
        surface.blit(vignette, (0, 0))

    def _draw_hud(self):
        # Health bar
        hx, hy = 10, 10
        for i in range(5):
            hp_per_heart = self.player.max_hp / 5
            if self.player.hp >= (i + 1) * hp_per_heart:
                screen.blit(self.heart_full, (hx + i * 26, hy))
            else:
                screen.blit(self.heart_empty, (hx + i * 26, hy))

        # HP number
        hp_text = font_sm.render(f"{self.player.hp}/{self.player.max_hp}", True, WHITE)
        screen.blit(hp_text, (hx + 135, hy + 3))

        # Coins
        coin_sprite = make_coin_sprite(0)
        screen.blit(coin_sprite, (10, 38))
        coin_text = font_md.render(f"{self.player.coins}", True, YELLOW)
        screen.blit(coin_text, (35, 38))

        # Current sword
        sw_name = SWORDS[self.player.sword_id]["name"]
        if self.player.sword_level > 0:
            sw_name += f" +{self.player.sword_level}"
        sw_text = font_sm.render(f"Sword: {sw_name}", True, SWORDS[self.player.sword_id]["color"])
        screen.blit(sw_text, (10, 62))

        # Damage
        dmg_text = font_sm.render(f"DMG: {self.player.get_damage()}", True, (255, 150, 150))
        screen.blit(dmg_text, (10, 80))

        # Team count
        if self.player.team:
            team_text = font_sm.render(f"Team: {', '.join(self.player.team)}", True, CYAN)
            screen.blit(team_text, (10, 98))

        # Teleport hint (outside)
        if self.state == "outside" or (hasattr(self, '_return_state') and self._return_state == "outside"):
            tp_y = 116 if self.player.team else 98
            tp_text = font_sm.render("[1] Teleport Home", True, CYAN)
            screen.blit(tp_text, (10, tp_y))

        # Wave & kills (outside only)
        if self.state == "outside" or (hasattr(self, '_return_state') and self._return_state == "outside"):
            wave_text = font_md.render(f"Wave: {self.wave}  Kills: {self.zombies_killed}", True, RED)
            screen.blit(wave_text, (SCREEN_W - wave_text.get_width() - 10, 10))

        # Ingredients indicator
        ing_x = SCREEN_W - 150
        ing_y = 40
        ing_label = font_sm.render("Ingredients:", True, WHITE)
        screen.blit(ing_label, (ing_x, ing_y))
        for i in range(4):
            color = GREEN if self.player.ingredients[i] else DARK_GRAY
            icon = make_ingredient_sprite(i)
            if not self.player.ingredients[i]:
                icon.set_alpha(80)
            screen.blit(icon, (ing_x + i * 32, ing_y + 18))

        # Antidote indicator
        if self.player.has_antidote:
            ant_text = font_md.render("Go to the Mountain (Far East)!", True, GREEN)
            bob = math.sin(pygame.time.get_ticks() * 0.005) * 3
            screen.blit(ant_text, (SCREEN_W // 2 - ant_text.get_width() // 2, 10 + bob))
        if self.in_boss_fight and self.boss and self.boss.alive:
            boss_text = font_lg.render("BOSS FIGHT!", True, RED)
            screen.blit(boss_text, (SCREEN_W // 2 - boss_text.get_width() // 2, 10))

        # Notification
        if self.notif_timer > 0:
            alpha = min(255, self.notif_timer * 4)
            notif_surf = font_md.render(self.notification, True, WHITE)
            bg = pygame.Surface((notif_surf.get_width() + 20, 30), pygame.SRCALPHA)
            bg.fill((0, 0, 0, min(180, alpha)))
            screen.blit(bg, (SCREEN_W // 2 - bg.get_width() // 2, SCREEN_H - 60))
            notif_surf.set_alpha(alpha)
            screen.blit(notif_surf, (SCREEN_W // 2 - notif_surf.get_width() // 2, SCREEN_H - 55))

        # Minimap (outside)
        if self.state == "outside":
            self._draw_minimap()

    def _draw_minimap(self):
        mm_w, mm_h = 160, 120
        mm_x, mm_y = SCREEN_W - mm_w - 10, SCREEN_H - mm_h - 10
        mm_surf = pygame.Surface((mm_w, mm_h), pygame.SRCALPHA)
        mm_surf.fill((0, 0, 0, 150))

        # Tiles overview
        scale_x = mm_w / (200 * TILE)
        scale_y = mm_h / (150 * TILE)

        # Mansion marker (highlighted pulsing beacon) near spawn
        mx = int(30 * TILE * scale_x)
        my = int(9 * TILE * scale_y)
        t = pygame.time.get_ticks()
        pulse = 4 + int(2 * math.sin(t * 0.005))
        pygame.draw.rect(mm_surf, (0, 255, 255, 200), (mx - pulse, my - pulse, pulse * 2, pulse * 2))
        if int(t / 400) % 2:
            pygame.draw.rect(mm_surf, YELLOW, (mx - pulse - 1, my - pulse - 1, pulse * 2 + 2, pulse * 2 + 2), 1)

        # Player dot
        px_mm = int(self.player.x * scale_x)
        py_mm = int(self.player.y * scale_y)
        pygame.draw.circle(mm_surf, GREEN, (px_mm, py_mm), 3)

        # Zombies as red dots
        for z in self.zombies:
            if z.alive:
                zx = int(z.x * scale_x)
                zy = int(z.y * scale_y)
                pygame.draw.circle(mm_surf, RED, (zx, zy), 1)

        # Survivors as cyan dots
        for surv in self.survivors:
            if not surv.rescued:
                sx2 = int(surv.x * scale_x)
                sy2 = int(surv.y * scale_y)
                pygame.draw.circle(mm_surf, CYAN, (sx2, sy2), 2)

        # Ingredients as yellow dots
        for ing in self.ingredients_world:
            if not ing.collected:
                ix = int(ing.x * scale_x)
                iy = int(ing.y * scale_y)
                pygame.draw.circle(mm_surf, YELLOW, (ix, iy), 2)

        # Mountain marker (far east)
        mt_x = int(185 * TILE * scale_x)
        mt_y = int(75 * TILE * scale_y)
        # Draw mountain triangle
        pygame.draw.polygon(mm_surf, (90, 80, 70),
                            [(mt_x - 6, mt_y + 5), (mt_x, mt_y - 5), (mt_x + 6, mt_y + 5)])
        pygame.draw.polygon(mm_surf, (120, 110, 90),
                            [(mt_x - 6, mt_y + 5), (mt_x, mt_y - 5), (mt_x + 6, mt_y + 5)], 1)
        if self.mountain_open:
            # Pulsing red glow when open
            t = pygame.time.get_ticks()
            glow = 3 + int(2 * math.sin(t * 0.006))
            pygame.draw.circle(mm_surf, (255, 50, 50, 180), (mt_x, mt_y), glow)
        # Boss dot
        if self.boss and self.boss.alive:
            pygame.draw.circle(mm_surf, (255, 0, 0), (mt_x, mt_y + 3), 2)

        pygame.draw.rect(mm_surf, WHITE, (0, 0, mm_w, mm_h), 1)
        screen.blit(mm_surf, (mm_x, mm_y))

    def _draw_shop(self):
        # Dark overlay
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        # Shop panel
        panel_w, panel_h = 560, 500
        px2 = SCREEN_W // 2 - panel_w // 2
        py2 = SCREEN_H // 2 - panel_h // 2
        pygame.draw.rect(screen, (35, 25, 20), (px2, py2, panel_w, panel_h))
        pygame.draw.rect(screen, ORANGE, (px2, py2, panel_w, panel_h), 2)

        # Title
        title = font_lg.render("BLACKSMITH FORGE", True, ORANGE)
        screen.blit(title, (px2 + panel_w // 2 - title.get_width() // 2, py2 + 10))

        # Coins
        coin_text = font_md.render(f"Your Coins: {self.player.coins}", True, YELLOW)
        screen.blit(coin_text, (px2 + 20, py2 + 50))

        # Items (scrollable - show 7 at a time)
        visible = 7
        scroll_offset = max(0, self.shop_selection - visible + 1)
        for idx, item in enumerate(self.shop_items[scroll_offset:scroll_offset + visible]):
            real_i = idx + scroll_offset
            action, sid, name, cost = item
            y_pos = py2 + 90 + idx * 50
            selected = real_i == self.shop_selection

            # Selection highlight
            if selected:
                pygame.draw.rect(screen, (60, 50, 80), (px2 + 10, y_pos - 5, panel_w - 20, 45))
                pygame.draw.rect(screen, YELLOW, (px2 + 10, y_pos - 5, panel_w - 20, 45), 1)

            # Sword preview
            sw_sprite = make_sword_sprite(sid)
            screen.blit(sw_sprite, (px2 + 20, y_pos))

            # Name & stats
            color = WHITE if self.player.coins >= cost else RED
            name_text = font_md.render(name, True, color)
            screen.blit(name_text, (px2 + 60, y_pos))

            if action == "buy":
                stats = f"DMG: {SWORDS[sid]['damage']}  SPD: {SWORDS[sid]['speed']}x  Cost: {cost}"
            else:
                bonus = SWORD_UPGRADES[sid]["dmg_per"]
                stats = f"+{bonus} DMG  Cost: {cost}"
            stats_text = font_sm.render(stats, True, GRAY)
            screen.blit(stats_text, (px2 + 60, y_pos + 22))

        if not self.shop_items:
            no_items = font_md.render("All weapons purchased & maxed!", True, GREEN)
            screen.blit(no_items, (px2 + panel_w // 2 - no_items.get_width() // 2, py2 + 150))

        # Instructions
        inst = font_sm.render("ENTER - Forge    ESC/TAB - Close    \u2191\u2193 - Scroll", True, GRAY)
        screen.blit(inst, (px2 + panel_w // 2 - inst.get_width() // 2, py2 + panel_h - 30))

    def _draw_dialog(self):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))

        panel_w, panel_h = 600, 250
        px2 = SCREEN_W // 2 - panel_w // 2
        py2 = SCREEN_H // 2 - panel_h // 2
        pygame.draw.rect(screen, (20, 20, 35), (px2, py2, panel_w, panel_h))
        pygame.draw.rect(screen, CYAN, (px2, py2, panel_w, panel_h), 2)

        # Text
        lines = self.dialog_text.split('\n')
        for i, line in enumerate(lines):
            text = font_md.render(line, True, WHITE)
            screen.blit(text, (px2 + 20, py2 + 15 + i * 22))

        # Options
        opt_y = py2 + panel_h - 30 - len(self.dialog_options) * 28
        for i, opt in enumerate(self.dialog_options):
            selected = i == self.dialog_selection
            color = YELLOW if selected else GRAY
            prefix = "> " if selected else "  "
            opt_text = font_md.render(prefix + opt, True, color)
            screen.blit(opt_text, (px2 + 40, opt_y + i * 28))

    def _draw_inventory(self):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        panel_w, panel_h = 450, 350
        px2 = SCREEN_W // 2 - panel_w // 2
        py2 = SCREEN_H // 2 - panel_h // 2
        pygame.draw.rect(screen, (25, 20, 30), (px2, py2, panel_w, panel_h))
        pygame.draw.rect(screen, PURPLE, (px2, py2, panel_w, panel_h), 2)

        title = font_lg.render("INVENTORY", True, PURPLE)
        screen.blit(title, (px2 + panel_w // 2 - title.get_width() // 2, py2 + 10))

        # Sword
        sw = SWORDS[self.player.sword_id]
        sw_sprite = make_sword_sprite(self.player.sword_id)
        screen.blit(sw_sprite, (px2 + 20, py2 + 55))
        sw_name = sw["name"]
        if self.player.sword_level > 0:
            sw_name += f" +{self.player.sword_level}"
        screen.blit(font_md.render(sw_name, True, sw["color"]), (px2 + 60, py2 + 55))
        screen.blit(font_sm.render(f"Damage: {self.player.get_damage()}", True, WHITE), (px2 + 60, py2 + 78))

        # Ingredients
        screen.blit(font_md.render("Antidote Ingredients:", True, WHITE), (px2 + 20, py2 + 115))
        for i in range(4):
            y_pos = py2 + 140 + i * 35
            sprite = make_ingredient_sprite(i)
            if not self.player.ingredients[i]:
                sprite.set_alpha(50)
            screen.blit(sprite, (px2 + 25, y_pos))
            status = "[FOUND]" if self.player.ingredients[i] else "[MISSING]"
            color = GREEN if self.player.ingredients[i] else RED
            screen.blit(font_sm.render(f"{INGREDIENT_NAMES[i]} {status}", True, color), (px2 + 60, y_pos + 5))

        # Team
        if self.player.team:
            screen.blit(font_md.render(f"Team: {', '.join(self.player.team)}", True, CYAN), (px2 + 20, py2 + 290))
            screen.blit(font_sm.render(f"Team bonus: +{len(self.player.team) * 2} DMG", True, GREEN), (px2 + 20, py2 + 312))

        inst = font_sm.render("Press I or ESC to close", True, GRAY)
        screen.blit(inst, (px2 + panel_w // 2 - inst.get_width() // 2, py2 + panel_h - 25))

    def _draw_win(self):
        t = pygame.time.get_ticks() / 1000
        screen.fill((10, 30, 10))

        # Celebration particles
        for i in range(20):
            cx = int(SCREEN_W / 2 + math.sin(t * 2 + i * 0.5) * 300)
            cy = int(200 + math.cos(t * 3 + i * 0.7) * 100)
            color = [YELLOW, GREEN, CYAN, PURPLE, WHITE][i % 5]
            pygame.draw.circle(screen, color, (cx, cy), random.randint(2, 5))

        title = font_title.render("WORLD SAVED!", True, GREEN)
        screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 100))

        sub = font_lg.render("The antidote worked!", True, WHITE)
        screen.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, 180))

        # Stats
        stats = [
            f"Zombies Killed: {self.zombies_killed}",
            f"Survivors Saved: {len(self.player.team)}",
            f"Final Wave: {self.wave}",
            f"Final Sword: {SWORDS[self.player.sword_id]['name']} +{self.player.sword_level}",
        ]
        for i, stat in enumerate(stats):
            st = font_md.render(stat, True, YELLOW)
            screen.blit(st, (SCREEN_W // 2 - st.get_width() // 2, 250 + i * 30))

        # Player and team
        p_sprite = make_player_sprite(0, int(t * 2) % 4)
        screen.blit(p_sprite, (SCREEN_W // 2 - 24, 400))
        for i in range(len(self.player.team)):
            s_sprite = make_survivor_sprite(i)
            screen.blit(s_sprite, (SCREEN_W // 2 - 100 + i * 60, 400))

        if int(t * 2) % 2:
            prompt = font_md.render("Press ENTER to return to title", True, WHITE)
            screen.blit(prompt, (SCREEN_W // 2 - prompt.get_width() // 2, 500))

    def _draw_gameover(self):
        screen.fill((20, 0, 0))
        title = font_title.render("GAME OVER", True, RED)
        screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 150))

        stats = [
            f"Zombies Killed: {self.zombies_killed}",
            f"Survivors Saved: {len(self.player.team)}",
            f"Wave Reached: {self.wave}",
        ]
        for i, stat in enumerate(stats):
            st = font_md.render(stat, True, WHITE)
            screen.blit(st, (SCREEN_W // 2 - st.get_width() // 2, 260 + i * 30))

        # Dead player
        dead_sprite = make_player_sprite(0, 0)
        dead_sprite = pygame.transform.rotate(dead_sprite, 90)
        screen.blit(dead_sprite, (SCREEN_W // 2 - 24, 380))

        t = pygame.time.get_ticks() / 1000
        if int(t * 2) % 2:
            prompt = font_md.render("Press ENTER to try again", True, WHITE)
            screen.blit(prompt, (SCREEN_W // 2 - prompt.get_width() // 2, 470))

    async def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            clock.tick(FPS)
            await asyncio.sleep(0)
        pygame.quit()
        sys.exit()


# ─── MAIN ───────────────────────────────────────────────────────────
async def main():
    game = Game()
    await game.run()

if __name__ == "__main__":
    asyncio.run(main())
