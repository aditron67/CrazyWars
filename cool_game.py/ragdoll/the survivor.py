"""
THE SURVIVOR - 2D Laser Tag Arena
==================================
Red Team vs Blue Team laser tag. You're on the Blue team.
After enough total kills, a BOSS MONSTER spawns - both teams
must work together to take it down!

Controls:
  WASD / Arrow Keys  - Move
  Mouse Aim + Click  - Shoot laser
  R                  - Reload (max 10 shots per clip)
  ESC                - Quit
"""

import pygame
import math
import random
import sys
import socket
import json
import threading
import time
import os

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
WIDTH, HEIGHT = 1024, 768
FPS = 60
TILE = 48

# Colours
BLACK   = (0, 0, 0)
WHITE   = (255, 255, 255)
RED     = (220, 40, 40)
BLUE    = (40, 100, 220)
GREEN   = (40, 200, 40)
YELLOW  = (255, 220, 0)
GRAY    = (120, 120, 120)
DARK    = (30, 30, 40)
PURPLE  = (160, 40, 200)
ORANGE  = (255, 140, 0)
DARK_RED = (120, 10, 10)

# Gameplay tuning
PLAYER_SPEED       = 3.5
BOT_SPEED          = 2.2
LASER_SPEED        = 12
LASER_RANGE        = 400
LASER_DAMAGE       = 25
CLIP_SIZE          = 10
RELOAD_TIME        = 60       # frames
BOT_SHOOT_COOLDOWN = 50       # frames
RESPAWN_TIME       = 120      # frames

BOSS_TRIGGER_KILLS = 15       # total kills across both teams to spawn boss
BOSS_HP            = 600
BOSS_SPEED         = 1.5
BOSS_SHOOT_CD      = 30
BOSS_LASER_DAMAGE  = 40

NUM_BOTS_PER_TEAM  = 4        # bots per side (you + 4 blue vs 5 red)

# ---------------------------------------------------------------------------
# Mutable settings (admin panel can tweak these at runtime)
# ---------------------------------------------------------------------------
settings = {
    "laser_speed":      12,
    "laser_damage":     25,
    "laser_range":      400,
    "bullets_per_shot": 1,
    "bullet_spread":    0.0,     # radians spread per extra bullet
    "player_speed":     3.5,
    "player_hp":        100,
    "clip_size":        10,
    "reload_time":      60,
    "god_mode":         False,
    "bot_count":        4,       # per team (applied on next respawn wave)
    "boss_hp":          600,
    "boss_trigger":     15,
}

ADMIN_CODE = "66640"
ADMIN_LOCKOUT_SECS = 7 * 24 * 3600   # 1 week
ADMIN_LOCK_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".admin_lock")

KILL_REWARD        = 50       # money per kill
BOSS_KILL_REWARD   = 300      # money for landing the killing blow on boss

# ---------------------------------------------------------------------------
# Weapons  (id, name, damage, speed, clip, reload, bullets, spread, cooldown,
#           cost, laser_colour, gun_pixels)
# gun_pixels: list of (dx, dy, colour) offsets from torso-right in the sprite
# ---------------------------------------------------------------------------
WEAPONS = {
    "pistol": {
        "name": "Pistol",
        "damage": 15,
        "speed": 12,
        "clip": 10,
        "reload": 60,
        "bullets": 1,
        "spread": 0.0,
        "cooldown": 14,
        "cost": 0,
        "laser_col": (0, 255, 100),
        "gun_col": (140, 140, 150),   # gray
        "gun_tip": (100, 255, 100),
    },
    "shotgun": {
        "name": "Shotgun",
        "damage": 12,
        "speed": 10,
        "clip": 6,
        "reload": 80,
        "bullets": 4,
        "spread": 0.12,
        "cooldown": 28,
        "cost": 200,
        "laser_col": (255, 160, 40),
        "gun_col": (120, 80, 40),     # brown
        "gun_tip": (255, 160, 40),
    },
    "rifle": {
        "name": "Rifle",
        "damage": 22,
        "speed": 18,
        "clip": 15,
        "reload": 50,
        "bullets": 1,
        "spread": 0.0,
        "cooldown": 10,
        "cost": 400,
        "laser_col": (40, 180, 255),
        "gun_col": (60, 60, 70),      # dark steel
        "gun_tip": (40, 180, 255),
    },
    "sniper": {
        "name": "Sniper",
        "damage": 50,
        "speed": 28,
        "clip": 4,
        "reload": 100,
        "bullets": 1,
        "spread": 0.0,
        "cooldown": 35,
        "cost": 600,
        "laser_col": (255, 50, 50),
        "gun_col": (50, 50, 50),      # black
        "gun_tip": (255, 50, 50),
    },
    "minigun": {
        "name": "Minigun",
        "damage": 30,
        "speed": 14,
        "clip": 80,
        "reload": 120,
        "bullets": 2,
        "spread": 0.08,
        "cooldown": 4,
        "cost": 1000,
        "laser_col": (255, 255, 60),
        "gun_col": (100, 100, 110),   # gunmetal
        "gun_tip": (255, 255, 60),
    },
}
WEAPON_ORDER = ["pistol", "shotgun", "rifle", "sniper", "minigun"]

# ---------------------------------------------------------------------------
# Networking  (LAN multiplayer)
# ---------------------------------------------------------------------------
NET_PORT    = 5555
NET_TICK    = 2        # broadcast state every N frames
MAX_PLAYERS = 4        # including host

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


class GameServer:
    """Lightweight UDP server the host runs alongside their game."""

    def __init__(self, port=NET_PORT):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("0.0.0.0", port))
        self.sock.settimeout(0.001)
        self.clients = {}            # addr -> {id, team, name, last_input}
        self.next_id = 1
        self.lock = threading.Lock()

    def poll(self):
        """Non-blocking read of all pending client packets."""
        while True:
            try:
                data, addr = self.sock.recvfrom(4096)
                msg = json.loads(data.decode())
                with self.lock:
                    if msg.get("t") == "join":
                        if addr not in self.clients and len(self.clients) < MAX_PLAYERS - 1:
                            team = "blue" if self.next_id % 2 == 1 else "red"
                            self.clients[addr] = {
                                "id": self.next_id, "team": team,
                                "name": msg.get("name", f"P{self.next_id}"),
                                "last_input": {},
                            }
                            reply = json.dumps({"t": "welcome", "id": self.next_id, "team": team})
                            self.sock.sendto(reply.encode(), addr)
                            self.next_id += 1
                        elif addr in self.clients:
                            c = self.clients[addr]
                            reply = json.dumps({"t": "welcome", "id": c["id"], "team": c["team"]})
                            self.sock.sendto(reply.encode(), addr)
                    elif msg.get("t") == "inp":
                        if addr in self.clients:
                            self.clients[addr]["last_input"] = msg
                    elif msg.get("t") == "leave":
                        self.clients.pop(addr, None)
            except socket.timeout:
                break
            except Exception:
                break

    def send_state_to(self, state_dict, addr):
        try:
            self.sock.sendto(json.dumps(state_dict).encode(), addr)
        except Exception:
            pass

    def get_client_inputs(self):
        with self.lock:
            return {c["id"]: dict(c["last_input"]) for c in self.clients.values()}

    def get_clients(self):
        with self.lock:
            return dict(self.clients)

    def close(self):
        self.sock.close()


class GameClient:
    """UDP client that connects to a host."""

    def __init__(self, host_ip, port=NET_PORT):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(0.001)
        self.server_addr = (host_ip, port)
        self.my_id = None
        self.my_team = None
        self.latest_state = None
        self.connected = False
        self.lock = threading.Lock()

    def send_join(self, name="Player"):
        msg = json.dumps({"t": "join", "name": name})
        self.sock.sendto(msg.encode(), self.server_addr)

    def send_input(self, dx, dy, angle, shoot, reload_req, weapon_id):
        msg = json.dumps({
            "t": "inp", "id": self.my_id,
            "dx": round(dx, 2), "dy": round(dy, 2),
            "a": round(angle, 3), "sh": shoot, "rl": reload_req,
            "w": weapon_id,
        })
        self.sock.sendto(msg.encode(), self.server_addr)

    def poll(self):
        while True:
            try:
                data, _ = self.sock.recvfrom(65536)
                msg = json.loads(data.decode())
                if msg.get("t") == "welcome":
                    self.my_id = msg["id"]
                    self.my_team = msg["team"]
                    self.connected = True
                elif msg.get("t") == "state":
                    with self.lock:
                        self.latest_state = msg
            except socket.timeout:
                break
            except Exception:
                break

    def get_state(self):
        with self.lock:
            return self.latest_state

    def close(self):
        try:
            self.sock.sendto(json.dumps({"t": "leave"}).encode(), self.server_addr)
        except Exception:
            pass
        self.sock.close()

# ---------------------------------------------------------------------------
# Pixel-art sprite generation
# ---------------------------------------------------------------------------
PX = 3  # size of each "pixel" in the sprite

def _build_sprite(team_colour, weapon_id="pistol"):
    """
    Build a 10x12 pixel-art guy (scaled by PX) facing RIGHT
    with a weapon-specific gun skin.
    """
    wpn = WEAPONS.get(weapon_id, WEAPONS["pistol"])
    SKIN  = (240, 200, 160)
    BLK   = (50, 40, 35)
    VISOR = (180, 240, 255)
    GUN   = wpn["gun_col"]
    TIP   = wpn["gun_tip"]
    T     = (0, 0, 0, 0)

    palette = {0: T, 1: SKIN, 2: team_colour, 3: BLK, 4: VISOR, 5: GUN, 6: TIP}

    # Weapon-specific gun shape on rows 5-6 (right side of sprite)
    if weapon_id == "shotgun":
        grid = [
            [0,0,0,1,1,1,1,0,0,0,0],
            [0,0,1,1,1,1,1,1,0,0,0],
            [0,0,1,1,4,4,1,1,0,0,0],
            [0,0,0,1,1,1,1,0,0,0,0],
            [0,0,2,2,2,2,2,2,0,0,0],
            [0,2,2,2,2,2,2,5,5,0,0],
            [0,2,2,2,2,2,5,5,6,6,6],
            [0,0,2,2,2,2,2,2,0,0,0],
            [0,0,0,3,3,3,3,0,0,0,0],
            [0,0,0,2,2,2,2,0,0,0,0],
            [0,0,3,3,0,0,3,3,0,0,0],
            [0,0,3,3,0,0,3,3,0,0,0],
        ]
    elif weapon_id == "rifle":
        grid = [
            [0,0,0,1,1,1,1,0,0,0,0,0],
            [0,0,1,1,1,1,1,1,0,0,0,0],
            [0,0,1,1,4,4,1,1,0,0,0,0],
            [0,0,0,1,1,1,1,0,0,0,0,0],
            [0,0,2,2,2,2,2,2,0,0,0,0],
            [0,2,2,2,2,2,2,5,5,5,0,0],
            [0,2,2,2,2,2,5,5,5,5,5,6],
            [0,0,2,2,2,2,2,5,0,0,0,0],
            [0,0,0,3,3,3,3,0,0,0,0,0],
            [0,0,0,2,2,2,2,0,0,0,0,0],
            [0,0,3,3,0,0,3,3,0,0,0,0],
            [0,0,3,3,0,0,3,3,0,0,0,0],
        ]
    elif weapon_id == "sniper":
        grid = [
            [0,0,0,1,1,1,1,0,0,0,0,0,0],
            [0,0,1,1,1,1,1,1,0,0,0,0,0],
            [0,0,1,1,4,4,1,1,0,0,0,0,0],
            [0,0,0,1,1,1,1,0,0,0,0,0,0],
            [0,0,2,2,2,2,2,2,0,0,0,0,0],
            [0,2,2,2,2,2,2,5,5,5,5,0,0],
            [0,2,2,2,2,2,5,5,5,5,5,5,6],
            [0,0,2,2,2,2,2,5,0,0,0,0,0],
            [0,0,0,3,3,3,3,0,0,0,0,0,0],
            [0,0,0,2,2,2,2,0,0,0,0,0,0],
            [0,0,3,3,0,0,3,3,0,0,0,0,0],
            [0,0,3,3,0,0,3,3,0,0,0,0,0],
        ]
    elif weapon_id == "minigun":
        grid = [
            [0,0,0,1,1,1,1,0,0,0,0,0,0],
            [0,0,1,1,1,1,1,1,0,0,0,0,0],
            [0,0,1,1,4,4,1,1,0,0,0,0,0],
            [0,0,0,1,1,1,1,0,0,0,0,0,0],
            [0,0,2,2,2,2,2,2,0,0,0,0,0],
            [0,2,2,2,2,2,5,5,5,5,6,6,0],
            [0,2,2,2,2,2,5,5,5,5,6,6,0],
            [0,2,2,2,2,2,5,5,5,5,6,6,0],
            [0,0,0,3,3,3,3,0,0,0,0,0,0],
            [0,0,0,2,2,2,2,0,0,0,0,0,0],
            [0,0,3,3,0,0,3,3,0,0,0,0,0],
            [0,0,3,3,0,0,3,3,0,0,0,0,0],
        ]
    else:  # pistol (default)
        grid = [
            [0,0,0,1,1,1,1,0,0,0],
            [0,0,1,1,1,1,1,1,0,0],
            [0,0,1,1,4,4,1,1,0,0],
            [0,0,0,1,1,1,1,0,0,0],
            [0,0,2,2,2,2,2,2,0,0],
            [0,2,2,2,2,2,2,2,5,0],
            [0,2,2,2,2,2,2,5,5,6],
            [0,0,2,2,2,2,2,2,0,0],
            [0,0,0,3,3,3,3,0,0,0],
            [0,0,0,2,2,2,2,0,0,0],
            [0,0,3,3,0,0,3,3,0,0],
            [0,0,3,3,0,0,3,3,0,0],
        ]

    w = len(grid[0]) * PX
    h = len(grid) * PX
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for gy, row in enumerate(grid):
        for gx, cell in enumerate(row):
            if cell == 0:
                continue
            colour = palette[cell]
            pygame.draw.rect(surf, colour, (gx * PX, gy * PX, PX, PX))
    return surf


def _build_boss_sprite():
    """Build a 14x14 pixel-art boss monster facing RIGHT."""
    P = (160, 40, 200)   # purple body
    E = (255, 220, 0)    # yellow eyes
    D = (80, 20, 100)    # dark purple
    M = (200, 60, 60)    # mouth / red
    T = (0, 0, 0, 0)

    palette = {0: T, 1: P, 2: D, 3: E, 4: M}
    grid = [
        [0,0,0,0,1,1,1,1,1,1,0,0,0,0],
        [0,0,0,1,1,1,1,1,1,1,1,0,0,0],
        [0,0,1,1,1,1,1,1,1,1,1,1,0,0],
        [0,1,1,3,3,1,1,1,3,3,1,1,1,0],
        [0,1,1,3,3,1,1,1,3,3,1,1,1,0],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,2,1,1,1,4,4,4,4,1,1,1,2,1],
        [1,2,2,1,1,1,4,4,1,1,1,2,2,1],
        [0,1,2,1,1,1,1,1,1,1,1,2,1,0],
        [0,1,1,2,1,1,1,1,1,1,2,1,1,0],
        [0,0,1,1,2,2,1,1,2,2,1,1,0,0],
        [0,0,0,1,1,1,1,1,1,1,1,0,0,0],
        [0,0,1,1,0,1,1,1,1,0,1,1,0,0],
        [0,1,1,0,0,0,1,1,0,0,0,1,1,0],
    ]
    w = len(grid[0]) * PX
    h = len(grid) * PX
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for gy, row in enumerate(grid):
        for gx, cell in enumerate(row):
            if cell == 0:
                continue
            colour = palette[cell]
            pygame.draw.rect(surf, colour, (gx * PX, gy * PX, PX, PX))
    return surf

# These get built AFTER pygame.init() — see main()
_sprites = {}   # key = "team_weapon", e.g. "blue_pistol"

def _init_sprites():
    for wid in WEAPON_ORDER:
        _sprites[f"red_{wid}"]  = _build_sprite(RED, wid)
        _sprites[f"blue_{wid}"] = _build_sprite(BLUE, wid)
    _sprites["boss"] = _build_boss_sprite()

def _get_char_sprite(team, weapon_id):
    key = f"{team}_{weapon_id}"
    return _sprites.get(key, _sprites.get(f"{team}_pistol"))

def _draw_rotated(surf, sprite, cx, cy, angle_rad):
    """Blit *sprite* centered on (cx, cy) rotated so it faces angle_rad."""
    deg = -math.degrees(angle_rad)          # pygame rotates counter-CW
    rotated = pygame.transform.rotate(sprite, deg)
    rect = rotated.get_rect(center=(int(cx), int(cy)))
    surf.blit(rotated, rect)

# ---------------------------------------------------------------------------
# Arena walls  (list of pygame.Rects built later)
# ---------------------------------------------------------------------------
WALL_LAYOUT = [
    # outer boundary
    (0, 0, WIDTH, 12), (0, 0, 12, HEIGHT),
    (0, HEIGHT - 12, WIDTH, 12), (WIDTH - 12, 0, 12, HEIGHT),
    # inner obstacles
    (200, 180, 120, 20), (700, 180, 120, 20),
    (200, 560, 120, 20), (700, 560, 120, 20),
    (460, 300, 100, 20), (460, 440, 100, 20),
    (460, 300, 20, 160),
    (150, 350, 100, 20), (770, 350, 100, 20),
    (320, 100, 20, 120), (680, 100, 20, 120),
    (320, 540, 20, 120), (680, 540, 20, 120),
    (100, 250, 20, 80), (900, 250, 20, 80),
    (100, 440, 20, 80), (900, 440, 20, 80),
]

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def angle_to(ax, ay, bx, by):
    return math.atan2(by - ay, bx - ax)


def dist(ax, ay, bx, by):
    return math.hypot(bx - ax, by - ay)


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def collides_walls(rect, walls):
    for w in walls:
        if rect.colliderect(w):
            return True
    return False


def line_hits_rect(x1, y1, x2, y2, rect):
    """Rough check: does the line segment touch the rect?"""
    clip = rect.clipline(x1, y1, x2, y2)
    return bool(clip)

# ---------------------------------------------------------------------------
# Laser
# ---------------------------------------------------------------------------
class Laser:
    def __init__(self, x, y, angle, team, damage=None, spd_override=None, col_override=None):
        self.x = x
        self.y = y
        spd = spd_override if spd_override else settings["laser_speed"]
        self.vx = math.cos(angle) * spd
        self.vy = math.sin(angle) * spd
        self.speed = spd
        self.team = team          # "red", "blue", or "boss"
        self.damage = damage if damage is not None else settings["laser_damage"]
        self.colour_override = col_override
        self.alive = True
        self.dist_traveled = 0

    def update(self, walls):
        self.x += self.vx
        self.y += self.vy
        self.dist_traveled += self.speed
        if self.dist_traveled > settings["laser_range"]:
            self.alive = False
            return
        pt = pygame.Rect(self.x - 2, self.y - 2, 4, 4)
        if collides_walls(pt, walls):
            self.alive = False

    def draw(self, surf):
        if self.colour_override:
            colour = self.colour_override
        else:
            colour = RED if self.team == "red" else BLUE if self.team == "blue" else PURPLE
        tail_x = self.x - self.vx * 3
        tail_y = self.y - self.vy * 3
        pygame.draw.line(surf, colour, (tail_x, tail_y), (self.x, self.y), 3)

# ---------------------------------------------------------------------------
# Character base
# ---------------------------------------------------------------------------
class Character:
    RADIUS = 14

    def __init__(self, x, y, team):
        self.x = x
        self.y = y
        self.team = team
        self.hp = settings["player_hp"]
        self.max_hp = settings["player_hp"]
        self.angle = 0.0
        self.alive = True
        self.respawn_timer = 0
        self.weapon_id = "pistol"
        self.money = 0
        self.owned_weapons = ["pistol"]
        wpn = WEAPONS[self.weapon_id]
        self.ammo = wpn["clip"]
        self.reload_timer = 0
        self.shoot_cd = 0
        self.kills = 0
        self.deaths = 0
        self.spawn_x = x
        self.spawn_y = y

    @property
    def rect(self):
        return pygame.Rect(self.x - self.RADIUS, self.y - self.RADIUS,
                           self.RADIUS * 2, self.RADIUS * 2)

    def take_damage(self, dmg):
        if not self.alive:
            return
        if settings["god_mode"] and self.team == "blue" and not isinstance(self, Bot):
            return
        self.hp -= dmg
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            self.respawn_timer = RESPAWN_TIME
            self.deaths += 1

    def try_respawn(self):
        if not self.alive:
            self.respawn_timer -= 1
            if self.respawn_timer <= 0:
                self.alive = True
                self.hp = settings["player_hp"]
                self.max_hp = settings["player_hp"]
                wpn = WEAPONS[self.weapon_id]
                self.ammo = wpn["clip"]
                self.reload_timer = 0
                self.x = self.spawn_x + random.randint(-30, 30)
                self.y = self.spawn_y + random.randint(-30, 30)

    def move(self, dx, dy, walls):
        if not self.alive:
            return
        nx = self.x + dx
        ny = self.y + dy
        r = self.RADIUS
        test = pygame.Rect(nx - r, self.y - r, r * 2, r * 2)
        if not collides_walls(test, walls):
            self.x = nx
        test = pygame.Rect(self.x - r, ny - r, r * 2, r * 2)
        if not collides_walls(test, walls):
            self.y = ny
        self.x = clamp(self.x, r, WIDTH - r)
        self.y = clamp(self.y, r, HEIGHT - r)

    def shoot(self, lasers):
        if not self.alive:
            return
        if self.reload_timer > 0:
            return
        if self.shoot_cd > 0:
            return
        wpn = WEAPONS[self.weapon_id]
        if self.ammo <= 0:
            self.reload_timer = wpn["reload"]
            return
        self.ammo -= 1
        self.shoot_cd = wpn["cooldown"]
        # admin overrides: if the admin changed a value from its default, use it
        dmg     = settings["laser_damage"]  if settings["laser_damage"]  != 25  else wpn["damage"]
        spd     = settings["laser_speed"]   if settings["laser_speed"]   != 12  else wpn["speed"]
        n       = settings["bullets_per_shot"] if settings["bullets_per_shot"] != 1 else wpn["bullets"]
        spread  = settings["bullet_spread"] if settings["bullet_spread"] != 0.0 else wpn["spread"]
        base_angle = self.angle
        if n == 1:
            lasers.append(Laser(
                self.x + math.cos(base_angle) * self.RADIUS,
                self.y + math.sin(base_angle) * self.RADIUS,
                base_angle, self.team, dmg,
                spd_override=spd, col_override=wpn["laser_col"]))
        else:
            total_spread = spread * (n - 1)
            start = base_angle - total_spread / 2
            for i in range(n):
                a = start + spread * i
                lasers.append(Laser(
                    self.x + math.cos(a) * self.RADIUS,
                    self.y + math.sin(a) * self.RADIUS,
                    a, self.team, dmg,
                    spd_override=spd, col_override=wpn["laser_col"]))

    def update_timers(self):
        if self.shoot_cd > 0:
            self.shoot_cd -= 1
        if self.reload_timer > 0:
            self.reload_timer -= 1
            if self.reload_timer == 0:
                self.ammo = WEAPONS[self.weapon_id]["clip"]

    def draw(self, surf):
        if not self.alive:
            return
        # pixelated character sprite with weapon skin
        sprite = _get_char_sprite(self.team, self.weapon_id)
        if sprite:
            _draw_rotated(surf, sprite, self.x, self.y, self.angle)
        # hp bar
        bw = 28
        bx = self.x - bw // 2
        by = self.y - self.RADIUS - 10
        pygame.draw.rect(surf, DARK_RED, (bx, by, bw, 4))
        pygame.draw.rect(surf, GREEN, (bx, by, int(bw * self.hp / self.max_hp), 4))

# ---------------------------------------------------------------------------
# Bot AI
# ---------------------------------------------------------------------------
class Bot(Character):
    def __init__(self, x, y, team):
        super().__init__(x, y, team)
        self.target = None
        self.wander_angle = random.uniform(0, 2 * math.pi)
        self.wander_timer = 0

    def pick_target(self, characters, boss):
        """Pick closest alive enemy (or the boss if it's active)."""
        best = None
        best_d = 9999
        # prioritize boss if alive
        if boss and boss.alive:
            d = dist(self.x, self.y, boss.x, boss.y)
            if d < best_d:
                best = boss
                best_d = d
        for c in characters:
            if c is self or not c.alive:
                continue
            if c.team == self.team:
                continue
            d = dist(self.x, self.y, c.x, c.y)
            if d < best_d:
                best = c
                best_d = d
        self.target = best

    def ai_update(self, walls, lasers, characters, boss):
        if not self.alive:
            self.try_respawn()
            return
        self.update_timers()
        self.pick_target(characters, boss)

        if self.target and self.target.alive:
            tx, ty = self.target.x, self.target.y
            d = dist(self.x, self.y, tx, ty)
            self.angle = angle_to(self.x, self.y, tx, ty)

            # move towards target but keep some distance
            if d > 180:
                dx = math.cos(self.angle) * BOT_SPEED
                dy = math.sin(self.angle) * BOT_SPEED
                self.move(dx, dy, walls)
            elif d < 100:
                dx = -math.cos(self.angle) * BOT_SPEED * 0.5
                dy = -math.sin(self.angle) * BOT_SPEED * 0.5
                self.move(dx, dy, walls)
            else:
                # strafe
                strafe = self.angle + math.pi / 2
                dx = math.cos(strafe) * BOT_SPEED * 0.6
                dy = math.sin(strafe) * BOT_SPEED * 0.6
                self.move(dx, dy, walls)

            # shoot at target
            if d < LASER_RANGE and self.shoot_cd == 0:
                self.shoot(lasers)
        else:
            # wander
            self.wander_timer -= 1
            if self.wander_timer <= 0:
                self.wander_angle = random.uniform(0, 2 * math.pi)
                self.wander_timer = random.randint(40, 100)
            self.angle = self.wander_angle
            dx = math.cos(self.angle) * BOT_SPEED * 0.5
            dy = math.sin(self.angle) * BOT_SPEED * 0.5
            self.move(dx, dy, walls)

# ---------------------------------------------------------------------------
# Boss Monster
# ---------------------------------------------------------------------------
class BossMonster:
    RADIUS = 36

    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.hp = BOSS_HP
        self.max_hp = BOSS_HP
        self.alive = False       # spawns later
        self.angle = 0.0
        self.shoot_cd = 0
        self.phase = 1           # gets harder at half hp
        self.pulse = 0

    @property
    def rect(self):
        return pygame.Rect(self.x - self.RADIUS, self.y - self.RADIUS,
                           self.RADIUS * 2, self.RADIUS * 2)

    def spawn(self):
        self.alive = True
        self.hp = BOSS_HP
        self.phase = 1
        self.x = WIDTH // 2
        self.y = HEIGHT // 2

    def take_damage(self, dmg):
        if not self.alive:
            return
        self.hp -= dmg
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def update(self, walls, lasers, characters):
        if not self.alive:
            return
        self.pulse = (self.pulse + 1) % 60
        if self.shoot_cd > 0:
            self.shoot_cd -= 1

        # phase change
        if self.hp < BOSS_HP // 2:
            self.phase = 2

        # pick closest character
        best = None
        best_d = 9999
        for c in characters:
            if not c.alive:
                continue
            d = dist(self.x, self.y, c.x, c.y)
            if d < best_d:
                best = c
                best_d = d

        if best:
            self.angle = angle_to(self.x, self.y, best.x, best.y)
            # move toward target
            spd = BOSS_SPEED if self.phase == 1 else BOSS_SPEED * 1.5
            dx = math.cos(self.angle) * spd
            dy = math.sin(self.angle) * spd
            nx = self.x + dx
            ny = self.y + dy
            r = self.RADIUS
            test = pygame.Rect(nx - r, self.y - r, r * 2, r * 2)
            if not collides_walls(test, walls):
                self.x = nx
            test = pygame.Rect(self.x - r, ny - r, r * 2, r * 2)
            if not collides_walls(test, walls):
                self.y = ny
            self.x = clamp(self.x, r, WIDTH - r)
            self.y = clamp(self.y, r, HEIGHT - r)

            # shoot
            cd = BOSS_SHOOT_CD if self.phase == 1 else BOSS_SHOOT_CD // 2
            if self.shoot_cd == 0 and best_d < LASER_RANGE * 1.3:
                if self.phase == 2:
                    # spread shot
                    for offset in [-0.3, 0, 0.3]:
                        lasers.append(Laser(
                            self.x + math.cos(self.angle + offset) * self.RADIUS,
                            self.y + math.sin(self.angle + offset) * self.RADIUS,
                            self.angle + offset, "boss", BOSS_LASER_DAMAGE))
                else:
                    lasers.append(Laser(
                        self.x + math.cos(self.angle) * self.RADIUS,
                        self.y + math.sin(self.angle) * self.RADIUS,
                        self.angle, "boss", BOSS_LASER_DAMAGE))
                self.shoot_cd = cd

    def draw(self, surf):
        if not self.alive:
            return
        # pixel-art boss sprite with glow pulse
        glow = abs(self.pulse - 30) / 30.0
        boss_sprite = _sprites.get("boss")
        if boss_sprite:
            # tint the sprite slightly based on glow
            tinted = boss_sprite.copy()
            overlay = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
            overlay.fill((int(60 * glow), 0, 0, int(40 * glow)))
            tinted.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            _draw_rotated(surf, tinted, self.x, self.y, self.angle)
        # hp bar
        bw = 60
        bx = self.x - bw // 2
        by = self.y - self.RADIUS - 12
        pygame.draw.rect(surf, DARK_RED, (bx, by, bw, 6))
        pygame.draw.rect(surf, ORANGE, (bx, by, int(bw * self.hp / self.max_hp), 6))
        # label
        font = pygame.font.SysFont(None, 20)
        label = font.render("BOSS", True, YELLOW)
        surf.blit(label, (self.x - label.get_width() // 2, by - 16))

# ---------------------------------------------------------------------------
# Particle (for hit effects)
# ---------------------------------------------------------------------------
class Particle:
    def __init__(self, x, y, colour):
        self.x = x
        self.y = y
        a = random.uniform(0, 2 * math.pi)
        s = random.uniform(1, 4)
        self.vx = math.cos(a) * s
        self.vy = math.sin(a) * s
        self.life = random.randint(8, 20)
        self.colour = colour

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surf):
        if self.life > 0:
            alpha = clamp(int(255 * self.life / 20), 0, 255)
            c = tuple(clamp(int(v * self.life / 20), 0, 255) for v in self.colour)
            pygame.draw.circle(surf, c, (int(self.x), int(self.y)), 2)

# ---------------------------------------------------------------------------
# Admin Panel  (TAB to open, code 66640)
# ---------------------------------------------------------------------------
class AdminPanel:
    SETTINGS_DEFS = [
        # (key,            label,                  min,  max,  step, fmt)
        ("laser_speed",    "Laser Speed",           2,   60,    1,  "{:.0f}"),
        ("laser_damage",   "Laser Damage",          1,  200,    5,  "{:.0f}"),
        ("laser_range",    "Laser Range",          50, 1200,   25,  "{:.0f}"),
        ("bullets_per_shot","Bullets / Shot",       1,   12,    1,  "{:.0f}"),
        ("bullet_spread",  "Bullet Spread",       0.0,  0.8, 0.05, "{:.2f}"),
        ("player_speed",   "Player Speed",        1.0, 15.0,  0.5, "{:.1f}"),
        ("player_hp",      "Player HP",            10, 1000,   10,  "{:.0f}"),
        ("clip_size",      "Clip Size",             1,  100,    1,  "{:.0f}"),
        ("reload_time",    "Reload Time (frames)",  5,  300,    5,  "{:.0f}"),
        ("god_mode",       "God Mode",              0,    1,    1,  "{:.0f}"),
        ("boss_hp",        "Boss HP",              50, 5000,   50,  "{:.0f}"),
        ("boss_trigger",   "Boss Trigger Kills",    1,  100,    1,  "{:.0f}"),
    ]

    def __init__(self):
        self.active = False
        self.unlocked = False
        self.code_input = ""
        self.selected = 0
        self.scroll = 0
        self.visible_rows = 10
        self.flash_timer = 0
        self.flash_msg = ""
        self.locked_out = False
        self.lockout_end = 0
        self._load_lockout()

    def _load_lockout(self):
        """Load last failed attempt time from file."""
        try:
            with open(ADMIN_LOCK_FILE, "r") as f:
                data = json.load(f)
                fail_time = data.get("t", 0)
                remaining = (fail_time + ADMIN_LOCKOUT_SECS) - time.time()
                if remaining > 0:
                    self.locked_out = True
                    self.lockout_end = fail_time + ADMIN_LOCKOUT_SECS
                else:
                    self.locked_out = False
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            self.locked_out = False

    def _save_lockout(self):
        """Save failed attempt timestamp to file."""
        with open(ADMIN_LOCK_FILE, "w") as f:
            json.dump({"t": time.time()}, f)
        self.locked_out = True
        self.lockout_end = time.time() + ADMIN_LOCKOUT_SECS

    def _lockout_remaining_str(self):
        secs = max(0, int(self.lockout_end - time.time()))
        days = secs // 86400
        hrs  = (secs % 86400) // 3600
        mins = (secs % 3600) // 60
        return f"{days}d {hrs}h {mins}m"

    def open(self):
        if self.unlocked:
            self.active = True
            return
        # check lockout
        self._load_lockout()
        if self.locked_out:
            self.active = True  # show locked screen
            self.flash_msg = f"LOCKED — wait {self._lockout_remaining_str()}"
            self.flash_timer = 120
        else:
            self.code_input = ""
            self.active = True

    def close(self):
        self.active = False

    def handle_event(self, ev):
        """Returns True if the event was consumed."""
        if not self.active:
            return False

        if ev.type != pygame.KEYDOWN:
            return True  # consume all non-key events while open

        # --- Locked out mode ---
        if self.locked_out and not self.unlocked:
            if ev.key == pygame.K_ESCAPE:
                self.close()
            return True

        # --- Code entry mode ---
        if not self.unlocked:
            if ev.key == pygame.K_ESCAPE:
                self.close()
                return True
            if ev.key == pygame.K_BACKSPACE:
                self.code_input = self.code_input[:-1]
                return True
            if ev.key == pygame.K_RETURN:
                if self.code_input == ADMIN_CODE:
                    self.unlocked = True
                    self.flash_msg = "ACCESS GRANTED"
                    self.flash_timer = 90
                    # clear lockout file on success
                    try:
                        os.remove(ADMIN_LOCK_FILE)
                    except FileNotFoundError:
                        pass
                else:
                    self.code_input = ""
                    self._save_lockout()
                    self.flash_msg = f"WRONG CODE — locked for 1 week"
                    self.flash_timer = 120
                return True
            if ev.unicode.isdigit():
                self.code_input += ev.unicode
            return True

        # --- Settings editor mode ---
        if ev.key in (pygame.K_ESCAPE, pygame.K_TAB):
            self.close()
            return True
        if ev.key in (pygame.K_UP, pygame.K_w):
            self.selected = max(0, self.selected - 1)
            if self.selected < self.scroll:
                self.scroll = self.selected
        elif ev.key in (pygame.K_DOWN, pygame.K_s):
            self.selected = min(len(self.SETTINGS_DEFS) - 1, self.selected + 1)
            if self.selected >= self.scroll + self.visible_rows:
                self.scroll = self.selected - self.visible_rows + 1
        elif ev.key in (pygame.K_LEFT, pygame.K_a):
            self._adjust(-1)
        elif ev.key in (pygame.K_RIGHT, pygame.K_d):
            self._adjust(1)
        elif ev.key == pygame.K_r:
            self._reset_all()
        return True

    def _adjust(self, direction):
        key, _, lo, hi, step, _ = self.SETTINGS_DEFS[self.selected]
        val = settings[key]
        if isinstance(val, bool):
            settings[key] = not val
        else:
            val += step * direction
            if isinstance(lo, int) and isinstance(hi, int) and isinstance(step, int):
                val = int(clamp(val, lo, hi))
            else:
                val = round(clamp(val, lo, hi), 3)
            settings[key] = val

    def _reset_all(self):
        defaults = {
            "laser_speed": 12, "laser_damage": 25, "laser_range": 400,
            "bullets_per_shot": 1, "bullet_spread": 0.0, "player_speed": 3.5,
            "player_hp": 100, "clip_size": 10, "reload_time": 60,
            "god_mode": False, "bot_count": 4, "boss_hp": 600, "boss_trigger": 15,
        }
        settings.update(defaults)
        self.flash_msg = "RESET TO DEFAULTS"
        self.flash_timer = 60

    def draw(self, surf):
        if not self.active:
            return
        font = pygame.font.SysFont(None, 26)
        title_font = pygame.font.SysFont(None, 34)

        # dim background
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surf.blit(overlay, (0, 0))

        pw, ph = 500, 420
        px = (WIDTH - pw) // 2
        py = (HEIGHT - ph) // 2
        pygame.draw.rect(surf, (20, 20, 30), (px, py, pw, ph), border_radius=8)
        pygame.draw.rect(surf, YELLOW, (px, py, pw, ph), 2, border_radius=8)

        # --- Locked out screen ---
        if self.locked_out and not self.unlocked:
            t = title_font.render("ADMIN PANEL", True, RED)
            surf.blit(t, (px + pw // 2 - t.get_width() // 2, py + 30))
            lock_lbl = font.render("ACCESS LOCKED", True, RED)
            surf.blit(lock_lbl, (px + pw // 2 - lock_lbl.get_width() // 2, py + 100))
            remain = font.render(f"Try again in: {self._lockout_remaining_str()}", True, ORANGE)
            surf.blit(remain, (px + pw // 2 - remain.get_width() // 2, py + 140))
            warn = font.render("1 attempt per week", True, GRAY)
            surf.blit(warn, (px + pw // 2 - warn.get_width() // 2, py + 180))
            hint = font.render("[ESC] Close", True, GRAY)
            surf.blit(hint, (px + pw // 2 - hint.get_width() // 2, py + 240))
            return

        # --- Code entry ---
        if not self.unlocked:
            t = title_font.render("ADMIN PANEL", True, YELLOW)
            surf.blit(t, (px + pw // 2 - t.get_width() // 2, py + 30))
            prompt = font.render("Enter access code:", True, WHITE)
            surf.blit(prompt, (px + pw // 2 - prompt.get_width() // 2, py + 90))
            code_display = "*" * len(self.code_input) + "_"
            cd = title_font.render(code_display, True, GREEN)
            surf.blit(cd, (px + pw // 2 - cd.get_width() // 2, py + 130))
            warn2 = font.render("WARNING: 1 attempt per week!", True, ORANGE)
            surf.blit(warn2, (px + pw // 2 - warn2.get_width() // 2, py + 170))
            hint = font.render("[ENTER] Submit   [ESC] Cancel", True, GRAY)
            surf.blit(hint, (px + pw // 2 - hint.get_width() // 2, py + 210))
            if self.flash_timer > 0:
                self.flash_timer -= 1
                fc = GREEN if "GRANTED" in self.flash_msg else RED
                fm = font.render(self.flash_msg, True, fc)
                surf.blit(fm, (px + pw // 2 - fm.get_width() // 2, py + 260))
            return

        # --- Settings editor ---
        t = title_font.render("ADMIN PANEL", True, YELLOW)
        surf.blit(t, (px + pw // 2 - t.get_width() // 2, py + 10))

        y = py + 50
        for i in range(self.scroll, min(self.scroll + self.visible_rows, len(self.SETTINGS_DEFS))):
            key, label, lo, hi, step, fmt = self.SETTINGS_DEFS[i]
            val = settings[key]
            if isinstance(val, bool):
                val_str = "ON" if val else "OFF"
            else:
                val_str = fmt.format(val)

            selected = (i == self.selected)
            colour = YELLOW if selected else WHITE
            prefix = "> " if selected else "  "

            lbl = font.render(f"{prefix}{label}", True, colour)
            surf.blit(lbl, (px + 20, y))
            vs = font.render(f"< {val_str} >", True, GREEN if selected else GRAY)
            surf.blit(vs, (px + pw - 20 - vs.get_width(), y))
            y += 32

        # controls hint
        hints = font.render("[UP/DN] Select  [LT/RT] Adjust  [R] Reset  [ESC] Close", True, GRAY)
        surf.blit(hints, (px + pw // 2 - hints.get_width() // 2, py + ph - 40))

        if self.flash_timer > 0:
            self.flash_timer -= 1
            fm = font.render(self.flash_msg, True, GREEN)
            surf.blit(fm, (px + pw // 2 - fm.get_width() // 2, py + ph - 65))

# ---------------------------------------------------------------------------
# Weapon Shop  (B to open)
# ---------------------------------------------------------------------------
class WeaponShop:
    def __init__(self):
        self.active = False
        self.selected = 0
        self.flash_msg = ""
        self.flash_timer = 0

    def open(self):
        self.active = True
        self.selected = 0

    def close(self):
        self.active = False

    def handle_event(self, ev, player):
        if not self.active:
            return False
        if ev.type != pygame.KEYDOWN:
            return True
        if ev.key in (pygame.K_ESCAPE, pygame.K_b):
            self.close()
            return True
        if ev.key in (pygame.K_UP, pygame.K_w):
            self.selected = max(0, self.selected - 1)
        elif ev.key in (pygame.K_DOWN, pygame.K_s):
            self.selected = min(len(WEAPON_ORDER) - 1, self.selected + 1)
        elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
            wid = WEAPON_ORDER[self.selected]
            wpn = WEAPONS[wid]
            if wid in player.owned_weapons:
                # equip it
                player.weapon_id = wid
                player.ammo = wpn["clip"]
                player.reload_timer = 0
                self.flash_msg = f"Equipped {wpn['name']}!"
                self.flash_timer = 60
            elif player.money >= wpn["cost"]:
                player.money -= wpn["cost"]
                player.owned_weapons.append(wid)
                player.weapon_id = wid
                player.ammo = wpn["clip"]
                player.reload_timer = 0
                self.flash_msg = f"Bought & equipped {wpn['name']}!"
                self.flash_timer = 60
            else:
                self.flash_msg = "Not enough money!"
                self.flash_timer = 60
        return True

    def draw(self, surf, player):
        if not self.active:
            return
        font = pygame.font.SysFont(None, 24)
        title_font = pygame.font.SysFont(None, 34)
        small = pygame.font.SysFont(None, 20)

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surf.blit(overlay, (0, 0))

        pw, ph = 560, 420
        px = (WIDTH - pw) // 2
        py = (HEIGHT - ph) // 2
        pygame.draw.rect(surf, (20, 20, 30), (px, py, pw, ph), border_radius=8)
        pygame.draw.rect(surf, ORANGE, (px, py, pw, ph), 2, border_radius=8)

        t = title_font.render("WEAPON SHOP", True, ORANGE)
        surf.blit(t, (px + pw // 2 - t.get_width() // 2, py + 10))
        money_lbl = font.render(f"Money: ${player.money}", True, YELLOW)
        surf.blit(money_lbl, (px + pw // 2 - money_lbl.get_width() // 2, py + 40))

        y = py + 70
        for i, wid in enumerate(WEAPON_ORDER):
            wpn = WEAPONS[wid]
            selected = (i == self.selected)
            owned = wid in player.owned_weapons
            equipped = player.weapon_id == wid

            col = YELLOW if selected else WHITE
            prefix = "> " if selected else "  "

            # weapon name + status
            if equipped:
                status = "[EQUIPPED]"
                scol = GREEN
            elif owned:
                status = "[OWNED]"
                scol = (100, 200, 100)
            else:
                status = f"${wpn['cost']}"
                scol = YELLOW if player.money >= wpn["cost"] else RED

            name_lbl = font.render(f"{prefix}{wpn['name']}", True, col)
            surf.blit(name_lbl, (px + 20, y))
            stat_lbl = font.render(status, True, scol)
            surf.blit(stat_lbl, (px + pw - 20 - stat_lbl.get_width(), y))

            # stats on selected
            if selected:
                stats = (f"DMG:{wpn['damage']}  SPD:{wpn['speed']}  "
                         f"CLIP:{wpn['clip']}  BULLETS:{wpn['bullets']}  "
                         f"CD:{wpn['cooldown']}")
                st = small.render(stats, True, GRAY)
                surf.blit(st, (px + 40, y + 22))
                y += 24

            y += 28

        # draw weapon preview — show pixel art of selected weapon
        sel_wid = WEAPON_ORDER[self.selected]
        preview = _get_char_sprite("blue", sel_wid)
        if preview:
            scaled = pygame.transform.scale(preview,
                (preview.get_width() * 3, preview.get_height() * 3))
            surf.blit(scaled, (px + pw - 120, py + ph - 130))

        hints = font.render("[UP/DN] Select  [ENTER] Buy/Equip  [ESC] Close", True, GRAY)
        surf.blit(hints, (px + pw // 2 - hints.get_width() // 2, py + ph - 35))

        if self.flash_timer > 0:
            self.flash_timer -= 1
            fc = GREEN if "Bought" in self.flash_msg or "Equipped" in self.flash_msg else RED
            fm = font.render(self.flash_msg, True, fc)
            surf.blit(fm, (px + pw // 2 - fm.get_width() // 2, py + ph - 60))

# ---------------------------------------------------------------------------
# HUD
# ---------------------------------------------------------------------------
def draw_hud(surf, player, red_score, blue_score, boss, boss_spawned, font, big_font):
    # team scores
    r_label = font.render(f"RED: {red_score}", True, RED)
    b_label = font.render(f"BLUE: {blue_score}", True, BLUE)
    surf.blit(r_label, (WIDTH // 2 - 120, 16))
    surf.blit(b_label, (WIDTH // 2 + 40, 16))

    # player stats
    hp_text = font.render(f"HP: {player.hp}", True, GREEN if player.hp > 30 else RED)
    surf.blit(hp_text, (16, 16))
    wpn = WEAPONS[player.weapon_id]
    ammo_text = font.render(f"Ammo: {player.ammo}/{wpn['clip']}", True, WHITE)
    surf.blit(ammo_text, (16, 38))
    wname = font.render(f"Gun: {wpn['name']}", True, ORANGE)
    surf.blit(wname, (16, 58))
    money_text = font.render(f"${player.money}", True, YELLOW)
    surf.blit(money_text, (16, 78))
    if player.reload_timer > 0:
        rl = font.render("RELOADING...", True, YELLOW)
        surf.blit(rl, (16, 98))
    kd = font.render(f"K/D: {player.kills}/{player.deaths}", True, WHITE)
    surf.blit(kd, (16, HEIGHT - 30))

    if not player.alive:
        resp = big_font.render("RESPAWNING...", True, WHITE)
        surf.blit(resp, (WIDTH // 2 - resp.get_width() // 2, HEIGHT // 2 - 20))

    # boss warning
    if boss_spawned and boss.alive:
        warn = big_font.render("!! BOSS MONSTER ACTIVE !!", True, PURPLE)
        surf.blit(warn, (WIDTH // 2 - warn.get_width() // 2, 50))
    elif boss_spawned and not boss.alive:
        win = big_font.render("BOSS DEFEATED!", True, GREEN)
        surf.blit(win, (WIDTH // 2 - win.get_width() // 2, 50))

    # boss kill bar
    if not boss_spawned:
        total = red_score + blue_score
        progress = min(total / BOSS_TRIGGER_KILLS, 1.0)
        bw = 200
        bx = WIDTH // 2 - bw // 2
        by = 42
        pygame.draw.rect(surf, GRAY, (bx, by, bw, 8))
        pygame.draw.rect(surf, PURPLE, (bx, by, int(bw * progress), 8))
        lbl = font.render(f"Boss spawn: {total}/{BOSS_TRIGGER_KILLS}", True, PURPLE)
        surf.blit(lbl, (bx, by + 10))

    # crosshair
    mx, my = pygame.mouse.get_pos()
    pygame.draw.line(surf, GREEN, (mx - 8, my), (mx + 8, my), 1)
    pygame.draw.line(surf, GREEN, (mx, my - 8), (mx, my + 8), 1)

    # admin hint
    if boss_spawned or True:  # always show
        tab_hint = font.render("[TAB] Admin  [B] Shop", True, (80, 80, 80))
        surf.blit(tab_hint, (WIDTH - tab_hint.get_width() - 12, HEIGHT - 24))

# ---------------------------------------------------------------------------
# Lobby Screen
# ---------------------------------------------------------------------------
def run_lobby(screen, clock):
    """Show title + mode selection.  Returns ("solo", None), ("host", GameServer), or ("client", GameClient)."""
    font = pygame.font.SysFont(None, 28)
    big   = pygame.font.SysFont(None, 52)
    small = pygame.font.SysFont(None, 22)
    options = ["SOLO  —  Play with bots",
               "HOST  —  Start a game for friends",
               "JOIN  —  Join a friend's game"]
    sel = 0
    state = "menu"       # menu | host_wait | join_input | join_wait
    ip_input = ""
    server = None
    client = None
    join_timer = 0
    local_ip = get_local_ip()

    while True:
        clock.tick(30)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type != pygame.KEYDOWN:
                continue
            if state == "menu":
                if ev.key in (pygame.K_UP, pygame.K_w):
                    sel = (sel - 1) % 3
                elif ev.key in (pygame.K_DOWN, pygame.K_s):
                    sel = (sel + 1) % 3
                elif ev.key == pygame.K_RETURN:
                    if sel == 0:
                        return ("solo", None)
                    elif sel == 1:
                        server = GameServer()
                        state = "host_wait"
                    elif sel == 2:
                        state = "join_input"
                        ip_input = ""
                elif ev.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
            elif state == "host_wait":
                if ev.key == pygame.K_RETURN:
                    return ("host", server)
                if ev.key == pygame.K_ESCAPE:
                    server.close(); server = None; state = "menu"
            elif state == "join_input":
                if ev.key == pygame.K_ESCAPE:
                    state = "menu"
                elif ev.key == pygame.K_RETURN and ip_input:
                    host_ip = ip_input.strip()
                    client = GameClient(host_ip)
                    client.send_join("Friend")
                    state = "join_wait"
                    join_timer = 0
                elif ev.key == pygame.K_BACKSPACE:
                    ip_input = ip_input[:-1]
                elif ev.unicode and ev.unicode in "0123456789.":
                    ip_input += ev.unicode
            elif state == "join_wait":
                if ev.key == pygame.K_ESCAPE:
                    client.close(); client = None; state = "menu"

        # host_wait: poll for connecting clients
        if state == "host_wait" and server:
            server.poll()

        # join_wait: poll for welcome
        if state == "join_wait" and client:
            client.poll()
            join_timer += 1
            if join_timer % 30 == 0:
                client.send_join("Friend")  # retry
            if client.connected:
                return ("client", client)

        # --- draw ---
        screen.fill(DARK)
        title = big.render("THE SURVIVOR", True, YELLOW)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))
        sub = font.render("2D Laser Tag Arena", True, GRAY)
        screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 135))

        if state == "menu":
            for i, opt in enumerate(options):
                col = YELLOW if i == sel else WHITE
                pre = "> " if i == sel else "  "
                lbl = font.render(f"{pre}{opt}", True, col)
                screen.blit(lbl, (WIDTH // 2 - 180, 220 + i * 50))
            hint = small.render("[UP/DOWN] Select   [ENTER] Confirm   [ESC] Quit", True, GRAY)
            screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 60))

        elif state == "host_wait":
            ip_lbl = font.render(f"Your IP:  {local_ip}:{NET_PORT}", True, GREEN)
            screen.blit(ip_lbl, (WIDTH // 2 - ip_lbl.get_width() // 2, 220))
            info = font.render("Share this IP with your friends!", True, WHITE)
            screen.blit(info, (WIDTH // 2 - info.get_width() // 2, 260))
            clients = server.get_clients()
            y = 320
            ct = font.render(f"Players connected: {len(clients)}", True, ORANGE)
            screen.blit(ct, (WIDTH // 2 - ct.get_width() // 2, y))
            y += 35
            for addr, cinfo in clients.items():
                pl = small.render(f"  {cinfo['name']}  —  Team {cinfo['team'].upper()}", True,
                                  BLUE if cinfo["team"] == "blue" else RED)
                screen.blit(pl, (WIDTH // 2 - 100, y))
                y += 25
            start = font.render("[ENTER]  Start Game", True, GREEN)
            screen.blit(start, (WIDTH // 2 - start.get_width() // 2, HEIGHT - 120))
            back = small.render("[ESC] Back", True, GRAY)
            screen.blit(back, (WIDTH // 2 - back.get_width() // 2, HEIGHT - 60))

        elif state == "join_input":
            prompt = font.render("Enter host IP address:", True, WHITE)
            screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, 250))
            ip_disp = big.render(ip_input + "_", True, GREEN)
            screen.blit(ip_disp, (WIDTH // 2 - ip_disp.get_width() // 2, 300))
            hint = small.render("[ENTER] Connect   [ESC] Back", True, GRAY)
            screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 60))

        elif state == "join_wait":
            dots = "." * ((join_timer // 15) % 4)
            ct = font.render(f"Connecting to {ip_input}{dots}", True, YELLOW)
            screen.blit(ct, (WIDTH // 2 - ct.get_width() // 2, 300))
            back = small.render("[ESC] Cancel", True, GRAY)
            screen.blit(back, (WIDTH // 2 - back.get_width() // 2, HEIGHT - 60))

        pygame.display.flip()


# ---------------------------------------------------------------------------
# Client-side game loop  (renders state from host, sends inputs)
# ---------------------------------------------------------------------------
def run_client_game(screen, clock, client):
    font     = pygame.font.SysFont(None, 24)
    big_font = pygame.font.SysFont(None, 36)
    walls    = [pygame.Rect(*w) for w in WALL_LAYOUT]
    shop     = WeaponShop()

    # proxy object so the weapon shop can read/write fields
    class Proxy:
        def __init__(self):
            self.money = 0
            self.owned_weapons = ["pistol"]
            self.weapon_id = "pistol"
            self.ammo = 10
            self.reload_timer = 0
            self.hp = 100
            self.max_hp = 100
            self.alive = True
            self.kills = 0
            self.deaths = 0
    proxy = Proxy()

    running = True
    pygame.mouse.set_visible(False)

    while running:
        clock.tick(FPS)
        client.poll()

        shoot_req = False
        reload_req = False
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False; continue
            if shop.active:
                shop.handle_event(ev, proxy)
                continue
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False
                if ev.key == pygame.K_r:
                    reload_req = True
                if ev.key == pygame.K_b:
                    shop.open()

        keys = pygame.key.get_pressed()
        dx = dy = 0
        spd = settings["player_speed"]
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx -= spd
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += spd
        if keys[pygame.K_w] or keys[pygame.K_UP]:    dy -= spd
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy += spd
        if dx and dy:
            dx *= 0.707; dy *= 0.707
        if pygame.mouse.get_pressed()[0]:
            shoot_req = True

        # figure out my position for angle calc
        state = client.get_state()
        my_x, my_y = WIDTH // 2, HEIGHT // 2
        if state:
            idx = state.get("my", -1)
            chars = state.get("ch", [])
            if 0 <= idx < len(chars):
                my_x, my_y = chars[idx]["x"], chars[idx]["y"]
        mx, my_mouse = pygame.mouse.get_pos()
        angle = angle_to(my_x, my_y, mx, my_mouse)

        if client.connected:
            client.send_input(dx, dy, angle, shoot_req, reload_req, proxy.weapon_id)

        # ---- render ----
        screen.fill(DARK)
        for gx in range(0, WIDTH, TILE):
            pygame.draw.line(screen, (40, 40, 50), (gx, 0), (gx, HEIGHT), 1)
        for gy in range(0, HEIGHT, TILE):
            pygame.draw.line(screen, (40, 40, 50), (0, gy), (WIDTH, gy), 1)
        for w in walls:
            pygame.draw.rect(screen, GRAY, w)

        if state:
            chars = state.get("ch", [])
            my_idx = state.get("my", -1)

            # characters
            for i, cd in enumerate(chars):
                if not cd.get("al", False):
                    continue
                sprite = _get_char_sprite(cd["t"], cd.get("w", "pistol"))
                if sprite:
                    _draw_rotated(screen, sprite, cd["x"], cd["y"], cd["a"])
                bw = 28
                bx = cd["x"] - bw // 2
                by_bar = cd["y"] - Character.RADIUS - 10
                pygame.draw.rect(screen, DARK_RED, (bx, by_bar, bw, 4))
                ratio = cd["hp"] / cd["mhp"] if cd["mhp"] else 0
                pygame.draw.rect(screen, GREEN, (bx, by_bar, int(bw * ratio), 4))
                if i == my_idx:
                    pygame.draw.circle(screen, YELLOW,
                                       (int(cd["x"]), int(cd["y"])), Character.RADIUS + 3, 2)

            # boss
            bd = state.get("bo")
            if bd and bd.get("al"):
                bs = _sprites.get("boss")
                if bs:
                    _draw_rotated(screen, bs, bd["x"], bd["y"], bd["a"])
                bw = 60; bx = bd["x"] - bw // 2; by_b = bd["y"] - 36 - 12
                pygame.draw.rect(screen, DARK_RED, (bx, by_b, bw, 6))
                pygame.draw.rect(screen, ORANGE, (bx, by_b, int(bw * bd["hp"] / max(bd["mhp"], 1)), 6))
                lf = pygame.font.SysFont(None, 20)
                ll = lf.render("BOSS", True, YELLOW)
                screen.blit(ll, (bd["x"] - ll.get_width() // 2, by_b - 16))

            # lasers
            for ld in state.get("la", []):
                col = tuple(ld.get("c", [255, 255, 255]))
                tx = ld["x"] - ld["vx"] * 3
                ty = ld["y"] - ld["vy"] * 3
                pygame.draw.line(screen, col, (tx, ty), (ld["x"], ld["y"]), 3)

            # update proxy from server
            proxy.money = state.get("$$", 0)
            proxy.owned_weapons = state.get("ow", ["pistol"])
            proxy.weapon_id = state.get("wi", "pistol")
            proxy.ammo = state.get("am", 0)
            proxy.reload_timer = 1 if state.get("rr") else 0
            proxy.hp = state.get("hp", 100)
            proxy.max_hp = state.get("mh", 100)
            proxy.alive = state.get("al", True)
            proxy.kills = state.get("k", 0)
            proxy.deaths = state.get("d", 0)

            # HUD
            rs = state.get("rs", 0)
            bs_score = state.get("bs", 0)
            rl = font.render(f"RED: {rs}", True, RED)
            bl = font.render(f"BLUE: {bs_score}", True, BLUE)
            screen.blit(rl, (WIDTH // 2 - 120, 16))
            screen.blit(bl, (WIDTH // 2 + 40, 16))
            hpt = font.render(f"HP: {proxy.hp}", True, GREEN if proxy.hp > 30 else RED)
            screen.blit(hpt, (16, 16))
            wpn = WEAPONS.get(proxy.weapon_id, WEAPONS["pistol"])
            at = font.render(f"Ammo: {proxy.ammo}/{wpn['clip']}", True, WHITE)
            screen.blit(at, (16, 38))
            wn = font.render(f"Gun: {wpn['name']}", True, ORANGE)
            screen.blit(wn, (16, 58))
            mt = font.render(f"${proxy.money}", True, YELLOW)
            screen.blit(mt, (16, 78))
            if proxy.reload_timer:
                rt = font.render("RELOADING...", True, YELLOW)
                screen.blit(rt, (16, 98))
            kd = font.render(f"K/D: {proxy.kills}/{proxy.deaths}", True, WHITE)
            screen.blit(kd, (16, HEIGHT - 30))
            if not proxy.alive:
                resp = big_font.render("RESPAWNING...", True, WHITE)
                screen.blit(resp, (WIDTH // 2 - resp.get_width() // 2, HEIGHT // 2 - 20))
            bsp = state.get("bsp", False)
            if bsp and bd and bd.get("al"):
                ww = big_font.render("!! BOSS MONSTER ACTIVE !!", True, PURPLE)
                screen.blit(ww, (WIDTH // 2 - ww.get_width() // 2, 50))
            elif bsp and (not bd or not bd.get("al")):
                ww = big_font.render("BOSS DEFEATED!", True, GREEN)
                screen.blit(ww, (WIDTH // 2 - ww.get_width() // 2, 50))
            team_t = font.render(f"Team: {client.my_team.upper()}", True,
                                 BLUE if client.my_team == "blue" else RED)
            screen.blit(team_t, (WIDTH - team_t.get_width() - 16, 16))

        # crosshair
        mx, my_mouse = pygame.mouse.get_pos()
        pygame.draw.line(screen, GREEN, (mx - 8, my_mouse), (mx + 8, my_mouse), 1)
        pygame.draw.line(screen, GREEN, (mx, my_mouse - 8), (mx, my_mouse + 8), 1)
        bh = font.render("[B] Shop", True, (80, 80, 80))
        screen.blit(bh, (WIDTH - bh.get_width() - 12, HEIGHT - 24))

        if not client.connected:
            ct = big_font.render("Connecting...", True, YELLOW)
            screen.blit(ct, (WIDTH // 2 - ct.get_width() // 2, HEIGHT // 2))

        if shop.active:
            shop.draw(screen, proxy)

        pygame.display.flip()

    client.close()
    pygame.mouse.set_visible(True)
    pygame.quit()
    sys.exit()


# ---------------------------------------------------------------------------
# State packing  (host -> clients)
# ---------------------------------------------------------------------------
def _pack_state(all_chars, boss, boss_spawned, lasers, red_score, blue_score):
    """Build compact state dict for network transmission."""
    ch = []
    for c in all_chars:
        ch.append({
            "x": round(c.x, 1), "y": round(c.y, 1), "a": round(c.angle, 2),
            "hp": c.hp, "mhp": c.max_hp, "al": c.alive,
            "t": c.team, "w": c.weapon_id,
        })
    bo = None
    if boss_spawned:
        bo = {
            "x": round(boss.x, 1), "y": round(boss.y, 1), "a": round(boss.angle, 2),
            "hp": boss.hp, "mhp": boss.max_hp, "al": boss.alive, "ph": boss.phase,
        }
    la = []
    for l in lasers:
        if l.alive:
            col = list(l.colour_override) if l.colour_override else (
                [220, 40, 40] if l.team == "red" else
                [40, 100, 220] if l.team == "blue" else [160, 40, 200])
            la.append({"x": round(l.x, 1), "y": round(l.y, 1),
                        "vx": round(l.vx, 1), "vy": round(l.vy, 1), "c": col})
    return {"t": "state", "ch": ch, "bo": bo, "bsp": boss_spawned,
            "la": la, "rs": red_score, "bs": blue_score}


# ---------------------------------------------------------------------------
# Main Game
# ---------------------------------------------------------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("THE SURVIVOR — 2D Laser Tag")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    big_font = pygame.font.SysFont(None, 36)

    # build pixel sprites (must be after pygame.init)
    _init_sprites()

    # ---- lobby ----
    mode, net_obj = run_lobby(screen, clock)
    if mode == "client":
        run_client_game(screen, clock, net_obj)
        return
    server = net_obj if mode == "host" else None  # None for solo

    # build walls
    walls = [pygame.Rect(*w) for w in WALL_LAYOUT]

    # spawn positions
    blue_spawns = [(100, HEIGHT // 2), (80, 200), (80, HEIGHT - 200)]
    red_spawns  = [(WIDTH - 100, HEIGHT // 2), (WIDTH - 80, 200), (WIDTH - 80, HEIGHT - 200)]

    # player (host is always blue)
    sx, sy = blue_spawns[0]
    player = Character(sx, sy, "blue")

    # bots
    blue_bots = []
    red_bots = []
    for i in range(NUM_BOTS_PER_TEAM):
        bx, by = blue_spawns[i % len(blue_spawns)]
        b = Bot(bx + random.randint(-20, 20), by + random.randint(-20, 20), "blue")
        blue_bots.append(b)
    for i in range(NUM_BOTS_PER_TEAM + 1):  # red has one more to balance the player
        rx, ry = red_spawns[i % len(red_spawns)]
        r = Bot(rx + random.randint(-20, 20), ry + random.randint(-20, 20), "red")
        red_bots.append(r)

    all_chars = [player] + blue_bots + red_bots

    # multiplayer: remote human players
    remote_players = {}  # client_id -> Character

    # boss
    boss = BossMonster()
    boss_spawned = False

    # projectiles & particles
    lasers = []
    particles = []

    # scores
    red_score = 0
    blue_score = 0

    running = True
    pygame.mouse.set_visible(False)

    admin = AdminPanel()
    shop = WeaponShop()
    frame_count = 0

    while running:
        clock.tick(FPS)
        frame_count += 1

        # ---- network: poll for remote player inputs ----
        if server:
            server.poll()
            # new connections -> create characters, replace bots
            for addr, cinfo in server.get_clients().items():
                cid = cinfo["id"]
                if cid not in remote_players:
                    team = cinfo["team"]
                    spawns = blue_spawns if team == "blue" else red_spawns
                    sx2, sy2 = spawns[cid % len(spawns)]
                    rp = Character(sx2 + random.randint(-30, 30),
                                   sy2 + random.randint(-30, 30), team)
                    remote_players[cid] = rp
                    all_chars.append(rp)
                    # remove one bot from that team to keep balance
                    if team == "blue" and blue_bots:
                        removed = blue_bots.pop()
                        if removed in all_chars:
                            all_chars.remove(removed)
                    elif team == "red" and red_bots:
                        removed = red_bots.pop()
                        if removed in all_chars:
                            all_chars.remove(removed)

            # apply remote inputs
            for cid, inp in server.get_client_inputs().items():
                rp = remote_players.get(cid)
                if not rp:
                    continue
                if rp.alive:
                    rp.move(inp.get("dx", 0), inp.get("dy", 0), walls)
                    rp.angle = inp.get("a", rp.angle)
                    if inp.get("sh"):
                        rp.shoot(lasers)
                    if inp.get("rl") and rp.reload_timer == 0:
                        wpn = WEAPONS[rp.weapon_id]
                        rp.reload_timer = wpn["reload"]
                        rp.ammo = 0
                    new_w = inp.get("w")
                    if new_w and new_w in WEAPON_ORDER and new_w != rp.weapon_id:
                        # allow weapon switch (client handles shop locally)
                        rp.weapon_id = new_w
                        rp.ammo = WEAPONS[new_w]["clip"]
                    rp.update_timers()
                else:
                    rp.try_respawn()

        # --- events ---
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
                continue
            # admin panel intercepts events when open
            if admin.active:
                admin.handle_event(ev)
                continue
            # weapon shop intercepts events when open
            if shop.active:
                shop.handle_event(ev, player)
                continue
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False
                if ev.key == pygame.K_r and player.alive:
                    wpn = WEAPONS[player.weapon_id]
                    player.reload_timer = wpn["reload"]
                    player.ammo = 0  # force reload
                if ev.key == pygame.K_TAB:
                    admin.open()
                if ev.key == pygame.K_b:
                    shop.open()

        # skip game logic while admin or shop is open
        if admin.active or shop.active:
            screen.fill(DARK)
            for gx in range(0, WIDTH, TILE):
                pygame.draw.line(screen, (40, 40, 50), (gx, 0), (gx, HEIGHT), 1)
            for gy in range(0, HEIGHT, TILE):
                pygame.draw.line(screen, (40, 40, 50), (0, gy), (WIDTH, gy), 1)
            for w in walls:
                pygame.draw.rect(screen, GRAY, w)
            for c in all_chars:
                c.draw(screen)
            if boss_spawned:
                boss.draw(screen)
            draw_hud(screen, player, red_score, blue_score, boss, boss_spawned, font, big_font)
            if admin.active:
                admin.draw(screen)
            if shop.active:
                shop.draw(screen, player)
            pygame.display.flip()
            continue

        # --- player input ---
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx -= settings["player_speed"]
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += settings["player_speed"]
        if keys[pygame.K_w] or keys[pygame.K_UP]:    dy -= settings["player_speed"]
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy += settings["player_speed"]
        if dx and dy:
            dx *= 0.707
            dy *= 0.707
        player.move(dx, dy, walls)

        mx, my = pygame.mouse.get_pos()
        player.angle = angle_to(player.x, player.y, mx, my)

        if pygame.mouse.get_pressed()[0]:
            player.shoot(lasers)

        player.update_timers()
        if not player.alive:
            player.try_respawn()

        # --- bot AI ---
        for b in blue_bots + red_bots:
            b.ai_update(walls, lasers, all_chars, boss if boss_spawned else None)

        # --- boss ---
        if not boss_spawned and (red_score + blue_score) >= settings["boss_trigger"]:
            boss_spawned = True
            boss.spawn()

        if boss_spawned:
            boss.update(walls, lasers, all_chars)

        # --- update lasers ---
        for laser in lasers:
            laser.update(walls)

        # --- collision: lasers vs characters ---
        for laser in lasers:
            if not laser.alive:
                continue
            # vs players/bots
            for c in all_chars:
                if not c.alive:
                    continue
                if laser.team == c.team:
                    continue  # no friendly fire
                if laser.team == "boss" or c.team != laser.team:
                    if dist(laser.x, laser.y, c.x, c.y) < Character.RADIUS + 4:
                        c.take_damage(laser.damage)
                        laser.alive = False
                        for _ in range(6):
                            particles.append(Particle(laser.x, laser.y,
                                RED if c.team == "red" else BLUE))
                        if not c.alive:
                            # credit kill & reward money
                            if laser.team == "red":
                                red_score += 1
                            elif laser.team == "blue":
                                blue_score += 1
                                # give all blue human players money
                                player.money += KILL_REWARD
                                for rp in remote_players.values():
                                    if rp.team == "blue":
                                        rp.money += KILL_REWARD
                            elif laser.team == "red":
                                for rp in remote_players.values():
                                    if rp.team == "red":
                                        rp.money += KILL_REWARD
                            player.kills += 1 if laser.team == "blue" else 0
                        break

            # vs boss
            if laser.alive and boss_spawned and boss.alive and laser.team != "boss":
                if dist(laser.x, laser.y, boss.x, boss.y) < BossMonster.RADIUS + 4:
                    boss.take_damage(laser.damage)
                    laser.alive = False
                    for _ in range(8):
                        particles.append(Particle(laser.x, laser.y, PURPLE))
                    if not boss.alive:
                        # boss killed — big reward to all humans
                        player.money += BOSS_KILL_REWARD
                        for rp in remote_players.values():
                            rp.money += BOSS_KILL_REWARD

        # clean up dead lasers
        lasers = [l for l in lasers if l.alive]

        # --- update particles ---
        for p in particles:
            p.update()
        particles = [p for p in particles if p.life > 0]

        # ---- network: broadcast state to clients ----
        if server and frame_count % NET_TICK == 0:
            base = _pack_state(all_chars, boss, boss_spawned, lasers,
                               red_score, blue_score)
            for addr, cinfo in server.get_clients().items():
                cid = cinfo["id"]
                rp = remote_players.get(cid)
                pkt = dict(base)
                if rp:
                    pkt["my"] = all_chars.index(rp)
                    pkt["$$"] = rp.money
                    pkt["ow"] = rp.owned_weapons
                    pkt["wi"] = rp.weapon_id
                    pkt["am"] = rp.ammo
                    pkt["rr"] = rp.reload_timer > 0
                    pkt["hp"] = rp.hp
                    pkt["mh"] = rp.max_hp
                    pkt["al"] = rp.alive
                    pkt["k"]  = rp.kills
                    pkt["d"]  = rp.deaths
                server.send_state_to(pkt, addr)

        # --- draw ---
        screen.fill(DARK)

        # floor grid for visual depth
        for gx in range(0, WIDTH, TILE):
            pygame.draw.line(screen, (40, 40, 50), (gx, 0), (gx, HEIGHT), 1)
        for gy in range(0, HEIGHT, TILE):
            pygame.draw.line(screen, (40, 40, 50), (0, gy), (WIDTH, gy), 1)

        # walls
        for w in walls:
            pygame.draw.rect(screen, GRAY, w)

        # spawn zone hints
        pygame.draw.circle(screen, (30, 40, 80), blue_spawns[0], 30, 1)
        pygame.draw.circle(screen, (80, 30, 30), red_spawns[0], 30, 1)

        # characters
        for c in all_chars:
            c.draw(screen)

        # player highlight ring
        if player.alive:
            pygame.draw.circle(screen, YELLOW, (int(player.x), int(player.y)),
                               Character.RADIUS + 3, 2)

        # boss
        if boss_spawned:
            boss.draw(screen)

        # lasers
        for laser in lasers:
            laser.draw(screen)

        # particles
        for p in particles:
            p.draw(screen)

        # HUD
        draw_hud(screen, player, red_score, blue_score, boss, boss_spawned, font, big_font)

        # show connected players count if hosting
        if server:
            nclients = len(server.get_clients())
            mp_lbl = font.render(f"Players online: {nclients + 1}", True, GREEN)
            screen.blit(mp_lbl, (WIDTH - mp_lbl.get_width() - 16, 40))

        pygame.display.flip()

    if server:
        server.close()
    pygame.mouse.set_visible(True)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
