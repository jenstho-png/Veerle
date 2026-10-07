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
# board met tas: echte render, staand, schuin op de rug
rb, rl = S2.bouw('draagtas-tegel')
rb = cv2.rotate(rb, cv2.ROTATE_90_COUNTERCLOCKWISE)
ys, xs = np.where(rb[..., 3] > .01); rb = rb[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
s = 880 / rb.shape[0]; rb = cv2.resize(rb, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
h, w = rb.shape[:2]
M = cv2.getRotationMatrix2D((w / 2, h / 2), -28, 1.0)
M[0, 2] += 790 - w / 2; M[1, 2] += 730 - h / 2
laag = cv2.warpAffine(rb, M, (W, H), flags=cv2.INTER_AREA)
a = laag[..., 3:4]
# schaduw van het board op de rug
sch = cv2.GaussianBlur(cv2.warpAffine(a[..., 0], np.float32([[1, 0, 10], [0, 1, 14]]), (W, H)), (0, 0), 10)[..., None]
img = img * (1 - 0.25 * sch) ; img = img * (1 - a) + laag[..., :3] * a
# bovenrand van het vak: zoek de band (blauwe kleur) bovenaan in de laag
def punt(x, y):
    p = M @ np.array([x, y, 1.0]); return int(p[0]), int(p[1])
lx, rx = punt(w * 0.02, h * 0.40), punt(w * 0.98, h * 0.37)
band = (0.40, 0.52, 0.66)
# de lus: van beide railkanten omhoog over de rechterschouder
t = np.linspace(0, 1, 60)
schouder = np.array([955, 392])
links = np.array(lx, float); rechts = np.array(rx, float)
p1 = [(1 - u) ** 2 * links + 2 * (1 - u) * u * np.array([820, 400]) + u ** 2 * schouder for u in t]
p2 = [(1 - u) ** 2 * schouder + 2 * (1 - u) * u * np.array([1010, 430]) + u ** 2 * rechts for u in t]
pad = np.int32(p1 + p2)
cv2.polylines(img, [pad], False, band, 34, cv2.LINE_AA)
cv2.polylines(img, [pad], False, (0.30, 0.40, 0.52), 2, cv2.LINE_AA)
# pijlen en uitleg
img = (np.clip(img, 0, 1) * 255).astype(np.uint8)
deep = (34, 50, 79)
def tekst(t, xy):
    cv2.putText(img, t, xy, cv2.FONT_HERSHEY_SIMPLEX, 0.9, deep, 2, cv2.LINE_AA)
tekst('strap loop over RIGHT shoulder', (1000, 380)); cv2.arrowedLine(img, (995, 372), (950, 410), deep, 3, cv2.LINE_AA, tipLength=.2)
tekst('sleeve wraps around the board', (1060, 700)); cv2.arrowedLine(img, (1055, 692), (930, 640), deep, 3, cv2.LINE_AA, tipLength=.2)
tekst('hands free', (230, 760)); cv2.arrowedLine(img, (420, 752), (570, 760), deep, 3, cv2.LINE_AA, tipLength=.2)
cv2.putText(img, 'LAYOUT REFERENCE  (seen from behind)', (40, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.1, deep, 2, cv2.LINE_AA)
uit = R / 'docs' / 'producten' / 'proef' / 'referentie-schouder.jpg'
cv2.imwrite(str(uit), cv2.cvtColor(img, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 90])
print(uit)
