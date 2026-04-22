# ═══════════════════════════════════════════════════════════════════════════
#  HORROR SURVIVAL — Forsaken-style Round-Based Horror Game
#  Run: python cool_game.py/ragdoll/forsaken_game.py
#  Requires: pip install ursina
# ═══════════════════════════════════════════════════════════════════════════
from ursina import *
from ursina import curve
import math, random, json, os, time as _time

def _rgb(r, g, b):
    return Color(r/255, g/255, b/255, 1)
def _rgba(r, g, b, a):
    return Color(r/255, g/255, b/255, a/255)

# ═══════════════════════════════════════════════════════════════════════════
#  CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════
TITLE = "Horror Survival"
WIN_SIZE = (1280, 720)
ROOM = 8
WALL_H = 5
PLAYER_SPEED = 5.0
SPRINT_SPEED = 8.5
CROUCH_SPEED = 2.5
P_HEIGHT = 1.8
CROUCH_H = 1.0
MAX_STAMINA = 100
STAM_DRAIN = 20
STAM_REGEN = 14
FLASH_MAX = 100
FLASH_DRAIN = 3.0
ROUND_TIME = 120          # seconds per round
COINS_ESCAPE = 150
COINS_SURVIVE = 80
COINS_KILL = 50
SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "forsaken_save.json")

# ── MAP ── Open town with buildings, NO maze walls inside ─────────────────
MAP = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,2,2,2,0,0,0,0,2,2,0,0,0,0,0,0,0,2,2,2,0,0,0,0,0,2,2,0,0,0,0,0,1],
    [1,0,0,2,2,2,0,0,0,0,2,2,0,0,0,0,0,0,0,2,2,2,0,0,0,0,0,2,2,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,2,2,2,0,0,0,0,0,2,2,0,0,0,0,0,0,2,2,2,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,2,2,2,0,0,0,0,0,2,2,0,0,0,0,0,0,2,2,2,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,2,2,0,0,0,0,0,0,0,0,2,2,0,0,0,0,0,2,2,0,0,0,0,0,0,0,2,2,0,0,0,1],
    [1,0,0,2,2,0,0,0,0,0,0,0,0,2,2,0,0,0,0,0,2,2,0,0,0,0,0,0,0,2,2,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,2,2,2,0,0,0,0,0,0,0,0,0,2,2,0,0,0,0,2,2,2,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,2,2,2,0,0,0,0,0,0,0,0,0,2,2,0,0,0,0,2,2,2,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,2,2,0,0,0,0,0,0,0,0,0,2,2,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,2,2,0,0,0,0,0,0,0,0,0,2,2,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

# ── KILLERS ───────────────────────────────────────────────────────────────
KILLERS = {
    "john_doe": {
        "name": "John Doe",
        "color": _rgb(15, 15, 15),
        "eye_color": _rgb(255, 0, 0),
        "speed": 5.5,
        "chase_speed": 8.0,
        "kill_range": 2.2,
        "detect_range": 18,
        "height": 2.8,
        "desc": "A faceless entity. Relentless pursuer.",
        "ability_name": "Shadow Dash",
        "ability_desc": "Teleports forward 15 blocks instantly",
        "ability_cooldown": 12,
    },
    "1x1x1x1": {
        "name": "1x1x1x1",
        "color": _rgb(0, 0, 0),
        "eye_color": _rgb(255, 255, 0),
        "speed": 6.0,
        "chase_speed": 9.0,
        "kill_range": 2.5,
        "detect_range": 999,
        "height": 2.2,
        "desc": "The hacker. Sees through walls. Always knows.",
        "ability_name": "Glitch Pulse",
        "ability_desc": "Disables all flashlights for 5 seconds",
        "ability_cooldown": 15,
    },
    "slasher": {
        "name": "The Slasher",
        "color": _rgb(60, 10, 10),
        "eye_color": _rgb(200, 0, 0),
        "speed": 4.5,
        "chase_speed": 10.0,
        "kill_range": 3.0,
        "detect_range": 14,
        "height": 2.5,
        "desc": "Slow patrol. Insane sprint. One-hit kill range.",
        "ability_name": "Frenzy",
        "ability_desc": "Double speed for 6 seconds",
        "ability_cooldown": 18,
    },
    "phantom": {
        "name": "The Phantom",
        "color": _rgba(60, 60, 80, 140),
        "eye_color": _rgb(150, 0, 255),
        "speed": 3.5,
        "chase_speed": 6.5,
        "kill_range": 2.8,
        "detect_range": 25,
        "height": 3.2,
        "desc": "Teleports near you. Semi-invisible.",
        "ability_name": "Phase Shift",
        "ability_desc": "Become invisible for 4 seconds",
        "ability_cooldown": 14,
    },
    "beast": {
        "name": "The Beast",
        "color": _rgb(40, 25, 15),
        "eye_color": _rgb(0, 255, 80),
        "speed": 7.0,
        "chase_speed": 11.0,
        "kill_range": 2.0,
        "detect_range": 10,
        "height": 1.8,
        "desc": "Crawls on all fours. Fastest killer. Short detect.",
        "ability_name": "Pounce",
        "ability_desc": "Leap forward and insta-kill at landing",
        "ability_cooldown": 10,
    },
}

# ── SURVIVORS ─────────────────────────────────────────────────────────────
SURVIVORS = {
    "runner": {
        "name": "Runner",
        "body": _rgb(80, 90, 80), "shirt": _rgb(60, 70, 60), "skin": _rgb(210, 180, 150),
        "desc": "Faster sprint speed.",
        "ability_name": "Adrenaline Rush",
        "ability_desc": "Max sprint for 4s, no stamina cost",
        "ability_cooldown": 20,
        "speed_mult": 1.25, "stamina_mult": 1.0, "flash_mult": 1.0,
    },
    "scout": {
        "name": "Scout",
        "body": _rgb(50, 70, 50), "shirt": _rgb(40, 60, 40), "skin": _rgb(200, 170, 140),
        "desc": "Can see killer direction on minimap.",
        "ability_name": "Radar Ping",
        "ability_desc": "Reveals killer location for 3 seconds",
        "ability_cooldown": 25,
        "speed_mult": 1.0, "stamina_mult": 1.0, "flash_mult": 1.0,
    },
    "engineer": {
        "name": "Engineer",
        "body": _rgb(180, 120, 40), "shirt": _rgb(150, 100, 30), "skin": _rgb(220, 190, 160),
        "desc": "Flashlight lasts longer. Better battery.",
        "ability_name": "Flashbang",
        "ability_desc": "Blinds killer for 3s if they're close",
        "ability_cooldown": 22,
        "speed_mult": 1.0, "stamina_mult": 1.0, "flash_mult": 1.8,
    },
    "medic": {
        "name": "Medic",
        "body": _rgb(200, 200, 200), "shirt": _rgb(200, 50, 50), "skin": _rgb(190, 160, 130),
        "desc": "Slower stamina drain. Self-heal.",
        "ability_name": "Heal Pulse",
        "ability_desc": "Restores stamina to full instantly",
        "ability_cooldown": 18,
        "speed_mult": 1.0, "stamina_mult": 0.6, "flash_mult": 1.0,
    },
    "shadow": {
        "name": "Shadow",
        "body": _rgb(20, 20, 30), "shirt": _rgb(15, 15, 25), "skin": _rgb(170, 140, 110),
        "desc": "Harder for killer to detect. Stealth expert.",
        "ability_name": "Vanish",
        "ability_desc": "Become invisible for 3 seconds",
        "ability_cooldown": 24,
        "speed_mult": 1.0, "stamina_mult": 1.0, "flash_mult": 1.0,
    },
    "tank": {
        "name": "Tank",
        "body": _rgb(100, 100, 110), "shirt": _rgb(80, 80, 90), "skin": _rgb(200, 175, 150),
        "desc": "Survives one hit. Slower speed.",
        "ability_name": "Shield",
        "ability_desc": "Block next kill for 5 seconds",
        "ability_cooldown": 30,
        "speed_mult": 0.85, "stamina_mult": 1.0, "flash_mult": 1.0,
    },
}

# NPC dialogue lines
NPC_LINES = [
    "I heard something down that hallway...",
    "Don't go alone. It's not safe.",
    "The exit is somewhere to the east...",
    "Keep your flashlight on. It hates the light.",
    "I saw it... those eyes... red...",
    "We need to find the exit before time runs out!",
    "Shh! Did you hear that?",
    "Stay close to the walls. Move quietly.",
    "I think someone didn't make it...",
    "The killer is somewhere in sector B.",
]

RARITY_COLORS = {
    "starter": _rgb(200,200,200), "common": _rgb(180,220,180),
    "rare": _rgb(100,170,255), "ultra_rare": _rgb(220,100,255),
}

# ═══════════════════════════════════════════════════════════════════════════
#  SAVE
# ═══════════════════════════════════════════════════════════════════════════
def load_save():
    d = {"coins":0,"escapes":0,"deaths":0,"rounds_played":0,
         "selected_survivor":"runner","username":""}
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE,"r") as f: data=json.load(f)
            for k,v in d.items(): data.setdefault(k,v)
            return data
        except: pass
    return d

def save_data(data):
    try:
        with open(SAVE_FILE,"w") as f: json.dump(data,f,indent=2)
    except: pass

# ═══════════════════════════════════════════════════════════════════════════
#  CHARACTER MODELS
# ═══════════════════════════════════════════════════════════════════════════
class HumanModel(Entity):
    def __init__(self, body_c, shirt_c, skin_c, nametag="", is_player=False, **kw):
        super().__init__(**kw)
        self.torso = Entity(parent=self, model="cube", color=shirt_c,
                            scale=(.6,.8,.35), position=(0,1.0,0))
        self.head = Entity(parent=self, model="sphere", color=skin_c,
                           scale=(.4,.45,.4), position=(0,1.65,0))
        Entity(parent=self.head, model="sphere", color=color.white,
               scale=(.15,.18,.1), position=(-.15,.02,.4))
        Entity(parent=self.head, model="sphere", color=color.black,
               scale=(.07,.09,.06), position=(-.15,.02,.48))
        Entity(parent=self.head, model="sphere", color=color.white,
               scale=(.15,.18,.1), position=(.15,.02,.4))
        Entity(parent=self.head, model="sphere", color=color.black,
               scale=(.07,.09,.06), position=(.15,.02,.48))
        self.la = Entity(parent=self, model="cube", color=shirt_c,
                         scale=(.2,.7,.2), position=(-.5,1.0,0))
        self.ra = Entity(parent=self, model="cube", color=shirt_c,
                         scale=(.2,.7,.2), position=(.5,1.0,0))
        self.ll = Entity(parent=self, model="cube", color=body_c,
                         scale=(.25,.7,.25), position=(-.18,.35,0))
        self.rl = Entity(parent=self, model="cube", color=body_c,
                         scale=(.25,.7,.25), position=(.18,.35,0))
        # feet
        Entity(parent=self.ll, model="cube", color=_rgb(40,40,40),
               scale=(1.1,.3,1.4), position=(0,-.5,.07))
        Entity(parent=self.rl, model="cube", color=_rgb(40,40,40),
               scale=(1.1,.3,1.4), position=(0,-.5,.07))
        if is_player:
            Entity(parent=self, model="cube", color=_rgb(255,255,50),
                   scale=(.12,.12,.12), position=(0,2.1,0), rotation=(45,45,0))
        if nametag:
            c = _rgb(255,255,80) if is_player else color.white
            Text(text=nametag, scale=10, billboard=True, parent=self,
                 position=(0,2.2,0), origin=(0,0), color=c)
        self._wp = 0

    def animate_walk(self, dt, spd=1.0):
        self._wp += dt * 10 * spd
        s = math.sin(self._wp) * 35
        self.la.rotation_x = s; self.ra.rotation_x = -s
        self.ll.rotation_x = -s*.8; self.rl.rotation_x = s*.8
        b = abs(math.sin(self._wp))*.04
        self.torso.y = 1.0+b; self.head.y = 1.65+b

    def animate_idle(self, dt):
        for p in (self.la,self.ra,self.ll,self.rl):
            p.rotation_x = lerp(p.rotation_x, 0, dt*5)


class KillerModel(Entity):
    def __init__(self, killer_type="john_doe", **kw):
        super().__init__(**kw)
        info = KILLERS[killer_type]
        mc, ec, h = info["color"], info["eye_color"], info["height"]
        if killer_type == "beast":
            self.body = Entity(parent=self, model="cube", color=mc,
                               scale=(.8,.4,1.5), position=(0,.3,0))
            self.head = Entity(parent=self, model="sphere", color=mc,
                               scale=(.5,.35,.5), position=(0,.4,.8))
            for side in [-1,1]:
                for z in [-.4,0,.4]:
                    Entity(parent=self.body, model="cube", color=mc,
                           scale=(.8,.12,.12), position=(side*.6,-.15,z),
                           rotation=(0,0,side*30))
        else:
            self.body = Entity(parent=self, model="cube", color=mc,
                               scale=(.7,h*.45,.5), position=(0,h*.35,0))
            self.head = Entity(parent=self, model="sphere", color=mc,
                               scale=(.5,.55,.5), position=(0,h*.7,0))
            Entity(parent=self, model="cube", color=mc, scale=(.18,h*.35,.18),
                   position=(-.5,h*.25,0))
            Entity(parent=self, model="cube", color=mc, scale=(.18,h*.35,.18),
                   position=(.5,h*.25,0))
            Entity(parent=self, model="cube", color=mc, scale=(.22,h*.3,.22),
                   position=(-.22,.3,0))
            Entity(parent=self, model="cube", color=mc, scale=(.22,h*.3,.22),
                   position=(.22,.3,0))
        # glowing eyes
        Entity(parent=self.head, model="sphere", color=ec, unlit=True,
               scale=(.15,.2,.1), position=(-.12,.05,.4))
        Entity(parent=self.head, model="sphere", color=ec, unlit=True,
               scale=(.15,.2,.1), position=(.12,.05,.4))
        self._bp = random.uniform(0,6.28)

    def animate_move(self, dt, spd=1.0):
        self._bp += dt*6*spd
        self.head.rotation_z = math.sin(self._bp*.3)*8


# ═══════════════════════════════════════════════════════════════════════════
#  NPC
# ═══════════════════════════════════════════════════════════════════════════
class NPC:
    def __init__(self, pos, name):
        self.name = name
        self.pos = Vec3(pos[0], 0, pos[2]) if len(pos)==3 else Vec3(pos[0],0,pos[1])
        shirts = [_rgb(100,80,60), _rgb(60,60,90), _rgb(80,100,80), _rgb(110,80,80)]
        skins = [_rgb(210,180,150), _rgb(180,150,120), _rgb(220,190,160)]
        self.model = HumanModel(
            body_c=_rgb(50,50,60), shirt_c=random.choice(shirts),
            skin_c=random.choice(skins), nametag=name, position=self.pos)
        self.alive = True
        self.dialogue_timer = 0
        self.current_line = ""
        self.speech_bubble = None
        self._patrol_target = None
        self._pick_target()

    def _pick_target(self):
        walkable = []
        for ri, row in enumerate(MAP):
            for ci, cell in enumerate(row):
                if cell != 1:
                    wx = ci*ROOM - len(row)*ROOM/2
                    wz = ri*ROOM - len(MAP)*ROOM/2
                    walkable.append(Vec3(wx,0,wz))
        self._patrol_target = random.choice(walkable) if walkable else Vec3(0,0,0)

    def update(self, dt, player_pos, killer_pos):
        if not self.alive: return
        # Patrol slowly
        if self._patrol_target:
            d = self._patrol_target - self.pos
            d.y = 0
            if d.length() < 2:
                self._pick_target()
            elif d.length() > 0.1:
                dn = d.normalized() * 2.0 * dt
                np = self.pos + dn
                mx = int((np.x + len(MAP[0])*ROOM/2)/ROOM)
                mz = int((np.z + len(MAP)*ROOM/2)/ROOM)
                if 0<=mz<len(MAP) and 0<=mx<len(MAP[0]) and MAP[mz][mx]!=1:
                    self.pos = np
                    self.pos.y = 0
                    ang = math.degrees(math.atan2(dn.x,dn.z))
                    self.model.rotation_y = lerp(self.model.rotation_y, ang, dt*5)
                    self.model.animate_walk(dt, 0.5)
                else:
                    self._pick_target()
        self.model.position = self.pos
        # Run from killer
        dk = distance(self.pos, killer_pos)
        if dk < 12:
            away = (self.pos - killer_pos)
            away.y = 0
            if away.length() > 0.1:
                self.pos += away.normalized() * 5 * dt
                self.model.animate_walk(dt, 1.5)
        # Die if killer too close
        if dk < 2.5:
            self.alive = False
            if self.model:
                self.model.animate_scale(0, duration=0.5)
                destroy(self.model, delay=0.6)
                self.model = None
            return "died"
        # Dialogue near player
        dp = distance(self.pos, player_pos)
        self.dialogue_timer -= dt
        if dp < 5 and self.dialogue_timer <= 0:
            self.current_line = random.choice(NPC_LINES)
            self.dialogue_timer = random.uniform(6, 12)
        if self.dialogue_timer > -2:
            pass  # speech bubble handled in HUD
        return None

    def destroy(self):
        if self.model:
            destroy(self.model)
            self.model = None


# ═══════════════════════════════════════════════════════════════════════════
#  KILLER AI
# ═══════════════════════════════════════════════════════════════════════════
class KillerAI:
    def __init__(self, killer_type, pos):
        self.type = killer_type
        self.info = KILLERS[killer_type]
        self.pos = Vec3(pos[0], 0, pos[2])
        self.model = KillerModel(killer_type=killer_type, position=self.pos)
        self.state = "patrol"
        self.speed = self.info["speed"]
        self.patrol_target = None
        self.chase_timer = 0
        self.ability_timer = 0
        self.ability_active = False
        self.ability_duration = 0
        self.stunned = False
        self.stun_timer = 0
        self.invisible = False
        self.frenzy = False
        self._pick_patrol()

    def _pick_patrol(self):
        walkable = []
        for ri, row in enumerate(MAP):
            for ci, cell in enumerate(row):
                if cell != 1:
                    wx = ci*ROOM - len(row)*ROOM/2
                    wz = ri*ROOM - len(MAP)*ROOM/2
                    walkable.append(Vec3(wx,0,wz))
        self.patrol_target = random.choice(walkable) if walkable else Vec3(0,0,0)

    def update(self, dt, player_pos, player_invisible, npc_positions):
        if not self.model: return False
        # Stun
        if self.stunned:
            self.stun_timer -= dt
            if self.stun_timer <= 0:
                self.stunned = False
            return False
        # Ability cooldown
        if self.ability_timer > 0:
            self.ability_timer -= dt
        if self.ability_duration > 0:
            self.ability_duration -= dt
            if self.ability_duration <= 0:
                self.frenzy = False
                self.invisible = False
        # Decide: use ability?
        dp = distance(self.pos, player_pos)
        if self.ability_timer <= 0 and dp < 20:
            self._use_ability(player_pos)
        # Detection
        detect = self.info["detect_range"]
        if self.type == "1x1x1x1":
            detect = 999  # always knows
        if player_invisible:
            detect *= 0.3
        # Choose target — player or nearest NPC
        target = player_pos
        target_is_player = True
        for np in npc_positions:
            nd = distance(self.pos, np)
            if nd < dp and nd < detect and random.random() < 0.3:
                target = np
                target_is_player = False
        if dp < detect and not player_invisible:
            self.state = "chase"
            self.chase_timer = 8
            target = player_pos
            target_is_player = True
        elif self.state == "chase":
            self.chase_timer -= dt
            if self.chase_timer <= 0:
                self.state = "patrol"
                self._pick_patrol()
        # Speed
        if self.state == "chase":
            spd = self.info["chase_speed"]
            if self.frenzy: spd *= 2
        else:
            spd = self.info["speed"]
            target = self.patrol_target
            if self.patrol_target and distance(self.pos, self.patrol_target) < 2:
                self._pick_patrol()
        # Move
        if target:
            d = target - self.pos
            d.y = 0
            if d.length() > 0.1:
                dn = d.normalized()
                np = self.pos + dn * spd * dt
                mx = int((np.x + len(MAP[0])*ROOM/2)/ROOM)
                mz = int((np.z + len(MAP)*ROOM/2)/ROOM)
                if 0<=mz<len(MAP) and 0<=mx<len(MAP[0]) and MAP[mz][mx]!=1:
                    self.pos = np
                    self.pos.y = 0
                ang = math.degrees(math.atan2(dn.x, dn.z))
                if self.model:
                    diff = (ang - self.model.rotation_y + 180)%360-180
                    self.model.rotation_y += diff*dt*8
        if self.model:
            self.model.position = self.pos
            self.model.animate_move(dt, spd/max(1,self.info["speed"]))
            # Visibility
            if self.invisible:
                self.model.color = _rgba(30,30,30,40)
            elif self.type == "phantom":
                self.model.color = _rgba(60,60,80,140)
        # Kill check
        if dp < self.info["kill_range"] and self.state == "chase" and target_is_player:
            return True
        return False

    def _use_ability(self, player_pos):
        self.ability_timer = self.info["ability_cooldown"]
        t = self.type
        if t == "john_doe":
            # Shadow Dash — teleport forward 15 blocks toward player
            d = player_pos - self.pos; d.y=0
            if d.length() > 0.1:
                tp = self.pos + d.normalized() * min(15, d.length()-2)
                mx = int((tp.x+len(MAP[0])*ROOM/2)/ROOM)
                mz = int((tp.z+len(MAP)*ROOM/2)/ROOM)
                if 0<=mz<len(MAP) and 0<=mx<len(MAP[0]) and MAP[mz][mx]!=1:
                    self.pos = tp; self.pos.y=0
                    if self.model: self.model.position = self.pos
        elif t == "1x1x1x1":
            self.ability_duration = 5  # glitch effect handled in game
        elif t == "slasher":
            self.frenzy = True
            self.ability_duration = 6
        elif t == "phantom":
            self.invisible = True
            self.ability_duration = 4
        elif t == "beast":
            # Pounce — leap forward
            d = player_pos - self.pos; d.y=0
            if d.length() > 0.1:
                tp = self.pos + d.normalized() * min(10, d.length())
                mx = int((tp.x+len(MAP[0])*ROOM/2)/ROOM)
                mz = int((tp.z+len(MAP)*ROOM/2)/ROOM)
                if 0<=mz<len(MAP) and 0<=mx<len(MAP[0]) and MAP[mz][mx]!=1:
                    self.pos = tp; self.pos.y=0
                    if self.model: self.model.position = self.pos

    def stun(self, duration=3):
        self.stunned = True
        self.stun_timer = duration

    def destroy(self):
        if self.model:
            destroy(self.model)
            self.model = None


# ═══════════════════════════════════════════════════════════════════════════
#  ITEM PICKUP
# ═══════════════════════════════════════════════════════════════════════════
class ItemPickup(Entity):
    def __init__(self, item_type, **kw):
        cmap = {"battery":_rgb(50,255,100),"exit_key":_rgb(255,50,50)}
        ic = cmap.get(item_type, color.white)
        super().__init__(model="cube", color=ic, scale=(.25,.25,.25), **kw)
        self.item_type = item_type
        self._bob = random.uniform(0,6.28)
        self._by = self.y
        Entity(parent=self, model="sphere", color=ic, scale=2, alpha=.12)
        labels = {"battery":"BATTERY","exit_key":"KEY"}
        Text(text=labels.get(item_type,"?"), scale=8, billboard=True,
             parent=self, position=(0,.7,0), origin=(0,0), color=ic)

    def update(self):
        self._bob += time.dt*3
        self.y = self._by + math.sin(self._bob)*.15
        self.rotation_y += time.dt*60


# ═══════════════════════════════════════════════════════════════════════════
#  PARTICLES
# ═══════════════════════════════════════════════════════════════════════════
def particles(pos, clr, n=8):
    for _ in range(n):
        p = Entity(model="sphere", color=clr, scale=random.uniform(.05,.15), position=pos)
        t = pos+Vec3(random.uniform(-1.5,1.5),random.uniform(.5,3),random.uniform(-1.5,1.5))
        p.animate_position(t, duration=.5, curve=curve.out_expo)
        p.animate_scale(0, duration=.5); destroy(p, delay=.55)


# ═══════════════════════════════════════════════════════════════════════════
#  MAIN GAME
# ═══════════════════════════════════════════════════════════════════════════
class HorrorSurvivalGame:
    def __init__(self):
        self.app = Ursina(title=TITLE, borderless=False, size=WIN_SIZE)
        window.color = _rgb(8,8,12)
        window.fps_counter.enabled = True
        self.save = load_save()
        self.state = "menu"

        # Player
        self.player_pos = Vec3(0,0,0)
        self.yaw = 0; self.pitch = 0
        self.stamina = MAX_STAMINA
        self.battery = FLASH_MAX
        self.flash_on = True
        self.sprinting = False; self.crouching = False
        self.alive = True
        self.invisible = False; self.invis_timer = 0
        self.shielded = False; self.shield_timer = 0
        self.ability_cooldown = 0
        self.game_time = 0
        self.round_timer = ROUND_TIME
        self.round_num = 0
        self.current_killer_type = None
        self.selected_survivor = "runner"

        # World
        self.walls=[]; self.floors=[]; self.ceilings=[]
        self.items=[]; self.npcs=[]; self.killer=None
        self.lights_list=[]; self.buildings=[]
        self.flashlight=None; self.exit_entity=None
        self._exit_pos=None; self._event_lines=[]
        self._scare_active=False; self._scare_timer=0
        self.glitch_timer = 0
        self._npc_speech_ents = []

        self._build_ui()
        self._show_menu()

    # ── BUILD MAP ─────────────────────────────────────────────────────────
    def _build_map(self):
        for lst in (self.walls,self.floors,self.ceilings,self.items,self.buildings,self.lights_list):
            for e in lst: destroy(e)
            lst.clear()
        for n in self.npcs: n.destroy()
        self.npcs.clear()
        if self.killer: self.killer.destroy(); self.killer=None
        if self.exit_entity: destroy(self.exit_entity); self.exit_entity=None
        for e in self._npc_speech_ents: destroy(e)
        self._npc_speech_ents.clear()

        rows, cols = len(MAP), len(MAP[0])
        ox, oz = cols*ROOM/2, rows*ROOM/2
        start_pos = None; exit_pos = None
        room_positions = []

        AmbientLight(color=Color(.12,.12,.15,1))

        for ri, row in enumerate(MAP):
            for ci, cell in enumerate(row):
                wx = ci*ROOM - ox
                wz = ri*ROOM - oz

                if cell == 1:
                    w = Entity(model="cube", color=_rgb(30,30,35),
                               scale=(ROOM, WALL_H, ROOM), position=(wx,WALL_H/2,wz))
                    self.walls.append(w)
                    if random.random() < .25:
                        st = Entity(model="cube", color=_rgba(50,15,15,random.randint(30,60)),
                                    scale=(random.uniform(1,3),random.uniform(.5,2),.05),
                                    position=(wx+random.uniform(-2,2),random.uniform(.5,3),wz+ROOM/2))
                        self.walls.append(st)
                else:
                    fc = _rgb(25,25,28) if random.random()>.15 else _rgb(30,22,22)
                    f = Entity(model="cube", color=fc, scale=(ROOM,.1,ROOM), position=(wx,0,wz))
                    self.floors.append(f)
                    c = Entity(model="cube", color=_rgb(18,18,22), scale=(ROOM,.1,ROOM),
                               position=(wx,WALL_H,wz))
                    self.ceilings.append(c)

                    if cell==3: start_pos = Vec3(wx,0,wz)
                    elif cell==4: exit_pos = Vec3(wx,0,wz)
                    elif cell==2: room_positions.append(Vec3(wx,0,wz))

                    # Debris
                    if random.random()<.12:
                        self.floors.append(Entity(model="cube", color=_rgb(35,30,25),
                            scale=(random.uniform(.2,.8),.1,random.uniform(.2,.8)),
                            position=(wx+random.uniform(-2,2),.08,wz+random.uniform(-2,2))))
                    # Lights in rooms
                    if cell==2 and random.random()<.5:
                        lc = random.choice([_rgba(255,220,150,60),_rgba(180,220,255,45),_rgba(255,130,100,40)])
                        lt = Entity(model="sphere", color=lc, unlit=True, scale=.2,
                                    position=(wx,WALL_H-.3,wz))
                        self.lights_list.append(lt)
                        Entity(model="cube",color=_rgb(60,60,60),scale=(.05,.3,.05),
                               position=(wx,WALL_H-.15,wz))

        # Buildings/towers in rooms
        for rp in room_positions:
            if random.random() < .35:
                bh = random.uniform(2,4)
                bw = random.uniform(1.5,3)
                bc = random.choice([_rgb(40,40,50),_rgb(50,40,35),_rgb(35,45,50)])
                b = Entity(model="cube", color=bc, scale=(bw,bh,bw),
                           position=(rp.x+random.uniform(-2,2), bh/2, rp.z+random.uniform(-2,2)))
                self.buildings.append(b)
                # Window
                Entity(parent=b, model="cube", color=_rgba(100,150,200,40),
                       scale=(.3,.25,.02), position=(0,.2,.51))
            if random.random() < .15:
                # Tower
                th = random.uniform(3.5, WALL_H-.5)
                tw = random.uniform(.8,1.5)
                t = Entity(model="cube", color=_rgb(45,45,55), scale=(tw,th,tw),
                           position=(rp.x+random.uniform(-1,1), th/2, rp.z+random.uniform(-1,1)))
                self.buildings.append(t)
                # Antenna on top
                Entity(parent=t, model="cube", color=_rgb(80,80,80),
                       scale=(.1,1,.1), position=(0,.55,0))

        self.player_pos = (start_pos or Vec3(0,0,0)) + Vec3(0,P_HEIGHT/2,0)

        # Exit
        if exit_pos:
            self.exit_entity = Entity(model="cube", color=_rgb(90,10,10),
                                       scale=(ROOM*.8, WALL_H, .5),
                                       position=exit_pos+Vec3(0,WALL_H/2,0))
            Text(text="EXIT", scale=15, billboard=True, color=_rgb(255,50,50),
                 position=exit_pos+Vec3(0,WALL_H-.5,0), parent=self.exit_entity)
        self._exit_pos = exit_pos

        # Batteries
        all_floor = room_positions[:]
        random.shuffle(all_floor)
        for i in range(min(8, len(all_floor))):
            it = ItemPickup("battery", position=all_floor[i]+Vec3(random.uniform(-2,2),.8,random.uniform(-2,2)))
            self.items.append(it)

        # NPCs (4 friendly survivors)
        npc_names = ["Alex","Sam","Jordan","Morgan","Riley","Casey"]
        random.shuffle(all_floor); random.shuffle(npc_names)
        for i in range(min(4, len(all_floor))):
            n = NPC((all_floor[i].x, 0, all_floor[i].z), npc_names[i%len(npc_names)])
            self.npcs.append(n)

        # Killer — random from pool
        ktype = self.current_killer_type or random.choice(list(KILLERS.keys()))
        self.current_killer_type = ktype
        kspawn = random.choice(room_positions) if room_positions else Vec3(40,0,40)
        self.killer = KillerAI(ktype, (kspawn.x, 0, kspawn.z))

        # Flashlight
        if self.flashlight: destroy(self.flashlight)
        self.flashlight = SpotLight(parent=camera, position=(0,0,0), rotation=(0,0,0),
                                     color=_rgba(255,240,200,255), outer_angle=45, shadows=False)

        scene.fog_color = _rgb(8,8,12)
        scene.fog_density = .03

    # ── UI ────────────────────────────────────────────────────────────────
    def _build_ui(self):
        self.hud = Entity(parent=camera.ui, enabled=False)

        # Stamina bar
        Entity(parent=self.hud, model="quad", color=_rgba(40,40,40,180),
               scale=(.22,.018), position=(-.62,-.42))
        self.stam_bar = Entity(parent=self.hud, model="quad", color=_rgb(50,200,255),
                                scale=(.22,.016), position=(-.62,-.42), origin=(-.5,0))
        Text(parent=self.hud, text="STAMINA", scale=.55, position=(-.74,-.405), color=_rgb(130,130,130))

        # Battery bar
        Entity(parent=self.hud, model="quad", color=_rgba(40,40,40,180),
               scale=(.22,.018), position=(-.62,-.455))
        self.bat_bar = Entity(parent=self.hud, model="quad", color=_rgb(50,255,100),
                               scale=(.22,.016), position=(-.62,-.455), origin=(-.5,0))
        Text(parent=self.hud, text="BATTERY", scale=.55, position=(-.74,-.44), color=_rgb(130,130,130))

        # Keys / round info
        self.round_label = Text(parent=self.hud, text="Round 1", scale=1.3,
                                 position=(0,.47), color=_rgb(255,80,80), origin=(0,0))
        self.killer_label = Text(parent=self.hud, text="", scale=.85,
                                  position=(0,.43), color=_rgb(255,200,200), origin=(0,0))
        self.timer_txt = Text(parent=self.hud, text="2:00", scale=1.0,
                               position=(.65,.47), color=_rgb(200,200,200), origin=(0,0))
        self.alive_txt = Text(parent=self.hud, text="Alive: 5", scale=.8,
                               position=(-.65,.47), color=_rgb(200,200,200), origin=(0,0))
        self.coin_txt = Text(parent=self.hud, text="Coins: 0", scale=.75,
                              position=(.6,.43), color=_rgb(255,215,0), origin=(0,0))

        # Interact
        self.interact_txt = Text(parent=self.hud, text="", scale=1.0,
                                  position=(0,-.3), color=_rgb(255,255,200), origin=(0,0))
        # Danger
        self.danger_txt = Text(parent=self.hud, text="", scale=1.5,
                                position=(0,.32), color=_rgb(255,0,0), origin=(0,0))
        # Crosshair
        Text(parent=self.hud, text="+", scale=1.8, position=(0,0),
             color=_rgba(200,200,200,100), origin=(0,0))
        # Flash indicator
        self.flash_txt = Text(parent=self.hud, text="[F] Light: ON", scale=.65,
                               position=(-.67,-.36), color=_rgb(255,240,200))
        self.sprint_txt = Text(parent=self.hud, text="", scale=.65,
                                position=(-.67,-.33), color=_rgb(100,200,255))
        # Controls
        Text(parent=self.hud, text="WASD/Arrows=Move | Shift=Sprint | Ctrl=Crouch | F=Light | 1=Ability | Esc=Pause",
             scale=.5, position=(0,-.48), color=_rgb(70,70,80), origin=(0,0))
        # Event log
        self.event_log = Text(parent=self.hud, text="", position=(.72,.1),
                               scale=.6, color=_rgb(200,200,200), origin=(1,0))

        # ── ABILITY SIDEBAR ──
        self.ability_bg = Entity(parent=self.hud, model="quad", color=_rgba(20,20,25,200),
                                  scale=(.18,.06), position=(-.65,-.25))
        self.ability_icon = Entity(parent=self.hud, model="quad", color=_rgb(100,200,255),
                                    scale=(.025,.025), position=(-.72,-.25))
        self.ability_name_txt = Text(parent=self.hud, text="[1] Ability", scale=.7,
                                      position=(-.70,-.24), color=_rgb(200,200,200))
        self.ability_cd_txt = Text(parent=self.hud, text="READY", scale=.6,
                                    position=(-.70,-.265), color=_rgb(100,255,100))
        # Ability cooldown overlay
        self.ability_cd_bar = Entity(parent=self.hud, model="quad", color=_rgba(0,0,0,150),
                                      scale=(.18,.06), position=(-.65,-.25), origin=(-.5,0))

        # NPC speech
        self.npc_speech = Text(parent=self.hud, text="", scale=.8,
                                position=(0,-.18), color=_rgb(255,255,200), origin=(0,0))

        # ── Vignette ──
        self.vignette = Entity(parent=camera.ui, model="quad", color=_rgba(0,0,0,50),
                                scale=(2,2), enabled=False)

        # ── Announce ──
        self.announce = Text(text="", scale=3, position=(0,.15), color=color.white,
                              origin=(0,0), enabled=False)
        self.sub_announce = Text(text="", scale=1.5, position=(0,.05), color=_rgb(200,200,200),
                                  origin=(0,0), enabled=False)

        # ── Round intro ──
        self.intro_root = Entity(parent=camera.ui, enabled=False)
        Entity(parent=self.intro_root, model="quad", color=_rgba(5,5,8,240), scale=(2,2))
        self.intro_title = Text(parent=self.intro_root, text="", scale=4,
                                 position=(0,.2), origin=(0,0), color=_rgb(255,0,0))
        self.intro_killer = Text(parent=self.intro_root, text="", scale=2,
                                  position=(0,.05), origin=(0,0), color=_rgb(255,200,200))
        self.intro_desc = Text(parent=self.intro_root, text="", scale=1,
                                position=(0,-.08), origin=(0,0), color=_rgb(180,180,180))
        self.intro_ability = Text(parent=self.intro_root, text="", scale=.9,
                                   position=(0,-.16), origin=(0,0), color=_rgb(100,200,255))

        # ── Jump scare ──
        self.scare_overlay = Entity(parent=camera.ui, model="quad", color=_rgba(0,0,0,0),
                                     scale=(2,2), enabled=False)
        self.scare_face = Entity(parent=camera.ui, model="quad", color=_rgb(255,0,0),
                                  scale=(.01,.01), enabled=False)

        # ── Death ──
        self.death_root = Entity(parent=camera.ui, enabled=False)
        Entity(parent=self.death_root, model="quad", color=_rgba(80,0,0,200), scale=(2,2))
        self.death_title = Text(parent=self.death_root, text="YOU DIED", scale=5,
                                 position=(0,.15), origin=(0,0), color=_rgb(255,0,0))
        self.death_msg = Text(parent=self.death_root, text="", scale=1.2,
                               position=(0,0), origin=(0,0), color=_rgb(200,150,150))
        self.death_stats = Text(parent=self.death_root, text="", scale=.9,
                                 position=(0,-.1), origin=(0,0), color=_rgb(180,180,180))
        Button(parent=self.death_root, text="NEXT ROUND", scale=(.25,.06),
               position=(0,-.22), color=_rgb(120,30,30), highlight_color=_rgb(160,50,50),
               on_click=self._next_round)
        Button(parent=self.death_root, text="MENU", scale=(.25,.06),
               position=(0,-.31), color=_rgb(60,60,80), highlight_color=_rgb(80,80,110),
               on_click=self._show_menu)

        # ── Survived ──
        self.win_root = Entity(parent=camera.ui, enabled=False)
        Entity(parent=self.win_root, model="quad", color=_rgba(0,40,0,200), scale=(2,2))
        self.win_title = Text(parent=self.win_root, text="YOU SURVIVED!", scale=4,
                               position=(0,.2), origin=(0,0), color=_rgb(50,255,50))
        self.win_stats = Text(parent=self.win_root, text="", scale=1,
                               position=(0,0), origin=(0,0), color=_rgb(200,200,200))
        self.win_coins = Text(parent=self.win_root, text="", scale=1.2,
                               position=(0,-.1), origin=(0,0), color=_rgb(255,215,0))
        Button(parent=self.win_root, text="NEXT ROUND", scale=(.25,.06),
               position=(0,-.22), color=_rgb(30,100,30), highlight_color=_rgb(50,140,50),
               on_click=self._next_round)
        Button(parent=self.win_root, text="MENU", scale=(.25,.06),
               position=(0,-.31), color=_rgb(60,60,80), highlight_color=_rgb(80,80,110),
               on_click=self._show_menu)

        # ── Pause ──
        self.pause_root = Entity(parent=camera.ui, enabled=False)
        Entity(parent=self.pause_root, model="quad", color=_rgba(0,0,0,180), scale=(2,2))
        Text(parent=self.pause_root, text="PAUSED", scale=3, position=(0,.15), origin=(0,0),
             color=_rgb(200,200,200))
        Button(parent=self.pause_root, text="RESUME", scale=(.25,.06), position=(0,.02),
               color=_rgb(50,80,50), highlight_color=_rgb(70,110,70), on_click=self._resume)
        Button(parent=self.pause_root, text="QUIT", scale=(.25,.06), position=(0,-.08),
               color=_rgb(80,40,40), highlight_color=_rgb(110,60,60), on_click=self._show_menu)

        # ── Menu ──
        self.menu_root = Entity(parent=camera.ui, enabled=False)
        Entity(parent=self.menu_root, model="quad", color=_rgba(5,5,8,255), scale=(2,2))
        Text(parent=self.menu_root, text="HORROR", scale=5, position=(0,.35), origin=(0,0),
             color=_rgb(180,0,0))
        Text(parent=self.menu_root, text="SURVIVAL", scale=3, position=(0,.24), origin=(0,0),
             color=_rgb(100,0,0))
        Text(parent=self.menu_root, text="Survive the killer. Escape or die.", scale=.85,
             position=(0,.17), origin=(0,0), color=_rgb(100,80,80))

        self.menu_name = InputField(parent=self.menu_root,
            default_value=self.save.get('username','') or 'Survivor',
            limit_content_to='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-',
            max_length=16, scale=(.3,.04), position=(.07,.10), color=_rgb(30,30,35))
        Text(parent=self.menu_root, text="Codename:", scale=.75, position=(-.15,.10),
             color=_rgb(130,130,140))

        # Survivor select
        Text(parent=self.menu_root, text="Choose Survivor:", scale=.8,
             position=(0,.04), origin=(0,0), color=_rgb(180,180,200))
        self.surv_buttons = []
        keys = list(SURVIVORS.keys())
        for i, sk in enumerate(keys):
            s = SURVIVORS[sk]
            x = -.5 + (i % 6) * .2
            y = -.05 - (i // 6) * .08
            b = Button(parent=self.menu_root, text=s["name"], scale=(.17,.055),
                       position=(x, y), color=_rgb(40,40,55), highlight_color=_rgb(60,60,80),
                       text_size=.7)
            b.on_click = self._make_surv_select(sk)
            self.surv_buttons.append(b)
        self.surv_desc = Text(parent=self.menu_root, text="", scale=.7,
                               position=(0,-.17), origin=(0,0), color=_rgb(160,200,255))
        self.surv_ability_txt = Text(parent=self.menu_root, text="", scale=.65,
                                      position=(0,-.21), origin=(0,0), color=_rgb(150,150,180))

        Button(parent=self.menu_root, text="PLAY", scale=(.3,.07), position=(0,-.28),
               color=_rgb(120,30,30), highlight_color=_rgb(170,50,50),
               on_click=self._start_game)

        self.menu_coins = Text(parent=self.menu_root, text=f"Coins: {self.save['coins']}",
                               scale=.9, position=(0,-.38), origin=(0,0), color=_rgb(255,215,0))
        self.menu_stats = Text(parent=self.menu_root, text="", scale=.7,
                                position=(0,-.42), origin=(0,0), color=_rgb(150,150,150))
        self._update_surv_preview()

    def _make_surv_select(self, key):
        def fn():
            self.selected_survivor = key
            self.save["selected_survivor"] = key
            save_data(self.save)
            self._update_surv_preview()
        return fn

    def _update_surv_preview(self):
        s = SURVIVORS[self.selected_survivor]
        self.surv_desc.text = f"{s['name']}: {s['desc']}"
        self.surv_ability_txt.text = f"Ability [1]: {s['ability_name']} — {s['ability_desc']} (CD: {s['ability_cooldown']}s)"
        for i, sk in enumerate(SURVIVORS.keys()):
            if i < len(self.surv_buttons):
                if sk == self.selected_survivor:
                    self.surv_buttons[i].color = _rgb(60,100,60)
                else:
                    self.surv_buttons[i].color = _rgb(40,40,55)

    # ── STATE ─────────────────────────────────────────────────────────────
    def _hide_all(self):
        for u in (self.menu_root, self.hud, self.death_root, self.win_root,
                  self.pause_root, self.intro_root, self.announce, self.sub_announce,
                  self.vignette, self.scare_overlay, self.scare_face):
            u.enabled = False

    def _show_menu(self):
        self._hide_all()
        self._cleanup()
        self.state = "menu"
        self.menu_root.enabled = True
        self.menu_coins.text = f"Coins: {self.save['coins']}"
        self.menu_stats.text = f"Escapes: {self.save['escapes']}  |  Deaths: {self.save['deaths']}  |  Rounds: {self.save['rounds_played']}"
        camera.position = Vec3(0,5,-10); camera.rotation = Vec3(15,0,0)
        mouse.locked = False

    def _cleanup(self):
        for lst in (self.walls,self.floors,self.ceilings,self.items,self.buildings,self.lights_list):
            for e in lst: destroy(e)
            lst.clear()
        for n in self.npcs: n.destroy()
        self.npcs.clear()
        if self.killer: self.killer.destroy(); self.killer=None
        if self.flashlight: destroy(self.flashlight); self.flashlight=None
        if self.exit_entity: destroy(self.exit_entity); self.exit_entity=None
        for e in self._npc_speech_ents: destroy(e)
        self._npc_speech_ents.clear()
        self._event_lines.clear()
        scene.fog_density = 0

    def _start_game(self):
        self._hide_all()
        self._cleanup()
        u = 'Survivor'
        if hasattr(self,'menu_name') and self.menu_name.text.strip():
            u = self.menu_name.text.strip()
        self.save['username'] = u
        self.selected_survivor = self.save.get("selected_survivor","runner")
        save_data(self.save)
        self.round_num = 0
        self._next_round()

    def _next_round(self):
        self._hide_all()
        self._cleanup()
        self.round_num += 1
        self.save["rounds_played"] += 1
        save_data(self.save)

        # Pick random killer
        self.current_killer_type = random.choice(list(KILLERS.keys()))
        ki = KILLERS[self.current_killer_type]
        si = SURVIVORS[self.selected_survivor]

        # Reset player
        self.alive = True
        self.stamina = MAX_STAMINA
        self.battery = FLASH_MAX * si["flash_mult"]
        self.flash_on = True
        self.sprinting = False; self.crouching = False
        self.invisible = False; self.invis_timer = 0
        self.shielded = False; self.shield_timer = 0
        self.ability_cooldown = 0
        self.game_time = 0
        self.round_timer = ROUND_TIME
        self.glitch_timer = 0
        self.yaw = 0; self.pitch = 0
        self._scare_active = False

        self._build_map()

        # Show round intro — "This round's killer is..."
        self.state = "intro"
        self.intro_root.enabled = True
        self.intro_title.text = f"ROUND {self.round_num}"
        self.intro_killer.text = f"This round's killer is... {ki['name']}"
        self.intro_desc.text = ki["desc"]
        self.intro_ability.text = f"Killer Ability: {ki['ability_name']} — {ki['ability_desc']}"
        mouse.locked = False

        # Auto-continue after 4 seconds
        invoke(self._begin_round, delay=4)

    def _begin_round(self):
        if self.state != "intro": return
        self._hide_all()
        self.state = "playing"
        self.hud.enabled = True
        self.vignette.enabled = True
        mouse.locked = True

        si = SURVIVORS[self.selected_survivor]
        self.ability_name_txt.text = f"[1] {si['ability_name']}"
        self.ability_icon.color = _rgb(100,200,255)

        self._add_event(f"Round {self.round_num} — Killer: {KILLERS[self.current_killer_type]['name']}")
        self._add_event(f"Survive {ROUND_TIME}s or find the EXIT!")

    def _resume(self):
        self.pause_root.enabled = False
        self.hud.enabled = True; self.vignette.enabled = True
        self.state = "playing"; mouse.locked = True

    def _player_die(self, cause=""):
        if not self.alive: return
        self.alive = False
        self.save["deaths"] += 1
        save_data(self.save)
        # Jump scare first
        self._trigger_scare()
        invoke(self._show_death, cause, delay=1.5)

    def _show_death(self, cause=""):
        self._hide_all()
        self.state = "death"
        self.death_root.enabled = True
        ki = KILLERS.get(self.current_killer_type, {})
        self.death_msg.text = cause or f"{ki.get('name','The killer')} caught you!"
        self.death_stats.text = f"Survived: {int(self.game_time)}s  |  Round {self.round_num}"
        mouse.locked = False

    def _player_survived(self):
        self.state = "won"
        self.save["escapes"] += 1
        earned = COINS_SURVIVE
        self.save["coins"] += earned
        save_data(self.save)
        self._hide_all()
        self.win_root.enabled = True
        self.win_stats.text = f"Survived Round {self.round_num}!"
        self.win_coins.text = f"+{earned} coins"
        mouse.locked = False

    def _player_escaped(self):
        self.state = "won"
        self.save["escapes"] += 1
        earned = COINS_ESCAPE
        self.save["coins"] += earned
        save_data(self.save)
        self._hide_all()
        self.win_root.enabled = True
        self.win_stats.text = f"ESCAPED in {int(self.game_time)}s!"
        self.win_coins.text = f"+{earned} coins"
        mouse.locked = False

    # ── JUMP SCARE ────────────────────────────────────────────────────────
    def _trigger_scare(self):
        if self._scare_active: return
        self._scare_active = True; self._scare_timer = 1.5
        ki = KILLERS.get(self.current_killer_type, {})
        self.scare_overlay.enabled = True; self.scare_overlay.color = _rgba(0,0,0,200)
        self.scare_face.enabled = True
        self.scare_face.color = ki.get("eye_color", _rgb(255,0,0))
        self.scare_face.scale = (.01,.01)
        self.scare_face.animate_scale((.6,.8), duration=.15, curve=curve.out_expo)
        camera.shake(duration=.5, magnitude=3)

    def _update_scare(self, dt):
        if not self._scare_active: return
        self._scare_timer -= dt
        if self._scare_timer <= 0:
            self._scare_active = False
            self.scare_overlay.enabled = False; self.scare_face.enabled = False

    # ── PLAYER ABILITY ────────────────────────────────────────────────────
    def _use_ability(self):
        if self.ability_cooldown > 0: return
        si = SURVIVORS[self.selected_survivor]
        self.ability_cooldown = si["ability_cooldown"]
        stype = self.selected_survivor

        if stype == "runner":
            # Adrenaline: max sprint 4s free
            self.stamina = MAX_STAMINA
            self._add_event("Adrenaline Rush activated!")
        elif stype == "scout":
            # Radar: reveal killer direction
            if self.killer:
                d = self.killer.pos - self.player_pos
                dx, dz = d.x, d.z
                if abs(dx) > abs(dz):
                    dir_str = "EAST" if dx > 0 else "WEST"
                else:
                    dir_str = "NORTH" if dz > 0 else "SOUTH"
                self._add_event(f"Radar Ping: Killer is to the {dir_str}!")
        elif stype == "engineer":
            # Flashbang: stun killer if close
            if self.killer and distance(self.player_pos, self.killer.pos) < 12:
                self.killer.stun(3)
                self._add_event("Flashbang! Killer stunned for 3s!")
            else:
                self._add_event("Flashbang! (Killer too far)")
                self.ability_cooldown = 5  # short CD if missed
        elif stype == "medic":
            self.stamina = MAX_STAMINA
            self._add_event("Heal Pulse! Stamina restored!")
        elif stype == "shadow":
            self.invisible = True; self.invis_timer = 3
            self._add_event("Vanish! Invisible for 3s!")
        elif stype == "tank":
            self.shielded = True; self.shield_timer = 5
            self._add_event("Shield! Blocking next hit for 5s!")

    # ── MOVEMENT ──────────────────────────────────────────────────────────
    def _move(self, dt):
        if not self.alive: return
        si = SURVIVORS[self.selected_survivor]

        self.yaw += mouse.velocity[0]*80
        self.pitch -= mouse.velocity[1]*80
        self.pitch = max(-80, min(80, self.pitch))

        self.sprinting = (held_keys["left shift"] or held_keys["right shift"]) and self.stamina > 10
        self.crouching = held_keys["left control"] or held_keys["right control"]
        if self.crouching: self.sprinting = False

        if self.sprinting:
            spd = SPRINT_SPEED * si["speed_mult"]
            self.stamina = max(0, self.stamina - STAM_DRAIN * si["stamina_mult"] * dt)
        elif self.crouching:
            spd = CROUCH_SPEED
            self.stamina = min(MAX_STAMINA, self.stamina + STAM_REGEN*.5*dt)
        else:
            spd = PLAYER_SPEED * si["speed_mult"]
            self.stamina = min(MAX_STAMINA, self.stamina + STAM_REGEN*dt)

        yr = math.radians(self.yaw)
        fwd = Vec3(math.sin(yr),0,math.cos(yr))
        right = Vec3(math.cos(yr),0,-math.sin(yr))

        mv = Vec3(0,0,0)
        # WASD + Arrow keys
        if held_keys["w"] or held_keys["up arrow"]: mv += fwd
        if held_keys["s"] or held_keys["down arrow"]: mv -= fwd
        if held_keys["a"] or held_keys["left arrow"]: mv -= right
        if held_keys["d"] or held_keys["right arrow"]: mv += right

        if mv.length() > 0:
            mv = mv.normalized() * spd * dt
            pad = .5
            # X
            tx = self.player_pos + Vec3(mv.x,0,0)
            mix = int((tx.x + pad*(1 if mv.x>0 else -1) + len(MAP[0])*ROOM/2)/ROOM)
            miz = int((self.player_pos.z + len(MAP)*ROOM/2)/ROOM)
            if 0<=miz<len(MAP) and 0<=mix<len(MAP[0]) and MAP[miz][mix]!=1:
                self.player_pos.x += mv.x
            # Z
            tz = self.player_pos + Vec3(0,0,mv.z)
            mix2 = int((self.player_pos.x + len(MAP[0])*ROOM/2)/ROOM)
            miz2 = int((tz.z + pad*(1 if mv.z>0 else -1) + len(MAP)*ROOM/2)/ROOM)
            if 0<=miz2<len(MAP) and 0<=mix2<len(MAP[0]) and MAP[miz2][mix2]!=1:
                self.player_pos.z += mv.z

        ch = CROUCH_H if self.crouching else P_HEIGHT
        cy = lerp(camera.y, self.player_pos.y+ch, dt*12)
        camera.position = Vec3(self.player_pos.x, cy, self.player_pos.z)
        camera.rotation = Vec3(self.pitch, self.yaw, 0)

    # ── FLASHLIGHT ────────────────────────────────────────────────────────
    def _update_flash(self, dt):
        # Glitch from 1x1x1x1
        if self.glitch_timer > 0:
            self.glitch_timer -= dt
            if self.flashlight: self.flashlight.enabled = False
            self.flash_on = False
            return
        if self.flash_on:
            si = SURVIVORS[self.selected_survivor]
            self.battery = max(0, self.battery - FLASH_DRAIN/si["flash_mult"]*dt)
            if self.battery <= 0: self.flash_on = False
            if self.flashlight:
                self.flashlight.enabled = True
                if self.battery < 20:
                    self.flashlight.enabled = random.random() > .12
        else:
            if self.flashlight: self.flashlight.enabled = False

    # ── HUD ───────────────────────────────────────────────────────────────
    def _update_hud(self):
        sf = self.stamina/MAX_STAMINA
        self.stam_bar.scale_x = .22*sf
        self.stam_bar.color = _rgb(255,80,50) if sf<.3 else _rgb(255,200,50) if sf<.6 else _rgb(50,200,255)

        si = SURVIVORS[self.selected_survivor]
        bmax = FLASH_MAX * si["flash_mult"]
        bf = self.battery/bmax if bmax>0 else 0
        self.bat_bar.scale_x = .22*bf
        self.bat_bar.color = _rgb(255,50,50) if bf<.2 else _rgb(255,200,50) if bf<.5 else _rgb(50,255,100)

        self.round_label.text = f"Round {self.round_num}"
        ki = KILLERS.get(self.current_killer_type,{})
        self.killer_label.text = f"Killer: {ki.get('name','???')}"
        rt = max(0, int(self.round_timer))
        self.timer_txt.text = f"{rt//60}:{rt%60:02d}"
        self.timer_txt.color = _rgb(255,80,80) if rt<30 else _rgb(200,200,200)
        alive_npcs = sum(1 for n in self.npcs if n.alive)
        self.alive_txt.text = f"Alive: {1+alive_npcs}" if self.alive else f"Alive: {alive_npcs}"
        self.coin_txt.text = f"Coins: {self.save['coins']}"
        self.flash_txt.text = f"[F] Light: {'ON' if self.flash_on else 'OFF'}"
        self.flash_txt.color = _rgb(255,240,200) if self.flash_on else _rgb(100,100,100)
        if self.sprinting: self.sprint_txt.text="SPRINTING"; self.sprint_txt.color=_rgb(255,150,50)
        elif self.crouching: self.sprint_txt.text="CROUCHING"; self.sprint_txt.color=_rgb(100,200,100)
        else: self.sprint_txt.text=""

        # Ability sidebar
        si = SURVIVORS[self.selected_survivor]
        if self.ability_cooldown > 0:
            self.ability_cd_txt.text = f"{int(self.ability_cooldown)}s"
            self.ability_cd_txt.color = _rgb(255,100,100)
            self.ability_icon.color = _rgb(100,50,50)
            frac = self.ability_cooldown / si["ability_cooldown"]
            self.ability_cd_bar.scale_x = .18 * frac
            self.ability_cd_bar.color = _rgba(0,0,0,150)
        else:
            self.ability_cd_txt.text = "READY"
            self.ability_cd_txt.color = _rgb(100,255,100)
            self.ability_icon.color = _rgb(100,255,100)
            self.ability_cd_bar.scale_x = 0

        # Danger
        if self.killer:
            dk = distance(self.player_pos, self.killer.pos)
            if dk < 6:
                self.danger_txt.text = "!! DANGER !!"; self.danger_txt.color = _rgb(255,0,0)
                self.danger_txt.scale = 2
            elif dk < 12:
                self.danger_txt.text = "...something is near..."; self.danger_txt.color = _rgb(200,100,100)
                self.danger_txt.scale = 1.2
            else:
                self.danger_txt.text = ""
        # NPC speech
        speech = ""
        for n in self.npcs:
            if n.alive and n.dialogue_timer > 0 and distance(self.player_pos, n.pos) < 6:
                speech = f"{n.name}: \"{n.current_line}\""
                break
        self.npc_speech.text = speech

        # Vignette
        self.vignette.color = _rgba(0,0,0,60)

        # Invisible indicator
        if self.invisible:
            self.sprint_txt.text = "INVISIBLE"
            self.sprint_txt.color = _rgb(150,100,255)
        if self.shielded:
            self.sprint_txt.text = "SHIELDED"
            self.sprint_txt.color = _rgb(255,200,50)

    # ── EVENT LOG ─────────────────────────────────────────────────────────
    def _add_event(self, msg):
        self._event_lines.append(msg)
        if len(self._event_lines) > 5: self._event_lines.pop(0)
        self.event_log.text = "\n".join(self._event_lines)
        invoke(self._pop_event, delay=6)
    def _pop_event(self):
        if self._event_lines: self._event_lines.pop(0)
        self.event_log.text = "\n".join(self._event_lines)

    # ── EXIT CHECK ────────────────────────────────────────────────────────
    def _check_exit(self):
        self.interact_txt.text = ""
        if not self._exit_pos: return False
        d = distance(self.player_pos, self._exit_pos)
        if d < 5:
            self.interact_txt.text = "[E] ESCAPE THROUGH EXIT"
            return True
        return False

    # ── ITEMS ─────────────────────────────────────────────────────────────
    def _check_items(self):
        closest = None; cd = 3.0
        for it in self.items:
            d = distance(self.player_pos, it.position)
            if d < cd: cd=d; closest=it
        if closest and closest.item_type == "battery":
            self.interact_txt.text = "[E] Pick up BATTERY"
        return closest

    def _pickup(self, item):
        if item.item_type == "battery":
            si = SURVIVORS[self.selected_survivor]
            self.battery = min(FLASH_MAX*si["flash_mult"], self.battery+40)
            self._add_event("Battery +40%!")
            particles(item.position, _rgb(50,255,100))
        self.items.remove(item); destroy(item)

    # ── MAIN UPDATE ──────────────────────────────────────────────────────
    def update(self):
        dt = time.dt

        if self.state == "intro":
            # Just waiting for auto-continue
            return

        if self.state != "playing": return

        self.game_time += dt
        self.round_timer -= dt
        if self.ability_cooldown > 0: self.ability_cooldown -= dt

        # Timers
        if self.invis_timer > 0:
            self.invis_timer -= dt
            if self.invis_timer <= 0: self.invisible = False
        if self.shield_timer > 0:
            self.shield_timer -= dt
            if self.shield_timer <= 0: self.shielded = False

        self._move(dt)
        self._update_flash(dt)
        self._update_scare(dt)

        # Killer
        if self.killer and self.alive:
            npc_pos = [n.pos for n in self.npcs if n.alive]
            caught = self.killer.update(dt, self.player_pos, self.invisible, npc_pos)
            # Check 1x1x1x1 glitch ability
            if self.killer.type == "1x1x1x1" and self.killer.ability_duration > 0:
                self.glitch_timer = max(self.glitch_timer, self.killer.ability_duration)
            if caught:
                if self.shielded:
                    self.shielded = False; self.shield_timer = 0
                    self._add_event("Shield blocked the hit!")
                    # Push killer back
                    d = self.killer.pos - self.player_pos
                    if d.length() > 0.1:
                        self.killer.pos += d.normalized() * 8
                        self.killer.model.position = self.killer.pos
                    self.killer.stun(2)
                else:
                    self._player_die()
                    return

        # NPCs
        kp = self.killer.pos if self.killer else Vec3(0,0,0)
        for n in self.npcs:
            result = n.update(dt, self.player_pos, kp)
            if result == "died":
                self._add_event(f"{n.name} was killed!")

        # Exit
        self._check_exit()
        self._check_items()

        # Round timer
        if self.round_timer <= 0:
            self._player_survived()
            return

        self._update_hud()

    # ── INPUT ─────────────────────────────────────────────────────────────
    def input(self, key):
        if self.state == "playing":
            if key == "escape":
                self.state = "paused"
                self.pause_root.enabled = True
                mouse.locked = False
            if key == "f": 
                if self.battery > 0 or not self.flash_on:
                    self.flash_on = not self.flash_on
            if key == "1":
                self._use_ability()
            if key == "e":
                it = self._check_items()
                if it:
                    self._pickup(it)
                elif self._check_exit():
                    self._player_escaped()
        elif self.state == "paused":
            if key == "escape": self._resume()
        elif self.state == "intro":
            if key in ("space","e","escape"):
                self._begin_round()

    # ── RUN ───────────────────────────────────────────────────────────────
    def run(self):
        e = Entity()
        e.update = self.update
        e.input = self.input
        self.app.run()


if __name__ == "__main__":
    game = HorrorSurvivalGame()
    game.run()
