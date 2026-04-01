import sys
sys.path.append(".")

from pycore.tikzeng import *
from pycore.blocks import *

def to_Pool(name, offset, to, width, height, depth, opacity=0.5, caption=" "):
    return r"""
\pic[shift={(%s)}] at (%s)
    {Box={
        name=%s,
        caption=%s,
        xlabel={{" ","dummy"}},
        zlabel=%s,
        fill=\PoolColor,
        opacity=%s,
        height=%s,
        width=%s,
        depth=%s
        }
    };
""" % (offset, to, name, caption, depth, opacity, height, width, depth)

arch = [
    to_head(".."),
    to_cor(),
    to_begin(),

    # ── INPUT NODES ──────────────────────────────────────────────────────────

    # Node v (left)
    r"""
\node[draw, circle, minimum size=1cm, fill=blue!20, thick]
    (nodeV) at (-10, 0) {\Large $v$};
""",
    # Node u (right)
    r"""
\node[draw, circle, minimum size=1cm, fill=orange!30, thick]
    (nodeU) at (10, 0) {\Large $u$};
""",

    # ── TIME-AWARE MODULE (top branch) ───────────────────────────────────────

    # Label
    r"""
\node[draw, rounded corners, minimum width=13cm, minimum height=0.6cm,
      fill=cyan!10, thick, dashed]
    (ta_box) at (0, 5.5) {};
\node[above] at (ta_box.north) {\textbf{Time-aware Module}};
""",

    # Recent neighbors of v
    to_Conv(name="rv1", s_filer=1, n_filer=1, offset="(0,0,0)", to="(nodeV)", width=1, height=3, depth=3,
            caption=r"$N_v(t,k_r)$"),
    r"""
\node[above=0.15cm of rv1-east, font=\small] {Recent};
\node[below=0.10cm of rv1-east, font=\small] {Neighbors};
""",

    # Recent neighbors of u
    to_Conv(name="ru1", s_filer=1, n_filer=1, offset="(0,0,0)", to="(nodeU)", width=1, height=3, depth=3,
            caption=r"$N_u(t,k_r)$"),
    r"""
\node[above=0.15cm of ru1-west, font=\small] {Recent};
\node[below=0.10cm of ru1-west, font=\small] {Neighbors};
""",

    # h_v^ta aggregation
    to_Conv(name="hv_ta", s_filer=172, n_filer=2, offset="(2,0,0)", to="(rv1-east)", width=1.5, height=2.5, depth=2.5,
            caption=r"$\mathbf{h}_v^{\mathrm{ta}}$"),
    # h_u^ta aggregation
    to_Conv(name="hu_ta", s_filer=172, n_filer=2, offset="(-2,0,0)", to="(ru1-west)", width=1.5, height=2.5, depth=2.5,
            caption=r"$\mathbf{h}_u^{\mathrm{ta}}$"),

    # Concat + MLP (time-aware score)
    to_Conv(name="ta_mlp", s_filer=1, n_filer=4, offset="(0,0,0)", to="(0,4,0)", width=2, height=2, depth=2,
            caption=r"MLP (2-layer)"),

    # s^ta score
    r"""
\node[draw, circle, minimum size=0.8cm, fill=cyan!40, thick]
    (s_ta) at (0, 4) {$s_{v,u}^{\mathrm{ta}}$};
""",

    # ── STRUCTURE-AWARE MODULE (bottom branch) ───────────────────────────────

    r"""
\node[draw, rounded corners, minimum width=13cm, minimum height=0.6cm,
      fill=green!10, thick, dashed]
    (sa_box) at (0, -5.5) {};
\node[below] at (sa_box.south) {\textbf{Structure-aware Module}};
""",

    # Influential nodes of v (T-PPR)
    to_Conv(name="pv1", s_filer=1, n_filer=1, offset="(0,0,0)", to="(nodeV)", width=1, height=3, depth=3,
            caption=r"$N_v(\pi_v,k_s)$"),
    r"""
\node[above=0.15cm of pv1-east, font=\small] {Influential};
\node[below=0.10cm of pv1-east, font=\small] {Nodes};
""",

    # Influential nodes of u (T-PPR)
    to_Conv(name="pu1", s_filer=1, n_filer=1, offset="(0,0,0)", to="(nodeU)", width=1, height=3, depth=3,
            caption=r"$N_u(\pi_u,k_s)$"),
    r"""
\node[above=0.15cm of pu1-west, font=\small] {Influential};
\node[below=0.10cm of pu1-west, font=\small] {Nodes};
""",

    # T-PPR vectors
    to_Conv(name="piv", s_filer=1, n_filer=2, offset="(2,0,0)", to="(pv1-east)", width=1.5, height=2.5, depth=2.5,
            caption=r"$\boldsymbol{\pi}_v(t)$"),
    to_Conv(name="piu", s_filer=1, n_filer=2, offset="(-2,0,0)", to="(pu1-west)", width=1.5, height=2.5, depth=2.5,
            caption=r"$\boldsymbol{\pi}_u(t)$"),

    # s^sa score (dot-product intersection)
    r"""
\node[draw, circle, minimum size=0.8cm, fill=green!40, thick]
    (s_sa) at (0, -4) {$s_{v,u}^{\mathrm{sa}}$};
""",

    # ── HYBRID MODULE (center) ───────────────────────────────────────────────

    r"""
\node[draw, rounded corners, minimum width=5cm, minimum height=2cm,
      fill=yellow!20, thick]
    (hybrid) at (0, 0)
    {\begin{tabular}{c}
        \textbf{Hybrid Module}\\[4pt]
        $s_{v,u}^{\mathrm{hy}} = \lambda\!\cdot\!
        (\mathrm{e}^{-\bar{t}_v}\!+\!\mathrm{e}^{-\bar{t}_u})\!\cdot\!
        s_{v,u}^{\mathrm{ta}} + s_{v,u}^{\mathrm{sa}}$
     \end{tabular}};
""",

    # ── OUTPUT ──────────────────────────────────────────────────────────────
    r"""
\node[draw, rounded corners, minimum width=3cm, minimum height=1cm,
      fill=red!20, thick]
    (output) at (6, 0) {Link Score $\hat{y}_{v,u}(t)$};
""",

    # ── ARROWS ──────────────────────────────────────────────────────────────

    # Node v → recent neighbors (top)
    r"""
\draw[->, thick, cyan!70!black] (nodeV) -- node[above, font=\small]{select $k_r$} (rv1-west);
""",
    # Node u → recent neighbors (top)
    r"""
\draw[->, thick, cyan!70!black] (nodeU) -- node[above, font=\small]{select $k_r$} (ru1-east);
""",
    # Recent neighbors → h_v^ta
    r"""
\draw[->, thick] (rv1-east) -- node[above, font=\tiny]{avg concat} (hv_ta-west);
""",
    r"""
\draw[->, thick] (ru1-west) -- node[above, font=\tiny]{avg concat} (hu_ta-east);
""",
    # h^ta → MLP/s_ta
    r"""
\draw[->, thick] (hv_ta-east) -- (s_ta);
\draw[->, thick] (hu_ta-west) -- (s_ta);
""",
    # Node v → influential nodes (bottom)
    r"""
\draw[->, thick, green!60!black] (nodeV) -- node[below, font=\small]{T-PPR $k_s$} (pv1-west);
\draw[->, thick, green!60!black] (nodeU) -- node[below, font=\small]{T-PPR $k_s$} (pu1-east);
""",
    # T-PPR → pi vectors
    r"""
\draw[->, thick] (pv1-east) -- (piv-west);
\draw[->, thick] (pu1-west) -- (piu-east);
""",
    # pi vectors → s_sa
    r"""
\draw[->, thick] (piv-east) -- node[right, font=\tiny]{$\cap$ dot-product} (s_sa);
\draw[->, thick] (piu-west) -- (s_sa);
""",
    # s_ta, s_sa → hybrid
    r"""
\draw[->, thick, cyan!70!black] (s_ta) -- node[right, font=\small]{$s_{v,u}^{\mathrm{ta}}$} (hybrid);
\draw[->, thick, green!60!black] (s_sa) -- node[right, font=\small]{$s_{v,u}^{\mathrm{sa}}$} (hybrid);
""",
    # Adaptive weights from nodes
    r"""
\draw[->, dashed, orange!70!black, thick] (nodeV) to[out=15, in=200]
    node[below left, font=\tiny]{$\bar{t}_v$} (hybrid);
\draw[->, dashed, orange!70!black, thick] (nodeU) to[out=165, in=-20]
    node[below right, font=\tiny]{$\bar{t}_u$} (hybrid);
""",
    # hybrid → output
    r"""
\draw[->, very thick, red!70!black] (hybrid) -- (output);
""",

    to_end(),
]

def main():
    namefile = str(sys.argv[0]).split(".")[0]
    to_generate(arch, namefile + ".tex")

if __name__ == "__main__":
    main()
