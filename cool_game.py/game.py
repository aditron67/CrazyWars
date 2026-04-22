# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  EPIC SURVIVOR â€” Complete Single-File Game
#  Run: python cool_game.py/game.py   (or import from main.py)
#  Requires: pip install ursina
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
from ursina import *
from ursina import curve
import math, random, socket, threading, json, time as _time
import os, hashlib, datetime                     


# â”€â”€ Color helpers (color.rgb doesn't normalize in all ursina versions) â”€â”€â”€â”€â”€â”€â”€â”€
def _rgb(r, g, b):
    return Color(r / 255, g / 255, b / 255, 1)

def _rgba(r, g, b, a):
    return Color(r / 255, g / 255, b / 255, a / 255)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  SETTINGS & CONSTANTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
TITLE = "EPIC SURVIVOR"
WINDOW_SIZE = (1280, 720)

DEFAULT_HEALTH = 150
DEFAULT_SPEED = 5
DEFAULT_JUMP_HEIGHT = 2
DEFAULT_MELEE_DAMAGE = 15
DEFAULT_RANGED_DAMAGE = 10
DEFAULT_ATTACK_COOLDOWN = 0.4
RESPAWN_TIME = 3.0
START_COINS = 100
BOT_REACTION_TIME = 0.3
BOT_ACCURACY = 0.7

BOT_NAMES = [
    "ShadowBot", "PixelKnight", "NeonSlayer", "CubeWarrior", "BlockBreaker",
    "VoxelNinja", "DigitalDemon", "ByteBrawler", "GridGhost", "CryptoFighter",
    "RetroRanger", "PixelPuncher", "DataDuelist", "ChipChomper",
]

GAME_MODES = [
    "deathmatch", "team_battle", "capture_the_flag",
    "king_of_the_hill", "survival", "last_man_standing",
]
MODE_DISPLAY_NAMES = {
    "deathmatch": "Deathmatch",
    "team_battle": "Team Battle",
    "capture_the_flag": "Capture The Flag",
    "king_of_the_hill": "King of the Hill",
    "survival": "Survival",
    "last_man_standing": "Last Man Standing",
}

ROUND_DURATION = 120
SCORE_TO_WIN = 20
CTF_CAPTURES_TO_WIN = 3
KOTH_POINTS_TO_WIN = 100
SURVIVAL_WAVE_INTERVAL = 15
ARENA_SIZE = 40
ARENA_WALL_HEIGHT = 8

WEAPONS = {
    "fist":    {"type": "melee",  "damage": 10, "range": 2.0,  "cooldown": 0.35, "cost": 0,   "name": "Fists",           "color": (0.9, 0.8, 0.7)},
    "sword":   {"type": "melee",  "damage": 25, "range": 3.0,  "cooldown": 0.5,  "cost": 150, "name": "Pixel Sword",     "color": (0.7, 0.7, 0.9)},
    "axe":     {"type": "melee",  "damage": 35, "range": 2.5,  "cooldown": 0.8,  "cost": 250, "name": "War Axe",         "color": (0.6, 0.3, 0.1)},
    "pistol":  {"type": "ranged", "damage": 12, "range": 40,   "cooldown": 0.25, "cost": 100, "name": "Pixel Pistol",    "color": (0.3, 0.3, 0.3)},
    "rifle":   {"type": "ranged", "damage": 20, "range": 60,   "cooldown": 0.15, "cost": 300, "name": "Laser Rifle",     "color": (0.2, 0.5, 0.9)},
    "shotgun": {"type": "ranged", "damage": 30, "range": 15,   "cooldown": 0.7,  "cost": 200, "name": "Scatter Shot",    "color": (0.8, 0.4, 0.1)},
    "rocket":  {"type": "ranged", "damage": 50, "range": 45,   "cooldown": 1.5,  "cost": 500, "name": "Rocket Launcher", "color": (0.9, 0.2, 0.2)},
    "voidstar":{"type": "ranged", "damage": 1000,"range": 80,  "cooldown": 0.8,  "cost": 0,   "name": "Void Star",       "color": (0.1, 0.0, 0.3)},
}

SHOP_UPGRADES = {
    "health_boost": {"stat": "max_health",  "amount": 20,  "cost": 80,  "name": "Health Boost",  "max_level": 5},
    "speed_boost":  {"stat": "speed",       "amount": 0.8, "cost": 100, "name": "Speed Boost",   "max_level": 5},
    "armor":        {"stat": "armor",       "amount": 5,   "cost": 120, "name": "Armor Plating", "max_level": 5},
    "melee_power":  {"stat": "melee_bonus", "amount": 5,   "cost": 100, "name": "Melee Power",   "max_level": 5},
    "ranged_power": {"stat": "ranged_bonus","amount": 4,   "cost": 100, "name": "Ranged Power",  "max_level": 5},
    "jump_boost":   {"stat": "jump_height", "amount": 0.4, "cost": 90,  "name": "Jump Boost",    "max_level": 3},
    "regen":        {"stat": "regen_rate",  "amount": 1,   "cost": 150, "name": "Regeneration",  "max_level": 3},
}

SKIN_COLORS = [
    ("Red",    (0.9, 0.2, 0.2)), ("Blue",   (0.2, 0.3, 0.9)),
    ("Green",  (0.2, 0.8, 0.3)), ("Yellow", (0.9, 0.9, 0.2)),
    ("Purple", (0.7, 0.2, 0.9)), ("Orange", (0.9, 0.5, 0.1)),
    ("Cyan",   (0.1, 0.9, 0.9)), ("Pink",   (0.9, 0.4, 0.7)),
    ("White",  (0.95, 0.95, 0.95)), ("Black", (0.15, 0.15, 0.15)),
]
HAT_STYLES = ["none", "top_hat", "crown", "helmet", "cap", "horns", "halo"]
FACE_STYLES = ["default", "angry", "happy", "cool", "robot", "skull", "ninja"]
TRAIL_COLORS = [
    ("None", None), ("Fire", (1, 0.4, 0)), ("Ice", (0.3, 0.7, 1)),
    ("Toxic", (0.3, 1, 0.2)), ("Shadow", (0.3, 0, 0.5)), ("Gold", (1, 0.85, 0)),
]

TEAM_RED = (0.9, 0.2, 0.2)
TEAM_BLUE = (0.2, 0.3, 0.9)
DEFAULT_PORT = 25565
TICK_RATE = 20

# â”€â”€ Theme colors (use Color() directly so values work before app init) â”€â”€â”€â”€â”€â”€â”€â”€
GOLD = Color(180/255, 150/255, 40/255, 1)
OLIVE = Color(70/255, 100/255, 45/255, 1)
TXT = Color(200/255, 195/255, 175/255, 1)
DIM = Color(110/255, 105/255, 90/255, 1)
DARK = Color(12/255, 14/255, 10/255, 1)
DBTN = Color(28/255, 35/255, 24/255, 1)
HBTN = Color(45/255, 58/255, 36/255, 1)
_HP_G = Color(60/255, 140/255, 50/255, 1)
_HP_M = Color(180/255, 150/255, 40/255, 1)
_HP_L = Color(160/255, 50/255, 40/255, 1)
_PANEL = Color(14/255, 18/255, 12/255, 180/255)
_PANEL2 = Color(24/255, 30/255, 20/255, 220/255)
_ERR = Color(160/255, 50/255, 40/255, 1)


def random_mode():
    return random.choice(GAME_MODES)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  ANIMATION CONTROLLER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
class AnimationController:
    def __init__(self, entity):
        self.entity = entity
        self.state = "idle"
        self._anim_timer = 0
        self._bob_phase = 0
        self._is_dead = False
        self.head = None
        self.body = None
        self.left_arm = None
        self.right_arm = None
        self.left_leg = None
        self.right_leg = None

    def setup_parts(self, head, body, left_arm, right_arm, left_leg, right_leg):
        self.head = head
        self.body = body
        self.left_arm = left_arm
        self.right_arm = right_arm
        self.left_leg = left_leg
        self.right_leg = right_leg

    def play(self, state):
        if self._is_dead and state != "respawn":
            return
        if state == self.state:
            return
        self.state = state
        self._anim_timer = 0
        if state == "death":
            self._play_death()
        elif state == "hit":
            self._play_hit()
        elif state == "respawn":
            self._play_respawn()
        elif state == "attack_melee":
            self._play_melee_attack()
        elif state == "attack_ranged":
            self._play_ranged_attack()
        elif state == "jump":
            self._play_jump()

    def update(self, dt, is_moving=False):
        self._anim_timer += dt
        if self._is_dead:
            return
        if is_moving and self.state not in ("attack_melee", "attack_ranged", "hit", "jump"):
            self._animate_walk(dt)
        elif self.state == "idle":
            self._animate_idle(dt)

    def _animate_idle(self, dt):
        self._bob_phase += dt * 2
        bob = math.sin(self._bob_phase) * 0.05
        if self.body:
            self.body.y = 0.75 + bob
        if self.head:
            self.head.y = 1.45 + bob
        for limb in (self.left_arm, self.right_arm, self.left_leg, self.right_leg):
            if limb:
                limb.rotation_x = limb.rotation_x * 0.9

    def _animate_walk(self, dt):
        self._bob_phase += dt * 10
        swing = math.sin(self._bob_phase) * 35
        if self.left_arm:
            self.left_arm.rotation_x = swing
        if self.right_arm:
            self.right_arm.rotation_x = -swing
        if self.left_leg:
            self.left_leg.rotation_x = -swing
        if self.right_leg:
            self.right_leg.rotation_x = swing
        bob = abs(math.sin(self._bob_phase)) * 0.08
        if self.body:
            self.body.y = 0.75 + bob
        if self.head:
            self.head.y = 1.45 + bob

    def _play_death(self):
        self._is_dead = True
        if self.entity:
            for part in (self.head, self.body, self.left_arm, self.right_arm, self.left_leg, self.right_leg):
                if part:
                    part.color = color.red
                    part.animate_color(_rgba(100, 100, 100, 150), duration=0.8)
            self.entity.animate_rotation(
                Vec3(-90, self.entity.rotation_y, 0), duration=0.5, curve=curve.out_bounce)
            self.entity.animate_position(
                self.entity.position + Vec3(0, -0.5, 0), duration=0.5)
            self._spawn_death_particles()

    def _play_respawn(self):
        self._is_dead = False
        self.state = "idle"
        if self.entity:
            self.entity.rotation = Vec3(0, self.entity.rotation_y, 0)
            for part in (self.head, self.body, self.left_arm, self.right_arm, self.left_leg, self.right_leg):
                if part and hasattr(part, "_original_color"):
                    part.color = color.white
                    part.animate_color(part._original_color, duration=0.5)
            self.entity.scale = Vec3(0.1, 0.1, 0.1)
            self.entity.animate_scale(Vec3(1, 1, 1), duration=0.4, curve=curve.out_back)

    def _play_hit(self):
        if self.entity:
            for part in (self.head, self.body, self.left_arm, self.right_arm, self.left_leg, self.right_leg):
                if part:
                    orig = getattr(part, "_original_color", part.color)
                    part.color = _rgb(255, 30, 30)
                    part.animate_color(orig, duration=0.3, delay=0.1)
            orig_pos = Vec3(self.entity.x, self.entity.y, self.entity.z)
            shake = Vec3(random.uniform(-0.2, 0.2), 0, random.uniform(-0.2, 0.2))
            self.entity.animate_position(orig_pos + shake, duration=0.05)
            self.entity.animate_position(orig_pos, duration=0.1, delay=0.05)
        invoke(self._return_to_idle, delay=0.35)

    def _play_melee_attack(self):
        if self.right_arm:
            self.right_arm.animate_rotation(Vec3(-90, 0, 0), duration=0.1, curve=curve.out_expo)
            self.right_arm.animate_rotation(Vec3(0, 0, 0), duration=0.2, delay=0.1, curve=curve.in_out_expo)
        if self.body:
            ry = self.body.rotation_y
            self.body.animate_rotation_y(ry + 15, duration=0.1)
            self.body.animate_rotation_y(ry, duration=0.15, delay=0.1)
        invoke(self._return_to_idle, delay=0.35)

    def _play_ranged_attack(self):
        if self.right_arm:
            self.right_arm.animate_rotation(Vec3(-20, 0, 0), duration=0.05)
            self.right_arm.animate_rotation(Vec3(5, 0, 0), duration=0.08, delay=0.05)
            self.right_arm.animate_rotation(Vec3(0, 0, 0), duration=0.1, delay=0.13)
        invoke(self._return_to_idle, delay=0.25)

    def _play_jump(self):
        if self.left_leg:
            self.left_leg.animate_rotation(Vec3(-30, 0, 0), duration=0.15)
            self.left_leg.animate_rotation(Vec3(0, 0, 0), duration=0.3, delay=0.3)
        if self.right_leg:
            self.right_leg.animate_rotation(Vec3(-30, 0, 0), duration=0.15)
            self.right_leg.animate_rotation(Vec3(0, 0, 0), duration=0.3, delay=0.3)
        invoke(self._return_to_idle, delay=0.6)

    def _return_to_idle(self):
        if not self._is_dead:
            self.state = "idle"

    def _spawn_death_particles(self):
        pos = self.entity.position + Vec3(0, 1, 0)
        for _ in range(12):
            p = Entity(model="cube", scale=random.uniform(0.08, 0.2), position=pos,
                       color=_rgb(random.randint(150, 255), random.randint(30, 80), random.randint(30, 80)))
            target = pos + Vec3(random.uniform(-2, 2), random.uniform(0.5, 3), random.uniform(-2, 2))
            p.animate_position(target, duration=0.5, curve=curve.out_expo)
            p.animate_scale(0, duration=0.6)
            p.animate_color(_rgba(0, 0, 0, 0), duration=0.6)
            destroy(p, delay=0.65)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  WEAPONS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
class Projectile(Entity):
    def __init__(self, origin_pos, direction, damage, owner, max_range=50, speed=60, **kw):
        super().__init__(model="sphere", color=color.yellow, scale=0.15,
                         position=origin_pos + direction * 2.0, collider="sphere")
        self.direction = Vec3(direction).normalized()
        self.speed = speed
        self.damage = damage
        self.owner = owner
        self.max_range = max_range
        self.start_pos = Vec3(origin_pos)
        self.hit_something = False
        self._grace = 0.1  # ignore hits for first 0.1s so it clears the owner
        self.trail = Entity(model="cube", color=_rgba(255, 255, 100, 120),
                            scale=(0.05, 0.05, 0.3), parent=self, z=-0.3)

    def _get_ignore_list(self):
        ignore = [self, self.owner]
        # Also ignore all child entities of the owner (body parts)
        if self.owner:
            for child in self.owner.children:
                ignore.append(child)
                for grandchild in child.children:
                    ignore.append(grandchild)
        return ignore

    def update(self):
        if self.hit_something:
            return
        self._grace -= time.dt
        self.position += self.direction * self.speed * time.dt
        if distance(self.position, self.start_pos) > self.max_range:
            self._remove()
            return
        if self._grace > 0:
            return
        # Distance-based hit detection against all fighters (reliable)
        for e in scene.entities:
            if e == self or e == self.owner:
                continue
            if not hasattr(e, "take_damage") or not hasattr(e, "is_alive"):
                continue
            if not e.is_alive:
                continue
            # Skip teammates
            if self.owner and hasattr(self.owner, 'team') and self.owner.team and hasattr(e, 'team') and e.team == self.owner.team:
                continue
            if distance(self.position, e.position + Vec3(0, 1, 0)) < 1.5:
                e.take_damage(self.damage, self.owner)
                self._hit_particles()
                self._remove()
                return
        # Also stop on walls/ground
        hit = raycast(self.position, self.direction,
                      distance=self.speed * time.dt + 0.3, ignore=self._get_ignore_list())
        if hit.hit:
            self._remove()

    def _hit_particles(self):
        for _ in range(5):
            p = Entity(model="cube", color=color.orange, scale=0.08, position=self.position)
            p.animate_position(
                self.position + Vec3(random.uniform(-1, 1), random.uniform(0.2, 1.5), random.uniform(-1, 1)),
                duration=0.3, curve=curve.out_expo)
            p.animate_scale(0, duration=0.3)
            destroy(p, delay=0.35)

    def _remove(self):
        self.hit_something = True
        destroy(self, delay=0.01)


class VoidStarProjectile(Entity):
    """A spinning star projectile for the Void Star weapon."""

    def __init__(self, origin_pos, direction, damage, owner, max_range=80, speed=40, **kw):
        super().__init__(position=origin_pos + direction * 2.5)
        self.direction = Vec3(direction).normalized()
        self.speed = speed
        self.damage = damage
        self.owner = owner
        self.max_range = max_range
        self.start_pos = Vec3(origin_pos)
        self.hit_something = False
        self._grace = 0.15
        # Build star shape from crossed cubes
        star_color = Color(0.3, 0.0, 0.8, 1)
        glow_color = Color(0.6, 0.1, 1.0, 1)
        self.blade1 = Entity(parent=self, model='cube', color=star_color,
                              scale=(1.2, 0.08, 0.25))
        self.blade2 = Entity(parent=self, model='cube', color=star_color,
                              scale=(0.25, 0.08, 1.2))
        self.blade3 = Entity(parent=self, model='cube', color=glow_color,
                              scale=(0.9, 0.08, 0.18), rotation=(0, 45, 0))
        self.blade4 = Entity(parent=self, model='cube', color=glow_color,
                              scale=(0.18, 0.08, 0.9), rotation=(0, 45, 0))
        # Center gem
        self.core = Entity(parent=self, model='cube', color=Color(0.9, 0.2, 1.0, 1),
                           scale=0.2)
        # Trailing glow
        self.trail = Entity(parent=self, model='cube', color=Color(0.4, 0.0, 0.6, 0.5),
                            scale=(0.15, 0.15, 0.8), position=(0, 0, -0.5))

    def update(self):
        if self.hit_something:
            return
        self._grace -= time.dt
        self.position += self.direction * self.speed * time.dt
        # Spin!
        self.rotation_y += 600 * time.dt
        self.rotation_x += 200 * time.dt
        if distance(self.position, self.start_pos) > self.max_range:
            self._remove()
            return
        if self._grace > 0:
            return
        for e in scene.entities:
            if e == self or e == self.owner:
                continue
            if not hasattr(e, 'take_damage') or not hasattr(e, 'is_alive'):
                continue
            if not e.is_alive:
                continue
            if self.owner and hasattr(self.owner, 'team') and self.owner.team and hasattr(e, 'team') and e.team == self.owner.team:
                continue
            if distance(self.position, e.position + Vec3(0, 1, 0)) < 2.0:
                e.take_damage(self.damage, self.owner)
                self._hit_particles()
                self._remove()
                return
        hit = raycast(self.position, self.direction,
                      distance=self.speed * time.dt + 0.5, ignore=[self, self.owner])
        if hit.hit:
            self._remove()

    def _hit_particles(self):
        for _ in range(10):
            p = Entity(model='cube', scale=random.uniform(0.1, 0.25), position=self.position,
                       color=Color(random.uniform(0.3, 0.8), 0.0, random.uniform(0.5, 1.0), 1))
            p.animate_position(
                self.position + Vec3(random.uniform(-2, 2), random.uniform(0.5, 3), random.uniform(-2, 2)),
                duration=0.5, curve=curve.out_expo)
            p.animate_scale(0, duration=0.5)
            destroy(p, delay=0.55)

    def _remove(self):
        self.hit_something = True
        destroy(self, delay=0.01)


class MeleeHitbox(Entity):
    def __init__(self, owner, damage, reach=2.5, duration=0.15, **kw):
        fwd = owner.forward if hasattr(owner, "forward") else Vec3(0, 0, 1)
        pos = owner.position + fwd * (reach * 0.5) + Vec3(0, 1, 0)
        super().__init__(model="cube", color=_rgba(255, 100, 100, 80),
                         scale=(reach * 0.8, 1.2, reach), position=pos,
                         collider="box", visible=False)
        self.owner = owner
        self.damage = damage
        self.duration = duration
        self.timer = 0
        self.hit_entities = set()

    def update(self):
        self.timer += time.dt
        if self.timer >= self.duration:
            destroy(self)
            return
        for entity in scene.entities:
            if entity == self or entity == self.owner or entity in self.hit_entities:
                continue
            if hasattr(entity, "take_damage") and hasattr(entity, "position"):
                # Skip teammates
                if self.owner and hasattr(self.owner, 'team') and self.owner.team and hasattr(entity, 'team') and entity.team == self.owner.team:
                    continue
                if distance(self.position, entity.position) < self.scale_x:
                    entity.take_damage(self.damage, self.owner)
                    self.hit_entities.add(entity)
                    slash = Entity(model="quad", color=color.white, scale=1.5,
                                   position=entity.position + Vec3(0, 1, 0), billboard=True)
                    slash.animate_scale(0, duration=0.2)
                    slash.animate_color(_rgba(255, 50, 50, 0), duration=0.2)
                    destroy(slash, delay=0.25)


class WeaponManager:
    def __init__(self, owner):
        self.owner = owner
        self.owned_weapons = ["fist"]
        self.current_index = 0
        self.cooldown_timer = 0
        self.weapon_visual = None
        self._create_visual()

    @property
    def current_weapon_id(self):
        return self.owned_weapons[self.current_index]

    @property
    def current_weapon(self):
        return WEAPONS[self.current_weapon_id]

    def _create_visual(self):
        if self.weapon_visual:
            destroy(self.weapon_visual)
        w = self.current_weapon
        wc = _rgb(*[int(c * 255) for c in w["color"]])
        if w["type"] == "melee":
            sc = (0.15, 0.15, 0.8) if self.current_weapon_id != "fist" else (0.2, 0.2, 0.2)
            self.weapon_visual = Entity(parent=self.owner, model="cube", color=wc,
                                        scale=sc, position=(0.5, 0.7, 0.5), rotation=(0, 0, -30))
        else:
            self.weapon_visual = Entity(parent=self.owner, model="cube", color=wc,
                                        scale=(0.12, 0.12, 0.6), position=(0.5, 0.6, 0.6), rotation=(0, 0, -10))

    def add_weapon(self, weapon_id):
        if weapon_id not in self.owned_weapons:
            self.owned_weapons.append(weapon_id)

    def switch_weapon(self, direction=1):
        self.current_index = (self.current_index + direction) % len(self.owned_weapons)
        self._create_visual()

    def attack(self):
        if self.cooldown_timer > 0:
            return False
        w = self.current_weapon
        self.cooldown_timer = w["cooldown"]
        bonus = 0
        if hasattr(self.owner, "stats"):
            bonus = self.owner.stats.get("melee_bonus" if w["type"] == "melee" else "ranged_bonus", 0)
        total = w["damage"] + bonus
        if w["type"] == "melee":
            self._melee_anim()
            MeleeHitbox(owner=self.owner, damage=total, reach=w["range"])
        else:
            self._ranged_anim()
            origin = self.owner.position + Vec3(0, 1.2, 0)
            if self.current_weapon_id == 'voidstar':
                VoidStarProjectile(origin_pos=origin,
                                   direction=self.owner.forward, damage=total,
                                   owner=self.owner, max_range=w["range"])
            else:
                Projectile(origin_pos=origin,
                           direction=self.owner.forward, damage=total,
                           owner=self.owner, max_range=w["range"])
        # Send attack over network
        if hasattr(self.owner, 'game_manager'):
            gm = self.owner.game_manager
            if gm and (gm.client or gm.server):
                atk = {"wtype": w["type"], "wid": self.current_weapon_id,
                       "dmg": total, "x": round(self.owner.x, 2),
                       "y": round(self.owner.y, 2), "z": round(self.owner.z, 2),
                       "ry": round(self.owner.rotation_y, 1),
                       "range": w["range"]}
                if gm.client:
                    gm.client.send_attack(atk)
                elif gm.server:
                    gm.server._broadcast("remote_attack", atk)
        return True

    def _melee_anim(self):
        if self.weapon_visual:
            r = self.weapon_visual.rotation
            self.weapon_visual.animate_rotation(Vec3(r.x - 60, r.y, r.z), duration=0.1, curve=curve.out_expo)
            self.weapon_visual.animate_rotation(r, duration=0.15, delay=0.1, curve=curve.in_out_expo)

    def _ranged_anim(self):
        if self.weapon_visual:
            p = self.weapon_visual.position
            self.weapon_visual.animate_position(p + Vec3(0, 0, -0.15), duration=0.05, curve=curve.linear)
            self.weapon_visual.animate_position(p, duration=0.1, delay=0.05, curve=curve.out_expo)

    def tick(self, dt):
        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  PLAYER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
class Player(Entity):
    def __init__(self, game_manager, skin_color=(0.2, 0.3, 0.9), hat="none", face="default", **kw):
        super().__init__(model=None, position=(0, 1, 0), collider="box", scale=1, **kw)
        self.game_manager = game_manager
        self.tag = "player"
        self.max_health = DEFAULT_HEALTH
        self.health = self.max_health
        self.speed = DEFAULT_SPEED
        self.jump_height = DEFAULT_JUMP_HEIGHT
        self.armor = 0
        self.stats = {"melee_bonus": 0, "ranged_bonus": 0, "regen_rate": 0}
        self.coins = START_COINS
        self.kills = 0
        self.deaths = 0
        self.score = 0
        self.team = None
        self.is_alive = True
        self.respawn_timer = 0
        self.velocity_y = 0
        self.grounded = False
        self.gravity = 25
        self.mouse_sensitivity = Vec2(40, 40)
        self.camera_pivot = Entity(parent=self, y=1.5)
        self.cam_distance = 5
        self.cam_angle_x = 25  # fixed comfortable angle
        self.cam_angle_y = 0
        self.skin_color = skin_color
        self.hat_style = hat
        self.face_style = face
        self._blocking = False
        self._build_model()
        self.weapon_manager = WeaponManager(self)
        self.anim = AnimationController(self)
        self.anim.setup_parts(self.head, self.body_part, self.left_arm, self.right_arm,
                              self.left_leg, self.right_leg)
        self.upgrade_levels = {k: 0 for k in SHOP_UPGRADES}
        self._regen_timer = 0

    def _build_model(self):
        sc = self.skin_color
        c = _rgb(*[int(x * 255) for x in sc])
        darker = _rgb(*[int(x * 200) for x in sc])
        self.body_part = Entity(parent=self, model="cube", color=c,
                                scale=(0.6, 0.8, 0.4), position=(0, 0.75, 0))
        self.body_part._original_color = c
        self.head = Entity(parent=self, model="cube", color=c,
                           scale=(0.5, 0.5, 0.5), position=(0, 1.45, 0))
        self.head._original_color = c
        # Eyes
        Entity(parent=self.head, model="cube", color=color.white,
               scale=(0.15, 0.1, 0.02), position=(-0.12, 0.05, 0.26))
        Entity(parent=self.head, model="cube", color=color.white,
               scale=(0.15, 0.1, 0.02), position=(0.12, 0.05, 0.26))
        Entity(parent=self.head, model="cube", color=color.black,
               scale=(0.07, 0.07, 0.02), position=(-0.12, 0.05, 0.275))
        Entity(parent=self.head, model="cube", color=color.black,
               scale=(0.07, 0.07, 0.02), position=(0.12, 0.05, 0.275))
        # Face style
        if self.face_style == "angry":
            Entity(parent=self.head, model="cube", color=color.black,
                   scale=(0.18, 0.03, 0.02), position=(-0.12, 0.13, 0.27), rotation=(0, 0, -15))
            Entity(parent=self.head, model="cube", color=color.black,
                   scale=(0.18, 0.03, 0.02), position=(0.12, 0.13, 0.27), rotation=(0, 0, 15))
        elif self.face_style == "cool":
            Entity(parent=self.head, model="cube", color=_rgb(20, 20, 20),
                   scale=(0.45, 0.12, 0.02), position=(0, 0.05, 0.27))
        elif self.face_style == "robot":
            Entity(parent=self.head, model="cube", color=_rgb(0, 255, 0),
                   scale=(0.12, 0.05, 0.02), position=(-0.12, 0.05, 0.275))
            Entity(parent=self.head, model="cube", color=_rgb(0, 255, 0),
                   scale=(0.12, 0.05, 0.02), position=(0.12, 0.05, 0.275))
        # Mouth
        Entity(parent=self.head, model="cube", color=_rgb(50, 50, 50),
               scale=(0.2, 0.04, 0.02), position=(0, -0.1, 0.26))
        # Arms
        self.left_arm = Entity(parent=self, model="cube", color=darker,
                               scale=(0.2, 0.6, 0.25), position=(-0.45, 0.7, 0), origin=(0, 0.5, 0))
        self.left_arm._original_color = darker
        self.right_arm = Entity(parent=self, model="cube", color=darker,
                                scale=(0.2, 0.6, 0.25), position=(0.45, 0.7, 0), origin=(0, 0.5, 0))
        self.right_arm._original_color = darker
        # Legs
        self.left_leg = Entity(parent=self, model="cube", color=darker,
                               scale=(0.25, 0.6, 0.3), position=(-0.15, 0.3, 0), origin=(0, 0.5, 0))
        self.left_leg._original_color = darker
        self.right_leg = Entity(parent=self, model="cube", color=darker,
                                scale=(0.25, 0.6, 0.3), position=(0.15, 0.3, 0), origin=(0, 0.5, 0))
        self.right_leg._original_color = darker
        self._add_hat()

    def _add_hat(self):
        if self.hat_style == "top_hat":
            Entity(parent=self.head, model="cube", color=_rgb(30, 30, 30),
                   scale=(0.55, 0.4, 0.55), position=(0, 0.4, 0))
            Entity(parent=self.head, model="cube", color=_rgb(30, 30, 30),
                   scale=(0.7, 0.06, 0.7), position=(0, 0.2, 0))
        elif self.hat_style == "crown":
            Entity(parent=self.head, model="cube", color=_rgb(255, 215, 0),
                   scale=(0.5, 0.25, 0.5), position=(0, 0.35, 0))
            for x in (-0.15, 0, 0.15):
                Entity(parent=self.head, model="cube", color=_rgb(255, 215, 0),
                       scale=(0.08, 0.12, 0.08), position=(x, 0.52, 0))
        elif self.hat_style == "helmet":
            Entity(parent=self.head, model="cube", color=_rgb(120, 120, 130),
                   scale=(0.56, 0.35, 0.56), position=(0, 0.3, 0))
        elif self.hat_style == "cap":
            Entity(parent=self.head, model="cube", color=_rgb(200, 50, 50),
                   scale=(0.55, 0.15, 0.55), position=(0, 0.28, 0))
            Entity(parent=self.head, model="cube", color=_rgb(200, 50, 50),
                   scale=(0.35, 0.06, 0.25), position=(0, 0.26, 0.3))
        elif self.hat_style == "horns":
            Entity(parent=self.head, model="cube", color=_rgb(180, 50, 50),
                   scale=(0.08, 0.3, 0.08), position=(-0.2, 0.35, 0), rotation=(0, 0, 15))
            Entity(parent=self.head, model="cube", color=_rgb(180, 50, 50),
                   scale=(0.08, 0.3, 0.08), position=(0.2, 0.35, 0), rotation=(0, 0, -15))
        elif self.hat_style == "halo":
            Entity(parent=self.head, model="cube", color=_rgb(255, 255, 150),
                   scale=(0.6, 0.04, 0.6), position=(0, 0.45, 0))

    def update(self):
        if not self.is_alive:
            self.respawn_timer -= time.dt
            if self.respawn_timer <= 0:
                self.respawn()
            return
        self._handle_movement()
        self._handle_combat()
        self._handle_camera()
        self.weapon_manager.tick(time.dt)
        self.anim.update(time.dt, is_moving=self._is_moving())
        if self.stats["regen_rate"] > 0:
            self._regen_timer += time.dt
            if self._regen_timer >= 1.0:
                self._regen_timer = 0
                self.health = min(self.max_health, self.health + self.stats["regen_rate"])
        if self.y < -20:
            self.die(None)

    def _is_moving(self):
        return (held_keys["up arrow"] or held_keys["down arrow"]
                or held_keys["left arrow"] or held_keys["right arrow"])

    def _handle_movement(self):
        move_dir = Vec3(0, 0, 0)
        forward = Vec3(math.sin(math.radians(self.rotation_y)), 0, math.cos(math.radians(self.rotation_y)))
        right = Vec3(forward.z, 0, -forward.x)
        if held_keys["up arrow"]:
            move_dir += forward
        if held_keys["down arrow"]:
            move_dir -= forward
        if held_keys["right arrow"]:
            move_dir += right
        if held_keys["left arrow"]:
            move_dir -= right
        if move_dir.length() > 0:
            move_dir = move_dir.normalized()
        self.position += move_dir * self.speed * time.dt
        ray = raycast(self.position + Vec3(0, 0.5, 0), Vec3(0, -1, 0), distance=1.2, ignore=[self])
        if ray.hit:
            self.grounded = True
            self.velocity_y = 0
            self.y = ray.world_point.y
        else:
            self.grounded = False
            self.velocity_y -= self.gravity * time.dt
            self.y += self.velocity_y * time.dt
        if held_keys["space"] and self.grounded:
            self.velocity_y = math.sqrt(2 * self.gravity * self.jump_height)
            self.anim.play("jump")
        self.x = clamp(self.x, -ARENA_SIZE, ARENA_SIZE)
        self.z = clamp(self.z, -ARENA_SIZE, ARENA_SIZE)

    def _handle_combat(self):
        if held_keys["h"] or held_keys["left mouse"]:
            success = self.weapon_manager.attack()
            if success:
                w = self.weapon_manager.current_weapon
                self.anim.play("attack_melee" if w["type"] == "melee" else "attack_ranged")
        self._blocking = held_keys["b"] or held_keys["right mouse"]

    def _handle_camera(self):
        if mouse.locked:
            self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity.x
            self.cam_angle_x -= mouse.velocity[1] * self.mouse_sensitivity.y * 0.3
            self.cam_angle_x = clamp(self.cam_angle_x, 10, 45)
        cam_y = math.sin(math.radians(self.cam_angle_x)) * self.cam_distance
        cam_hz = math.cos(math.radians(self.cam_angle_x)) * self.cam_distance
        cam_offset = Vec3(
            -math.sin(math.radians(self.rotation_y)) * cam_hz,
            cam_y + 1.5,
            -math.cos(math.radians(self.rotation_y)) * cam_hz)
        target_pos = self.position + cam_offset
        camera.position = lerp(camera.position, target_pos, time.dt * 10)
        # Face same direction as player (no +180) — z=0 prevents flip
        camera.rotation = Vec3(self.cam_angle_x, self.rotation_y, 0)
        self.cam_distance = clamp(self.cam_distance, 3, 10)
        camera.clip_plane_near = 0.1

    def input(self, key):
        if not self.is_alive:
            return
        if key == "scroll up":
            self.cam_distance -= 1
        elif key == "scroll down":
            self.cam_distance += 1
        elif key == "e":
            self.weapon_manager.switch_weapon(1)

    def take_damage(self, amount, attacker):
        if not self.is_alive:
            return
        # God mode for admins
        if getattr(self, 'god_mode', False):
            return
        # No friendly fire
        if attacker and self.team and hasattr(attacker, 'team') and attacker.team == self.team:
            return
        if getattr(self, '_blocking', False):
            amount = int(amount * 0.4)
        reduced = max(1, amount - self.armor)
        self.health -= reduced
        self.anim.play("hit")
        # $1 per successful hit to attacker
        if attacker and hasattr(attacker, 'coins'):
            attacker.coins += 1
        if self.health <= 0:
            self.health = 0
            self.die(attacker)

    def die(self, killer):
        self.is_alive = False
        self.deaths += 1
        self.respawn_timer = RESPAWN_TIME
        self.anim.play("death")
        self.collider = None
        if killer and hasattr(killer, "kills"):
            killer.kills += 1
            killer.score += 1
            if hasattr(killer, "coins"):
                killer.coins += 5
        if self.game_manager and hasattr(self.game_manager, "on_player_death"):
            self.game_manager.on_player_death(self, killer)

    def respawn(self):
        self.is_alive = True
        self.health = self.max_health
        self.collider = "box"
        spawn = self.game_manager.get_spawn_point(self) if self.game_manager else Vec3(0, 2, 0)
        self.position = spawn
        self.rotation = Vec3(0, random.uniform(0, 360), 0)
        self.velocity_y = 0
        self.anim.play("respawn")

    def apply_upgrade(self, upgrade_id):
        upgrade = SHOP_UPGRADES.get(upgrade_id)
        if not upgrade:
            return False
        lv = self.upgrade_levels.get(upgrade_id, 0)
        if lv >= upgrade["max_level"]:
            return False
        cost = upgrade["cost"] * (lv + 1)
        if self.coins < cost:
            return False
        self.coins -= cost
        self.upgrade_levels[upgrade_id] = lv + 1
        stat = upgrade["stat"]
        amt = upgrade["amount"]
        if stat == "max_health":
            self.max_health += amt; self.health = self.max_health
        elif stat == "speed":
            self.speed += amt
        elif stat == "armor":
            self.armor += amt
        elif stat == "jump_height":
            self.jump_height += amt
        elif stat in self.stats:
            self.stats[stat] += amt
        return True

    def buy_weapon(self, weapon_id):
        w = WEAPONS.get(weapon_id)
        if not w or weapon_id in self.weapon_manager.owned_weapons or self.coins < w["cost"]:
            return False
        self.coins -= w["cost"]
        self.weapon_manager.add_weapon(weapon_id)
        return True


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  NPC / BOT AI
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
class NPC(Entity):
    def __init__(self, game_manager, name=None, difficulty=1.0, skin_color=None, **kw):
        super().__init__(model=None, position=(0, 1, 0), collider="box", scale=1, **kw)
        self.game_manager = game_manager
        self.tag = "npc"
        self.bot_name = name or random.choice(BOT_NAMES)
        self.difficulty = clamp(difficulty, 0.3, 2.0)
        self.max_health = DEFAULT_HEALTH
        self.health = self.max_health
        self.speed = DEFAULT_SPEED * 0.7
        self.jump_height = DEFAULT_JUMP_HEIGHT
        self.armor = 0
        self.stats = {"melee_bonus": 0, "ranged_bonus": 0, "regen_rate": 0}
        self.kills = 0
        self.deaths = 0
        self.score = 0
        self.team = None
        self.is_alive = True
        self.respawn_timer = 0
        self.coins = 0
        self.ai_state = "idle"
        self.target = None
        self.patrol_target = None
        self._state_timer = 0
        self._attack_timer = 0
        self._decision_timer = 0
        self._strafe_dir = 1
        self.velocity_y = 0
        self.grounded = False
        self.gravity = 25
        self.skin_color = skin_color or random.choice(SKIN_COLORS)[1]
        self._build_model()
        self.weapon_manager = WeaponManager(self)
        chosen = random.choice(["sword", "pistol", "rifle", "shotgun"])
        self.weapon_manager.add_weapon(chosen)
        self.weapon_manager.switch_weapon(1)
        self.anim = AnimationController(self)
        self.anim.setup_parts(self.head, self.body_part, self.left_arm, self.right_arm,
                              self.left_leg, self.right_leg)
        self._build_nameplate()

    def _build_nameplate(self):
        # Name tag
        self.nametag = Text(
            text=self.bot_name, scale=12, color=color.white,
            parent=self, position=(0, 2.4, 0), origin=(0, 0),
            billboard=True,
        )
        # Health bar background
        self.hp_bg = Entity(
            parent=self, model='cube', color=color.black,
            scale=(1.0, 0.08, 0.01), position=(0, 2.15, 0),
            billboard=True,
        )
        # Health bar fill
        self.hp_fill = Entity(
            parent=self, model='cube', color=color.green,
            scale=(0.96, 0.06, 0.01), position=(0, 2.15, 0),
            origin=(-0.5, 0, 0), billboard=True,
        )

    def _build_model(self):
        sc = self.skin_color
        c = _rgb(*[int(x * 255) for x in sc])
        darker = _rgb(*[int(x * 200) for x in sc])
        self.body_part = Entity(parent=self, model="cube", color=c,
                                scale=(0.6, 0.8, 0.4), position=(0, 0.75, 0))
        self.body_part._original_color = c
        self.head = Entity(parent=self, model="cube", color=c,
                           scale=(0.5, 0.5, 0.5), position=(0, 1.45, 0))
        self.head._original_color = c
        Entity(parent=self.head, model="cube", color=_rgb(255, 50, 50),
               scale=(0.15, 0.08, 0.02), position=(-0.12, 0.05, 0.26))
        Entity(parent=self.head, model="cube", color=_rgb(255, 50, 50),
               scale=(0.15, 0.08, 0.02), position=(0.12, 0.05, 0.26))
        self.left_arm = Entity(parent=self, model="cube", color=darker,
                               scale=(0.2, 0.6, 0.25), position=(-0.45, 0.7, 0), origin=(0, 0.5, 0))
        self.left_arm._original_color = darker
        self.right_arm = Entity(parent=self, model="cube", color=darker,
                                scale=(0.2, 0.6, 0.25), position=(0.45, 0.7, 0), origin=(0, 0.5, 0))
        self.right_arm._original_color = darker
        self.left_leg = Entity(parent=self, model="cube", color=darker,
                               scale=(0.25, 0.6, 0.3), position=(-0.15, 0.3, 0), origin=(0, 0.5, 0))
        self.left_leg._original_color = darker
        self.right_leg = Entity(parent=self, model="cube", color=darker,
                                scale=(0.25, 0.6, 0.3), position=(0.15, 0.3, 0), origin=(0, 0.5, 0))
        self.right_leg._original_color = darker
        # Bot antenna
        Entity(parent=self.head, model="cube", color=_rgb(255, 100, 100),
               scale=(0.04, 0.2, 0.04), position=(0, 0.35, 0))
        Entity(parent=self.head, model="sphere", color=_rgb(255, 50, 50),
               scale=0.08, position=(0, 0.48, 0))

    def update(self):
        if not self.is_alive:
            self.respawn_timer -= time.dt
            if self.respawn_timer <= 0:
                self.respawn()
            # Hide nameplate when dead
            if hasattr(self, 'nametag'):
                self.nametag.enabled = False
                self.hp_bg.enabled = False
                self.hp_fill.enabled = False
            return
        # Update nameplate
        if hasattr(self, 'hp_fill'):
            self.nametag.enabled = True
            self.hp_bg.enabled = True
            self.hp_fill.enabled = True
            ratio = self.health / self.max_health if self.max_health > 0 else 0
            self.hp_fill.scale_x = 0.96 * ratio
            if ratio > 0.5:
                self.hp_fill.color = color.green
            elif ratio > 0.25:
                self.hp_fill.color = color.yellow
            else:
                self.hp_fill.color = color.red
            # Color nametag by team
            if self.team == "red":
                self.nametag.color = Color(1, 0.3, 0.3, 1)
            elif self.team == "blue":
                self.nametag.color = Color(0.3, 0.4, 1, 1)
            else:
                self.nametag.color = color.white
        self._decision_timer += time.dt
        self.weapon_manager.tick(time.dt)
        self._apply_gravity()
        if self._decision_timer >= BOT_REACTION_TIME / self.difficulty:
            self._decision_timer = 0
            self._make_decision()
        self._execute_state()
        self.anim.update(time.dt, is_moving=self.ai_state in ("chase", "patrol", "flee"))

    def _apply_gravity(self):
        ray = raycast(self.position + Vec3(0, 0.5, 0), Vec3(0, -1, 0), distance=1.2, ignore=[self])
        if ray.hit:
            self.grounded = True
            self.velocity_y = 0
            self.y = ray.world_point.y
        else:
            self.grounded = False
            self.velocity_y -= self.gravity * time.dt
            self.y += self.velocity_y * time.dt
        if self.y < -20:
            self.die(None)

    def _make_decision(self):
        nearest = None
        nearest_dist = float("inf")
        for e in scene.entities:
            if e == self or not hasattr(e, "is_alive") or not e.is_alive or not hasattr(e, "health"):
                continue
            if self.team and hasattr(e, "team") and e.team == self.team:
                continue
            if e.tag in ("player", "npc"):
                d = distance(self.position, e.position)
                if d < nearest_dist:
                    nearest_dist = d
                    nearest = e
        self.target = nearest
        if nearest is None:
            self.ai_state = "patrol"
            if self.patrol_target is None or distance(self.position, self.patrol_target) < 3:
                self.patrol_target = Vec3(random.uniform(-ARENA_SIZE + 5, ARENA_SIZE - 5), 1,
                                          random.uniform(-ARENA_SIZE + 5, ARENA_SIZE - 5))
            return
        attack_range = self.weapon_manager.current_weapon["range"] * 0.8
        if self.health < self.max_health * 0.2 and nearest_dist < 10:
            self.ai_state = "flee"
        elif nearest_dist <= attack_range:
            self.ai_state = "attack"
        else:
            self.ai_state = "chase"
        if random.random() < 0.3:
            self._strafe_dir *= -1

    def _execute_state(self):
        if self.ai_state == "chase" and self.target:
            self._move_toward(self.target.position)
        elif self.ai_state == "attack" and self.target:
            self._face_target(self.target.position)
            self._attack_timer += time.dt
            if self._attack_timer >= self.weapon_manager.current_weapon["cooldown"]:
                self._attack_timer = 0
                if random.random() < BOT_ACCURACY * self.difficulty:
                    self.weapon_manager.attack()
                    w = self.weapon_manager.current_weapon
                    self.anim.play("attack_melee" if w["type"] == "melee" else "attack_ranged")
            right = Vec3(self.forward.z, 0, -self.forward.x)
            self.position += right * self._strafe_dir * self.speed * 0.4 * time.dt
        elif self.ai_state == "flee" and self.target:
            away = (self.position - self.target.position).normalized()
            self._move_toward(self.position + away * 10)
        elif self.ai_state == "patrol" and self.patrol_target:
            self._move_toward(self.patrol_target)
        self.x = clamp(self.x, -ARENA_SIZE, ARENA_SIZE)
        self.z = clamp(self.z, -ARENA_SIZE, ARENA_SIZE)

    def _move_toward(self, target_pos):
        direction = Vec3(target_pos.x - self.x, 0, target_pos.z - self.z)
        if direction.length() > 0.5:
            direction = direction.normalized()
            self._face_target(target_pos)
            # Check for wall/block collision before moving
            move_ray = raycast(self.position + Vec3(0, 0.5, 0), direction, distance=0.8, ignore=[self])
            if move_ray.hit:
                # Blocked — try to jump over if grounded
                if self.grounded:
                    self.velocity_y = math.sqrt(2 * self.gravity * self.jump_height)
            else:
                self.position += direction * self.speed * time.dt

    def _face_target(self, target_pos):
        dx = target_pos.x - self.x
        dz = target_pos.z - self.z
        angle = math.degrees(math.atan2(dx, dz))
        self.rotation_y = lerp(self.rotation_y, angle, time.dt * 10)

    def take_damage(self, amount, attacker):
        if not self.is_alive:
            return
        # No friendly fire
        if attacker and self.team and hasattr(attacker, 'team') and attacker.team == self.team:
            return
        reduced = max(1, amount - self.armor)
        self.health -= reduced
        self.anim.play("hit")
        # $1 per successful hit to attacker
        if attacker and hasattr(attacker, 'coins'):
            attacker.coins += 1
        if attacker and attacker != self:
            self.target = attacker
            self.ai_state = "chase"
        if self.health <= 0:
            self.health = 0
            self.die(attacker)

    def die(self, killer):
        self.is_alive = False
        self.deaths += 1
        self.respawn_timer = RESPAWN_TIME + random.uniform(0, 2)
        self.anim.play("death")
        self.collider = None
        if killer and hasattr(killer, "kills"):
            killer.kills += 1
            killer.score += 1
            if hasattr(killer, "coins"):
                killer.coins += 5
        if self.game_manager and hasattr(self.game_manager, "on_player_death"):
            self.game_manager.on_player_death(self, killer)

    def respawn(self):
        self.is_alive = True
        self.health = self.max_health
        self.collider = "box"
        spawn = self.game_manager.get_spawn_point(self) if self.game_manager else Vec3(
            random.uniform(-20, 20), 2, random.uniform(-20, 20))
        self.position = spawn
        self.rotation = Vec3(0, random.uniform(0, 360), 0)
        self.velocity_y = 0
        self.ai_state = "idle"
        self.anim.play("respawn")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  ARENA / WORLD
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
class Arena:
    def __init__(self):
        self.entities = []

    def build(self):
        self.clear()
        self._build_ground()
        self._build_walls()
        self._build_obstacles()
        self._build_decorations()
        self._build_lighting()

    def clear(self):
        for e in self.entities:
            if e:
                destroy(e)
        self.entities.clear()

    def _build_ground(self):
        ground = Entity(model="cube", color=Color(0.45, 0.48, 0.52, 1),
                        scale=(ARENA_SIZE * 2 + 2, 1, ARENA_SIZE * 2 + 2),
                        position=(0, -0.5, 0), collider="box")
        self.entities.append(ground)
        # Center cross pattern
        for axis in ('x', 'z'):
            strip = Entity(model="cube", color=Color(0.55, 0.58, 0.62, 1),
                           scale=(ARENA_SIZE * 2, 0.05, 2) if axis == 'x' else (2, 0.05, ARENA_SIZE * 2),
                           position=(0, 0.01, 0))
            self.entities.append(strip)

    def _build_walls(self):
        wc = Color(0.4, 0.42, 0.48, 1)
        h = ARENA_WALL_HEIGHT
        sz = ARENA_SIZE
        walls = [
            (Vec3(0, h / 2, -sz), Vec3(sz * 2 + 2, h, 1)),
            (Vec3(0, h / 2, sz), Vec3(sz * 2 + 2, h, 1)),
            (Vec3(sz, h / 2, 0), Vec3(1, h, sz * 2 + 2)),
            (Vec3(-sz, h / 2, 0), Vec3(1, h, sz * 2 + 2)),
        ]
        for pos, scale in walls:
            w = Entity(model="cube", color=wc, position=pos, scale=scale, collider="box")
            self.entities.append(w)

    def _build_obstacles(self):
        platform = Entity(model="cube", color=Color(0.6, 0.65, 0.7, 1),
                          scale=(6, 1.5, 6), position=(0, 0.75, 0), collider="box")
        self.entities.append(platform)
        for angle in [0, 90, 180, 270]:
            ramp = Entity(model="cube", color=Color(0.55, 0.6, 0.65, 1), scale=(2, 0.3, 4),
                          position=(math.sin(math.radians(angle)) * 5, 0.5,
                                    math.cos(math.radians(angle)) * 5),
                          rotation=(15 if angle in (0, 180) else 0, angle,
                                    0 if angle in (0, 180) else 15),
                          collider="box")
            self.entities.append(ramp)
        for _ in range(10):
            size = random.uniform(1.5, 3)
            height = random.uniform(1, 3)
            pos = Vec3(random.uniform(-ARENA_SIZE + 5, ARENA_SIZE - 5), height / 2,
                       random.uniform(-ARENA_SIZE + 5, ARENA_SIZE - 5))
            if distance(Vec3(pos.x, 0, pos.z), Vec3(0, 0, 0)) < 8:
                continue
            block = Entity(model="cube",
                           color=Color(random.uniform(0.45, 0.65), random.uniform(0.5, 0.7), random.uniform(0.55, 0.72), 1),
                           scale=(size, height, size), position=pos, collider="box")
            self.entities.append(block)
        corners = [(-ARENA_SIZE + 6, ARENA_SIZE - 6), (ARENA_SIZE - 6, ARENA_SIZE - 6),
                   (-ARENA_SIZE + 6, -ARENA_SIZE + 6), (ARENA_SIZE - 6, -ARENA_SIZE + 6)]
        for cx, cz in corners:
            plat = Entity(model="cube", color=Color(0.5, 0.53, 0.58, 1),
                          scale=(5, 4, 5), position=(cx, 2, cz), collider="box")
            self.entities.append(plat)
            ladder = Entity(model="cube", color=Color(0.7, 0.55, 0.3, 1),
                            scale=(0.5, 4, 0.1), position=(cx, 2, cz + 2.5))
            self.entities.append(ladder)

    def _build_decorations(self):
        for i in range(4):
            angle = i * 90
            dx = math.sin(math.radians(angle)) * (ARENA_SIZE - 3)
            dz = math.cos(math.radians(angle)) * (ARENA_SIZE - 3)
            pole = Entity(model="cube", color=Color(0.55, 0.55, 0.57, 1),
                          scale=(0.2, 5, 0.2), position=(dx, 2.5, dz))
            self.entities.append(pole)
            light = Entity(model="cube", color=Color(1, 0.94, 0.7, 1),
                           scale=(0.6, 0.3, 0.6), position=(dx, 5.2, dz))
            self.entities.append(light)

    def _build_lighting(self):
        # No explicit lights — Ursina's default unlit shader shows colors directly
        # Just set a subtle fog for depth
        scene.fog_color = Color(0.12, 0.13, 0.16, 1)
        scene.fog_density = 0.002


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  GAME MODES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
def _recolor_fighter(fighter, team_color):
    """Repaint all body parts of a fighter to their team color (red or blue)."""
    tc = Color(team_color[0], team_color[1], team_color[2], 1)
    tc_dark = Color(team_color[0] * 0.7, team_color[1] * 0.7, team_color[2] * 0.7, 1)
    for part in ('body_part', 'head'):
        p = getattr(fighter, part, None)
        if p:
            p.color = tc
            p._original_color = tc
    for part in ('left_arm', 'right_arm', 'left_leg', 'right_leg'):
        p = getattr(fighter, part, None)
        if p:
            p.color = tc_dark
            p._original_color = tc_dark
    # Update nameplate color if it exists
    if hasattr(fighter, 'nametag'):
        fighter.nametag.color = color.red if team_color == TEAM_RED else Color(0.3, 0.5, 1, 1)


class BaseGameMode:
    name = "Base"
    description = "Override me"

    def __init__(self, game_manager):
        self.gm = game_manager
        self.timer = ROUND_DURATION
        self.is_active = False
        self.winner = None
        self.entities = []

    def start(self):
        self.is_active = True
        self.timer = ROUND_DURATION
        self.winner = None
        self._setup()

    def _setup(self):
        pass

    def update(self, dt):
        if not self.is_active:
            return
        self.timer -= dt
        if self.timer <= 0:
            self.end_round()
            return
        self._check_win_condition()
        self._update(dt)

    def _update(self, dt):
        pass

    def _check_win_condition(self):
        pass

    def end_round(self):
        self.is_active = False
        if not self.winner:
            self.winner = self._determine_winner()
        self._cleanup()
        if self.gm:
            self.gm.on_round_end(self.winner)

    def _determine_winner(self):
        fighters = self.gm.get_all_fighters() if self.gm else []
        return max(fighters, key=lambda f: f.score) if fighters else None

    def _cleanup(self):
        for e in self.entities:
            if e:
                destroy(e)
        self.entities.clear()

    def on_player_death(self, victim, killer):
        pass

    def get_spawn_point(self, entity):
        return Vec3(random.uniform(-ARENA_SIZE + 5, ARENA_SIZE - 5), 2,
                    random.uniform(-ARENA_SIZE + 5, ARENA_SIZE - 5))

    def get_scoreboard_info(self):
        fighters = self.gm.get_all_fighters() if self.gm else []
        return [(getattr(f, "bot_name", "Player"), f.score)
                for f in sorted(fighters, key=lambda x: -x.score)]


class DeathmatchMode(BaseGameMode):
    name = "Deathmatch"
    description = "Free-for-all! Most kills wins."

    def _setup(self):
        for f in self.gm.get_all_fighters():
            f.score = 0
            f.kills = 0

    def _check_win_condition(self):
        for f in self.gm.get_all_fighters():
            if f.kills >= SCORE_TO_WIN:
                self.winner = f
                self.end_round()
                return

    def get_scoreboard_info(self):
        fighters = self.gm.get_all_fighters()
        return [(getattr(f, "bot_name", "You"), f"Kills: {f.kills}")
                for f in sorted(fighters, key=lambda x: -x.kills)]


class TeamBattleMode(BaseGameMode):
    name = "Team Battle"
    description = "Red vs Blue â€” team with most kills wins!"

    def __init__(self, gm):
        super().__init__(gm)
        self.red_score = 0
        self.blue_score = 0

    def _setup(self):
        self.red_score = 0
        self.blue_score = 0
        fighters = self.gm.get_all_fighters()
        random.shuffle(fighters)
        for i, f in enumerate(fighters):
            f.team = "red" if i % 2 == 0 else "blue"
            f.score = 0
            f.kills = 0
            tc = TEAM_RED if f.team == "red" else TEAM_BLUE
            # Repaint body parts to team color
            _recolor_fighter(f, tc)
            ind = Entity(parent=f, model="cube", color=_rgb(*[int(c * 255) for c in tc]),
                         scale=(0.7, 0.08, 0.7), position=(0, 2.0, 0), billboard=True)
            self.entities.append(ind)
        rb = Entity(model="cube", color=_rgb(*[int(c * 255) for c in TEAM_RED]),
                    scale=(2, 6, 0.3), position=(-ARENA_SIZE + 2, 3, 0))
        bb = Entity(model="cube", color=_rgb(*[int(c * 255) for c in TEAM_BLUE]),
                    scale=(2, 6, 0.3), position=(ARENA_SIZE - 2, 3, 0))
        self.entities.extend([rb, bb])

    def on_player_death(self, victim, killer):
        if killer and hasattr(killer, "team"):
            if killer.team == "red":
                self.red_score += 1
            elif killer.team == "blue":
                self.blue_score += 1

    def _check_win_condition(self):
        if self.red_score >= SCORE_TO_WIN:
            self.winner = "Red Team"
            self.end_round()
        elif self.blue_score >= SCORE_TO_WIN:
            self.winner = "Blue Team"
            self.end_round()

    def _determine_winner(self):
        return "Red Team" if self.red_score >= self.blue_score else "Blue Team"

    def get_spawn_point(self, entity):
        if hasattr(entity, "team"):
            if entity.team == "red":
                return Vec3(random.uniform(-ARENA_SIZE, -ARENA_SIZE / 2), 2, random.uniform(-10, 10))
            return Vec3(random.uniform(ARENA_SIZE / 2, ARENA_SIZE), 2, random.uniform(-10, 10))
        return super().get_spawn_point(entity)

    def get_scoreboard_info(self):
        return [("Red Team", f"Score: {self.red_score}"), ("Blue Team", f"Score: {self.blue_score}")]

    def _cleanup(self):
        for f in self.gm.get_all_fighters():
            f.team = None
        super()._cleanup()


class CaptureTheFlagMode(BaseGameMode):
    name = "Capture The Flag"
    description = "Steal the enemy flag and bring it home!"

    def __init__(self, gm):
        super().__init__(gm)
        self.red_captures = 0
        self.blue_captures = 0
        self.red_flag = None
        self.blue_flag = None
        self.red_base = Vec3(-ARENA_SIZE + 5, 1, 0)
        self.blue_base = Vec3(ARENA_SIZE - 5, 1, 0)
        self.flag_carriers = {}

    def _setup(self):
        self.red_captures = 0
        self.blue_captures = 0
        self.flag_carriers.clear()
        fighters = self.gm.get_all_fighters()
        random.shuffle(fighters)
        for i, f in enumerate(fighters):
            f.team = "red" if i % 2 == 0 else "blue"
            f.score = 0
            _recolor_fighter(f, TEAM_RED if f.team == "red" else TEAM_BLUE)
        self.red_flag = self._create_flag(self.red_base, TEAM_RED)
        self.blue_flag = self._create_flag(self.blue_base, TEAM_BLUE)
        self.entities.extend([self.red_flag, self.blue_flag])
        for base_pos, tc in [(self.red_base, TEAM_RED), (self.blue_base, TEAM_BLUE)]:
            bm = Entity(model="cube", color=_rgb(*[int(c * 255) for c in tc]),
                        scale=(4, 0.2, 4), position=base_pos - Vec3(0, 0.8, 0), alpha=0.5)
            self.entities.append(bm)

    def _create_flag(self, pos, tc):
        flag = Entity(model="cube", color=_rgb(*[int(c * 255) for c in tc]),
                      scale=(0.15, 2, 0.15), position=pos)
        flag.home_pos = Vec3(pos)
        flag.is_carried = False
        flag.carrier = None
        cloth = Entity(parent=flag, model="cube", color=_rgb(*[int(c * 255) for c in tc]),
                       scale=(3, 2, 0.1), position=(0.25, 0.35, 0))
        self.entities.append(cloth)
        return flag

    def _update(self, dt):
        for f in self.gm.get_all_fighters():
            if not f.is_alive:
                continue
            if f.team == "red" and self.blue_flag and not self.blue_flag.is_carried:
                if distance(f.position, self.blue_flag.position) < 3:
                    self._pickup(f, self.blue_flag)
            elif f.team == "blue" and self.red_flag and not self.red_flag.is_carried:
                if distance(f.position, self.red_flag.position) < 3:
                    self._pickup(f, self.red_flag)
            if f in self.flag_carriers:
                flag = self.flag_carriers[f]
                flag.position = f.position + Vec3(0, 2.5, 0)
                base = self.red_base if f.team == "red" else self.blue_base
                if distance(f.position, base) < 4:
                    self._capture(f, flag)
        for flag in [self.red_flag, self.blue_flag]:
            if flag and not flag.is_carried:
                flag.rotation_y += 60 * dt

    def _pickup(self, carrier, flag):
        flag.is_carried = True
        flag.carrier = carrier
        self.flag_carriers[carrier] = flag

    def _capture(self, carrier, flag):
        if carrier.team == "red":
            self.red_captures += 1
        else:
            self.blue_captures += 1
        carrier.score += 5
        carrier.coins = getattr(carrier, "coins", 0) + 25
        flag.position = flag.home_pos
        flag.is_carried = False
        flag.carrier = None
        self.flag_carriers.pop(carrier, None)

    def on_player_death(self, victim, killer):
        if victim in self.flag_carriers:
            flag = self.flag_carriers[victim]
            flag.is_carried = False
            flag.carrier = None
            flag.position = Vec3(victim.position.x, 1, victim.position.z)
            del self.flag_carriers[victim]

    def _check_win_condition(self):
        if self.red_captures >= CTF_CAPTURES_TO_WIN:
            self.winner = "Red Team"
            self.end_round()
        elif self.blue_captures >= CTF_CAPTURES_TO_WIN:
            self.winner = "Blue Team"
            self.end_round()

    def _determine_winner(self):
        return "Red Team" if self.red_captures >= self.blue_captures else "Blue Team"

    def get_spawn_point(self, entity):
        if hasattr(entity, "team"):
            base = self.red_base if entity.team == "red" else self.blue_base
            return base + Vec3(random.uniform(-3, 3), 1, random.uniform(-3, 3))
        return super().get_spawn_point(entity)

    def get_scoreboard_info(self):
        return [("Red Team", f"Captures: {self.red_captures}/{CTF_CAPTURES_TO_WIN}"),
                ("Blue Team", f"Captures: {self.blue_captures}/{CTF_CAPTURES_TO_WIN}")]

    def _cleanup(self):
        for f in self.gm.get_all_fighters():
            f.team = None
        super()._cleanup()


class KingOfTheHillMode(BaseGameMode):
    name = "King of the Hill"
    description = "Hold the hill zone to score points!"

    def __init__(self, gm):
        super().__init__(gm)
        self.hill_pos = Vec3(0, 0, 0)
        self.hill_radius = 6
        self.player_scores = {}
        self.hill_zone = None
        self.hill_indicator = None
        self._hill_timer = 0

    def _setup(self):
        self.player_scores.clear()
        for f in self.gm.get_all_fighters():
            self.player_scores[f] = 0
            f.score = 0
        self.hill_pos = Vec3(random.uniform(-ARENA_SIZE / 2, ARENA_SIZE / 2), 0.1,
                             random.uniform(-ARENA_SIZE / 2, ARENA_SIZE / 2))
        self.hill_zone = Entity(model="cube", color=_rgba(255, 215, 0, 80),
                                scale=(self.hill_radius * 2, 0.15, self.hill_radius * 2),
                                position=self.hill_pos)
        self.entities.append(self.hill_zone)
        self.hill_indicator = Entity(model="cube", color=_rgba(255, 215, 0, 150),
                                     scale=(0.5, 8, 0.5), position=self.hill_pos + Vec3(0, 4, 0))
        self.entities.append(self.hill_indicator)
        for dx, dz in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            post = Entity(model="cube", color=_rgb(200, 170, 50), scale=(0.3, 3, 0.3),
                          position=self.hill_pos + Vec3(dx * self.hill_radius, 1.5, dz * self.hill_radius))
            self.entities.append(post)

    def _update(self, dt):
        self._hill_timer += dt
        if self.hill_indicator:
            self.hill_indicator.rotation_y += 30 * dt
        if self._hill_timer >= 0.5:
            self._hill_timer = 0
            occupants = []
            for f in self.gm.get_all_fighters():
                if not f.is_alive:
                    continue
                d = distance(Vec3(f.x, 0, f.z), Vec3(self.hill_pos.x, 0, self.hill_pos.z))
                if d <= self.hill_radius:
                    occupants.append(f)
            if len(occupants) == 1:
                f = occupants[0]
                self.player_scores[f] = self.player_scores.get(f, 0) + 2
                f.score = self.player_scores[f]
            elif len(occupants) > 1:
                for f in occupants:
                    self.player_scores[f] = self.player_scores.get(f, 0) + 1
                    f.score = self.player_scores[f]
            if self.hill_zone:
                if len(occupants) == 0:
                    self.hill_zone.color = _rgba(255, 215, 0, 80)
                elif len(occupants) == 1:
                    self.hill_zone.color = _rgba(100, 255, 100, 120)
                else:
                    self.hill_zone.color = _rgba(255, 100, 100, 120)
        if int(self.timer) % 30 == 0 and int(self.timer) != int(ROUND_DURATION):
            self._move_hill()

    def _move_hill(self):
        new_pos = Vec3(random.uniform(-ARENA_SIZE / 2, ARENA_SIZE / 2), 0.1,
                       random.uniform(-ARENA_SIZE / 2, ARENA_SIZE / 2))
        self.hill_pos = new_pos
        if self.hill_zone:
            self.hill_zone.animate_position(new_pos, duration=2, curve=curve.in_out_expo)
        if self.hill_indicator:
            self.hill_indicator.animate_position(new_pos + Vec3(0, 4, 0), duration=2, curve=curve.in_out_expo)

    def _check_win_condition(self):
        for f, sc in self.player_scores.items():
            if sc >= KOTH_POINTS_TO_WIN:
                self.winner = f
                self.end_round()
                return

    def _determine_winner(self):
        return max(self.player_scores, key=self.player_scores.get) if self.player_scores else None

    def get_scoreboard_info(self):
        ss = sorted(self.player_scores.items(), key=lambda x: -x[1])
        return [(getattr(f, "bot_name", "You"), f"Points: {s}/{KOTH_POINTS_TO_WIN}") for f, s in ss[:8]]


class SurvivalMode(BaseGameMode):
    name = "Survival"
    description = "Survive waves of enemies as long as you can!"

    def __init__(self, gm):
        super().__init__(gm)
        self.wave = 0
        self.wave_timer = 0
        self.enemies = []
        self.enemies_per_wave = 3
        self.total_kills = 0

    def _setup(self):
        self.wave = 0
        self.wave_timer = SURVIVAL_WAVE_INTERVAL
        self.enemies.clear()
        self.total_kills = 0
        self.timer = 999
        for f in self.gm.get_all_fighters():
            f.score = 0
            f.team = "player"
        self._spawn_wave()

    def _spawn_wave(self):
        self.wave += 1
        count = self.enemies_per_wave + self.wave * 2
        diff = 0.5 + self.wave * 0.15
        for i in range(count):
            enemy = NPC(self.gm, name=f"Wave{self.wave}_Enemy{i+1}",
                        difficulty=min(diff, 2.0),
                        skin_color=(0.4 + random.uniform(-0.1, 0.1), 0.1, 0.1))
            enemy.team = "enemy"
            enemy.max_health = int(DEFAULT_HEALTH * (0.6 + self.wave * 0.2))
            enemy.health = enemy.max_health
            enemy.speed = DEFAULT_SPEED * (0.7 + self.wave * 0.05)
            side = random.choice(["n", "s", "e", "w"])
            if side == "n":
                pos = Vec3(random.uniform(-ARENA_SIZE, ARENA_SIZE), 2, -ARENA_SIZE + 2)
            elif side == "s":
                pos = Vec3(random.uniform(-ARENA_SIZE, ARENA_SIZE), 2, ARENA_SIZE - 2)
            elif side == "e":
                pos = Vec3(ARENA_SIZE - 2, 2, random.uniform(-ARENA_SIZE, ARENA_SIZE))
            else:
                pos = Vec3(-ARENA_SIZE + 2, 2, random.uniform(-ARENA_SIZE, ARENA_SIZE))
            enemy.position = pos
            self.enemies.append(enemy)

    def _update(self, dt):
        # Remove truly dead enemies (prevent ghost respawns)
        for e in self.enemies:
            if not e.is_alive:
                e.respawn_timer = 9999
        alive_enemies = [e for e in self.enemies if e.is_alive]
        if len(alive_enemies) == 0:
            self.wave_timer -= dt
            if self.wave_timer <= 0:
                self.wave_timer = 3  # 3 seconds between waves (was 15)
                # Clean up old dead enemies
                for e in self.enemies:
                    if not e.is_alive:
                        destroy(e)
                self.enemies = [e for e in self.enemies if e.is_alive]
                self._spawn_wave()
        players = [f for f in self.gm.get_all_fighters() if f.tag == "player" or f.team == "player"]
        if not any(p.is_alive for p in players):
            self.end_round()

    def on_player_death(self, victim, killer):
        if victim in self.enemies:
            self.total_kills += 1

    def _determine_winner(self):
        return f"Survived {self.wave} waves! ({self.total_kills} kills)"

    def _cleanup(self):
        for e in self.enemies:
            if e:
                destroy(e)
        self.enemies.clear()
        for f in self.gm.get_all_fighters():
            f.team = None
        super()._cleanup()

    def get_scoreboard_info(self):
        return [("Wave", str(self.wave)),
                ("Enemies Left", str(sum(1 for e in self.enemies if e.is_alive))),
                ("Total Kills", str(self.total_kills))]


class LastManStandingMode(BaseGameMode):
    name = "Last Man Standing"
    description = "One life â€” last player alive wins!"

    def __init__(self, gm):
        super().__init__(gm)
        self.eliminated = []

    def _setup(self):
        self.eliminated.clear()
        for f in self.gm.get_all_fighters():
            f.score = 0
            f.kills = 0
            f.health = f.max_health
            f.is_alive = True

    def on_player_death(self, victim, killer):
        if victim not in self.eliminated:
            self.eliminated.append(victim)
            victim.respawn_timer = 9999

    def _check_win_condition(self):
        alive = [f for f in self.gm.get_all_fighters() if f.is_alive]
        if len(alive) <= 1:
            self.winner = alive[0] if alive else (self.eliminated[-1] if self.eliminated else None)
            self.end_round()

    def _determine_winner(self):
        alive = [f for f in self.gm.get_all_fighters() if f.is_alive]
        return alive[0] if alive else None

    def get_scoreboard_info(self):
        return [(getattr(f, "bot_name", "You"), "ALIVE" if f.is_alive else "ELIMINATED")
                for f in self.gm.get_all_fighters()]

    def _cleanup(self):
        for f in self.gm.get_all_fighters():
            f.respawn_timer = 0
        self.eliminated.clear()
        super()._cleanup()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  NETWORKING
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
class NetworkMessage:
    @staticmethod
    def encode(msg_type, data):
        return (json.dumps({"type": msg_type, "data": data}) + "\n").encode("utf-8")

    @staticmethod
    def decode(raw):
        msgs = []
        for line in raw.decode("utf-8", errors="replace").strip().split("\n"):
            if line.strip():
                try:
                    msgs.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        return msgs


class GameServer:
    def __init__(self, port=None, max_players=8):
        self.port = port or DEFAULT_PORT
        self.max_players = max_players
        self.clients = {}
        self.player_states = {}
        self.server_socket = None
        self.running = False
        self._next_id = 1
        self._lock = threading.Lock()
        self.on_player_join = None
        self.on_player_leave = None
        self.on_player_update = None
        self.on_remote_attack = None

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(("0.0.0.0", self.port))
        self.server_socket.listen(self.max_players)
        self.server_socket.settimeout(1.0)
        self.running = True
        threading.Thread(target=self._accept_loop, daemon=True).start()
        print(f"[Server] Listening on port {self.port}")

    def _accept_loop(self):
        while self.running:
            try:
                conn, addr = self.server_socket.accept()
                pid = self._next_id
                self._next_id += 1
                with self._lock:
                    self.clients[conn] = pid
                    self.player_states[pid] = {"x": 0, "y": 1, "z": 0, "ry": 0, "hp": 100, "alive": True}
                conn.sendall(NetworkMessage.encode("welcome", {"id": pid, "players": list(self.player_states.keys())}))
                self._broadcast("player_join", {"id": pid})
                if self.on_player_join:
                    self.on_player_join(pid)
                threading.Thread(target=self._client_loop, args=(conn, pid), daemon=True).start()
            except socket.timeout:
                continue
            except OSError:
                break

    def _client_loop(self, conn, pid):
        buf = b""
        while self.running:
            try:
                data = conn.recv(4096)
                if not data:
                    break
                buf += data
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    for msg in NetworkMessage.decode(line + b"\n"):
                        self._handle(conn, pid, msg)
            except (ConnectionResetError, OSError):
                break
        with self._lock:
            self.clients.pop(conn, None)
            self.player_states.pop(pid, None)
        self._broadcast("player_leave", {"id": pid})
        if self.on_player_leave:
            self.on_player_leave(pid)
        try:
            conn.close()
        except OSError:
            pass

    def _handle(self, conn, pid, msg):
        mt = msg.get("type")
        data = msg.get("data", {})
        if mt == "state":
            with self._lock:
                self.player_states[pid] = data
            self._broadcast_raw(NetworkMessage.encode("remote_state", {"id": pid, **data}), exclude=conn)
            # Notify host too
            if self.on_player_update:
                self.on_player_update(pid, data)
        elif mt == "attack":
            self._broadcast("remote_attack", {"id": pid, **data}, exclude=conn)
            # Notify host too
            if self.on_remote_attack:
                self.on_remote_attack({"id": pid, **data})
        elif mt == "chat":
            safe = str(data.get("text", ""))[:200]
            self._broadcast("chat", {"id": pid, "text": safe})

    def _broadcast(self, msg_type, data, exclude=None):
        self._broadcast_raw(NetworkMessage.encode(msg_type, data), exclude)

    def _broadcast_raw(self, raw, exclude=None):
        with self._lock:
            for conn in list(self.clients.keys()):
                if conn == exclude:
                    continue
                try:
                    conn.sendall(raw)
                except (OSError, BrokenPipeError):
                    pass

    def broadcast_game_state(self, state):
        self._broadcast("game_state", state)

    def stop(self):
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except OSError:
                pass


class GameClient:
    def __init__(self):
        self.socket = None
        self.connected = False
        self.my_id = None
        self.remote_players = {}
        self._buffer = b""
        self._lock = threading.Lock()
        self.on_welcome = None
        self.on_player_join = None
        self.on_player_leave = None
        self.on_remote_state = None
        self.on_remote_attack = None
        self.on_game_state = None
        self.on_chat = None

    def connect(self, host, port=None):
        port = port or DEFAULT_PORT
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(5.0)
        try:
            self.socket.connect((host, port))
            self.socket.settimeout(0.1)
            self.connected = True
            threading.Thread(target=self._recv_loop, daemon=True).start()
            return True
        except (ConnectionRefusedError, socket.timeout, OSError):
            return False

    def _recv_loop(self):
        while self.connected:
            try:
                data = self.socket.recv(4096)
                if not data:
                    self.connected = False
                    break
                self._buffer += data
                while b"\n" in self._buffer:
                    line, self._buffer = self._buffer.split(b"\n", 1)
                    for msg in NetworkMessage.decode(line + b"\n"):
                        self._handle(msg)
            except socket.timeout:
                continue
            except (ConnectionResetError, OSError):
                self.connected = False
                break

    def _handle(self, msg):
        mt = msg.get("type")
        data = msg.get("data", {})
        if mt == "welcome":
            self.my_id = data.get("id")
            if self.on_welcome:
                self.on_welcome(data)
        elif mt == "player_join":
            pid = data.get("id")
            with self._lock:
                self.remote_players[pid] = {}
            if self.on_player_join:
                self.on_player_join(pid)
        elif mt == "player_leave":
            pid = data.get("id")
            with self._lock:
                self.remote_players.pop(pid, None)
            if self.on_player_leave:
                self.on_player_leave(pid)
        elif mt == "remote_state":
            pid = data.pop("id", None)
            if pid:
                with self._lock:
                    self.remote_players[pid] = data
                if self.on_remote_state:
                    self.on_remote_state(pid, data)
        elif mt == "remote_attack":
            if self.on_remote_attack:
                self.on_remote_attack(data)
        elif mt == "game_state":
            if self.on_game_state:
                self.on_game_state(data)
        elif mt == "chat":
            if self.on_chat:
                self.on_chat(data)

    def send_state(self, state):
        if self.connected:
            try:
                self.socket.sendall(NetworkMessage.encode("state", state))
            except (OSError, BrokenPipeError):
                self.connected = False

    def send_attack(self, data):
        if self.connected:
            try:
                self.socket.sendall(NetworkMessage.encode("attack", data))
            except (OSError, BrokenPipeError):
                self.connected = False

    def send_chat(self, text):
        if self.connected:
            try:
                self.socket.sendall(NetworkMessage.encode("chat", {"text": str(text)[:200]}))
            except (OSError, BrokenPipeError):
                self.connected = False

    def disconnect(self):
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except OSError:
                pass


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  UI â€” HUD
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
class HUD:
    def __init__(self, player, gm):
        self.player = player
        self.gm = gm
        self._ents = []

        def _e(*a, **k):
            e = Entity(*a, **k); self._ents.append(e); return e
        def _t(*a, **k):
            t = Text(*a, **k); self._ents.append(t); return t

        _e(parent=camera.ui, model="quad", color=_rgba(20, 20, 18, 200), scale=(0.38, 0.03), position=(-0.44, 0.45))
        self.hp_bar = _e(parent=camera.ui, model="quad", color=_HP_G, scale=(0.38, 0.03),
                         position=(-0.44, 0.45), origin=(-0.5, 0))
        self.hp_txt = _t(text="100/100", scale=0.7, position=(-0.44, 0.438), origin=(0, 0), color=TXT)
        _e(parent=camera.ui, model="quad", color=_PANEL, scale=(0.22, 0.05), position=(0.42, -0.42))
        self.wpn = _t(text="Fists", scale=0.8, position=(0.42, -0.42), origin=(0, 0), color=GOLD)
        _t(text="[E] Switch", scale=0.5, position=(0.42, -0.455), origin=(0, 0), color=DIM)
        self.coins_txt = _t(text="$100", scale=0.9, position=(0.54, 0.45), origin=(1, 0), color=GOLD)
        self.score_txt = _t(text="K:0 D:0", scale=0.7, position=(0, 0.45), origin=(0, 0), color=TXT)
        self.timer_txt = _t(text="2:00", scale=1.1, position=(0, 0.415), origin=(0, 0), color=TXT)
        self.mode_txt = _t(text="", scale=0.7, position=(0, 0.47), origin=(0, 0), color=OLIVE)
        # Team indicator
        self.team_txt = _t(text="", scale=1.0, position=(0, 0.39), origin=(0, 0), color=TXT)
        self.kf_txt = []
        for i in range(5):
            self.kf_txt.append(_t(text="", scale=0.55, position=(0.55, 0.35 - i * 0.026), origin=(1, 0), color=DIM))
        self.kf = []
        _e(parent=camera.ui, model="quad", color=_rgba(180, 170, 140, 100), scale=(0.001, 0.014), position=(0, 0))
        _e(parent=camera.ui, model="quad", color=_rgba(180, 170, 140, 100), scale=(0.014, 0.001), position=(0, 0))
        _e(parent=camera.ui, model="quad", color=_PANEL, scale=(0.15, 0.26), position=(-0.55, 0.02))
        _t(text="CONTROLS", scale=0.55, position=(-0.55, 0.12), origin=(0, 0), color=GOLD)
        for i, ln in enumerate(["Arrows Move", "H  Attack", "B  Block", "Space Jump",
                                 "E  Weapon", "S  Shop", "Tab Score", "Esc Quit"]):
            _t(text=ln, scale=0.4, position=(-0.55, 0.09 - i * 0.025), origin=(0, 0), color=DIM)
        self._r_bg = _e(parent=camera.ui, model="quad", color=_rgba(8, 8, 6, 200),
                        scale=(3, 3), position=(0, 0), z=5, enabled=False)
        self._r_t1 = _t(text="RESPAWNING...", scale=1.8, position=(0, 0.04), origin=(0, 0),
                        color=GOLD, enabled=False)
        self._r_t2 = _t(text="", scale=1.3, position=(0, -0.04), origin=(0, 0), color=TXT, enabled=False)
        self._updater = Entity(parent=camera.ui, visible=False)
        self._updater.update = self._update
        self._ents.append(self._updater)

    def _update(self):
        p = self.player
        if not p:
            return
        r = p.health / p.max_health if p.max_health > 0 else 0
        self.hp_bar.scale_x = 0.38 * r
        self.hp_bar.color = _HP_G if r > 0.5 else (_HP_M if r > 0.25 else _HP_L)
        self.hp_txt.text = f"{int(p.health)}/{int(p.max_health)}"
        self.wpn.text = p.weapon_manager.current_weapon["name"]
        self.coins_txt.text = f"${int(p.coins)}"
        self.score_txt.text = f"K:{p.kills} D:{p.deaths}"
        if self.gm and self.gm.current_mode:
            t = max(0, int(self.gm.current_mode.timer))
            self.timer_txt.text = f"{t // 60}:{t % 60:02d}"
            self.mode_txt.text = self.gm.current_mode.name
            # Show team
            if p.team == "red":
                self.team_txt.text = "RED TEAM"
                self.team_txt.color = Color(0.9, 0.2, 0.2, 1)
            elif p.team == "blue":
                self.team_txt.text = "BLUE TEAM"
                self.team_txt.color = Color(0.2, 0.3, 0.9, 1)
            else:
                self.team_txt.text = ""
        alive = p.is_alive
        self._r_bg.enabled = not alive
        self._r_t1.enabled = not alive
        self._r_t2.enabled = not alive
        if not alive:
            self._r_t2.text = f"{p.respawn_timer:.1f}s"
        self.kf = [k for k in self.kf if k[1] > 0]
        for k in self.kf:
            k[1] -= time.dt
        for i, t in enumerate(self.kf_txt):
            t.text = self.kf[i][0] if i < len(self.kf) else ""

    def add_kill_feed(self, killer, victim):
        self.kf.insert(0, [f"{killer} > {victim}", 5.0])
        if len(self.kf) > 5:
            self.kf.pop()

    def destroy_hud(self):
        for e in self._ents:
            if e:
                destroy(e)
        self._ents.clear()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  UI â€” SHOP
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
class ShopUI:
    def __init__(self, player, on_close=None):
        self.player = player
        self.on_close = on_close
        self._ents = []
        self._built = False

    def _build(self):
        if self._built:
            return
        self._built = True

        def _e(*a, **k):
            e = Entity(*a, **k); self._ents.append(e); return e
        def _t(*a, **k):
            t = Text(*a, **k); self._ents.append(t); return t

        _e(parent=camera.ui, model="quad", color=DARK, scale=(3, 3), z=10)
        _t(text="SHOP", scale=1.6, position=(0, 0.42), origin=(0, 0), color=GOLD)
        self.coins_txt = _t(text=f"${self.player.coins if self.player else 0}", scale=0.9,
                            position=(0, 0.36), origin=(0, 0), color=GOLD)
        b = Button(parent=camera.ui, text="X", scale=(0.04, 0.04), position=(0.55, 0.42),
                   color=_ERR, text_color=TXT)
        b.on_click = self._close
        self._ents.append(b)

        _t(text="WEAPONS", scale=1, position=(-0.35, 0.28), origin=(0, 0), color=OLIVE)
        x0, yp, col = -0.48, 0.2, 0
        for wid, wd in WEAPONS.items():
            if wd["cost"] == 0:
                continue
            self._item(wd["name"], f"DMG:{wd['damage']}", wd["cost"],
                       (x0 + col * 0.25, yp), lambda w=wid: self._bw(w))
            col += 1
            if col >= 4:
                col = 0; yp -= 0.11

        _t(text="UPGRADES", scale=1, position=(-0.35, yp - 0.05), origin=(0, 0), color=OLIVE)
        yp -= 0.11; col = 0
        for uid, ud in SHOP_UPGRADES.items():
            lv = self.player.upgrade_levels.get(uid, 0) if self.player else 0
            c = ud["cost"] * (lv + 1) if lv < ud["max_level"] else "MAX"
            self._item(ud["name"], f"Lv{lv}/{ud['max_level']}", c,
                       (x0 + col * 0.25, yp), lambda u=uid: self._bu(u))
            col += 1
            if col >= 4:
                col = 0; yp -= 0.11

        self.status = _t(text="", scale=0.9, position=(0, -0.38), origin=(0, 0), color=OLIVE)

    def _item(self, name, info, cost, pos, cb):
        p = Entity(parent=camera.ui, model="quad", color=_PANEL2, scale=(0.23, 0.09), position=pos)
        self._ents.append(p)
        t1 = Text(parent=camera.ui, text=name, scale=0.65, position=(pos[0], pos[1] + 0.025), origin=(0, 0), color=TXT)
        self._ents.append(t1)
        t2 = Text(parent=camera.ui, text=info, scale=0.5, position=(pos[0], pos[1] + 0.005), origin=(0, 0), color=DIM)
        self._ents.append(t2)
        cs = f"${cost}" if isinstance(cost, int) else str(cost)
        t3 = Text(parent=camera.ui, text=cs, scale=0.55, position=(pos[0], pos[1] - 0.015), origin=(0, 0), color=GOLD)
        self._ents.append(t3)
        b = Button(parent=camera.ui, text="BUY", scale=(0.065, 0.025), position=(pos[0] + 0.08, pos[1]),
                   color=_rgba(40, 70, 35, 220), text_color=TXT)
        b.text_entity.scale *= 0.7
        b.on_click = cb
        self._ents.append(b)

    def _bw(self, wid):
        if not self.player:
            return
        if self.player.buy_weapon(wid):
            self.status.text = f"Bought {WEAPONS[wid]['name']}!"
            self.status.color = OLIVE
        else:
            self.status.text = "Owned!" if wid in self.player.weapon_manager.owned_weapons else "No coins!"
            self.status.color = _ERR
        self.coins_txt.text = f"${int(self.player.coins)}"

    def _bu(self, uid):
        if not self.player:
            return
        if self.player.apply_upgrade(uid):
            self.status.text = "Upgraded!"
            self.status.color = OLIVE
        else:
            self.status.text = "Max or no coins!"
            self.status.color = _ERR
        self.coins_txt.text = f"${int(self.player.coins)}"

    def _close(self):
        self.do_hide()
        if self.on_close:
            self.on_close()

    def do_show(self):
        self._build()
        for e in self._ents:
            e.enabled = True
        if self.player:
            self.coins_txt.text = f"${int(self.player.coins)}"
        mouse.locked = False
        mouse.visible = True

    def do_hide(self):
        for e in self._ents:
            e.enabled = False


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  UI â€” CUSTOMIZE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
class CustomizeUI:
    def __init__(self, on_close=None):
        self.on_close = on_close
        self.sel = {"skin": 0, "hat": 0, "face": 0, "trail": 0}
        self._ents = []
        self._built = False

    def _build(self):
        if self._built:
            return
        self._built = True

        def _e(*a, **k):
            e = Entity(*a, **k); self._ents.append(e); return e
        def _t(*a, **k):
            t = Text(*a, **k); self._ents.append(t); return t

        _e(parent=camera.ui, model="quad", color=DARK, scale=(3, 3), z=10)
        _t(text="CUSTOMIZE", scale=2.8, position=(0, 0.42), origin=(0, 0), color=GOLD)
        b = Button(parent=camera.ui, text="X", scale=(0.04, 0.04), position=(0.55, 0.42),
                   color=_ERR, text_color=TXT)
        b.on_click = self._close
        self._ents.append(b)
        # Skin
        _t(text="SKIN COLOR", scale=0.9, position=(-0.4, 0.28), origin=(0, 0), color=TXT)
        self.skin_lbl = _t(text=SKIN_COLORS[0][0], scale=0.8, position=(-0.4, 0.22), origin=(0, 0), color=GOLD)
        self._arrow("L", (-0.5, 0.22), lambda: self._cy("skin", -1))
        self._arrow("R", (-0.3, 0.22), lambda: self._cy("skin", 1))
        self.skin_pv = _e(parent=camera.ui, model="quad",
                          color=_rgb(*[int(c * 255) for c in SKIN_COLORS[0][1]]),
                          scale=(0.05, 0.05), position=(-0.4, 0.17))
        # Hat
        _t(text="HAT", scale=0.9, position=(0, 0.28), origin=(0, 0), color=TXT)
        self.hat_lbl = _t(text=HAT_STYLES[0].replace("_", " ").title(), scale=0.8,
                          position=(0, 0.22), origin=(0, 0), color=GOLD)
        self._arrow("L", (-0.1, 0.22), lambda: self._cy("hat", -1))
        self._arrow("R", (0.1, 0.22), lambda: self._cy("hat", 1))
        # Face
        _t(text="FACE", scale=0.9, position=(0.4, 0.28), origin=(0, 0), color=TXT)
        self.face_lbl = _t(text=FACE_STYLES[0].replace("_", " ").title(), scale=0.8,
                           position=(0.4, 0.22), origin=(0, 0), color=GOLD)
        self._arrow("L", (0.3, 0.22), lambda: self._cy("face", -1))
        self._arrow("R", (0.5, 0.22), lambda: self._cy("face", 1))
        # Trail
        _t(text="TRAIL", scale=0.9, position=(0, 0.08), origin=(0, 0), color=TXT)
        self.trail_lbl = _t(text=TRAIL_COLORS[0][0], scale=0.8, position=(0, 0.02), origin=(0, 0), color=GOLD)
        self._arrow("L", (-0.1, 0.02), lambda: self._cy("trail", -1))
        self._arrow("R", (0.1, 0.02), lambda: self._cy("trail", 1))
        # Preview
        _t(text="PREVIEW", scale=0.9, position=(0, -0.08), origin=(0, 0), color=TXT)
        self.pv_body = _e(parent=camera.ui, model="quad",
                          color=_rgb(*[int(c * 255) for c in SKIN_COLORS[0][1]]),
                          scale=(0.07, 0.11), position=(0, -0.2))
        self.pv_head = _e(parent=camera.ui, model="quad",
                          color=_rgb(*[int(c * 255) for c in SKIN_COLORS[0][1]]),
                          scale=(0.06, 0.06), position=(0, -0.12))
        ab = Button(parent=camera.ui, text="APPLY & CLOSE", scale=(0.28, 0.055), position=(0, -0.36),
                    color=_rgba(40, 70, 35, 220), text_color=TXT)
        ab.text_entity.scale *= 0.7
        ab.on_click = self._close
        self._ents.append(ab)

    def _arrow(self, t, p, cb):
        b = Button(parent=camera.ui, text=t, scale=(0.035, 0.035), position=p, color=_PANEL2, text_color=TXT)
        b.on_click = cb
        self._ents.append(b)

    def _cy(self, cat, d):
        if cat == "skin":
            self.sel["skin"] = (self.sel["skin"] + d) % len(SKIN_COLORS)
            n, c = SKIN_COLORS[self.sel["skin"]]
            self.skin_lbl.text = n
            rc = _rgb(*[int(x * 255) for x in c])
            self.skin_pv.color = rc
            self.pv_body.color = rc
            self.pv_head.color = rc
        elif cat == "hat":
            self.sel["hat"] = (self.sel["hat"] + d) % len(HAT_STYLES)
            self.hat_lbl.text = HAT_STYLES[self.sel["hat"]].replace("_", " ").title()
        elif cat == "face":
            self.sel["face"] = (self.sel["face"] + d) % len(FACE_STYLES)
            self.face_lbl.text = FACE_STYLES[self.sel["face"]].replace("_", " ").title()
        elif cat == "trail":
            self.sel["trail"] = (self.sel["trail"] + d) % len(TRAIL_COLORS)
            self.trail_lbl.text = TRAIL_COLORS[self.sel["trail"]][0]

    def get_customization(self):
        return {"skin_color": SKIN_COLORS[self.sel["skin"]][1], "hat": HAT_STYLES[self.sel["hat"]],
                "face": FACE_STYLES[self.sel["face"]], "trail": TRAIL_COLORS[self.sel["trail"]]}

    def _close(self):
        self.hide()
        if self.on_close:
            self.on_close()

    def show(self):
        self._build()
        for e in self._ents:
            e.enabled = True
        mouse.locked = False
        mouse.visible = True

    def hide(self):
        for e in self._ents:
            e.enabled = False


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  UI â€” SCOREBOARD + ROUND END
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
class ScoreboardUI:
    def __init__(self, gm):
        self.gm = gm
        self._ents = []
        self._built = False

    def _build(self):
        if self._built:
            return
        self._built = True

        def _e(*a, **k):
            e = Entity(*a, **k); self._ents.append(e); return e
        def _t(*a, **k):
            t = Text(*a, **k); self._ents.append(t); return t

        _e(parent=camera.ui, model="quad", color=_rgba(10, 12, 8, 220), scale=(0.7, 0.65), z=5)
        _t(text="SCOREBOARD", scale=1.8, position=(0, 0.26), origin=(0, 0), color=GOLD)
        self.rows = []
        for i in range(10):
            n = _t(text="", scale=0.8, position=(-0.16, 0.18 - i * 0.04), origin=(0, 0), color=TXT)
            s = _t(text="", scale=0.8, position=(0.16, 0.18 - i * 0.04), origin=(0, 0), color=DIM)
            self.rows.append((n, s))
        # Server IP line at bottom
        self.ip_txt = _t(text="", scale=0.55, position=(0, -0.26), origin=(0, 0), color=DIM)

    def _refresh(self):
        if self.gm and self.gm.current_mode:
            info = self.gm.current_mode.get_scoreboard_info()
            for i, (n, s) in enumerate(self.rows):
                if i < len(info):
                    n.text = str(info[i][0])
                    s.text = str(info[i][1])
                else:
                    n.text = ""
                    s.text = ""
        # Show server IP
        if hasattr(self, 'ip_txt'):
            ip = "Offline"
            if self.gm.server:
                try:
                    import socket as _sk
                    s = _sk.socket(_sk.AF_INET, _sk.SOCK_DGRAM)
                    s.connect(('8.8.8.8', 80))
                    ip = f"Hosting: {s.getsockname()[0]}:{DEFAULT_PORT}"
                    s.close()
                except Exception:
                    ip = f"Hosting: localhost:{DEFAULT_PORT}"
            elif self.gm.client and self.gm.client.connected:
                ip = "Connected to server"
            self.ip_txt.text = ip

    def do_show(self):
        self._build()
        for e in self._ents:
            e.enabled = True
        self._refresh()

    def do_hide(self):
        for e in self._ents:
            e.enabled = False


class RoundEndUI:
    def __init__(self):
        self._ents = []

        def _e(*a, **k):
            e = Entity(*a, **k); self._ents.append(e); return e
        def _t(*a, **k):
            t = Text(*a, **k); self._ents.append(t); return t

        _e(parent=camera.ui, model="quad", color=_rgba(8, 10, 6, 230), scale=(3, 3), z=5)
        _t(text="ROUND OVER", scale=2.8, position=(0, 0.14), origin=(0, 0), color=GOLD)
        self.winner_txt = _t(text="", scale=1.8, position=(0, 0.03), origin=(0, 0), color=OLIVE)
        _t(text="Next round starting...", scale=0.9, position=(0, -0.07), origin=(0, 0), color=DIM)

    def show_result(self, winner):
        for e in self._ents:
            e.enabled = True
        if hasattr(winner, "bot_name"):
            self.winner_txt.text = f"Winner: {winner.bot_name}"
        elif hasattr(winner, "tag") and winner.tag == "player":
            self.winner_txt.text = "Winner: YOU!"
        else:
            self.winner_txt.text = f"Winner: {winner}"
        mouse.locked = False
        mouse.visible = True

    def do_hide(self):
        for e in self._ents:
            e.enabled = False


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  GAME MANAGER â€” plain class, NOT Entity
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
class RemotePlayer(Entity):
    def __init__(self, player_id, **kw):
        super().__init__(model=None, position=(0, 1, 0), scale=1, **kw)
        self.player_id = player_id
        self.tag = "remote"
        self.is_alive = True
        self.health = 150
        self.max_health = 150
        self.kills = 0
        self.deaths = 0
        self.score = 0
        self.team = None
        self.bot_name = f"Player_{player_id}"
        # Build visible body (green tint to distinguish from bots)
        rc = Color(0.2, 0.8, 0.4, 1)
        dk = Color(0.15, 0.6, 0.3, 1)
        self.body_part = Entity(parent=self, model="cube", color=rc,
                                scale=(0.6, 0.8, 0.4), position=(0, 0.75, 0))
        self.head = Entity(parent=self, model="cube", color=rc,
                           scale=(0.5, 0.5, 0.5), position=(0, 1.45, 0))
        Entity(parent=self.head, model="cube", color=color.white,
               scale=(0.15, 0.1, 0.02), position=(-0.12, 0.05, 0.26))
        Entity(parent=self.head, model="cube", color=color.white,
               scale=(0.15, 0.1, 0.02), position=(0.12, 0.05, 0.26))
        Entity(parent=self.head, model="cube", color=color.black,
               scale=(0.07, 0.07, 0.02), position=(-0.12, 0.05, 0.275))
        Entity(parent=self.head, model="cube", color=color.black,
               scale=(0.07, 0.07, 0.02), position=(0.12, 0.05, 0.275))
        self.left_arm = Entity(parent=self, model="cube", color=dk,
                               scale=(0.2, 0.6, 0.25), position=(-0.45, 0.7, 0))
        self.right_arm = Entity(parent=self, model="cube", color=dk,
                                scale=(0.2, 0.6, 0.25), position=(0.45, 0.7, 0))
        self.left_leg = Entity(parent=self, model="cube", color=dk,
                               scale=(0.25, 0.6, 0.3), position=(-0.15, 0.3, 0))
        self.right_leg = Entity(parent=self, model="cube", color=dk,
                                scale=(0.25, 0.6, 0.3), position=(0.15, 0.3, 0))
        # Name tag
        self.nametag = Text(text=self.bot_name, scale=12, color=color.white,
                            parent=self, position=(0, 2.4, 0), origin=(0, 0), billboard=True)
        # Health bar
        self.hp_bg = Entity(parent=self, model='cube', color=color.black,
                            scale=(1.0, 0.08, 0.01), position=(0, 2.15, 0), billboard=True)
        self.hp_fill = Entity(parent=self, model='cube', color=color.green,
                              scale=(0.96, 0.06, 0.01), position=(0, 2.15, 0),
                              origin=(-0.5, 0, 0), billboard=True)

    def apply_state(self, state):
        target = Vec3(state.get("x", self.x), state.get("y", self.y), state.get("z", self.z))
        self.position = lerp(self.position, target, 0.3)
        self.rotation_y = state.get("ry", self.rotation_y)
        self.health = state.get("hp", self.health)
        self.is_alive = state.get("alive", True)
        name = state.get("name", self.bot_name)
        if name != self.bot_name:
            self.bot_name = name
            self.nametag.text = name
        # Update team color
        new_team = state.get("team", "") or None
        if new_team != self.team:
            self.team = new_team
            self._apply_team_color()
        # Update health bar
        ratio = self.health / self.max_health if self.max_health > 0 else 0
        self.hp_fill.scale_x = 0.96 * ratio
        self.hp_fill.color = color.green if ratio > 0.5 else (color.yellow if ratio > 0.25 else color.red)
        # Hide when dead
        self.visible = self.is_alive
        for c in self.children:
            c.enabled = self.is_alive

    def _apply_team_color(self):
        if self.team == "red":
            main = Color(0.9, 0.2, 0.2, 1)
            dark = Color(0.7, 0.15, 0.15, 1)
            tag_c = Color(1, 0.3, 0.3, 1)
        elif self.team == "blue":
            main = Color(0.2, 0.3, 0.9, 1)
            dark = Color(0.15, 0.2, 0.7, 1)
            tag_c = Color(0.3, 0.4, 1, 1)
        else:
            main = Color(0.2, 0.8, 0.4, 1)
            dark = Color(0.15, 0.6, 0.3, 1)
            tag_c = color.white
        self.body_part.color = main
        self.head.color = main
        for limb in (self.left_arm, self.right_arm, self.left_leg, self.right_leg):
            limb.color = dark
        self.nametag.color = tag_c

    def take_damage(self, amount, attacker):
        if not self.is_alive:
            return
        self.health -= amount
        # Flash red
        self.body_part.color = color.red
        self.head.color = color.red
        invoke(self._apply_team_color, delay=0.2)
        if self.health <= 0:
            self.health = 0
            self.is_alive = False
            if attacker and hasattr(attacker, 'kills'):
                attacker.kills += 1
                attacker.score += 1
            if attacker and hasattr(attacker, 'coins'):
                attacker.coins += 5


class GameManager:
    """Central game controller â€” plain class, NOT Entity."""

    MODE_MAP = {
        "deathmatch": DeathmatchMode,
        "team_battle": TeamBattleMode,
        "capture_the_flag": CaptureTheFlagMode,
        "king_of_the_hill": KingOfTheHillMode,
        "survival": SurvivalMode,
        "last_man_standing": LastManStandingMode,
    }

    def __init__(self):
        self.state = "menu"
        self.player = None
        self.bots = []
        self.remote_players = {}
        self.current_mode = None
        self.arena = Arena()
        self.hud = None
        self.round_end_timer = 0
        self.server = None
        self.client = None
        self.is_host = False
        self.net_tick_timer = 0
        self.desired_players = 4
        self._scoreboard = None
        self._shop_ui = None
        self._round_end_ui = None

    def get_all_fighters(self):
        fighters = []
        if self.player:
            fighters.append(self.player)
        fighters.extend(self.bots)
        return fighters

    def get_spawn_point(self, entity):
        if self.current_mode:
            return self.current_mode.get_spawn_point(entity)
        return Vec3(random.uniform(-20, 20), 2, random.uniform(-20, 20))

    def on_player_death(self, victim, killer):
        if self.current_mode:
            self.current_mode.on_player_death(victim, killer)
        if self.hud:
            k = getattr(killer, "bot_name", "???") if killer else "World"
            v = getattr(victim, "bot_name", "???")
            self.hud.add_kill_feed(k, v)

    def on_round_end(self, winner):
        self.state = "round_end"
        self.round_end_timer = 6
        self._round_end_ui = RoundEndUI()
        self._round_end_ui.show_result(winner)

    def start_game(self, skin_color=(0.2, 0.3, 0.9), hat="none", face="default", username="Player"):
        self.state = "playing"
        self.username = username
        self.arena.build()
        self._cleanup_fighters()
        self.player = Player(self, skin_color=skin_color, hat=hat, face=face)
        self.player.bot_name = username
        self.player.position = Vec3(0, 2, 0)
        num_bots = max(0, self.desired_players - 1 - len(self.remote_players))
        for i in range(num_bots):
            bot = NPC(self, difficulty=random.uniform(0.3, 0.8))
            bot.position = Vec3(random.uniform(-ARENA_SIZE + 5, ARENA_SIZE - 5), 2,
                                random.uniform(-ARENA_SIZE + 5, ARENA_SIZE - 5))
            self.bots.append(bot)
        mode_key = random_mode()
        self.current_mode = self.MODE_MAP[mode_key](self)
        self.current_mode.start()
        self.hud = HUD(self.player, self)
        mouse.locked = True
        mouse.visible = False
        print(f"[Game] Mode: {self.current_mode.name}")

    def _cleanup_fighters(self):
        if self.player:
            destroy(self.player)
            self.player = None
        for b in self.bots:
            destroy(b)
        self.bots.clear()
        if self.hud:
            self.hud.destroy_hud()
            self.hud = None

    def next_round(self):
        try:
            if self._round_end_ui:
                self._round_end_ui.do_hide()
                self._round_end_ui = None
            self.arena.clear()
            skin = self.player.skin_color if self.player else (0.2, 0.3, 0.9)
            hat = self.player.hat_style if self.player else "none"
            face = self.player.face_style if self.player else "default"
            coins = self.player.coins if self.player else START_COINS
            weapons = list(self.player.weapon_manager.owned_weapons) if self.player else ["fist"]
            weapon_idx = self.player.weapon_manager.current_index if self.player else 0
            upgrades = dict(self.player.upgrade_levels) if self.player else {}
            uname = getattr(self, 'username', 'Player')
            self.start_game(skin_color=skin, hat=hat, face=face, username=uname)
            if self.player:
                self.player.coins = coins
                for w in weapons:
                    self.player.weapon_manager.add_weapon(w)
                self.player.upgrade_levels = upgrades
                # Re-apply stat upgrades
                for uid, lv in upgrades.items():
                    upg = SHOP_UPGRADES.get(uid)
                    if upg and lv > 0:
                        stat = upg["stat"]
                        amt = upg["amount"] * lv
                        if stat == "max_health":
                            self.player.max_health = DEFAULT_HEALTH + amt
                            self.player.health = self.player.max_health
                        elif stat == "speed":
                            self.player.speed = DEFAULT_SPEED + amt
                        elif stat == "armor":
                            self.player.armor = amt
                        elif stat == "jump_height":
                            self.player.jump_height = DEFAULT_JUMP_HEIGHT + amt
                        elif stat in self.player.stats:
                            self.player.stats[stat] = amt
                # Restore weapon selection
                if weapon_idx < len(self.player.weapon_manager.owned_weapons):
                    self.player.weapon_manager.current_index = weapon_idx
                    self.player.weapon_manager._create_visual()
            print("[Game] New round started!")
        except Exception as e:
            print(f"[ERROR] next_round failed: {e}")
            import traceback; traceback.print_exc()

    def host_game(self, port=None):
        self.server = GameServer(port=port)
        self.server.on_player_join = self._on_net_join
        self.server.on_player_leave = self._on_net_leave
        self.server.on_player_update = self._on_remote_state
        self.server.on_remote_attack = self._on_remote_attack
        self.server.start()
        self.is_host = True

    def join_game(self, host_ip, port=None):
        self.client = GameClient()
        self.client.on_player_join = self._on_net_join
        self.client.on_player_leave = self._on_net_leave
        self.client.on_remote_state = self._on_remote_state
        self.client.on_remote_attack = self._on_remote_attack
        self.client.on_game_state = self._on_game_state
        try:
            result = self.client.connect(host_ip, port)
            if result:
                print(f'[Net] Connected to {host_ip}')
            else:
                print(f'[Net] Failed to connect to {host_ip}')
            return result
        except Exception as e:
            print(f'[Net] Connection error: {e}')
            return False

    def _on_net_join(self, pid):
        if pid not in self.remote_players:
            self.remote_players[pid] = RemotePlayer(pid)

    def _on_net_leave(self, pid):
        rp = self.remote_players.pop(pid, None)
        if rp:
            destroy(rp)

    def _on_remote_state(self, pid, state):
        if pid in self.remote_players:
            self.remote_players[pid].apply_state(state)

    def _on_remote_attack(self, data):
        """Spawn attack from remote player on our screen."""
        pid = data.get('id')
        rp = self.remote_players.get(pid) if pid else None
        # Use remote player as owner, or create a dummy position
        owner_pos = Vec3(data.get('x', 0), data.get('y', 1), data.get('z', 0))
        ry = data.get('ry', 0)
        fwd = Vec3(math.sin(math.radians(ry)), 0, math.cos(math.radians(ry)))
        dmg = data.get('dmg', 10)
        wid = data.get('wid', 'fist')
        wtype = data.get('wtype', 'melee')
        wrange = data.get('range', 3)
        owner = rp if rp else Entity(visible=False)
        if wtype == 'melee':
            MeleeHitbox(owner=owner, damage=dmg, reach=wrange)
        else:
            origin = owner_pos + Vec3(0, 1.2, 0)
            if wid == 'voidstar':
                VoidStarProjectile(origin_pos=origin, direction=fwd, damage=dmg,
                                   owner=owner, max_range=wrange)
            else:
                Projectile(origin_pos=origin, direction=fwd, damage=dmg,
                           owner=owner, max_range=wrange)

    def _on_game_state(self, data):
        """Client receives game mode state from host."""
        if not self.current_mode:
            return
        if 'timer' in data:
            self.current_mode.timer = data['timer']
        if hasattr(self.current_mode, 'red_score') and 'red_score' in data:
            self.current_mode.red_score = data['red_score']
            self.current_mode.blue_score = data['blue_score']
        if hasattr(self.current_mode, 'red_captures') and 'red_caps' in data:
            self.current_mode.red_captures = data['red_caps']
            self.current_mode.blue_captures = data['blue_caps']
        if hasattr(self.current_mode, 'wave') and 'wave' in data:
            self.current_mode.wave = data['wave']

    def _send_state(self):
        if not self.player:
            return
        st = {"x": round(self.player.x, 2), "y": round(self.player.y, 2),
              "z": round(self.player.z, 2), "ry": round(self.player.rotation_y, 1),
              "hp": int(self.player.health), "alive": self.player.is_alive,
              "name": getattr(self, 'username', 'Player'),
              "team": self.player.team or ""}
        if self.client:
            self.client.send_state(st)
        elif self.server:
            self.server.broadcast_game_state(st)
            # Host also sends game mode state to all clients
            if self.current_mode:
                mode_st = {"mode": self.current_mode.name,
                           "timer": round(self.current_mode.timer, 1),
                           "active": self.current_mode.is_active}
                # Add mode-specific scores
                if hasattr(self.current_mode, 'red_score'):
                    mode_st["red_score"] = self.current_mode.red_score
                    mode_st["blue_score"] = self.current_mode.blue_score
                if hasattr(self.current_mode, 'red_captures'):
                    mode_st["red_caps"] = self.current_mode.red_captures
                    mode_st["blue_caps"] = self.current_mode.blue_captures
                if hasattr(self.current_mode, 'wave'):
                    mode_st["wave"] = self.current_mode.wave
                self.server._broadcast("game_state", mode_st)

    def update(self):
        if self.state == "playing":
            if self.current_mode:
                self.current_mode.update(time.dt)
            self.net_tick_timer += time.dt
            if self.net_tick_timer >= 1.0 / TICK_RATE:
                self.net_tick_timer = 0
                self._send_state()
        elif self.state == "round_end":
            self.round_end_timer -= time.dt
            if self.round_end_timer <= 0:
                self.next_round()

    def input(self, key):
        if self.state == "playing":
            if key == "tab":
                if not self._scoreboard:
                    self._scoreboard = ScoreboardUI(self)
                self._scoreboard.do_show()
            elif key == "tab up":
                if self._scoreboard:
                    self._scoreboard.do_hide()
            if key == "s":
                if not self._shop_ui:
                    self._shop_ui = ShopUI(self.player, on_close=self._close_shop)
                # Always update player reference in case of new round
                self._shop_ui.player = self.player
                self._shop_ui.do_show()

    def _close_shop(self):
        mouse.locked = True
        mouse.visible = False

    def disconnect(self):
        if self.server:
            self.server.stop()
            self.server = None
        if self.client:
            self.client.disconnect()
            self.client = None
        for rp in self.remote_players.values():
            destroy(rp)
        self.remote_players.clear()


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN — only runs when executed directly
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = Ursina(title=TITLE, borderless=False, size=WINDOW_SIZE)

    # Simple background — do NOT touch display regions, it breaks 3D rendering
    window.color = color.dark_gray
    window.exit_button.visible = False
    window.fps_counter.enabled = False

    # ── Menu ──────────────────────────────────────────────────────────────────
    _menu = []

    def _me(*a, **k):
        e = Entity(*a, **k); _menu.append(e); return e

    def _mt(*a, **k):
        t = Text(*a, **k); _menu.append(t); return t

    _me(parent=camera.ui, model="quad", color=DARK, scale=(3, 3), z=10)
    _me(parent=camera.ui, model="quad", color=OLIVE, scale=(1.4, 0.003), position=(0, 0.21), z=9)
    _me(parent=camera.ui, model="quad", color=OLIVE, scale=(1.4, 0.003), position=(0, -0.25), z=9)
    _mt(text="EPIC SURVIVOR", scale=3.5, position=(0, 0.35), origin=(0, 0), color=GOLD)
    _mt(text="Fight. Survive. Win.", scale=1.1, position=(0, 0.27), origin=(0, 0), color=DIM)
    _mt(text="v1.0", scale=0.5, position=(-0.55, -0.46), origin=(0, 0), color=DIM)

    _mt(text="CONTROLS", scale=0.85, position=(0.50, 0.18), origin=(0, 0), color=GOLD)
    _ctrls = [
        "Arrows .... Move", "H ......... Attack", "B ......... Block", "Space ..... Jump",
        "E ......... Weapon", "S ......... Shop", "Tab ....... Score", "Esc ....... Quit",
    ]
    for i, line in enumerate(_ctrls):
        _mt(text=line, scale=0.55, position=(0.50, 0.14 - i * 0.035), origin=(0, 0), color=DIM)

    def _mbtn(label, y):
        b = Button(text=label, scale=(0.26, 0.055), position=(0, y),
                   color=DBTN, highlight_color=HBTN, text_color=TXT)
        b.text_entity.scale *= 0.75
        _menu.append(b)
        return b

    btn_play = _mbtn("PLAY", 0.10)
    btn_cust = _mbtn("CUSTOMIZE", 0.015)
    btn_shop = _mbtn("SHOP", -0.07)
    btn_admin = _mbtn("ADMIN", -0.155)
    btn_quit = _mbtn("QUIT", -0.24)

    # Username input
    _mt(text="USERNAME", scale=0.7, position=(-0.35, 0.18), origin=(0, 0), color=GOLD)
    username_field = InputField(default_value="Player", limit_content_to='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_',
                                max_width=12, color=DBTN, text_color=TXT,
                                position=(-0.35, 0.14), scale=(0.22, 0.04))
    _menu.append(username_field)

    # Multiplayer section
    _mt(text="MULTIPLAYER", scale=0.7, position=(-0.35, 0.06), origin=(0, 0), color=GOLD)
    ip_field = InputField(default_value="192.168.1.", limit_content_to='0123456789.',
                          max_width=15, color=DBTN, text_color=TXT,
                          position=(-0.35, 0.02), scale=(0.22, 0.04))
    _menu.append(ip_field)
    mp_status = _mt(text="", scale=0.55, position=(-0.35, -0.02), origin=(0, 0), color=DIM)

    def _on_host():
        gm.host_game()
        import socket as _sock
        try:
            s = _sock.socket(_sock.AF_INET, _sock.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            local_ip = s.getsockname()[0]
            s.close()
        except Exception:
            local_ip = '???'
        mp_status.text = f'Hosting: {local_ip}:{DEFAULT_PORT} (0 players)'
        mp_status.color = Color(0.2, 0.8, 0.2, 1)
        print(f'[Server] Hosting on {local_ip}:{DEFAULT_PORT}')
        print(f'[Server] Tell your friend to enter {local_ip} and click JOIN')

    def _on_join():
        ip = ip_field.text.strip()
        if not ip:
            mp_status.text = 'Enter an IP first'
            mp_status.color = _ERR
            return
        mp_status.text = f'Connecting to {ip}...'
        mp_status.color = DIM
        ok = gm.join_game(ip)
        if ok:
            mp_status.text = f'Connected to {ip}!'
            mp_status.color = Color(0.2, 0.8, 0.2, 1)
        else:
            mp_status.text = f'Failed! Check IP/firewall'
            mp_status.color = _ERR

    # Update player count on menu
    _mp_update_ent = Entity(parent=camera.ui, visible=False)
    def _mp_tick():
        if gm.server and mp_status.enabled:
            count = len(gm.server.clients)
            import socket as _sk
            try:
                s = _sk.socket(_sk.AF_INET, _sk.SOCK_DGRAM)
                s.connect(('8.8.8.8', 80))
                lip = s.getsockname()[0]
                s.close()
            except Exception:
                lip = '???'
            mp_status.text = f'Hosting: {lip}:{DEFAULT_PORT} ({count} player{"s" if count != 1 else ""})'
        elif gm.client and mp_status.enabled:
            if gm.client.connected:
                mp_status.text = 'Connected!'
                mp_status.color = Color(0.2, 0.8, 0.2, 1)
            else:
                mp_status.text = 'Disconnected'
                mp_status.color = _ERR
    _mp_update_ent.update = _mp_tick
    _menu.append(_mp_update_ent)

    btn_host = _mbtn("HOST", -0.06)
    btn_host.scale = (0.12, 0.04)
    btn_host.position = (-0.42, -0.06)
    btn_host.text_entity.scale *= 0.9
    btn_host.on_click = _on_host

    btn_join = _mbtn("JOIN", -0.06)
    btn_join.scale = (0.12, 0.04)
    btn_join.position = (-0.28, -0.06)
    btn_join.text_entity.scale *= 0.9
    btn_join.on_click = _on_join

    def show_menu():
        for e in _menu:
            e.enabled = True
        mouse.locked = False
        mouse.visible = True

    def hide_menu():
        for e in _menu:
            e.enabled = False

    # ── Admin state ───────────────────────────────────────────────────────────
    _admin = [False]  # mutable so nested functions can modify
    _ADMIN_LOCKFILE = os.path.join(os.path.expanduser('~'), '.epic_survivor_admin')
    _ADMIN_MAX_TRIES = 5

    def _admin_locked():
        if os.path.exists(_ADMIN_LOCKFILE):
            try:
                with open(_ADMIN_LOCKFILE, 'r') as f:
                    data = json.loads(f.read().strip())
                ts = data.get('time', 0)
                tries = data.get('tries', 0)
                elapsed = _time.time() - ts
                if elapsed > 7 * 24 * 3600:  # reset after 7 days
                    return False
                if tries >= _ADMIN_MAX_TRIES:
                    return True
            except Exception:
                pass
        return False

    def _get_admin_tries():
        if os.path.exists(_ADMIN_LOCKFILE):
            try:
                with open(_ADMIN_LOCKFILE, 'r') as f:
                    data = json.loads(f.read().strip())
                elapsed = _time.time() - data.get('time', 0)
                if elapsed > 7 * 24 * 3600:
                    return 0
                return data.get('tries', 0)
            except Exception:
                pass
        return 0

    def _record_admin_attempt():
        tries = _get_admin_tries() + 1
        with open(_ADMIN_LOCKFILE, 'w') as f:
            f.write(json.dumps({'time': _time.time(), 'tries': tries}))

    # ── Admin Panel UI ────────────────────────────────────────────────────────
    _admin_ui = []

    def _show_admin():
        if _admin_locked():
            print('[Admin] Locked - one try per week')
            return
        hide_menu()
        for e in _admin_ui:
            e.enabled = True
        mouse.locked = False
        mouse.visible = True

    def _hide_admin():
        for e in _admin_ui:
            e.enabled = False
        show_menu()

    def _build_admin_panel():
        def _ae(*a, **k):
            e = Entity(*a, **k); _admin_ui.append(e); return e
        def _at(*a, **k):
            t = Text(*a, **k); _admin_ui.append(t); return t

        _ae(parent=camera.ui, model='quad', color=DARK, scale=(3, 3), z=10)
        _at(text='ADMIN PANEL', scale=1.8, position=(0, 0.3), origin=(0, 0), color=GOLD)
        _at(text='Enter access code:', scale=0.8, position=(0, 0.2), origin=(0, 0), color=TXT)
        remaining = _ADMIN_MAX_TRIES - _get_admin_tries()
        _at(text=f'5 tries per week ({remaining} left)', scale=0.6, position=(0, 0.15), origin=(0, 0), color=DIM)

        code_field = InputField(default_value='', limit_content_to='0123456789',
                                max_width=8, color=DBTN, text_color=TXT,
                                position=(0, 0.06), scale=(0.2, 0.04))
        _admin_ui.append(code_field)

        status_txt = _at(text='', scale=0.7, position=(0, -0.02), origin=(0, 0), color=_ERR)

        def _try_code():
            entered = code_field.text.strip()
            _record_admin_attempt()
            if entered == '66640':
                _admin[0] = True
                status_txt.text = 'ACCESS GRANTED'
                status_txt.color = Color(0.2, 0.9, 0.2, 1)
                print('[Admin] Admin mode activated!')
                invoke(_hide_admin, delay=1.0)
            else:
                status_txt.text = 'WRONG CODE - ' + str(_ADMIN_MAX_TRIES - _get_admin_tries()) + ' tries left'
                status_txt.color = _ERR
                invoke(_hide_admin, delay=1.5)

        submit_btn = Button(parent=camera.ui, text='SUBMIT', scale=(0.16, 0.045), position=(0, -0.06),
                            color=DBTN, highlight_color=HBTN, text_color=TXT)
        submit_btn.text_entity.scale *= 0.7
        submit_btn.on_click = _try_code
        _admin_ui.append(submit_btn)

        cancel_btn = Button(parent=camera.ui, text='BACK', scale=(0.16, 0.045), position=(0, -0.12),
                            color=DBTN, highlight_color=HBTN, text_color=TXT)
        cancel_btn.text_entity.scale *= 0.7
        cancel_btn.on_click = _hide_admin
        _admin_ui.append(cancel_btn)

        for e in _admin_ui:
            e.enabled = False

    _build_admin_panel()
    btn_admin.on_click = _show_admin

    # ── Game Manager ──────────────────────────────────────────────────────────
    gm = GameManager()
    customize_ui = None
    shop_ui = None

    def on_play():
        hide_menu()
        uname = username_field.text.strip() or "Player"
        skin, hat, face = (0.2, 0.3, 0.9), "none", "default"
        if customize_ui:
            c = customize_ui.get_customization()
            skin, hat, face = c["skin_color"], c["hat"], c["face"]
        gm.start_game(skin_color=skin, hat=hat, face=face, username=uname)
        # Apply admin perks
        if _admin[0] and gm.player:
            gm.player.god_mode = True
            for wid in WEAPONS:
                gm.player.weapon_manager.add_weapon(wid)
            print('[Admin] God mode ON, all weapons + Void Star unlocked')

    def on_customize():
        global customize_ui
        hide_menu()
        if not customize_ui:
            customize_ui = CustomizeUI(on_close=lambda: (customize_ui.hide(), show_menu()))
        customize_ui.show()

    def on_shop_click():
        global shop_ui
        if gm.player is None:
            gm.player = Player(gm)
            gm.player.enabled = False
        hide_menu()
        if not shop_ui:
            shop_ui = ShopUI(gm.player, on_close=lambda: (shop_ui.do_hide(), show_menu()))
        shop_ui.do_show()

    def on_quit():
        gm.disconnect()
        application.quit()

    btn_play.on_click = on_play
    btn_cust.on_click = on_customize
    btn_shop.on_click = on_shop_click
    btn_quit.on_click = on_quit

    # ── Game Loop Bridge ──────────────────────────────────────────────────────
    class _GameLoop(Entity):
        def __init__(self):
            super().__init__(parent=camera.ui, visible=False)

        def update(self):
            gm.update()

        def input(self, key):
            gm.input(key)
            if key == "escape" and gm.state == "menu":
                on_quit()
            if key == "f11":
                window.fullscreen = not window.fullscreen

    _GameLoop()

    def host(port=None):
        gm.host_game(port)

    def join(ip, port=None):
        gm.join_game(ip, port)

    print("[EPIC SURVIVOR] Ready! Click PLAY to start.")
    app.run()
