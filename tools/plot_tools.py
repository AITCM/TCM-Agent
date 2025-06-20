import matplotlib
matplotlib.use('Agg')  # 设置matplotlib使用非GUI后端，避免在非主线程中创建窗口
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np
import pandas as pd
from datetime import datetime 
import networkx as nx

from agents.pathway_enrich import save_dict_to_excel

def plot_terms_by_pvalue(data, term_col='Term', pvalue_col='Adjusted P-value', 
                         figsize=(10, 12), color='skyblue', 
                         title='Terms Sorted by Adjusted P-value',
                         save_path=None, dpi=300, format='png',
                         log_transform=False):
    # If data is a string, assume it's a file path and load it
    if isinstance(data, str):
        if data.endswith('.csv'):
            df = pd.read_csv(data)
        elif data.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(data)
        else:
            raise ValueError("File format not supported. Please provide a CSV or Excel file.")
    else:
        # Create a deep copy to avoid modifying the original data
        df = data.copy(deep=True)
    
    # Apply -log10 transformation if requested
    if log_transform:
        df[pvalue_col] = [-np.log10(x) for x in df[pvalue_col]]
        x_label = '-log10(Adjusted P-value)'
    else:
        x_label = 'Adjusted P-value'
    
    # Sort by adjusted p-value in ascending order
    df_sorted = df.sort_values(by=pvalue_col)
    
    # Create the figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Create horizontal bar plot
    sns.barplot(x=pvalue_col, y=term_col, data=df_sorted, color=color, ax=ax)
    
    # Add labels and title
    ax.set_xlabel(x_label)
    ax.set_ylabel('Term')
    ax.set_title(title)
    
    # Add p-value annotations to the end of each bar
    for i, p in enumerate(df_sorted[pvalue_col]):
        ax.text(p + p*0.01, i, f'{p:.2e}', va='center')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the figure if a save path is provided
    if save_path is not None:
        # Create directory if it doesn't exist
        save_dir = os.path.dirname(save_path)
        if save_dir and not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        # Add file extension if not in the save_path
        if not save_path.lower().endswith(f'.{format.lower()}'):
            save_path = f"{save_path}.{format}"
            
        # Save the figure
        fig.savefig(save_path, dpi=dpi, format=format, bbox_inches='tight')
        print(f"Figure saved to: {save_path}")
    
    return fig, ax

def draw_pvalue_analysis(summary):
    save_info = ""
    base_dir = "files"
    os.makedirs(base_dir, exist_ok=True)
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")

    for index, data in summary.items():
        # 使用索引作为文件名的一部分，确保唯一性
        save_path = os.path.join(base_dir, f"pvalue_analysis_{index}_{current_time}")
        if '未找到匹配的疾病结果' in data:
            continue
        else:
            # 使用log_transform参数而不是直接修改数据
            fig, ax = plot_terms_by_pvalue(
                data, 
                save_path=save_path,
                log_transform=True,  # 在函数内部应用转换
                title=f"{index} - Terms Sorted by -log10(Adjusted P-value)"
            )
            plt.close(fig)  # 关闭图形以释放内存
            
            save_info += f"{index} 的富集结果图已保存到 {save_path}.png\n"
    return save_info


def plot_enrichment(summary, enrichment_results):

    # file_path： 带当前日期的文件名
    file_name = f"enrichment_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    file_path = f"files/{file_name}"
    save_dict_to_excel(enrichment_results, file_path)

    # 绘制富集分析结果图保存位置信息，示例位置：Figure saved to: files\pvalue_analysis_GO_Biological_Process_2025_20250414012205.png

    save_info = draw_pvalue_analysis(summary)

    # 构建文件下载链接
    download_link = f"/files/{file_name}"
    
    # 在摘要末尾添加下载链接信息，并使其更加醒目
    summary_with_link = str(summary) + f"\n\n## 富集分析完整结果 📊\n\n您可以**点击下方链接**下载完整的富集分析结果Excel文件：\n\n**👉 [下载富集分析完整Excel文件]({download_link}) 👈 **\n\n富集分析结果图保存位置：{save_info}\n\n[中药靶点信息如右图]"

    return summary_with_link

def plot_compound_target_activity(result_df, output_lines, figsize=(12, 10), dpi=300, 
                                node_size=3000, font_size=20):
    import matplotlib.pyplot as plt
    import networkx as nx
    import numpy as np
    from datetime import datetime
    import os

    # 设置全局样式
    plt.style.use('seaborn-v0_8-darkgrid')  # 深色网格背景
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['axes.titleweight'] = 'bold'
    plt.rcParams['axes.labelweight'] = 'bold'

    # 创建有向图
    G = nx.DiGraph()

    # 动态边宽度（根据数据调整）
    max_degree = result_df.shape[0]
    edge_widths = np.linspace(1.2, 2.5, num=max_degree)

    # 添加节点和边（带动态属性）
    for idx, row in result_df.iterrows():
        compound = row['DrugName']
        target = row['GeneName']
        
        # 节点属性
        G.add_node(compound, 
                  node_type='compound', 
                  color='#FF9E4F',  # 暖橙色
                  size=node_size * 1.2, 
                  shape='h',        # 六边形
                  alpha=0.95,
                  edgecolor='#333333',
                  linewidths=1.5)
        
        G.add_node(target, 
                  node_type='target', 
                  color='#6A9F58',  # 冷绿色
                  size=node_size, 
                  shape='o',        # 圆形
                  alpha=0.95,
                  edgecolor='#333333',
                  linewidths=1.5)
        
        # 边属性（动态宽度和透明度）
        G.add_edge(compound, target, 
                   width=edge_widths[idx % max_degree],
                   color='#7F7F7F', 
                   alpha=0.7 - 0.3 * (idx / max_degree),  # 渐变透明度
                   arrowstyle='-|>', 
                   arrowsize=20,
                   connectionstyle='arc3,rad=0.1')  # 轻微弯曲的边

    # 布局算法（带权重和迭代优化）
    pos = nx.spring_layout(G, k=0.6, iterations=200, seed=42, weight='width')

    # 绘制图形
    fig, ax = plt.subplots(figsize=figsize, facecolor='#F0F0F0')
    fig.set_facecolor('#F0F0F0')

    # --- 绘制节点（按形状分组）---
    for shape in {'h', 'o'}:  # 六边形和圆形
        nodes = [node for node in G.nodes() if G.nodes[node]['shape'] == shape]
        nx.draw_networkx_nodes(
            G, pos,
            nodelist=nodes,
            node_shape=shape,
            node_size=[G.nodes[node]['size'] for node in nodes],
            node_color=[G.nodes[node]['color'] for node in nodes],
            alpha=[G.nodes[node]['alpha'] for node in nodes],
            edgecolors=[G.nodes[node]['edgecolor'] for node in nodes],
            linewidths=[G.nodes[node]['linewidths'] for node in nodes],
            ax=ax
        )

    # --- 绘制边 ---
    nx.draw_networkx_edges(
        G, pos,
        width=[G.edges[edge]['width'] for edge in G.edges()],
        edge_color=[G.edges[edge]['color'] for edge in G.edges()],
        alpha=[G.edges[edge]['alpha'] for edge in G.edges()],
        arrowstyle=[G.edges[edge]['arrowstyle'] for edge in G.edges()],
        arrowsize=[G.edges[edge]['arrowsize'] for edge in G.edges()],
        connectionstyle=[G.edges[edge].get('connectionstyle', 'arc3,rad=0') for edge in G.edges()],
        ax=ax
    )

    # --- 绘制标签 ---
    label_options = {
        "font_size": font_size,
        "font_family": "SimHei",
        "font_weight": "bold",
        "bbox": dict(facecolor='white', alpha=0, edgecolor='none', boxstyle='round,pad=0.3'),
        "horizontalalignment": "center"
    }
    nx.draw_networkx_labels(G, pos, **label_options)

    # --- 图例 ---
    legend_elements = [
        plt.Line2D([0], [0], marker='h', color='w', label='Compound',
                  markerfacecolor='#FF9E4F', markersize=15, markeredgewidth=1.5),
        plt.Line2D([0], [0], marker='o', color='w', label='Target',
                  markerfacecolor='#6A9F58', markersize=15, markeredgewidth=1.5)
    ]
    ax.legend(
        handles=legend_elements, 
        loc='upper right', 
        frameon=True,
        framealpha=0.9,
        edgecolor='#333333',
        facecolor='white',
        fontsize=12,
        title='Node type',
        title_fontsize=13
    )

    # --- 标题和边框 ---
    ax.set_title("Compound-Target Regulatory Network", 
                fontsize=18, 
                pad=25,
                color='#333333',
                fontweight='bold')
    
    # 背景和边框美化
    ax.set_facecolor('#F0F0F0')
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color('#CCCCCC')
        spine.set_linewidth(2)
    
    # 添加阴影效果
    ax.patch.set_edgecolor('#DDDDDD')
    ax.patch.set_linewidth(2)
    ax.patch.set_alpha(0.8)

    plt.grid(False)
    ax.axis('off')
    plt.tight_layout()

    # --- 保存图片 ---
    base_dir = "files"
    os.makedirs(base_dir, exist_ok=True)
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    save_path = os.path.join(base_dir, f"compound_target_network_{current_time}.png")
    fig.savefig(save_path, dpi=dpi, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()

    # 返回结果信息
    save_info = f"优化后的化合物-靶点网络图已保存到：\n{save_path}\n"
    summary_with_link = str(output_lines) + f"\n\n## 可视化结果\n{save_info}\n"
    return summary_with_link