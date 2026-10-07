"""Herovideo voor de homepage: volledig geanimeerd uit onze eigen tasbeelden, ca. 14 s, 1920 x 1080, 24 fps, lus.

Shots, allemaal recht van boven in de studiostijl van de productfoto's:
 1. drie boards met de draagtas op het zand: camera schuift langzaam in, palmschaduw wiegt, warme lichtflits
 2. macro van het geweven label en de tegelstof: focus trekt van onscherp naar scherp
 3. de lus van de band staat rechtop en klapt om op het zand (schaduw krimpt mee bij het landen)
 4. de rand van de tas over het board: langzame zijwaartse camerabeweging
 5. terug naar de drie boards, camera trekt terug; overvloeien naar shot 1 voor de lus
Echt-gefilmd gevoel: camera uit de hand, bewegingsonscherpte, scherptediepte aan de randen, lichte kleurranden van de
lens, filmkorrel, warme kleur en vignet.
Gebruik: python3 tools/video/hero_video.py  -> docs/video/tide-tode-hero.mp4, -720.mp4 en -poster.jpg
"""
import pathlib, subprocess, sys
import cv2
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / 'tools' / 'tas')); sys.path.insert(0, str(ROOT / 'tools' / 'producten'))
import studio2 as S2  # noqa: E402
import stijl as ST  # noqa: E402

PB = ROOT / 'docs' / 'producten' / 'beelden'
UIT = ROOT / 'docs' / 'video'
W, H, FPS = 1920, 1080, 24
OVER = 12
RNG = np.random.default_rng(5)


def lees(pad):
    return cv2.cvtColor(cv2.imread(str(pad)), cv2.COLOR_BGR2RGB).astype(np.float32) / 255


def ease(t):
    return 0.5 - 0.5 * np.cos(np.pi * np.clip(t, 0, 1))


def uitsnede(img, cx, cy, zoom, dx=0.0, dy=0.0, rot=0.0):
    h, w = img.shape[:2]
    vw = min(w, h * W / H) / zoom; vh = vw * H / W
    x0 = np.clip(cx * w - vw / 2, 0, w - vw) + dx; y0 = np.clip(cy * h - vh / 2, 0, h - vh) + dy
    s = W / vw
    M = cv2.getRotationMatrix2D((x0 + vw / 2, y0 + vh / 2), rot, s)
    M[0, 2] += W / 2 - (x0 + vw / 2); M[1, 2] += H / 2 - (y0 + vh / 2)
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)


# ---------- camera uit de hand: trage, gladde ruis ----------
def _ruis1d(n, schaal, zaad):
    r = np.random.default_rng(zaad).normal(0, 1, n + 40)
    r = np.convolve(r, np.hanning(schaal) / np.hanning(schaal).sum(), 'same')[20:20 + n]
    return r / (np.abs(r).max() + 1e-6)

NTOT = 400
HX, HY, HR = _ruis1d(NTOT, 36, 1) * 5, _ruis1d(NTOT, 36, 2) * 4, _ruis1d(NTOT, 48, 3) * 0.12


# ---------- palmschaduw ----------
def palmmasker(t, schaal=1.0, x0=0.2, y0=-0.15):
    m = np.zeros((H // 2, W // 2), np.float32)
    cx, cy = int(W / 2 * x0), int(H / 2 * y0)
    for i in range(14):
        hoek = np.radians(25 + i * 9 + 3.0 * np.sin(2 * np.pi * (t * 0.3 + i * 0.07)))
        lengte = (340 + 60 * np.sin(i * 1.7)) * schaal
        for j in range(22):
            f = j / 21
            px = cx + np.cos(hoek) * lengte * f + 5 * np.sin(2 * np.pi * (t * 0.45 + f))
            py = cy + np.sin(hoek) * lengte * f
            r = (1 - f) ** 0.6 * 20 * schaal + 3
            for zij in (-1, 1):
                bx = px + np.cos(hoek + zij * 1.2) * r * 1.6
                by = py + np.sin(hoek + zij * 1.2) * r * 1.6
                cv2.ellipse(m, (int(bx), int(by)), (int(r * 1.8), max(2, int(r * 0.45))), np.degrees(hoek + zij * 0.9), 0, 360, 1, -1, cv2.LINE_AA)
        cv2.line(m, (cx, cy), (int(cx + np.cos(hoek) * lengte), int(cy + np.sin(hoek) * lengte)), 1, 3, cv2.LINE_AA)
    m = cv2.resize(m, (W, H), interpolation=cv2.INTER_LINEAR)
    return cv2.GaussianBlur(m, (0, 0), 8)


def palm(img, t, sterkte=0.30, **kw):
    s = palmmasker(t, **kw)[..., None]
    return img * (1 - sterkte * s * np.array([1.0, 0.94, 0.82], np.float32))


# ---------- shots ----------
def still(pad, n, van, naar, palmkw=None, focus=None, rot=(0, 0)):
    img = lees(pad) if isinstance(pad, (str, pathlib.Path)) else pad
    for k in range(n):
        t = ease(k / (n - 1))
        cx, cy, z = [a + (b - a) * t for a, b in zip(van, naar)]
        f = uitsnede(img, cx, cy, z, rot=rot[0] + (rot[1] - rot[0]) * t)
        if focus:
            blur = focus * (1 - ease(min(1, k / (n * 0.6))))
            if blur > 0.3: f = cv2.GaussianBlur(f, (0, 0), blur)
        if palmkw is not None: f = palm(f, k / FPS, **palmkw)
        yield f


def lus_shot(n):
    """De lus staat rechtop (verkort in beeld) en klapt om op het zand."""
    ST.B, ST.H = W, H
    _l = ST._licht; ST._licht = lambda h=H, b=W: _l(h, b)
    rb, rl = S2.bouw('draagtas-tegel')
    zand = S2.zand_detail(1.0, zaad=6)
    ST._licht = _l

    def schaal(r, sx, sy):
        pm = np.dstack([r[..., :3] * r[..., 3:4], r[..., 3]])
        pm = cv2.resize(pm, None, fx=sx, fy=sy, interpolation=cv2.INTER_AREA)
        a = np.clip(pm[..., 3], 0, 1)
        return np.dstack([np.clip(pm[..., :3] / np.maximum(a[..., None], 1e-4), 0, 1), a]).astype(np.float32)

    s = 0.86
    midden = (960, 690)
    b = schaal(rb, s, s)
    basis = zand.copy()
    a_b = S2.alfa_op_doek(b, 1.0, midden, basis)
    basis = S2.slagschaduw(basis, a_b, [(3, 3, .5), (14, 12, .32), (40, 34, .26)])
    basis = ST.leg(basis, b, breedte=b.shape[1], midden=midden, hoogte=20, zachtheid=.9, contact=.7)
    # lus los: bounding box en aanhechting (onderkant van de lus = bovenrand van het board)
    ys, xs = np.where(rl[..., 3] > 0.01)
    lus = rl[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    hecht_x = (xs.min() + xs.max()) / 2; hecht_y = ys.max()
    ch, cw = rl.shape[:2]
    # plek van de aanhechting op het doek
    ax = midden[0] + (hecht_x - cw / 2) * s; ay = midden[1] + (hecht_y - ch / 2) * s
    for k in range(n):
        t = np.clip((k - n * 0.18) / (n * 0.42), 0, 1)
        val = 1 - (1 - t) ** 3                                  # klapt om, remt af
        stuit = 0.035 * np.sin(np.clip((k - n * 0.6) / (n * 0.25), 0, 1) * np.pi) if k > n * 0.6 else 0
        sy = max(0.12, 0.22 + 0.78 * val - stuit)
        hoogte = (1 - val) * 70 + stuit * 200 + 1.6
        l = schaal(lus, s * (1 + 0.06 * (1 - val)), s * sy)
        mid = (ax, ay - l.shape[0] / 2)
        d = basis.copy()
        a_l = S2.alfa_op_doek(l, 1.0, mid, d)
        d = S2.slagschaduw(d, a_l, [(1.5 + hoogte * .7, 1.3 + hoogte * .6, 0.5 * (1 - hoogte / 120)), (5 + hoogte * .9, 5 + hoogte * .9, .26)])
        d = ST.leg(d, l, breedte=l.shape[1], midden=mid, hoogte=hoogte, contact=.6 if hoogte < 4 else 0.15)
        yield uitsnede(d, 0.5, 0.52 - 0.02 * ease(k / n), 1.06 + 0.06 * ease(k / n))   # zachte camerabeweging erbovenop


# ---------- film-effecten ----------
VIG = RAND = XX = YY = None
_vorige = [None]
def camera(f, i, totaal):
    global VIG, RAND, XX, YY
    if VIG is None:
        YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
        r2 = ((XX - W / 2) / (W / 2)) ** 2 + ((YY - H / 2) / (H / 2)) ** 2
        VIG = (1 - 0.24 * r2 ** 1.15)[..., None]
        RAND = np.clip((r2 - 0.45) / 0.9, 0, 1)[..., None]          # scherptediepte: randen iets zachter
    M = cv2.getRotationMatrix2D((W / 2, H / 2), HR[i % NTOT], 1.012)
    M[0, 2] += HX[i % NTOT]; M[1, 2] += HY[i % NTOT]
    f = cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    f = f * (1 - RAND * 0.7) + cv2.GaussianBlur(f, (0, 0), 3.0) * RAND * 0.7
    if _vorige[0] is not None: f = f * 0.78 + _vorige[0] * 0.22     # bewegingsonscherpte (sluiter)
    _vorige[0] = f
    rgb = f.copy()                                                  # kleurranden van de lens
    rgb[..., 0] = cv2.warpAffine(f[..., 0], np.float32([[1.0015, 0, -W * 0.00075], [0, 1.0015, -H * 0.00075]]), (W, H), borderMode=cv2.BORDER_REFLECT)
    rgb[..., 2] = cv2.warpAffine(f[..., 2], np.float32([[0.9985, 0, W * 0.00075], [0, 0.9985, H * 0.00075]]), (W, H), borderMode=cv2.BORDER_REFLECT)
    f = rgb * np.array([1.04, 1.0, 0.93], np.float32)              # warme look
    g = f.mean(-1, keepdims=True); f = g + (f - g) * 0.92
    f = 0.025 + 0.95 * np.clip(f + 0.05 * np.sin(np.pi * (f - 0.5)), 0, 1)
    f = f * VIG
    for piek in (int(0.4 * FPS), totaal - int(1.0 * FPS)):          # warme lichtflits
        a = np.exp(-((i - piek) / (0.55 * FPS)) ** 2) * 0.28
        if a > 0.01:
            lek = np.clip(1 - (((XX - W * 0.95) / (W * 0.55)) ** 2 + ((YY - H * 0.05) / (H * 0.8)) ** 2), 0, 1)[..., None]
            f = 1 - (1 - f) * (1 - a * lek * np.array([1.0, 0.72, 0.42], np.float32))
    k = RNG.normal(0, 0.017, (H // 2, W // 2)).astype(np.float32)
    return np.clip(f + cv2.resize(k, (W, H))[..., None], 0, 1)


def plak(shots):
    """Shots achter elkaar met overvloei; het einde vloeit in het begin (lus). Frames gaan één voor één door."""
    begin, staart = [], []
    eerste = True
    for shot in shots:
        shot = iter(shot)
        if not eerste:
            for i in range(OVER):
                a = (i + 1) / (OVER + 1)
                staart[i] = staart[i] * (1 - a) + next(shot) * a
            for f in staart: yield f
            staart = []
        for f in shot:
            if eerste and len(begin) < OVER:
                begin.append(f); continue
            staart.append(f)
            if len(staart) > OVER: yield staart.pop(0)
        eerste = False
    for i in range(OVER):                                           # lus
        a = (i + 1) / (OVER + 1)
        yield staart[i] * (1 - a) + begin[i] * a


def encoder(pad, w, h, crf):
    return subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                             '-vf', f'scale={w}:{h}:flags=lanczos', '-an', '-c:v', 'libx264', '-preset', 'slow', '-crf', str(crf),
                             '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(pad)], stdin=subprocess.PIPE)


if __name__ == '__main__':
    UIT.mkdir(parents=True, exist_ok=True)
    hero = lees(ROOT / 'theme' / 'assets' / 'tt-foto-hero-home.jpg')
    f = lambda s: int(s * FPS)
    shots = [
        still(hero, f(3.6), (0.62, 0.5, 1.0), (0.70, 0.5, 1.32), palmkw=dict(schaal=1.3, x0=0.12, y0=-0.2), rot=(-0.4, 0.2)),
        still(PB / 'draagtas-tegel-2.jpg', f(3.2), (0.5, 0.42, 1.2), (0.52, 0.5, 1.5), focus=10, palmkw=dict(schaal=1.1, x0=0.85, y0=-0.25)),
        lus_shot(f(3.4)),
        still(PB / 'draagtas-golfjes-3.jpg', f(3.0), (0.38, 0.5, 1.25), (0.62, 0.46, 1.3), palmkw=dict(schaal=1.2, x0=0.05, y0=-0.3)),
        still(hero, f(3.0), (0.72, 0.5, 1.4), (0.66, 0.5, 1.05), palmkw=dict(schaal=1.3, x0=0.12, y0=-0.2)),
    ]
    totaal = sum(int(x * FPS) for x in (3.6, 3.2, 3.4, 3.0, 3.0)) - 4 * OVER
    groot = encoder(UIT / 'tide-tode-hero.mp4', 1920, 1080, 23)
    klein = encoder(UIT / 'tide-tode-hero-720.mp4', 1280, 720, 25)
    momenten = {int(s * FPS): i for i, s in enumerate([1.5, 5.0, 8.4, 11.0])}
    for i, fr in enumerate(plak(shots)):
        fr = camera(fr, i, totaal)
        b8 = (fr * 255 + 0.5).astype(np.uint8)
        groot.stdin.write(b8.tobytes()); klein.stdin.write(b8.tobytes())
        if i == 0:
            cv2.imwrite(str(UIT / 'tide-tode-hero-poster.jpg'), cv2.cvtColor(b8, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 86])
        if i in momenten:
            cv2.imwrite(f'/tmp/claude-0/-home-user-Veerle/e622134c-148a-50b2-bdf1-45d3e9d54d8e/scratchpad/vf{momenten[i]}.jpg', cv2.cvtColor(b8, cv2.COLOR_RGB2BGR))
    for e in (groot, klein): e.stdin.close(); e.wait()
    print(i + 1, 'frames', round((i + 1) / FPS, 1), 's')
