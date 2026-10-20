"""Generate flat-lay vector illustrations of the race kit (one SVG per item).

Colours are CSS custom properties in KIT_STYLE so the whole set can be
recoloured to match Driver Dave's kit in one place (or per file afterwards).

Usage: python3 make_kit.py [out_dir]
"""
import os
import sys

KIT_STYLE = """
  <style>
    :root {
      --line: #1d1f24;       /* outline */
      --suit: #1f4fa0;       /* race suit main colour */
      --suit-accent: #1d1f24;
      --trim: #f4f2ec;       /* white trim / piping */
      --nomex: #ecebe6;      /* undyed Nomex: balaclava, socks */
      --nomex-shade: #cfccc3;
      --glove: #1d1f24;
      --glove-accent: #c8102e;
      --boot: #1d1f24;
      --boot-accent: #c8102e;
      --sole: #3a3d44;
    }
    .o  { stroke: var(--line); stroke-width: 6; stroke-linejoin: round; stroke-linecap: round; }
    .s  { fill: none; stroke: var(--line); stroke-width: 3; stroke-linecap: round; stroke-dasharray: 2 9; } /* stitching */
    .l  { fill: none; stroke: var(--line); stroke-width: 4; stroke-linecap: round; }
  </style>"""

# Small embroidered homologation label (blank - no FIA artwork reproduced).
LABEL = """
  <g transform="translate({x} {y}) rotate({r})">
    <rect x="-22" y="-14" width="44" height="28" rx="3" fill="#fff" class="o" style="stroke-width:3"/>
    <path d="M-14-5h28M-14 1h20M-14 7h24" stroke="#9aa0a8" stroke-width="2.5"/>
  </g>"""


def svg(w, h, body, title):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n'
        f"  <title>{title}</title>{KIT_STYLE}\n{body}\n</svg>\n"
    )


def suit():
    outline = (
        "M500,88 L440,78 C380,95 330,110 300,122 C255,138 235,160 225,190 L112,540 L205,585 "
        "L330,350 L342,560 L328,1048 L472,1048 L500,655 L528,1048 L672,1048 L658,560 L670,350 "
        "L795,585 L888,540 L775,190 C765,160 745,138 700,122 C670,110 620,95 560,78 Z"
    )
    body = f"""
  <path class="o" fill="var(--suit)" d="{outline}"/>
  <!-- side panels -->
  <path fill="var(--suit-accent)" d="M330,350 L342,560 L328,1048 L372,1048 L384,600 L372,380 Z"/>
  <path fill="var(--suit-accent)" d="M670,350 L658,560 L672,1048 L628,1048 L616,600 L628,380 Z"/>
  <path fill="var(--trim)" d="M372,380 L384,600 L372,1048 L384,1048 L396,600 L384,385 Z"/>
  <path fill="var(--trim)" d="M628,380 L616,600 L628,1048 L616,1048 L604,600 L616,385 Z"/>
  <!-- arm stripes -->
  <path fill="var(--suit-accent)" d="M225,190 L112,540 L150,558 L262,205 Z"/>
  <path fill="var(--suit-accent)" d="M775,190 L888,540 L850,558 L738,205 Z"/>
  <!-- belt -->
  <path class="o" fill="var(--suit-accent)" d="M341,520 L659,520 L658,562 L342,562 Z"/>
  <!-- knit cuffs -->
  <path class="o" fill="var(--suit-accent)" d="M112,540 L205,585 L222,553 L123,507 Z"/>
  <path class="o" fill="var(--suit-accent)" d="M888,540 L795,585 L778,553 L877,507 Z"/>
  <path class="o" fill="var(--suit-accent)" d="M329,1010 L475,1010 L472,1048 L328,1048 Z"/>
  <path class="o" fill="var(--suit-accent)" d="M671,1010 L525,1010 L528,1048 L672,1048 Z"/>
  <!-- epaulettes (rescue handles) -->
  <path class="o" fill="var(--trim)" d="M440,92 L310,132 L316,150 L446,110 Z"/>
  <path class="o" fill="var(--trim)" d="M560,92 L690,132 L684,150 L554,110 Z"/>
  <!-- collar -->
  <path class="o" fill="var(--suit-accent)" d="M440,78 Q500,102 560,78 L556,46 Q500,68 444,46 Z"/>
  <!-- zip -->
  <path class="l" d="M500,96 V520"/>
  <rect x="490" y="104" width="20" height="30" rx="4" fill="var(--trim)" class="o" style="stroke-width:4"/>
  <!-- crotch / leg seams -->
  <path class="s" d="M500,562 V650"/>
  <path class="s" d="M342,575 L335,1000 M658,575 L665,1000"/>
  {LABEL.format(x=560, y=170, r=0)}
"""
    return svg(1000, 1100, body, "Race suit (flat-lay)")


def glove_path():
    return (
        "M75,400 L65,290 L22,225 Q8,200 28,186 Q48,176 64,196 L100,240 "
        "L100,105 Q100,80 124,80 Q148,80 148,105 "
        "L148,82 Q148,55 172,55 Q196,55 196,82 "
        "L196,95 Q196,70 219,70 Q242,70 242,95 "
        "L242,140 Q242,118 262,118 Q282,118 282,140 "
        "L282,300 L265,400 Z"
    )


def gloves():
    one = f"""
    <path class="o" fill="var(--glove)" d="{glove_path()}"/>
    <!-- knuckle pad -->
    <rect x="104" y="232" width="172" height="44" rx="20" fill="var(--glove-accent)" class="o" style="stroke-width:4"/>
    <!-- finger seams -->
    <path class="l" style="stroke:#5a5e66" d="M148,108 V226 M196,98 V226 M242,142 V226"/>
    <!-- cuff -->
    <path class="o" fill="var(--glove-accent)" d="M75,400 L265,400 L280,520 L60,520 Z"/>
    <path class="s" style="stroke:var(--trim)" d="M80,420 H262"/>
    {LABEL.format(x=170, y=470, r=0)}"""
    body = f"""
  <g transform="translate(40 30)">{one}
  </g>
  <g transform="translate(760 30) scale(-1 1)">{one}
  </g>"""
    return svg(800, 580, body, "Race gloves (pair, flat-lay)")


def socks():
    one = """
    <path class="o" fill="var(--nomex)" d="M60,40 L180,40 L180,470 Q180,500 210,505 L330,520 Q372,528 372,565 Q372,602 330,602 L120,602 Q60,602 60,540 Z"/>
    <!-- heel + toe reinforcement -->
    <path fill="var(--nomex-shade)" d="M60,520 Q60,602 120,602 L150,602 Q110,570 112,520 Z"/>
    <path fill="var(--nomex-shade)" d="M320,522 Q372,528 372,565 Q372,602 330,602 L318,602 Q340,565 320,522 Z"/>
    <path class="o" fill="none" d="M60,40 L180,40 L180,470 Q180,500 210,505 L330,520 Q372,528 372,565 Q372,602 330,602 L120,602 Q60,602 60,540 Z"/>
    <!-- ribbed cuff -->
    <path class="o" fill="var(--nomex-shade)" d="M60,40 H180 V100 H60 Z"/>
    <path class="l" style="stroke-width:3;stroke:#a9a59b" d="M80,48 V92 M100,48 V92 M120,48 V92 M140,48 V92 M160,48 V92"/>
    """ + LABEL.format(x=120, y=140, r=0)
    body = f"""
  <g transform="translate(0 0)">{one}</g>
  <g transform="translate(300 60)">{one}</g>"""
    return svg(700, 690, body, "Fireproof socks (pair, flat-lay)")


def boots():
    one = """
    <!-- sole -->
    <path class="o" fill="var(--sole)" d="M52,408 L438,408 Q446,408 444,420 L440,432 Q438,440 428,440 L60,440 Q50,440 50,430 Z"/>
    <path class="o" fill="var(--boot)" d="M90,60 L222,60 L232,248 Q300,298 380,318 Q434,332 436,378 L438,408 L52,408 Q46,330 68,250 Z"/>
    <!-- toe cap + heel counter -->
    <path class="o" fill="var(--boot-accent)" d="M330,300 Q300,340 312,408 L438,408 L436,378 Q434,332 380,318 Q352,311 330,300 Z"/>
    <path class="o" fill="var(--boot-accent)" d="M52,408 Q46,330 68,250 L110,258 Q96,330 108,408 Z"/>
    <!-- ankle strap -->
    <path class="o" fill="var(--trim)" d="M80,170 L228,180 L230,214 L76,206 Z"/>
    <!-- collar padding + heel pull tab -->
    <path class="o" fill="var(--boot-accent)" d="M90,60 L222,60 L223,80 L91,80 Z"/>
    <path d="M92,66 C64,62 60,100 90,104" fill="none" stroke="var(--line)" stroke-width="16" stroke-linecap="round"/>
    <path d="M92,66 C64,62 60,100 90,104" fill="none" stroke="var(--boot-accent)" stroke-width="8" stroke-linecap="round"/>
    <path class="s" style="stroke:#8a8e96" d="M240,262 Q300,310 380,330"/>
    """ + LABEL.format(x=150, y=120, r=0)
    body = f"""
  <g transform="translate(400 30)">{one}</g>
  <g transform="translate(10 50)">{one}</g>"""
    return svg(900, 520, body, "Race boots (pair, flat-lay)")


def balaclava():
    outline = (
        "M260,40 C380,40 430,140 430,260 L430,420 Q430,470 470,520 L500,640 Q260,690 20,640 "
        "L50,520 Q90,470 90,420 L90,260 C90,140 140,40 260,40 Z"
    )
    body = f"""
  <path class="o" fill="var(--nomex)" d="{outline}"/>
  <!-- neck flare shading -->
  <path fill="var(--nomex-shade)" d="M90,470 Q260,500 430,470 Q440,500 470,520 L500,640 Q260,690 20,640 L50,520 Q80,500 90,470 Z" opacity=".55"/>
  <path class="o" fill="none" d="{outline}"/>
  <!-- eye opening (shows the inside back of the hood) -->
  <rect x="140" y="225" width="240" height="110" rx="50" fill="var(--nomex-shade)" class="o"/>
  <rect x="140" y="225" width="240" height="110" rx="50" fill="none" class="s"/>
  <!-- seams -->
  <path class="s" d="M260,48 V218"/>
  <path class="s" d="M95,430 Q260,465 425,430"/>
  {LABEL.format(x=260, y=590, r=0)}
"""
    return svg(520, 700, body, "Balaclava (flat-lay)")


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "kit"
    os.makedirs(out, exist_ok=True)
    for name, fn in [
        ("01-balaclava", balaclava),
        ("02-race-suit", suit),
        ("03-gloves", gloves),
        ("04-socks", socks),
        ("05-boots", boots),
    ]:
        with open(os.path.join(out, f"{name}.svg"), "w") as f:
            f.write(fn())


if __name__ == "__main__":
    main()
