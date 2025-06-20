import requests
import json
import pandas as pd
from typing import List, Dict
import matplotlib.pyplot as plt
import json
from typing import Dict, Tuple
import os
import pandas as pd
from datetime import datetime 
import networkx as nx

class STRINGAPIClient:
    """
    A client for interacting with the STRING database API to query protein-protein interactions
    蛋白质互作（STRING）数据库API的客户端，用于查询蛋白质-蛋白质相互作用
    """
    
    def __init__(self):
        # Updated API URL to version 11.5
        self.base_url = "https://version-11-5.string-db.org/api"
        self.output_format = "json"
        self.species = 9606  # Human species ID
    
    def get_protein_ids(self, protein_names: List[str]) -> Dict[str, str]:
        """
        Convert protein names to STRING database IDs
        """
        endpoint = f"{self.base_url}/json/get_string_ids"  # Updated endpoint
        
        params = {
            "identifiers": "\r".join(protein_names),
            "species": self.species,
            "limit": 1,  # Get only the best match for each protein
            "echo_query": 1
        }
        
        try:
            response = requests.post(endpoint, data=params)
            response.raise_for_status()
            results = response.json()
            
            # Create mapping of protein names to STRING IDs
            protein_mapping = {}
            for result in results:
                if "stringId" in result:
                    protein_mapping[result["queryItem"]] = result["stringId"]
            
            return protein_mapping
            
        except requests.exceptions.RequestException as e:
            print(f"Error getting protein IDs: {e}")
            return {}

    def get_interactions(self, string_ids: List[str], required_score: float = 0.4) -> pd.DataFrame:
        """
        Get protein-protein interactions between the provided STRING IDs
        """
        endpoint = f"{self.base_url}/json/network"  # Updated endpoint
        
        params = {
            "identifiers": "\r".join(string_ids),
            "species": self.species,
            "required_score": int(required_score * 1000),  # Convert score to STRING format (0-1000)
            "network_flavor": "confidence"  # Get confidence scores
        }
        
        try:
            response = requests.post(endpoint, data=params)
            response.raise_for_status()
            results = response.json()
            
            # Convert results to DataFrame
            if results:
                df = pd.DataFrame(results)
                # Select and rename relevant columns
                if 'preferredName_A' in df.columns and 'preferredName_B' in df.columns and 'score' in df.columns:
                    interaction_df = df[['preferredName_A', 'preferredName_B', 'score']].copy()
                    # Convert score back to 0-1 range
                    interaction_df['score'] = interaction_df['score'] #/ 1000
                    
                    return interaction_df.rename(columns={
                        'preferredName_A': 'Protein_A',
                        'preferredName_B': 'Protein_B',
                        'score': 'Interaction_Score'
                    })
            
            return pd.DataFrame(columns=['Protein_A', 'Protein_B', 'Interaction_Score'])
            
        except requests.exceptions.RequestException as e:

            return pd.DataFrame(columns=['Protein_A', 'Protein_B', 'Interaction_Score'])
        



# def query_protein_interactions(protein_list: List[str], min_score: float = 0.4) -> pd.DataFrame:
#     """
#     Main function to query protein-protein interactions for a list of proteins
    
#     Args:
#         protein_list: List of protein names to query
#         min_score: Minimum required interaction score (0-1)
        
#     Returns:
#         DataFrame containing interaction information
#     """
#     client = STRINGAPIClient()
    
#     # Get STRING IDs for proteins
#     protein_mapping = client.get_protein_ids(protein_list)
    
#     if not protein_mapping:

#         return pd.DataFrame()
    
    
#     # Get interactions
#     string_ids = list(protein_mapping.values())
#     interactions_df = client.get_interactions(string_ids, min_score)
    
#     unique_interactions = interactions_df.drop_duplicates(
#                 subset=["Protein_A", "Protein_B"],
#                 keep='first'  # keep the first occurrence of each duplicate
#             )
            
#         # 2. Convert to desired JSON format
#     interactions_json = {
#         "interactions": [
#             {
#                 "source": row["Protein_A"],
#                 "target": row["Protein_B"],
#                 "interaction_score": float(row["Interaction_Score"])
#             }
#             for _, row in unique_interactions.iterrows()
#         ]
#     }
    

#     return interactions_json




from typing import List, Dict, Any
import pandas as pd

def query_protein_interactions(protein_list: List[str], min_score: float = 0.4) -> List[Dict[str, Any]]:
    """
    查询蛋白质-蛋白质相互作用信息
    
    Args:
        protein_list: 要查询的蛋白质名称列表
        min_score: 最小相互作用分数阈值(0-1)
        
    Returns:
        包含相互作用信息的列表，每个元素是一个字典，结构为：
        [
            {'source': 'ACE2', 'target': 'IL6', 'interaction_score': 0.9},
            ...
        ]
        如果无结果返回空列表
    """
    if not protein_list:  # 空输入检查
        return []

    client = STRINGAPIClient()
    
    # 1. 获取STRING ID映射
    protein_mapping = client.get_protein_ids(protein_list)
    if not protein_mapping:
        return []

    # 2. 查询相互作用数据
    interactions_df = client.get_interactions(list(protein_mapping.values()), min_score)
    if interactions_df.empty:
        return []
    
     # 3. 处理并格式化结果
    interactions_json = [
        {
            'source': row['Protein_A'],
            'target': row['Protein_B'],
            'interaction_score': round(float(row['Interaction_Score']), 4)
        }
        for _, row in interactions_df.drop_duplicates(
            subset=["Protein_A", "Protein_B"],
            keep='first'
        ).iterrows()
    ]

   
    return interactions_json

import networkx as nx
import matplotlib
matplotlib.use('Agg')  # 设置matplotlib使用非GUI后端，避免在非主线程中创建窗口
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import Tuple, List
from matplotlib.colors import LinearSegmentedColormap

# def analyze_protein_network(data: list, 
#                           visualize: bool = True,
#                           top_n: int = 5,
#                           label_non_highlighted: bool = True) -> Tuple[pd.DataFrame, dict]:
#     """
#     增强版蛋白互作网络分析函数（含MCC等高级网络指标）
    
#     参数:
#         data: 包含interactions的字典
#         visualize: 是否可视化
#         top_n: 高亮显示的关键节点数
#         label_non_highlighted: 是否显示非高亮节点标签
    
#     返回:
#         Tuple: (重要性排序DataFrame, 增强版网络指标字典)
#     """
#     # 1. 构建网络图（带权重）
#     G = nx.Graph()
#     for interaction in data:
#         G.add_edge(interaction["source"], 
#                   interaction["target"], 
#                   weight=float(interaction.get("interaction_score", 1.0)))
    

    
#     # 2. 关键靶点分析（含MCC参与度）
#     def calculate_centralities(graph):
#         # 先计算最大团
#         cliques = list(nx.find_cliques(graph))
#         node_clique_counts = {n: sum(1 for c in cliques if n in c) for n in graph.nodes()}
        
#         metrics = {
#             # "Degree": nx.degree_centrality(graph),
#             # "Betweenness": nx.betweenness_centrality(graph, weight='weight'),
#             # "PageRank": nx.pagerank(graph, weight='weight'),
#             "Closeness": {n: 1/v if v !=0 else 0 for n,v in nx.closeness_centrality(graph, distance='weight').items()},
#             "MCC_Participation": {n: node_clique_counts[n]/len(cliques) if cliques else 0 
#                                  for n in graph.nodes()}  # 节点参与最大团的比例
#         }
#         return metrics
    
#     # 合并所有指标
#     centralities = calculate_centralities(G)
#     metrics_df = pd.DataFrame(centralities)
    
#     # 归一化处理
#     def safe_normalize(series):
#         range_val = series.max() - series.min()
#         return (series - series.min()) / range_val if range_val > 0 else series * 0 + 0.5
    
#     normalized = metrics_df.apply(safe_normalize)
#     metrics_df['Composite_Score'] = normalized.mean(axis=1)
#     sorted_nodes = metrics_df.sort_values('Composite_Score', ascending=False)

#     # 3. 可视化（保持原有样式）
#     if visualize:
#         plt.figure(figsize=(16, 6))
        
#         # ===== 网络图 =====
#         plt.subplot(1, 2, 1)
#         pos = nx.spring_layout(G, seed=42, k=0.8/max(1, len(G)**0.5))
        
#         # 绘制边（细线）
#         edge_weights = [G[u][v]['weight'] for u,v in G.edges()]
#         min_w, max_w = min(edge_weights), max(edge_weights)
#         edge_widths = [0.5 + 2*(w-min_w)/(max_w-min_w) if max_w > min_w else 1 
#                       for w in edge_weights]
#         nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color='#888888', alpha=0.6)
        
#         # 绘制节点
#         nx.draw_networkx_nodes(G, pos, node_size=400, node_color='#1f78b4', alpha=0.9)
        
#         # 高亮关键节点
#         if top_n > 0:
#             highlight_nodes = sorted_nodes.index[:top_n]
#             nx.draw_networkx_nodes(G, pos, nodelist=highlight_nodes,
#                                  node_size=800, node_color='#e31a1c')
#             nx.draw_networkx_labels(G, pos, labels={n:n for n in highlight_nodes},
#                                   font_size=10, font_weight='bold')
        
#         # 非高亮节点标签
#         if label_non_highlighted and len(G.nodes()) <= 20:
#             non_highlight = [n for n in G.nodes() if n not in sorted_nodes.index[:top_n]]
#             nx.draw_networkx_labels(G, pos, labels={n:n for n in non_highlight},
#                                   font_size=8, alpha=0.7)
        
#         plt.title(f"Network (Top {top_n} Key Targets in Red)\nNodes: {len(G.nodes())}, Edges: {len(G.edges())}")
#         plt.axis('off')

#         # ===== 热力图 =====
#         plt.subplot(1, 2, 2)
#         display_data = sorted_nodes.head(min(8, len(G.nodes()))).drop('Composite_Score', axis=1)
#         display_data = display_data.apply(lambda x: np.clip(x, 0, 1))
        
#         cmap = LinearSegmentedColormap.from_list("GreyRed", [(0.8,0.8,0.8), (1,0,0)])
#         heatmap = plt.imshow(display_data, cmap=cmap, vmin=0, vmax=1, aspect='auto')
        
#         for i in range(len(display_data)):
#             for j in range(len(display_data.columns)):
#                 value = display_data.iloc[i,j]
#                 text_color = 'black' if value < 0.7 else 'white'
#                 plt.text(j, i, f"{value:.2f}", ha="center", va="center", 
#                         color=text_color, fontsize=8)
        
#         plt.colorbar(heatmap, label='Normalized Value')
#         plt.xticks(range(len(display_data.columns)), display_data.columns, rotation=45)
#         plt.yticks(range(len(display_data)), display_data.index)
#         plt.title("Key Targets Metrics (Grey=Low, Red=High)")
#         plt.tight_layout()
#         plt.show()

#     return sorted_nodes


# def analyze_protein_network(data: list, 
#                           visualize: bool = True,
#                           top_n: int = 5,
#                           label_non_highlighted: bool = True) -> Tuple[pd.DataFrame, dict]:
#     """
#     Enhanced protein-protein interaction network analysis (with advanced metrics like MCC)
    
#     Parameters:
#         data: List of interaction dictionaries
#         visualize: Whether to visualize the network
#         top_n: Number of top nodes to highlight
#         label_non_highlighted: Whether to show labels for non-highlighted nodes
    
#     Returns:
#         Tuple: (DataFrame of node importance, Dictionary of network metrics)
#     """
#     # 1. Build weighted network graph
#     G = nx.Graph()
#     for interaction in data:
#         G.add_edge(interaction["source"], 
#                   interaction["target"], 
#                   weight=float(interaction.get("interaction_score", 1.0)))
    
#     # 2. Key target analysis (including MCC participation)
#     def calculate_centralities(graph):
#         # Calculate maximal cliques
#         cliques = list(nx.find_cliques(graph))
#         node_clique_counts = {n: sum(1 for c in cliques if n in c) for n in graph.nodes()}
        
#         metrics = {
#             "Closeness": {n: 1/v if v !=0 else 0 for n,v in nx.closeness_centrality(graph, distance='weight').items()},
#             "MCC_Participation": {n: node_clique_counts[n]/len(cliques) if cliques else 0 
#                                  for n in graph.nodes()}  # Node participation in maximal cliques
#         }
#         return metrics
    
#     # Calculate all metrics
#     centralities = calculate_centralities(G)
#     metrics_df = pd.DataFrame(centralities)
    
#     # Normalize metrics
#     def safe_normalize(series):
#         range_val = series.max() - series.min()
#         return (series - series.min()) / range_val if range_val > 0 else series * 0 + 0.5
    
#     normalized = metrics_df.apply(safe_normalize)
#     metrics_df['Composite_Score'] = normalized.mean(axis=1)
#     sorted_nodes = metrics_df.sort_values('Composite_Score', ascending=False)

#     # 3. Visualization (network only)
#     if visualize:
#         plt.figure(figsize=(10, 8))
#         pos = nx.spring_layout(G, seed=42, k=0.8/max(1, len(G)**0.5))
        
#         # Draw edges (thin lines)
#         edge_weights = [G[u][v]['weight'] for u,v in G.edges()]
#         min_w, max_w = min(edge_weights), max(edge_weights)
#         edge_widths = [0.5 + 2*(w-min_w)/(max_w-min_w) if max_w > min_w else 1 
#                       for w in edge_weights]
#         nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color='#888888', alpha=0.6)
        
#         # Draw nodes
#         nx.draw_networkx_nodes(G, pos, node_size=400, node_color='#1f78b4', alpha=0.9)
        
#         # Highlight key nodes
#         if top_n > 0:
#             highlight_nodes = sorted_nodes.index[:top_n]
#             nx.draw_networkx_nodes(G, pos, nodelist=highlight_nodes,
#                                  node_size=800, node_color='#e31a1c')
#             nx.draw_networkx_labels(G, pos, labels={n:n for n in highlight_nodes},
#                                   font_size=10, font_weight='bold')
        
#         # Non-highlighted node labels
#         if label_non_highlighted and len(G.nodes()) <= 20:
#             non_highlight = [n for n in G.nodes() if n not in sorted_nodes.index[:top_n]]
#             nx.draw_networkx_labels(G, pos, labels={n:n for n in non_highlight},
#                                   font_size=8, alpha=0.7)
        
#         plt.title(f"Protein Interaction Network (Top {top_n} Key Targets in Red)\nNodes: {len(G.nodes())}, Edges: {len(G.edges())}")
#         plt.axis('off')
#         plt.tight_layout()
#         plt.show()

#     return sorted_nodes


def analyze_protein_network(data: list, 
                          visualize: bool = True,
                          top_n: int = 5,
                          label_non_highlighted: bool = True,
                          figsize=(10, 8),
                          dpi=300) -> Tuple[pd.DataFrame, dict, str]:
    """
    Enhanced protein-protein interaction network analysis (with advanced metrics like MCC)
    
    Parameters:
        data: List of interaction dictionaries
        visualize: Whether to visualize the network
        top_n: Number of top nodes to highlight
        label_non_highlighted: Whether to show labels for non-highlighted nodes
        figsize: Figure size for visualization
        dpi: DPI for saved image
    
    Returns:
        Tuple: (DataFrame of node importance, Dictionary of network metrics, Summary with link)
    """
    # 1. Build weighted network graph
    G = nx.Graph()
    for interaction in data:
        G.add_edge(interaction["source"], 
                  interaction["target"], 
                  weight=float(interaction.get("interaction_score", 1.0)))
    
    # 2. Key target analysis (including MCC participation)
    def calculate_centralities(graph):
        # Calculate maximal cliques
        cliques = list(nx.find_cliques(graph))
        node_clique_counts = {n: sum(1 for c in cliques if n in c) for n in graph.nodes()}
        
        metrics = {
            "Closeness": {n: 1/v if v !=0 else 0 for n,v in nx.closeness_centrality(graph, distance='weight').items()},
            "MCC_Participation": {n: node_clique_counts[n]/len(cliques) if cliques else 0 
                                 for n in graph.nodes()}  # Node participation in maximal cliques
        }
        return metrics
    
    # Calculate all metrics
    centralities = calculate_centralities(G)
    metrics_df = pd.DataFrame(centralities)
    
    # Normalize metrics
    def safe_normalize(series):
        range_val = series.max() - series.min()
        return (series - series.min()) / range_val if range_val > 0 else series * 0 + 0.5
    
    normalized = metrics_df.apply(safe_normalize)
    metrics_df['Composite_Score'] = normalized.mean(axis=1)
    sorted_nodes = metrics_df.sort_values('Composite_Score', ascending=False)

    # Prepare summary information
    summary_lines = [
        f"蛋白质互作网络分析结果:",
        f"- 节点数量: {len(G.nodes())}",
        f"- 边数量: {len(G.edges())}",
        f"- 网络密度: {nx.density(G):.4f}",
        f"- 平均聚类系数: {nx.average_clustering(G):.4f}",
        f"\nTop {top_n} 关键靶点:",
    ]
    
    for i, (node, row) in enumerate(sorted_nodes.head(top_n).iterrows(), 1):
        summary_lines.append(f"{i}. {node} (综合评分: {row['Composite_Score']:.3f})")
    
    # 3. Visualization (network only)
    save_info = ""
    if visualize:
        plt.style.use('ggplot')
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        
        fig, ax = plt.subplots(figsize=figsize, facecolor='#F5F5F5')
        pos = nx.spring_layout(G, seed=42, k=0.8/max(1, len(G)**0.5))
        
        # Draw edges (soft pastel colors)
        edge_weights = [G[u][v]['weight'] for u,v in G.edges()]
        min_w, max_w = min(edge_weights), max(edge_weights)
        edge_widths = [0.5 + 2*(w-min_w)/(max_w-min_w) if max_w > min_w else 1 
                      for w in edge_weights]
        nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color='#B0BEC5', alpha=0.5, ax=ax)  # Soft blue-gray
        
        # Draw nodes (soft colors)
        nx.draw_networkx_nodes(G, pos, node_size=400, node_color='#90CAF9', alpha=0.9, ax=ax)  # Soft blue
        
        # Highlight key nodes (soft red)
        if top_n > 0:
            highlight_nodes = sorted_nodes.index[:top_n]
            nx.draw_networkx_nodes(G, pos, nodelist=highlight_nodes,
                                 node_size=800, node_color='#D9675A', ax=ax)  # Soft red
            nx.draw_networkx_labels(G, pos, labels={n:n for n in highlight_nodes},
                                  font_size=10, font_weight='bold', ax=ax)
        
        # Non-highlighted node labels
        if label_non_highlighted and len(G.nodes()) <= 20:
            non_highlight = [n for n in G.nodes() if n not in sorted_nodes.index[:top_n]]
            nx.draw_networkx_labels(G, pos, labels={n:n for n in non_highlight},
                                  font_size=8, alpha=0.7, ax=ax)
        
        ax.set_title(f"Protein-Protein Interaction Network (Top {top_n} Key Targets Highlighted)\nNodes: {len(G.nodes())}, Edges: {len(G.edges())}", 
                    fontsize=12, pad=20)
        ax.axis('off')
        
        # Add legend with soft colors
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', label='Targets',
                      markerfacecolor='#90CAF9', markersize=10),
            plt.Line2D([0], [0], marker='o', color='w', label=f'Top {top_n} key targets',
                      markerfacecolor='#EF9A9A', markersize=10)
        ]
        ax.legend(handles=legend_elements, loc='upper right', frameon=True, 
                 framealpha=0.9, edgecolor='#333333', fontsize=10)
        
        plt.tight_layout()
        
        # Save image
        base_dir = "files"
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        save_path = os.path.join(base_dir, f"protein_network_analysis_{current_time}.png")
        fig.savefig(save_path, dpi=dpi, bbox_inches='tight', facecolor=fig.get_facecolor())
        plt.close()
        
        save_info = f"\n\nThe protein-protein interaction network diagram has been saved to {save_path}"
    
    summary_with_link = "\n".join(summary_lines) + save_info
    
    return summary_with_link



# Example usage
if __name__ == "__main__":
    # Example protein list
    genes = [
        'IL6', 'IL10', 'CXCL8', 'STAT3', 'TNF', 'VEGFA', 'SOD1'
    ]
    
    print("Starting protein interaction query...")
    interactions_json = query_protein_interactions(genes, min_score=0.4)
    print(interactions_json)

        # 将PPI写入network_plot.json文件，用于展示网络图
    with open("client/public/data/network_plot.json", "w", encoding="utf-8") as f:
        json.dump(interactions_json, f, ensure_ascii=False)


    # 分析网络
    result = analyze_protein_network(interactions_json)


    print("\n节点重要性 (含MCC参与度):")
