# ═══════════════════════════════════════════════════════════════════════════
#  DON'T FALL (OR ELSE...)  —  3D Knockout Battle Game
#  Inspired by Knockout! (Roblox)
#  Run: python cool_game.py/ragdoll/knockout.py
#  Requires: pip install ursina
# ═══════════════════════════════════════════════════════════════════════════
from ursina import *
from ursina import curve
import math, random, json, os, time as _time

# ── Color helpers ──────────────────────────────────────────────────────────
def _rgb(r, g, b):
    return Color(r / 255, g / 255, b / 255, 1)

def _rgba(r, g, b, a):
    return Color(r / 255, g / 255, b / 255, a / 255)

# ═══════════════════════════════════════════════════════════════════════════
#  SETTINGS & CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════
TITLE = "Don't Fall (Or Else...)"
WINDOW_SIZE = (1280, 720)

# Platform
PLATFORM_START_SIZE = 30
PLATFORM_MIN_SIZE = 10
PLATFORM_SHRINK_INTERVAL = 15     # seconds between shrinks
PLATFORM_SHRINK_AMOUNT = 1.2
PLATFORM_HEIGHT = 0.5
PLATFORM_Y = 0
FALL_Y = -20                      # below this = fell off

# Physics
GRAVITY = 22
FRICTION = 0.88
ICE_FRICTION = 0.93               # less slippery — harder to slide off
KNOCKBACK_BASE = 5
KNOCKBACK_SCALE = 0.10            # less knockback scaling
MAX_VELOCITY = 22

# Combat — turn-based launch system
LAUNCH_SPEED = 14                 # how fast you slide when launched
LAUNCH_SPEED_MAX = 22             # max speed at full power
BUMP_KNOCKBACK = 8               # knockback when two players collide
BUMP_RADIUS = 1.5                 # collision radius between fighters
AIM_TIME = 5.0                    # 5 seconds to aim each turn
SETTLE_TIME = 3.0                 # seconds to wait for physics to settle after launch
POWER_DEFAULT = 0.6               # default launch power (0-1)

# Player
PLAYER_SPEED = 8
PLAYER_JUMP_FORCE = 10
MAX_HEALTH = 100

# Rounds
ROUNDS_TO_WIN = 5
ROUND_START_DELAY = 3
COINS_PER_ROUND_WIN = 50
COINS_PER_KILL = 15
EGGS_PER_ROUND = 1
EGGS_PER_WIN = 3
EGG_PRICE = 25                    # coins per basic egg

# Egg tiers — each has a cost and a loot pool of rarities
EGG_TIERS = {
    "common": {"cost": 25, "name": "Common Egg", "color": _rgb(200, 200, 200),
               "weights": {"common": 70, "rare": 25, "ultra_rare": 5}},
    "rare": {"cost": 75, "name": "Rare Egg", "color": _rgb(100, 180, 255),
             "weights": {"common": 30, "rare": 50, "ultra_rare": 20}},
    "ultra": {"cost": 200, "name": "Ultra Egg", "color": _rgb(200, 100, 255),
              "weights": {"common": 5, "rare": 35, "ultra_rare": 60}},
}

# Bots
BOT_COUNT = 5
BOT_NAMES = [
    "PolarPete", "ArcticAce", "IcyIgloo", "FrostBite", "ChillyCharlie",
    "SnowPuff", "GlacierGus", "TundraMax", "BergyBob", "SlippySam",
    "WaddleKing", "FlipperFred", "IceCapDan", "PebblePat", "ColdCrash",
]

# ── Animal Shop ───────────────────────────────────────────────────────────
ANIMALS = {
    "duck": {
        "name": "Duck", "rarity": "starter",
        "body_color": _rgb(255, 210, 50), "belly_color": _rgb(255, 235, 130),
        "accent_color": _rgb(255, 140, 0), "description": "Quack attack! The starter skin.",
    },
    "penguin": {
        "name": "Penguin", "rarity": "common",
        "body_color": _rgb(30, 30, 40), "belly_color": _rgb(230, 230, 240),
        "accent_color": _rgb(255, 165, 0), "description": "Classic waddle and bonk.",
    },
    "seal": {
        "name": "Seal", "rarity": "common",
        "body_color": _rgb(130, 130, 140), "belly_color": _rgb(200, 200, 210),
        "accent_color": _rgb(50, 50, 60), "description": "Smooth slider. Less friction.",
    },
    "rabbit": {
        "name": "Snow Bunny", "rarity": "common",
        "body_color": _rgb(245, 245, 250), "belly_color": _rgb(255, 200, 200),
        "accent_color": _rgb(255, 150, 170), "description": "Bouncy escape artist.",
    },
    "polar_bear": {
        "name": "Polar Bear", "rarity": "rare",
        "body_color": _rgb(240, 240, 245), "belly_color": _rgb(220, 215, 200),
        "accent_color": _rgb(40, 40, 50), "description": "Big and tough. Extra knockback.",
    },
    "fox": {
        "name": "Arctic Fox", "rarity": "rare",
        "body_color": _rgb(240, 240, 250), "belly_color": _rgb(255, 255, 255),
        "accent_color": _rgb(60, 60, 70), "description": "Quick and nimble. Speed boost!",
    },
    "walrus": {
        "name": "Walrus", "rarity": "rare",
        "body_color": _rgb(150, 110, 80), "belly_color": _rgb(190, 160, 130),
        "accent_color": _rgb(230, 220, 200), "description": "Heavy hitter. Hard to push.",
    },
    "owl": {
        "name": "Snowy Owl", "rarity": "rare",
        "body_color": _rgb(250, 250, 255), "belly_color": _rgb(230, 230, 240),
        "accent_color": _rgb(255, 200, 50), "description": "Higher jumps. Aerial master!",
    },
    "husky": {
        "name": "Husky", "rarity": "ultra_rare",
        "body_color": _rgb(80, 80, 95), "belly_color": _rgb(220, 220, 230),
        "accent_color": _rgb(100, 170, 255), "description": "Fierce and balanced.",
    },
    "phoenix": {
        "name": "Phoenix", "rarity": "ultra_rare",
        "body_color": _rgb(255, 80, 20), "belly_color": _rgb(255, 180, 50),
        "accent_color": _rgb(255, 220, 0), "description": "Born from fire. Blazing fast!",
    },
    "dragon": {
        "name": "Ice Dragon", "rarity": "ultra_rare",
        "body_color": _rgb(40, 100, 180), "belly_color": _rgb(100, 180, 255),
        "accent_color": _rgb(200, 230, 255), "description": "Ancient frost beast. Unstoppable.",
    },
    "ghost": {
        "name": "Ghost", "rarity": "ultra_rare",
        "body_color": _rgb(200, 200, 220), "belly_color": _rgb(240, 240, 255),
        "accent_color": _rgb(150, 150, 200), "description": "Spooky and weightless. Boo!",
    },
}

RARITY_COLORS = {
    "starter": _rgb(200, 200, 200),
    "common": _rgb(180, 220, 180),
    "rare": _rgb(100, 170, 255),
    "ultra_rare": _rgb(220, 100, 255),
}
RARITY_NAMES = {
    "starter": "Starter", "common": "Common", "rare": "Rare", "ultra_rare": "ULTRA RARE",
}

# ── Power-ups ───────────────────────────────────────────────────────
POWERUP_TYPES = {
    "speed": {"color": _rgb(50, 200, 255), "duration": 5, "desc": "Speed Boost!"},
    "super_punch": {"color": _rgb(255, 50, 50), "duration": 8, "desc": "Super Punch!"},
    "shield": {"color": _rgb(50, 255, 100), "duration": 6, "desc": "Shield!"},
    "heavy": {"color": _rgb(180, 100, 255), "duration": 7, "desc": "Heavy! (Hard to push)"},
    "freeze_aura": {"color": _rgb(150, 220, 255), "duration": 5, "desc": "Freeze Aura!"},
}
POWERUP_SPAWN_INTERVAL = 8
MAX_POWERUPS = 3

# ── Save file ─────────────────────────────────────────────────────────────
SAVE_FILE = os.path.join(os.path.dirname(__file__), "knockout_save.json")


def load_save():
    defaults = {
        "coins": 0, "eggs": 0, "total_wins": 0, "total_kills": 0,
        "unlocked_animals": ["duck"], "selected_animal": "duck",
        "username": "",
    }
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
            for k, v in defaults.items():
                data.setdefault(k, v)
            return data
        except (json.JSONDecodeError, IOError):
            pass
    return defaults


def save_game(data):
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except IOError:
        pass


# ═══════════════════════════════════════════════════════════════════════════
#  ANIMAL 3D MODEL BUILDER
# ═══════════════════════════════════════════════════════════════════════════
class AnimalModel(Entity):
    """Builds a cute 3D animal out of primitives."""

    def __init__(self, animal_key="penguin", is_player=False, nametag="", **kwargs):
        super().__init__(**kwargs)
        self.animal_key = animal_key
        self.nametag_text = None
        info = ANIMALS.get(animal_key, ANIMALS["penguin"])
        bc = info["body_color"]
        belly = info["belly_color"]
        acc = info["accent_color"]

        # Scale body parts differently per animal type
        # big = polar_bear, walrus; thin = fox, rabbit, seal; normal = rest
        if animal_key in ("polar_bear", "walrus"):
            body_s = (0.9, 1.0, 0.8)
            head_s = (0.6, 0.55, 0.55)
            arm_s = (0.2, 0.55, 0.25)
        elif animal_key in ("fox", "rabbit", "owl"):
            body_s = (0.5, 0.7, 0.45)
            head_s = (0.5, 0.45, 0.45)
            arm_s = (0.12, 0.4, 0.15)
        elif animal_key in ("seal",):
            body_s = (0.6, 0.6, 0.9)
            head_s = (0.5, 0.45, 0.5)
            arm_s = (0.2, 0.3, 0.15)
        elif animal_key in ("phoenix", "dragon"):
            body_s = (0.7, 0.95, 0.6)
            head_s = (0.5, 0.5, 0.55)
            arm_s = (0.2, 0.6, 0.3)
        elif animal_key in ("ghost",):
            body_s = (0.7, 1.1, 0.7)
            head_s = (0.6, 0.6, 0.6)
            arm_s = (0.1, 0.5, 0.15)
        else:
            body_s = (0.7, 0.9, 0.6)
            head_s = (0.55, 0.5, 0.5)
            arm_s = (0.15, 0.5, 0.2)

        # Body
        self.body = Entity(parent=self, model="sphere", color=bc,
                           scale=body_s, position=(0, 0.9, 0))
        # Belly
        self.belly = Entity(parent=self, model="sphere", color=belly,
                            scale=(body_s[0]*0.8, body_s[1]*0.8, body_s[2]*0.75), position=(0, 0.85, 0.1))
        # Head
        self.head = Entity(parent=self, model="sphere", color=bc,
                           scale=head_s, position=(0, 1.55, 0))
        # Eyes
        self.left_eye = Entity(parent=self.head, model="sphere", color=color.white,
                               scale=(0.2, 0.22, 0.15), position=(-0.18, 0.05, 0.4))
        self.left_pupil = Entity(parent=self.left_eye, model="sphere", color=color.black,
                                 scale=(0.5, 0.5, 0.6), position=(0, 0, 0.3))
        self.right_eye = Entity(parent=self.head, model="sphere", color=color.white,
                                scale=(0.2, 0.22, 0.15), position=(0.18, 0.05, 0.4))
        self.right_pupil = Entity(parent=self.right_eye, model="sphere", color=color.black,
                                  scale=(0.5, 0.5, 0.6), position=(0, 0, 0.3))

        # Beak / Mouth
        self.beak = Entity(parent=self.head, model="cube", color=acc,
                           scale=(0.15, 0.1, 0.2), position=(0, -0.1, 0.45))

        # Feet
        self.left_foot = Entity(parent=self, model="cube", color=acc,
                                scale=(0.25, 0.08, 0.3), position=(-0.2, 0.04, 0.05))
        self.right_foot = Entity(parent=self, model="cube", color=acc,
                                 scale=(0.25, 0.08, 0.3), position=(0.2, 0.04, 0.05))

        # Arms / Flippers
        self.left_arm = Entity(parent=self, model="cube", color=bc,
                               scale=arm_s, position=(-0.5, 0.9, 0))
        self.right_arm = Entity(parent=self, model="cube", color=bc,
                                scale=arm_s, position=(0.5, 0.9, 0))

        # Tail (small)
        self.tail = Entity(parent=self, model="sphere", color=bc,
                           scale=(0.15, 0.12, 0.15), position=(0, 0.6, -0.35))

        # Player indicator
        if is_player:
            self.indicator = Entity(parent=self, model="cube", color=_rgb(255, 255, 50),
                                    scale=(0.15, 0.15, 0.15), position=(0, 2.1, 0),
                                    rotation=(45, 45, 0))
        else:
            self.indicator = None

        # Nametag (billboard text above head)
        if nametag:
            tag_color = _rgb(255, 255, 80) if is_player else color.white
            self.nametag_text = Text(
                text=nametag, scale=12, billboard=True,
                parent=self, position=(0, 2.3, 0),
                origin=(0, 0), color=tag_color
            )
        else:
            self.nametag_text = None

        self._bob_phase = random.uniform(0, 6.28)
        self._walk_phase = 0

    def animate_idle(self, dt):
        self._bob_phase += dt * 2.5
        bob = math.sin(self._bob_phase) * 0.03
        self.body.y = 0.9 + bob
        self.head.y = 1.55 + bob
        self.belly.y = 0.85 + bob
        # Gentle arm sway
        sway = math.sin(self._bob_phase * 0.7) * 5
        self.left_arm.rotation_z = 10 + sway
        self.right_arm.rotation_z = -10 - sway

    def animate_walk(self, dt):
        self._walk_phase += dt * 14
        swing = math.sin(self._walk_phase) * 30
        self.left_arm.rotation_x = swing
        self.right_arm.rotation_x = -swing
        self.left_foot.rotation_x = -swing * 0.6
        self.right_foot.rotation_x = swing * 0.6
        # Waddle
        waddle = math.sin(self._walk_phase) * 5
        self.body.rotation_z = waddle
        self.head.rotation_z = waddle * 0.5
        bob = abs(math.sin(self._walk_phase)) * 0.06
        self.body.y = 0.9 + bob
        self.head.y = 1.55 + bob

    def animate_punch(self):
        self.right_arm.animate_rotation(Vec3(-100, 0, -10), duration=0.1, curve=curve.out_expo)
        self.right_arm.animate_rotation(Vec3(0, 0, -10), duration=0.2, delay=0.15)
        # Lunge head forward
        self.head.animate_position(Vec3(0, 1.55, 0.15), duration=0.08)
        self.head.animate_position(Vec3(0, 1.55, 0), duration=0.15, delay=0.1)

    def animate_hit(self):
        for p in (self.body, self.head, self.belly):
            orig = p.color
            p.color = _rgb(255, 80, 80)
            p.animate_color(orig, duration=0.3, delay=0.05)

    def animate_fall(self):
        """Spin and shrink when falling off."""
        self.animate_rotation(Vec3(random.uniform(-360, 360),
                                    random.uniform(-360, 360), 0), duration=1.5)
        self.animate_scale(0, duration=1.5)

    def reset_pose(self):
        self.rotation = Vec3(0, 0, 0)
        self.scale = Vec3(1, 1, 1)
        self.left_arm.rotation = Vec3(0, 0, 10)
        self.right_arm.rotation = Vec3(0, 0, -10)
        self.left_foot.rotation = Vec3(0, 0, 0)
        self.right_foot.rotation = Vec3(0, 0, 0)
        self.body.rotation = Vec3(0, 0, 0)
        self.head.rotation = Vec3(0, 0, 0)


# ═══════════════════════════════════════════════════════════════════════════
#  FIGHTER (Player & Bot base)
# ═══════════════════════════════════════════════════════════════════════════
class Fighter:
    def __init__(self, name, animal_key="penguin", is_player=False):
        self.name = name
        self.animal_key = animal_key
        self.is_player = is_player
        self.alive = True
        self.damage_taken = 0
        self.position = Vec3(0, 5, 0)
        self.velocity = Vec3(0, 0, 0)
        self.grounded = False
        self.kills = 0
        self.wins = 0

        # Turn-based aim
        self.aim_angle = 0          # degrees — direction to launch
        self.aim_power = POWER_DEFAULT  # 0-1 power
        self.aim_locked = False     # True once player confirms aim
        self.arrow_entity = None    # 3D arrow in world
        self.arrow_head = None

        # Power-up state
        self.powerups = {}
        self.shield_entity = None

        # Animal bonuses
        self.speed_mult = 1.0
        self.knockback_resist = 1.0
        self.weight = 1.0           # heavier = harder to push, slower launch
        self._apply_animal_bonuses()

        self.model = None

    def _apply_animal_bonuses(self):
        if self.animal_key == "polar_bear":
            self.knockback_resist = 0.6
            self.weight = 1.4
        elif self.animal_key == "seal":
            self.weight = 0.8       # slides further
        elif self.animal_key == "fox":
            self.speed_mult = 1.3
            self.weight = 0.9
        elif self.animal_key == "walrus":
            self.knockback_resist = 0.4
            self.weight = 1.6
        elif self.animal_key == "owl":
            self.weight = 0.7
        elif self.animal_key == "rabbit":
            self.weight = 0.75
        elif self.animal_key == "husky":
            self.speed_mult = 1.1
            self.knockback_resist = 0.8
            self.weight = 1.1

    def spawn_model(self, pos, is_player=False):
        self.position = Vec3(pos[0], pos[1], pos[2])
        self.velocity = Vec3(0, 0, 0)
        self.alive = True
        self.damage_taken = 0
        self.grounded = False
        self.aim_locked = False
        self.aim_power = POWER_DEFAULT
        self.powerups = {}

        if self.model:
            destroy(self.model)
        self.model = AnimalModel(animal_key=self.animal_key, is_player=is_player,
                                 nametag=self.name, position=self.position)

        # Create aim arrow (hidden initially)
        if self.arrow_entity:
            destroy(self.arrow_entity)
        if self.arrow_head:
            destroy(self.arrow_head)
        arrow_color = _rgba(255, 255, 255, 255) if is_player else _rgba(200, 200, 200, 0)
        self.arrow_entity = Entity(model="cube", color=arrow_color,
                                    scale=(0.5, 0.25, 4), position=(0, -100, 0))
        self.arrow_head = Entity(model="cube", color=arrow_color,
                                  scale=(1.0, 0.3, 1.0), position=(0, -100, 0),
                                  rotation=(0, 45, 0))
        return self.model

    def show_arrow(self, visible=True, force_reveal=False):
        """Show/hide the aim arrow. Bots are hidden unless force_reveal."""
        if not self.model or not self.alive:
            return
        if visible:
            # During aiming, only show player's arrow — hide bot arrows
            if not self.is_player and not force_reveal:
                self.arrow_entity.position = Vec3(0, -100, 0)
                self.arrow_head.position = Vec3(0, -100, 0)
                return

            rad = math.radians(self.aim_angle)
            fwd = Vec3(math.sin(rad), 0, math.cos(rad))
            arrow_len = 3 + 8 * self.aim_power
            mid = self.model.position + fwd * (arrow_len * 0.5) + Vec3(0, 0.5, 0)
            tip = self.model.position + fwd * arrow_len + Vec3(0, 0.5, 0)

            self.arrow_entity.position = mid
            self.arrow_entity.scale = Vec3(0.5 + 0.5 * self.aim_power, 0.25, arrow_len)
            self.arrow_entity.rotation_y = self.aim_angle

            self.arrow_head.position = tip
            head_sz = 1.0 + 1.0 * self.aim_power
            self.arrow_head.scale = Vec3(head_sz, 0.3, head_sz)
            self.arrow_head.rotation_y = self.aim_angle + 45

            if self.aim_locked:
                c = _rgba(100, 255, 100, 255)  # green = locked
            elif self.is_player:
                c = _rgba(255, 255, 255, 255)  # white for player
            else:
                c = _rgba(255, 100, 100, 255)  # red for revealed bots
            self.arrow_entity.color = c
            self.arrow_head.color = c
        else:
            self.arrow_entity.position = Vec3(0, -100, 0)
            self.arrow_head.position = Vec3(0, -100, 0)

    def launch(self):
        """Launch this fighter in their aimed direction."""
        if not self.alive:
            return
        rad = math.radians(self.aim_angle)
        speed = LAUNCH_SPEED + (LAUNCH_SPEED_MAX - LAUNCH_SPEED) * self.aim_power
        speed *= self.speed_mult
        speed /= max(0.5, self.weight)  # heavier = slower
        self.velocity = Vec3(math.sin(rad) * speed, 1.5, math.cos(rad) * speed)

    def die(self, killer=None):
        if not self.alive:
            return
        self.alive = False
        if self.model:
            self.model.animate_fall()
        self.show_arrow(False)
        if killer and killer != self:
            killer.kills += 1


# ═══════════════════════════════════════════════════════════════════════════
#  POWER-UP ENTITY
# ═══════════════════════════════════════════════════════════════════════════
class PowerUpEntity(Entity):
    def __init__(self, ptype, platform_size, **kwargs):
        info = POWERUP_TYPES[ptype]
        pos = Vec3(
            random.uniform(-platform_size * 0.4, platform_size * 0.4),
            PLATFORM_Y + 1.5,
            random.uniform(-platform_size * 0.4, platform_size * 0.4),
        )
        super().__init__(
            model="sphere", color=info["color"], scale=0.5,
            position=pos, **kwargs
        )
        self.ptype = ptype
        self._bob = random.uniform(0, 6.28)
        # Glow ring
        self.ring = Entity(parent=self, model="cube", color=info["color"],
                           scale=(1.8, 0.1, 1.8), alpha=0.4)

    def update(self):
        self._bob += time.dt * 3
        self.y = PLATFORM_Y + 1.5 + math.sin(self._bob) * 0.3
        self.rotation_y += time.dt * 90
        if self.ring:
            self.ring.rotation_x += time.dt * 60


# ═══════════════════════════════════════════════════════════════════════════
#  PARTICLE EFFECTS
# ═══════════════════════════════════════════════════════════════════════════
def spawn_hit_particles(pos, clr=None):
    for _ in range(6):
        p = Entity(model="cube", color=clr or _rgb(255, 255, 100),
                   scale=random.uniform(0.05, 0.15), position=pos)
        target = pos + Vec3(random.uniform(-1.5, 1.5), random.uniform(0.5, 2),
                             random.uniform(-1.5, 1.5))
        p.animate_position(target, duration=0.4, curve=curve.out_expo)
        p.animate_scale(0, duration=0.4)
        destroy(p, delay=0.45)


def spawn_fall_particles(pos):
    for _ in range(10):
        p = Entity(model="sphere", color=_rgba(200, 220, 255, 200),
                   scale=random.uniform(0.1, 0.3), position=pos)
        target = pos + Vec3(random.uniform(-2, 2), random.uniform(-3, -1),
                             random.uniform(-2, 2))
        p.animate_position(target, duration=0.8)
        p.animate_scale(0, duration=0.8)
        p.animate_color(_rgba(200, 220, 255, 0), duration=0.8)
        destroy(p, delay=0.85)


def spawn_powerup_particles(pos, clr):
    for _ in range(8):
        p = Entity(model="sphere", color=clr, scale=random.uniform(0.05, 0.12), position=pos)
        target = pos + Vec3(random.uniform(-1, 1), random.uniform(1, 3),
                             random.uniform(-1, 1))
        p.animate_position(target, duration=0.6, curve=curve.out_expo)
        p.animate_scale(0, duration=0.6)
        destroy(p, delay=0.65)


# ═══════════════════════════════════════════════════════════════════════════
#  GAME MANAGER
# ═══════════════════════════════════════════════════════════════════════════
class DontFallGame:
    def __init__(self):
        self.app = Ursina(title=TITLE, borderless=False, size=WINDOW_SIZE)
        window.color = _rgb(25, 25, 35)
        window.fps_counter.enabled = True
        self.save_data = load_save()

        # ── State machine ──
        # menu, shop, countdown, aiming, launching, settle, round_over, game_over
        self.state = "menu"
        self.round_number = 0
        self.turn_number = 0
        self.aim_timer = 0
        self.settle_timer = 0
        self.countdown = 0
        self.platform_size = PLATFORM_START_SIZE
        self.shrink_count = 0

        # Fighters
        self.player = None
        self.bots = []
        self.all_fighters = []
        self.alive_count = 0

        # World
        self.platform = None
        self.platform_edge_warn = None
        self.sky = None

        self._build_world()
        self._build_ui()
        self._show_menu()

    # ─── WORLD ────────────────────────────────────────────────────────────
    def _build_world(self):
        self.sky = Entity(model="sphere", scale=500, color=_rgb(30, 40, 70), double_sided=True)
        for _ in range(60):
            Entity(model="sphere", color=_rgba(255, 255, 255, random.randint(100, 255)),
                   scale=random.uniform(0.1, 0.3),
                   position=Vec3(random.uniform(-200, 200), random.uniform(50, 200),
                                  random.uniform(-200, 200)))
        DirectionalLight(y=10, rotation=(45, -45, 0))
        AmbientLight(color=Color(0.4, 0.4, 0.5, 1))

        # ── Ocean water ──
        self.water = Entity(model="cube", color=_rgba(30, 80, 160, 200),
                            scale=(200, 0.1, 200), position=(0, -8, 0))
        # Water surface shimmer
        Entity(parent=self.water, model="cube", color=_rgba(60, 120, 200, 100),
               scale=(0.98, 1.5, 0.98), position=(0, 0.05, 0))
        # Waves (decorative rings)
        for r in (40, 60, 80):
            Entity(model="cube", color=_rgba(80, 140, 220, 60),
                   scale=(r, 0.05, r), position=(0, -7.9, 0))

        # ── Iceberg (underneath platform) ──
        # Main ice block tapering down
        Entity(model="cube", color=_rgb(200, 230, 255),
               scale=(PLATFORM_START_SIZE * 0.9, 6, PLATFORM_START_SIZE * 0.9),
               position=(0, PLATFORM_Y - 3, 0))
        # Tapered bottom
        Entity(model="cube", color=_rgb(180, 215, 245),
               scale=(PLATFORM_START_SIZE * 0.6, 4, PLATFORM_START_SIZE * 0.6),
               position=(0, PLATFORM_Y - 7, 0))
        Entity(model="cube", color=_rgb(160, 200, 235),
               scale=(PLATFORM_START_SIZE * 0.3, 3, PLATFORM_START_SIZE * 0.3),
               position=(0, PLATFORM_Y - 10, 0))
        # Underwater tip
        Entity(model="sphere", color=_rgba(140, 190, 230, 180),
               scale=(PLATFORM_START_SIZE * 0.15, 2, PLATFORM_START_SIZE * 0.15),
               position=(0, PLATFORM_Y - 12, 0))

        # ── Platform top (icy surface) ──
        self.platform = Entity(model="cube", color=_rgb(210, 240, 255),
                                scale=(PLATFORM_START_SIZE, PLATFORM_HEIGHT, PLATFORM_START_SIZE),
                                position=(0, PLATFORM_Y, 0), collider="box")
        Entity(parent=self.platform, model="cube", color=_rgba(230, 245, 255, 180),
               scale=(0.95, 1.02, 0.95), position=(0, 0.01, 0))
        self.platform_edge_warn = Entity(model="cube", color=_rgba(255, 80, 80, 0),
                                          scale=(PLATFORM_START_SIZE * 0.95, 0.15, PLATFORM_START_SIZE * 0.95),
                                          position=(0, PLATFORM_Y + 0.3, 0))

        # Snow chunks on edges
        for _ in range(12):
            angle = random.uniform(0, 6.28)
            r = PLATFORM_START_SIZE * 0.48
            Entity(model="sphere", color=_rgb(220, 235, 255),
                   scale=random.uniform(0.5, 1.5),
                   position=Vec3(math.cos(angle) * r, PLATFORM_Y + 0.2, math.sin(angle) * r))

        # ── Spectator platform (floating above arena) ──
        sp = Vec3(30, 18, 0)  # spectator platform center
        Entity(model="cube", color=_rgb(60, 65, 80), scale=(16, 0.5, 12), position=sp)
        # Floor pattern
        Entity(model="cube", color=_rgb(70, 75, 95), scale=(14, 0.52, 10), position=sp + Vec3(0, 0.01, 0))
        # Railings
        for z_off in [-5.8, 5.8]:
            Entity(model="cube", color=_rgb(90, 100, 120), scale=(16, 1.5, 0.2), position=sp + Vec3(0, 0.8, z_off))
        Entity(model="cube", color=_rgb(90, 100, 120), scale=(0.2, 1.5, 12), position=sp + Vec3(7.8, 0.8, 0))
        # Glass viewing wall facing arena
        Entity(model="cube", color=_rgba(150, 200, 255, 40), scale=(0.1, 3, 12), position=sp + Vec3(-8, 1.5, 0))

        # ── Egg Shop Stand (with rarest skin on display) ──
        # Counter
        Entity(model="cube", color=_rgb(140, 100, 50), scale=(4, 1.2, 2), position=sp + Vec3(4, 0.85, 0))
        # Sign above counter
        Entity(model="cube", color=_rgb(200, 160, 60), scale=(3, 0.6, 0.1), position=sp + Vec3(4, 2, -1))
        # Display pedestal for rare skin
        Entity(model="cube", color=_rgb(80, 60, 120), scale=(1.5, 0.8, 1.5), position=sp + Vec3(4, 0.65, 0))
        # Rarest skin model (Husky) on display stand
        self.shop_display_skin = AnimalModel(animal_key="husky", is_player=False,
                                              position=sp + Vec3(4, 1.8, 0))
        self.shop_display_skin.scale = 0.7
        # Viewing bench
        Entity(model="cube", color=_rgb(80, 70, 55), scale=(5, 0.5, 1), position=sp + Vec3(-3, 0.5, -4))

    # ─── UI ───────────────────────────────────────────────────────────────
    def _build_ui(self):
        self.hud_root = Entity(parent=camera.ui, enabled=False)

        # Damage % display
        self.damage_pct_text = Text(parent=self.hud_root, text="0%", scale=1.5,
                                     position=(-0.65, 0.45), color=color.white, origin=(0, 0))
        self.coin_text = Text(parent=self.hud_root, text="Coins: 0", position=(0.55, 0.47),
                              scale=0.9, color=_rgb(255, 215, 0), origin=(0, 0))
        self.egg_text = Text(parent=self.hud_root, text="Eggs: 0", position=(0.55, 0.44),
                             scale=0.8, color=_rgb(255, 200, 150), origin=(0, 0))
        self.round_text = Text(parent=self.hud_root, text="Round 1", position=(0, 0.47),
                               scale=1.2, color=color.white, origin=(0, 0))
        self.alive_text = Text(parent=self.hud_root, text="Alive: 6", position=(0, 0.43),
                               scale=0.9, color=_rgb(200, 200, 200), origin=(0, 0))

        # Turn timer (big center)
        self.timer_text = Text(parent=self.hud_root, text="", scale=3,
                               position=(0, 0.3), color=color.white, origin=(0, 0))
        self.phase_text = Text(parent=self.hud_root, text="", scale=1.5,
                               position=(0, 0.22), color=_rgb(200, 200, 200), origin=(0, 0))
        self.power_text = Text(parent=self.hud_root, text="", scale=1.2,
                               position=(0, -0.35), color=_rgb(255, 200, 100), origin=(0, 0))

        # Kill feed (right side)
        self.kill_feed = Text(parent=self.hud_root, text="", position=(0.72, 0.1),
                              scale=0.7, color=_rgb(255, 200, 200), origin=(1, 0))
        self._kill_feed_lines = []

        # Turn counter
        self.turn_text = Text(parent=self.hud_root, text="Turn 1", position=(-0.65, 0.40),
                              scale=0.8, color=_rgb(180, 180, 200), origin=(0, 0))

        # ── Spectator HUD (shown when player dies) ──
        self.spec_root = Entity(parent=camera.ui, enabled=False)
        self.spec_label = Text(parent=self.spec_root, text="YOU FELL OFF!",
                               scale=1.5, position=(0, 0.45), color=_rgb(255, 100, 100),
                               origin=(0, 0))
        self.spec_hint = Text(parent=self.spec_root, text="Arrow Keys = Walk  |  E = Buy Eggs at Stand  |  Tab = My Skins",
                              scale=0.7, position=(0, -0.45), color=_rgb(160, 160, 180),
                              origin=(0, 0))
        self.spec_coins_text = Text(parent=self.spec_root, text="",
                                     scale=0.9, position=(0.55, 0.45), color=_rgb(255, 215, 0),
                                     origin=(0, 0))
        self.spec_shop_msg = Text(parent=self.spec_root, text="",
                                   scale=1.2, position=(0, 0.35), color=_rgb(100, 255, 100),
                                   origin=(0, 0))
        self.spec_near_shop = Text(parent=self.spec_root, text="",
                                    scale=1.2, position=(0, -0.3), color=_rgb(255, 220, 80),
                                    origin=(0, 0))

        # ── Egg buy panel (shown when near stand and press E) ──
        self.egg_panel = Entity(parent=camera.ui, enabled=False)
        Entity(parent=self.egg_panel, model="quad", color=_rgba(15, 20, 30, 230),
               scale=(0.5, 0.4), position=(0, 0))
        Text(parent=self.egg_panel, text="HATCH EGGS", scale=1.8,
             position=(0, 0.16), origin=(0, 0), color=_rgb(255, 215, 0))
        self.egg_panel_coins = Text(parent=self.egg_panel, text="", scale=1,
                                     position=(0, 0.1), origin=(0, 0), color=_rgb(255, 215, 0))
        Button(parent=self.egg_panel, text="Common Egg (25)", scale=(0.35, 0.05),
               position=(0, 0.03), color=_rgb(80, 80, 80), highlight_color=_rgb(110, 110, 110),
               on_click=lambda: self._spec_hatch("common"))
        Button(parent=self.egg_panel, text="Rare Egg (75)", scale=(0.35, 0.05),
               position=(0, -0.04), color=_rgb(50, 80, 160), highlight_color=_rgb(70, 110, 200),
               on_click=lambda: self._spec_hatch("rare"))
        Button(parent=self.egg_panel, text="Ultra Egg (200)", scale=(0.35, 0.05),
               position=(0, -0.11), color=_rgb(130, 50, 180), highlight_color=_rgb(170, 70, 220),
               on_click=lambda: self._spec_hatch("ultra"))
        self.egg_panel_msg = Text(parent=self.egg_panel, text="", scale=0.9,
                                   position=(0, -0.17), origin=(0, 0), color=_rgb(100, 255, 100))
        Button(parent=self.egg_panel, text="X Close", scale=(0.12, 0.04),
               position=(0.2, 0.16), color=_rgb(120, 40, 40), highlight_color=_rgb(160, 60, 60),
               on_click=lambda: setattr(self.egg_panel, 'enabled', False))

        # Spectator character + state
        self.spec_char = None
        self.spec_pos = Vec3(30, 18.5, 0)

        # ── Announcements ──
        self.announce_text = Text(text="", scale=3, position=(0, 0.1),
                                  color=color.white, origin=(0, 0), enabled=False)
        self.sub_announce = Text(text="", scale=1.2, position=(0, 0.02),
                                 color=_rgb(200, 200, 200), origin=(0, 0), enabled=False)

        # ── Controls hint ──
        self.controls_hint = Text(parent=self.hud_root, text="",
                                  scale=0.7, position=(0, -0.45),
                                  color=_rgb(160, 160, 180), origin=(0, 0))

        # ── MENU ──
        self.menu_root = Entity(parent=camera.ui, enabled=False)
        Text(parent=self.menu_root, text="DON'T FALL", scale=4,
             position=(0, 0.3), origin=(0, 0), color=_rgb(100, 200, 255))
        Text(parent=self.menu_root, text="(Or Else...)", scale=1.8,
             position=(0, 0.2), origin=(0, 0), color=_rgb(255, 150, 100))

        self.menu_name_label = Text(parent=self.menu_root, text="Username:",
                                     scale=0.9, position=(-0.17, 0.11), color=_rgb(180, 180, 200))
        self.menu_name_field = InputField(parent=self.menu_root,
                                          default_value=self.save_data.get('username', '') or 'Player',
                                          limit_content_to='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-',
                                          max_length=16, scale=(0.3, 0.05), position=(0.07, 0.11),
                                          color=_rgb(30, 35, 45))
        Button(parent=self.menu_root, text="PLAY", scale=(0.3, 0.07), position=(0, 0.01),
               color=_rgb(50, 140, 80), highlight_color=_rgb(70, 180, 100),
               on_click=self._start_game)
        Button(parent=self.menu_root, text="HATCH EGGS", scale=(0.3, 0.07), position=(0, -0.09),
               color=_rgb(180, 120, 50), highlight_color=_rgb(220, 150, 70),
               on_click=self._show_shop)
        Button(parent=self.menu_root, text="MY SKINS", scale=(0.3, 0.07), position=(0, -0.19),
               color=_rgb(80, 60, 140), highlight_color=_rgb(110, 80, 180),
               on_click=self._show_collection)
        self.menu_coins = Text(parent=self.menu_root,
                               text=f"Coins: {self.save_data['coins']}",
                               scale=1, position=(0, -0.30), origin=(0, 0), color=_rgb(255, 215, 0))
        self.menu_stats = Text(parent=self.menu_root,
                               text=f"Wins: {self.save_data['total_wins']}  |  Kills: {self.save_data['total_kills']}",
                               scale=0.8, position=(0, -0.36), origin=(0, 0), color=_rgb(180, 180, 180))
        self.menu_animal = Text(parent=self.menu_root,
                                text=f"Selected: {ANIMALS[self.save_data['selected_animal']]['name']}",
                                scale=0.9, position=(0, -0.42), origin=(0, 0), color=_rgb(150, 220, 255))
        Text(parent=self.menu_root,
             text="Mouse/A/D = Aim  |  Hold LClick = Power Up  |  Space = Power Down  |  Right Click = Lock",
             scale=0.6, position=(0, -0.42), origin=(0, 0), color=_rgb(130, 130, 140))

        # ── SHOP (Egg Hatching) ──
        self.shop_root = Entity(parent=camera.ui, enabled=False)
        Text(parent=self.shop_root, text="HATCH EGGS", scale=4,
             position=(0, 0.42), origin=(0, 0), color=_rgb(255, 200, 50))
        self.shop_coins_text = Text(parent=self.shop_root, text="", scale=1.5,
                                     position=(0, 0.33), origin=(0, 0), color=_rgb(255, 215, 0))
        Button(parent=self.shop_root, text="< BACK", scale=(0.18, 0.06), position=(-0.6, 0.44),
               color=_rgb(100, 50, 50), highlight_color=_rgb(140, 70, 70), on_click=self._show_menu)
        # Egg tier buttons
        Button(parent=self.shop_root, text=f"Common Egg\n25 coins\nCommon 70% | Rare 25% | Ultra 5%",
               scale=(0.38, 0.2), position=(-0.4, 0.05), text_size=0.6,
               color=_rgb(80, 80, 80), highlight_color=_rgb(110, 110, 110),
               on_click=lambda: self._hatch_egg("common"))
        Button(parent=self.shop_root, text=f"Rare Egg\n75 coins\nCommon 30% | Rare 50% | Ultra 20%",
               scale=(0.38, 0.2), position=(0, 0.05), text_size=0.6,
               color=_rgb(50, 80, 160), highlight_color=_rgb(70, 110, 200),
               on_click=lambda: self._hatch_egg("rare"))
        Button(parent=self.shop_root, text=f"Ultra Egg\n200 coins\nCommon 5% | Rare 35% | Ultra 60%",
               scale=(0.38, 0.2), position=(0.4, 0.05), text_size=0.6,
               color=_rgb(130, 50, 180), highlight_color=_rgb(170, 70, 220),
               on_click=lambda: self._hatch_egg("ultra"))
        self.shop_message = Text(parent=self.shop_root, text="", scale=2,
                                  position=(0, -0.12), origin=(0, 0), color=_rgb(100, 255, 100))
        self.shop_result_name = Text(parent=self.shop_root, text="", scale=2.5,
                                      position=(0, -0.2), origin=(0, 0), color=color.white)
        self.shop_result_rarity = Text(parent=self.shop_root, text="", scale=1.3,
                                        position=(0, -0.28), origin=(0, 0), color=color.white)
        # Color preview of hatched skin
        self.shop_preview_body = Entity(parent=self.shop_root, model="quad",
                                         scale=(0.06, 0.06), position=(-0.08, -0.35),
                                         color=color.white, enabled=False)
        self.shop_preview_belly = Entity(parent=self.shop_root, model="quad",
                                          scale=(0.06, 0.06), position=(0, -0.35),
                                          color=color.white, enabled=False)
        self.shop_preview_accent = Entity(parent=self.shop_root, model="quad",
                                           scale=(0.06, 0.06), position=(0.08, -0.35),
                                           color=color.white, enabled=False)
        self.shop_buttons = []  # kept for compat

        # ── COLLECTION (My Skins) ──
        self.collection_root = Entity(parent=camera.ui, enabled=False)
        Text(parent=self.collection_root, text="MY SKINS", scale=2.5,
             position=(0, 0.42), origin=(0, 0), color=_rgb(180, 130, 255))
        Button(parent=self.collection_root, text="< BACK", scale=(0.15, 0.05), position=(-0.62, 0.44),
               color=_rgb(100, 50, 50), highlight_color=_rgb(140, 70, 70), on_click=self._show_menu)
        self.collection_items = []
        self.collection_msg = Text(parent=self.collection_root, text="", scale=0.9,
                                    position=(0, -0.43), origin=(0, 0), color=_rgb(100, 255, 100))

        # ── GAME OVER ──
        self.gameover_root = Entity(parent=camera.ui, enabled=False)
        self.gameover_title = Text(parent=self.gameover_root, text="", scale=3,
                                    position=(0, 0.2), origin=(0, 0), color=_rgb(255, 215, 0))
        self.gameover_stats = Text(parent=self.gameover_root, text="", scale=1,
                                    position=(0, 0.05), origin=(0, 0), color=color.white)
        Button(parent=self.gameover_root, text="BACK TO MENU", scale=(0.3, 0.07),
               position=(0, -0.12), color=_rgb(50, 80, 150), highlight_color=_rgb(70, 110, 190),
               on_click=self._show_menu)

    def _build_shop_items(self):
        pass  # egg shop uses buttons directly, no dynamic rebuild needed

    def _hatch_egg(self, tier):
        egg = EGG_TIERS[tier]
        if self.save_data["coins"] < egg["cost"]:
            self.shop_message.text = f"Need {egg['cost']} coins! You have {self.save_data['coins']}"
            self.shop_message.color = _rgb(255, 100, 100)
            self.shop_result_name.text = ""
            self.shop_result_rarity.text = ""
            self.shop_preview_body.enabled = False
            self.shop_preview_belly.enabled = False
            self.shop_preview_accent.enabled = False
            return

        self.save_data["coins"] -= egg["cost"]

        # Roll rarity based on weights
        weights = egg["weights"]
        roll = random.randint(1, 100)
        cumulative = 0
        chosen_rarity = "common"
        for rarity, weight in weights.items():
            cumulative += weight
            if roll <= cumulative:
                chosen_rarity = rarity
                break

        # Pick random skin from that rarity (exclude already owned)
        pool = [k for k, v in ANIMALS.items() if v["rarity"] == chosen_rarity
                and k not in self.save_data["unlocked_animals"]]
        if not pool:
            # All of this rarity owned, try any unowned
            pool = [k for k in ANIMALS if k not in self.save_data["unlocked_animals"]]
        if not pool:
            # All owned — refund
            self.save_data["coins"] += egg["cost"]
            self.shop_message.text = "You own all skins! Refunded."
            self.shop_message.color = _rgb(255, 200, 100)
            self.shop_result_name.text = ""
            self.shop_result_rarity.text = ""
            save_game(self.save_data)
            self.shop_coins_text.text = f"Coins: {self.save_data['coins']}"
            return

        hatched = random.choice(pool)
        info = ANIMALS[hatched]
        self.save_data["unlocked_animals"].append(hatched)
        self.save_data["selected_animal"] = hatched
        save_game(self.save_data)

        rarity_name = RARITY_NAMES.get(info["rarity"], info["rarity"])
        rarity_color = RARITY_COLORS.get(info["rarity"], color.white)

        self.shop_message.text = f"EGG HATCHED!"
        self.shop_message.color = rarity_color
        self.shop_result_name.text = f"{info['name']}"
        self.shop_result_name.color = rarity_color
        self.shop_result_rarity.text = f"[{rarity_name}] {info['description']}"
        self.shop_result_rarity.color = rarity_color

        # Show color preview
        self.shop_preview_body.enabled = True
        self.shop_preview_body.color = info["body_color"]
        self.shop_preview_belly.enabled = True
        self.shop_preview_belly.color = info["belly_color"]
        self.shop_preview_accent.enabled = True
        self.shop_preview_accent.color = info["accent_color"]

        self.shop_coins_text.text = f"Coins: {self.save_data['coins']}"

    def _make_shop_click(self, key):
        def _click():
            info = ANIMALS[key]
            if key in self.save_data["unlocked_animals"]:
                self.save_data["selected_animal"] = key
                save_game(self.save_data)
                self.collection_msg.text = f"Selected {info['name']}!"
                self.collection_msg.color = _rgb(100, 255, 100)
            self._build_collection()
        return _click

    def _show_collection(self):
        self._hide_all_ui()
        self.state = "collection"
        self.collection_root.enabled = True
        self._build_collection()
        mouse.locked = False

    def _build_collection(self):
        for item in self.collection_items:
            destroy(item)
        self.collection_items = []
        owned = self.save_data["unlocked_animals"]
        cols = 5
        for i, key in enumerate(ANIMALS.keys()):
            info = ANIMALS[key]
            row, col = i // cols, i % cols
            x = -0.5 + col * 0.25
            y = 0.25 - row * 0.2
            is_owned = key in owned
            is_selected = key == self.save_data["selected_animal"]
            rarity_clr = RARITY_COLORS.get(info["rarity"], color.white)

            if is_owned:
                # Card background
                bg_color = _rgb(40, 80, 50) if is_selected else _rgb(35, 40, 55)
                card = Button(parent=self.collection_root, scale=(0.22, 0.17),
                              position=(x, y), color=bg_color,
                              highlight_color=_rgb(50, 90, 65) if is_selected else _rgb(50, 55, 70))
                # Body/belly/accent color circles
                Entity(parent=card, model="quad", color=info["body_color"],
                       scale=(0.15, 0.2), position=(-0.22, 0.15))
                Entity(parent=card, model="quad", color=info["belly_color"],
                       scale=(0.15, 0.2), position=(0, 0.15))
                Entity(parent=card, model="quad", color=info["accent_color"],
                       scale=(0.15, 0.2), position=(0.22, 0.15))
                # Name + rarity
                Text(parent=card, text=info["name"], scale=2.5,
                     position=(0, -0.1), origin=(0, 0), color=color.white)
                Text(parent=card, text=RARITY_NAMES.get(info["rarity"], ""), scale=1.8,
                     position=(0, -0.3), origin=(0, 0), color=rarity_clr)
                if is_selected:
                    Text(parent=card, text="EQUIPPED", scale=1.8,
                         position=(0, 0.35), origin=(0, 0), color=_rgb(100, 255, 100))
                card.on_click = self._make_shop_click(key)
                self.collection_items.append(card)
            else:
                # Locked card
                card = Entity(parent=self.collection_root, model="quad",
                              scale=(0.22, 0.17), position=(x, y),
                              color=_rgba(30, 30, 40, 200))
                Text(parent=card, text="???", scale=4,
                     position=(0, 0.05), origin=(0, 0), color=_rgb(80, 80, 90))
                Text(parent=card, text=RARITY_NAMES.get(info["rarity"], ""), scale=1.8,
                     position=(0, -0.3), origin=(0, 0), color=_rgba(int(rarity_clr.r*255), int(rarity_clr.g*255), int(rarity_clr.b*255), 100))
                self.collection_items.append(card)

    # ─── STATE TRANSITIONS ────────────────────────────────────────────────
    def _hide_all_ui(self):
        for ui in (self.menu_root, self.shop_root, self.hud_root, self.gameover_root,
                   self.announce_text, self.sub_announce, self.spec_root,
                   self.collection_root, self.egg_panel):
            ui.enabled = False

    def _show_menu(self):
        self._hide_all_ui()
        self._cleanup_round()
        self.state = "menu"
        self.menu_root.enabled = True
        self.menu_coins.text = f"Coins: {self.save_data['coins']}"
        self.menu_stats.text = f"Wins: {self.save_data['total_wins']}  |  Kills: {self.save_data['total_kills']}"
        self.menu_animal.text = f"Selected: {ANIMALS[self.save_data['selected_animal']]['name']}"
        camera.position = Vec3(0, 25, -30)
        camera.rotation = Vec3(30, 0, 0)
        mouse.locked = False

    def _show_shop(self):
        self._hide_all_ui()
        self.state = "shop"
        self.shop_root.enabled = True
        self.shop_coins_text.text = f"Coins: {self.save_data['coins']}"
        self.shop_message.text = ""
        self._build_shop_items()
        mouse.locked = False

    def _show_game_over(self, winner):
        self._hide_all_ui()
        self.state = "game_over"
        self.gameover_root.enabled = True
        mouse.locked = False
        if winner == self.player:
            self.gameover_title.text = "YOU WIN!"
            self.gameover_title.color = _rgb(255, 215, 0)
            bonus_coins, bonus_eggs = 150, EGGS_PER_WIN
            self.save_data["total_wins"] += 1
        else:
            self.gameover_title.text = f"{winner.name} WINS!"
            self.gameover_title.color = _rgb(200, 100, 100)
            bonus_coins, bonus_eggs = 30, 1
        self.save_data["coins"] += bonus_coins
        self.save_data["eggs"] += bonus_eggs
        self.save_data["total_kills"] += self.player.kills
        save_game(self.save_data)
        self.gameover_stats.text = (f"Your kills: {self.player.kills}\n"
                                     f"+{bonus_coins} coins  |  +{bonus_eggs} eggs")

    # ─── GAME START / ROUNDS ──────────────────────────────────────────────
    def _start_game(self):
        self._hide_all_ui()
        self.hud_root.enabled = True
        mouse.locked = False

        username = 'Player'
        if hasattr(self, 'menu_name_field') and self.menu_name_field.text.strip():
            username = self.menu_name_field.text.strip()
        self.save_data['username'] = username
        save_game(self.save_data)

        animal = self.save_data["selected_animal"]
        self.player = Fighter(username, animal_key=animal, is_player=True)
        self.bots = []
        used_names = set()
        for _ in range(BOT_COUNT):
            name = random.choice([n for n in BOT_NAMES if n not in used_names])
            used_names.add(name)
            ba = random.choice(list(ANIMALS.keys()))
            self.bots.append(Fighter(name, animal_key=ba, is_player=False))

        self.all_fighters = [self.player] + self.bots
        self.round_number = 0
        for f in self.all_fighters:
            f.wins = 0
            f.kills = 0
        self._start_round()

    def _start_round(self):
        # Hide spectator shop if it was open
        self.spec_root.enabled = False
        self.egg_panel.enabled = False
        # Destroy spectator character so camera returns to arena
        if self.spec_char:
            destroy(self.spec_char)
            self.spec_char = None
        self.round_number += 1
        self.turn_number = 0
        self.platform_size = PLATFORM_START_SIZE
        self.shrink_count = 0

        self.platform.scale = Vec3(PLATFORM_START_SIZE, PLATFORM_HEIGHT, PLATFORM_START_SIZE)
        self.platform_edge_warn.scale = Vec3(PLATFORM_START_SIZE * 0.95, 0.15, PLATFORM_START_SIZE * 0.95)
        self.platform_edge_warn.color = _rgba(255, 80, 80, 0)

        n = len(self.all_fighters)
        for i, f in enumerate(self.all_fighters):
            angle = (2 * math.pi * i) / n
            r = PLATFORM_START_SIZE * 0.35
            x, z = math.cos(angle) * r, math.sin(angle) * r
            f.spawn_model((x, PLATFORM_Y + 2, z), is_player=f.is_player)
            f.aim_angle = math.degrees(math.atan2(-x, -z))  # face center
            if f.model:
                f.model.rotation_y = f.aim_angle

        self.alive_count = n
        self.round_text.text = f"Round {self.round_number}"
        self._update_hud()

        # 3..2..1 countdown then first aim phase
        self.state = "countdown"
        self.countdown = 4
        self.announce_text.enabled = True
        self.sub_announce.enabled = True
        self.sub_announce.text = f"Round {self.round_number}"
        self.announce_text.text = "3..."

    def _cleanup_round(self):
        for f in self.all_fighters:
            if f.model:
                destroy(f.model)
                f.model = None
            if f.arrow_entity:
                destroy(f.arrow_entity)
                f.arrow_entity = None
            if f.arrow_head:
                destroy(f.arrow_head)
                f.arrow_head = None
            if f.shield_entity:
                destroy(f.shield_entity)
                f.shield_entity = None
        self.all_fighters = []
        self.bots = []
        self.player = None
        self._kill_feed_lines = []
        self.spec_root.enabled = False
        self.egg_panel.enabled = False
        if self.spec_char:
            destroy(self.spec_char)
            self.spec_char = None

    def _start_aim_phase(self):
        """Begin a new aim phase — everyone picks direction."""
        self.turn_number += 1
        self.aim_timer = AIM_TIME
        self.state = "aiming"

        # Shrink platform every 3 turns
        if self.turn_number > 1 and self.turn_number % 3 == 0:
            self._shrink_platform()

        for f in self.all_fighters:
            if f.alive:
                f.aim_locked = False
                f.aim_power = POWER_DEFAULT
                f.velocity = Vec3(0, 0, 0)
                # Bot picks random aim toward nearest enemy or random
                if not f.is_player:
                    self._bot_pick_aim(f)
                f.show_arrow(True)

        self.turn_text.text = f"Turn {self.turn_number}"
        self.controls_hint.text = "Mouse/A/D = Turn  |  Hold LClick = Power Up  |  Hold Space = Power Down  |  Right Click = Lock"
        self.announce_text.enabled = True
        self.announce_text.text = "AIM!"
        self.announce_text.color = _rgb(100, 200, 255)
        self.announce_text.scale = 3
        self.sub_announce.enabled = False
        invoke(setattr, self.announce_text, "enabled", False, delay=1)

    def _start_launch_phase(self):
        """Reveal all arrows, then launch everyone."""
        self.state = "launching"

        # Show ALL arrows (reveal bots)
        for f in self.all_fighters:
            if f.alive:
                f.aim_locked = True
                f.arrow_entity.color = _rgba(255, 255, 255, 255)
                f.arrow_head.color = _rgba(255, 255, 255, 255)
                f.show_arrow(True)

        # Announce
        self.announce_text.enabled = True
        self.announce_text.text = "LAUNCH!"
        self.announce_text.color = _rgb(255, 100, 50)
        self.announce_text.scale = 4
        self.sub_announce.enabled = False

        # Short reveal pause then launch
        invoke(self._do_launch, delay=0.8)

    def _do_launch(self):
        """Actually launch all fighters."""
        self.announce_text.enabled = False
        for f in self.all_fighters:
            if f.alive:
                f.launch()
                f.show_arrow(False)
                if f.model:
                    f.model.animate_walk(0.1)
        self.settle_timer = SETTLE_TIME
        self.state = "settle"
        self.controls_hint.text = ""

    def _check_round_end(self):
        """Check if round is over (LMS)."""
        alive = [f for f in self.all_fighters if f.alive]
        self.alive_count = len(alive)
        if len(alive) <= 1:
            winner = alive[0] if alive else self.all_fighters[0]
            winner.wins += 1
            if winner == self.player:
                self.save_data["coins"] += COINS_PER_ROUND_WIN
                self.save_data["eggs"] += EGGS_PER_ROUND
                save_game(self.save_data)
            if winner.wins >= ROUNDS_TO_WIN:
                invoke(self._show_game_over, winner, delay=2)
                self.state = "round_over"
                return True
            self.announce_text.enabled = True
            self.sub_announce.enabled = True
            self.announce_text.text = f"{winner.name} wins!"
            self.sub_announce.text = f"Score: {winner.wins}/{ROUNDS_TO_WIN}"
            self.state = "round_over"
            invoke(self._start_round, delay=3)
            return True
        return False

    # ─── BOT AI ───────────────────────────────────────────────────────────
    def _bot_pick_aim(self, bot):
        """Bot picks aim direction toward a target."""
        targets = [f for f in self.all_fighters if f.alive and f != bot]
        if not targets:
            bot.aim_angle = random.uniform(0, 360)
            bot.aim_power = random.uniform(0.3, 0.8)
            return
        # Usually aim at nearest, sometimes random
        if random.random() < 0.7:
            nearest = min(targets, key=lambda t: distance(bot.position, t.position) if t.model else 999)
            if nearest.model and bot.model:
                dx = nearest.model.position.x - bot.model.position.x
                dz = nearest.model.position.z - bot.model.position.z
                bot.aim_angle = math.degrees(math.atan2(dx, dz)) + random.uniform(-15, 15)
        else:
            bot.aim_angle = random.uniform(0, 360)
        bot.aim_power = random.uniform(0.4, 1.0)
        # Lock after random delay
        lock_delay = random.uniform(1.0, AIM_TIME - 0.5)
        invoke(self._bot_lock_aim, bot, delay=lock_delay)

    def _bot_lock_aim(self, bot):
        if self.state == "aiming" and bot.alive:
            bot.aim_locked = True
            bot.show_arrow(True)

    # ─── PLAYER INPUT (AIM PHASE) ────────────────────────────────────────
    def _handle_aim_input(self, dt):
        if not self.player or not self.player.alive or self.player.aim_locked:
            return
        p = self.player
        # Move mouse left/right to turn the arrow
        p.aim_angle += mouse.velocity[0] * 300
        # A/D keys also work
        if held_keys["a"]:
            p.aim_angle -= 150 * dt
        if held_keys["d"]:
            p.aim_angle += 150 * dt
        # Power with W/S
        if held_keys["w"]:
            p.aim_power = min(1.0, p.aim_power + 0.4 * dt)
        if held_keys["s"]:
            p.aim_power = max(0.1, p.aim_power - 0.4 * dt)
        # Hold left click to charge power up, hold space to reduce
        if held_keys["left mouse"]:
            p.aim_power = min(1.0, p.aim_power + 0.3 * dt)
        if held_keys["space"]:
            p.aim_power = max(0.1, p.aim_power - 0.3 * dt)
        # Smoothly rotate model to face aim direction
        if p.model:
            current = p.model.rotation_y
            diff = (p.aim_angle - current + 180) % 360 - 180
            p.model.rotation_y += diff * dt * 12
        p.show_arrow(True)
        self.power_text.text = f"Power: {int(p.aim_power * 100)}%"

    # ─── PHYSICS ──────────────────────────────────────────────────────────
    def _update_physics(self, fighter, dt):
        if not fighter.alive or not fighter.model:
            return
        fighter.velocity.y -= GRAVITY * dt
        # Friction
        if fighter.grounded:
            fighter.velocity.x *= ICE_FRICTION
            fighter.velocity.z *= ICE_FRICTION
        else:
            fighter.velocity.x *= 0.99
            fighter.velocity.z *= 0.99
        # Clamp
        for attr in ("x", "y", "z"):
            v = getattr(fighter.velocity, attr)
            setattr(fighter.velocity, attr, max(-MAX_VELOCITY, min(MAX_VELOCITY, v)))
        fighter.position += fighter.velocity * dt
        fighter.model.position = fighter.position

        # Ground
        dist_xz = math.sqrt(fighter.position.x ** 2 + fighter.position.z ** 2)
        on_platform = dist_xz < self.platform_size * 0.48
        if fighter.position.y <= PLATFORM_Y + PLATFORM_HEIGHT + 0.05 and on_platform:
            fighter.position.y = PLATFORM_Y + PLATFORM_HEIGHT + 0.05
            fighter.velocity.y = max(0, fighter.velocity.y)
            fighter.grounded = True
        else:
            if fighter.position.y > PLATFORM_Y + PLATFORM_HEIGHT + 0.2:
                fighter.grounded = False
        fighter.model.position = fighter.position

        # Fell off
        if fighter.position.y < FALL_Y:
            spawn_fall_particles(fighter.position + Vec3(0, 2, 0))
            fighter.die()
            self.alive_count -= 1
            self._add_kill_feed(f"{fighter.name} fell off!")
            # If player fell, enter spectator mode with egg shop
            if fighter == self.player:
                self._enter_spectator()

    def _check_collisions(self):
        """Check all alive fighters for bumping into each other."""
        alive = [f for f in self.all_fighters if f.alive and f.model]
        for i in range(len(alive)):
            for j in range(i + 1, len(alive)):
                a, b = alive[i], alive[j]
                d = distance(a.model.position, b.model.position)
                if d < BUMP_RADIUS and d > 0.01:
                    # Bump! Push each other apart
                    direction = (b.model.position - a.model.position)
                    direction.y = 0
                    if direction.length() < 0.01:
                        direction = Vec3(random.uniform(-1, 1), 0, random.uniform(-1, 1))
                    dn = direction.normalized()

                    # Knockback based on relative speed
                    rel_speed = (a.velocity - b.velocity).length()
                    kb = BUMP_KNOCKBACK * (1 + rel_speed * 0.1)

                    # Lighter fighters get pushed more
                    a_kb = kb / max(0.5, a.weight) * b.knockback_resist
                    b_kb = kb / max(0.5, b.weight) * a.knockback_resist

                    a.velocity -= dn * a_kb * 0.5
                    a.velocity.y = max(a.velocity.y, 2)
                    b.velocity += dn * b_kb * 0.5
                    b.velocity.y = max(b.velocity.y, 2)

                    a.damage_taken += kb * 0.3
                    b.damage_taken += kb * 0.3

                    if a.model:
                        a.model.animate_hit()
                    if b.model:
                        b.model.animate_hit()
                    mid = (a.model.position + b.model.position) * 0.5
                    spawn_hit_particles(mid + Vec3(0, 1, 0))

    # ─── PLATFORM SHRINK ─────────────────────────────────────────────────
    # ─── SPECTATOR + EGG SHOP (when player dies) ──────────────────────────
    def _enter_spectator(self):
        self.spec_root.enabled = True
        self.spec_label.text = "YOU FELL OFF!"
        self.spec_coins_text.text = f"Coins: {self.save_data['coins']}"
        self.spec_shop_msg.text = ""
        mouse.locked = False
        # Spawn walkable character on spectator platform
        self.spec_pos = Vec3(30, 18.75, 0)
        if self.spec_char:
            destroy(self.spec_char)
        animal = self.save_data["selected_animal"]
        self.spec_char = AnimalModel(animal_key=animal, is_player=True,
                                      nametag=self.save_data.get('username', 'You'),
                                      position=self.spec_pos)

    def _update_spectator(self, dt):
        if not self.spec_char:
            return
        # Move with arrow keys — relative to camera direction
        move = Vec3(0, 0, 0)
        cam_yaw = getattr(self, '_spec_cam_yaw', 0)
        cam_rad = math.radians(cam_yaw)
        fwd = Vec3(-math.sin(cam_rad), 0, -math.cos(cam_rad))
        right = Vec3(-math.cos(cam_rad), 0, math.sin(cam_rad))
        if held_keys["up arrow"]:
            move += fwd
        if held_keys["down arrow"]:
            move -= fwd
        if held_keys["left arrow"]:
            move -= right
        if held_keys["right arrow"]:
            move += right
        if move.length() > 0:
            move = move.normalized() * 6 * dt
            self.spec_pos += move
            self.spec_pos.x = max(23, min(37, self.spec_pos.x))
            self.spec_pos.z = max(-5, min(5, self.spec_pos.z))
            self.spec_pos.y = 18.75
            self.spec_char.position = self.spec_pos
            angle = math.degrees(math.atan2(move.x, move.z))
            self.spec_char.rotation_y = angle
            self.spec_char.animate_walk(dt)
        else:
            self.spec_char.animate_idle(dt)

        # Check proximity to shop stand (at ~34, 18.75, 0)
        dist_to_shop = math.sqrt((self.spec_pos.x - 34)**2 + (self.spec_pos.z - 0)**2)
        if dist_to_shop < 3:
            self.spec_near_shop.text = "Press E to buy eggs!"
        else:
            self.spec_near_shop.text = ""
            if self.egg_panel.enabled:
                self.egg_panel.enabled = False

        # Rotate display skin on pedestal
        if hasattr(self, 'shop_display_skin') and self.shop_display_skin:
            self.shop_display_skin.rotation_y += dt * 30

        # Camera: A/D keys rotate view horizontally around character
        if not hasattr(self, '_spec_cam_yaw'):
            self._spec_cam_yaw = 0
            self._spec_cam_dist = 10
        if held_keys["a"] and not held_keys["left arrow"]:
            self._spec_cam_yaw -= 90 * dt
        if held_keys["d"] and not held_keys["right arrow"]:
            self._spec_cam_yaw += 90 * dt
        rad = math.radians(self._spec_cam_yaw)
        d = self._spec_cam_dist
        cam_x = self.spec_pos.x + math.sin(rad) * d
        cam_z = self.spec_pos.z + math.cos(rad) * d
        cam_y = self.spec_pos.y + 5
        camera.position = lerp(camera.position, Vec3(cam_x, cam_y, cam_z), dt * 6)
        # Use rotation instead of look_at to avoid flip
        dx = self.spec_pos.x - camera.x
        dz = self.spec_pos.z - camera.z
        dy = (self.spec_pos.y + 1) - camera.y
        yaw = math.degrees(math.atan2(dx, dz))
        pitch = math.degrees(math.atan2(-dy, math.sqrt(dx*dx + dz*dz)))
        camera.rotation = Vec3(pitch, yaw, 0)

        self.spec_coins_text.text = f"Coins: {self.save_data['coins']}"

    def _spec_hatch(self, tier):
        egg = EGG_TIERS[tier]
        if self.save_data["coins"] < egg["cost"]:
            self.spec_shop_msg.text = f"Need {egg['cost']} coins!"
            self.spec_shop_msg.color = _rgb(255, 100, 100)
            self._update_spec_shop()
            return
        self.save_data["coins"] -= egg["cost"]
        weights = egg["weights"]
        roll = random.randint(1, 100)
        cumulative = 0
        chosen_rarity = "common"
        for rarity, weight in weights.items():
            cumulative += weight
            if roll <= cumulative:
                chosen_rarity = rarity
                break
        pool = [k for k, v in ANIMALS.items() if v["rarity"] == chosen_rarity
                and k not in self.save_data["unlocked_animals"]]
        if not pool:
            pool = [k for k in ANIMALS if k not in self.save_data["unlocked_animals"]]
        if not pool:
            self.save_data["coins"] += egg["cost"]
            self.spec_shop_msg.text = "All skins owned! Refunded."
            self.spec_shop_msg.color = _rgb(255, 200, 100)
            save_game(self.save_data)
            self._update_spec_shop()
            return
        hatched = random.choice(pool)
        info = ANIMALS[hatched]
        self.save_data["unlocked_animals"].append(hatched)
        save_game(self.save_data)
        rarity_clr = RARITY_COLORS.get(info["rarity"], color.white)
        rname = RARITY_NAMES.get(info["rarity"], "")
        self.spec_shop_msg.text = f"HATCHED: {info['name']} [{rname}]!"
        self.spec_shop_msg.color = rarity_clr
        self._update_spec_shop()

    def _buy_eggs(self, count):
        pass  # legacy compat

    def _shrink_platform(self):
        self.platform_size = max(PLATFORM_MIN_SIZE, self.platform_size - PLATFORM_SHRINK_AMOUNT)
        self.platform.animate_scale(Vec3(self.platform_size, PLATFORM_HEIGHT, self.platform_size),
                                     duration=1.5, curve=curve.in_out_expo)
        self.platform_edge_warn.color = _rgba(255, 80, 80, 150)
        self.platform_edge_warn.animate_color(_rgba(255, 80, 80, 0), duration=2)
        self._add_kill_feed(">> Platform shrinking!")

    # ─── HUD ─────────────────────────────────────────────────────────────
    def _update_hud(self):
        if not self.player:
            return
        dmg = int(self.player.damage_taken)
        if dmg < 50:
            self.damage_pct_text.color = color.white
        elif dmg < 100:
            self.damage_pct_text.color = _rgb(255, 200, 50)
        else:
            self.damage_pct_text.color = _rgb(255, 50, 50)
        self.damage_pct_text.text = f"{dmg}%"
        self.coin_text.text = f"Coins: {self.save_data['coins']}"
        self.egg_text.text = f"Eggs: {self.save_data['eggs']}"
        self.alive_text.text = f"Alive: {self.alive_count}/{len(self.all_fighters)}"

    def _add_kill_feed(self, msg):
        self._kill_feed_lines.append(msg)
        if len(self._kill_feed_lines) > 6:
            self._kill_feed_lines.pop(0)
        self.kill_feed.text = "\n".join(self._kill_feed_lines)
        invoke(self._remove_old_kill, delay=5)

    def _remove_old_kill(self):
        if self._kill_feed_lines:
            self._kill_feed_lines.pop(0)
            self.kill_feed.text = "\n".join(self._kill_feed_lines)

    # ─── CAMERA ──────────────────────────────────────────────────────────
    def _update_camera(self):
        # If on spectator platform, camera handled by _update_spectator
        if self.spec_char:
            return
        # Normal overhead view
        target = Vec3(0, 50, -20)
        camera.position = lerp(camera.position, target, time.dt * 4)
        camera.look_at(Vec3(0, -3, 0))

    # ─── MAIN UPDATE ─────────────────────────────────────────────────────
    def update(self):
        dt = time.dt

        # ── Countdown 3..2..1..GO ──
        if self.state == "countdown":
            self.countdown -= dt
            r = self.countdown
            if r > 3:
                self.announce_text.text = "3..."
                self.announce_text.color = color.white
                self.announce_text.scale = 3
            elif r > 2:
                self.announce_text.text = "2.."
                self.announce_text.color = _rgb(255, 200, 50)
                self.announce_text.scale = 3.5
            elif r > 1:
                self.announce_text.text = "1."
                self.announce_text.color = _rgb(255, 100, 50)
                self.announce_text.scale = 4
            elif r > 0:
                self.announce_text.text = "GO!"
                self.announce_text.color = _rgb(50, 255, 80)
                self.announce_text.scale = 5
                self.sub_announce.text = ""
            else:
                self.announce_text.enabled = False
                self.sub_announce.enabled = False
                self._start_aim_phase()
            self._update_camera()
            return

        # ── AIM PHASE ──
        if self.state == "aiming":
            self.aim_timer -= dt
            self._handle_aim_input(dt)
            # Timer display
            secs = max(0, int(self.aim_timer) + 1)
            self.timer_text.text = str(secs)
            if secs <= 2:
                self.timer_text.color = _rgb(255, 80, 80)
                self.timer_text.scale = 4
            else:
                self.timer_text.color = color.white
                self.timer_text.scale = 3
            self.phase_text.text = "AIM YOUR LAUNCH!"

            # Idle animation
            for f in self.all_fighters:
                if f.alive and f.model:
                    f.model.animate_idle(dt)

            # Time up or everyone locked
            all_locked = all(f.aim_locked or not f.alive for f in self.all_fighters)
            if self.aim_timer <= 0 or all_locked:
                self.timer_text.text = ""
                self.phase_text.text = ""
                self.power_text.text = ""
                self._start_launch_phase()

            self._update_camera()
            self._update_hud()
            if self.spec_char:
                self._update_spectator(dt)
            return

        # ── LAUNCHING (brief reveal) ──
        if self.state == "launching":
            self._update_camera()
            if self.spec_char:
                self._update_spectator(dt)
            return

        # ── SETTLE PHASE (physics play out) ──
        if self.state == "settle":
            self.settle_timer -= dt
            for f in self.all_fighters:
                self._update_physics(f, dt)
            self._check_collisions()

            # Show timer
            secs = max(0, int(self.settle_timer) + 1)
            self.timer_text.text = str(secs) if self.settle_timer > 0.5 else ""
            self.timer_text.color = _rgb(200, 200, 200)
            self.timer_text.scale = 2
            self.phase_text.text = "..." if self.settle_timer > 0.5 else ""

            # Check if anyone fell
            if self._check_round_end():
                self.timer_text.text = ""
                self.phase_text.text = ""
                self._update_hud()
                self._update_camera()
                return

            # Settle done → new aim phase
            if self.settle_timer <= 0:
                # Check if all are still, or time is up
                self.timer_text.text = ""
                self.phase_text.text = ""
                self._start_aim_phase()

            self._update_camera()
            self._update_hud()
            if self.spec_char:
                self._update_spectator(dt)
            return

        # ── ROUND OVER (waiting for next) ──
        if self.state == "round_over":
            self._update_camera()
            if self.spec_char:
                self._update_spectator(dt)
            return

    # ─── INPUT EVENTS ────────────────────────────────────────────────────
    def input(self, key):
        if key == "escape":
            if self.state in ("aiming", "launching", "settle", "round_over", "countdown"):
                self._show_menu()

        # Lock aim with right click or space
        if self.state == "aiming" and self.player and self.player.alive and not self.player.aim_locked:
            if key in ("right mouse down",):
                self.player.aim_locked = True
                self.player.show_arrow(True)
                self.power_text.text = "AIM LOCKED!"
                self.power_text.color = _rgb(100, 255, 100)
                self.controls_hint.text = "Waiting for others..."
            # Scroll wheel for power
            if key == "scroll up" and self.player:
                self.player.aim_power = min(1.0, self.player.aim_power + 0.05)
            if key == "scroll down" and self.player:
                self.player.aim_power = max(0.1, self.player.aim_power - 0.05)

        # Spectator camera zoom with scroll
        if self.spec_char:
            if key == "scroll up":
                self._spec_cam_dist = max(5, getattr(self, '_spec_cam_dist', 12) - 1)
            if key == "scroll down":
                self._spec_cam_dist = min(25, getattr(self, '_spec_cam_dist', 12) + 1)

        # E key to open egg shop when near the stand (spectating)
        if key == "e" and self.spec_char and self.spec_root.enabled:
            dist_to_shop = math.sqrt((self.spec_pos.x - 34)**2 + (self.spec_pos.z - 0)**2)
            if dist_to_shop < 3:
                self.egg_panel.enabled = not self.egg_panel.enabled
                if self.egg_panel.enabled:
                    self.egg_panel_coins.text = f"Coins: {self.save_data['coins']}"

    # ─── RUN ─────────────────────────────────────────────────────────────
    def run(self):
        scene_updater = Entity()
        scene_updater.update = self.update
        scene_updater.input = self.input
        self.app.run()


# ═══════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    game = DontFallGame()
    game.run()
