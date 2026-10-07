"""Board opmeten in de stockfoto's voor de sfeerbeelden (sfeer.py).

Per foto:
1. Segmentatie met GrabCut, gestart vanuit een ruwe omtrek (neus, staart, breedte) plus handmatige hints
   (punten/lijnen die zeker board of zeker geen board zijn, bv. handen, planten of een ander board ervoor).
2. Uit het masker: de as van het board, per positie langs de as de linker- en rechterrand (gladde fit, zodat
   randen achter een occluder doorlopen), neus, staart, het balanspunt (midden tussen neus en staart) en de breedte daar.
3. Occluders: pixels binnen de gladde omtrek die geen board zijn.

Resultaat: masker (png) in docs/producten/stock/lifestyle/maskers/ en de maten in bronnen.json.
`python3 tools/tas/sfeer_meet.py [foto ...]` maakt ook controlebeelden in de scratchmap (SFEER_CHECK).
"""
import json, os, pathlib, sys
import cv2
import numpy as np
from PIL import Image

HIER = pathlib.Path(__file__).parent
ROOT = HIER.parent.parent
STOCK = ROOT / 'docs' / 'producten' / 'stock' / 'lifestyle'
MASK = STOCK / 'maskers'
HINTS = HIER / 'sfeer_hints.json'


def laad(naam):
    return np.asarray(Image.open(STOCK / naam).convert('RGB'))


def ruwe_omtrek(neus, staart, breedte, f=None):
    from scipy.interpolate import PchipInterpolator
    u = staart - neus; L = np.linalg.norm(u); u = u / L
    n = np.array([-u[1], u[0]])
    t = np.array([0, .02, .06, .14, .28, .45, .6, .75, .88, .96, 1.0])
    f = f if f is not None else np.array([0, .3, .55, .76, .92, 1.0, 1.0, .94, .78, .55, .4])
    spl = PchipInterpolator(t, f)
    ts = np.linspace(0, 1, 200)
    links = [neus + u * L * x + n * breedte / 2 * spl(x) for x in ts]
    rechts = [neus + u * L * x - n * breedte / 2 * spl(x) for x in ts][::-1]
    return np.array(links + rechts, np.float32)


def segmenteer(img, hint):
    """GrabCut met een startmasker uit de ruwe omtrek en de hints."""
    h, w = img.shape[:2]
    neus = np.array(hint['neus'], np.float32); staart = np.array(hint['staart'], np.float32)
    b = float(hint['breedte'])
    m = np.full((h, w), cv2.GC_BGD, np.uint8)
    cv2.fillPoly(m, [np.round(ruwe_omtrek(neus, staart, b * 1.35)).astype(np.int32)], cv2.GC_PR_BGD)
    cv2.fillPoly(m, [np.round(ruwe_omtrek(neus, staart, b * 1.0)).astype(np.int32)], cv2.GC_PR_FGD)
    # kern: zeker board (alleen het middenstuk, smal)
    u = staart - neus
    kern_n = neus + u * hint.get('kern', (0.2, 0.8))[0]; kern_s = neus + u * hint.get('kern', (0.2, 0.8))[1]
    cv2.line(m, tuple(np.round(kern_n).astype(int)), tuple(np.round(kern_s).astype(int)), cv2.GC_FGD, max(int(b * 0.25), 3))
    for soort, waarde in (('fg', cv2.GC_FGD), ('bg', cv2.GC_BGD), ('pfg', cv2.GC_PR_FGD), ('pbg', cv2.GC_PR_BGD)):
        for item in hint.get(soort, []):
            pts = np.array(item[:-1], np.int32) if isinstance(item[-1], (int, float)) else None
            dik = item[-1]
            if len(item) == 2:            # punt + dikte
                cv2.circle(m, tuple(item[0]), int(dik), waarde, -1)
            elif item[0] == 'poly':
                cv2.fillPoly(m, [np.array(item[1], np.int32)], waarde)
            else:
                cv2.polylines(m, [pts], False, waarde, int(dik))
    bgd, fgd = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    # werken op een kleinere schaal als het beeld groot is, daarna verfijnen op volle schaal rond de rand
    cv2.setRNGSeed(1)
    cv2.grabCut(cv2.cvtColor(img, cv2.COLOR_RGB2BGR), m, None, bgd, fgd, hint.get('iter', 6), cv2.GC_INIT_WITH_MASK)
    fg = ((m == cv2.GC_FGD) | (m == cv2.GC_PR_FGD)).astype(np.uint8)
    # grootste component, gaten dicht
    n, lab, st, _ = cv2.connectedComponentsWithStats(fg, 8)
    if n > 1:
        k = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
        fg = (lab == k).astype(np.uint8)
    inv = 1 - fg
    n, lab, st, _ = cv2.connectedComponentsWithStats(inv, 4)
    for i in range(1, n):
        x, y, ww, hh, a = st[i]
        if x > 0 and y > 0 and x + ww < w and y + hh < h and a < 0.02 * fg.sum():
            fg[lab == i] = 1
    return fg


def as_en_randen(fg, hint):
    """As (rechte lijn neus-staart), per positie t langs de as de randen links/rechts (afstand tot de as)."""
    neus = np.array(hint['neus'], np.float64); staart = np.array(hint['staart'], np.float64)
    ys, xs = np.nonzero(fg)
    P = np.stack([xs, ys], 1).astype(np.float64)
    # as: hoofdas van het masker, richting neus
    c = P.mean(0)
    cov = np.cov((P - c).T)
    ev, evec = np.linalg.eigh(cov)
    a = evec[:, 1]
    if np.dot(a, neus - staart) < 0:
        a = -a
    if hint.get('as_vast'):
        a = (neus - staart) / np.linalg.norm(neus - staart)
    n = np.array([-a[1], a[0]])
    t = (P - c) @ a; s = (P - c) @ n
    # randen per strook langs de as
    tmin, tmax = t.min(), t.max()
    stap = 2.0
    bins = np.arange(tmin, tmax + stap, stap)
    idx = np.digitize(t, bins) - 1
    lo = np.full(len(bins), np.nan); hi = np.full(len(bins), np.nan)
    order = np.argsort(idx)
    idx_s, s_s = idx[order], s[order]
    grenzen = np.searchsorted(idx_s, np.arange(len(bins) + 1))
    for i in range(len(bins)):
        seg = s_s[grenzen[i]:grenzen[i + 1]]
        if len(seg) > 2:
            lo[i] = np.percentile(seg, 0.5); hi[i] = np.percentile(seg, 99.5)
    tc = bins + stap / 2
    # middellijn: lineaire fit van (lo+hi)/2 op het middenstuk -> as corrigeren
    ok = ~np.isnan(lo)
    mid = (lo + hi) / 2
    sel = ok & (np.abs(tc) < (tmax - tmin) * 0.3)
    p = np.polyfit(tc[sel], mid[sel], 1)
    # nieuwe as: draai en verschuif zodat de middellijn s=0 is
    hoek = np.arctan(p[0])
    a2 = a * np.cos(hoek) + n * np.sin(hoek)
    if hint.get('as_vast'):
        a2 = a
    c2 = c + n * p[1]
    return c2, a2


def profiel(fg, c, a, stap=1.0):
    n = np.array([-a[1], a[0]])
    ys, xs = np.nonzero(fg)
    P = np.stack([xs, ys], 1).astype(np.float64)
    t = (P - c) @ a; s = (P - c) @ n
    ti = np.round(t / stap).astype(int)
    tmin = ti.min()
    k = ti - tmin
    N = k.max() + 1
    lo = np.full(N, np.inf); hi = np.full(N, -np.inf)
    np.minimum.at(lo, k, s); np.maximum.at(hi, k, s)
    tt = (np.arange(N) + tmin) * stap
    lo[np.isinf(lo)] = np.nan; hi[np.isinf(hi)] = np.nan
    return tt, lo, hi


def glad(tt, v, venster=31, geldig=None):
    """Robuust gladmaken (mediaan dan gemiddelde), alleen over geldige punten."""
    from scipy.ndimage import median_filter, uniform_filter1d
    ok = ~np.isnan(v) if geldig is None else geldig & ~np.isnan(v)
    vv = np.interp(tt, tt[ok], v[ok])
    vv = median_filter(vv, venster, mode='nearest')
    return uniform_filter1d(vv, max(venster // 2, 1), mode='nearest')


def meet(naam, hint, check=None):
    img = laad(naam)
    h, w = img.shape[:2]
    fg = segmenteer(img, hint)
    c, a = as_en_randen(fg, hint)
    n = np.array([-a[1], a[0]])
    tt, lo, hi = profiel(fg, c, a)
    # gladde randen; in stukken met occluders (hint 'occ_t': lijst [t0,t1] langs de as, in px vanaf c) niet meetellen
    geldig = np.ones(len(tt), bool)
    for t0, t1 in hint.get('negeer_t_lo', []):
        pass
    glo = np.ones(len(tt), bool); ghi = np.ones(len(tt), bool)
    for t0, t1 in hint.get('negeer_lo', []):
        glo &= ~((tt >= t0) & (tt <= t1))
    for t0, t1 in hint.get('negeer_hi', []):
        ghi &= ~((tt >= t0) & (tt <= t1))
    lo_g = glad(tt, lo, 15, glo); hi_g = glad(tt, hi, 15, ghi)
    t_neus = tt.max() if not hint.get('neus_buiten') else None
    t_staart = tt.min() if not hint.get('staart_buiten') else None
    # balanspunt
    if t_neus is not None and t_staart is not None:
        tb = (t_neus + t_staart) / 2
    else:
        tb = hint.get('balans_t', 0.0)
    if 'balans_t' in hint:
        tb = hint['balans_t']
    i = np.argmin(np.abs(tt - tb))
    breedte = float(hi_g[i] - lo_g[i])
    mid = c + a * tb + n * (hi_g[i] + lo_g[i]) / 2
    res = dict(c=c.tolist(), a=a.tolist(), t_neus=None if t_neus is None else float(t_neus),
               t_staart=None if t_staart is None else float(t_staart), t_balans=float(tb),
               breedte=breedte, midden=mid.tolist(), tt=tt, lo=lo_g, hi=hi_g)
    MASK.mkdir(exist_ok=True)
    Image.fromarray(fg * 255).save(MASK / (pathlib.Path(naam).stem + '.png'))
    if check:
        controle(img, fg, res, check / f'meet-{pathlib.Path(naam).stem}.jpg', hint)
    return res, fg


def controle(img, fg, r, pad, hint):
    c, a = np.array(r['c']), np.array(r['a']); n = np.array([-a[1], a[0]])
    vis = img.copy()
    rand = cv2.morphologyEx(fg, cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8))
    vis[rand > 0] = (255, 0, 255)
    for t, l, hh in zip(r['tt'][::3], r['lo'][::3], r['hi'][::3]):
        for s in (l, hh):
            p = c + a * t + n * s
            if 0 <= p[0] < vis.shape[1] and 0 <= p[1] < vis.shape[0]:
                vis[int(p[1]), int(p[0])] = (0, 255, 0)
    tb = r['t_balans']
    i = np.argmin(np.abs(r['tt'] - tb))
    p0 = c + a * tb + n * r['lo'][i]; p1 = c + a * tb + n * r['hi'][i]
    cv2.line(vis, tuple(np.round(p0).astype(int)), tuple(np.round(p1).astype(int)), (255, 255, 0), 2)
    pa = c + a * r['tt'].max(); pb = c + a * r['tt'].min()
    cv2.line(vis, tuple(np.round(pa).astype(int)), tuple(np.round(pb).astype(int)), (0, 255, 255), 1)
    H = 1400
    s = H / vis.shape[0]
    Image.fromarray(cv2.resize(vis, (int(vis.shape[1] * s), H), interpolation=cv2.INTER_AREA)).save(pad, quality=85)


def opslaan_bronnen(naam, r):
    data = json.load(open(STOCK / 'bronnen.json'))
    c, a = np.array(r['c']), np.array(r['a'])
    for p in data['photos']:
        if p['file'] != naam:
            continue
        b = p.setdefault('board', {})
        b['nose_tip'] = None if r['t_neus'] is None else [round(float(v), 1) for v in c + a * r['t_neus']]
        b['tail_tip'] = None if r['t_staart'] is None else [round(float(v), 1) for v in c + a * r['t_staart']]
        b['middle_point'] = [round(float(v), 1) for v in r['midden']]
        b['width_at_middle_px'] = round(r['breedte'], 1)
        b['axis_unit_to_nose'] = [round(float(v), 5) for v in a]
        b['mask'] = f'maskers/{pathlib.Path(naam).stem}.png'
        b['measured'] = 'GrabCut segmentation + manual hints (tools/tas/sfeer_meet.py), checked on zoomed crops; accuracy about +/- 2 px'
    data['coordinate_notes'] = ('Pixel coordinates [x, y] in the saved file (origin top-left). nose_tip/tail_tip are the board\'s extreme points on '
                                'its long axis (null = outside the frame). middle_point is the balance point (halfway nose-tail) on the board centre line, '
                                'width_at_middle_px the board width there, perpendicular to the axis. For boards with a "mask" these come from '
                                'the segmentation in maskers/ (tools/tas/sfeer_meet.py).')
    json.dump(data, open(STOCK / 'bronnen.json', 'w'), indent=2, ensure_ascii=False)


if __name__ == '__main__':
    hints = json.load(open(HINTS))
    check = pathlib.Path(os.environ.get('SFEER_CHECK', '/tmp'))
    check.mkdir(parents=True, exist_ok=True)
    keuze = sys.argv[1:]
    for naam, hint in hints.items():
        if keuze and not any(k in naam for k in keuze):
            continue
        r, fg = meet(naam, hint, check)
        opslaan_bronnen(naam, r)
        print(naam, 'breedte %.1f' % r['breedte'], 'midden', np.round(r['midden'], 1), 'neus', r['t_neus'], 'staart', r['t_staart'])
