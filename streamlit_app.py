import heapq

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Dijkstra | En kısa yol",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="expanded",
)

GRAPH = {
    "START": {"A": 2.0, "E": 6.0, "D": 8.0},
    "A": {"B": 3.0, "C": 27 / 4, "E": 5.0},
    "B": {"C": 5.0, "E": 8 / 3},
    "C": {"TARGET": 6.0, "G": 11 / 4},
    "E": {"TARGET": 3.0, "D": 1.0},
    "D": {"TARGET": 4.25, "G": 5.0},
    "TARGET": {"G": 9.0},
    "G": {},
}

POSITIONS = {
    "START": (0.0, 1.4), "A": (1.7, 2.5), "B": (3.7, 2.5),
    "C": (5.7, 2.5), "E": (3.2, 0.8), "D": (5.2, 0.8),
    "TARGET": (7.8, 1.8), "G": (9.8, 1.8),
}


def dijkstra(graph, start):
    distances = {node: float("inf") for node in graph}
    parents = {node: None for node in graph}
    distances[start] = 0.0
    queue = [(0.0, start)]
    steps = []

    while queue:
        distance, node = heapq.heappop(queue)
        if distance > distances[node]:
            continue
        changes, pushed = [], []
        for neighbor, weight in graph[node].items():
            candidate = distance + weight
            if candidate < distances[neighbor]:
                distances[neighbor] = candidate
                parents[neighbor] = node
                heapq.heappush(queue, (candidate, neighbor))
                changes.append(f"{neighbor} · {candidate:.2f}")
                pushed.append(f"({candidate:.2f}, {neighbor})")
        steps.append({
            "Adım": len(steps) + 1,
            "İşlenen düğüm": f"{node} · {distance:.2f}",
            "Mesafe güncellemeleri": ", ".join(changes) or "Güncelleme yok",
            "Kuyruğa eklenenler": ", ".join(pushed) or "—",
        })
    return distances, parents, steps


def get_path(parents, distances, target):
    if distances[target] == float("inf"):
        return []
    path, node = [], target
    while node is not None:
        path.append(node)
        node = parents[node]
    return path[::-1]


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
:root { --ink:#e8edf7; --muted:#91a0b8; --panel:#111a2b; --line:#22304a; }
.stApp { background: radial-gradient(ellipse at 15% 0%, #172743 0%, #0b1220 48%, #090f1a 100%); color:var(--ink); }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
h1,h2,h3 { font-family:'Space Grotesk',sans-serif !important; letter-spacing:-.035em; }
h1 { font-size:2.6rem !important; margin-bottom:.15rem !important; }
section[data-testid="stSidebar"] { background:#0c1422; border-right:1px solid #1c2940; }
.eyebrow { color:#7dd3fc; text-transform:uppercase; letter-spacing:.16em; font-size:.72rem; font-weight:700; }
.subtitle { color:#aab6c9; font-size:1.02rem; margin:.2rem 0 1.3rem; }
.panel { background:linear-gradient(145deg,rgba(20,31,50,.95),rgba(13,22,37,.95)); border:1px solid #24334d; border-radius:18px; padding:1.15rem 1.3rem; }
.route { font-family:'Space Grotesk',sans-serif; color:#dce8fa; font-size:1.08rem; font-weight:600; }
div[data-testid="stMetric"] { background:rgba(17,26,43,.88); border:1px solid #263550; padding:16px 18px; border-radius:15px; }
div[data-testid="stMetricLabel"] { color:#91a0b8; }
div[data-testid="stMetricValue"] { color:#f3f7ff; font-family:'Space Grotesk',sans-serif; }
div[data-testid="stDataFrame"], div[data-testid="stTable"] { border:1px solid #263550; border-radius:12px; overflow:hidden; }
.block-container { padding-top:2.5rem; padding-bottom:3rem; max-width:1450px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="eyebrow">GRAPH ALGORITHM · INTERACTIVE TRACE</div>', unsafe_allow_html=True)
st.title("Dijkstra görselleştiricisi")
st.markdown('<div class="subtitle">Bir başlangıç düğümünden en kısa yolları keşfedin.</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Kontroller")
    st.caption("Yönlü grafikte başlangıç ve hedefi seçin.")
    start_node = st.selectbox("Başlangıç", list(GRAPH), index=0)
    target_node = st.selectbox("Hedef", list(GRAPH), index=list(GRAPH).index("TARGET"))
    st.divider()
    st.markdown("**Renk anahtarı**")
    st.markdown("🟢 Başlangıç&nbsp;&nbsp; 🔴 Hedef<br>🟠 En kısa rota&nbsp;&nbsp; 🔵 Diğer düğümler", unsafe_allow_html=True)
    st.caption("Kenar ağırlıkları yönlüdür; oklar geçiş yönünü gösterir.")

distances, parents, steps = dijkstra(GRAPH, start_node)
path = get_path(parents, distances, target_node)
path_edges = set(zip(path, path[1:]))

distance_value = distances[target_node]
distance_label = "∞" if distance_value == float("inf") else f"{distance_value:.2f}"
route_label = " → ".join(path) if path else "Hedefe ulaşılamıyor"
reachable = sum(value != float("inf") for value in distances.values())

m1, m2, m3 = st.columns(3)
m1.metric("En kısa mesafe", distance_label)
m2.metric("Rotadaki düğüm", f"{len(path)}" if path else "—")
m3.metric("Ulaşılabilen düğüm", f"{reachable} / {len(GRAPH)}")

st.markdown("#### En kısa rota")
st.markdown(f'<div class="panel"><div class="route">{route_label}</div></div>', unsafe_allow_html=True)
st.markdown("")

left, right = st.columns([1.65, 1], gap="large")
with left:
    st.markdown("#### Ağ haritası")
    fig, ax = plt.subplots(figsize=(11, 5.8), facecolor="#111a2b")
    ax.set_facecolor("#111a2b")
    network = nx.DiGraph()
    for source, neighbors in GRAPH.items():
        for dest, weight in neighbors.items():
            network.add_edge(source, dest, weight=weight)
    colors = ["#35d39a" if n == start_node else "#fb7185" if n == target_node else "#f6b94a" if n in path else "#42618e" for n in network.nodes]
    edge_colors = ["#f6b94a" if edge in path_edges else "#3b4b65" for edge in network.edges]
    widths = [3.1 if edge in path_edges else 1.35 for edge in network.edges]
    nx.draw_networkx_nodes(network, POSITIONS, node_color=colors, node_size=1320, linewidths=2, edgecolors="#dce8fa", ax=ax)
    nx.draw_networkx_edges(network, POSITIONS, edge_color=edge_colors, width=widths, arrows=True, arrowstyle="-|>", arrowsize=19, connectionstyle="arc3,rad=0.045", min_source_margin=22, min_target_margin=24, ax=ax)
    nx.draw_networkx_labels(network, POSITIONS, font_size=10, font_weight="bold", font_color="#08111e", ax=ax)
    labels = {(u, v): f"{w:g}" for u, v, w in network.edges(data="weight")}
    nx.draw_networkx_edge_labels(network, POSITIONS, edge_labels=labels, font_size=9, font_color="#d8e2f0", rotate=False, label_pos=.52, bbox={"alpha": .9, "color": "#111a2b", "pad": 2, "edgecolor": "none"}, ax=ax)
    ax.margins(.12)
    ax.axis("off")
    fig.tight_layout(pad=1)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

with right:
    st.markdown("#### Mesafe tablosu")
    summary = []
    for node in sorted(GRAPH):
        node_path = get_path(parents, distances, node)
        summary.append({
            "Düğüm": node,
            "Mesafe": "∞" if distances[node] == float("inf") else f"{distances[node]:.2f}",
            "Rota": " → ".join(node_path) if node_path else "—",
        })
    st.dataframe(pd.DataFrame(summary), hide_index=True, use_container_width=True, height=365)
    st.caption("∞: başlangıç düğümünden ulaşılamıyor")

st.markdown("#### Algoritmanın izi")
st.caption("Düğümler, öncelik kuyruğundan en küçük geçici mesafeye göre çıkarılır.")
st.dataframe(pd.DataFrame(steps), hide_index=True, use_container_width=True)
