import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))  # 添加项目根目录到PATH
import requests

import pandas as pd
import logging
from pubchempy import get_compounds


from tools.plot_tools import plot_compound_target_activity
import pandas as pd

import pandas as pd
# from pubchempy import get_compounds

def search_drug_target_activity(compound_names=None, target_names=None):
    """
    根据化合物名称和/或靶点名称查询药物-靶标关系
    
    参数:
        compound_names: 要查询的化合物名称列表(可选)
        target_names: 要查询的靶点名称列表(可选)
    
    返回:
        包含查询结果的DataFrame，如果没有查询条件则返回提示信息，
        如果没有结果则返回未查询到信息提示
    """

    data_file = "data/drug_target_data.xlsx"
    
    # # 检查是否提供了任何查询条件
    # if (compound_names is None or len(compound_names) == 0) and \
    #     (target_names is None or len(target_names) == 0):
    #     return "请输入要查询的药物或靶点信息"
    
    # 获取化合物CID列表
    pubchem_cids = []
    if compound_names is not None and len(compound_names) > 0:
        for name in compound_names:
            compounds = get_compounds(name, 'name')
            if compounds:
                pubchem_cids.append(str(compounds[0].cid))  # 转换为字符串
    
    # 读取数据文件
    df = pd.read_excel(data_file)
    
    # 确保列名正确
    df.columns = ['PubChemCID', 'DrugName', 'GeneName']
    df['PubChemCID'] = df['PubChemCID'].astype(str)  # 确保CID是字符串类型
    
    # 初始化查询条件
    conditions = []
    
    # 如果提供了PubChemCID列表，添加查询条件
    if pubchem_cids and len(pubchem_cids) > 0:
        conditions.append(df['PubChemCID'].isin(pubchem_cids))
    
    # 如果提供了GeneName列表，添加查询条件
    if target_names is not None and len(target_names) > 0:
        conditions.append(df['GeneName'].isin(target_names))
    
    # 应用查询条件
    if conditions:
        # 组合所有条件(AND逻辑)
        combined_condition = pd.Series(True, index=df.index)
        for cond in conditions:
            combined_condition &= cond
        
        result = df[combined_condition]
    else:
        result = pd.DataFrame()  # 返回空DataFrame
    
    # 重置索引并返回结果
    result_df = result.reset_index(drop=True)[['DrugName', 'GeneName']]
    print(result_df)

    return result_df


# 要从PubChem的XML响应中提取CID号，可以使用以下Python代码：

import requests
from xml.etree import ElementTree as ET

def get_cid_from_pubchem(compound_name: str) -> str:
    """
    从PubChem获取化合物的CID号
    
    Args:
        compound_name: 化合物名称
        
    Returns:
        化合物的CID号字符串，如果查询失败返回None
    """
    base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name"
    url = f"{base_url}/{compound_name}/synonyms/XML"
    
    try:
        # 发送请求
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功
        
        # 解析XML
        root = ET.fromstring(response.content)
        
        # 查找CID节点 - 注意XML命名空间
        ns = {'pug': 'http://pubchem.ncbi.nlm.nih.gov/pug_rest'}
        cid_element = root.find('.//pug:CID', ns)
        
        if cid_element is not None:
            return cid_element.text
        else:
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"请求PubChem失败: {e}")
        return None
    except ET.ParseError as e:
        print(f"解析XML失败: {e}")
        return None



def df_to_dict_and_print(df):
    """
    将DataFrame转换为字典并输出格式化字符串
    
    参数:
    df -- pandas DataFrame, 必须包含'DrugName'和'GeneName'列
    
    返回:
    字典, 格式为 {drug_name: [gene1, gene2, ...]}
    """
    # 使用groupby按DrugName分组，然后将每个组的GeneName转换为列表
    result_dict = df.groupby('DrugName')['GeneName'].apply(list).to_dict()
    
    # 生成格式化输出
    output_lines = []
    for drug, genes in result_dict.items():
        genes_str = "、".join(genes)  # 用顿号连接基因名
        output_lines.append(f"查询到{drug}化合物靶向{genes_str}靶点")
    
    # 打印结果
    # print("\n".join(output_lines))
    
    return output_lines


from typing import List, Dict, Any

def convert_drug_target_to_json(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    将药物-靶点DataFrame转换为指定的JSON格式
    
    Args:
        df: 包含药物-靶点关系的DataFrame，需要包含'DrugName'和'GeneName'两列
        
    Returns:
        转换后的JSON格式列表，每个元素是一个字典，结构为：
        [
            {'compound': '药物名', 'target': '靶点基因', 'relation': 'compound_target'},
            ...
        ]
    """
    # 检查输入DataFrame是否符合要求
    if not isinstance(df, pd.DataFrame) or not {'DrugName', 'GeneName'}.issubset(df.columns):
        raise ValueError("输入必须包含'DrugName'和'GeneName'列的DataFrame")
    
    # 去除可能的重复行
    df = df.drop_duplicates(subset=['DrugName', 'GeneName'])
    
    # 转换为指定JSON格式
    return [
        {
            'compound': row['DrugName'],
            'target': row['GeneName'],
            'relation': 'compound_target'
        }
        for _, row in df.iterrows()
    ]



# def search_drug_target_activity(drug_names, target_names, max_drugs=5, max_targets=10):
#     """
#     查询多个药物与多个靶点的活性数据
    
#     参数:
#         drug_names: 药物名称列表
#         target_names: 靶点名称列表
#         max_drugs: 一次分析的最大药物数量(默认5)
#         max_targets: 一次分析的最大靶点数量(默认10)
    
#     返回:
#         result_str: 结果摘要字符串
#         df: 包含所有活性数据的DataFrame
#     """
#     # 检查输入限制

    
#     # 初始化客户端
#     molecule = new_client.molecule
#     target = new_client.target
#     activity = new_client.activity
    
#     # 1. 查找所有药物的CHEMBL ID
#     drug_chembl_ids = []
#     for drug_name in drug_names:
#         try:
#             drug_query = molecule.filter(pref_name__icontains=drug_name)
#             drug_chembl_ids.extend([mol['molecule_chembl_id'] for mol in drug_query])
#         except Exception as e:
#             print(f"查询药物{drug_name}时出错: {str(e)}")
#             continue
    
#     # 去重
#     drug_chembl_ids = list(set(drug_chembl_ids))
#     if not drug_chembl_ids:
#         return "未找到任何药物的CHEMBL ID", pd.DataFrame()
    
#     # 2. 查找所有靶点的CHEMBL ID
#     target_chembl_ids = []
#     for gene_name in target_names:
#         try:
#             target_query = target.filter(pref_name__icontains=gene_name)
#             target_chembl_ids.extend([t['target_chembl_id'] for t in target_query])
#         except Exception as e:
#             print(f"查询靶点{gene_name}时出错: {str(e)}")
#             continue
    
#     # 去重
#     target_chembl_ids = list(set(target_chembl_ids))
#     if not target_chembl_ids:
#         return "未找到任何靶点的CHEMBL ID", pd.DataFrame()
    
#     # 3. 查询活性数据
#     try:
#         activities = activity.filter(
#             molecule_chembl_id__in=drug_chembl_ids,
#             target_chembl_id__in=target_chembl_ids,
#             standard_type__in=['IC50', 'Ki', 'Kd', 'EC50', 'Potency']
#         ).only([
#             'molecule_chembl_id',
#             'target_chembl_id',
#             'standard_type',
#             'standard_value',
#             'standard_units',
#             'assay_description',
#             'molecule_pref_name',
#             'target_pref_name'
#         ])
        
#         # 转换为DataFrame以便分析
#         df = pd.DataFrame(list(activities))
#     except Exception as e:
#         return f"查询活性数据时出错: {str(e)}", pd.DataFrame()
    
#     if df.empty:
#         drug_list = ", ".join(drug_names)
#         gene_list = ", ".join(target_names)
#         return f"未找到{drug_list}与{gene_list}的直接结合活性数据", pd.DataFrame()
    
#     # 数据处理和分析
#     activity_summary = {}
#     for drug in df['molecule_pref_name'].unique():
#         for target in df['target_pref_name'].unique():
#             for activity_type in df['standard_type'].unique():
#                 df_filtered = df[
#                     (df['molecule_pref_name'] == drug) & 
#                     (df['target_pref_name'] == target) & 
#                     (df['standard_type'] == activity_type)
#                 ]
#                 df_filtered['standard_value'] = pd.to_numeric(df_filtered['standard_value'], errors='coerce')
#                 if not df_filtered.empty:
#                     key = f"{drug} - {target} - {activity_type}"
#                     mean_activity = df_filtered['standard_value'].mean()
#                     activity_summary[key] = {
#                         'mean_value': mean_activity,
#                         'units': df_filtered['standard_units'].iloc[0],
#                         'count': len(df_filtered)
#                     }
    
#     # 构建结果字符串
#     result_str = f"\n药物与靶点的活性数据总结(共{len(activity_summary)}组有效数据):\n"
#     for key, stats in activity_summary.items():
#         result_str += f"{key}: {stats['mean_value']} {stats['units']} (基于{stats['count']}个测量)\n"
        
#     return result_str, df

if __name__ == "__main__":

    cid = get_cid_from_pubchem("Glycyrrhizin")
    print(f"CID: {cid}")  # 输出: CID: 14982

    # 示例用法
    # drug_names = ["Glycyrrhizin", "Curcumin", "Baicalin"]
    # gene_names = ["IL-6", "IL1B"]
    # result, df = search_drug_target_activity(drug_names, gene_names)
    # print(result)
    # print(df.head())

    # # 示例1: 没有提供查询条件
    # print("示例1: 没有提供查询条件")
    # result1 = search_drug_target_activity()
    # print(result1)  # 输出: "请输入要查询的药物或靶点信息"
    
    # # 示例2: 查询存在的记录
    # print("\n示例2: 查询Glycyrrhizic acid、Curcumin、Baicalin记录")
    # result2, output_lines = search_drug_target_activity(compound_names=['Glycyrrhizic acid', 'Curcumin', 'Baicalin'])
    # print(result2)
    # plot_compound_target_activity(result2, output_lines )

    
    # # 示例3: 查询不存在的记录
    # print("\n示例3: 查询PubChemCID为99999999的记录")
    # result3, output_lines= search_drug_target_activity(compound_names=['Glycyrrhizic acid', 'Curcumin', 'Baicalin'], target_names=['MMP9', 'IL6', 'IL1B'] )
    # print(result3)  # 输出: "未查询到任何药物靶点作用信息"
    
    # # 示例4: 查询不存在的GeneName
    # print("\n示例4: 查询GeneName为'NOT_EXIST'的记录")
    # result4 = search_drug_target_activity(target_names=['NOT_EXIST'])
    # print(result4)  # 输出: "未查询到任何药物靶点作用信息"
