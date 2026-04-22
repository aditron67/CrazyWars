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
ROUND_TIME = 300          # 5 minutes per round
COINS_ESCAPE = 150
COINS_SURVIVE = 80
COINS_KILL = 50
GENS_NEEDED = 5           # generators to power exit
GEN_REPAIR_TIME = 4.0     # seconds to hold E on a gen
SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "forsaken_save.json")
TEX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "textures")

def _tex(name):
    """Load a texture from the textures folder if it exists."""
    p = os.path.join(TEX_DIR, f"{name}.png")
    return p if os.path.exists(p) else None

# ── MAP ── Open town: buildings (2), streets (0), walls only on edges ─────
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
    "faceless": {
        "name": "The Faceless Man",
        "color": _rgb(10, 10, 10),
        "eye_color": _rgb(255, 255, 255),
        "speed": 4.0,
        "chase_speed": 6.5,
        "kill_range": 3.0,
        "detect_range": 35,
        "height": 4.0,
        "desc": "Unnaturally tall. No face. Tentacles reach far. Watching you always.",
        "ability_name": "Tentacle Grab",
        "ability_desc": "Extends tentacles 12 blocks — grabs and pulls survivor closer",
        "ability_cooldown": 10,
        "ability2_name": "Static Field",
        "ability2_desc": "Distorts vision of all survivors for 5s, disables flashlights",
        "ability2_cooldown": 18,
        "ability3_name": "Vanish",
        "ability3_desc": "Teleport behind nearest survivor instantly",
        "ability3_cooldown": 25,
    },
    "corner": {
        "name": "Man in the Corner",
        "color": _rgb(25, 20, 20),
        "eye_color": _rgb(255, 200, 0),
        "speed": 3.0,
        "chase_speed": 12.0,
        "kill_range": 1.5,
        "detect_range": 15,
        "height": 2.5,
        "desc": "Stands perfectly still in dark corners. When you look away... it SPRINTS.",
        "ability_name": "Corner Lurk",
        "ability_desc": "Become invisible when standing still for 2s",
        "ability_cooldown": 8,
        "ability2_name": "Jumpscare Rush",
        "ability2_desc": "Insane burst sprint for 3s when breaking from stillness",
        "ability2_cooldown": 14,
    },
    "carved": {
        "name": "The Carved",
        "color": _rgb(245, 245, 245),
        "eye_color": _rgb(0, 0, 0),
        "speed": 5.5,
        "chase_speed": 8.5,
        "kill_range": 2.0,
        "detect_range": 18,
        "height": 2.5,
        "desc": "White skin. Carved smile. Never stops smiling. Never stops running.",
        "ability_name": "Frenzy",
        "ability_desc": "Triple speed for 4 seconds",
        "ability_cooldown": 16,
        "ability2_name": "Hysteria",
        "ability2_desc": "Nearest survivor's controls reverse for 3s",
        "ability2_cooldown": 22,
    },
    "masked": {
        "name": "The Masked One",
        "color": _rgb(50, 50, 55),
        "eye_color": _rgb(200, 0, 0),
        "speed": 4.5,
        "chase_speed": 9.0,
        "kill_range": 2.2,
        "detect_range": 16,
        "height": 2.8,
        "desc": "Hockey mask. Machete. Slow walk. Unstoppable force.",
        "ability_name": "Relentless",
        "ability_desc": "Cannot be stunned for 8 seconds",
        "ability_cooldown": 20,
        "ability2_name": "Machete Throw",
        "ability2_desc": "Throw machete — ranged hit at 20 blocks",
        "ability2_cooldown": 12,
    },
    "glitch": {
        "name": "The Glitch",
        "color": _rgb(0, 0, 0),
        "eye_color": _rgb(255, 255, 0),
        "speed": 6.0,
        "chase_speed": 9.5,
        "kill_range": 1.8,
        "detect_range": 999,
        "height": 2.2,
        "desc": "A hacker entity. Sees through walls. Corrupts everything it touches.",
        "ability_name": "System Crash",
        "ability_desc": "Disable all flashlights and HUD for 5s",
        "ability_cooldown": 15,
        "ability2_name": "Corrupted Teleport",
        "ability2_desc": "Teleport directly to a random survivor",
        "ability2_cooldown": 25,
    },
    "crawler": {
        "name": "The Crawler",
        "color": _rgb(40, 25, 15),
        "eye_color": _rgb(0, 255, 80),
        "speed": 7.5,
        "chase_speed": 12.0,
        "kill_range": 1.3,
        "detect_range": 10,
        "height": 1.2,
        "desc": "Scuttles on all fours. Fastest killer. Hides under objects.",
        "ability_name": "Pounce",
        "ability_desc": "Leap forward 10 blocks — insta-hit at landing",
        "ability_cooldown": 10,
        "ability2_name": "Screech",
        "ability2_desc": "Stun all survivors within 8 blocks for 2s",
        "ability2_cooldown": 18,
    },
    "phantom": {
        "name": "The Phantom",
        "color": _rgba(60, 60, 80, 140),
        "eye_color": _rgb(150, 0, 255),
        "speed": 3.5,
        "chase_speed": 7.0,
        "kill_range": 1.8,
        "detect_range": 25,
        "height": 3.2,
        "desc": "Semi-invisible. Teleports near you. You'll never hear it coming.",
        "ability_name": "Phase Shift",
        "ability_desc": "Become invisible for 4 seconds",
        "ability_cooldown": 14,
        "ability2_name": "Spirit Walk",
        "ability2_desc": "Pass through walls for 2 seconds",
        "ability2_cooldown": 22,
    },
    "mimic": {
        "name": "The Mimic",
        "color": _rgb(50, 40, 35),
        "eye_color": _rgb(200, 255, 200),
        "speed": 5.0,
        "chase_speed": 8.0,
        "kill_range": 1.8,
        "detect_range": 20,
        "height": 3.0,
        "desc": "Shapeshifts to look like a survivor. Trust no one.",
        "ability_name": "Disguise",
        "ability_desc": "Look like a random NPC survivor for 6s",
        "ability_cooldown": 16,
        "ability2_name": "Lure",
        "ability2_desc": "Create fake survivor cries to attract players",
        "ability2_cooldown": 12,
    },
    "warden": {
        "name": "The Warden",
        "color": _rgb(20, 20, 40),
        "eye_color": _rgb(255, 255, 255),
        "speed": 4.0,
        "chase_speed": 7.0,
        "kill_range": 2.5,
        "detect_range": 30,
        "height": 3.5,
        "desc": "Blind giant. Hunts by sound. Crouch to survive. Sprint to die.",
        "ability_name": "Sonic Pulse",
        "ability_desc": "Reveals all moving survivors for 4 seconds",
        "ability_cooldown": 20,
        "ability2_name": "Ground Pound",
        "ability2_desc": "Stun and knockback all survivors within 10 blocks",
        "ability2_cooldown": 25,
    },
}

# ── SURVIVORS (playable + NPC) ─────────────────────────────────────────────
SURVIVORS = {
    "builderman": {
        "name": "Rookie",
        "body": _rgb(80, 80, 80), "shirt": _rgb(90, 90, 95), "skin": _rgb(210, 185, 155),
        "hat_color": None,
        "desc": "New recruit. No special perks. Starter skin.",
        "ability_name": "Sprint Burst",
        "ability_desc": "Slight speed boost for 2 seconds",
        "ability_cooldown": 25,
        "ability2_name": "Quick Fix",
        "ability2_desc": "Repair gen 50% faster for 3s",
        "ability2_cooldown": 30,
        "speed_mult": 0.95, "stamina_mult": 1.1, "flash_mult": 0.9,
        "npc_ability": "speed_boost",
        "npc_lines": ["I'm new here...", "Which way is the exit?", "Is that... the killer?!", "Wait for me!"],
    },
    "guest1337": {
        "name": "Specter",
        # Roblox Guest: charcoal body, no face details, grey tone
        "body": _rgb(99, 95, 98), "shirt": _rgb(99, 95, 98), "skin": _rgb(245, 245, 245),
        "hat_color": None,
        "desc": "The mysterious guest. Radar vision.",
        "ability_name": "Radar Ping",
        "ability_desc": "Reveals killer direction for 3 seconds",
        "ability_cooldown": 25,
        "ability2_name": "Sixth Sense",
        "ability2_desc": "See killer outline through walls for 5s",
        "ability2_cooldown": 28,
        "speed_mult": 1.05, "stamina_mult": 1.0, "flash_mult": 1.0,
        "npc_ability": "radar",
        "npc_lines": ["I sense it nearby...", "The killer is that way!", "My instincts say run...", "Something's coming!"],
    },
    "veronica": {
        "name": "Blaze",
        # Bright pink/magenta top, purple pants, light skin
        "body": _rgb(107, 50, 124), "shirt": _rgb(218, 77, 168), "skin": _rgb(245, 220, 190),
        "hat_color": _rgb(90, 40, 50),  # dark hair
        "desc": "Fast and fierce. Speed boost ability.",
        "ability_name": "Adrenaline Rush",
        "ability_desc": "Max sprint for 4s, no stamina cost",
        "ability_cooldown": 20,
        "ability2_name": "Afterburner",
        "ability2_desc": "Leave a fire trail that stuns killer 2s",
        "ability2_cooldown": 25,
        "speed_mult": 1.25, "stamina_mult": 1.0, "flash_mult": 1.0,
        "npc_ability": "speed_boost",
        "npc_lines": ["Keep up with me!", "Run faster!", "I'll distract it, GO!", "Don't slow down!"],
    },
    "taph": {
        "name": "Bomber",
        # Brown outfit, tactical look, tan skin
        "body": _rgb(105, 64, 40), "shirt": _rgb(141, 85, 36), "skin": _rgb(215, 175, 135),
        "hat_color": _rgb(60, 40, 20),  # brown cap
        "desc": "Demolitions expert. Drops bombs.",
        "ability_name": "Bomb",
        "ability_desc": "Drop a bomb that stuns killer for 4s on contact",
        "ability_cooldown": 24,
        "ability2_name": "Decoy",
        "ability2_desc": "Place a fake survivor to distract killer",
        "ability2_cooldown": 30,
        "speed_mult": 1.0, "stamina_mult": 1.0, "flash_mult": 1.0,
        "npc_ability": "bomb",
        "npc_lines": ["FIRE IN THE HOLE!", "Bomb planted!", "Get clear!", "Boom goes the dynamite!"],
    },
    "noob": {
        "name": "Rookie",
        # Classic Roblox Noob: bright yellow head/arms, blue torso, green legs
        "body": _rgb(40, 127, 71), "shirt": _rgb(13, 105, 172), "skin": _rgb(245, 205, 48),
        "hat_color": None,
        "desc": "Classic noob. Tanky — survives one hit.",
        "ability_name": "Shield",
        "ability_desc": "Block next kill for 5 seconds",
        "ability_cooldown": 30,
        "ability2_name": "Last Stand",
        "ability2_desc": "When at 1HP, gain 3s invincibility",
        "ability2_cooldown": 40,
        "speed_mult": 0.9, "stamina_mult": 1.0, "flash_mult": 1.0,
        "npc_ability": "shield",
        "npc_lines": ["I'm not scared! ...okay maybe a little.", "What was that?!", "Is this the exit?", "Help!"],
    },
    "bacon": {
        "name": "Flicker",
        # Roblox Bacon: oof green shirt, blue jeans, bacon-brown hair
        "body": _rgb(13, 105, 172), "shirt": _rgb(88, 142, 23), "skin": _rgb(245, 205, 48),
        "hat_color": _rgb(150, 85, 40),  # bacon hair brown
        "desc": "Lucky survivor. Better flashlight battery.",
        "ability_name": "Flashbang",
        "ability_desc": "Blinds killer for 3s if they're close",
        "ability_cooldown": 22,
        "ability2_name": "Lucky Escape",
        "ability2_desc": "Teleport 10 blocks in a random safe direction",
        "ability2_cooldown": 35,
        "speed_mult": 1.0, "stamina_mult": 1.0, "flash_mult": 1.8,
        "npc_ability": "flashbang",
        "npc_lines": ["Hey, over here!", "FLASH!", "Take that!", "Did I get it?!"],
    },
    "shadow": {
        "name": "Shade",
        # All black, barely visible
        "body": _rgb(10, 10, 12), "shirt": _rgb(8, 8, 10), "skin": _rgb(25, 25, 30),
        "hat_color": _rgb(5, 5, 5),
        "desc": "Stealth master. Can turn invisible.",
        "ability_name": "Vanish",
        "ability_desc": "Become invisible for 3 seconds",
        "ability_cooldown": 24,
        "ability2_name": "Shadow Step",
        "ability2_desc": "Silent footsteps for 5 seconds",
        "ability2_cooldown": 20,
        "speed_mult": 1.0, "stamina_mult": 1.0, "flash_mult": 1.0,
        "npc_ability": "vanish",
        "npc_lines": ["...", "You can't see me.", "I was never here.", "Shh."],
    },
    "captain": {
        "name": "Medic",
        # Military blue uniform, captain hat, light skin
        "body": _rgb(20, 40, 80), "shirt": _rgb(30, 60, 130), "skin": _rgb(225, 195, 165),
        "hat_color": _rgb(20, 30, 60),  # navy cap
        "desc": "Medic veteran. Heals stamina.",
        "ability_name": "Heal Pulse",
        "ability_desc": "Restores stamina to full instantly",
        "ability_cooldown": 18,
        "ability2_name": "Triage",
        "ability2_desc": "Heal 1 HP (once per round)",
        "ability2_cooldown": 60,
        "speed_mult": 1.0, "stamina_mult": 0.6, "flash_mult": 1.0,
        "npc_ability": "heal",
        "npc_lines": ["Let me patch you up!", "Stay close, I'll heal you!", "Don't give up!", "We'll get through this!"],
    },
    "hacker": {
        "name": "Cipher",
        "body": _rgb(30, 30, 40), "shirt": _rgb(20, 80, 20), "skin": _rgb(210, 185, 155),
        "hat_color": _rgb(20, 20, 25),
        "desc": "Tech genius. Repairs gens faster.",
        "ability_name": "Overclock",
        "ability_desc": "Instantly repair nearest generator",
        "ability_cooldown": 30,
        "ability2_name": "EMP",
        "ability2_desc": "Disable killer abilities for 4s",
        "ability2_cooldown": 35,
        "speed_mult": 1.0, "stamina_mult": 1.0, "flash_mult": 1.0,
        "npc_ability": "radar",
        "npc_lines": ["Hacking the system!", "Gen's almost done!", "I can see the code...", "Firewall bypassed!"],
    },
    "athlete": {
        "name": "Dash",
        "body": _rgb(40, 40, 120), "shirt": _rgb(200, 200, 220), "skin": _rgb(160, 120, 80),
        "hat_color": None,
        "desc": "Track star. Fastest sprinter.",
        "ability_name": "Burst",
        "ability_desc": "Double speed for 3 seconds",
        "ability_cooldown": 18,
        "ability2_name": "Slide",
        "ability2_desc": "Dodge-slide through killer for 1s invincibility",
        "ability2_cooldown": 15,
        "speed_mult": 1.35, "stamina_mult": 0.8, "flash_mult": 1.0,
        "npc_ability": "speed_boost",
        "npc_lines": ["Can't catch me!", "On your marks!", "GO GO GO!", "I'm outta here!"],
    },
    "scout2": {
        "name": "Tracker",
        "body": _rgb(80, 70, 50), "shirt": _rgb(60, 80, 40), "skin": _rgb(230, 200, 170),
        "hat_color": _rgb(70, 60, 40),
        "desc": "Wilderness expert. Sees killer from far.",
        "ability_name": "Mark",
        "ability_desc": "Marks killer location for 5 seconds",
        "ability_cooldown": 22,
        "ability2_name": "Trap",
        "ability2_desc": "Place a bear trap that slows killer 3s",
        "ability2_cooldown": 28,
        "speed_mult": 1.1, "stamina_mult": 1.0, "flash_mult": 1.2,
        "npc_ability": "radar",
        "npc_lines": ["Tracks lead this way...", "I can smell it.", "Movement detected!", "Stay low."],
    },
    "tank2": {
        "name": "Breaker",
        "body": _rgb(100, 50, 50), "shirt": _rgb(80, 40, 40), "skin": _rgb(200, 170, 140),
        "hat_color": None,
        "desc": "Brawler. Extra HP and shield.",
        "ability_name": "Iron Wall",
        "ability_desc": "Block next 2 hits for 6 seconds",
        "ability_cooldown": 35,
        "ability2_name": "War Cry",
        "ability2_desc": "Knockback killer 10 blocks",
        "ability2_cooldown": 30,
        "speed_mult": 0.85, "stamina_mult": 1.0, "flash_mult": 1.0,
        "npc_ability": "shield",
        "npc_lines": ["Come at me!", "I can take it!", "Stand behind me!", "BRING IT!"],
    },
}

# Generic NPC lines (fallback)
NPC_LINES = [
    "I heard something down that hallway...",
    "Don't go alone. It's not safe.",
    "The exit is somewhere to the east...",
    "Keep your flashlight on. It hates the light.",
    "Shh! Did you hear that?",
    "Stay close to the walls. Move quietly.",
]

RARITY_COLORS = {
    "starter": _rgb(200,200,200), "common": _rgb(180,220,180),
    "rare": _rgb(100,170,255), "ultra_rare": _rgb(220,100,255),
}

# ═══════════════════════════════════════════════════════════════════════════
#  SAVE
# ═══════════════════════════════════════════════════════════════════════════
def load_save():
    d = {"coins":0,"malice":0,"escapes":0,"deaths":0,"rounds_played":0,
         "selected_survivor":"builderman","username":"",
         "unlocked_survivors":["builderman"],
         "unlocked_killers":["carved"],
         "selected_killer":"carved"}
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
    def __init__(self, body_c, shirt_c, skin_c, nametag="", is_player=False, hat_color=None, **kw):
        super().__init__(**kw)
        # ── R15-style detailed character ──
        # Torso — upper + lower with belt line
        self.torso = Entity(parent=self, model="cube", color=shirt_c,
                            scale=(.65,.5,.35), position=(0,1.15,0))
        self.lower_torso = Entity(parent=self, model="cube", color=body_c,
                                   scale=(.6,.35,.33), position=(0,.78,0))
        # Belt
        Entity(parent=self, model="cube", color=_rgb(50,40,30),
               scale=(.63,.06,.36), position=(0,.95,0))
        # Collar / neckline
        Entity(parent=self.torso, model="cube", color=skin_c,
               scale=(.4,.08,.3), position=(0,.48,0))
        # Neck
        Entity(parent=self, model="cube", color=skin_c,
               scale=(.18,.12,.18), position=(0,1.45,0))
        # Head — with face texture
        self.head = Entity(parent=self, model="cube", color=skin_c,
                           scale=(.5,.52,.48), position=(0,1.62,0))
        # Apply face texture if available
        face_tex = None
        if hat_color == _rgb(5,5,5):  # Shadow/Shade
            face_tex = _tex("survivor_dark")
        elif skin_c.r > .9:  # light skin
            face_tex = _tex("survivor_light")
        elif skin_c.r < .5:  # dark skin
            face_tex = _tex("survivor_dark")
        else:
            face_tex = _tex("survivor_default")
        if face_tex:
            # Face plane on front of head
            Entity(parent=self.head, model="quad", texture=face_tex,
                   scale=(.95,.95), position=(0,0,.501), color=color.white)
        # Hair / hat
        if hat_color:
            # Hat with brim + band
            Entity(parent=self.head, model="cube", color=hat_color,
                   scale=(1.12,.35,1.12), position=(0,.42,0))
            Entity(parent=self.head, model="cube", color=hat_color,
                   scale=(1.4,.08,1.4), position=(0,.25,0))  # brim
            # Hat band
            Entity(parent=self.head, model="cube", color=_rgb(max(0,int(hat_color.r*255)-40),
                   max(0,int(hat_color.g*255)-40), max(0,int(hat_color.b*255)-40)),
                   scale=(1.14,.06,1.14), position=(0,.35,0))
        else:
            # Default hair
            hair_c = _rgb(40, 30, 20)
            Entity(parent=self.head, model="cube", color=hair_c,
                   scale=(1.02,.25,1.02), position=(0,.38,0))
            Entity(parent=self.head, model="cube", color=hair_c,
                   scale=(1.02,.5,.15), position=(0,.1,-.48))  # back hair
            Entity(parent=self.head, model="cube", color=hair_c,
                   scale=(.15,.35,.5), position=(-.5,.15,-.15))  # side
            Entity(parent=self.head, model="cube", color=hair_c,
                   scale=(.15,.35,.5), position=(.5,.15,-.15))  # side

        # Shoulders — rounded
        self.l_shoulder = Entity(parent=self, model="cube", color=shirt_c,
                                  scale=(.22,.15,.22), position=(-.44,1.35,0))
        self.r_shoulder = Entity(parent=self, model="cube", color=shirt_c,
                                  scale=(.22,.15,.22), position=(.44,1.35,0))
        # Upper arms
        self.la = Entity(parent=self, model="cube", color=shirt_c,
                         scale=(.2,.35,.2), position=(-.48,1.1,0))
        self.ra = Entity(parent=self, model="cube", color=shirt_c,
                         scale=(.2,.35,.2), position=(.48,1.1,0))
        # Lower arms (skin colored = forearms)
        self.la_lower = Entity(parent=self.la, model="cube", color=skin_c,
                                scale=(.85,.8,.85), position=(0,-.55,0))
        self.ra_lower = Entity(parent=self.ra, model="cube", color=skin_c,
                                scale=(.85,.8,.85), position=(0,-.55,0))
        # Hands
        Entity(parent=self.la_lower, model="cube", color=skin_c,
               scale=(.9,.4,.7), position=(0,-.5,0))
        Entity(parent=self.ra_lower, model="cube", color=skin_c,
               scale=(.9,.4,.7), position=(0,-.5,0))

        # Upper legs
        self.ll = Entity(parent=self, model="cube", color=body_c,
                         scale=(.25,.4,.25), position=(-.17,.5,0))
        self.rl = Entity(parent=self, model="cube", color=body_c,
                         scale=(.25,.4,.25), position=(.17,.5,0))
        # Lower legs (slightly darker)
        self.ll_lower = Entity(parent=self.ll, model="cube", color=body_c,
                                scale=(.9,.85,.9), position=(0,-.5,0))
        self.rl_lower = Entity(parent=self.rl, model="cube", color=body_c,
                                scale=(.9,.85,.9), position=(0,-.5,0))
        # Shoes — detailed with sole
        shoe_c = _rgb(35,35,35)
        for leg_lower in [self.ll_lower, self.rl_lower]:
            shoe = Entity(parent=leg_lower, model="cube", color=shoe_c,
                          scale=(1.1,.35,1.4), position=(0,-.52,.05))
            Entity(parent=shoe, model="cube", color=_rgb(25,25,25),
                   scale=(1.02,.3,.95), position=(0,-.4,0))  # sole
            Entity(parent=shoe, model="cube", color=_rgb(60,60,60),
                   scale=(.8,.15,.3), position=(0,.3,.35))  # tongue

        # Player indicator
        if is_player:
            Entity(parent=self, model="cube", color=_rgb(255,255,50),
                   scale=(.1,.1,.1), position=(0,2.3,0), rotation=(45,45,0))
        # Nametag
        if nametag:
            c = _rgb(255,255,80) if is_player else color.white
            Text(text=nametag, scale=10, billboard=True, parent=self,
                 position=(0,2.5,0), origin=(0,0), color=c)
        self._wp = 0
        self._idle_phase = random.uniform(0, 6.28)
        self._hit_timer = 0

    def animate_walk(self, dt, spd=1.0):
        self._wp += dt * 10 * spd
        s = math.sin(self._wp) * 35
        self.la.rotation_x = s; self.ra.rotation_x = -s
        self.ll.rotation_x = -s*.8; self.rl.rotation_x = s*.8
        b = abs(math.sin(self._wp))*.04
        self.torso.y = 1.0+b; self.head.y = 1.65+b
        # Slight body lean when walking
        self.torso.rotation_z = math.sin(self._wp) * 3
        self.head.rotation_z = math.sin(self._wp) * 1.5

    def animate_idle(self, dt):
        self._idle_phase += dt * 1.5
        for p in (self.la,self.ra,self.ll,self.rl):
            p.rotation_x = lerp(p.rotation_x, 0, dt*5)
        # Breathing bob
        breath = math.sin(self._idle_phase) * 0.015
        self.torso.y = 1.0 + breath
        self.head.y = 1.65 + breath
        # Subtle arm sway
        sway = math.sin(self._idle_phase * 0.7) * 3
        self.la.rotation_z = 5 + sway
        self.ra.rotation_z = -5 - sway
        # Slight head look around
        self.head.rotation_y = math.sin(self._idle_phase * 0.3) * 8

    def animate_hit(self):
        """Flinch/stagger animation when hit."""
        self._hit_timer = 0.5
        # Stagger back
        self.torso.animate_rotation(Vec3(-20, 0, random.uniform(-15,15)), duration=.1)
        self.torso.animate_rotation(Vec3(0,0,0), duration=.3, delay=.15)
        # Head snap
        self.head.animate_rotation(Vec3(-30, random.uniform(-20,20), 0), duration=.08)
        self.head.animate_rotation(Vec3(0,0,0), duration=.25, delay=.12)
        # Arms fly up
        self.la.animate_rotation(Vec3(-60, 0, 30), duration=.1)
        self.la.animate_rotation(Vec3(0, 0, 5), duration=.3, delay=.15)
        self.ra.animate_rotation(Vec3(-60, 0, -30), duration=.1)
        self.ra.animate_rotation(Vec3(0, 0, -5), duration=.3, delay=.15)

    def animate_throw(self):
        """Throw animation — wind up then release."""
        self.ra.animate_rotation(Vec3(-90, 0, -20), duration=.15)
        self.ra.animate_rotation(Vec3(60, 0, -10), duration=.12, delay=.15)
        self.ra.animate_rotation(Vec3(0, 0, -5), duration=.2, delay=.3)
        self.torso.animate_rotation(Vec3(0, -20, 0), duration=.15)
        self.torso.animate_rotation(Vec3(0, 30, 0), duration=.12, delay=.15)
        self.torso.animate_rotation(Vec3(0, 0, 0), duration=.2, delay=.3)


class KillerModel(Entity):
    def __init__(self, killer_type="john_doe", **kw):
        super().__init__(**kw)
        info = KILLERS[killer_type]
        mc, ec, h = info["color"], info["eye_color"], info["height"]
        if killer_type == "beast":
            self.body = Entity(parent=self, model="cube", color=mc, unlit=True,
                               scale=(.8,.4,1.5), position=(0,.3,0))
            self.head = Entity(parent=self, model="sphere", color=mc, unlit=True,
                               scale=(.5,.35,.5), position=(0,.4,.8))
            for side in [-1,1]:
                for z in [-.4,0,.4]:
                    Entity(parent=self.body, model="cube", color=mc, unlit=True,
                           scale=(.8,.12,.12), position=(side*.6,-.15,z),
                           rotation=(0,0,side*30))
        else:
            self.body = Entity(parent=self, model="cube", color=mc, unlit=True,
                               scale=(.7,h*.45,.5), position=(0,h*.35,0))
            self.head = Entity(parent=self, model="sphere", color=mc, unlit=True,
                               scale=(.5,.55,.5), position=(0,h*.7,0))
            Entity(parent=self, model="cube", color=mc, unlit=True, scale=(.18,h*.35,.18),
                   position=(-.5,h*.25,0))
            Entity(parent=self, model="cube", color=mc, unlit=True, scale=(.18,h*.35,.18),
                   position=(.5,h*.25,0))
            Entity(parent=self, model="cube", color=mc, unlit=True, scale=(.22,h*.3,.22),
                   position=(-.22,.3,0))
            Entity(parent=self, model="cube", color=mc, unlit=True, scale=(.22,h*.3,.22),
                   position=(.22,.3,0))
        # Dim glowing eyes only — no other glow
        Entity(parent=self.head, model="sphere", color=ec, unlit=True,
               scale=(.15,.2,.1), position=(-.12,.05,.4))
        Entity(parent=self.head, model="sphere", color=ec, unlit=True,
               scale=(.15,.2,.1), position=(.12,.05,.4))
        # Face texture on killer head
        face_tex = _tex(killer_type)
        if face_tex:
            Entity(parent=self.head, model="quad", texture=face_tex,
                   scale=(.9,.9), position=(0,0,.51), color=color.white, unlit=True)
        # No outlines, no aura, no name tag — killer is dark and silent
        self.ground_glow = Entity(parent=self, model="cube", color=ec, unlit=True,
                                   scale=(.01,.01,.01), position=(0,-100,0), alpha=0)
        self.aura = Entity(parent=self, model="sphere", color=ec, unlit=True,
                           scale=(.01,.01,.01), position=(0,-100,0), alpha=0)
        self._bp = random.uniform(0,6.28)
        self._ec = ec

    def animate_move(self, dt, spd=1.0):
        self._bp += dt*6*spd
        # Eerie head tilt
        self.head.rotation_z = math.sin(self._bp*.3)*8


# ═══════════════════════════════════════════════════════════════════════════
#  NPC
# ═══════════════════════════════════════════════════════════════════════════
class NPC:
    def __init__(self, pos, survivor_key):
        info = SURVIVORS[survivor_key]
        self.name = info["name"]
        self.survivor_key = survivor_key
        self.pos = Vec3(pos[0], 0, pos[2]) if len(pos)==3 else Vec3(pos[0],0,pos[1])
        self.model = HumanModel(
            body_c=info["body"], shirt_c=info["shirt"],
            skin_c=info["skin"], nametag=self.name, position=self.pos,
            hat_color=info.get("hat_color"))
        self.alive = True
        self.dialogue_timer = 0
        self.current_line = ""
        self._patrol_target = None
        self._pick_target()
        # Ability state
        self.ability_cd = 0
        self.ability_type = info.get("npc_ability", "")
        self.ability_cooldown_max = info.get("ability_cooldown", 20)
        self.npc_lines = info.get("npc_lines", NPC_LINES)
        self._ability_entities = []  # turrets, bombs etc.

    def _pick_target(self):
        walkable = []
        for ri, row in enumerate(MAP):
            for ci, cell in enumerate(row):
                if cell != 1:
                    wx = ci*ROOM - len(row)*ROOM/2
                    wz = ri*ROOM - len(MAP)*ROOM/2
                    walkable.append(Vec3(wx,0,wz))
        self._patrol_target = random.choice(walkable) if walkable else Vec3(0,0,0)

    def update(self, dt, player_pos, killer_pos, killer_ref=None):
        if not self.alive: return None
        # Ability cooldown
        if self.ability_cd > 0: self.ability_cd -= dt
        # Patrol slowly
        if self._patrol_target:
            d = self._patrol_target - self.pos; d.y = 0
            if d.length() < 2:
                self._pick_target()
            elif d.length() > 0.1:
                dn = d.normalized() * 2.0 * dt
                np2 = self.pos + dn
                mx = int((np2.x + len(MAP[0])*ROOM/2)/ROOM)
                mz = int((np2.z + len(MAP)*ROOM/2)/ROOM)
                if 0<=mz<len(MAP) and 0<=mx<len(MAP[0]) and MAP[mz][mx]!=1:
                    self.pos = np2; self.pos.y = 0
                    ang = math.degrees(math.atan2(dn.x,dn.z))
                    self.model.rotation_y = lerp(self.model.rotation_y, ang, dt*5)
                    self.model.animate_walk(dt, 0.5)
                else:
                    self._pick_target()
        self.model.position = self.pos
        # Collaboration: run from killer but group up near player
        dk = distance(self.pos, killer_pos)
        dp = distance(self.pos, player_pos)
        if dk < 14:
            away = (self.pos - killer_pos); away.y = 0
            if away.length() > 0.1:
                # Group up near player while fleeing
                if dp < 20 and dp > 3:
                    toward_player = (player_pos - self.pos); toward_player.y = 0
                    if toward_player.length() > 0.1:
                        move_dir = (away.normalized() * 0.6 + toward_player.normalized() * 0.4).normalized()
                    else:
                        move_dir = away.normalized()
                else:
                    move_dir = away.normalized()
                self.pos += move_dir * 5.5 * dt
                self.model.animate_walk(dt, 1.5)
            # Use ability when killer is close!
            if dk < 10 and self.ability_cd <= 0:
                self._use_npc_ability(killer_pos, killer_ref)
        elif dp < 10 and dp > 2:
            # Follow player when safe (collaborate)
            toward = (player_pos - self.pos); toward.y = 0
            if toward.length() > 0.1:
                self.pos += toward.normalized() * 1.5 * dt
                self.model.animate_walk(dt, 0.4)
        # NPC repairs generators when safe and near one
        if dk > 18 and hasattr(self, '_gen_repair_timer'):
            self._gen_repair_timer -= dt
            if self._gen_repair_timer <= 0:
                self._gen_repair_timer = random.uniform(8, 15)
                # Completed a gen!
                return "gen_done"
        elif dk > 18:
            self._gen_repair_timer = random.uniform(8, 15)
        # Die if killer too close
        if dk < 2.5:
            self.alive = False
            if self.model:
                self.model.animate_scale(0, duration=0.5)
                destroy(self.model, delay=0.6); self.model = None
            self._cleanup_abilities()
            return "died"
        # Check turrets/bombs vs killer
        self._check_ability_entities(killer_pos, killer_ref, dt)
        # Dialogue near player
        dp = distance(self.pos, player_pos)
        self.dialogue_timer -= dt
        if dp < 6 and self.dialogue_timer <= 0:
            self.current_line = random.choice(self.npc_lines)
            self.dialogue_timer = random.uniform(5, 10)
        return None

    def _use_npc_ability(self, killer_pos, killer_ref):
        self.ability_cd = self.ability_cooldown_max
        self.current_line = random.choice(self.npc_lines)
        self.dialogue_timer = 4
        at = self.ability_type

        # ── THROW PROJECTILE AT KILLER (all NPCs can do this) ──
        if killer_ref and distance(self.pos, killer_pos) < 15:
            d = killer_pos - self.pos; d.y = 0
            if d.length() > 0.1:
                dn = d.normalized()
                # Throw animation
                if self.model:
                    self.model.animate_throw()
                # Projectile — colored by survivor type
                si = SURVIVORS.get(self.survivor_key, {})
                proj_color = si.get("shirt", _rgb(200,200,100))
                proj = Entity(model="sphere", color=proj_color, unlit=True,
                              scale=.25, position=self.pos + Vec3(0, 1.5, 0) + dn * 1)
                Entity(parent=proj, model="sphere", color=proj_color, scale=2, alpha=.1)
                proj._dir = dn; proj._speed = 18; proj._life = 2.0
                proj._stun_dur = 1.5; proj._type = "npc_throw"
                self._ability_entities.append(proj)
                # Trail particles
                for _ in range(4):
                    tp = Entity(model="sphere", color=proj_color, scale=.08,
                                position=proj.position)
                    tp.animate_scale(0, duration=.3)
                    destroy(tp, delay=.35)

        if at == "turret":
            # Place a turret entity at current position
            t = Entity(model="cube", color=_rgb(50,130,200), scale=(.6,.8,.6),
                       position=self.pos+Vec3(0,.4,0))
            # Barrel
            Entity(parent=t, model="cube", color=_rgb(80,80,90), scale=(.2,.2,.8),
                   position=(0,.3,.4))
            # Base
            Entity(parent=t, model="cube", color=_rgb(60,60,70), scale=(1.2,.15,1.2),
                   position=(0,-.35,0))
            t._life = 15.0  # lasts 15 seconds
            t._stun_range = 6.0
            t._type = "turret"
            self._ability_entities.append(t)
            particles(self.pos+Vec3(0,1,0), _rgb(50,150,255), 6)
        elif at == "bomb":
            b = Entity(model="sphere", color=_rgb(60,60,60), scale=.4,
                       position=self.pos+Vec3(0,.3,0))
            # Fuse
            Entity(parent=b, model="cube", color=_rgb(200,100,30), scale=(.08,.5,.08),
                   position=(0,.6,0))
            # Spark
            Entity(parent=b, model="sphere", color=_rgb(255,200,50), unlit=True,
                   scale=.15, position=(0,.9,0))
            b._life = 8.0
            b._explode_range = 7.0
            b._type = "bomb"
            self._ability_entities.append(b)
            particles(self.pos+Vec3(0,1,0), _rgb(255,150,50), 6)
        elif at == "flashbang":
            if killer_ref and distance(self.pos, killer_pos) < 10:
                killer_ref.stun(3)
                particles(self.pos+Vec3(0,1.5,0), _rgb(255,255,200), 12)
        elif at == "heal":
            # Heal aura — visual ring
            ring = Entity(model="sphere", color=_rgba(50,255,100,60), scale=.5,
                          position=self.pos+Vec3(0,.5,0))
            ring.animate_scale(5, duration=1); ring.animate_color(_rgba(50,255,100,0), duration=1)
            destroy(ring, delay=1.1)
        elif at == "speed_boost":
            particles(self.pos+Vec3(0,1,0), _rgb(255,200,50), 8)
        elif at == "vanish":
            if self.model:
                self.model.color = _rgba(50,50,50,30)
                invoke(setattr, self.model, 'color', color.white, delay=3)
        elif at == "radar":
            particles(self.pos+Vec3(0,2,0), _rgb(100,200,255), 10)
        elif at == "shield":
            ring = Entity(model="sphere", color=_rgba(255,220,50,80), scale=1,
                          position=self.pos+Vec3(0,1,0))
            ring.animate_scale(3, duration=.5); ring.animate_color(_rgba(255,220,50,0), duration=1.5)
            destroy(ring, delay=1.6)

    def _check_ability_entities(self, killer_pos, killer_ref, dt):
        to_remove = []
        for ent in self._ability_entities:
            if not ent: to_remove.append(ent); continue
            ent._life -= dt
            if ent._life <= 0:
                destroy(ent); to_remove.append(ent); continue
            etype = getattr(ent, '_type', '')
            dk = distance(ent.position, killer_pos)
            if etype == "npc_throw":
                # Flying projectile toward killer
                ent.position += ent._dir * ent._speed * dt
                ent.position.y = 1.5
                ent.rotation_y += dt * 360
                if dk < 2.0 and killer_ref:
                    killer_ref.stun(getattr(ent, '_stun_dur', 1.5))
                    particles(ent.position + Vec3(0,.5,0), ent.color, 8)
                    ent._life = 0
                # Break on walls
                mx = int((ent.position.x + len(MAP[0])*ROOM/2)/ROOM)
                mz = int((ent.position.z + len(MAP)*ROOM/2)/ROOM)
                if not (0<=mz<len(MAP) and 0<=mx<len(MAP[0])) or MAP[mz][mx] == 1:
                    ent._life = 0
            elif etype == "turret":
                ent.rotation_y += dt * 90  # spinning turret
                if dk < ent._stun_range and killer_ref and not killer_ref.stunned:
                    killer_ref.stun(3)
                    particles(ent.position+Vec3(0,1,0), _rgb(50,150,255), 10)
                    ent._life = 0  # used up
            elif etype == "bomb":
                if dk < ent._explode_range:
                    # BOOM
                    if killer_ref: killer_ref.stun(4)
                    particles(ent.position+Vec3(0,1,0), _rgb(255,100,0), 20)
                    particles(ent.position+Vec3(0,1,0), _rgb(255,200,50), 15)
                    # Explosion visual
                    boom = Entity(model="sphere", color=_rgba(255,100,0,180), scale=.5,
                                  position=ent.position)
                    boom.animate_scale(8, duration=.4); boom.animate_color(_rgba(255,50,0,0), duration=.6)
                    destroy(boom, delay=.65)
                    ent._life = 0
        for e in to_remove:
            if e in self._ability_entities: self._ability_entities.remove(e)

    def _cleanup_abilities(self):
        for e in self._ability_entities:
            if e: destroy(e)
        self._ability_entities.clear()

    def destroy(self):
        if self.model: destroy(self.model); self.model = None
        self._cleanup_abilities()


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
        self.attack_cooldown = 0  # 2s cooldown between melee attacks
        self.ranged_cd = 0  # ranged attack cooldown
        self.ranged_interval = 8  # seconds between ranged shots
        self._projectiles = []
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
        # Attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
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
        # Detection — use actual detect range, not instant
        detect = self.info["detect_range"]
        if player_invisible:
            detect *= 0.3
        # Choose target — chase NPCs more often (60% chance if NPC closer)
        target = player_pos
        target_is_player = True
        for np_pos in npc_positions:
            nd = distance(self.pos, np_pos)
            if nd < dp and nd < detect and random.random() < 0.6:
                target = np_pos
                target_is_player = False
        if dp < detect and not player_invisible and random.random() > 0.5:
            self.state = "chase"
            self.chase_timer = 6
            target = player_pos
            target_is_player = True
        elif self.state == "chase":
            self.chase_timer -= dt
            if self.chase_timer <= 0:
                self.state = "patrol"
                self._pick_patrol()
        elif random.random() < 0.002:
            # Rarely aggro toward player when patrolling
            self.state = "chase"
            self.chase_timer = 4
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
                if hasattr(self.model, 'aura'): self.model.aura.alpha = 0
                if hasattr(self.model, 'ground_glow'): self.model.ground_glow.alpha = 0
            elif self.type == "phantom":
                self.model.color = _rgba(60,60,80,140)
            else:
                if hasattr(self.model, 'aura'): self.model.aura.enabled = True
                if hasattr(self.model, 'ground_glow'): self.model.ground_glow.enabled = True
        # Kill check — 2 second cooldown between melee attacks
        if dp < self.info["kill_range"] and self.state == "chase" and target_is_player and self.attack_cooldown <= 0:
            self.attack_cooldown = 2.0
            return True
        # Ranged attack — projectile every 8s when chasing and >5 away
        if self.ranged_cd > 0:
            self.ranged_cd -= dt
        if self.state == "chase" and target_is_player and dp > 5 and dp < 30 and self.ranged_cd <= 0 and not self.stunned:
            self.ranged_cd = self.ranged_interval
            self._fire_projectile(player_pos)
        # Update projectiles
        self._update_projectiles(dt, player_pos)
        return False

    def _fire_projectile(self, player_pos):
        """Killer fires a ranged projectile toward player."""
        d = player_pos - self.pos; d.y = 0
        if d.length() < 0.1: return
        dn = d.normalized()
        ec = self.info.get("eye_color", _rgb(255,0,0))
        # Projectile entity
        proj = Entity(model="sphere", color=ec, unlit=True,
                      scale=.35, position=self.pos + Vec3(0, 1.5, 0) + dn * 1.5)
        # Trail glow
        Entity(parent=proj, model="sphere", color=ec, unlit=True,
               scale=2, alpha=.15)
        proj._dir = dn
        proj._speed = 15
        proj._life = 3.0
        proj._hit = False
        self._projectiles.append(proj)
        # Muzzle flash
        flash = Entity(model="sphere", color=ec, unlit=True, scale=.8,
                       position=self.pos + Vec3(0, 1.5, 0) + dn * 1.5)
        flash.animate_scale(0, duration=.3)
        destroy(flash, delay=.35)

    def _update_projectiles(self, dt, player_pos):
        to_remove = []
        for p in self._projectiles:
            if not p or p._hit:
                to_remove.append(p); continue
            p._life -= dt
            if p._life <= 0:
                destroy(p); to_remove.append(p); continue
            p.position += p._dir * p._speed * dt
            p.position.y = 1.5
            # Hit player check
            if distance(p.position, player_pos) < 1.8:
                p._hit = True
                # Impact particles
                for _ in range(8):
                    sp = Entity(model="cube", color=p.color, unlit=True,
                                scale=random.uniform(.05,.15), position=p.position)
                    t = p.position + Vec3(random.uniform(-1.5,1.5),random.uniform(.5,2.5),random.uniform(-1.5,1.5))
                    sp.animate_position(t, duration=.4)
                    sp.animate_scale(0, duration=.4)
                    destroy(sp, delay=.45)
                destroy(p); to_remove.append(p)
                # Signal hit to game (will be checked in main update)
                self._ranged_hit = True
            # Hit wall check
            mx = int((p.position.x + len(MAP[0])*ROOM/2)/ROOM)
            mz = int((p.position.z + len(MAP)*ROOM/2)/ROOM)
            if not (0<=mz<len(MAP) and 0<=mx<len(MAP[0])) or MAP[mz][mx] == 1:
                destroy(p); to_remove.append(p)
        for r in to_remove:
            if r in self._projectiles: self._projectiles.remove(r)

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
        # Visual: killer flashes blue/white, sparks fly, "STUNNED" text
        if self.model:
            # Electric sparks around killer
            for _ in range(12):
                sp = Entity(model="cube", color=_rgb(100,200,255), unlit=True,
                            scale=random.uniform(.05,.15),
                            position=self.pos+Vec3(random.uniform(-1,1),random.uniform(.5,2.5),random.uniform(-1,1)))
                t = self.pos+Vec3(random.uniform(-2,2),random.uniform(1,4),random.uniform(-2,2))
                sp.animate_position(t, duration=.4, curve=curve.out_expo)
                sp.animate_scale(0, duration=.5)
                destroy(sp, delay=.55)
            # Stun ring
            ring = Entity(model="sphere", color=_rgba(100,200,255,150), unlit=True,
                          scale=.5, position=self.pos+Vec3(0,1.5,0))
            ring.animate_scale(5, duration=.5)
            ring.animate_color(_rgba(100,200,255,0), duration=.8)
            destroy(ring, delay=.85)
            # Dizzy stars orbiting head
            for i in range(3):
                star = Entity(model="cube", color=_rgb(255,255,100), unlit=True,
                              scale=.15, position=self.pos+Vec3(0,3,0),
                              rotation=(0,0,45))
                star.animate_position(self.pos+Vec3(
                    math.cos(i*2.1)*1.5, 3+math.sin(i*3)*.3, math.sin(i*2.1)*1.5),
                    duration=duration, curve=curve.linear)
                star.animate_rotation(Vec3(0,720,45), duration=duration)
                star.animate_scale(0, duration=.3, delay=duration-.3)
                destroy(star, delay=duration)
            # Flash killer body white briefly
            orig_body_c = self.model.body.color if hasattr(self.model,'body') else None
            if orig_body_c and hasattr(self.model, 'body'):
                self.model.body.color = _rgb(150,200,255)
                invoke(setattr, self.model.body, 'color', orig_body_c, delay=.5)

    def destroy(self):
        if self.model:
            destroy(self.model)
            self.model = None
        for p in getattr(self, '_projectiles', []):
            if p: destroy(p)
        self._projectiles = []


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
        self.ability2_cooldown = 0
        self.game_time = 0
        self.round_timer = ROUND_TIME
        self.round_num = 0
        self.current_killer_type = None
        self.selected_survivor = "builderman"

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

        AmbientLight(color=Color(.25,.25,.30,1))
        DirectionalLight(y=10, rotation=(35,-45,0), color=Color(.3,.28,.25,1))

        for ri, row in enumerate(MAP):
            for ci, cell in enumerate(row):
                wx = ci*ROOM - ox
                wz = ri*ROOM - oz

                if cell == 1:
                    wall_tex = _tex("wall_brick")
                    w = Entity(model="cube", color=_rgb(50,50,58),
                               texture=wall_tex,
                               scale=(ROOM, WALL_H, ROOM), position=(wx,WALL_H/2,wz))
                    self.walls.append(w)
                    if random.random() < .25:
                        st = Entity(model="cube", color=_rgba(50,15,15,random.randint(30,60)),
                                    scale=(random.uniform(1,3),random.uniform(.5,2),.05),
                                    position=(wx+random.uniform(-2,2),random.uniform(.5,3),wz+ROOM/2))
                        self.walls.append(st)
                else:
                    fc = _rgb(40,40,45) if random.random()>.15 else _rgb(45,35,35)
                    floor_tex = _tex("floor_tile") if random.random() > .3 else _tex("floor_dirt")
                    f = Entity(model="cube", color=fc, texture=floor_tex,
                               scale=(ROOM,.1,ROOM), position=(wx,0,wz))
                    self.floors.append(f)
                    ceil_tex = _tex("wall_dark")
                    c = Entity(model="cube", color=_rgb(30,30,35), texture=ceil_tex,
                               scale=(ROOM,.1,ROOM),
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
                    # Lights in rooms — brighter
                    if cell==2 and random.random()<.65:
                        lc = random.choice([_rgba(255,230,170,120),_rgba(200,230,255,100),_rgba(255,160,120,90)])
                        lt = Entity(model="sphere", color=lc, unlit=True, scale=.2,
                                    position=(wx,WALL_H-.3,wz))
                        self.lights_list.append(lt)
                        Entity(model="cube",color=_rgb(60,60,60),scale=(.05,.3,.05),
                               position=(wx,WALL_H-.15,wz))

        # Climbable buildings with ramps/rooftops
        self._rooftops = []  # (center_pos, half_width, roof_y) for player standing
        for rp in room_positions:
            if random.random() < .40:
                bh = random.choice([2.0, 2.5, 3.0, 3.5])
                bw = random.uniform(2.5, 4.0)
                bx = rp.x + random.uniform(-1.5, 1.5)
                bz = rp.z + random.uniform(-1.5, 1.5)
                bc = random.choice([_rgb(55,50,60),_rgb(65,55,50),_rgb(50,55,65),_rgb(60,60,55)])
                # Main building body
                b = Entity(model="cube", color=bc, scale=(bw, bh, bw),
                           position=(bx, bh/2, bz))
                self.buildings.append(b)
                # Roof platform (slightly wider, flat top you can stand on)
                roof = Entity(model="cube", color=_rgb(70,65,60),
                              scale=(bw+.6, .2, bw+.6), position=(bx, bh+.1, bz))
                self.buildings.append(roof)
                self._rooftops.append((Vec3(bx, bh+.2, bz), (bw+.6)/2, bh+.2))
                # Ramp/stairs on one side so player can climb up
                side = random.choice([-1, 1])
                ramp_dir = random.choice(['x', 'z'])
                steps = int(bh / 0.5)
                for si_idx in range(steps):
                    step_y = (si_idx + 1) * (bh / steps)
                    step_frac = (si_idx + 1) / steps
                    if ramp_dir == 'x':
                        sx = bx + side * (bw/2 + .4 + si_idx * .35)
                        sz = bz
                    else:
                        sx = bx
                        sz = bz + side * (bw/2 + .4 + si_idx * .35)
                    step = Entity(model="cube", color=_rgb(50,50,55),
                                  scale=(.8, .25, .8), position=(sx, step_y - .1, sz))
                    self.buildings.append(step)
                    self._rooftops.append((Vec3(sx, step_y, sz), .5, step_y))
                # Windows on two sides
                for wz_off in [-.25, .15]:
                    Entity(parent=b, model="cube", color=_rgba(120,170,220,50),
                           scale=(.25,.2,.02), position=(0, wz_off, .51))
                    Entity(parent=b, model="cube", color=_rgba(120,170,220,50),
                           scale=(.02,.2,.25), position=(.51, wz_off, 0))
                # Door
                Entity(parent=b, model="cube", color=_rgb(80,60,40),
                       scale=(.25,.35,.02), position=(0, -.3, .51))
            if random.random() < .18:
                # Watch tower — tall, climbable
                th = random.uniform(3.5, WALL_H - .3)
                tw = 1.2
                tx = rp.x + random.uniform(-1, 1)
                tz = rp.z + random.uniform(-1, 1)
                t = Entity(model="cube", color=_rgb(55,55,65), scale=(tw, th, tw),
                           position=(tx, th/2, tz))
                self.buildings.append(t)
                # Top platform
                tp = Entity(model="cube", color=_rgb(65,60,55),
                            scale=(tw+1, .2, tw+1), position=(tx, th+.1, tz))
                self.buildings.append(tp)
                self._rooftops.append((Vec3(tx, th+.2, tz), (tw+1)/2, th+.2))
                # Ladder (cubes going up one side)
                for li in range(int(th / 0.6)):
                    ly = (li + 1) * 0.6
                    lad = Entity(model="cube", color=_rgb(80,70,50),
                                 scale=(.15, .08, tw+.2), position=(tx + tw/2 + .15, ly, tz))
                    self.buildings.append(lad)
                    self._rooftops.append((Vec3(tx + tw/2 + .15, ly+.05, tz), .3, ly+.05))
                # Antenna
                Entity(parent=t, model="cube", color=_rgb(90,90,90),
                       scale=(.08, 1.2, .08), position=(0, .55, 0))
                # Blinking light on top
                lt = Entity(model="sphere", color=_rgb(255,50,50), unlit=True,
                            scale=.12, position=(tx, th+1.2, tz))
                self.lights_list.append(lt)

        self.player_pos = (start_pos or Vec3(0,0,0)) + Vec3(0,P_HEIGHT/2,0)

        # Exit
        if exit_pos:
            self.exit_entity = Entity(model="cube", color=_rgb(90,10,10),
                                       scale=(ROOM*.8, WALL_H, .5),
                                       position=exit_pos+Vec3(0,WALL_H/2,0))
            Text(text="EXIT", scale=15, billboard=True, color=_rgb(255,50,50),
                 position=exit_pos+Vec3(0,WALL_H-.5,0), parent=self.exit_entity)
        self._exit_pos = exit_pos

        # Generators — scattered in rooms
        self.generators = []
        gen_positions = room_positions[:]
        random.shuffle(gen_positions)
        for i in range(min(GENS_NEEDED + 2, len(gen_positions))):
            gp = gen_positions[i]
            # Generator box
            g = Entity(model="cube", color=_rgb(60,70,60), scale=(1.2, 1.0, .8),
                       position=gp + Vec3(random.uniform(-2,2), .5, random.uniform(-2,2)))
            # Panel on front
            Entity(parent=g, model="cube", color=_rgb(40,50,40), scale=(.6,.5,.05),
                   position=(0,.1,.51))
            # Red light (unrepaired)
            light = Entity(parent=g, model="sphere", color=_rgb(255,50,50), unlit=True,
                           scale=.15, position=(0,.45,.4))
            # Label
            Text(text="GENERATOR", scale=6, billboard=True, parent=g,
                 position=(0,1.2,0), origin=(0,0), color=_rgb(100,255,200))
            g._repaired = False
            g._light = light
            self.generators.append(g)
            self.buildings.append(g)

        # Hide spots — crates/lockers near buildings
        self._hide_spots = []
        for rp in room_positions:
            if random.random() < .3:
                hx = rp.x + random.uniform(-3,3)
                hz = rp.z + random.uniform(-3,3)
                crate = Entity(model="cube", color=_rgb(60,50,35), scale=(1.5,1.5,1.5),
                               position=(hx, .75, hz))
                Entity(parent=crate, model="cube", color=_rgb(50,40,25),
                       scale=(.9,.1,.9), position=(0,.52,0))  # lid
                self._hide_spots.append(Vec3(hx, 0, hz))
                self.buildings.append(crate)

        # Batteries
        all_floor = room_positions[:]
        random.shuffle(all_floor)
        for i in range(min(8, len(all_floor))):
            it = ItemPickup("battery", position=all_floor[i]+Vec3(random.uniform(-2,2),.8,random.uniform(-2,2)))
            self.items.append(it)

        # NPCs — spawn other survivors (not the one player picked)
        npc_survivor_keys = [k for k in SURVIVORS.keys() if k != self.selected_survivor]
        random.shuffle(npc_survivor_keys)
        random.shuffle(all_floor)
        for i in range(min(5, len(all_floor), len(npc_survivor_keys))):
            n = NPC((all_floor[i].x, 0, all_floor[i].z), npc_survivor_keys[i])
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

        scene.fog_color = _rgb(15,15,22)
        scene.fog_density = .02

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

        # Health bar (hearts)
        Entity(parent=self.hud, model="quad", color=_rgba(40,40,40,180),
               scale=(.15,.018), position=(-.62,-.49))
        self.health_bar = Entity(parent=self.hud, model="quad", color=_rgb(255,50,50),
                                  scale=(.15,.016), position=(-.62,-.49), origin=(-.5,0))
        Text(parent=self.hud, text="HEALTH", scale=.55, position=(-.74,-.475), color=_rgb(130,130,130))
        self.health_txt = Text(parent=self.hud, text="3/3", scale=.6,
                                position=(-.53,-.485), color=_rgb(255,100,100))

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
        # Generator counter
        self.gen_txt = Text(parent=self.hud, text="Gens: 0/5", scale=1.0,
                             position=(0,.39), color=_rgb(100,255,200), origin=(0,0))
        self.gen_progress_bg = Entity(parent=self.hud, model="quad", color=_rgba(40,40,40,180),
                                       scale=(.2,.015), position=(0,.355), enabled=False)
        self.gen_progress_bar = Entity(parent=self.hud, model="quad", color=_rgb(100,255,200),
                                        scale=(.2,.013), position=(0,.355), origin=(-.5,0), enabled=False)
        # Gen puzzle UI
        self.puzzle_root = Entity(parent=camera.ui, enabled=False)
        Entity(parent=self.puzzle_root, model="quad", color=_rgba(10,10,15,220), scale=(.45,.12))
        self.puzzle_title = Text(parent=self.puzzle_root, text="REPAIR PUZZLE", scale=.8,
                                  position=(0,.04), origin=(0,0), color=_rgb(100,255,200))
        self.puzzle_keys_txt = Text(parent=self.puzzle_root, text="", scale=1.5,
                                     position=(0,-.02), origin=(0,0), color=_rgb(255,255,255))
        self.puzzle_hint = Text(parent=self.puzzle_root, text="Press the keys in order!", scale=.6,
                                 position=(0,-.05), origin=(0,0), color=_rgb(150,150,160))
        self._puzzle_active = False
        self._puzzle_sequence = []
        self._puzzle_index = 0
        self._puzzle_gen = None

        # Interact
        self.interact_txt = Text(parent=self.hud, text="", scale=1.0,
                                  position=(0,-.3), color=_rgb(255,255,200), origin=(0,0))
        # Danger
        self.danger_txt = Text(parent=self.hud, text="", scale=1.5,
                                position=(0,.32), color=_rgb(255,0,0), origin=(0,0))
        # Chase indicator — red border overlays
        self.chase_border_top = Entity(parent=self.hud, model="quad",
            color=_rgba(255,0,0,0), scale=(2,.015), position=(0,.5))
        self.chase_border_bot = Entity(parent=self.hud, model="quad",
            color=_rgba(255,0,0,0), scale=(2,.015), position=(0,-.5))
        self.chase_border_left = Entity(parent=self.hud, model="quad",
            color=_rgba(255,0,0,0), scale=(.01,1), position=(-.78,0))
        self.chase_border_right = Entity(parent=self.hud, model="quad",
            color=_rgba(255,0,0,0), scale=(.01,1), position=(.78,0))
        self.chase_txt = Text(parent=self.hud, text="", scale=1.8,
            position=(0,.38), color=_rgb(255,50,50), origin=(0,0))
        self._chase_pulse = 0
        # Killer direction indicator (visible through walls)
        self.killer_arrow = Text(parent=self.hud, text="▼", scale=3, origin=(0,0),
                                  position=(0,0), color=_rgb(255,255,0), enabled=False)
        self.killer_dist_txt = Text(parent=self.hud, text="", scale=.7, origin=(0,0),
                                     position=(0,0), color=_rgb(255,255,0), enabled=False)
        # Crosshair
        Text(parent=self.hud, text="+", scale=1.8, position=(0,0),
             color=_rgba(200,200,200,100), origin=(0,0))
        # Flash indicator
        self.flash_txt = Text(parent=self.hud, text="[F] Light: ON", scale=.65,
                               position=(-.67,-.36), color=_rgb(255,240,200))
        self.sprint_txt = Text(parent=self.hud, text="", scale=.65,
                                position=(-.67,-.33), color=_rgb(100,200,255))
        # Controls
        Text(parent=self.hud, text="WASD/Arrows=Move | Shift=Sprint | Ctrl=Crouch | F=Light | 1/2=Abilities | Esc=Pause",
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

        # ── ABILITY 2 SIDEBAR ──
        self.ability2_bg = Entity(parent=self.hud, model="quad", color=_rgba(20,20,25,200),
                                   scale=(.18,.06), position=(-.65,-.19))
        self.ability2_icon = Entity(parent=self.hud, model="quad", color=_rgb(255,180,50),
                                     scale=(.025,.025), position=(-.72,-.19))
        self.ability2_name_txt = Text(parent=self.hud, text="[2] Ability 2", scale=.7,
                                       position=(-.70,-.18), color=_rgb(200,200,200))
        self.ability2_cd_txt = Text(parent=self.hud, text="READY", scale=.6,
                                     position=(-.70,-.205), color=_rgb(100,255,100))
        self.ability2_cd_bar = Entity(parent=self.hud, model="quad", color=_rgba(0,0,0,150),
                                       scale=(.18,.06), position=(-.65,-.19), origin=(-.5,0))

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

        # ── Death (lobby) ──
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
        Text(parent=self.death_root, text="[1] Quests  |  [2] Shop  |  [3] Spectate",
             scale=.7, position=(0,-.40), origin=(0,0), color=_rgb(180,180,200))

        # ── Quests panel (toggle with 1 in lobby) ──
        self.quests_root = Entity(parent=camera.ui, enabled=False)
        Entity(parent=self.quests_root, model="quad", color=_rgba(10,15,30,240), scale=(.6,.7))
        Text(parent=self.quests_root, text="QUESTS", scale=2.5, position=(0,.3), origin=(0,0),
             color=_rgb(255,200,50))
        quests = [
            ("Survive 3 rounds", "+50 coins"),
            ("Escape in under 60s", "+100 coins"),
            ("Use ability 5 times", "+30 coins"),
            ("Stun the killer 3 times", "+75 coins"),
            ("Survive with 1 HP", "+60 coins"),
        ]
        for i, (q, r) in enumerate(quests):
            y = .18 - i * .09
            Entity(parent=self.quests_root, model="quad", color=_rgba(30,35,50,200),
                   scale=(.52,.065), position=(0, y))
            Text(parent=self.quests_root, text=q, scale=.7, position=(-.24, y+.01),
                 color=_rgb(220,220,220))
            Text(parent=self.quests_root, text=r, scale=.65, position=(.2, y+.01),
                 color=_rgb(255,215,0))
        Text(parent=self.quests_root, text="[1] Close", scale=.6, position=(0,-.28),
             origin=(0,0), color=_rgb(150,150,160))

        # ── Shop panel (toggle with 2 in lobby) ──
        self.shop_root = Entity(parent=camera.ui, enabled=False)
        Entity(parent=self.shop_root, model="quad", color=_rgba(15,10,25,240), scale=(.75,.85))
        Text(parent=self.shop_root, text="SHOP", scale=2.5, position=(0,.38), origin=(0,0),
             color=_rgb(200,100,255))
        self.shop_coins_label = Text(parent=self.shop_root, text="", scale=.8,
             position=(-.15,.32), origin=(0,0), color=_rgb(255,215,0))
        self.shop_malice_label = Text(parent=self.shop_root, text="", scale=.8,
             position=(.15,.32), origin=(0,0), color=_rgb(200,50,255))

        # Survivor shop section
        Text(parent=self.shop_root, text="── SURVIVORS (coins) ──", scale=.65,
             position=(0,.26), origin=(0,0), color=_rgb(180,200,180))
        surv_prices = {"guest1337":80,"veronica":100,"taph":120,"noob":60,"bacon":80,
                       "shadow":150,"captain":100,"hacker":130,"athlete":110,"scout2":90,"tank2":140}
        self._shop_surv_btns = []
        idx = 0
        for sk, price in surv_prices.items():
            if sk not in SURVIVORS: continue
            sn = SURVIVORS[sk]["name"]
            y = .18 - idx * .055
            b = Button(parent=self.shop_root, text=f"{sn} — {price}c",
                       scale=(.35,.045), position=(-.18, y), color=_rgb(35,40,55),
                       highlight_color=_rgb(50,55,75), text_size=.6)
            b.on_click = self._make_buy_survivor(sk, price)
            self._shop_surv_btns.append(b)
            idx += 1

        # Killer shop section
        Text(parent=self.shop_root, text="── KILLERS (malice) ──", scale=.65,
             position=(.22,.26), origin=(0,0), color=_rgb(200,150,200))
        killer_prices = {"faceless":150,"corner":80,"masked":60,"glitch":50,"crawler":70,"phantom":80,"mimic":100,"warden":90}
        self._shop_killer_btns = []
        idx2 = 0
        for kk, price in killer_prices.items():
            if kk not in KILLERS: continue
            kn = KILLERS[kk]["name"]
            y = .18 - idx2 * .055
            b = Button(parent=self.shop_root, text=f"{kn} — {price}m",
                       scale=(.3,.045), position=(.22, y), color=_rgb(45,25,55),
                       highlight_color=_rgb(65,35,80), text_size=.6)
            b.on_click = self._make_buy_killer(kk, price)
            self._shop_killer_btns.append(b)
            idx2 += 1

        self.shop_msg = Text(parent=self.shop_root, text="", scale=.7,
             position=(0,-.35), origin=(0,0), color=_rgb(100,255,100))
        Text(parent=self.shop_root, text="[2] Close", scale=.6, position=(0,-.40),
             origin=(0,0), color=_rgb(150,150,160))
        self._shop_buttons = []  # compat

        # ── Spectate panel (toggle with 3 in lobby) ──
        self.spec_root = Entity(parent=camera.ui, enabled=False)
        self.spec_label = Text(parent=self.spec_root, text="SPECTATING", scale=1.5,
             position=(0,.45), origin=(0,0), color=_rgb(200,200,255))
        self.spec_name = Text(parent=self.spec_root, text="", scale=1.2,
             position=(0,.40), origin=(0,0), color=_rgb(255,255,200))
        Text(parent=self.spec_root, text="Left/Right Arrow = Switch  |  [3] Stop",
             scale=.6, position=(0,-.45), origin=(0,0), color=_rgb(150,150,170))
        self._spec_index = 0
        self._spec_active = False

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

        Button(parent=self.menu_root, text="PLAY", scale=(.3,.07), position=(0,-.02),
               color=_rgb(120,30,30), highlight_color=_rgb(170,50,50),
               on_click=self._start_game)

        # Hidden survivor buttons (kept for code compat, not shown on menu)
        self.surv_buttons = []
        self.surv_desc = Text(parent=self.menu_root, text="", scale=.7,
                               position=(0,-.12), origin=(0,0), color=_rgb(160,200,255))
        self.surv_ability_txt = Text(parent=self.menu_root, text="", scale=.65,
                                      position=(0,-.16), origin=(0,0), color=_rgb(150,150,180))

        self.menu_coins = Text(parent=self.menu_root, text=f"Coins: {self.save['coins']}",
                               scale=.9, position=(-.15,-.25), origin=(0,0), color=_rgb(255,215,0))
        self.menu_malice = Text(parent=self.menu_root, text=f"Malice: {self.save.get('malice',0)}",
                               scale=.9, position=(.15,-.25), origin=(0,0), color=_rgb(200,50,255))
        self.menu_stats = Text(parent=self.menu_root, text="", scale=.7,
                                position=(0,-.32), origin=(0,0), color=_rgb(150,150,150))

    def _make_surv_select(self, key):
        def fn():
            if key not in self.save.get("unlocked_survivors",["builderman"]):
                return  # locked
            self.selected_survivor = key
            self.save["selected_survivor"] = key
            save_data(self.save)
            self._update_surv_preview()
        return fn

    def _update_surv_preview(self):
        if self.selected_survivor not in SURVIVORS:
            self.selected_survivor = "builderman"
        s = SURVIVORS[self.selected_survivor]
        self.surv_desc.text = f"{s['name']}: {s['desc']}"
        a1 = f"[1] {s['ability_name']} — {s['ability_desc']} (CD:{s['ability_cooldown']}s)"
        a2n = s.get('ability2_name','')
        a2 = f"  |  [2] {a2n} — {s.get('ability2_desc','')} (CD:{s.get('ability2_cooldown',0)}s)" if a2n else ""
        self.surv_ability_txt.text = a1 + a2
        unlocked = self.save.get("unlocked_survivors", ["builderman"])
        for i, sk in enumerate(SURVIVORS.keys()):
            if i < len(self.surv_buttons):
                if sk == self.selected_survivor:
                    self.surv_buttons[i].color = _rgb(60,100,60)
                elif sk in unlocked:
                    self.surv_buttons[i].color = _rgb(40,40,55)
                else:
                    self.surv_buttons[i].color = _rgb(25,25,30)  # locked = dark

    def _make_shop_buy(self, idx, cost, name):
        def fn():
            if self.save["coins"] >= cost:
                self.save["coins"] -= cost
                save_data(self.save)
                self.shop_msg.text = f"Bought {name}!"
                self.shop_msg.color = _rgb(100,255,100)
                self.shop_coins_label.text = f"Coins: {self.save['coins']}"
            else:
                self.shop_msg.text = f"Need {cost} coins!"
                self.shop_msg.color = _rgb(255,100,100)
        return fn

    def _make_buy_survivor(self, sk, price):
        def fn():
            unlocked = self.save.get("unlocked_survivors", ["builderman"])
            if sk in unlocked:
                self.shop_msg.text = f"Already unlocked!"
                self.shop_msg.color = _rgb(255,200,100)
                return
            if self.save["coins"] >= price:
                self.save["coins"] -= price
                unlocked.append(sk)
                self.save["unlocked_survivors"] = unlocked
                save_data(self.save)
                self.shop_msg.text = f"Unlocked {SURVIVORS[sk]['name']}!"
                self.shop_msg.color = _rgb(100,255,100)
                self.shop_coins_label.text = f"Coins: {self.save['coins']}"
            else:
                self.shop_msg.text = f"Need {price} coins!"
                self.shop_msg.color = _rgb(255,100,100)
        return fn

    def _make_buy_killer(self, kk, price):
        def fn():
            unlocked = self.save.get("unlocked_killers", ["john_doe"])
            if kk in unlocked:
                self.shop_msg.text = f"Already unlocked!"
                self.shop_msg.color = _rgb(255,200,100)
                return
            malice = self.save.get("malice", 0)
            if malice >= price:
                self.save["malice"] = malice - price
                unlocked.append(kk)
                self.save["unlocked_killers"] = unlocked
                save_data(self.save)
                self.shop_msg.text = f"Unlocked {KILLERS[kk]['name']}!"
                self.shop_msg.color = _rgb(200,100,255)
                self.shop_malice_label.text = f"Malice: {self.save['malice']}"
            else:
                self.shop_msg.text = f"Need {price} malice!"
                self.shop_msg.color = _rgb(255,100,100)
        return fn

    def _start_killer_mode(self):
        """Play as the killer, hunting NPC survivors."""
        unlocked_k = self.save.get("unlocked_killers", ["carved"])
        # Filter out killers that no longer exist
        unlocked_k = [k for k in unlocked_k if k in KILLERS]
        if not unlocked_k:
            unlocked_k = [list(KILLERS.keys())[0]]
        self.save["unlocked_killers"] = unlocked_k
        save_data(self.save)
        self._hide_all()
        self._cleanup()
        u = 'Killer'
        if hasattr(self,'menu_name') and self.menu_name.text.strip():
            u = self.menu_name.text.strip()
        self.save['username'] = u
        save_data(self.save)
        self.round_num += 1
        self.save["rounds_played"] += 1
        save_data(self.save)

        # Pick killer from unlocked
        self.current_killer_type = random.choice(unlocked_k)
        ki = KILLERS[self.current_killer_type]

        # Reset for killer mode
        self.alive = True
        self.health = 999; self.max_health = 999
        self.hit_cooldown = 0
        self.stamina = MAX_STAMINA
        self.battery = FLASH_MAX
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
        self._killcam_timer = 0; self._killcam_model = None; self._killcam_fx = []
        self.gens_repaired = 0; self.gens_total = GENS_NEEDED
        self.gen_progress = 0; self.repairing_gen = None; self.hiding = False
        self._killer_mode = True
        self._kills_this_round = 0

        self._build_map()
        # Remove the AI killer — player IS the killer
        if self.killer: self.killer.destroy(); self.killer = None

        # Show intro
        self.state = "intro"
        self.intro_root.enabled = True
        self.intro_title.text = f"KILLER MODE"
        self.intro_killer.text = f"You are... {ki['name']}"
        self.intro_desc.text = f"Hunt them all. {ki['desc']}"
        self.intro_ability.text = f"Speed: {ki['chase_speed']} | Kill Range: {ki['kill_range']}"
        mouse.locked = False
        invoke(self._begin_killer_round, delay=4)

    def _begin_killer_round(self):
        if self.state != "intro": return
        self._hide_all()
        self.state = "playing"
        self.hud.enabled = True
        self.vignette.enabled = True
        mouse.locked = True
        ki = KILLERS[self.current_killer_type]
        self._add_event(f"KILLER MODE — You are {ki['name']}")
        self._add_event("Hunt all survivors before time runs out!")

    def _start_spectate(self):
        alive = [n for n in self.npcs if n.alive]
        if not alive and self.killer:
            # Spectate killer if no NPCs alive
            self._spec_targets = [('killer', self.killer)]
        elif alive:
            self._spec_targets = [('npc', n) for n in alive]
            if self.killer:
                self._spec_targets.append(('killer', self.killer))
        else:
            self._spec_targets = []
            return
        self._spec_index = 0
        self._spec_active = True
        self.spec_root.enabled = True
        self.death_root.enabled = False
        mouse.locked = False
        self._update_spec_cam()

    def _update_spec_cam(self):
        if not self._spec_targets: return
        self._spec_index = self._spec_index % len(self._spec_targets)
        kind, target = self._spec_targets[self._spec_index]
        name = target.name if kind == 'npc' else KILLERS[self.killer.type]["name"]
        self.spec_name.text = f"Watching: {name}"

    def _update_spectate(self, dt):
        if not self._spec_active or not self._spec_targets: return
        # Refresh target list (NPCs may have died)
        alive = [('npc', n) for n in self.npcs if n.alive]
        if self.killer: alive.append(('killer', self.killer))
        self._spec_targets = alive
        if not self._spec_targets:
            self._spec_active = False; self.spec_root.enabled = False
            self.death_root.enabled = True; return
        self._spec_index = self._spec_index % len(self._spec_targets)
        kind, target = self._spec_targets[self._spec_index]
        tpos = target.pos
        cam_target = tpos + Vec3(0, 6, -8)
        camera.position = lerp(camera.position, cam_target, dt * 4)
        dx = tpos.x - camera.x; dz = tpos.z - camera.z; dy = (tpos.y+1.5) - camera.y
        yaw = math.degrees(math.atan2(dx, dz))
        pitch = math.degrees(math.atan2(-dy, math.sqrt(dx*dx+dz*dz)))
        camera.rotation = Vec3(pitch, yaw, 0)
        name = target.name if kind == 'npc' else KILLERS[self.killer.type]["name"]
        self.spec_name.text = f"Watching: {name}"

    # ── STATE ─────────────────────────────────────────────────────────────
    def _hide_all(self):
        for u in (self.menu_root, self.hud, self.death_root, self.win_root,
                  self.pause_root, self.intro_root, self.announce, self.sub_announce,
                  self.vignette, self.scare_overlay, self.scare_face,
                  self.quests_root, self.shop_root, self.spec_root):
            u.enabled = False
        self._spec_active = False

    def _show_menu(self):
        self._hide_all()
        self._cleanup()
        self.state = "menu"
        self.menu_root.enabled = True
        self.menu_coins.text = f"Coins: {self.save['coins']}"
        self.menu_malice.text = f"Malice: {self.save.get('malice',0)}"
        self.menu_stats.text = f"Escapes: {self.save['escapes']}  |  Deaths: {self.save['deaths']}  |  Rounds: {self.save['rounds_played']}"
        camera.position = Vec3(0,5,-10); camera.rotation = Vec3(15,0,0)
        mouse.locked = False

    def _cleanup(self):
        for lst in (self.walls,self.floors,self.ceilings,self.items,self.buildings,self.lights_list):
            for e in lst: destroy(e)
            lst.clear()
        if hasattr(self, '_rooftops'): self._rooftops = []
        if hasattr(self, '_player_turrets'):
            for t in self._player_turrets:
                if t: destroy(t)
            self._player_turrets = []
        for n in self.npcs: n.destroy()
        self.npcs.clear()
        if self.killer: self.killer.destroy(); self.killer=None
        if self.flashlight: destroy(self.flashlight); self.flashlight=None
        if self.exit_entity: destroy(self.exit_entity); self.exit_entity=None
        for e in self._npc_speech_ents: destroy(e)
        self._npc_speech_ents.clear()
        self._event_lines.clear()
        self._cleanup_lobby()
        scene.fog_density = 0

    def _start_game(self):
        self._hide_all()
        self._cleanup()
        u = 'Survivor'
        if hasattr(self,'menu_name') and self.menu_name.text.strip():
            u = self.menu_name.text.strip()
        self.save['username'] = u
        self.selected_survivor = self.save.get("selected_survivor","builderman")
        if self.selected_survivor not in SURVIVORS:
            self.selected_survivor = "builderman"
        save_data(self.save)
        self.round_num = 0
        self._next_round()

    def _next_round(self):
        self._hide_all()
        self._cleanup()
        self.round_num += 1
        self.save["rounds_played"] += 1
        save_data(self.save)

        # Normal survivor round — no forced killer mode
        # Pick random killer (AI controlled)
        self.current_killer_type = random.choice(list(KILLERS.keys()))
        ki = KILLERS[self.current_killer_type]
        si = SURVIVORS[self.selected_survivor]

        # Reset player
        self.alive = True
        self.health = 3  # 3 hits to die
        self.max_health = 3
        self.hit_cooldown = 0  # invincibility after hit
        self.stamina = MAX_STAMINA
        self.battery = FLASH_MAX * si["flash_mult"]
        self.flash_on = True
        self.sprinting = False; self.crouching = False
        self.invisible = False; self.invis_timer = 0
        self.shielded = False; self.shield_timer = 0
        self.ability_cooldown = 0
        self.ability2_cooldown = 0
        self.game_time = 0
        self.round_timer = ROUND_TIME
        self.glitch_timer = 0
        self.yaw = 0; self.pitch = 0
        self._scare_active = False
        self._killcam_timer = 0
        self._killcam_model = None
        self._killcam_fx = []
        self.gens_repaired = 0
        self.gens_total = GENS_NEEDED
        self.gen_progress = 0  # 0-1 progress on current gen
        self.repairing_gen = None
        self.hiding = False

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
        a2 = si.get('ability2_name', '')
        self.ability2_name_txt.text = f"[2] {a2}" if a2 else "[2] ---"
        self.ability2_icon.color = _rgb(255,180,50) if a2 else _rgb(60,60,60)

        self._add_event(f"Round {self.round_num} — Killer: {KILLERS[self.current_killer_type]['name']}")
        self._add_event(f"Survive {ROUND_TIME}s or find the EXIT!")

    def _resume(self):
        self.pause_root.enabled = False
        self.hud.enabled = True; self.vignette.enabled = True
        self.state = "playing"; mouse.locked = True

    def _player_hit(self):
        """Player takes one hit. Dies at 0 HP."""
        if self.hit_cooldown > 0: return
        if self.shielded:
            self.shielded = False; self.shield_timer = 0
            self._add_event("Shield blocked the hit!")
            if self.killer:
                d = self.killer.pos - self.player_pos
                if d.length() > 0.1:
                    self.killer.pos += d.normalized() * 8
                    if self.killer.model: self.killer.model.position = self.killer.pos
                self.killer.stun(2)
            return
        self.health -= 1
        self.hit_cooldown = 1.5  # invincibility frames
        camera.shake(duration=.5, magnitude=3)
        # Blood splatter particles
        for _ in range(15):
            bp = Entity(model="cube", color=random.choice([_rgb(200,0,0),_rgb(150,0,0),_rgb(180,20,20)]),
                        scale=random.uniform(.05,.2), position=self.player_pos+Vec3(0,1,0))
            t = self.player_pos+Vec3(random.uniform(-3,3),random.uniform(.5,4),random.uniform(-3,3))
            bp.animate_position(t, duration=random.uniform(.3,.8), curve=curve.out_expo)
            bp.animate_scale(0, duration=.8)
            destroy(bp, delay=.85)
        # Red flash vignette — intense
        self.vignette.color = _rgba(220, 0, 0, 200)
        invoke(setattr, self.vignette, 'color', _rgba(120, 0, 0, 100), delay=.2)
        invoke(setattr, self.vignette, 'color', _rgba(0,0,0,60), delay=.8)
        # Screen crack lines (UI overlay)
        for angle in [random.uniform(-60,60) for _ in range(4)]:
            crack = Entity(parent=camera.ui, model="quad",
                           color=_rgba(200,0,0,150), scale=(.002, random.uniform(.2,.5)),
                           position=(random.uniform(-.3,.3), random.uniform(-.2,.2)),
                           rotation=(0,0,angle))
            crack.animate_color(_rgba(200,0,0,0), duration=1.5)
            destroy(crack, delay=1.6)
        # Heartbeat pulse if low HP
        if self.health == 1:
            pulse = Entity(parent=camera.ui, model="quad", color=_rgba(180,0,0,0), scale=(2,2))
            pulse.animate_color(_rgba(180,0,0,80), duration=.3)
            pulse.animate_color(_rgba(180,0,0,0), duration=.3, delay=.3)
            pulse.animate_color(_rgba(180,0,0,60), duration=.3, delay=.6)
            pulse.animate_color(_rgba(180,0,0,0), duration=.3, delay=.9)
            destroy(pulse, delay=1.3)
        # Knockback away from killer
        if self.killer:
            kb = self.player_pos - self.killer.pos
            kb.y = 0
            if kb.length() > 0.1:
                self.player_pos += kb.normalized() * 5
        if self.health > 0:
            self._add_event(f"HIT! {self.health}/{self.max_health} HP remaining!")
        else:
            self._player_die()

    def _player_die(self, cause=""):
        if not self.alive: return
        self.alive = False
        self.save["deaths"] += 1
        save_data(self.save)
        # Start kill cam instead of instant scare
        self._start_killcam(cause)

    def _show_death(self, cause=""):
        self._hide_all()
        self._cleanup()
        self.state = "lobby"
        mouse.locked = False
        mouse.visible = True
        self.death_root.enabled = True
        ki = KILLERS.get(self.current_killer_type, {})
        self.death_msg.text = cause or f"{ki.get('name','The killer')} caught you!"
        self.death_stats.text = f"Survived: {int(self.game_time)}s  |  Round {self.round_num}"

        # Build 3D lobby room
        self._lobby_ents = []
        lc = _rgb(50, 45, 55)
        # Floor
        f = Entity(model="cube", color=_rgb(40,38,45), scale=(30,.1,30), position=(0,0,0))
        self._lobby_ents.append(f)
        # Walls
        for wx, wz, sx, sz in [(-15,0,.5,30),(15,0,.5,30),(0,-15,30,.5),(0,15,30,.5)]:
            w = Entity(model="cube", color=lc, scale=(sx,5,sz), position=(wx,2.5,wz))
            self._lobby_ents.append(w)
        # Ceiling
        c = Entity(model="cube", color=_rgb(35,33,40), scale=(30,.1,30), position=(0,5,0))
        self._lobby_ents.append(c)
        # Lights
        AmbientLight(color=Color(.3,.3,.35,1))
        for lx, lz in [(-6,0),(6,0),(0,-6),(0,6)]:
            lt = Entity(model="sphere", color=_rgba(255,220,150,100), unlit=True,
                        scale=.2, position=(lx,4.7,lz))
            self._lobby_ents.append(lt)

        # Shop counter
        shop = Entity(model="cube", color=_rgb(80,50,30), scale=(4,1.2,2), position=(-8,.6,0))
        self._lobby_ents.append(shop)
        Entity(parent=shop, model="cube", color=_rgb(100,65,35), scale=(.9,.1,.9), position=(0,.52,0))
        Text(text="SHOP [2]", scale=10, billboard=True, color=_rgb(200,100,255),
             position=(-8,2.5,0), parent=scene)
        self._lobby_shop_pos = Vec3(-8,0,0)

        # Quest board
        qb = Entity(model="cube", color=_rgb(60,50,30), scale=(3,2.5,.3), position=(0,.125,-13))
        self._lobby_ents.append(qb)
        Entity(parent=qb, model="cube", color=_rgb(200,180,120), scale=(.85,.85,.5), position=(0,.1,.52))
        Text(text="QUESTS [1]", scale=10, billboard=True, color=_rgb(255,200,50),
             position=(0,2.8,-13), parent=scene)
        self._lobby_quest_pos = Vec3(0,0,-13)

        # Spectate screen
        sc = Entity(model="cube", color=_rgb(20,20,25), scale=(4,2.5,.2), position=(8,1.25,0))
        self._lobby_ents.append(sc)
        Entity(parent=sc, model="cube", color=_rgb(40,60,80), scale=(.9,.85,.5), position=(0,0,.52))
        Text(text="SPECTATE [3]", scale=10, billboard=True, color=_rgb(100,200,255),
             position=(8,3,0), parent=scene)
        self._lobby_spec_pos = Vec3(8,0,0)

        # Skin display pedestals — show ALL survivors
        all_surv_keys = list(SURVIVORS.keys())
        cols = min(6, len(all_surv_keys))
        for i, sk in enumerate(all_surv_keys):
            si = SURVIVORS[sk]
            row_i = i // cols
            col_i = i % cols
            px = -10 + col_i * 4
            pz = 8 + row_i * 4
            ped = Entity(model="cube", color=_rgb(50,50,60), scale=(1.5,.3,1.5),
                         position=(px,.15,pz))
            self._lobby_ents.append(ped)
            # Glow if unlocked
            unlocked = self.save.get("unlocked_survivors", ["builderman"])
            if sk in unlocked:
                Entity(parent=ped, model="cube", color=_rgb(50,255,100), unlit=True,
                       scale=(.8,.5,.8), position=(0,.3,0), alpha=.15)
            m = HumanModel(body_c=si["body"], shirt_c=si["shirt"], skin_c=si["skin"],
                           hat_color=si.get("hat_color"), nametag=si["name"],
                           position=(px,.3,pz))
            self._lobby_ents.append(m)

        # Next round button area
        nr = Entity(model="cube", color=_rgb(100,30,30), scale=(3,.3,3), position=(0,.15,12))
        self._lobby_ents.append(nr)
        Entity(parent=nr, model="cube", color=_rgb(140,40,40), unlit=True, scale=(.8,.5,.8),
               position=(0,.5,0))
        Text(text="NEXT ROUND [E]", scale=10, billboard=True, color=_rgb(255,100,100),
             position=(0,2,12), parent=scene)
        self._lobby_next_pos = Vec3(0,0,12)

        # Player spawn in lobby center
        self.player_pos = Vec3(0, P_HEIGHT/2, 0)
        self.yaw = 0; self.pitch = 0
        self.alive = True
        self.stamina = MAX_STAMINA
        scene.fog_density = 0

    def _update_lobby(self, dt):
        """Walk around 3D lobby, interact with stations."""
        if self._spec_active:
            self._update_spectate(dt)
            return
        # Movement (reuse same controls)
        self.yaw += mouse.velocity[0] * 80
        self.pitch -= mouse.velocity[1] * 80
        self.pitch = max(-80, min(80, self.pitch))
        yr = math.radians(self.yaw)
        fwd = Vec3(math.sin(yr), 0, math.cos(yr))
        right = Vec3(math.cos(yr), 0, -math.sin(yr))
        mv = Vec3(0, 0, 0)
        if held_keys["w"] or held_keys["up arrow"]: mv += fwd
        if held_keys["s"] or held_keys["down arrow"]: mv -= fwd
        if held_keys["a"] or held_keys["left arrow"]: mv -= right
        if held_keys["d"] or held_keys["right arrow"]: mv += right
        if mv.length() > 0:
            mv = mv.normalized() * PLAYER_SPEED * dt
            np2 = self.player_pos + mv
            np2.x = max(-14, min(14, np2.x))
            np2.z = max(-14, min(14, np2.z))
            self.player_pos = np2
        self.player_pos.y = P_HEIGHT / 2
        camera.position = Vec3(self.player_pos.x, self.player_pos.y + P_HEIGHT, self.player_pos.z)
        camera.rotation = Vec3(self.pitch, self.yaw, 0)
        # Proximity prompts
        prompt = ""
        if hasattr(self, '_lobby_shop_pos') and distance(self.player_pos, self._lobby_shop_pos) < 5:
            prompt = "[2] Open Shop"
        elif hasattr(self, '_lobby_quest_pos') and distance(self.player_pos, self._lobby_quest_pos) < 5:
            prompt = "[1] View Quests"
        elif hasattr(self, '_lobby_spec_pos') and distance(self.player_pos, self._lobby_spec_pos) < 5:
            prompt = "[3] Spectate"
        elif hasattr(self, '_lobby_next_pos') and distance(self.player_pos, self._lobby_next_pos) < 5:
            prompt = "[E] Start Next Round"
        self.death_msg.text = prompt
        self.death_msg.color = _rgb(255, 255, 200)

    def _cleanup_lobby(self):
        if hasattr(self, '_lobby_ents'):
            for e in self._lobby_ents:
                if e: destroy(e)
            self._lobby_ents = []

    def _player_survived(self):
        self.state = "won"
        self.save["escapes"] += 1
        earned = COINS_SURVIVE
        malice_earned = 15
        self.save["coins"] += earned
        self.save["malice"] = self.save.get("malice",0) + malice_earned
        save_data(self.save)
        self._hide_all()
        self.win_root.enabled = True
        self.win_stats.text = f"Survived Round {self.round_num}!"
        self.win_coins.text = f"+{earned} coins  |  +{malice_earned} malice"
        mouse.locked = False

    def _player_escaped(self):
        self.state = "won"
        self.save["escapes"] += 1
        earned = COINS_ESCAPE
        malice_earned = 30
        self.save["coins"] += earned
        self.save["malice"] = self.save.get("malice",0) + malice_earned
        save_data(self.save)
        self._hide_all()
        self.win_root.enabled = True
        self.win_stats.text = f"ESCAPED in {int(self.game_time)}s!"
        self.win_coins.text = f"+{earned} coins  |  +{malice_earned} malice"
        mouse.locked = False

    # ── KILL CAM ─────────────────────────────────────────────────────────
    def _start_killcam(self, cause=""):
        """Third-person death camera showing the killer's kill animation."""
        self.state = "killcam"
        self._killcam_timer = 4.0
        self._killcam_cause = cause
        mouse.locked = False
        self.hud.enabled = False

        # Spawn player body at death position
        si = SURVIVORS[self.selected_survivor]
        self._killcam_model = HumanModel(
            body_c=si["body"], shirt_c=si["shirt"], skin_c=si["skin"],
            hat_color=si.get("hat_color"), position=self.player_pos)
        # Make body fall over
        self._killcam_model.animate_rotation(Vec3(90, 0, random.uniform(-30,30)), duration=.8)
        self._killcam_model.animate_position(
            self.player_pos + Vec3(0, -.5, 0), duration=.8)

        # Kill FX — red slash marks, sparks, shockwave
        self._killcam_fx = []
        ki = KILLERS.get(self.current_killer_type, {})
        ec = ki.get("eye_color", _rgb(255,0,0))
        # Shockwave ring
        ring = Entity(model="sphere", color=ec, scale=.5, position=self.player_pos + Vec3(0,.5,0),
                      alpha=.6, unlit=True)
        ring.animate_scale(12, duration=1.2)
        ring.animate_color(_rgba(int(ec.r*255), int(ec.g*255), int(ec.b*255), 0), duration=1.2)
        self._killcam_fx.append(ring)
        # Blood/red particles flying out
        for _ in range(20):
            p = Entity(model="cube", color=_rgb(200,0,0), unlit=True,
                       scale=random.uniform(.08,.25), position=self.player_pos + Vec3(0,1,0))
            target = self.player_pos + Vec3(random.uniform(-4,4), random.uniform(1,5),
                                             random.uniform(-4,4))
            p.animate_position(target, duration=random.uniform(.5,1.2), curve=curve.out_expo)
            p.animate_scale(0, duration=1.2)
            p.animate_rotation(Vec3(random.uniform(-360,360),random.uniform(-360,360),0), duration=1.2)
            self._killcam_fx.append(p)
        # Killer slash lines (X pattern)
        for angle in [45, -45, 135, -135]:
            slash = Entity(model="cube", color=ec, unlit=True,
                           scale=(.05, .01, .01), position=self.player_pos + Vec3(0,1.5,0),
                           rotation=(0, 0, angle))
            slash.animate_scale(Vec3(4, .15, .1), duration=.3, curve=curve.out_expo)
            slash.animate_color(_rgba(int(ec.r*255), int(ec.g*255), int(ec.b*255), 0),
                                duration=1.5, delay=.5)
            self._killcam_fx.append(slash)
        # Ground crack
        crack = Entity(model="cube", color=_rgb(60,0,0), unlit=True,
                       scale=(0.1, .02, 0.1), position=self.player_pos + Vec3(0,.02,0))
        crack.animate_scale(Vec3(6, .02, 6), duration=.6, curve=curve.out_expo)
        self._killcam_fx.append(crack)

        # Camera shake
        camera.shake(duration=1, magnitude=4)

        # Fade overlay
        self.scare_overlay.enabled = True
        self.scare_overlay.color = _rgba(0, 0, 0, 0)
        self.scare_overlay.animate_color(_rgba(0, 0, 0, 200), duration=3.5)

    def _update_killcam(self, dt):
        """Orbit camera around death scene."""
        self._killcam_timer -= dt
        # Orbit camera around the death position
        t = (4.0 - self._killcam_timer)  # time elapsed
        orbit_angle = t * 40  # slow spin
        orbit_dist = 8
        cam_x = self.player_pos.x + math.sin(math.radians(orbit_angle)) * orbit_dist
        cam_z = self.player_pos.z + math.cos(math.radians(orbit_angle)) * orbit_dist
        cam_y = self.player_pos.y + 4 + t * 0.5  # slowly rise
        camera.position = lerp(camera.position, Vec3(cam_x, cam_y, cam_z), dt * 4)
        # Look at death spot
        look_target = self.player_pos + Vec3(0, 1, 0)
        dx = look_target.x - camera.x
        dz = look_target.z - camera.z
        dy = look_target.y - camera.y
        yaw = math.degrees(math.atan2(dx, dz))
        pitch = math.degrees(math.atan2(-dy, math.sqrt(dx*dx + dz*dz)))
        camera.rotation = Vec3(pitch, yaw, 0)

        if self._killcam_timer <= 0:
            # Cleanup killcam
            if self._killcam_model:
                destroy(self._killcam_model); self._killcam_model = None
            for fx in self._killcam_fx:
                if fx: destroy(fx)
            self._killcam_fx = []
            self.scare_overlay.enabled = False
            self._show_death(self._killcam_cause)

    # ── JUMP SCARE (kept for other uses) ──────────────────────────────────
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

        if stype == "builderman":
            # Rookie — Sprint Burst: brief speed boost
            self.stamina = min(MAX_STAMINA, self.stamina + 50)
            self._add_event("Sprint Burst! Quick speed boost!")
            particles(self.player_pos+Vec3(0,.5,0), _rgb(150,200,255), 6)
        elif stype == "guest1337":
            # Specter — Radar Ping
            if self.killer:
                d = self.killer.pos - self.player_pos; dx, dz = d.x, d.z
                if abs(dx) > abs(dz): dir_str = "EAST" if dx > 0 else "WEST"
                else: dir_str = "NORTH" if dz > 0 else "SOUTH"
                dist = int(distance(self.player_pos, self.killer.pos))
                self._add_event(f"Radar Ping: Killer is {dir_str}, ~{dist}m away!")
                particles(self.player_pos+Vec3(0,2,0), _rgb(100,200,255), 10)
        elif stype == "veronica":
            # Blaze — Adrenaline Rush
            self.stamina = MAX_STAMINA
            self._add_event("Adrenaline Rush! Full sprint!")
            particles(self.player_pos+Vec3(0,1,0), _rgb(255,100,50), 10)
        elif stype == "taph":
            # Bomber — Bomb
            b = Entity(model="sphere", color=_rgb(60,60,60), scale=.4,
                       position=self.player_pos+Vec3(0,.3,0))
            Entity(parent=b, model="cube", color=_rgb(200,100,30), scale=(.08,.5,.08),
                   position=(0,.6,0))
            Entity(parent=b, model="sphere", color=_rgb(255,200,50), unlit=True,
                   scale=.15, position=(0,.9,0))
            b._life = 8.0; b._explode_range = 7.0; b._type = "bomb"
            if not hasattr(self, '_player_turrets'): self._player_turrets = []
            self._player_turrets.append(b)
            particles(self.player_pos+Vec3(0,1,0), _rgb(255,150,50), 8)
            self._add_event("Bomb planted! Stuns killer for 4s on contact!")
        elif stype == "noob":
            # Rookie(Noob) — Shield
            self.shielded = True; self.shield_timer = 5
            self._add_event("Shield! Blocking next hit for 5s!")
            ring = Entity(model="sphere", color=_rgba(255,220,50,80), scale=1,
                          position=self.player_pos+Vec3(0,1,0))
            ring.animate_scale(3, duration=.5); ring.animate_color(_rgba(255,220,50,0), duration=1.5)
            destroy(ring, delay=1.6)
        elif stype == "bacon":
            # Flicker — Flashbang
            if self.killer and distance(self.player_pos, self.killer.pos) < 12:
                self.killer.stun(3)
                particles(self.player_pos+Vec3(0,1.5,0), _rgb(255,255,200), 12)
                # Flash effect
                boom = Entity(model="sphere", color=_rgba(255,255,255,200), scale=.5,
                              position=self.player_pos+Vec3(0,1.5,0), unlit=True)
                boom.animate_scale(8, duration=.3); boom.animate_color(_rgba(255,255,255,0), duration=.5)
                destroy(boom, delay=.6)
                self._add_event("Flashbang! Killer stunned for 3s!")
            else:
                self._add_event("Flashbang! (Killer too far)")
                self.ability_cooldown = 5
        elif stype == "shadow":
            # Shade — Vanish
            self.invisible = True; self.invis_timer = 3
            particles(self.player_pos+Vec3(0,1,0), _rgb(80,80,120), 8)
            self._add_event("Vanish! Invisible for 3s!")
        elif stype == "captain":
            # Medic — Heal Pulse
            self.stamina = MAX_STAMINA
            ring = Entity(model="sphere", color=_rgba(50,255,100,80), scale=.5,
                          position=self.player_pos+Vec3(0,.5,0))
            ring.animate_scale(5, duration=.8); ring.animate_color(_rgba(50,255,100,0), duration=1)
            destroy(ring, delay=1.1)
            self._add_event("Heal Pulse! Stamina restored!")
        elif stype == "hacker":
            # Cipher — Overclock: instant gen repair
            nearest_gen = None; nd = 5.0
            if hasattr(self, 'generators'):
                for g in self.generators:
                    if g._repaired: continue
                    d = distance(self.player_pos, g.position)
                    if d < nd: nd = d; nearest_gen = g
            if nearest_gen:
                nearest_gen._repaired = True
                nearest_gen._light.color = _rgb(50,255,100)
                self.gens_repaired += 1
                self.save["malice"] = self.save.get("malice",0) + 5
                self.save["coins"] += 10; save_data(self.save)
                particles(nearest_gen.position+Vec3(0,1,0), _rgb(0,255,200), 12)
                self._add_event(f"Overclock! Gen instant-repaired! ({self.gens_repaired}/{self.gens_total})")
                if self.gens_repaired >= self.gens_total:
                    self._add_event("ALL GENERATORS REPAIRED! Get to the EXIT!")
            else:
                self._add_event("Overclock! (No gen nearby)")
                self.ability_cooldown = 5
        elif stype == "athlete":
            # Dash — Burst: double speed 3s
            self.stamina = MAX_STAMINA
            particles(self.player_pos+Vec3(0,.5,0), _rgb(100,150,255), 10)
            self._add_event("Burst! Double speed for 3s!")
        elif stype == "scout2":
            # Tracker — Mark: reveal killer
            if self.killer:
                d = self.killer.pos - self.player_pos; dx, dz = d.x, d.z
                if abs(dx) > abs(dz): dir_str = "EAST" if dx > 0 else "WEST"
                else: dir_str = "NORTH" if dz > 0 else "SOUTH"
                dist = int(distance(self.player_pos, self.killer.pos))
                self._add_event(f"Mark! Killer is {dir_str}, ~{dist}m! Tracked for 5s!")
                particles(self.player_pos+Vec3(0,2,0), _rgb(80,200,80), 10)
        elif stype == "tank2":
            # Breaker — Iron Wall: block next 2 hits
            self.shielded = True; self.shield_timer = 6
            self._add_event("Iron Wall! Blocking hits for 6s!")
            ring = Entity(model="sphere", color=_rgba(200,150,50,100), scale=1.5,
                          position=self.player_pos+Vec3(0,1,0))
            ring.animate_scale(4, duration=.5); ring.animate_color(_rgba(200,150,50,0), duration=2)
            destroy(ring, delay=2.1)

    def _use_ability2(self):
        """Use the second ability slot."""
        if not hasattr(self, 'ability2_cooldown'): self.ability2_cooldown = 0
        if self.ability2_cooldown > 0: return
        si = SURVIVORS[self.selected_survivor]
        a2 = si.get("ability2_name", "")
        if not a2: return
        self.ability2_cooldown = si.get("ability2_cooldown", 30)
        stype = self.selected_survivor

        if stype == "builderman":
            # Quick Fix — faster gen repair
            self._add_event("Quick Fix! Gen repair speed boosted!")
        elif stype == "guest1337":
            # Sixth Sense — see killer through walls (just event msg, arrow already does it)
            self._add_event("Sixth Sense! Killer highlighted!")
        elif stype == "veronica":
            # Afterburner — stun killer if close
            if self.killer and distance(self.player_pos, self.killer.pos) < 8:
                self.killer.stun(2)
                particles(self.player_pos+Vec3(0,.5,0), _rgb(255,150,0), 10)
                self._add_event("Afterburner! Fire trail stuns killer!")
            else:
                self._add_event("Afterburner! (Killer not close enough)")
                self.ability2_cooldown = 5
        elif stype == "taph":
            # Decoy — place fake survivor
            d = Entity(model="cube", color=_rgb(100,100,80), scale=(.5,1.8,.4),
                       position=self.player_pos+Vec3(0,.9,0))
            Entity(parent=d, model="cube", color=_rgb(200,180,150), scale=(.8,.5,.8),
                   position=(0,.7,0))
            d._life = 10.0; d._type = "decoy"
            if not hasattr(self, '_player_turrets'): self._player_turrets = []
            self._player_turrets.append(d)
            self._add_event("Decoy placed! Distracting killer!")
        elif stype == "noob":
            # Last Stand — invincibility at 1HP
            if getattr(self, 'health', 3) <= 1:
                self.shielded = True; self.shield_timer = 3
                self._add_event("Last Stand! 3s invincibility!")
            else:
                self._add_event("Last Stand! (Only works at 1 HP)")
                self.ability2_cooldown = 5
        elif stype == "bacon":
            # Lucky Escape — teleport away
            angle = random.uniform(0, math.pi*2)
            tp = self.player_pos + Vec3(math.cos(angle)*10, 0, math.sin(angle)*10)
            mx = int((tp.x + len(MAP[0])*ROOM/2)/ROOM)
            mz = int((tp.z + len(MAP)*ROOM/2)/ROOM)
            if 0<=mz<len(MAP) and 0<=mx<len(MAP[0]) and MAP[mz][mx]!=1:
                self.player_pos = tp
                particles(self.player_pos+Vec3(0,1,0), _rgb(255,215,0), 12)
                self._add_event("Lucky Escape! Teleported!")
            else:
                self._add_event("Lucky Escape! (Blocked)")
                self.ability2_cooldown = 5
        elif stype == "shadow":
            # Shadow Step — silent for 5s (same as invisible but less)
            self.invisible = True; self.invis_timer = 2
            self._add_event("Shadow Step! Silent movement!")
        elif stype == "captain":
            # Triage — heal 1 HP
            if getattr(self, 'health', 3) < getattr(self, 'max_health', 3):
                self.health += 1
                self._add_event(f"Triage! Healed to {self.health}/{self.max_health} HP!")
                particles(self.player_pos+Vec3(0,1,0), _rgb(50,255,100), 8)
            else:
                self._add_event("Triage! (Already full HP)")
                self.ability2_cooldown = 5
        elif stype == "hacker":
            # EMP — stun killer
            if self.killer:
                self.killer.stun(4)
                self._add_event("EMP! Killer disabled for 4s!")
                particles(self.player_pos+Vec3(0,2,0), _rgb(0,255,255), 15)
            else:
                self._add_event("EMP! (No target)")
        elif stype == "athlete":
            # Slide — brief invincibility
            self.shielded = True; self.shield_timer = 1
            self.stamina = MAX_STAMINA
            self._add_event("Slide! 1s invincibility!")
        elif stype == "scout2":
            # Trap — stun killer if close
            t = Entity(model="cube", color=_rgb(100,80,40), scale=(.5,.1,.5),
                       position=self.player_pos+Vec3(0,.05,0))
            t._life = 20.0; t._stun_range = 3.0; t._type = "turret"
            if not hasattr(self, '_player_turrets'): self._player_turrets = []
            self._player_turrets.append(t)
            self._add_event("Trap placed! Slows killer on contact!")
        elif stype == "tank2":
            # War Cry — knockback
            if self.killer and distance(self.player_pos, self.killer.pos) < 12:
                d = self.killer.pos - self.player_pos
                if d.length() > 0.1:
                    self.killer.pos += d.normalized() * 10
                    if self.killer.model: self.killer.model.position = self.killer.pos
                self.killer.stun(2)
                camera.shake(duration=.3, magnitude=2)
                self._add_event("WAR CRY! Killer knocked back!")
            else:
                self._add_event("War Cry! (Killer too far)")
                self.ability2_cooldown = 5

    # ── PLAYER TURRETS/BOMBS CHECK ────────────────────────────────────────
    def _check_player_turrets(self, dt):
        if not hasattr(self, '_player_turrets'): self._player_turrets = []
        to_remove = []
        kp = self.killer.pos if self.killer else Vec3(0,0,0)
        for ent in self._player_turrets:
            if not ent: to_remove.append(ent); continue
            ent._life -= dt
            if ent._life <= 0: destroy(ent); to_remove.append(ent); continue
            dk = distance(ent.position, kp)
            etype = getattr(ent, '_type', '')
            if etype == "turret":
                ent.rotation_y += dt * 90
                if dk < ent._stun_range and self.killer and not self.killer.stunned:
                    self.killer.stun(3)
                    particles(ent.position+Vec3(0,1,0), _rgb(50,150,255), 10)
                    self._add_event("Turret stunned the killer!")
                    ent._life = 0
            elif etype == "bomb":
                if dk < ent._explode_range:
                    if self.killer: self.killer.stun(4)
                    particles(ent.position+Vec3(0,1,0), _rgb(255,100,0), 20)
                    boom = Entity(model="sphere", color=_rgba(255,100,0,180), scale=.5,
                                  position=ent.position)
                    boom.animate_scale(8, duration=.4); boom.animate_color(_rgba(255,50,0,0), duration=.6)
                    destroy(boom, delay=.65)
                    self._add_event("BOOM! Killer stunned for 4s!")
                    ent._life = 0
        for e in to_remove:
            if e in self._player_turrets: self._player_turrets.remove(e)

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

        # Gravity / rooftop standing
        on_ground = True
        target_y = 0  # default ground
        if hasattr(self, '_rooftops'):
            for (rpos, rhw, ry) in self._rooftops:
                dx = abs(self.player_pos.x - rpos.x)
                dz = abs(self.player_pos.z - rpos.z)
                if dx < rhw and dz < rhw:
                    # Player is above this rooftop
                    if self.player_pos.y >= ry - 0.5:
                        target_y = max(target_y, ry)
        self.player_pos.y = lerp(self.player_pos.y, target_y, dt * 12)

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

        # Health bar
        mh = getattr(self, 'max_health', 3)
        hp = getattr(self, 'health', 3)
        hf = hp / mh if mh > 0 else 0
        self.health_bar.scale_x = .15 * hf
        self.health_bar.color = _rgb(255,50,50) if hf <= .34 else _rgb(255,180,50) if hf <= .67 else _rgb(50,255,80)
        self.health_txt.text = f"{hp}/{mh}"
        # Flash health bar when low
        if hp == 1 and hasattr(self, 'hit_cooldown') and self.hit_cooldown > 0:
            self.health_bar.color = _rgb(255, int(abs(math.sin(self.game_time*8))*255), 50)

        self.round_label.text = f"Round {self.round_num}"
        ki = KILLERS.get(self.current_killer_type,{})
        self.killer_label.text = f"Killer: {ki.get('name','???')}"
        rt = max(0, int(self.round_timer))
        self.timer_txt.text = f"{rt//60}:{rt%60:02d}"
        self.timer_txt.color = _rgb(255,80,80) if rt<30 else _rgb(200,200,200)
        alive_npcs = sum(1 for n in self.npcs if n.alive)
        self.alive_txt.text = f"Alive: {1+alive_npcs}" if self.alive else f"Alive: {alive_npcs}"
        self.coin_txt.text = f"Coins: {self.save['coins']}"
        # Generator counter
        gr = getattr(self, 'gens_repaired', 0)
        gt = getattr(self, 'gens_total', GENS_NEEDED)
        self.gen_txt.text = f"Gens: {gr}/{gt}"
        if gr >= gt:
            self.gen_txt.color = _rgb(50,255,50)
        else:
            self.gen_txt.color = _rgb(100,255,200)
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

        # Ability 2 sidebar
        a2cd = getattr(self, 'ability2_cooldown', 0)
        a2max = si.get("ability2_cooldown", 30)
        if a2cd > 0:
            self.ability2_cd_txt.text = f"{int(a2cd)}s"
            self.ability2_cd_txt.color = _rgb(255,100,100)
            self.ability2_icon.color = _rgb(100,50,50)
            frac2 = a2cd / a2max if a2max > 0 else 0
            self.ability2_cd_bar.scale_x = .18 * frac2
            self.ability2_cd_bar.color = _rgba(0,0,0,150)
        else:
            self.ability2_cd_txt.text = "READY"
            self.ability2_cd_txt.color = _rgb(100,255,100)
            self.ability2_icon.color = _rgb(255,180,50)
            self.ability2_cd_bar.scale_x = 0

        # Danger + Chase indicator
        if self.killer:
            dk = distance(self.player_pos, self.killer.pos)
            chasing = self.killer.state == "chase" and dk < 30
            if chasing:
                self._chase_pulse += time.dt * 6
                pulse = (math.sin(self._chase_pulse) + 1) * 0.5  # 0-1
                alpha = int(80 + pulse * 150)
                border_c = _rgba(255, 0, 0, alpha)
                self.chase_border_top.color = border_c
                self.chase_border_bot.color = border_c
                self.chase_border_left.color = border_c
                self.chase_border_right.color = border_c
                # Pulsing border thickness
                thick = .012 + pulse * .008
                self.chase_border_top.scale = Vec2(2, thick)
                self.chase_border_bot.scale = Vec2(2, thick)
                self.chase_border_left.scale = Vec2(thick * 0.6, 1)
                self.chase_border_right.scale = Vec2(thick * 0.6, 1)
                self.chase_txt.text = "BEING CHASED!"
                self.chase_txt.color = _rgba(255, int(50 + pulse * 60), int(50 + pulse * 60), 255)
                self.vignette.color = _rgba(int(50 + pulse * 40), 0, 0, int(60 + pulse * 60))
                if dk < 6:
                    self.danger_txt.text = "!! RUN !!"; self.danger_txt.color = _rgb(255,0,0)
                    self.danger_txt.scale = 2.5
                elif dk < 12:
                    self.danger_txt.text = "!! DANGER !!"; self.danger_txt.color = _rgb(255,50,50)
                    self.danger_txt.scale = 2
                else:
                    self.danger_txt.text = "!! CHASING YOU !!"; self.danger_txt.color = _rgb(255,100,80)
                    self.danger_txt.scale = 1.5
            else:
                no_chase = _rgba(255, 0, 0, 0)
                self.chase_border_top.color = no_chase
                self.chase_border_bot.color = no_chase
                self.chase_border_left.color = no_chase
                self.chase_border_right.color = no_chase
                self.chase_txt.text = ""
                self._chase_pulse = 0
                if dk < 8:
                    self.danger_txt.text = "...something is near..."
                    self.danger_txt.color = _rgb(200,100,100); self.danger_txt.scale = 1.2
                else:
                    self.danger_txt.text = ""
                self.vignette.color = _rgba(0,0,0,60)
        # Killer direction indicator — DISABLED (killer is silent/dark)
        self.killer_arrow.enabled = False
        self.killer_dist_txt.enabled = False

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
        if getattr(self, 'hiding', False):
            self.sprint_txt.text = "HIDDEN"
            self.sprint_txt.color = _rgb(80,200,80)

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
            if self.gens_repaired >= self.gens_total:
                self.interact_txt.text = "[E] ESCAPE THROUGH EXIT"
                return True
            else:
                need = self.gens_total - self.gens_repaired
                self.interact_txt.text = f"EXIT LOCKED — Repair {need} more generators!"
        return False

    # ── GENERATOR CHECK ──────────────────────────────────────────────────
    def _check_gens(self, dt):
        """Check if player is near a generator — starts puzzle on E press."""
        if self._puzzle_active:
            return  # puzzle handles itself via input
        nearest_gen = None
        nearest_dist = 3.5
        for g in self.generators:
            if g._repaired: continue
            d = distance(self.player_pos, g.position)
            if d < nearest_dist:
                nearest_dist = d; nearest_gen = g
        if nearest_gen and not self.interact_txt.text:
            self.interact_txt.text = "[E] Start Repair Puzzle"

    def _start_gen_puzzle(self):
        """Start a key-sequence puzzle to repair the generator."""
        nearest_gen = None; nd = 3.5
        for g in self.generators:
            if g._repaired: continue
            d = distance(self.player_pos, g.position)
            if d < nd: nd = d; nearest_gen = g
        if not nearest_gen: return
        self._puzzle_active = True
        self._puzzle_gen = nearest_gen
        # Generate random key sequence (4-6 keys)
        seq_len = random.randint(4, 6)
        possible = ['q','w','e','r','a','s','d','f']
        self._puzzle_sequence = [random.choice(possible) for _ in range(seq_len)]
        self._puzzle_index = 0
        self.puzzle_root.enabled = True
        self._update_puzzle_display()
        self._add_event("Repair puzzle started! Press the keys in order!")

    def _update_puzzle_display(self):
        """Update the puzzle UI to show which keys to press."""
        display = ""
        for i, k in enumerate(self._puzzle_sequence):
            if i < self._puzzle_index:
                display += f"[{k.upper()}] "  # completed — green bracket
            elif i == self._puzzle_index:
                display += f">{k.upper()}< "  # current — highlighted
            else:
                display += f" {k.upper()}  "  # upcoming
        self.puzzle_keys_txt.text = display
        # Color the text based on progress
        frac = self._puzzle_index / len(self._puzzle_sequence) if self._puzzle_sequence else 0
        r = int(255 * (1 - frac))
        g = int(255 * frac)
        self.puzzle_keys_txt.color = _rgb(r, g, 100)
        # Progress bar reuse
        self.gen_progress_bg.enabled = True
        self.gen_progress_bar.enabled = True
        self.gen_progress_bar.scale_x = .2 * frac

    def _puzzle_input(self, key):
        """Handle key press during gen puzzle."""
        if not self._puzzle_active: return False
        if key == "escape":
            # Cancel puzzle
            self._puzzle_active = False
            self.puzzle_root.enabled = False
            self.gen_progress_bg.enabled = False
            self.gen_progress_bar.enabled = False
            self._puzzle_gen = None
            self._add_event("Repair cancelled!")
            return True
        expected = self._puzzle_sequence[self._puzzle_index]
        if key == expected:
            self._puzzle_index += 1
            # Success flash
            particles(self.player_pos + Vec3(0, 1, 0), _rgb(100, 255, 200), 3)
            if self._puzzle_index >= len(self._puzzle_sequence):
                # Puzzle complete — repair gen!
                self._puzzle_active = False
                self.puzzle_root.enabled = False
                self.gen_progress_bg.enabled = False
                self.gen_progress_bar.enabled = False
                g = self._puzzle_gen
                if g:
                    g._repaired = True
                    g._light.color = _rgb(50, 255, 100)
                    self.gens_repaired += 1
                    self.save["malice"] = self.save.get("malice", 0) + 5
                    self.save["coins"] += 10
                    save_data(self.save)
                    particles(g.position + Vec3(0, 1, 0), _rgb(100, 255, 200), 12)
                    self._add_event(f"PUZZLE COMPLETE! Gen repaired! ({self.gens_repaired}/{self.gens_total})")
                    if self.gens_repaired >= self.gens_total:
                        self._add_event("ALL GENERATORS REPAIRED! Get to the EXIT!")
                self._puzzle_gen = None
            else:
                self._update_puzzle_display()
            return True
        elif key in ['q','w','e','r','a','s','d','f']:
            # Wrong key — reset progress
            self._puzzle_index = 0
            self._update_puzzle_display()
            camera.shake(duration=.15, magnitude=1)
            self.puzzle_hint.text = "WRONG! Start over!"
            self.puzzle_hint.color = _rgb(255, 80, 80)
            invoke(setattr, self.puzzle_hint, 'text', "Press the keys in order!", delay=1)
            invoke(setattr, self.puzzle_hint, 'color', _rgb(150, 150, 160), delay=1)
            return True
        return False

    # ── HIDING ─────────────────────────────────────────────────────────
    def _check_hiding(self):
        """Crouch near a crate/locker to hide — killer can't detect you."""
        if not self.crouching:
            self.hiding = False
            return
        if not hasattr(self, '_hide_spots'):
            self.hiding = False
            return
        for hs in self._hide_spots:
            if distance(self.player_pos, hs) < 2.5:
                self.hiding = True
                return
        self.hiding = False

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

        if self.state == "killcam":
            self._update_killcam(dt)
            return

        if self.state == "lobby":
            self._update_lobby(dt)
            return

        if self.state != "playing": return

        # Hit invincibility cooldown
        if hasattr(self, 'hit_cooldown') and self.hit_cooldown > 0:
            self.hit_cooldown -= dt

        self.game_time += dt
        self.round_timer -= dt
        if self.ability_cooldown > 0: self.ability_cooldown -= dt
        if hasattr(self, 'ability2_cooldown') and self.ability2_cooldown > 0:
            self.ability2_cooldown -= dt

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
        self._check_player_turrets(dt)

        # ── KILLER MODE gameplay ──
        if getattr(self, '_killer_mode', False):
            ki = KILLERS.get(self.current_killer_type, {})
            kill_range = ki.get('kill_range', 2.5)
            # Check NPC kills
            for n in self.npcs:
                if not n.alive: continue
                d = distance(self.player_pos, n.pos)
                if d < kill_range:
                    n.alive = False
                    if n.model:
                        n.model.animate_scale(0, duration=.4)
                        destroy(n.model, delay=.5); n.model = None
                    n._cleanup_abilities()
                    self._kills_this_round = getattr(self, '_kills_this_round', 0) + 1
                    self.save['malice'] = self.save.get('malice', 0) + 15
                    self.save['coins'] = self.save.get('coins', 0) + 10
                    save_data(self.save)
                    self._add_event(f"Killed {n.name}! +15 malice +10 coins")
                    particles(n.pos + Vec3(0,1,0), _rgb(255,0,0), 12)
                    camera.shake(duration=.2, magnitude=1)
            # NPC patrol (they run from player in killer mode)
            for n in self.npcs:
                if not n.alive: continue
                n.update(dt, Vec3(9999,0,9999), self.player_pos, None)  # player IS the threat
            # Check if all NPCs dead
            alive_npcs = sum(1 for n in self.npcs if n.alive)
            if alive_npcs == 0:
                earned_m = getattr(self, '_kills_this_round', 0) * 15 + 50
                self.save['malice'] = self.save.get('malice', 0) + 50  # bonus
                save_data(self.save)
                self._hide_all()
                self.state = "won"
                self.win_root.enabled = True
                self.win_title.text = "ALL ELIMINATED!"
                self.win_title.color = _rgb(200,50,255)
                self.win_stats.text = f"Kills: {getattr(self,'_kills_this_round',0)} | Round {self.round_num}"
                self.win_coins.text = f"+{earned_m} malice (total: {self.save.get('malice',0)})"
                mouse.locked = False
                return
            # Timer — if time runs out in killer mode, survivors win
            if self.round_timer <= 0:
                self._hide_all()
                self.state = "death"
                self.death_root.enabled = True
                self.death_title.text = "TIME'S UP"
                self.death_title.color = _rgb(200,100,100)
                self.death_msg.text = f"{alive_npcs} survivors escaped!"
                self.death_stats.text = f"Kills: {getattr(self,'_kills_this_round',0)}"
                mouse.locked = False
                return
            self._check_exit()
            self._update_hud()
            return

        # ── SURVIVOR MODE gameplay ──
        self._check_gens(dt)
        self._check_hiding()

        # Killer
        if self.killer and self.alive:
            npc_pos = [n.pos for n in self.npcs if n.alive]
            player_hidden = self.invisible or self.hiding
            caught = self.killer.update(dt, self.player_pos, player_hidden, npc_pos)
            # Check 1x1x1x1 glitch ability
            if self.killer.type == "1x1x1x1" and self.killer.ability_duration > 0:
                self.glitch_timer = max(self.glitch_timer, self.killer.ability_duration)
            if caught:
                self._player_hit()
                if not self.alive:
                    return
            # Check ranged projectile hit
            if hasattr(self.killer, '_ranged_hit') and self.killer._ranged_hit:
                self.killer._ranged_hit = False
                self._player_hit()
                if not self.alive:
                    return

        # NPCs — pass killer ref so they can use abilities
        kp = self.killer.pos if self.killer else Vec3(0,0,0)
        for n in self.npcs:
            result = n.update(dt, self.player_pos, kp, self.killer)
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
            # Puzzle input takes priority
            if getattr(self, '_puzzle_active', False):
                if self._puzzle_input(key):
                    return
            if key == "escape":
                if getattr(self, '_puzzle_active', False):
                    self._puzzle_input("escape")
                else:
                    self.state = "paused"
                    self.pause_root.enabled = True
                    mouse.locked = False
            if key == "f": 
                if self.battery > 0 or not self.flash_on:
                    self.flash_on = not self.flash_on
            if key == "1":
                self._use_ability()
            if key == "2":
                self._use_ability2()
            if key == "e":
                # Start gen puzzle if near a gen
                if not getattr(self, '_puzzle_active', False):
                    nearest_gen = None; nd = 3.5
                    for g in getattr(self, 'generators', []):
                        if g._repaired: continue
                        d = distance(self.player_pos, g.position)
                        if d < nd: nd = d; nearest_gen = g
                    if nearest_gen:
                        self._start_gen_puzzle()
                        return
                it = self._check_items()
                if it:
                    self._pickup(it)
                elif self._check_exit():
                    self._player_escaped()
        elif self.state == "lobby":
            # Lobby keybinds + walk around
            if key == "escape":
                self._show_menu()
            elif key == "1":
                self.quests_root.enabled = not self.quests_root.enabled
                self.shop_root.enabled = False; self.spec_root.enabled = False
                self._spec_active = False
            elif key == "2":
                self.shop_root.enabled = not self.shop_root.enabled
                self.shop_coins_label.text = f"Coins: {self.save['coins']}"
                self.shop_malice_label.text = f"Malice: {self.save.get('malice',0)}"
                self.shop_msg.text = ""
                self.quests_root.enabled = False; self.spec_root.enabled = False
                self._spec_active = False
            elif key == "3":
                if self._spec_active:
                    self._spec_active = False; self.spec_root.enabled = False
                    self.death_root.enabled = True; mouse.locked = True
                else:
                    self._start_spectate()
                self.quests_root.enabled = False; self.shop_root.enabled = False
            elif key == "e":
                # Check proximity to next round pad
                if hasattr(self, '_lobby_next_pos') and distance(self.player_pos, self._lobby_next_pos) < 5:
                    self._cleanup_lobby()
                    self._next_round()
            elif key == "right arrow" and self._spec_active:
                self._spec_index += 1; self._update_spec_cam()
            elif key == "left arrow" and self._spec_active:
                self._spec_index -= 1; self._update_spec_cam()
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
