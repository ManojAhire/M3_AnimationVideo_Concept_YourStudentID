import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation, FFMpegWriter

# ============================================================
# 1. CONFIGURATION (Exact 16:9 1080p & 6:52.32 Duration)
# ============================================================
STUDENT_NAME = "Manoj Lahu Ahire"
STUDENT_ID = "E25B070628"

FPS = 24                 # Set to 24 for ultra-smooth final render (~7-8 min on Colab)
DURATION = 412.32        # Exact match to video_1.mp4 (6 min 52.32 sec)
TOTAL_FRAMES = int(round(FPS * DURATION))
SHOW_CAPTIONS = True     # Set to False if you prefer no bottom caption bar
OUTPUT_VIDEO = "M3_Derivative_Animation_Silent.mp4"

# Modern Dark Theme Palette
BG = "#0F172A"           # Deep navy-slate canvas
PANEL = "#1E293B"        # Elevated card fill
PLOT_BG = "#0B1220"      # Crisp dark graph background
BORDER = "#334155"       # Subtle border
WHITE = "#F8FAFC"        # Primary text & parabola
MUTED = "#94A3B8"        # Secondary text & axes
BLUE = "#38BDF8"         # Fixed point P(1, 1) & headers
ORANGE = "#F59E0B"       # Moving point Q, secant line, highlights
GREEN = "#22C55E"        # Tangent line & final derivative f'(1) = 2
RED = "#EF4444"          # Factor cancellation slashes
PURPLE = "#A78BFA"       # Secondary accent

# ============================================================
# 2. EXACT CAPTIONS SYNCED TO YOUR VOICEOVER (video_1.mp4)
# ============================================================
CAPTIONS = [
    (0, 13, "Hello. This video explains the derivative as a rate of change using the simple curve\nf(x) = x² to understand how a curve can have a slope at one exact point."),
    (13, 24, "A straight line has one fixed slope, whereas a curve changes direction as we move along it.\nSo what does slope mean at just one point on a curve?"),
    (24, 35, "We will answer this for the point P = (1, 1) on the curve f(x) = x²."),
    (35, 48, "Our function is f(x) = x². Choose a fixed point P = (1, f(1)) = (1, 1)."),
    (48, 63, "Take a second point Q = (a, f(a)) = (a, a²).\nThe line passing through P and Q is called a secant line."),
    (63, 81, "Taking a = 3, Q becomes (3, 9). The secant line joining (1, 1) and (3, 9) looks steep."),
    (81, 101, "We calculate the slope as (9 - 1) / (3 - 1) = 8 / 2 = 4."),
    (101, 106, "Because Q is far from P, the secant line is steep."),
    (106, 118, "Now take a = 2, which makes Q = (2, 4)."),
    (118, 131, "The line joining (1, 1) and (2, 4) has slope (4 - 1) / (2 - 1) = 3."),
    (131, 138, "Here Q moves closer to P, and the secant line becomes less steep."),
    (138, 151, "Moving Q even closer with a = 1.5 gives Q = (1.5, 2.25).\nThe line joining these points is much less steep than before."),
    (151, 171, "Its slope is (2.25 - 1) / (1.5 - 1) = 1.25 / 0.5 = 2.5."),
    (171, 188, "Moving further to a = 1.1 makes Q = (1.1, 1.21).\nNow the secant line joining these two points is almost tangent."),
    (188, 207, "Calculating the slope: (1.21 - 1) / (1.1 - 1) = 0.21 / 0.1 = 2.1."),
    (207, 223, "Now let's find the general secant slope formula: m = (y₂ - y₁) / (x₂ - x₁).\nWith P = (1, 1) and Q = (a, a²), this becomes m = (a² - 1) / (a - 1)."),
    (223, 245, "Factoring the numerator gives m = (a - 1)(a + 1) / (a - 1)."),
    (245, 268, "Canceling (a - 1) leaves m = a + 1 (when a ≠ 1).\nKey idea: canceling (a - 1) makes the slope easy to evaluate."),
    (268, 286, "At a = 3 → m = 4; a = 2 → m = 3; a = 1.5 → m = 2.5; a = 1.1 → m = 2.1; a = 1.01 → m = 2.01."),
    (286, 296, "As a gets closer to 1, the secant slope approaches 2.\nThe exact value 2 is the limiting slope."),
    (296, 319, "The derivative at x = 1 is the limit of the secant slope as Q approaches P:\nf'(1) = lim (a → 1) (a + 1) = 2."),
    (319, 331, "Therefore f'(1) = 2. This is the exact slope of the tangent line at point P."),
    (331, 360, "At x = 1, the tangent slope is 2. Using the point-slope formula: y - y₀ = m(x - x₀)."),
    (360, 381, "Substituting (1, 1) and m = 2 gives y - 1 = 2(x - 1), which simplifies to y = 2x - 1."),
    (381, 391, "Near x = 1, an increase of 0.1 in x gives about a 0.2 increase in f(x)."),
    (391, 413, "Three things to remember: 1) A secant joins two points. 2) As Q → P, secant slope → tangent slope.\n3) For f(x) = x², the derivative at x = 1 is 2. Thank you!")
]

# ============================================================
# 3. HELPER UTILITIES (Smooth Easing, Cards, Captions, Axes)
# ============================================================
def smoothstep(t, t0, t1):
    """Smooth cubic ease-in-out between 0 and 1 over [t0, t1]."""
    if t <= t0:
        return 0.0
    if t >= t1:
        return 1.0
    u = (t - t0) / (t1 - t0)
    return u * u * (3.0 - 2.0 * u)

def lerp(a, b, u):
    return a + (b - a) * u

def card(ax, x, y, w, h, fc=PANEL, ec=BORDER, lw=1.8, rad=0.025, alpha=1.0, zorder=1):
    patch = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.0,rounding_size={rad}",
        facecolor=fc, edgecolor=ec, linewidth=lw, alpha=alpha, zorder=zorder
    )
    ax.add_patch(patch)
    return patch

def style_axes(ax, xlim=(0, 3.4), ylim=(-0.4, 10.5), xlabel="x", ylabel="y = f(x)"):
    ax.set_facecolor(PLOT_BG)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.grid(True, color="#1E293B", linestyle="--", linewidth=0.9)
    ax.axhline(0, color="#475569", lw=1.2)
    ax.axvline(0, color="#475569", lw=1.2)
    ax.tick_params(colors=MUTED, labelsize=11)
    for sp in ax.spines.values():
        sp.set_color(BORDER)
        sp.set_linewidth(1.4)
    if xlabel:
        ax.set_xlabel(xlabel, color=WHITE, fontsize=13, fontweight="bold")
    if ylabel:
        ax.set_ylabel(ylabel, color=WHITE, fontsize=13, fontweight="bold")

def draw_header(fig, scene_tag, title, subtitle=""):
    fig.text(0.04, 0.955, scene_tag.upper(), color=BLUE, fontsize=11, fontweight="bold", ha="left")
    fig.text(0.04, 0.912, title, color=WHITE, fontsize=22, fontweight="bold", ha="left")
    if subtitle:
        fig.text(0.96, 0.916, subtitle, color=MUTED, fontsize=13, ha="right")
    line_ax = fig.add_axes([0.04, 0.892, 0.92, 0.004])
    line_ax.axis("off")
    line_ax.axhline(0.5, color=BORDER, lw=1.5)

def draw_caption_bar(fig, t):
    if not SHOW_CAPTIONS:
        return
    txt = ""
    for s, e, c in CAPTIONS:
        if s <= t < e:
            txt = c
            break
    if not txt:
        return
    ax_c = fig.add_axes([0.04, 0.015, 0.92, 0.105])
    ax_c.set_xlim(0, 1)
    ax_c.set_ylim(0, 1)
    ax_c.axis("off")
    card(ax_c, 0.0, 0.05, 1.0, 0.90, fc="#020617", ec=BORDER, lw=1.4, rad=0.02, alpha=0.94)
    ax_c.text(0.5, 0.5, txt, color=WHITE, fontsize=13.5, ha="center", va="center", linespacing=1.35)

# ============================================================
# 4. MASTER FRAME RENDERER (All 6 Scenes, 0s -> 412.32s)
# ============================================================
fig = plt.figure(figsize=(16, 9), dpi=120, facecolor=BG)

def render_frame(frame_idx):
    t = frame_idx / FPS
    fig.clf()
    fig.patch.set_facecolor(BG)

    # --------------------------------------------------------
    # OPENING TITLE CARD (0:00 – 0:13)
    # --------------------------------------------------------
    if t < 13.0:
        ax_l = fig.add_axes([0.04, 0.15, 0.50, 0.78], facecolor=BG)
        ax_l.set_xlim(0, 1)
        ax_l.set_ylim(0, 1)
        ax_l.axis("off")

        card(ax_l, 0.02, 0.83, 0.42, 0.08, fc="#172554", ec=BLUE, lw=1.5, rad=0.02)
        ax_l.text(0.23, 0.87, "M3 INTERNAL ASSESSMENT", color=BLUE, fontsize=12, fontweight="bold", ha="center", va="center")

        ax_l.text(0.02, 0.67, "DERIVATIVE AS\nRATE OF CHANGE", color=WHITE, fontsize=36, fontweight="bold", va="center", linespacing=1.18)
        ax_l.text(0.02, 0.46, "How a moving secant line becomes a tangent", color=BLUE, fontsize=18, fontweight="medium", va="center")
        ax_l.text(0.02, 0.37, r"A visual explanation using $f(x) = x^2$ at $P(1, 1)$", color=MUTED, fontsize=15.5, va="center")

        ax_l.plot([0.02, 0.88], [0.27, 0.27], color=BORDER, lw=1.8)
        ax_l.text(0.02, 0.18, f"Student: {STUDENT_NAME}", color=WHITE, fontsize=15, fontweight="bold")
        ax_l.text(0.02, 0.11, f"Student ID: {STUDENT_ID}", color=MUTED, fontsize=14)

        # Animated Hero Graph on Right
        ax_r = fig.add_axes([0.56, 0.18, 0.40, 0.72])
        style_axes(ax_r, xlim=(-0.2, 3.3), ylim=(-0.5, 10.2), xlabel="x", ylabel="f(x)")
        xs = np.linspace(0, 3.2, 250)
        ax_r.plot(xs, xs**2, color=BLUE, lw=3.2)

        # Smooth preview sweep of Q -> P
        u = smoothstep(t, 1.5, 11.5)
        a_val = lerp(2.9, 1.001, u)
        slope = a_val + 1.0
        lx = np.linspace(0.0, 3.2, 100)
        line_col = GREEN if u > 0.92 else ORANGE
        ax_r.plot(lx, 1.0 + slope * (lx - 1.0), color=line_col, lw=2.8)
        ax_r.scatter([1], [1], color=WHITE, edgecolor=BLUE, s=110, lw=2.5, zorder=6)
        if u <= 0.95:
            ax_r.scatter([a_val], [a_val**2], color=ORANGE, s=100, zorder=6)
        ax_r.text(0.15, 8.8, f"Live Slope = {slope:.2f}", color=line_col, fontsize=14, fontweight="bold",
                  bbox=dict(boxstyle="round,pad=0.35", facecolor=PANEL, edgecolor=line_col, lw=1.8))

    # --------------------------------------------------------
    # SCENE 1: HOOK / CONTEXT (0:13 – 0:35)
    # --------------------------------------------------------
    elif t < 35.0:
        draw_header(fig, "Scene 1 | Hook & Context", "Can a Curved Graph Have a Slope?", "Straight Line vs. Curve")

        if t < 23.5:
            # Left: Straight line with constant slope
            ax1 = fig.add_axes([0.06, 0.18, 0.41, 0.65])
            style_axes(ax1, xlim=(0, 4), ylim=(0, 8), xlabel="x", ylabel="y")
            ax1.set_title("Straight Line: ONE Fixed Slope", color=BLUE, fontsize=15, fontweight="bold", pad=10)
            xs = np.linspace(0, 4, 100)
            ax1.plot(xs, 1.5 * xs + 1, color=BLUE, lw=3.2)

            # Two identical rise/run triangles
            for x0 in [0.8, 2.2]:
                y0 = 1.5 * x0 + 1
                ax1.plot([x0, x0 + 1], [y0, y0], color=GREEN, lw=2.2, ls="--")
                ax1.plot([x0 + 1, x0 + 1], [y0, y0 + 1.5], color=GREEN, lw=2.2, ls="--")
                ax1.text(x0 + 0.5, y0 - 0.45, "+1", color=GREEN, fontsize=12, fontweight="bold", ha="center")
                ax1.text(x0 + 1.15, y0 + 0.75, "+1.5", color=GREEN, fontsize=12, fontweight="bold", va="center")
            ax1.text(0.25, 6.8, "Slope = 1.5 everywhere", color=WHITE, fontsize=13.5, fontweight="bold",
                     bbox=dict(boxstyle="round,pad=0.35", facecolor=PANEL, edgecolor=BLUE, lw=1.6))

            # Right: Curve changing direction dynamically
            ax2 = fig.add_axes([0.54, 0.18, 0.41, 0.65])
            style_axes(ax2, xlim=(0, 3.3), ylim=(0, 10.5), xlabel="x", ylabel="f(x)")
            ax2.set_title(r"Curve $f(x) = x^2$: Direction Changes Constantly", color=ORANGE, fontsize=15, fontweight="bold", pad=10)
            xs2 = np.linspace(0, 3.2, 200)
            ax2.plot(xs2, xs2**2, color=WHITE, lw=3.2)

            # Moving dot with live tangent segment tilting steeper
            u = smoothstep(t, 14.5, 22.8)
            xm = lerp(0.3, 2.8, u)
            ym = xm**2
            sl = 2 * xm
            dx = 0.55 / np.sqrt(1 + sl**2)
            ax2.plot([xm - dx, xm + dx], [ym - sl * dx, ym + sl * dx], color=ORANGE, lw=3.5, zorder=5)
            ax2.scatter([xm], [ym], color=ORANGE, s=115, zorder=6)
            ax2.text(0.2, 8.8, f"At x = {xm:.1f}, slope = {sl:.1f}\n(Always changing!)", color=ORANGE,
                     fontsize=13.5, fontweight="bold",
                     bbox=dict(boxstyle="round,pad=0.35", facecolor=PANEL, edgecolor=ORANGE, lw=1.6))
        else:
            # Focus on P = (1, 1) question
            ax_txt = fig.add_axes([0.04, 0.16, 0.42, 0.70], facecolor=BG)
            ax_txt.set_xlim(0, 1)
            ax_txt.set_ylim(0, 1)
            ax_txt.axis("off")

            ax_txt.text(0.02, 0.84, "Look at this curve:", color=WHITE, fontsize=22, fontweight="bold")
            ax_txt.text(0.02, 0.72, r"$f(x) = x^2$", color=BLUE, fontsize=30, fontweight="bold")
            ax_txt.text(0.02, 0.55, "At the single point P = (1, 1),\nwhat should its slope be?",
                        color=WHITE, fontsize=18, linespacing=1.4)

            card(ax_txt, 0.02, 0.18, 0.94, 0.25, fc="#0C223A", ec=BLUE, lw=2.2, rad=0.03)
            ax_txt.text(0.49, 0.305, "Core Question:\nWhat is the slope of a curve\nat exactly ONE point?",
                        color=BLUE, fontsize=16, fontweight="bold", ha="center", va="center", linespacing=1.35)

            ax_g = fig.add_axes([0.50, 0.18, 0.45, 0.67])
            style_axes(ax_g, xlim=(0, 3.3), ylim=(-0.3, 10.5))
            xs = np.linspace(0, 3.2, 250)
            ax_g.plot(xs, xs**2, color=WHITE, lw=3.2)

            # Pulsing halo around P(1, 1)
            pulse = 180 + 130 * np.sin((t - 23.5) * 5.0)
            ax_g.scatter([1], [1], color=BLUE, s=pulse, alpha=0.35, zorder=4)
            ax_g.scatter([1], [1], color=BLUE, s=110, zorder=6)
            ax_g.plot([1, 1], [0, 1], color=BLUE, ls=":", lw=1.6)
            ax_g.plot([0, 1], [1, 1], color=BLUE, ls=":", lw=1.6)
            ax_g.text(1.18, 1.35, "P = (1, 1)  Slope = ?", color=ORANGE, fontsize=15, fontweight="bold",
                      bbox=dict(boxstyle="round,pad=0.3", facecolor=PANEL, edgecolor=ORANGE, lw=1.6))

    # --------------------------------------------------------
    # SCENE 2: CONCEPT INTRODUCTION (0:35 – 1:03)
    # --------------------------------------------------------
    elif t < 63.0:
        draw_header(fig, "Scene 2 | Concept Introduction", "Start with a Simple Function & Secant Line", r"$f(x) = x^2$")

        ax_txt = fig.add_axes([0.04, 0.16, 0.41, 0.70], facecolor=BG)
        ax_txt.set_xlim(0, 1)
        ax_txt.set_ylim(0, 1)
        ax_txt.axis("off")

        card(ax_txt, 0.02, 0.75, 0.95, 0.20, fc=PANEL, ec=WHITE, lw=1.6, rad=0.025)
        ax_txt.text(0.07, 0.88, "Function:", color=MUTED, fontsize=13, fontweight="bold")
        ax_txt.text(0.07, 0.79, r"$f(x) = x^2$", color=WHITE, fontsize=24, fontweight="bold")

        if t >= 40.0:
            card(ax_txt, 0.02, 0.51, 0.95, 0.20, fc="#0C223A", ec=BLUE, lw=1.8, rad=0.025)
            ax_txt.text(0.07, 0.64, "1. Choose a fixed point:", color=BLUE, fontsize=13, fontweight="bold")
            ax_txt.text(0.07, 0.55, r"$P = (1,\ f(1)) = (1,\ 1)$", color=WHITE, fontsize=19, fontweight="bold")

        if t >= 48.5:
            card(ax_txt, 0.02, 0.27, 0.95, 0.20, fc="#291E0E", ec=ORANGE, lw=1.8, rad=0.025)
            ax_txt.text(0.07, 0.40, "2. Choose a movable point:", color=ORANGE, fontsize=13, fontweight="bold")
            ax_txt.text(0.07, 0.31, r"$Q = (a,\ f(a)) = (a,\ a^2)$", color=WHITE, fontsize=19, fontweight="bold")

        if t >= 57.0:
            card(ax_txt, 0.02, 0.04, 0.95, 0.18, fc="#0B2918", ec=GREEN, lw=2.0, rad=0.025)
            ax_txt.text(0.495, 0.13, "The line through P and Q\nis called a SECANT LINE.",
                        color=GREEN, fontsize=15.5, fontweight="bold", ha="center", va="center", linespacing=1.35)

        ax_g = fig.add_axes([0.49, 0.18, 0.46, 0.67])
        style_axes(ax_g, xlim=(0, 3.4), ylim=(-0.4, 10.5))

        # Progressive curve draw
        u_curve = smoothstep(t, 35.0, 40.5)
        xs = np.linspace(0, 3.25 * max(0.05, u_curve), 250)
        ax_g.plot(xs, xs**2, color=WHITE, lw=3.2)
        if u_curve > 0.7:
            ax_g.text(2.8, 9.6, r"$f(x) = x^2$", color=WHITE, fontsize=15, fontweight="bold")

        if t >= 40.0:
            ax_g.plot([1, 1], [0, 1], color=BLUE, ls=":", lw=1.5)
            ax_g.plot([0, 1], [1, 1], color=BLUE, ls=":", lw=1.5)
            ax_g.scatter([1], [1], color=BLUE, s=115, zorder=6)
            ax_g.text(1.12, 0.65, "P(1, 1)", color=BLUE, fontsize=14, fontweight="bold")

        if t >= 48.5:
            # Glide Q gently along curve before settling at a = 3
            a_val = 2.4 + 0.55 * np.sin((t - 48.5) * 0.9) if t < 58.0 else lerp(2.4 + 0.55 * np.sin(9.5 * 0.9), 3.0, smoothstep(t, 58.0, 62.5))
            ax_g.scatter([a_val], [a_val**2], color=ORANGE, s=115, zorder=6)
            ax_g.text(a_val - 0.78, a_val**2 + 0.35, r"$Q(a, a^2)$", color=ORANGE, fontsize=14, fontweight="bold")

            if t >= 57.0:
                sl = a_val + 1.0
                lx = np.linspace(0.2, 3.3, 100)
                ax_g.plot(lx, 1.0 + sl * (lx - 1.0), color=ORANGE, lw=2.8, zorder=4)
                ax_g.text(1.75, 1.0 + sl * 0.75 + 1.1, "Secant Line", color=ORANGE, fontsize=14, fontweight="bold",
                          bbox=dict(boxstyle="round,pad=0.25", facecolor=PANEL, edgecolor=ORANGE, lw=1.4))

    # --------------------------------------------------------
    # SCENE 3: VISUAL INTUITION (1:03 – 3:27)
    # Smooth sliding Q -> P across a = 3, 2, 1.5, 1.1
    # --------------------------------------------------------
    elif t < 207.0:
        # Determine stage, current animated a_val, ghosts, and calc step timing
        ghosts = []
        if t < 106.0:
            stage_title = "Move Q Towards P: a = 3"
            subtitle = "Stage 1 of 4  |  Q is far from P"
            a_val = 3.0
            calc_t1, calc_t2, note_t = 81.0, 92.0, 100.0
            q_label = "Q = (3, 9)"
            eq1 = r"$m = \frac{9 - 1}{3 - 1}$"
            eq2 = r"$= \frac{8}{2} = 4$"
            slope_badge = "Slope = 4"
            note_txt = "Q is far from P.\nThe secant line is very steep."
            show_zoom = False
        elif t < 138.0:
            stage_title = "Move Q Closer: a = 2"
            subtitle = "Stage 2 of 4  |  Less steep"
            ghosts = [3.0]
            a_val = lerp(3.0, 2.0, smoothstep(t, 106.0, 113.5))
            calc_t1, calc_t2, note_t = 117.0, 123.0, 128.0
            q_label = "Q = (2, 4)"
            eq1 = r"$m = \frac{4 - 1}{2 - 1}$"
            eq2 = r"$= \frac{3}{1} = 3$"
            slope_badge = "Slope = 3"
            note_txt = "Q moves closer to P.\nSlope drops from 4 to 3."
            show_zoom = False
        elif t < 171.0:
            stage_title = "Move Q Even Closer: a = 1.5"
            subtitle = "Stage 3 of 4  |  Getting nearer to 2"
            ghosts = [3.0, 2.0]
            a_val = lerp(2.0, 1.5, smoothstep(t, 138.0, 145.5))
            calc_t1, calc_t2, note_t = 156.0, 165.0, 148.0
            q_label = "Q = (1.5, 2.25)"
            eq1 = r"$m = \frac{2.25 - 1}{1.5 - 1}$"
            eq2 = r"$= \frac{1.25}{0.5} = 2.5$"
            slope_badge = "Slope = 2.5"
            note_txt = "Much less steep than before.\nSlope drops from 3 to 2.5."
            show_zoom = False
        else:
            stage_title = "Q Very Close to P: a = 1.1"
            subtitle = "Stage 4 of 4  |  Almost tangent!"
            ghosts = [3.0, 2.0, 1.5]
            a_val = lerp(1.5, 1.1, smoothstep(t, 171.0, 179.0))
            calc_t1, calc_t2, note_t = 191.0, 199.0, 182.0
            q_label = "Q = (1.1, 1.21)"
            eq1 = r"$m = \frac{1.21 - 1}{1.1 - 1}$"
            eq2 = r"$= \frac{0.21}{0.1} = 2.1$"
            slope_badge = "Slope = 2.1"
            note_txt = "Q is right next to P.\nThe secant is almost tangent!"
            show_zoom = t >= 179.0

        draw_header(fig, "Scene 3 | Visual Intuition", stage_title, subtitle)

        # Left Info & Animated Calculation Panel
        ax_l = fig.add_axes([0.04, 0.16, 0.39, 0.70], facecolor=BG)
        ax_l.set_xlim(0, 1)
        ax_l.set_ylim(0, 1)
        ax_l.axis("off")

        card(ax_l, 0.02, 0.76, 0.45, 0.20, fc="#0C223A", ec=BLUE, lw=1.6, rad=0.025)
        ax_l.text(0.245, 0.90, "Fixed Point", color=BLUE, fontsize=12, fontweight="bold", ha="center")
        ax_l.text(0.245, 0.81, "P = (1, 1)", color=WHITE, fontsize=17, fontweight="bold", ha="center")

        card(ax_l, 0.51, 0.76, 0.47, 0.20, fc="#291E0E", ec=ORANGE, lw=1.6, rad=0.025)
        ax_l.text(0.745, 0.90, "Moving Point", color=ORANGE, fontsize=12, fontweight="bold", ha="center")
        ax_l.text(0.745, 0.81, q_label, color=WHITE, fontsize=16, fontweight="bold", ha="center")

        # Calculation Card (Replaces hand-drawn scribbles!)
        card(ax_l, 0.02, 0.31, 0.96, 0.41, fc=PANEL, ec=BORDER, lw=1.8, rad=0.025)
        ax_l.text(0.07, 0.65, "Secant Slope Calculation:", color=MUTED, fontsize=13, fontweight="bold")
        live_slope = a_val + 1.0
        if t < calc_t1:
            ax_l.text(0.50, 0.49, f"Live Slope = {live_slope:.2f}", color=ORANGE, fontsize=22, fontweight="bold", ha="center")
        else:
            ax_l.text(0.08, 0.52, eq1, color=WHITE, fontsize=23, va="center")
            if t >= calc_t2:
                ax_l.text(0.52, 0.52, eq2, color=GREEN if show_zoom else ORANGE, fontsize=23, fontweight="bold", va="center")
                badge_col = GREEN if show_zoom else ORANGE
                card(ax_l, 0.16, 0.34, 0.68, 0.11, fc="#0B2918" if show_zoom else "#291E0E", ec=badge_col, lw=2.0, rad=0.02)
                ax_l.text(0.50, 0.395, slope_badge, color=badge_col, fontsize=18, fontweight="bold", ha="center", va="center")

        if t >= note_t:
            card(ax_l, 0.02, 0.05, 0.96, 0.21, fc="#131F36", ec=BLUE, lw=1.6, rad=0.025)
            ax_l.text(0.50, 0.155, note_txt, color=WHITE, fontsize=14.5, ha="center", va="center", linespacing=1.4)

        # Right Main Graph
        ax_g = fig.add_axes([0.47, 0.18, 0.49, 0.67])
        style_axes(ax_g, xlim=(0, 3.4), ylim=(-0.4, 10.5))
        xs = np.linspace(0, 3.25, 250)
        ax_g.plot(xs, xs**2, color=WHITE, lw=3.2)

        lx = np.linspace(0.1, 3.35, 100)
        # Draw faint ghost trails of previous secant lines
        for ga in ghosts:
            g_sl = ga + 1.0
            ax_g.plot(lx, 1.0 + g_sl * (lx - 1.0), color=MUTED, lw=1.5, ls=":", alpha=0.38, zorder=2)

        # Current secant line & rise/run triangle
        sl = a_val + 1.0
        lcol = "#84CC16" if show_zoom else ORANGE
        ax_g.plot(lx, 1.0 + sl * (lx - 1.0), color=lcol, lw=3.0, zorder=4)

        # Rise/Run triangle when big enough to read cleanly
        if a_val >= 1.45:
            ax_g.plot([1.0, a_val], [1.0, 1.0], color=BLUE, lw=2.0, ls="--", zorder=3)
            ax_g.plot([a_val, a_val], [1.0, a_val**2], color=ORANGE, lw=2.0, ls="--", zorder=3)
            ax_g.text((1.0 + a_val)/2, 0.45, f"Δx = {a_val - 1:.1f}", color=BLUE, fontsize=11.5, fontweight="bold", ha="center")
            ax_g.text(a_val + 0.08, (1.0 + a_val**2)/2, f"Δy = {a_val**2 - 1:.2f}", color=ORANGE, fontsize=11.5, fontweight="bold", va="center")

        ax_g.scatter([1], [1], color=BLUE, s=115, zorder=6)
        ax_g.scatter([a_val], [a_val**2], color=lcol, s=115, zorder=6)
        ax_g.text(1.06, 0.42 if a_val < 1.45 else 1.25, "P(1, 1)", color=BLUE, fontsize=12.5, fontweight="bold")
        if a_val >= 1.45:
            ax_g.text(a_val - 0.85, a_val**2 + 0.35, f"Q({a_val:.1f}, {a_val**2:.2f})", color=ORANGE, fontsize=12.5, fontweight="bold")

        # Zoom-In Magnifier Inset for a = 1.1!
        if show_zoom:
            ax_in = fig.add_axes([0.50, 0.51, 0.21, 0.30])
            style_axes(ax_in, xlim=(0.88, 1.22), ylim=(0.75, 1.48), xlabel="", ylabel="")
            ax_in.set_title("Zoomed In Near P(1, 1)", color=GREEN, fontsize=10.5, fontweight="bold", pad=5)
            xz = np.linspace(0.85, 1.25, 120)
            ax_in.plot(xz, xz**2, color=WHITE, lw=2.8)
            ax_in.plot(xz, 1.0 + sl * (xz - 1.0), color=lcol, lw=2.6)
            ax_in.plot([1.0, 1.1], [1.0, 1.0], color=BLUE, ls="--", lw=1.6)
            ax_in.plot([1.1, 1.1], [1.0, 1.21], color=lcol, ls="--", lw=1.6)
            ax_in.scatter([1.0], [1.0], color=BLUE, s=80, zorder=6)
            ax_in.scatter([1.1], [1.21], color=lcol, s=80, zorder=6)
            ax_in.text(0.91, 1.04, "P(1,1)", color=BLUE, fontsize=9.5, fontweight="bold")
            ax_in.text(1.11, 1.25, "Q(1.1,1.21)", color=lcol, fontsize=9.5, fontweight="bold")
            for sp in ax_in.spines.values():
                sp.set_color(GREEN)
                sp.set_linewidth(2.0)

    # --------------------------------------------------------
    # SCENE 4A: WORKED EXAMPLE — ALGEBRAIC FORMULA (3:27 – 4:28)
    # --------------------------------------------------------
    elif t < 268.0:
        draw_header(fig, "Scene 4 | Worked Example", "Now Calculate the General Secant Slope", r"$P=(1,1),\ Q=(a,a^2)$")

        # Left Reference Graph
        ax_g = fig.add_axes([0.05, 0.20, 0.34, 0.63])
        style_axes(ax_g, xlim=(0, 3.2), ylim=(-0.3, 9.8))
        xs = np.linspace(0, 3.1, 200)
        ax_g.plot(xs, xs**2, color=WHITE, lw=2.8)
        a_demo = 2.4
        lx = np.linspace(0.2, 3.1, 100)
        ax_g.plot(lx, 1 + (a_demo + 1)*(lx - 1), color=ORANGE, lw=2.6)
        ax_g.plot([1, a_demo], [1, 1], color=BLUE, ls="--", lw=2.0)
        ax_g.plot([a_demo, a_demo], [1, a_demo**2], color=ORANGE, ls="--", lw=2.0)
        ax_g.scatter([1], [1], color=BLUE, s=100, zorder=6)
        ax_g.scatter([a_demo], [a_demo**2], color=ORANGE, s=100, zorder=6)
        ax_g.text(1.08, 0.45, "P(1, 1)", color=BLUE, fontsize=12, fontweight="bold")
        ax_g.text(1.45, 6.2, r"$Q(a, a^2)$", color=ORANGE, fontsize=13, fontweight="bold")
        ax_g.text(1.7, 0.45, r"$a - 1$", color=BLUE, fontsize=13, fontweight="bold", ha="center")
        ax_g.text(2.48, 3.4, r"$a^2 - 1$", color=ORANGE, fontsize=13, fontweight="bold", va="center")

        # Right Step-by-Step Algebra Panel
        ax_a = fig.add_axes([0.42, 0.16, 0.54, 0.70], facecolor=BG)
        ax_a.set_xlim(0, 1)
        ax_a.set_ylim(0, 1)
        ax_a.axis("off")
        card(ax_a, 0.01, 0.02, 0.98, 0.96, fc=PANEL, ec=BORDER, lw=1.8, rad=0.025)

        steps_data = [
            (207.0, 0.85, "1", r"$m = \frac{y_2 - y_1}{x_2 - x_1}$", "Slope formula (rise over run)", WHITE),
            (217.0, 0.68, "2", r"$m = \frac{a^2 - 1}{a - 1}$", r"Substitute $P(1,1)$ and $Q(a,a^2)$", WHITE),
            (232.0, 0.50, "3", r"$m = \frac{(a - 1)(a + 1)}{a - 1}$", r"Factor $a^2 - 1 = (a-1)(a+1)$", ORANGE),
            (250.0, 0.31, "4", r"$m = a + 1 \quad (a \neq 1)$", "Simplified secant slope!", GREEN),
        ]

        for st, yp, num, eq, desc, col in steps_data:
            if t >= st:
                ax_a.add_patch(patches.Circle((0.075, yp), 0.036, facecolor="#172554", edgecolor=BLUE, lw=1.8))
                ax_a.text(0.075, yp, num, color=WHITE, fontsize=14, fontweight="bold", ha="center", va="center")
                ax_a.text(0.14, yp, eq, color=col, fontsize=22, va="center")
                ax_a.text(0.61, yp, desc, color=MUTED if col != GREEN else GREEN, fontsize=12.5, fontweight="bold" if col == GREEN else "normal", va="center")

        # Animated Red Cancellation Slashes on (a - 1) starting at 4:06 (246s)
        if t >= 246.0:
            u_sl = smoothstep(t, 246.0, 249.5)
            # Numerator (a - 1) slash
            ax_a.plot([0.24, 0.24 + 0.10 * u_sl], [0.515, 0.515 + 0.055 * u_sl], color=RED, lw=3.2)
            # Denominator (a - 1) slash
            ax_a.plot([0.28, 0.28 + 0.10 * u_sl], [0.435, 0.435 + 0.052 * u_sl], color=RED, lw=3.2)

        if t >= 256.0:
            card(ax_a, 0.05, 0.07, 0.90, 0.14, fc="#0B2918", ec=GREEN, lw=2.0, rad=0.02)
            ax_a.text(0.50, 0.14, r"Key Idea: The factor $(a - 1)$ cancels (since $a \neq 1$), leaving $m = a + 1$.",
                      color=GREEN, fontsize=14.5, fontweight="bold", ha="center", va="center")

    # --------------------------------------------------------
    # SCENE 4B: TABLE & CONVERGENCE PLOT (4:28 – 4:56)
    # --------------------------------------------------------
    elif t < 296.0:
        draw_header(fig, "Scene 4 | Numerical Convergence", "Watch the Slope Values Approach 2", r"Using $m = a + 1$")

        # Left Animated Table
        ax_t = fig.add_axes([0.04, 0.16, 0.44, 0.70], facecolor=BG)
        ax_t.set_xlim(0, 1)
        ax_t.set_ylim(0, 1)
        ax_t.axis("off")

        card(ax_t, 0.02, 0.05, 0.96, 0.90, fc=PANEL, ec=BORDER, lw=1.8, rad=0.025)
        card(ax_t, 0.02, 0.81, 0.96, 0.14, fc="#172554", ec=BLUE, lw=1.6, rad=0.02)
        ax_t.text(0.27, 0.88, "Position of Q (a)", color=WHITE, fontsize=15, fontweight="bold", ha="center", va="center")
        ax_t.text(0.74, 0.88, "Secant Slope (a + 1)", color=ORANGE, fontsize=15, fontweight="bold", ha="center", va="center")

        rows = [
            (270.5, "3", "4"),
            (274.5, "2", "3"),
            (277.5, "1.5", "2.5"),
            (280.0, "1.1", "2.1"),
            (282.5, "1.01", "2.01"),
        ]
        yp = 0.70
        for st, a_s, m_s in rows:
            if t >= st:
                is_new = (t - st) < 3.0
                row_ec = ORANGE if is_new else BORDER
                card(ax_t, 0.05, yp - 0.05, 0.90, 0.105, fc="#243047" if is_new else "#162032", ec=row_ec, lw=1.4, rad=0.015)
                ax_t.text(0.27, yp, a_s, color=WHITE, fontsize=16, fontweight="bold", ha="center", va="center")
                ax_t.text(0.74, yp, m_s, color=ORANGE if is_new else GREEN, fontsize=16, fontweight="bold", ha="center", va="center")
            yp -= 0.135

        # Right Animated Convergence Plot + Banner
        ax_p = fig.add_axes([0.53, 0.36, 0.42, 0.49])
        style_axes(ax_p, xlim=(0.8, 3.25), ylim=(1.6, 4.35), xlabel="Value of a  (approaching 1)", ylabel="Secant Slope m = a + 1")
        ax_p.invert_xaxis()  # Left-to-right shows a moving 3 -> 1!
        ax_p.axhline(2.0, color=GREEN, lw=2.4, ls="--", label="Limiting Slope = 2")
        ax_p.axvline(1.0, color=BLUE, lw=1.6, ls=":")

        pts_a, pts_m = [], []
        for st, a_s, m_s in rows:
            if t >= st:
                pts_a.append(float(a_s))
                pts_m.append(float(m_s))
        if pts_a:
            ax_p.plot(pts_a, pts_m, color=ORANGE, lw=2.6, marker="o", markersize=9, zorder=5)
            for pa, pm in zip(pts_a, pts_m):
                ax_p.text(pa, pm + 0.14, f"{pm:g}", color=WHITE, fontsize=11, fontweight="bold", ha="center")
        if t >= 287.0:
            ax_p.scatter([1.0], [2.0], color=GREEN, s=150, edgecolor=WHITE, lw=2, zorder=7)
            ax_p.text(1.08, 1.78, "Limit = 2", color=GREEN, fontsize=13, fontweight="bold")
        ax_p.legend(loc="upper right", facecolor=PANEL, edgecolor=BORDER, labelcolor=WHITE, fontsize=11)

        ax_b = fig.add_axes([0.52, 0.15, 0.44, 0.15], facecolor=BG)
        ax_b.set_xlim(0, 1)
        ax_b.set_ylim(0, 1)
        ax_b.axis("off")
        if t >= 285.0:
            card(ax_b, 0.0, 0.08, 1.0, 0.84, fc="#0B2918", ec=GREEN, lw=2.2, rad=0.03)
            ax_b.text(0.5, 0.62, "4  →  3  →  2.5  →  2.1  →  2.01  →  2", color=GREEN, fontsize=16, fontweight="bold", ha="center", va="center")
            ax_b.text(0.5, 0.26, "The exact value 2 is the limiting slope as a → 1.", color=WHITE, fontsize=13.5, ha="center", va="center")

    # --------------------------------------------------------
    # SCENE 5A: SECANT BECOMES TANGENT (4:56 – 5:31)
    # --------------------------------------------------------
    elif t < 331.0:
        draw_header(fig, "Scene 5 | Interpretation", "The Secant Line Becomes the Tangent", r"$f'(1) = 2$")

        ax_l = fig.add_axes([0.04, 0.16, 0.42, 0.70], facecolor=BG)
        ax_l.set_xlim(0, 1)
        ax_l.set_ylim(0, 1)
        ax_l.axis("off")

        card(ax_l, 0.02, 0.06, 0.96, 0.88, fc=PANEL, ec=BORDER, lw=1.8, rad=0.025)
        ax_l.text(0.07, 0.85, "Derivative at x = 1:", color=BLUE, fontsize=15, fontweight="bold")
        ax_l.text(0.07, 0.71, r"$f'(1) = \lim_{a \to 1}\ \frac{f(a) - f(1)}{a - 1}$", color=WHITE, fontsize=22, va="center")

        if t >= 309.0:
            ax_l.text(0.16, 0.53, r"$= \lim_{a \to 1}\ (a + 1) = 1 + 1 = 2$", color=ORANGE, fontsize=21, va="center")

        if t >= 319.0:
            card(ax_l, 0.08, 0.22, 0.84, 0.19, fc="#0B2918", ec=GREEN, lw=2.5, rad=0.025)
            ax_l.text(0.50, 0.315, r"$f'(1) = 2$", color=GREEN, fontsize=30, fontweight="bold", ha="center", va="center")
            ax_l.text(0.50, 0.13, "This is the exact slope of the tangent line at P(1, 1).",
                      color=WHITE, fontsize=13.5, ha="center", va="center")

        # Right Smooth Transformation: Secant -> Tangent
        ax_g = fig.add_axes([0.50, 0.18, 0.46, 0.67])
        style_axes(ax_g, xlim=(0, 3.2), ylim=(-0.8, 9.8))
        xs = np.linspace(0, 3.1, 250)
        ax_g.plot(xs, xs**2, color=WHITE, lw=3.2)

        u = smoothstep(t, 297.0, 316.0)
        a_val = lerp(2.2, 1.0001, u)
        sl = a_val + 1.0
        is_tan = u > 0.96
        lcol = GREEN if is_tan else ORANGE

        lx = np.linspace(0.0, 3.1, 120)
        ax_g.plot(lx, 1.0 + sl * (lx - 1.0), color=lcol, lw=3.4, zorder=4)
        ax_g.scatter([1], [1], color=BLUE, s=125, edgecolor=WHITE, lw=1.8, zorder=6)
        if not is_tan:
            ax_g.scatter([a_val], [a_val**2], color=ORANGE, s=110, zorder=6)
            ax_g.text(0.18, 8.4, f"Q → P  (a = {a_val:.2f},  slope = {sl:.2f})", color=ORANGE, fontsize=13.5, fontweight="bold",
                      bbox=dict(boxstyle="round,pad=0.35", facecolor=PANEL, edgecolor=ORANGE, lw=1.6))
        else:
            ax_g.text(0.18, 8.4, "TANGENT LINE LOCKED!\nSlope = f'(1) = 2.00", color=GREEN, fontsize=14, fontweight="bold",
                      bbox=dict(boxstyle="round,pad=0.35", facecolor="#0B2918", edgecolor=GREEN, lw=2.0))
        ax_g.text(1.12, 0.55, "P(1, 1)", color=BLUE, fontsize=13, fontweight="bold")

    # --------------------------------------------------------
    # SCENE 5B: TANGENT EQUATION & LOCAL LINEARITY (5:31 – 6:31)
    # --------------------------------------------------------
    elif t < 391.0:
        draw_header(fig, "Scene 5 | Interpretation", "What Does a Slope of 2 Tell Us?", "Tangent Equation & Local Rate")

        ax_l = fig.add_axes([0.04, 0.16, 0.43, 0.70], facecolor=BG)
        ax_l.set_xlim(0, 1)
        ax_l.set_ylim(0, 1)
        ax_l.axis("off")

        card(ax_l, 0.02, 0.04, 0.96, 0.92, fc=PANEL, ec=BORDER, lw=1.8, rad=0.025)
        ax_l.text(0.07, 0.87, "At x = 1, tangent slope m = 2", color=GREEN, fontsize=17, fontweight="bold")
        ax_l.text(0.07, 0.78, "Passing through point P = (1, 1)", color=BLUE, fontsize=14.5)

        if t >= 343.0:
            ax_l.text(0.07, 0.67, "Point-Slope Form:", color=MUTED, fontsize=12.5, fontweight="bold")
            ax_l.text(0.07, 0.59, r"$y - y_0 = m(x - x_0)$", color=WHITE, fontsize=22, va="center")

        if t >= 363.0:
            ax_l.text(0.07, 0.45, r"$y - 1 = 2(x - 1)$", color=ORANGE, fontsize=22, va="center")

        if t >= 374.0:
            card(ax_l, 0.07, 0.25, 0.86, 0.13, fc="#0B2918", ec=GREEN, lw=2.2, rad=0.02)
            ax_l.text(0.50, 0.315, r"Tangent Line:   $y = 2x - 1$", color=GREEN, fontsize=22, fontweight="bold", ha="center", va="center")

        if t >= 381.0:
            card(ax_l, 0.07, 0.07, 0.86, 0.14, fc="#172554", ec=BLUE, lw=1.8, rad=0.02)
            ax_l.text(0.50, 0.14, "Near x = 1:\nΔx = +0.1  ⇒  Δf(x) ≈ +0.2",
                      color=WHITE, fontsize=14.5, fontweight="bold", ha="center", va="center", linespacing=1.35)

        # Right Graph: Full View -> Smooth Zoom into Local Linearity at 6:21 (381s)
        ax_g = fig.add_axes([0.50, 0.18, 0.46, 0.67])
        u_zoom = smoothstep(t, 381.0, 386.0)
        x_lo = lerp(-0.2, 0.86, u_zoom)
        x_hi = lerp(3.2, 1.24, u_zoom)
        y_lo = lerp(-1.5, 0.72, u_zoom)
        y_hi = lerp(9.8, 1.48, u_zoom)
        style_axes(ax_g, xlim=(x_lo, x_hi), ylim=(y_lo, y_hi))

        xs = np.linspace(max(-0.2, x_lo), x_hi, 300)
        ax_g.plot(xs, xs**2, color=WHITE, lw=3.4, label=r"$f(x) = x^2$")
        ax_g.plot(xs, 2*xs - 1, color=GREEN, lw=3.0, ls="--" if u_zoom > 0.5 else "-", label=r"Tangent: $y = 2x - 1$")
        ax_g.scatter([1], [1], color=BLUE, s=130, edgecolor=WHITE, lw=1.8, zorder=6)

        if u_zoom < 0.3:
            ax_g.scatter([0], [-1], color=GREEN, s=80, zorder=6)
            ax_g.text(0.12, -1.1, "(0, -1)", color=GREEN, fontsize=11.5, fontweight="bold")
            ax_g.text(1.15, 0.6, "P(1, 1)", color=BLUE, fontsize=13, fontweight="bold")
        else:
            # Show Δx = +0.1 and Δy = +0.2 step arrows!
            ax_g.annotate("", xy=(1.1, 1.0), xytext=(1.0, 1.0), arrowprops=dict(arrowstyle="->", color=ORANGE, lw=3.0))
            ax_g.annotate("", xy=(1.1, 1.2), xytext=(1.1, 1.0), arrowprops=dict(arrowstyle="->", color=ORANGE, lw=3.0))
            ax_g.scatter([1.1], [1.21], color=ORANGE, s=95, zorder=6)
            ax_g.text(1.05, 0.94, "+0.1", color=ORANGE, fontsize=13, fontweight="bold", ha="center")
            ax_g.text(1.12, 1.10, "+0.2", color=ORANGE, fontsize=13, fontweight="bold", va="center")
            ax_g.text(0.89, 1.38, "Local Linearity:\nCurve ≈ Tangent Line!", color=GREEN, fontsize=13, fontweight="bold",
                      bbox=dict(boxstyle="round,pad=0.3", facecolor=PANEL, edgecolor=GREEN, lw=1.8))

        ax_g.legend(loc="upper left" if u_zoom < 0.3 else "lower right",
                    facecolor=PANEL, edgecolor=BORDER, labelcolor=WHITE, fontsize=12)

    # --------------------------------------------------------
    # SCENE 6: SUMMARY & CREDITS (6:31 – 6:52.32)
    # --------------------------------------------------------
    else:
        draw_header(fig, "Scene 6 | Summary & Credits", "Three Things to Remember", f"{STUDENT_NAME} ({STUDENT_ID})")

        ax = fig.add_axes([0.04, 0.15, 0.92, 0.72], facecolor=BG)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")

        takeaways = [
            (392.5, 0.79, "1", "A secant line joins two points on a curve.", BLUE),
            (397.0, 0.59, "2", "As the second point approaches the first, the secant slope approaches the tangent slope.", ORANGE),
            (403.5, 0.39, "3", r"For $f(x) = x^2$, the derivative at $x = 1$ is $f'(1) = 2$ (tangent line: $y = 2x - 1$).", GREEN),
        ]
        for st, yp, num, txt, col in takeaways:
            if t >= st:
                card(ax, 0.02, yp - 0.075, 0.96, 0.15, fc=PANEL, ec=col, lw=2.0, rad=0.02)
                ax.add_patch(patches.Circle((0.065, yp), 0.032, facecolor="#0B1220", edgecolor=col, lw=2.0))
                ax.text(0.065, yp, num, color=col, fontsize=16, fontweight="bold", ha="center", va="center")
                ax.text(0.12, yp, txt, color=WHITE, fontsize=16.5, fontweight="bold", va="center")

        # Credits & AI Disclosure Footer
        card(ax, 0.02, 0.04, 0.74, 0.22, fc="#0B1220", ec=BORDER, lw=1.4, rad=0.02)
        credits = (
            f"Creator: {STUDENT_NAME}  |  Student ID: {STUDENT_ID}  |  M3 Linear Algebra & Calculus\n"
            "Credits: Custom Python (Matplotlib) animation created for this project. No external music used.\n"
            "AI Disclosure: AI assisted with storyboard structuring and Python animation code; all mathematics,\n"
            "verification, and voiceover narration were created and recorded by Manoj Lahu Ahire."
        )
        ax.text(0.04, 0.15, credits, color=MUTED, fontsize=11.5, va="center", linespacing=1.45)

        if t >= 408.0:
            card(ax, 0.79, 0.04, 0.19, 0.22, fc="#0B2918", ec=GREEN, lw=2.2, rad=0.025)
            ax.text(0.885, 0.15, "Thank You!", color=GREEN, fontsize=22, fontweight="bold", ha="center", va="center")

    draw_caption_bar(fig, t)

# ============================================================
# 5. RENDER 1080p MP4
# ============================================================
print(f"Rendering {TOTAL_FRAMES} frames ({DURATION:.2f}s @ {FPS} fps)...")
anim = FuncAnimation(fig, render_frame, frames=TOTAL_FRAMES, interval=1000 / FPS)
writer = FFMpegWriter(fps=FPS, bitrate=4000, metadata={"title": "Derivative as Rate of Change - Manoj Lahu Ahire"})
anim.save(
    OUTPUT_VIDEO,
    writer=writer,
    dpi=120,
    progress_callback=lambda i, n: print(f"Progress: {i}/{n} ({100*i/n:.1f}%)") if i % (FPS * 15) == 0 else None
)
print(f"Animation saved to {OUTPUT_VIDEO}!")