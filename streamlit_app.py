import heapq
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Dijkstra & NetworkX Görselleştirici", layout="wide"
)


def dijkstra_visualizer(graph, start_node):
  """Dijkstra algoritmasını çalıştırır ve adım adım verileri toplar."""
  distances = {node: float("inf") for node in graph}
  distances[start_node] = 0.0
  parents = {node: None for node in graph}
  pq = [(0.0, start_node)]

  iteration_data = []

  while pq:
    current_distance, current_node = heapq.heappop(pq)

    if current_distance > distances[current_node]:
      continue

    updated_neighbors = []
    added_to_pq = []

    for neighbor, weight in graph[current_node].items():
      new_distance = current_distance + weight

      if new_distance < distances[neighbor]:
        distances[neighbor] = new_distance
        parents[neighbor] = current_node
        heapq.heappush(pq, (new_distance, neighbor))

        updated_neighbors.append(f"{neighbor} = {new_distance:.2f}")
        added_to_pq.append(f"({new_distance:.2f}, {neighbor})")

    iteration_data.append({
        "İşlenen Düğüm": f"{current_node} ({current_distance:.2f})",
        "Güncellenen Komşular": ", ".join(updated_neighbors)
        if updated_neighbors
        else "Daha kısa yol bulunmadı",
        "Öncelik Kuyruğuna Eklenenler": ", ".join(added_to_pq)
        if added_to_pq
        else "—",
    })

  return distances, parents, iteration_data


st.title("🕸️ NetworkX ve Streamlit ile Dijkstra Görselleştiricisi")

# Grafik tanımı
graph = {
    "START": {"A": 2.0, "E": 6.0, "D": 8.0},
    "A": {"B": 3.0, "C": 27 / 4, "E": 5.0},
    "B": {"C": 5.0, "E": 8 / 3},
    "C": {"TARGET": 6.0, "G": 11 / 4},
    "E": {"TARGET": 3.0, "D": 1.0},
    "D": {"TARGET": 4.25, "G": 5.0},
    "TARGET": {"G": 9.0},
    "G": {},
}

# Kenar çubuğu kontrolleri
st.sidebar.header("Algoritma Ayarları")
start_node = st.sidebar.selectbox(
    "Başlangıç Düğümü:", list(graph.keys()), index=0
)
target_node = st.sidebar.selectbox(
    "Hedef Düğüm:", list(graph.keys()), index=7
)

# Algoritmatorü çalıştır
shortest_distances, parent_pointers, all_iterations = dijkstra_visualizer(
    graph, start_node
)

# NetworkX Grafiği Oluşturma
G = nx.DiGraph()
for u, neighbors in graph.items():
  for v, weight in neighbors.items():
    G.add_edge(u, v, weight=weight)

st.subheader("1. Grafik ve En Kısa Yol Görselleştirmesi")

fig, ax = plt.subplots(figsize=(10, 6))
pos = nx.spring_layout(G, seed=42)

# Hedefe giden en kısa yolu geriye doğru takip et
path = []
curr = target_node
while curr:
  path.append(curr)
  curr = parent_pointers[curr]
path = list(reversed(path)) if shortest_distances[target_node] != float("inf") else []
path_edges = list(zip(path, path[1:]))

# Düğüm renklerini belirle
node_colors = []
for node in G.nodes():
  if node == start_node:
    node_colors.append("#2ecc71")  # Yeşil: Başlangıç
  elif node == target_node:
    node_colors.append("#e74c3c")  # Kırmızı: Hedef
  elif node in path:
    node_colors.append("#f39c12")  # Turuncu: En kısa yol üstü
  else:
    node_colors.append("#3498db")  # Mavi: Diğer

# Kenar renklerini belirle
edge_colors = ["#e74c3c" if (u, v) in path_edges else "#bdc3c7" for u, v in G.edges()]

# Çizim
nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=800, ax=ax)
nx.draw_networkx_edges(
    G, pos, edge_color=edge_colors, width=2.5, arrowstyle="->", arrowsize=20, ax=ax
)
nx.draw_networkx_labels(
    G,
    pos,
    font_size=11,
    font_weight="bold",
    font_color="white",
    font_family="sans-serif",
    ax=ax,
)

edge_labels = {
    (u, v): f"{w:.2f}" if isinstance(w, float) and w % 1 != 0 else str(int(w) if isinstance(w, float) else w)
    for u, v, w in G.edges(data="weight")
}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax)

ax.set_title(
    f"{start_node} → {target_node} Rotası (En Kısa Mesafe:"
    f" {shortest_distances[target_node]:.2f})",
    fontsize=14,
)
ax.axis("off")
st.pyplot(fig)

# Adım Adım Tablo
st.subheader("2. Algoritma Adım Detayları")
df_iterations = pd.DataFrame(all_iterations)
st.dataframe(df_iterations, use_container_width=True)

# Özet Tablo
st.subheader("3. Tüm Düğümlere En Kısa Mesafeler ve Rotalar")
summary_data = []
for node, distance in sorted(shortest_distances.items()):
  p = []
  curr = node
  while curr:
    p.append(curr)
    curr = parent_pointers[curr]
  path_str = (
      " ➔ ".join(reversed(p)) if distance != float("inf") else "Ulaşılamaz"
  )

  summary_data.append({
      "Düğüm": node,
      "Toplam Mesafe": f"{distance:.2f}"
      if distance != float("inf")
      else "Sonsuz",
      "Tam Rota": path_str,
  })

df_summary = pd.DataFrame(summary_data)
st.table(df_summary)
