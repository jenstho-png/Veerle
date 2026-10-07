"""Herovideo van de homepage: één film van ca. 14 seconden, 1920 x 1080, 24 fps, zonder geluid, in een lus.

Shots (allemaal in dezelfde filmlook: warme kleur, zachte contrastcurve, korrel, vignet):
 1. golven die over een breed zandstrand spoelen (echte opname, Mixkit 1921, vertraagd)
 2. drie boards met de draagtas van bovenaf (studiofoto), langzaam inzoomen, schaduw van palmbladeren die wiegen
 3. macro van het geweven label en de tegelstof: focus trekt van onscherp naar scherp, palmschaduw
 4. golven op het zand recht van boven (echte opname, Mixkit 1078, vertraagd)
 5. de rand van de tas over het board, langzaam inzoomen, palmschaduw; overvloeien naar shot 1 voor de lus
De tas komt uit onze eigen productbeelden, dus hij klopt precies met de shop.
Gebruik: python3 tools/video/hero_video.py  -> docs/video/tide-tode-hero.mp4 (+ -720.mp4)
"""
import pathlib, subprocess
import cv2
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
VID = pathlib.Path('/tmp/claude-0/-home-user-Veerle/e622134c-148a-50b2-bdf1-45d3e9d54d8e/scratchpad/vid')
PB = ROOT / 'docs' / 'producten' / 'beelden'
UIT = ROOT / 'docs' / 'video'
W, H, FPS = 1920, 1080, 24
OVER = 12                       # frames overvloeien (0,5 s)
RNG = np.random.default_rng(5)


def lees(pad):
    return cv2.cvtColor(cv2.imread(str(pad)), cv2.COLOR_BGR2RGB).astype(np.float32) / 255


def uitsnede(img, cx, cy, zoom):
    """Venster van W x H rond (cx, cy) in fracties, zoom 1 = zo groot mogelijk 16:9 venster."""
    h, w = img.shape[:2]
    vw = min(w, h * W / H) / zoom; vh = vw * H / W
    x0 = np.clip(cx * w - vw / 2, 0, w - vw); y0 = np.clip(cy * h - vh / 2, 0, h - vh)
    M = np.float32([[W / vw, 0, -x0 * W / vw], [0, H / vh, -y0 * H / vh]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)


def ease(t):
    return 0.5 - 0.5 * np.cos(np.pi * np.clip(t, 0, 1))


# ---------- palmschaduw: bladeren van een waaierpalm, wiegend in de wind ----------
def palmmasker(t, schaal=1.0, x0=0.2, y0=-0.15):
    m = np.zeros((H // 2, W // 2), np.float32)
    cx, cy = int(W / 2 * x0), int(H / 2 * y0)
    for i in range(14):
        hoek = np.radians(25 + i * 9 + 3.2 * np.sin(2 * np.pi * (t * 0.35 + i * 0.07)))
        lengte = (360 + 60 * np.sin(i * 1.7)) * schaal
        for j in range(26):
            f = j / 25
            px = cx + np.cos(hoek) * lengte * f + 6 * np.sin(2 * np.pi * (t * 0.5 + f))
            py = cy + np.sin(hoek) * lengte * f
            r = (1 - f) ** 0.6 * 22 * schaal + 3
            # blaadjes langs de nerf
            for zij in (-1, 1):
                bx = px + np.cos(hoek + zij * 1.2) * r * 1.6
                by = py + np.sin(hoek + zij * 1.2) * r * 1.6
                cv2.ellipse(m, (int(bx), int(by)), (int(r * 1.8), max(2, int(r * 0.45))), np.degrees(hoek + zij * 0.9), 0, 360, 1, -1, cv2.LINE_AA)
        cv2.line(m, (cx, cy), (int(cx + np.cos(hoek) * lengte), int(cy + np.sin(hoek) * lengte)), 1, 3, cv2.LINE_AA)
    m = cv2.resize(m, (W, H), interpolation=cv2.INTER_LINEAR)
    return cv2.GaussianBlur(m, (0, 0), 7)


def schaduw(img, t, sterkte=0.32, **kw):
    s = palmmasker(t, **kw)[..., None]
    koel = np.array([0.80, 0.86, 0.98], np.float32)       # schaduw op zand is iets blauwer
    return img * (1 - sterkte * s) * (1 - (1 - koel) * sterkte * 0.6 * s)


# ---------- filmlook ----------
VIG = None
def look(img, i):
    global VIG
    if VIG is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        VIG = (1 - 0.22 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) ** 1.2)[..., None]
    img = np.clip(img, 0, 1)
    img = img * np.array([1.045, 1.0, 0.93], np.float32)                     # warm
    g = img.mean(-1, keepdims=True); img = g + (img - g) * 0.9               # iets minder verzadigd
    img = 0.03 + 0.94 * (img + 0.12 * np.sin(np.pi * (img - 0.5)) * 0.5)     # zachte S-curve, opgetilde zwarten
    img = img * VIG
    korrel = RNG.normal(0, 0.016, (H // 2, W // 2)).astype(np.float32)
    img = img + cv2.resize(korrel, (W, H))[..., None]
    return np.clip(img, 0, 1)


# ---------- shots ----------
def stock(naam, start, duur, snelheid=0.6, zoom=1.04):
    cap = cv2.VideoCapture(str(VID / naam))
    bron_fps = cap.get(cv2.CAP_PROP_FPS)
    n = int(duur * FPS)
    cap.set(cv2.CAP_PROP_POS_MSEC, start * 1000)
    nodig = int(n * snelheid * bron_fps / FPS) + 3
    fr = []
    for _ in range(nodig):
        ok, f = cap.read()
        if not ok: break
        fr.append(cv2.cvtColor(f, cv2.COLOR_BGR2RGB).astype(np.float32) / 255)
    uit = []
    for k in range(n):
        p = k * snelheid * bron_fps / FPS
        a, b = int(p), min(int(p) + 1, len(fr) - 1); f = p - a
        beeld = fr[a] * (1 - f) + fr[b] * f                              # vertraging met overvloei tussen frames
        z = zoom + 0.03 * k / n
        uit.append(uitsnede(cv2.resize(beeld, (W, H)), 0.5, 0.5, z))
    return uit


def still(pad, duur, van, naar, palm=True, focus=None, **pk):
    img = lees(pad)
    n = int(duur * FPS); uit = []
    for k in range(n):
        t = ease(k / (n - 1))
        cx, cy, z = [a + (b - a) * t for a, b in zip(van, naar)]
        f = uitsnede(img, cx, cy, z)
        if focus:
            blur = focus * (1 - ease(min(1, k / (n * 0.55))))
            if blur > 0.2: f = cv2.GaussianBlur(f, (0, 0), blur)
        if palm: f = schaduw(f, k / FPS, **pk)
        uit.append(f)
    return uit


def plak(shots):
    film = shots[0]
    for s in shots[1:]:
        for i in range(OVER):
            a = (i + 1) / (OVER + 1)
            film[-OVER + i] = film[-OVER + i] * (1 - a) + s[i] * a
        film += s[OVER:]
    # lus: einde overvloeien in het begin
    for i in range(OVER):
        a = (i + 1) / (OVER + 1)
        film[-OVER + i] = film[-OVER + i] * (1 - a) + film[i] * a
    return film[:-OVER]


def schrijf(frames, pad, w, h, crf):
    p = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-vf', f'scale={w}:{h}:flags=lanczos', '-an', '-c:v', 'libx264', '-preset', 'slow', '-crf', str(crf),
                          '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(pad)], stdin=subprocess.PIPE)
    for f in frames:
        p.stdin.write((f * 255 + 0.5).astype(np.uint8).tobytes())
    p.stdin.close(); p.wait()


if __name__ == '__main__':
    UIT.mkdir(parents=True, exist_ok=True)
    hero = ROOT / 'theme' / 'assets' / 'tt-foto-hero-home.jpg'
    shots = [
        stock('1921-hd.mp4', 2.0, 3.4, snelheid=0.55),
        still(hero, 3.6, (0.62, 0.5, 1.0), (0.70, 0.5, 1.35), schaal=1.3, x0=0.15, y0=-0.2),
        still(PB / 'draagtas-tegel-2.jpg', 3.2, (0.5, 0.45, 1.25), (0.52, 0.5, 1.55), focus=9, schaal=1.1, x0=0.8, y0=-0.25),
        stock('1078-hd.mp4', 8.0, 3.0, snelheid=0.5),
        still(PB / 'draagtas-golfjes-3.jpg', 3.2, (0.5, 0.5, 1.2), (0.45, 0.42, 1.45), schaal=1.2, x0=0.1, y0=-0.3),
    ]
    film = plak(shots)
    film = [look(f, i) for i, f in enumerate(film)]
    schrijf(film, UIT / 'tide-tode-hero.mp4', 1920, 1080, 24)
    schrijf(film, UIT / 'tide-tode-hero-720.mp4', 1280, 720, 26)
    cv2.imwrite(str(UIT / 'tide-tode-hero-poster.jpg'), cv2.cvtColor((film[int(4.5 * FPS)] * 255).astype(np.uint8), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 85])
    print(len(film) / FPS, 's')
