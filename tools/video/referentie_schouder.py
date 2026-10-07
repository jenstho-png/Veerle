"""Schetsbeeld voor een AI-beeldmaker: hoe de draagtas gedragen wordt (board schuin op de rug, band over de schouder).
De tas en het board zijn onze echte render (studio2.bouw), de persoon is een eenvoudige vlakke schets.
Schrijft docs/producten/proef/referentie-schouder.jpg"""
import pathlib, sys
import cv2, numpy as np
R = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(R / 'tools' / 'tas'))
import studio2 as S2

W, H = 1600, 1200
img = np.ones((H, W, 3), np.float32) * np.array([0.93, 0.90, 0.84], np.float32)
# lucht / zee / duin als vlakken
img[:430] = np.array([0.86, 0.89, 0.92]); img[430:520] = np.array([0.62, 0.72, 0.78]); img[520:] = np.array([0.88, 0.82, 0.70])
def poly(pts, kleur):
    cv2.fillPoly(img, [np.int32(pts)], kleur, cv2.LINE_AA)
deep = (0.13, 0.20, 0.31)
# persoon van achteren
cv2.circle(img, (800, 300), 70, (0.45, 0.33, 0.24), -1, cv2.LINE_AA)                 # hoofd (haar)
poly([(690, 380), (910, 380), (960, 470), (930, 760), (670, 760), (640, 470)], (0.95, 0.93, 0.86))   # t-shirt
poly([(655, 470), (610, 470), (585, 740), (625, 745)], (0.82, 0.66, 0.54))           # linkerarm
poly([(945, 470), (990, 470), (1010, 740), (972, 745)], (0.82, 0.66, 0.54))         # rechterarm
poly([(675, 760), (925, 760), (915, 900), (810, 900), (800, 820), (790, 900), (685, 900)], (0.22, 0.24, 0.28))  # short
poly([(700, 900), (780, 900), (770, 1150), (710, 1150)], (0.82, 0.66, 0.54))
poly([(820, 900), (900, 900), (890, 1150), (830, 1150)], (0.82, 0.66, 0.54))
poly([(560, 735), (640, 735), (650, 960), (575, 960)], (0.30, 0.45, 0.62))           # handdoek
# board met tas: echte render, liggend (lus komt uit de bovenste rail), lus langer zodat hij over de schouder reikt
rb, rl = S2.bouw('draagtas-tegel')
ys, xs = np.where(np.maximum(rb[..., 3], rl[..., 3]) > .01)
rb = rb[ys.min():ys.max() + 1, xs.min():xs.max() + 1]; rl = rl[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
# board-bovenrand (eerste rij met board) en de lus erboven uitrekken
rij_b = np.where(rb[..., 3].max(1) > .5)[0].min()
boven = rl[:rij_b]; onder_l = rl[rij_b:]
rek = 1.9
boven = cv2.resize(boven, (boven.shape[1], int(boven.shape[0] * rek)), interpolation=cv2.INTER_LINEAR)
pad_b = np.zeros((boven.shape[0] - rij_b, rb.shape[1], 4), np.float32)
rb = np.concatenate([pad_b, rb], 0); rl = np.concatenate([boven, onder_l], 0)
laag_rgba = rl.copy()
a_b = rb[..., 3:4]
laag_rgba[..., :3] = rb[..., :3] * a_b + rl[..., :3] * rl[..., 3:4] * (1 - a_b)
laag_rgba[..., 3:4] = np.clip(a_b + rl[..., 3:4] * (1 - a_b), 0, 1)
laag_rgba[..., :3] = laag_rgba[..., :3] / np.maximum(laag_rgba[..., 3:4], 1e-4)
s_ = 980 / laag_rgba.shape[1]
laag_rgba = cv2.resize(laag_rgba, None, fx=s_, fy=s_, interpolation=cv2.INTER_AREA)
h, w = laag_rgba.shape[:2]
# toppunt van de lus vinden en op de rechterschouder leggen; board schuin (neus rechtsboven)
ys2, xs2 = np.where(laag_rgba[..., 3] > .5)
top = np.array([xs2[ys2 == ys2.min()].mean(), ys2.min()])
hoek = 22
M = cv2.getRotationMatrix2D((float(top[0]), float(top[1])), hoek, 1.0)
M[0, 2] += 950 - top[0]; M[1, 2] += 392 - top[1]
laag = cv2.warpAffine(laag_rgba, M, (W, H), flags=cv2.INTER_AREA)
a = laag[..., 3:4]
sch = cv2.GaussianBlur(cv2.warpAffine(a[..., 0], np.float32([[1, 0, 10], [0, 1, 14]]), (W, H)), (0, 0), 10)[..., None]
img = img * (1 - 0.25 * sch); img = img * (1 - a) + laag[..., :3] * a
# schouder over de lus heen tekenen: de lus ligt OP de schouder
# pijlen en uitleg
img = (np.clip(img, 0, 1) * 255).astype(np.uint8)
deep = (34, 50, 79)
def tekst(t, xy):
    cv2.putText(img, t, xy, cv2.FONT_HERSHEY_SIMPLEX, 0.9, deep, 2, cv2.LINE_AA)
tekst('strap loop over RIGHT shoulder', (1000, 380)); cv2.arrowedLine(img, (995, 372), (950, 410), deep, 3, cv2.LINE_AA, tipLength=.2)
tekst('both strap ends come out of the TOP rail', (1030, 560)); cv2.arrowedLine(img, (1150, 575), (1080, 700), deep, 3, cv2.LINE_AA, tipLength=.2)
tekst('sleeve wraps around the board', (1030, 1130)); cv2.arrowedLine(img, (1150, 1100), (1150, 960), deep, 3, cv2.LINE_AA, tipLength=.2)
tekst('board hangs at the right side, deck facing out', (60, 1150))
tekst('hands free', (230, 760)); cv2.arrowedLine(img, (420, 752), (570, 760), deep, 3, cv2.LINE_AA, tipLength=.2)
cv2.putText(img, 'LAYOUT REFERENCE  (seen from behind)', (40, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.1, deep, 2, cv2.LINE_AA)
uit = R / 'docs' / 'producten' / 'proef' / 'referentie-schouder.jpg'
cv2.imwrite(str(uit), cv2.cvtColor(img, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 90])
print(uit)
