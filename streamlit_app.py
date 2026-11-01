import heapq

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Cisco Packet Tracer · Dijkstra",
    page_icon="🌐",
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

NODE_POSITIONS = {
    "START": (0.08, 0.53), "A": (0.27, 0.78), "B": (0.47, 0.78),
    "C": (0.67, 0.78), "E": (0.39, 0.31), "D": (0.59, 0.31),
    "TARGET": (0.82, 0.53), "G": (0.96, 0.29),
}


def build_frames(graph, start):
    """Return one immutable UI snapshot for each algorithm action."""
    distances = {node: float("inf") for node in graph}
    parents = {node: None for node in graph}
    distances[start] = 0.0
    queue = [(0.0, start)]
    visited = set()
    frames = []

    def snapshot(message, current=None, neighbor=None, action="INIT"):
        frames.append({
            "distances": distances.copy(),
            "parents": parents.copy(),
            "visited": visited.copy(),
            "queue": sorted(queue),
            "current": current,
            "neighbor": neighbor,
            "message": message,
            "action": action,
        })

    snapshot(f"[SYSTEM] SPF başlatıldı. Kaynak düğüm: {start}")
    while queue:
        distance, node = heapq.heappop(queue)
        if node in visited or distance > distances[node]:
            snapshot(f"[SKIP] Eski kuyruk kaydı atlandı: {node} ({distance:.2f})", node, action="SKIP")
            continue

        snapshot(f"[PROCESS] Kuyruktan çıkarıldı: {node} ({distance:.2f})", node, action="POLL")
        visited.add(node)
        snapshot(f"[VISITED] {node} işlendi olarak işaretlendi.", node, action="VISIT")

        for neighbor, weight in graph[node].items():
            snapshot(
                f"[DISCOVERY] {node} → {neighbor} bağlantısı inceleniyor · maliyet {weight:.2f}",
                node, neighbor, "EXAMINE",
            )
            candidate = distances[node] + weight
            if neighbor not in visited and candidate < distances[neighbor]:
                distances[neighbor] = candidate
                parents[neighbor] = node
                heapq.heappush(queue, (candidate, neighbor))
                snapshot(
                    f"[RELAXATION] {neighbor} mesafesi {candidate:.2f} olarak güncellendi · ata {node}",
                    node, neighbor, "UPDATE",
                )
            else:
                old = distances[neighbor]
                old_label = "∞" if old == float("inf") else f"{old:.2f}"
                snapshot(
                    f"[SKIP] {neighbor} için daha kısa mesafe korunuyor ({old_label}).",
                    node, neighbor, "NO_UPDATE",
                )

    snapshot("[COMPLETE] Tüm erişilebilir düğümler işlendi.", action="COMPLETE")
    return frames


def path_to(parents, distances, node):
    if distances[node] == float("inf"):
        return []
    path = []
    while node is not None:
        path.append(node)
        node = parents[node]
    return path[::-1]


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');
:root { --cyan:#00bceb; --bg:#060b13; --panel:#0f172a; --border:#1e293b; --green:#10b981; --amber:#fbbf24; --rose:#f43f5e; }
.stApp { background:radial-gradient(ellipse at 50% -25%,#12243a 0%,#080e18 58%,#060b13 100%); color:#dbe5f1; }
html,body,[class*="css"] { font-family:'Inter',sans-serif; }
h1,h2,h3 { letter-spacing:-.035em; }
section[data-testid="stSidebar"] { background:rgba(10,17,30,.96); border-right:1px solid var(--border); }
.block-container { padding-top:1.35rem; padding-bottom:2rem; max-width:1800px; }
.topbar { display:flex; justify-content:space-between; align-items:center; padding:.8rem 1rem; margin-bottom:1.25rem; background:rgba(15,23,42,.78); border:1px solid var(--border); border-radius:12px; }
.brand { color:var(--cyan); font-weight:700; letter-spacing:.11em; font-size:.95rem; }
.mono,.eyebrow { font-family:'Fira Code',monospace; }
.eyebrow { color:#7d91a9; font-size:.69rem; letter-spacing:.12em; }
.status { font:600 .7rem 'Fira Code',monospace; color:#34d399; padding:.42rem .65rem; background:#071a19; border:1px solid #145344; border-radius:6px; }
.panel { background:linear-gradient(145deg,rgba(15,23,42,.96),rgba(9,16,28,.96)); border:1px solid #1e293b; border-radius:12px; padding:.85rem 1rem; }
.terminal { background:#070c14; border:1px solid #1e293b; border-radius:9px; padding:.8rem; color:#cbd5e1; font: .75rem 'Fira Code',monospace; min-height:4rem; }
div[data-testid="stMetric"] { background:rgba(15,23,42,.85); border:1px solid #1e293b; border-radius:10px; padding:12px 15px; }
div[data-testid="stMetricLabel"] { color:#94a3b8; font-size:.75rem; }
div[data-testid="stMetricValue"] { color:#e2e8f0; font-family:'Fira Code',monospace; }
div[data-testid="stDataFrame"] { border:1px solid #1e293b; border-radius:9px; overflow:hidden; }
div.stButton > button { border-radius:7px; font-family:'Fira Code',monospace; font-weight:600; }
div[data-testid="stSelectbox"] label, div[data-testid="stSlider"] label { font-family:'Fira Code',monospace; color:#9aaabd; font-size:.75rem; }
</style>
""", unsafe_allow_html=True)


with st.sidebar:
    st.markdown("### `≋`  ROTA KONTROLÜ")
    st.caption("DIJKSTRA · SHORTEST PATH FIRST")
    start = st.selectbox("Başlangıç · SRC", list(GRAPH), index=0, key="start")
    target = st.selectbox("Hedef · DST", list(GRAPH), index=list(GRAPH).index("TARGET"), key="target")
    st.caption("Adım modu, algoritma olayları arasında ilerler. ‘Tümünü çalıştır’ kalan adımları tek seferde tamamlar.")
    st.divider()

    state_key = (start, target)
    if st.session_state.get("state_key") != state_key:
        st.session_state.state_key = state_key
        st.session_state.frame_index = 0
        st.session_state.log_cleared = False
        st.session_state.traffic = False

    frames = build_frames(GRAPH, start)
    last = len(frames) - 1
    index = st.session_state.get("frame_index", 0)
    index = max(0, min(index, last))

    c1, c2, c3 = st.columns(3)
    if c1.button("▶ Tümünü çalıştır", use_container_width=True, disabled=index == last):
        st.session_state.frame_index = last
        st.rerun()
    if c2.button("▸ Adım", use_container_width=True, disabled=index == last):
        st.session_state.frame_index = min(index + 1, last)
        st.rerun()
    if c3.button("↺ Sıfırla", use_container_width=True):
        st.session_state.frame_index = 0
        st.session_state.traffic = False
        st.session_state.log_cleared = False
        st.rerun()

    current_frame = frames[index]
    completed = index == last
    if st.button("➤  En kısa rotada paket trafiği", use_container_width=True, disabled=not completed):
        st.session_state.traffic = True
        st.rerun()
    if st.session_state.get("traffic"):
        st.success("Paket rotası etkin · " + " → ".join(path_to(current_frame["parents"], current_frame["distances"], target)))
    st.divider()

    st.markdown("#### ÖNCELİK KUYRUĞU · MIN-HEAP")
    queue = current_frame["queue"]
    if queue:
        for distance, node in queue:
            st.markdown(f"`{node}`　<span style='color:#fbbf24;font-family:Fira Code'>{distance:.2f}</span>", unsafe_allow_html=True)
    else:
        st.caption("Kuyruk boş.")

    st.markdown("#### YÖNLENDİRME TABLOSU")
    routing_rows = []
    for node in GRAPH:
        distance = current_frame["distances"][node]
        routing_rows.append({
            "Düğüm": node,
            "Mesafe": "∞" if distance == float("inf") else f"{distance:.2f}",
            "Ata": current_frame["parents"][node] or "—",
            "Durum": "KAYNAK" if node == start else "İŞLENDİ" if node in current_frame["visited"] else "KUYRUKTA" if distance < float("inf") else "BEKLEMEDE",
        })
    st.dataframe(pd.DataFrame(routing_rows), hide_index=True, use_container_width=True, height=280)


frame = frames[st.session_state.frame_index]
distances, parents = frame["distances"], frame["parents"]
route = path_to(parents, distances, target) if st.session_state.frame_index == last else []
route_edges = set(zip(route, route[1:]))

st.markdown(f"<div class='topbar'><div><div class='brand'>◈ CISCO PACKET TRACER <span style='font-size:.65rem;background:#062230;padding:.2rem .4rem;border-radius:4px'>SPF SIMULATOR</span></div><div class='eyebrow' style='margin-top:.35rem'>NETWORK ROUTING · DIJKSTRA SIMULATION</div></div><div class='status'>● LINK STATUS: ONLINE</div></div>", unsafe_allow_html=True)

col_graph, col_stats = st.columns([2.2, 1], gap="large")
with col_graph:
    st.markdown("#### NETWORK TOPOLOGY")
    st.caption("Oklar bağlantı yönünü gösterir · Ağırlıklar kenar maliyetidir")
    network = nx.DiGraph()
    for source, neighbors in GRAPH.items():
        for dest, weight in neighbors.items():
            network.add_edge(source, dest, weight=weight)

    active_node, active_neighbor = frame["current"], frame["neighbor"]
    colors = []
    for node in network.nodes:
        if node == start:
            colors.append("#047857")
        elif node == target:
            colors.append("#9f1239")
        elif node == active_node or node == active_neighbor:
            colors.append("#92400e")
        elif node in route:
            colors.append("#075985")
        elif node in frame["visited"]:
            colors.append("#15253a")
        else:
            colors.append("#172033")
    edge_colors = []
    edge_widths = []
    for edge in network.edges:
        if edge in route_edges:
            edge_colors.append("#00bceb")
            edge_widths.append(3.5)
        elif edge == (active_node, active_neighbor):
            edge_colors.append("#fbbf24")
            edge_widths.append(3)
        else:
            edge_colors.append("#334155")
            edge_widths.append(1.4)

    fig, ax = plt.subplots(figsize=(12.5, 6.8), facecolor="#080e18")
    ax.set_facecolor("#080e18")
    nx.draw_networkx_nodes(network, NODE_POSITIONS, node_color=colors, node_size=1450, linewidths=1.8, edgecolors="#40516a", ax=ax)
    nx.draw_networkx_edges(network, NODE_POSITIONS, edge_color=edge_colors, width=edge_widths, arrows=True, arrowstyle="-|>", arrowsize=20, connectionstyle="arc3,rad=0.035", min_source_margin=24, min_target_margin=28, ax=ax)
    nx.draw_networkx_labels(network, NODE_POSITIONS, font_size=9, font_weight="bold", font_color="#f1f5f9", ax=ax)
    weights = {(u, v): f"{w:.2f}" for u, v, w in network.edges(data="weight")}
    nx.draw_networkx_edge_labels(network, NODE_POSITIONS, edge_labels=weights, font_size=8, font_color="#a8bbd0", rotate=False, bbox={"alpha": .95, "color": "#080e18", "pad": 2, "edgecolor": "#1e293b"}, ax=ax)
    ax.set_xlim(-.04, 1.04)
    ax.set_ylim(.05, 1.0)
    ax.axis("off")
    fig.tight_layout(pad=.3)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
    st.markdown("🟢 Kaynak　 🔴 Hedef　 🟠 Aktif düğüm/bağlantı　 🔹 En kısa rota", unsafe_allow_html=True)

with col_stats:
    st.markdown("#### ROUTE SUMMARY")
    distance = distances[target]
    st.metric("HEDEF MALİYETİ", "∞" if distance == float("inf") else f"{distance:.2f}")
    st.metric("İŞLENEN DÜĞÜM", frame["current"] or "—")
    st.metric("KUYRUKTA", len(frame["queue"]))
    st.markdown("#### EN KISA ROTA")
    if route:
        st.markdown(f"<div class='panel' style='color:#00bceb;font-family:Fira Code,monospace'>{' &nbsp;›&nbsp; '.join(route)}</div>", unsafe_allow_html=True)
    elif completed:
        st.markdown("<div class='panel'>Hedefe ulaşılamıyor.</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='panel' style='color:#94a3b8'>Simülasyon tamamlandığında rota gösterilir.</div>", unsafe_allow_html=True)
    st.markdown("#### RENK ANAHTARI")
    st.markdown("<div class='panel'>🟢 Başlangıç düğümü<br>🔴 Hedef düğüm<br>🟠 Aktif incelenen bağlantı<br>🔹 Tamamlanan en kısa rota</div>", unsafe_allow_html=True)

st.markdown("")
trace_col, console_col = st.columns([1.25, 1], gap="large")
with trace_col:
    st.markdown("#### ALGORİTMA ADIMLARI")
    st.progress((st.session_state.frame_index + 1) / len(frames), text=f"Olay {st.session_state.frame_index + 1} / {len(frames)}")
    st.markdown(f"<div class='terminal'>{frame['message']}</div>", unsafe_allow_html=True)
with console_col:
    st.markdown("#### CISCO IOS CONSOLE LOG")
    st.caption("Son algoritma olayları")
    if st.button("⌫ Konsolu temizle", key="clear_log"):
        st.session_state.log_cleared = True
    if st.session_state.get("log_cleared"):
        st.markdown("<div class='terminal'>Konsol görünümü temizlendi. İlerleme sürdükçe yeni olaylar görünür.</div>", unsafe_allow_html=True)
    else:
        logs = [f['message'] for f in frames[:st.session_state.frame_index + 1]][-7:]
        st.markdown("<div class='terminal'>" + "<br>".join(logs) + "</div>", unsafe_allow_html=True)

st.markdown("#### TÜM DÜĞÜMLERE EN KISA MESAFELER")
summary = []
for node in sorted(GRAPH):
    node_path = path_to(parents, distances, node)
    summary.append({
        "Düğüm": node,
        "Mesafe": "∞" if distances[node] == float("inf") else f"{distances[node]:.2f}",
        "Rota": " → ".join(node_path) if node_path else "Ulaşılamaz",
    })
st.dataframe(pd.DataFrame(summary), hide_index=True, use_container_width=True)
