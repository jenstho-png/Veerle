"""Rekent de organische merktekens van Tide-Tode uit: spiraal (tij), golvende zonnestralen en het TT-monogram."""
import math, json

def f(n): return f"{n:.1f}"

def spiral(cx, cy, r0, r1, turns, start=0.0, steps_per_turn=48):
    pts = []
    n = int(turns * steps_per_turn)
    for i in range(n + 1):
        t = i / n
        a = start + t * turns * 2 * math.pi
        r = r0 + (r1 - r0) * t
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return "M" + "L".join(f"{f(x)} {f(y)}" for x, y in pts)

def wavy_ray(cx, cy, angle, r_in, r_out, amp, waves=1.0, steps=24):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        r = r_in + (r_out - r_in) * t
        side = amp * math.sin(t * waves * 2 * math.pi)
        x = r * math.cos(angle) - side * math.sin(angle)
        y = r * math.sin(angle) + side * math.cos(angle)
        pts.append((cx + x, cy + y))
    return "M" + "L".join(f"{f(x)} {f(y)}" for x, y in pts)

def wave(x0, x1, y, amp, n):
    w = (x1 - x0) / n
    d = f"M{f(x0)} {f(y)}"
    for i in range(n):
        xa = x0 + i * w
        sgn = -1 if i % 2 == 0 else 1
        d += f"C{f(xa + w * .35)} {f(y + sgn * amp)} {f(xa + w * .65)} {f(y + sgn * amp)} {f(xa + w)} {f(y)}"
    return d

marks = {
    # icoon: spiraal in 48-grid
    "spiraal_icoon": spiral(24, 24, 2.5, 17, 2.1, start=-math.pi / 2),
    # zon-spiraal: ring + 12 golvende stralen + spiraal (200-grid)
    "zon_stralen": "".join(wavy_ray(100, 100, i * math.pi / 6 - math.pi / 2, 68, 96, 4.5, 1.0) for i in range(12)),
    "zon_spiraal": spiral(100, 100, 3, 27, 1.7, start=-math.pi / 2),
    # TT-monogram: één golf als dwarsbalk, twee draagbanden als poten (200-grid)
    "tt_balk": wave(18, 182, 58, 9, 6),
}
print(json.dumps(marks))
