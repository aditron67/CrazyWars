import pygame
import math
import random
import sys

# --- Constants ---
WIDTH, HEIGHT = 1024, 700
FPS = 60
GRAVITY = 0.3
GROUND_Y = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
BLUE = (50, 100, 220)
GREEN = (50, 200, 50)
YELLOW = (255, 220, 50)
ORANGE = (255, 140, 0)
GRAY = (150, 150, 150)
DARK_GRAY = (80, 80, 80)
SKY_BLUE = (135, 200, 235)
BROWN = (139, 90, 43)
DARK_GREEN = (34, 120, 34)
LIGHT_BLUE = (100, 180, 255)

# Arrow types: unlocked by accumulating XP
ARROW_TYPES = {
    "normal":    {"color": BROWN,      "damage": 20, "speed": 1.0, "xp_needed": 0},
    "fire":      {"color": ORANGE,     "damage": 30, "speed": 1.0, "xp_needed": 100},
    "ice":       {"color": LIGHT_BLUE, "damage": 15, "speed": 0.8, "xp_needed": 200},
    "triple":    {"color": GREEN,      "damage": 15, "speed": 1.0, "xp_needed": 300},
    "explosive": {"color": RED,        "damage": 50, "speed": 0.7, "xp_needed": 400},
}


# ---------------------------------------------------------------------------
# Minimal 2-D vector helper
# ---------------------------------------------------------------------------
class Vec2:
    __slots__ = ("x", "y")

    def __init__(self, x=0.0, y=0.0):
        self.x = float(x)
        self.y = float(y)

    def copy(self):
        return Vec2(self.x, self.y)

    def length(self):
        return math.hypot(self.x, self.y)

    def dist(self, other):
        return math.hypot(self.x - other.x, self.y - other.y)

    def normalized(self):
        ln = self.length()
        return Vec2(self.x / ln, self.y / ln) if ln else Vec2()

    def __add__(self, o):
        return Vec2(self.x + o.x, self.y + o.y)

    def __sub__(self, o):
        return Vec2(self.x - o.x, self.y - o.y)

    def __mul__(self, s):
        return Vec2(self.x * s, self.y * s)


# ---------------------------------------------------------------------------
# Verlet physics primitives
# ---------------------------------------------------------------------------
class VerletPoint:
    def __init__(self, x, y, pinned=False):
        self.pos = Vec2(x, y)
        self.old = Vec2(x, y)
        self.pinned = pinned

    def update(self, grav=GRAVITY):
        if self.pinned:
            return
        vx = (self.pos.x - self.old.x) * 0.99
        vy = (self.pos.y - self.old.y) * 0.99
        self.old.x = self.pos.x
        self.old.y = self.pos.y
        self.pos.x += vx
        self.pos.y += vy + grav


class Stick:
    def __init__(self, a, b, length=None):
        self.a = a
        self.b = b
        self.length = length if length is not None else a.pos.dist(b.pos)

    def solve(self):
        dx = self.b.pos.x - self.a.pos.x
        dy = self.b.pos.y - self.a.pos.y
        d = math.hypot(dx, dy) or 0.0001
        diff = (self.length - d) / d * 0.5
        if not self.a.pinned and not self.b.pinned:
            self.a.pos.x -= dx * diff
            self.a.pos.y -= dy * diff
            self.b.pos.x += dx * diff
            self.b.pos.y += dy * diff
        elif self.a.pinned:
            self.b.pos.x += dx * diff * 2
            self.b.pos.y += dy * diff * 2
        elif self.b.pinned:
            self.a.pos.x -= dx * diff * 2
            self.a.pos.y -= dy * diff * 2


# ---------------------------------------------------------------------------
# Ragdoll (stick-figure character)
# ---------------------------------------------------------------------------
class Ragdoll:
    def __init__(self, x, y, color, facing=1):
        self.color = color
        self.facing = facing
        self.health = 100
        self.max_health = 100
        self.active = True
        self.is_ragdoll = False
        self.hit_flash = 0

        # Build skeleton centred on (x, y) which is roughly hip-level
        f = facing
        self.head      = VerletPoint(x, y - 60)
        self.neck      = VerletPoint(x, y - 45)
        self.shoulder  = VerletPoint(x, y - 40)
        self.hip       = VerletPoint(x, y - 5)
        self.l_elbow   = VerletPoint(x - 15 * f, y - 25)
        self.l_hand    = VerletPoint(x - 25 * f, y - 15)
        self.r_elbow   = VerletPoint(x + 15 * f, y - 25)
        self.r_hand    = VerletPoint(x + 30 * f, y - 30)
        self.l_knee    = VerletPoint(x - 8, y + 15)
        self.l_foot    = VerletPoint(x - 10, y + 35)
        self.r_knee    = VerletPoint(x + 8, y + 15)
        self.r_foot    = VerletPoint(x + 10, y + 35)

        self.points = [
            self.head, self.neck, self.shoulder, self.hip,
            self.l_elbow, self.l_hand, self.r_elbow, self.r_hand,
            self.l_knee, self.l_foot, self.r_knee, self.r_foot,
        ]

        self.sticks = [
            Stick(self.head, self.neck, 15),
            Stick(self.neck, self.shoulder, 5),
            Stick(self.shoulder, self.hip, 35),
            Stick(self.shoulder, self.l_elbow, 20),
            Stick(self.l_elbow, self.l_hand, 18),
            Stick(self.shoulder, self.r_elbow, 20),
            Stick(self.r_elbow, self.r_hand, 18),
            Stick(self.hip, self.l_knee, 22),
            Stick(self.l_knee, self.l_foot, 22),
            Stick(self.hip, self.r_knee, 22),
            Stick(self.r_knee, self.r_foot, 22),
        ]

        # Hit-boxes: (point, radius, damage multiplier)
        self.body_parts = {
            "head":  (self.head, 12, 2.5),
            "torso": (self.shoulder, 15, 1.0),
            "hip":   (self.hip, 12, 0.8),
            "l_arm": (self.l_elbow, 8, 0.5),
            "r_arm": (self.r_elbow, 8, 0.5),
            "l_leg": (self.l_knee, 8, 0.6),
            "r_leg": (self.r_knee, 8, 0.6),
        }

        self.stand_x = x
        self.stand_y = y

        # Store the initial offsets from stand position for each point
        self._pose_offsets = []
        for p in self.points:
            self._pose_offsets.append((p.pos.x - x, p.pos.y - y))

        # Arrows stuck in this ragdoll: list of (arrow_obj, body_part_name, offset_x, offset_y)
        self.stuck_arrows = []
        # Body part hit flash: {part_name: frames_remaining}
        self.part_flash = {}

    # -- helpers --
    def centre(self):
        return Vec2(self.shoulder.pos.x, self.shoulder.pos.y)

    def set_position(self, x, y):
        dx = x - self.shoulder.pos.x
        dy = y - self.shoulder.pos.y
        for p in self.points:
            p.pos.x += dx;  p.pos.y += dy
            p.old.x += dx;  p.old.y += dy
        self.stand_x = x
        self.stand_y = y

    def apply_force(self, fx, fy):
        if self.is_ragdoll:
            for p in self.points:
                if not p.pinned:
                    p.pos.x += fx
                    p.pos.y += fy
        else:
            # When standing, horizontal force moves the whole character
            self.stand_x += fx

    def apply_force_at(self, pt, fx, fy):
        if not pt.pinned:
            pt.pos.x += fx
            pt.pos.y += fy

    def add_stuck_arrow(self, arrow, part_name):
        """Pin an arrow to a body part so it moves with the ragdoll."""
        if part_name in self.body_parts:
            pt = self.body_parts[part_name][0]
            ox = arrow.pos.x - pt.pos.x
            oy = arrow.pos.y - pt.pos.y
            self.stuck_arrows.append((arrow, part_name, ox, oy))

    # -- damage --
    def take_damage(self, damage, part_name, arrow_vel):
        mult = self.body_parts[part_name][2] if part_name in self.body_parts else 1
        actual = damage * mult
        self.health -= actual
        self.hit_flash = 10
        self.part_flash[part_name] = 20  # flash the hit limb red

        if arrow_vel:
            n = arrow_vel.normalized()
            if part_name in self.body_parts:
                self.apply_force_at(self.body_parts[part_name][0], n.x * 3, n.y * 3)
            self.apply_force(n.x * 0.9, n.y * 0.9)

        if self.health <= 0:
            self.health = 0
            self.is_ragdoll = True
            self.active = False
            for p in self.points:
                p.pinned = False
            if arrow_vel:
                n = arrow_vel.normalized()
                self.apply_force(n.x * 8, n.y * 8 - 5)
        return actual

    # -- physics --
    def update(self, platforms):
        if self.is_ragdoll:
            # Full ragdoll physics
            for p in self.points:
                p.update(GRAVITY)
            for _ in range(5):
                for s in self.sticks:
                    s.solve()
                self._collide(platforms)
        else:
            # Standing mode: snap skeleton to pose, only allow horizontal movement
            self._maintain_pose(platforms)

        if self.hit_flash > 0:
            self.hit_flash -= 1
        for k in list(self.part_flash):
            self.part_flash[k] -= 1
            if self.part_flash[k] <= 0:
                del self.part_flash[k]

        # Update stuck arrows to follow body
        for (ar, pname, ox, oy) in self.stuck_arrows:
            if pname in self.body_parts:
                pt = self.body_parts[pname][0]
                ar.pos.x = pt.pos.x + ox
                ar.pos.y = pt.pos.y + oy

    def _maintain_pose(self, platforms):
        """Keep the character in a standing pose pinned to stand_x/stand_y."""
        # Clamp stand_x within screen
        self.stand_x = max(20, min(WIDTH - 20, self.stand_x))

        # The character's feet are roughly at stand_y + 35
        feet_y = self.stand_y + 35

        # Find the ground or platform the character is standing on
        # Only count a platform if the feet are within a few pixels of its top
        foot_y = GROUND_Y
        for (px, py, pw, ph) in platforms:
            if px <= self.stand_x <= px + pw:
                # Feet must be near the platform top (within 10 pixels above or touching)
                if py - 10 <= feet_y <= py + ph:
                    foot_y = min(foot_y, py)

        base_y = foot_y
        bx = self.stand_x

        # Smoothly lerp each point toward its pose position
        lerp = 0.4
        for i, p in enumerate(self.points):
            ox, oy = self._pose_offsets[i]
            tx = bx + ox
            ty = base_y - 35 + oy  # -35 because stand_y was y which is GROUND_Y-35
            p.pos.x += (tx - p.pos.x) * lerp
            p.pos.y += (ty - p.pos.y) * lerp
            p.old.x = p.pos.x
            p.old.y = p.pos.y

        self.stand_y = base_y - 35

    def _collide(self, platforms):
        for p in self.points:
            if p.pos.y > GROUND_Y:
                p.pos.y = GROUND_Y
                vx = p.pos.x - p.old.x
                p.old.x = p.pos.x - vx * 0.8
            for (px, py, pw, ph) in platforms:
                if px <= p.pos.x <= px + pw and py <= p.pos.y <= py + ph and p.old.y <= py + 2:
                    p.pos.y = py
                    vx = p.pos.x - p.old.x
                    p.old.x = p.pos.x - vx * 0.8
            p.pos.x = max(10, min(WIDTH - 10, p.pos.x))

    # -- drawing --
    def _part_color(self, *part_names):
        """Return RED if any of the given parts are flashing, else default."""
        for pn in part_names:
            if pn in self.part_flash:
                return RED
        if self.hit_flash > 0 and self.hit_flash % 2 == 0:
            return WHITE
        return self.color

    def draw(self, surf, aim_angle=None, is_aiming=False):
        w = 3

        def line(a, b, color=None, width=w):
            col = color if color else self.color
            if self.hit_flash > 0 and self.hit_flash % 2 == 0 and color is None:
                col = WHITE
            pygame.draw.line(surf, col, (int(a.pos.x), int(a.pos.y)),
                             (int(b.pos.x), int(b.pos.y)), width)

        # torso
        tc = self._part_color("torso", "hip")
        pygame.draw.line(surf, tc, (int(self.neck.pos.x), int(self.neck.pos.y)),
                         (int(self.hip.pos.x), int(self.hip.pos.y)), w + 1)
        # left arm
        lac = self._part_color("l_arm")
        pygame.draw.line(surf, lac, (int(self.shoulder.pos.x), int(self.shoulder.pos.y)),
                         (int(self.l_elbow.pos.x), int(self.l_elbow.pos.y)), w)
        pygame.draw.line(surf, lac, (int(self.l_elbow.pos.x), int(self.l_elbow.pos.y)),
                         (int(self.l_hand.pos.x), int(self.l_hand.pos.y)), w)
        # right arm
        rac = self._part_color("r_arm")
        pygame.draw.line(surf, rac, (int(self.shoulder.pos.x), int(self.shoulder.pos.y)),
                         (int(self.r_elbow.pos.x), int(self.r_elbow.pos.y)), w)
        pygame.draw.line(surf, rac, (int(self.r_elbow.pos.x), int(self.r_elbow.pos.y)),
                         (int(self.r_hand.pos.x), int(self.r_hand.pos.y)), w)
        # left leg
        llc = self._part_color("l_leg")
        pygame.draw.line(surf, llc, (int(self.hip.pos.x), int(self.hip.pos.y)),
                         (int(self.l_knee.pos.x), int(self.l_knee.pos.y)), w)
        pygame.draw.line(surf, llc, (int(self.l_knee.pos.x), int(self.l_knee.pos.y)),
                         (int(self.l_foot.pos.x), int(self.l_foot.pos.y)), w)
        # right leg
        rlc = self._part_color("r_leg")
        pygame.draw.line(surf, rlc, (int(self.hip.pos.x), int(self.hip.pos.y)),
                         (int(self.r_knee.pos.x), int(self.r_knee.pos.y)), w)
        pygame.draw.line(surf, rlc, (int(self.r_knee.pos.x), int(self.r_knee.pos.y)),
                         (int(self.r_foot.pos.x), int(self.r_foot.pos.y)), w)

        # head
        hc = self._part_color("head")
        hx, hy = int(self.head.pos.x), int(self.head.pos.y)
        pygame.draw.circle(surf, hc, (hx, hy), 10)
        pygame.draw.circle(surf, BLACK, (hx, hy), 10, 2)

        # --- Bow ---
        self._draw_bow(surf, aim_angle, is_aiming)

        # --- Draw stuck arrows ---
        for (ar, pname, ox, oy) in self.stuck_arrows:
            if ar.active:
                ar.draw(surf)

        # health bar
        if self.active:
            bw, bh = 40, 5
            bx = hx - bw // 2
            by = hy - 22
            fill = max(0, self.health / self.max_health)
            pygame.draw.rect(surf, RED, (bx, by, bw, bh))
            pygame.draw.rect(surf, GREEN, (bx, by, int(bw * fill), bh))
            pygame.draw.rect(surf, BLACK, (bx, by, bw, bh), 1)

    def _draw_bow(self, surf, aim_angle=None, is_aiming=False):
        """Draw a bow on the character's hand."""
        if self.is_ragdoll:
            return
        hx, hy = self.r_hand.pos.x, self.r_hand.pos.y

        # Determine bow facing angle
        if aim_angle is not None:
            angle = aim_angle
        else:
            angle = math.atan2(self.r_hand.pos.y - self.shoulder.pos.y,
                               self.r_hand.pos.x - self.shoulder.pos.x)

        bow_len = 22
        perp = angle + math.pi / 2
        # Bow arc: three-point curve
        top = (int(hx + math.cos(perp) * bow_len), int(hy + math.sin(perp) * bow_len))
        bot = (int(hx - math.cos(perp) * bow_len), int(hy - math.sin(perp) * bow_len))
        # Bow bend outward
        bend = 10 if is_aiming else 6
        mid = (int(hx + math.cos(angle) * bend), int(hy + math.sin(angle) * bend))

        # Draw bow arc (two lines through midpoint)
        pygame.draw.line(surf, BROWN, top, mid, 3)
        pygame.draw.line(surf, BROWN, mid, bot, 3)
        # Bowstring
        string_pull = -8 if is_aiming else -2
        string_mid = (int(hx + math.cos(angle) * string_pull),
                       int(hy + math.sin(angle) * string_pull))
        pygame.draw.line(surf, DARK_GRAY, top, string_mid, 1)
        pygame.draw.line(surf, DARK_GRAY, string_mid, bot, 1)


# ---------------------------------------------------------------------------
# Arrow projectile
# ---------------------------------------------------------------------------
class Arrow:
    def __init__(self, x, y, vx, vy, arrow_type="normal", owner=None):
        self.pos = Vec2(x, y)
        self.vel = Vec2(vx, vy)
        self.arrow_type = arrow_type
        self.owner = owner
        self.active = True
        self.stuck = False
        self.stuck_timer = 0
        self.lifetime = 300
        self.trail = []

        props = ARROW_TYPES.get(arrow_type, ARROW_TYPES["normal"])
        self.damage = props["damage"]
        self.color = props["color"]

    def update(self):
        if self.stuck:
            self.stuck_timer += 1
            if self.stuck_timer > 300:  # stuck arrows last 5 seconds
                self.active = False
            return

        self.trail.append((self.pos.x, self.pos.y))
        if len(self.trail) > 8:
            self.trail.pop(0)

        # Arrows fly in a straight line (no gravity)
        self.pos.x += self.vel.x
        self.pos.y += self.vel.y

        self.lifetime -= 1
        if self.lifetime <= 0 or self.pos.y > GROUND_Y + 50 or self.pos.x < -50 or self.pos.x > WIDTH + 50:
            self.active = False

        if self.pos.y >= GROUND_Y:
            self.pos.y = GROUND_Y
            self.stuck = True

    def check_hit(self, ragdoll):
        if self.stuck or not self.active or ragdoll is self.owner:
            return False, None
        for name, (pt, radius, _) in ragdoll.body_parts.items():
            if (self.pos.x - pt.pos.x) ** 2 + (self.pos.y - pt.pos.y) ** 2 < radius * radius:
                self.stuck = True
                ragdoll.add_stuck_arrow(self, name)
                return True, name
        return False, None

    def check_platform(self, platforms):
        if self.stuck:
            return
        for (px, py, pw, ph) in platforms:
            if px <= self.pos.x <= px + pw and py <= self.pos.y <= py + ph:
                self.stuck = True
                return

    def draw(self, surf):
        if not self.active:
            return
        # trail
        for i, (tx, ty) in enumerate(self.trail):
            a = (i + 1) / max(len(self.trail), 1)
            r = max(1, int(a * 2))
            pygame.draw.circle(surf, self.color, (int(tx), int(ty)), r)

        angle = math.atan2(self.vel.y, self.vel.x)
        length = 20
        cx, cy = self.pos.x, self.pos.y
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        tip  = (int(cx + cos_a * length * 0.5), int(cy + sin_a * length * 0.5))
        tail = (int(cx - cos_a * length * 0.5), int(cy - sin_a * length * 0.5))
        pygame.draw.line(surf, self.color, tail, tip, 2)

        # arrowhead
        hs = 6
        pygame.draw.polygon(surf, self.color, [
            tip,
            (int(tip[0] - math.cos(angle - 0.4) * hs), int(tip[1] - math.sin(angle - 0.4) * hs)),
            (int(tip[0] - math.cos(angle + 0.4) * hs), int(tip[1] - math.sin(angle + 0.4) * hs)),
        ])

        # fletching
        fl = 5
        pygame.draw.line(surf, DARK_GRAY, tail,
                         (int(tail[0] - math.cos(angle - 0.5) * fl),
                          int(tail[1] - math.sin(angle - 0.5) * fl)), 1)
        pygame.draw.line(surf, DARK_GRAY, tail,
                         (int(tail[0] - math.cos(angle + 0.5) * fl),
                          int(tail[1] - math.sin(angle + 0.5) * fl)), 1)

        # special FX
        if self.arrow_type == "fire" and not self.stuck:
            for _ in range(2):
                px = self.pos.x + random.uniform(-5, 5)
                py = self.pos.y + random.uniform(-5, 5)
                pygame.draw.circle(surf, YELLOW, (int(px), int(py)), random.randint(1, 3))
        elif self.arrow_type == "explosive" and not self.stuck:
            pygame.draw.circle(surf, RED, (int(self.pos.x), int(self.pos.y)), 4, 1)


# ---------------------------------------------------------------------------
# AI controller
# ---------------------------------------------------------------------------
class AIController:
    def __init__(self, ragdoll):
        self.ragdoll = ragdoll
        self.timer = 0
        self.cooldown = random.randint(90, 180)
        self.aim_angle = 0.0
        self.aim_power = 12.0
        self.arrow_type = "normal"

    def update(self, target, arrows, platforms):
        if not self.ragdoll.active or target is None or not target.active:
            return
        dx = target.centre().x - self.ragdoll.r_hand.pos.x
        dy = target.centre().y - self.ragdoll.r_hand.pos.y
        dist = math.hypot(dx, dy)
        self.aim_angle = math.atan2(dy, dx) - 0.05 + random.uniform(-0.15, 0.15)
        self.aim_power = min(18, max(8, dist * 0.04))

        self.timer += 1
        if self.timer >= self.cooldown:
            self.timer = 0
            self.cooldown = random.randint(100, 200)
            vx = math.cos(self.aim_angle) * self.aim_power
            vy = math.sin(self.aim_angle) * self.aim_power
            arrows.append(Arrow(self.ragdoll.r_hand.pos.x,
                                self.ragdoll.r_hand.pos.y,
                                vx, vy, self.arrow_type, self.ragdoll))


# ---------------------------------------------------------------------------
# Particle & floating damage number
# ---------------------------------------------------------------------------
class Particle:
    def __init__(self, x, y, vx, vy, color, life=30, size=3):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.color = color
        self.life = self.max_life = life
        self.size = size

    def update(self):
        self.x += self.vx; self.y += self.vy; self.vy += 0.1; self.life -= 1

    def draw(self, surf):
        r = max(1, int(self.size * self.life / self.max_life))
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), r)


class DamageNumber:
    def __init__(self, x, y, dmg, color=RED):
        self.x, self.y, self.dmg, self.color = x, y, int(dmg), color
        self.life = 40; self.vy = -1.5

    def update(self):
        self.y += self.vy; self.vy += 0.02; self.life -= 1

    def draw(self, surf, font):
        if self.life > 0:
            t = font.render(str(self.dmg), True, self.color)
            surf.blit(t, (int(self.x) - t.get_width() // 2, int(self.y)))


# ---------------------------------------------------------------------------
# Main game
# ---------------------------------------------------------------------------
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Ragdoll Archers")
        self.clock = pygame.time.Clock()
        self.font     = pygame.font.SysFont("Arial", 20, bold=True)
        self.big_font = pygame.font.SysFont("Arial", 40, bold=True)
        self.sm_font  = pygame.font.SysFont("Arial", 14)

        self.state = "menu"
        self.wave = 1
        self.xp = 0
        self.total_kills = 0
        self.unlocked_arrows = ["normal"]
        self.sel_arrow = 0

        self.platforms = self._make_platforms()
        # Player starts on the left platform
        player_plat = self.platforms[0]
        px = player_plat[0] + player_plat[2] // 2
        py = player_plat[1] - 35
        self.player = Ragdoll(px, py, BLUE, facing=1)
        self.enemies = []
        self.ais = []
        self._spawn_wave()

        self.arrows = []
        self.particles = []
        self.dmg_nums = []

        self.aiming = False
        self.aim_start = None
        self.aim_cur = None
        self.shoot_cd = 0

    # -- level generation --
    def _make_platforms(self):
        # Player platform always on the left
        player_plat = (80, GROUND_Y - 80, 120, 15)
        platforms = [player_plat]

        # Generate random enemy platforms at least 360px (3 blocks) from player
        player_cx = player_plat[0] + player_plat[2] // 2
        n_enemies = min(1 + self.wave // 2, 5)
        min_dist = 360  # ~3 platform widths

        for _ in range(n_enemies):
            for _try in range(50):
                ex = random.randint(int(player_cx + min_dist), WIDTH - 140)
                ey = random.randint(GROUND_Y - 180, GROUND_Y - 50)
                # Check no overlap with existing platforms
                overlap = False
                for (px, py, pw, ph) in platforms:
                    if abs(ex - px) < 160 and abs(ey - py) < 50:
                        overlap = True
                        break
                if not overlap:
                    platforms.append((ex, ey, 120, 15))
                    break

        return platforms

    def _spawn_wave(self):
        self.enemies.clear()
        self.ais.clear()
        n = min(1 + self.wave // 2, 5)
        # Each enemy spawns on its own platform (platforms[1], [2], ...)
        for i in range(n):
            if i + 1 < len(self.platforms):
                plat = self.platforms[i + 1]  # skip index 0 (player)
                x = plat[0] + plat[2] // 2
                y = plat[1] - 35
            else:
                # Overflow enemies go on ground, still 3+ platforms away
                x = random.randint(int(self.platforms[0][0] + 360), WIDTH - 60)
                y = GROUND_Y - 35

            e = Ragdoll(x, y, RED, facing=-1)
            e.max_health = 80 + self.wave * 10
            e.health = e.max_health

            ai = AIController(e)
            pool = ["normal"]
            if self.wave >= 3: pool.append("fire")
            if self.wave >= 5: pool.append("ice")
            if self.wave >= 6: pool.append("triple")
            if self.wave >= 7: pool.append("explosive")
            ai.arrow_type = random.choice(pool)

            self.enemies.append(e)
            self.ais.append(ai)

    def _check_unlocks(self):
        for name, props in ARROW_TYPES.items():
            if name not in self.unlocked_arrows and self.xp >= props["xp_needed"]:
                self.unlocked_arrows.append(name)

    # -- effects --
    def _hit_particles(self, x, y, color, count=8):
        for _ in range(count):
            self.particles.append(
                Particle(x, y, random.uniform(-3, 3), random.uniform(-4, 1),
                         color, random.randint(15, 30)))

    def _explosion(self, x, y):
        for _ in range(20):
            a = random.uniform(0, math.tau)
            s = random.uniform(2, 8)
            self.particles.append(
                Particle(x, y, math.cos(a) * s, math.sin(a) * s,
                         random.choice([RED, ORANGE, YELLOW]),
                         random.randint(20, 40), random.randint(2, 5)))

    # -- input --
    def handle_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False

            if self.state == "menu":
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE:
                    self.state = "playing"

            elif self.state == "playing":
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    if self.player.active and self.shoot_cd <= 0:
                        self.aiming = True
                        self.aim_start = self.aim_cur = pygame.mouse.get_pos()
                elif ev.type == pygame.MOUSEMOTION and self.aiming:
                    self.aim_cur = pygame.mouse.get_pos()
                elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1 and self.aiming:
                    self._shoot()
                    self.aiming = False

                if ev.type == pygame.MOUSEWHEEL:
                    self.sel_arrow = (self.sel_arrow + ev.y) % len(self.unlocked_arrows)
                if ev.type == pygame.KEYDOWN:
                    for i in range(5):
                        if ev.key == pygame.K_1 + i and i < len(self.unlocked_arrows):
                            self.sel_arrow = i
                    if ev.key == pygame.K_r:
                        self.__init__()
                        self.state = "playing"

            elif self.state == "wave_clear":
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE:
                    self.wave += 1
                    self.platforms = self._make_platforms()
                    self._spawn_wave()
                    old_hp = self.player.health
                    player_plat = self.platforms[0]
                    ppx = player_plat[0] + player_plat[2] // 2
                    ppy = player_plat[1] - 35
                    self.player = Ragdoll(ppx, ppy, BLUE, facing=1)
                    # Every 10 waves: full heal; otherwise +30
                    if self.wave % 10 == 1:  # just completed wave 10,20,30...
                        self.player.health = self.player.max_health
                    else:
                        self.player.health = min(self.player.max_health, old_hp + 30)
                    self.arrows.clear(); self.particles.clear()
                    self.state = "playing"

            elif self.state == "game_over":
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE:
                    self.__init__()
                    self.state = "playing"

        return True

    def _shoot(self):
        if not self.aim_start or not self.aim_cur:
            return
        dx = self.aim_start[0] - self.aim_cur[0]
        dy = self.aim_start[1] - self.aim_cur[1]
        power = min(math.hypot(dx, dy) * 0.12, 20)
        if power < 1:
            return
        angle = math.atan2(dy, dx)
        atype = self.unlocked_arrows[self.sel_arrow]
        hx, hy = self.player.r_hand.pos.x, self.player.r_hand.pos.y

        if atype == "triple":
            for spread in (-0.15, 0, 0.15):
                a = angle + spread
                self.arrows.append(Arrow(hx, hy,
                                         math.cos(a) * power, math.sin(a) * power,
                                         atype, self.player))
        else:
            sp = ARROW_TYPES[atype]["speed"]
            self.arrows.append(Arrow(hx, hy,
                                     math.cos(angle) * power * sp,
                                     math.sin(angle) * power * sp,
                                     atype, self.player))
        self.shoot_cd = 15

    # -- update --
    def update(self):
        if self.state != "playing":
            return
        if self.shoot_cd > 0:
            self.shoot_cd -= 1

        # movement
        keys = pygame.key.get_pressed()
        if self.player.active:
            spd = 2
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.player.apply_force(-spd, 0); self.player.stand_x -= spd
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.player.apply_force(spd, 0);  self.player.stand_x += spd

        self.player.update(self.platforms)
        for e in self.enemies:
            e.update(self.platforms)
        for ai in self.ais:
            ai.update(self.player, self.arrows, self.platforms)

        # arrows
        for ar in self.arrows:
            ar.update()
            ar.check_platform(self.platforms)

            # hit player
            if ar.owner is not self.player and self.player.active:
                hit, part = ar.check_hit(self.player)
                if hit:
                    dmg = self.player.take_damage(ar.damage, part, ar.vel)
                    self._hit_particles(ar.pos.x, ar.pos.y, RED)
                    self.dmg_nums.append(DamageNumber(ar.pos.x, ar.pos.y, dmg))
                    if ar.arrow_type == "explosive":
                        self._explosion(ar.pos.x, ar.pos.y)

            # hit enemies
            for e in self.enemies:
                if ar.owner is self.player and e.active:
                    hit, part = ar.check_hit(e)
                    if hit:
                        dmg = e.take_damage(ar.damage, part, ar.vel)
                        self._hit_particles(ar.pos.x, ar.pos.y, ORANGE)
                        self.dmg_nums.append(DamageNumber(ar.pos.x, ar.pos.y, dmg, YELLOW))
                        if ar.arrow_type == "explosive":
                            self._explosion(ar.pos.x, ar.pos.y)
                        if not e.active:
                            self.xp += 25 + self.wave * 5
                            self.total_kills += 1
                            self._check_unlocks()

        self.arrows = [a for a in self.arrows if a.active]

        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]
        for d in self.dmg_nums:
            d.update()
        self.dmg_nums = [d for d in self.dmg_nums if d.life > 0]

        if all(not e.active for e in self.enemies):
            self.state = "wave_clear"
        if not self.player.active:
            self.state = "game_over"

    # -- drawing --
    def draw(self):
        self.screen.fill(SKY_BLUE)

        # hills
        for i in range(3):
            yo = 450 + i * 30
            col = tuple(max(0, c - i * 20) for c in DARK_GREEN)
            pts = [(0, HEIGHT)]
            for x in range(0, WIDTH + 20, 20):
                pts.append((x, yo + math.sin(x * 0.01 + i) * 20 + math.sin(x * 0.005 + i * 2) * 30))
            pts.append((WIDTH, HEIGHT))
            pygame.draw.polygon(self.screen, col, pts)

        pygame.draw.rect(self.screen, DARK_GREEN, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
        pygame.draw.line(self.screen, BROWN, (0, GROUND_Y), (WIDTH, GROUND_Y), 3)

        for pl in self.platforms:
            px, py, pw, ph = pl
            pygame.draw.rect(self.screen, BROWN, pl)
            pygame.draw.rect(self.screen, DARK_GREEN, (px, py, pw, 4))
            pygame.draw.rect(self.screen, BLACK, pl, 1)

        for ar in self.arrows:
            ar.draw(self.screen)
        for p in self.particles:
            p.draw(self.screen)

        # Compute player aim angle for bow drawing
        p_aim = None
        p_aiming = False
        if self.aiming and self.aim_start and self.aim_cur:
            dx = self.aim_start[0] - self.aim_cur[0]
            dy = self.aim_start[1] - self.aim_cur[1]
            if math.hypot(dx, dy) > 2:
                p_aim = math.atan2(dy, dx)
                p_aiming = True

        self.player.draw(self.screen, aim_angle=p_aim, is_aiming=p_aiming)
        for e in self.enemies:
            e.draw(self.screen)
        for d in self.dmg_nums:
            d.draw(self.screen, self.font)

        if self.aiming and self.aim_start and self.aim_cur:
            self._draw_aim()
        self._draw_hud()

        if self.state == "menu":
            self._overlay("RAGDOLL ARCHERS",
                          "Click and drag to aim  |  Defeat endless waves!",
                          "Press SPACE to start", YELLOW)
        elif self.state == "wave_clear":
            nxt = None
            for n, pr in ARROW_TYPES.items():
                if n not in self.unlocked_arrows:
                    if nxt is None or pr["xp_needed"] < ARROW_TYPES[nxt]["xp_needed"]:
                        nxt = n
            sub2 = f"Next unlock: {nxt.capitalize()} arrow at {ARROW_TYPES[nxt]['xp_needed']} XP" if nxt else "All arrows unlocked!"
            self._overlay(f"Wave {self.wave} Clear!",
                          f"XP: {self.xp}   —   {sub2}",
                          "Press SPACE for next wave", GREEN)
        elif self.state == "game_over":
            self._overlay("GAME OVER",
                          f"Waves: {self.wave}  |  Kills: {self.total_kills}  |  XP: {self.xp}",
                          "Press SPACE to restart", RED)

        pygame.display.flip()

    def _draw_aim(self):
        dx = self.aim_start[0] - self.aim_cur[0]
        dy = self.aim_start[1] - self.aim_cur[1]
        power = min(math.hypot(dx, dy) * 0.12, 20)
        angle = math.atan2(dy, dx)
        hx, hy = self.player.r_hand.pos.x, self.player.r_hand.pos.y
        # Straight line trajectory
        end_x = hx + math.cos(angle) * power * 25
        end_y = hy + math.sin(angle) * power * 25
        # Draw dashed line
        steps = 30
        for i in range(steps):
            t = i / steps
            sx = hx + (end_x - hx) * t
            sy = hy + (end_y - hy) * t
            if i % 2 == 0:
                pygame.draw.circle(self.screen, WHITE, (int(sx), int(sy)), 2)

        pct = power / 20
        bx, by, bw, bh = 20, HEIGHT - 40, 150, 12
        pygame.draw.rect(self.screen, DARK_GRAY, (bx, by, bw, bh))
        col = GREEN if pct < 0.5 else YELLOW if pct < 0.8 else RED
        pygame.draw.rect(self.screen, col, (bx, by, int(bw * pct), bh))
        pygame.draw.rect(self.screen, WHITE, (bx, by, bw, bh), 1)
        self.screen.blit(self.sm_font.render(f"Power: {int(pct*100)}%", True, WHITE),
                         (bx + bw + 10, by - 2))

    def _draw_hud(self):
        wt = self.font.render(f"Wave {self.wave}", True, WHITE)
        self.screen.blit(wt, (WIDTH // 2 - wt.get_width() // 2, 10))
        kt = self.sm_font.render(f"Kills: {self.total_kills}", True, WHITE)
        self.screen.blit(kt, (WIDTH // 2 - kt.get_width() // 2, 35))
        self.screen.blit(self.sm_font.render(f"XP: {self.xp}", True, YELLOW), (10, 10))

        for i, at in enumerate(self.unlocked_arrows):
            sel = i == self.sel_arrow
            col = ARROW_TYPES[at]["color"] if sel else GRAY
            pre = "> " if sel else "  "
            self.screen.blit(self.sm_font.render(f"{pre}[{i+1}] {at.capitalize()}", True, col),
                             (10, 60 + i * 20))

        if self.player.active:
            bx, by, bw, bh = 10, HEIGHT - 60, 200, 15
            fill = max(0, self.player.health / self.player.max_health)
            pygame.draw.rect(self.screen, DARK_GRAY, (bx, by, bw, bh))
            col = GREEN if fill > 0.5 else YELLOW if fill > 0.25 else RED
            pygame.draw.rect(self.screen, col, (bx, by, int(bw * fill), bh))
            pygame.draw.rect(self.screen, WHITE, (bx, by, bw, bh), 1)
            self.screen.blit(self.sm_font.render(
                f"HP: {int(self.player.health)}/{self.player.max_health}", True, WHITE),
                (bx + 5, by))

        ct = self.sm_font.render(
            "A/D: Move | Click+Drag: Aim | Scroll/1-5: Arrow Type | R: Restart", True, (200, 200, 200))
        self.screen.blit(ct, (WIDTH // 2 - ct.get_width() // 2, HEIGHT - 20))

    def _overlay(self, title, subtitle, action, title_color):
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 140))
        self.screen.blit(ov, (0, 0))
        t = self.big_font.render(title, True, title_color)
        self.screen.blit(t, (WIDTH // 2 - t.get_width() // 2, 230))
        s = self.sm_font.render(subtitle, True, (200, 200, 200))
        self.screen.blit(s, (WIDTH // 2 - s.get_width() // 2, 290))
        a = self.font.render(action, True, WHITE)
        self.screen.blit(a, (WIDTH // 2 - a.get_width() // 2, 340))

    # -- main loop --
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
