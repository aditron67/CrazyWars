"""Generate procedural face/mask textures for Horror Survival characters."""
from PIL import Image, ImageDraw
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "textures")
os.makedirs(OUT, exist_ok=True)

def make_face(name, skin=(245,205,170), eye=(40,30,20), mouth=(150,70,70),
              brow=(50,40,30), scar=False, mask=None, white_face=False):
    """Generate a 64x64 face texture."""
    sz = 64
    img = Image.new("RGBA", (sz,sz), (0,0,0,0))
    d = ImageDraw.Draw(img)
    # Face fill
    fc = (255,255,255) if white_face else skin
    d.rectangle([0,0,sz-1,sz-1], fill=fc)
    if mask:
        # Full mask overlay
        d.rectangle([0,0,sz-1,sz-1], fill=mask)
        # Eye holes
        d.ellipse([14,18,24,28], fill=(0,0,0))
        d.ellipse([40,18,50,28], fill=(0,0,0))
        # Red glow in eye holes
        d.ellipse([16,20,22,26], fill=eye)
        d.ellipse([42,20,48,26], fill=eye)
    else:
        # Eyes — white + iris + pupil
        for ex in [16, 40]:
            d.ellipse([ex,20,ex+10,30], fill=(255,255,255))  # white
            d.ellipse([ex+2,22,ex+8,28], fill=eye)  # iris
            d.ellipse([ex+4,24,ex+6,26], fill=(0,0,0))  # pupil
        # Eyebrows
        d.rectangle([14,16,26,19], fill=brow)
        d.rectangle([38,16,50,19], fill=brow)
        # Nose
        d.rectangle([29,28,35,36], fill=(max(0,fc[0]-15),max(0,fc[1]-15),max(0,fc[2]-10)))
        # Mouth
        d.ellipse([22,40,42,50], fill=mouth)
        d.rectangle([22,40,42,44], fill=fc)  # upper lip cutoff
    # Scars
    if scar:
        d.line([10,15,30,45], fill=(180,40,40), width=2)
        d.line([50,10,35,50], fill=(160,30,30), width=1)
    if white_face:
        # Carved smile for "The Carved"
        d.arc([15,35,49,55], 0, 180, fill=(200,0,0), width=2)
        d.line([15,44,20,40], fill=(200,0,0), width=2)
        d.line([44,40,49,44], fill=(200,0,0), width=2)
    img.save(os.path.join(OUT, f"{name}.png"))
    return os.path.join(OUT, f"{name}.png")

def make_wall_tex(name, base=(50,50,58), detail=(40,42,48)):
    """Generate a brick-like wall texture."""
    sz = 64
    img = Image.new("RGB", (sz,sz), base)
    d = ImageDraw.Draw(img)
    # Brick pattern
    for y in range(0, sz, 8):
        offset = 16 if (y//8) % 2 else 0
        for x in range(-16, sz+16, 32):
            bx = x + offset
            bc = (base[0]+random_v(), base[1]+random_v(), base[2]+random_v())
            d.rectangle([bx+1, y+1, bx+30, y+6], fill=bc)
    # Mortar lines
    for y in range(0, sz, 8):
        d.line([0,y,sz,y], fill=detail, width=1)
    for y in range(0, sz, 8):
        offset = 16 if (y//8) % 2 else 0
        for x in range(-16, sz+16, 32):
            bx = x + offset
            d.line([bx,y,bx,y+8], fill=detail, width=1)
    img.save(os.path.join(OUT, f"{name}.png"))

def make_floor_tex(name, base=(35,35,40)):
    """Generate a tile/concrete floor texture."""
    sz = 64
    img = Image.new("RGB", (sz,sz), base)
    d = ImageDraw.Draw(img)
    # Tile grid
    for x in range(0, sz, 16):
        d.line([x,0,x,sz], fill=(base[0]-8,base[1]-8,base[2]-8), width=1)
    for y in range(0, sz, 16):
        d.line([0,y,sz,y], fill=(base[0]-8,base[1]-8,base[2]-8), width=1)
    # Random dirt spots
    import random
    for _ in range(8):
        sx = random.randint(0,sz-4)
        sy = random.randint(0,sz-4)
        sc = (base[0]-15, base[1]-12, base[2]-10)
        d.ellipse([sx,sy,sx+random.randint(2,6),sy+random.randint(2,6)], fill=sc)
    img.save(os.path.join(OUT, f"{name}.png"))

import random
def random_v():
    return random.randint(-8,8)

if __name__ == "__main__":
    print("Generating textures...")
    # Killer faces
    make_face("faceless", skin=(20,20,20), eye=(255,255,255), mask=None,
              brow=(20,20,20), mouth=(20,20,20))  # blank face
    make_face("corner", skin=(40,35,35), eye=(255,200,0), brow=(30,25,25),
              mouth=(60,30,30))
    make_face("carved", white_face=True, eye=(0,0,0), brow=(200,200,200))
    make_face("masked", mask=(80,80,90), eye=(200,0,0))
    make_face("glitch", skin=(10,10,10), eye=(255,255,0), brow=(0,0,0),
              mouth=(0,0,0), scar=True)
    make_face("crawler", skin=(50,35,20), eye=(0,255,80), brow=(40,25,15),
              mouth=(80,40,20))
    make_face("phantom", skin=(60,60,80), eye=(150,0,255), brow=(50,50,70),
              mouth=(80,60,100))
    make_face("mimic", skin=(200,180,150), eye=(200,255,200), brow=(50,40,35),
              mouth=(150,100,80))
    make_face("warden", skin=(30,30,50), eye=(255,255,255), brow=(20,20,40),
              mouth=(40,40,60))

    # Survivor faces
    make_face("survivor_default", skin=(210,185,155))
    make_face("survivor_light", skin=(245,220,190))
    make_face("survivor_dark", skin=(160,120,80))
    make_face("survivor_pale", skin=(230,215,200))

    # Wall/floor textures
    make_wall_tex("wall_brick", base=(50,48,55))
    make_wall_tex("wall_dark", base=(35,33,40))
    make_floor_tex("floor_tile", base=(38,38,42))
    make_floor_tex("floor_dirt", base=(45,35,30))
    print(f"Done! Textures saved to {OUT}")
