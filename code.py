from flask import Flask, request, render_template_string
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import json

app = Flask(__name__)
GATES = {
    "I": np.eye(2, dtype=complex),
    "X": np.array([[0, 1], [1, 0]], complex),
    "Y": np.array([[0, -1j], [1j, 0]], complex),
    "Z": np.array([[1, 0], [0, -1]], complex),
    "H": np.array([[1, 1], [1, -1]], complex) / np.sqrt(2),
    "S": np.array([[1, 0], [0, 1j]], complex),
    "T": np.array(
        [
            [1, 0],
            [0, np.exp(1j * np.pi / 4)],
        ],
        complex,
    ),
}
INITIAL = {
    "0": np.array([1, 0], complex),
    "1": np.array([0, 1], complex),
    "+": np.array([1, 1], complex) / np.sqrt(2),
    "-": np.array([1, -1], complex) / np.sqrt(2),
    "+i": np.array([1, 1j], complex) / np.sqrt(2),
}


def gate_matrix(name, angle):
    if name in GATES:
        return GATES[name]
    theta = np.deg2rad(angle)
    p = {
        "Rx": np.array([[0, 1], [1, 0]], complex),
        "Ry": np.array([[0, -1j], [1j, 0]], complex),
        "Rz": np.array([[1, 0], [0, -1]], complex),
    }[name]
    return np.cos(theta / 2) * np.eye(2) - 1j * np.sin(theta / 2) * p


def cfmt(v):
    r, i = float(v.real), float(v.imag)
    if abs(r) < 1e-8:
        r = 0
    if abs(i) < 1e-8:
        i = 0
    if i == 0:
        return f"{r:.3f}"
    return f"{r:.3f} {'+' if i>=0 else '−'} {abs(i):.3f}i"


def bloch(s):
    a, b = s
    return [
        float(2 * np.real(np.conj(a) * b)),
        float(2 * np.imag(np.conj(a) * b)),
        float(abs(a) ** 2 - abs(b) ** 2),
    ]


def chart(p0, p1):
    f = go.Figure(
        go.Bar(
            x=["|0⟩", "|1⟩"],
            y=[p0, p1],
            marker_color=["#818cf8", "#2dd4bf"],
            text=[f"{p0*100:.1f}%", f"{p1*100:.1f}%"],
            textposition="outside",
        )
    )
    f.update_layout(
        title="Measurement probabilities",
        height=330,
        yaxis=dict(title="Probability", range=[0, 1.15], tickformat=".0%"),
        margin=dict(l=20, r=15, t=55, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"),
    )
    return pio.to_html(
        f,
        full_html=False,
        include_plotlyjs="cdn",
        config={"displayModeBar": False, "responsive": True},
    )


def sphere(s):
    u = np.linspace(0, 2 * np.pi, 55)
    v = np.linspace(0, np.pi, 35)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones_like(u), np.cos(v))
    f = go.Figure(
        go.Surface(
            x=x,
            y=y,
            z=z,
            opacity=0.18,
            colorscale=[[0, "#6366f1"], [1, "#2dd4bf"]],
            showscale=False,
            hoverinfo="skip",
        )
    )
    for xx, yy, zz in [
        ([0, 0], [0, 0], [-1.1, 1.1]),
        ([-1.1, 1.1], [0, 0], [0, 0]),
        ([0, 0], [-1.1, 1.1], [0, 0]),
    ]:
        f.add_trace(
            go.Scatter3d(
                x=xx,
                y=yy,
                z=zz,
                mode="lines",
                line=dict(color="#94a3b8", width=3),
                showlegend=False,
                hoverinfo="skip",
            )
        )
    x1, y1, z1 = bloch(s)
    f.add_trace(
        go.Scatter3d(
            x=[0, x1],
            y=[0, y1],
            z=[0, z1],
            mode="lines+markers",
            line=dict(color="#fb7185", width=7),
            marker=dict(size=[3, 7], color="#fb7185"),
            showlegend=False,
        )
    )
    f.update_layout(
        title="3D Bloch sphere",
        height=330,
        margin=dict(l=0, r=0, t=55, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"),
        scene=dict(
            xaxis=dict(visible=False, range=[-1.2, 1.2]),
            yaxis=dict(visible=False, range=[-1.2, 1.2]),
            zaxis=dict(visible=False, range=[-1.2, 1.2]),
            aspectmode="cube",
        ),
    )
    return pio.to_html(
        f,
        full_html=False,
        include_plotlyjs=False,
        config={"displayModeBar": False, "responsive": True},
    )


HTML = r"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Quantum Gate Studio</title><style>
*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at top left,#172554,#0b1020 52%,#070b14);color:#e5e7eb;font-family:Segoe UI,Arial}
main{max-width:1250px;margin:auto;padding:26px 18px}header,.panel,.stat{background:#111b30;border:1px solid #29364b;border-radius:17px;padding:18px}
header{background:linear-gradient(120deg,#172554,#111827);margin-bottom:18px;padding:25px}.kicker{color:#a5b4fc;letter-spacing:3px;text-transform:uppercase;font-size:12px;font-weight:bold}
h1{font-size:clamp(28px,4vw,42px);margin:10px 0}p{color:#cbd5e1;line-height:1.6}.layout{display:grid;grid-template-columns:270px 1fr;gap:18px}
label{display:block;color:#cbd5e1;margin:14px 0 6px;font-size:13px}select,input,button{width:100%;padding:11px;border-radius:9px;border:1px solid #475569;background:#0b1222;color:#f8fafc;font:inherit}
button{cursor:pointer;font-weight:bold;margin-top:12px;background:#6366f1;border:0}.secondary{background:#253047}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:16px}
.stat span{display:block;color:#94a3b8;font-size:11px;text-transform:uppercase;letter-spacing:1px}.stat strong{display:block;font-size:22px;margin-top:8px}
.charts{display:grid;grid-template-columns:1fr 1fr;gap:16px}.sequence{background:#0b1222;border-radius:9px;padding:12px;overflow-wrap:anywhere}.state{font:17px Consolas,monospace;overflow-wrap:anywhere}
table{width:100%;border-collapse:collapse;font-size:13px}td,th{text-align:left;border-bottom:1px solid #334155;padding:9px 5px}th{color:#a5b4fc}
@media(max-width:850px){.layout,.charts{grid-template-columns:1fr}.stats{grid-template-columns:repeat(2,1fr)}}
</style></head><body><main>
<header><div class="kicker">Python quantum simulator</div><h1>⚛ Quantum Gate Studio</h1>
<p>Build a single-qubit circuit, apply gates in sequence, and explore measurement probabilities and the qubit's position on the Bloch sphere.</p></header>
<div class="layout"><aside class="panel"><h2>Circuit controls</h2><form method="post">
<label>Initial state</label><select name="initial">{% for k,l in initials %}<option value="{{k}}" {% if initial==k %}selected{% endif %}>{{l}}</option>{% endfor %}</select>
<label>Quantum gate</label><select name="gate">{% for g in gates %}<option {% if gate==g %}selected{% endif %}>{{g}}</option>{% endfor %}</select>
<label>Rotation angle (Rx/Ry/Rz)</label><input name="angle" type="number" min="0" max="360" step="15" value="{{angle}}">
<input type="hidden" name="seq" value="{{seq_json}}">
<button name="action" value="add">＋ Add gate</button><button class="secondary" name="action" value="example">Load H → S → X example</button><button class="secondary" name="action" value="reset">Reset circuit</button></form>
<h2 style="margin-top:22px">Gate sequence</h2><div class="sequence">{% if sequence %}{% for g in sequence %}<b>{{loop.index}}.</b> {{g}}{% if not loop.last %} → {% endif %}{% endfor %}{% else %}No gates added{% endif %}</div>
<p style="font-size:13px;color:#94a3b8">The first gate listed acts first.</p></aside>
<section><div class="stats"><div class="stat"><span>Gates applied</span><strong>{{sequence|length}}</strong></div>
<div class="stat"><span>Probability 0</span><strong>{{"%.1f"|format(p0*100)}}%</strong></div><div class="stat"><span>Probability 1</span><strong>{{"%.1f"|format(p1*100)}}%</strong></div>
<div class="stat"><span>Simulation</span><strong>Pure state</strong></div></div>
<div class="charts"><div class="panel">{{prob_chart|safe}}</div><div class="panel">{{sphere_chart|safe}}</div></div>
<div class="panel" style="margin-top:16px"><h2>Final quantum state</h2><div class="state">{{state_text}}</div>
<p>Bloch coordinates: ({{"%.3f"|format(xyz[0])}}, {{"%.3f"|format(xyz[1])}}, {{"%.3f"|format(xyz[2])}})</p></div>
<details class="panel" style="margin-top:16px"><summary><b>Inspect state after every gate</b></summary><div style="overflow:auto"><table><tr><th>Step</th><th>Operation</th><th>State</th><th>P(0)</th><th>P(1)</th></tr>
{% for r in history %}<tr><td>{{loop.index0}}</td><td>{{r.op}}</td><td>{{r.state}}</td><td>{{"%.3f"|format(r.p0)}}</td><td>{{"%.3f"|format(r.p1)}}</td></tr>{% endfor %}</table></div></details>
<div class="panel" style="margin-top:16px"><h2>Gate guide</h2><p><b>I</b> identity · <b>X</b> bit flip · <b>Y/Z</b> Pauli gates · <b>H</b> Hadamard · <b>S/T</b> phase gates · <b>Rx/Ry/Rz</b> rotations.</p><p>Measurement probabilities are the squared magnitudes of the amplitudes. This is an ideal single-qubit educational simulator, not quantum hardware.</p></div>
</section></div></main></body></html>"""


@app.route("/", methods=["GET", "POST"])
def home():
    initial = "0"
    gate = "H"
    angle = 90
    sequence = []
    if request.method == "POST":
        initial = request.form.get("initial", "0")
        gate = request.form.get("gate", "H")
        try:
            angle = max(0, min(360, int(request.form.get("angle", "90"))))
        except ValueError:
            angle = 90
        try:
            sequence = json.loads(request.form.get("seq", "[]"))
            if not isinstance(sequence, list):
                sequence = []
            sequence = [str(x) for x in sequence if isinstance(x, str)]
        except (ValueError, TypeError):
            sequence = []
        action = request.form.get("action", "add")
        if action == "reset":
            sequence = []
        elif action == "example":
            sequence = ["H", "S", "X"]
        elif action == "add":
            if gate in GATES:
                sequence.append(gate)
            elif gate in ("Rx", "Ry", "Rz"):
                sequence.append(f"{gate}:{angle}")
    if initial not in INITIAL:
        initial = "0"
    state = INITIAL[initial].copy()
    history = [
        {
            "op": "Initial state",
            "state": f"({cfmt(state[0])})|0⟩ + ({cfmt(state[1])})|1⟩",
            "p0": float(abs(state[0]) ** 2),
            "p1": float(abs(state[1]) ** 2),
        }
    ]
    for item in sequence:
        try:
            if ":" in item and item.split(":")[0] in ("Rx", "Ry", "Rz"):
                name, deg = item.split(":", 1)
                matrix = gate_matrix(name, float(deg))
                label = f"{name}({deg}°)"
            elif item in GATES:
                matrix = GATES[item]
                label = item
            else:
                continue
            state = matrix @ state
            state = state / np.linalg.norm(state)
            history.append(
                {
                    "op": label,
                    "state": f"({cfmt(state[0])})|0⟩ + ({cfmt(state[1])})|1⟩",
                    "p0": float(abs(state[0]) ** 2),
                    "p1": float(abs(state[1]) ** 2),
                }
            )
        except (ValueError, KeyError):
            continue
    p0, p1 = float(abs(state[0]) ** 2), float(abs(state[1]) ** 2)
    return render_template_string(
        HTML,
        initial=initial,
        gate=gate,
        angle=angle,
        sequence=sequence,
        seq_json=json.dumps(sequence),
        initials=[
            ("0", "|0⟩ — Ground state"),
            ("1", "|1⟩ — Excited state"),
            ("+", "|+⟩ — Superposition"),
            ("-", "|−⟩ — Opposite superposition"),
            ("+i", "|+i⟩ — Y-axis superposition"),
        ],
        gates=["I", "X", "Y", "Z", "H", "S", "T", "Rx", "Ry", "Rz"],
        p0=p0,
        p1=p1,
        xyz=bloch(state),
        state_text=f"({cfmt(state[0])})|0⟩ + ({cfmt(state[1])})|1⟩",
        prob_chart=chart(p0, p1),
        sphere_chart=sphere(state),
        history=history,
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
