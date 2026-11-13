"""Builds the Trophy Room and matchcut tiles and the three small square tiles from the existing project tiles.

Run from the repo root: python tools/make_tiles.py
Reads assets/tiles/{cadence,vibeleak-skills,vibeleak-atlas}.svg, writes
assets/tiles/hermes-trophy-room.svg, assets/tiles/matchcut.svg and assets/tiles/small/*.svg.
"""
import base64, colorsys, io, re
from pathlib import Path

import numpy as np
from PIL import Image

T = Path('assets/tiles')
IMG = re.compile(r'<image[^>]*?(?:/>|>.*?</image>)', re.S)


def parts(svg):
    defs = re.search(r'<defs>(.*?)</defs>', svg, re.S).group(1)
    bg = re.search(r'<rect width="1200" height="600" fill="url\(#bgG\)"/>.*?(?=<rect width="1200" height="600" fill="url\(#vig\)"/>|<g clip-path|<rect x="720")', svg, re.S).group(0)
    bg = ''.join(m for m in re.findall(r'<rect width="1200" height="600" fill="url\(#(?:bgG|glowG)\)"/>', bg)) + ''.join(i for i in IMG.findall(bg) if 'width="1200"' in i)
    flame = re.search(r'<g><image[^>]*width="246".*?</g>', svg, re.S).group(0)
    fy = int(re.search(r'width="246"', flame) and re.search(r'x="868" y="(\d+)"', flame).group(1))
    return defs, bg, flame, fy


def hue_shift_png(b64, deg):
    im = Image.open(io.BytesIO(base64.b64decode(b64))).convert('RGBA')
    a = np.asarray(im).astype(np.float32) / 255
    rgb = a[..., :3]
    mx, mn = rgb.max(-1), rgb.min(-1)
    # rotate hue in YIQ space: fast and keeps greys and whites untouched
    th = np.deg2rad(deg)
    c, s = np.cos(th), np.sin(th)
    m = np.array([[0.299, 0.587, 0.114], [0.596, -0.274, -0.322], [0.211, -0.523, 0.312]])
    inv = np.linalg.inv(m)
    yiq = rgb @ m.T
    i, q = yiq[..., 1].copy(), yiq[..., 2].copy()
    yiq[..., 1] = i * c - q * s
    yiq[..., 2] = i * s + q * c
    out = np.clip(yiq @ inv.T, 0, 1)
    a[..., :3] = out
    buf = io.BytesIO()
    Image.fromarray((a * 255).round().astype(np.uint8)).save(buf, 'PNG', optimize=True)
    return base64.b64encode(buf.getvalue()).decode()


def recolor(svg, deg, colors):
    svg = re.sub(r'data:image/png;base64,([A-Za-z0-9+/=]+)', lambda m: 'data:image/png;base64,' + hue_shift_png(m.group(1), deg), svg)
    for a, b in colors.items():
        svg = svg.replace(a, b)
    return svg


TIERS = ['#d08a5c', '#c9d2e0', '#ffbf2e', '#8fe3ff', '#b79cff']


def trophy_tile():
    src = (T / 'cadence.svg').read_text(encoding='utf-8')
    accent = '#6fd8ff'
    head, body = src.split('</defs>', 1)
    body = re.sub(r'<rect x="720" y="24"[^>]*/>', '', body)
    body = re.sub(r'<rect x="\d+" y="\d+" width="24" height="24"[^>]*><animate[^>]*/></rect>', '', body)
    body = re.sub(r'<text .*?</text>', '', body, flags=re.S)
    svg = head + '</defs>' + body
    svg = recolor(svg, 53, {'#8f7bff': accent})
    svg = svg.replace('Cadence: streaks, a heatmap and model mix for Hermes.', 'Hermes Trophy Room: 120 achievements for Hermes Desktop.')
    # five tier cards where the heatmap was, lit one after another
    cards = [f'<rect x="720" y="24" width="408" height="152" fill="#07070e" fill-opacity=".94" stroke="{accent}" stroke-opacity=".35" stroke-width="1.5"/>']
    for k, col in enumerate(TIERS):
        x = 748 + k * 72
        cards.append(
            f'<g opacity=".55"><animate attributeName="opacity" values=".45;1;.45;.45" keyTimes="0;.12;.3;1" dur="3s" begin="{k * 0.45:.2f}s" repeatCount="indefinite"/>'
            f'<rect x="{x}" y="40" width="56" height="78" fill="{col}" fill-opacity=".16" stroke="{col}" stroke-width="2"/>'
            f'<rect x="{x + 8}" y="48" width="40" height="40" fill="{col}" fill-opacity=".55"/>'
            f'<rect x="{x + 8}" y="96" width="40" height="5" fill="{col}" fill-opacity=".8"/>'
            f'<rect x="{x + 8}" y="106" width="26" height="4" fill="{col}" fill-opacity=".5"/></g>')
    cards.append(f'<text class="k" x="924" y="156" text-anchor="middle" fill="{accent}" font-size="18" letter-spacing="4">COPPER TO OLYMPIAN</text>')
    text = (f'<text class="k" x="72" y="168" fill="{accent}">DESKTOP PLUGIN</text>'
            '<text class="t" x="72" y="270" font-size="96">Hermes</text>'
            '<text class="t" x="72" y="362" font-size="96">Trophy Room</text>'
            '<text class="s" x="72" y="430">120 trophies as collectible cards</text>'
            '<text class="s" x="72" y="472">for Hermes Desktop.</text>'
            '<text class="m" x="72" y="548">github.com/abundantbeing/hermes-trophy-room</text>')
    svg = svg.replace('<rect width="1200" height="600" fill="url(#vig)"/>', '<rect width="1200" height="600" fill="url(#vig)"/>' + ''.join(cards) + text, 1)
    (T / 'hermes-trophy-room.svg').write_text(svg, encoding='utf-8', newline='\n')


def matchcut_tile():
    src = (T / 'cadence.svg').read_text(encoding='utf-8')
    accent = '#39e0c3'
    head, body = src.split('</defs>', 1)
    body = re.sub(r'<rect x="720" y="24"[^>]*/>', '', body)
    body = re.sub(r'<rect x="\d+" y="\d+" width="24" height="24"[^>]*><animate[^>]*/></rect>', '', body)
    body = re.sub(r'<text .*?</text>', '', body, flags=re.S)
    svg = head + '</defs>' + body
    svg = recolor(svg, 82, {'#8f7bff': accent})
    svg = svg.replace('Cadence: streaks, a heatmap and model mix for Hermes.', 'matchcut: agent skills for product launch films from your real app.')
    # an edit timeline where the heatmap was: clips on a track, beat ticks, a playhead sweeping across
    p = [f'<rect x="720" y="24" width="408" height="152" fill="#07070e" fill-opacity=".94" stroke="{accent}" stroke-opacity=".35" stroke-width="1.5"/>']
    for i in range(16):
        x = 744 + i * 23.5
        p.append(f'<rect x="{x:.1f}" y="44" width="2" height="{10 if i % 4 == 0 else 5}" fill="{accent}" fill-opacity="{.9 if i % 4 == 0 else .4}"/>')
    clips = [(744, 70, '#5b6cff'), (818, 92, accent), (914, 58, '#8fe3ff'), (976, 128, accent)]
    for x, w, col in clips:
        p.append(f'<rect x="{x}" y="66" width="{w - 4}" height="34" fill="{col}" fill-opacity=".22" stroke="{col}" stroke-width="2"/>')
        p.append(f'<rect x="{x + 6}" y="74" width="{max(10, w - 30)}" height="5" fill="{col}" fill-opacity=".7"/>')
    p.append('<rect x="744" y="108" width="356" height="10" fill="#ffffff" fill-opacity=".06"/>')
    for x in (750, 790, 830, 870, 910, 950, 990, 1030, 1070):
        p.append(f'<rect x="{x}" y="110" width="22" height="6" fill="{accent}" fill-opacity=".35"/>')
    p.append(f'<rect x="744" y="38" width="3" height="86" fill="#ffffff"><animate attributeName="x" values="744;1100" dur="4s" repeatCount="indefinite"/></rect>')
    p.append(f'<text class="k" x="924" y="156" text-anchor="middle" fill="{accent}" style="font-size:15px;letter-spacing:3px">EVERY CUT ON THE BEAT</text>')
    text = (f'<text class="k" x="72" y="168" fill="{accent}">AGENT SKILLS</text>'
            '<text class="t" x="72" y="318" font-size="132">matchcut</text>'
            '<text class="s" x="72" y="410">Launch films from your real app,</text>'
            '<text class="s" x="72" y="452">cut like a trailer.</text>'
            '<text class="m" x="72" y="548">github.com/abundantbeing/matchcut</text>')
    svg = svg.replace('<rect width="1200" height="600" fill="url(#vig)"/>', '<rect width="1200" height="600" fill="url(#vig)"/>' + ''.join(p) + text, 1)
    (T / 'matchcut.svg').write_text(svg, encoding='utf-8', newline='\n')


def small(name, kicker, lines, accent, label):
    src = (T / f'{name}.svg').read_text(encoding='utf-8')
    defs, bg, flame, fy = parts(src)
    S = 800
    fcx, fcy = 991, fy + 153
    tx, ty = 560 - fcx, 250 - fcy
    size = 104 if len(lines) == 2 else 120
    ys = [612, 716] if len(lines) == 2 else [690]
    title = ''.join(f'<text class="t" x="56" y="{y}" font-size="{size}">{l}</text>' for y, l in zip(ys, lines))
    out = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{S}" height="{S}" viewBox="0 0 {S} {S}" role="img" aria-label="{label}"><title>{label}</title>'
           f'<defs>{defs}<radialGradient id="vigS" cx="400" cy="400" r="580" gradientUnits="userSpaceOnUse"><stop offset=".5" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".6"/></radialGradient>'
           '<linearGradient id="floor" x1="0" y1="0" x2="0" y2="1"><stop offset=".45" stop-color="#07070e" stop-opacity="0"/><stop offset="1" stop-color="#07070e" stop-opacity=".88"/></linearGradient></defs>'
           f'<g transform="translate(-600 0) scale(1.33333)">{bg}</g>'
           f'<rect width="{S}" height="{S}" fill="url(#vigS)"/>'
           f'<g transform="translate({tx} {ty})"><circle cx="991" cy="371" r="200" fill="url(#halo)"/>{flame}</g>'
           f'<rect width="{S}" height="{S}" fill="url(#floor)"/>'
           f'<text class="k" x="56" y="{ys[0] - size - 6}" fill="{accent}" font-size="30">{kicker}</text>{title}'
           f'<rect x="1" y="1" width="{S - 2}" height="{S - 2}" fill="none" stroke="{accent}" stroke-opacity=".3" stroke-width="2"/></svg>')
    # the halo gradient is in user space of the flame position; it moves with the group, so keep it
    (T / 'small').mkdir(exist_ok=True)
    (T / 'small' / f'{name}.svg').write_text(out, encoding='utf-8', newline='\n')


trophy_tile()
small('cadence', 'LOCAL USAGE PAGE', ['Cadence'], '#8f7bff', 'Cadence: streaks, a heatmap and model mix for Hermes.')
small('vibeleak-skills', 'AGENT SKILLS', ['VibeLeak', 'Skills'], '#36d399', 'VibeLeak Skills: agent skills for website trust scans and fixes.')
small('vibeleak-atlas', 'HERMES PLUGIN', ['VibeLeak', 'Atlas'], '#36d399', 'VibeLeak Atlas: a Hermes plugin for owner-approved website assessments and local code review.')
matchcut_tile()
print('ok')
