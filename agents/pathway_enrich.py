import pandas as pd
import gseapy as gp
import re
from typing import List, Dict
import os

class GSEAPyDatabaseMap:
    def __init__(self):
        # 获取 gseapy 支持的所有数据库名称
        self.all_databases = gp.get_library_name()
        # 动态生成数据库名称的映射（用户输入 -> gseapy 数据库名称）
        self.database_mapping = self._generate_database_mapping()
        # 动态生成正则表达式，匹配数据库名称中的核心关键词
        self.pattern = re.compile(
            r'(kegg|KEGG|KEGG通路|go|GO|GO富集分析|gene ontology|reactome|Reactome|Reactome通路|wikipathways|WikiPathways|msigdb|MSigDB|disgenet|DisGeNET)',
            re.IGNORECASE
        )

    def _generate_database_mapping(self) -> Dict[str, str]:
        """
        动态生成数据库名称的映射。
        根据 gseapy 支持的数据库列表，生成用户输入可能匹配的数据库名称。
        """
        mapping = {}
        for db in self.all_databases:
            # 提取数据库类别（去除年份和版本信息）
            db_category = re.sub(r"(_\d{4}|_\d{4}_.+)$", "", db)
            # 将数据库类别转换为小写，作为用户输入的匹配键
            key = db_category.lower()
            # 如果 key 已经存在，则跳过（避免覆盖更具体的映射）
            if key not in mapping:
                mapping[key] = db
        # 添加一些常见的别名映射
        mapping.update({
            "kegg": "KEGG_2019_Human",  # 使用 gseapy 支持的 KEGG 数据库
            "go": "GO_Biological_Process_2021",  # 使用 gseapy 支持的 GO 数据库
            "reactome": "Reactome_2016",  # 使用 gseapy 支持的 Reactome 数据库
            "wikipathways": "WikiPathways_2019_Human",  # 使用 gseapy 支持的 WikiPathways 数据库
            "msigdb": "MSigDB_Hallmark_2020",  # 使用 gseapy 支持的 MSigDB Hallmark
            "disgenet": "DisGeNET",  # DisGeNET 没有年份信息
        })
        return mapping

    def _get_latest_database(self, databases: List[str]) -> List[str]:
        """
        从数据库列表中提取每个类别的最新版本。
        """
        latest_db = {}
        for db in databases:
            # 提取数据库类别和年份
            match = re.match(r"([a-zA-Z_]+)_(\d{4})", db)
            if match:
                db_category, year = match.groups()
                # 如果已有该类别，则比较年份
                if db_category in latest_db:
                    existing_db = latest_db[db_category]
                    existing_year = re.search(r"_(\d{4})", existing_db).group(1)
                    if int(year) > int(existing_year):
                        latest_db[db_category] = db
                else:
                    latest_db[db_category] = db
        return list(latest_db.values())

    def extract_database_names(self, user_input: str) -> List[str]:
        """
        从用户输入中提取数据库名称，并返回每个类别的最新版本。
        """
        matched_databases = []
        matches = self.pattern.findall(user_input.lower())
        if matches:
            # 提取所有匹配的关键词
            matched_keywords = set(matches)
            print(f"匹配的关键词: {matched_keywords}")  # 调试信息
            # 遍历数据库，找到名称中包含匹配关键词的数据库
            for db in self.all_databases:
                for keyword in matched_keywords:
                    if keyword in db.lower():
                        matched_databases.append(db)
                        break
        print(f"匹配的数据库: {matched_databases}")  # 调试信息
        # 提取每个类别的最新版本
        return self._get_latest_database(matched_databases)

    def validate_databases(self, databases: List[str]) -> List[str]:
        """
        验证提取的数据库名称是否在 gseapy 的支持列表中。
        """
        valid_databases = []
        for db in databases:
            # 检查数据库名称是否在 gseapy 的支持列表中
            if db in self.all_databases:
                valid_databases.append(db)
            else:
                print(f"警告: 数据库 '{db}' 不在 gseapy 的支持列表中，已忽略。")
        return valid_databases

    def get_databases(self, user_input: str, disease_names: List[str] = None) -> List[str]:
        """
        根据用户输入获取有效的数据库名称列表。
        
        Args:
            user_input: 用户的输入文本。
            disease_names: 要查找的疾病名称列表。
            
        Returns:
            有效的数据库名称列表。
        """
        # 提取数据库名称
        databases = self.extract_database_names(user_input)
        
        # 如果有疾病名称，则确保 DisGeNET 在数据库中
        if disease_names:
            if "DisGeNET" not in databases:
                databases.append("DisGeNET")

        # # 目前，疾病的分析是默认的基础分析，故确保 DisGeNET 在数据库中
        # if "DisGeNET" not in databases:
        #     databases.append("DisGeNET")
        
        # 如果未匹配到任何数据库，则返回默认的 GO_Biological_Process_2023
        if not databases:
            databases.append("GO_Biological_Process_2023")
        
        # 验证数据库名称
        valid_databases = self.validate_databases(databases)
        return valid_databases


# class GeneEnrichmentAnalyzer:
#     """用于基因富集分析的类
    
#     支持多种基因集库和疾病筛选功能。
#     """
    
#     def __init__(self):
#         # 支持的基因集库
#         self.gene_sets = {
#             'DisGeNET': 'DisGeNET',
#             'KEGG': 'KEGG_2021_Human',
#             'GO_Biological_Process': 'GO_Biological_Process_2023',
#             'Reactome': 'Reactome_2022'
#         }
        
#         # 默认参数
#         self.default_params = {
#             'organism': 'human',
#             'cutoff': 0.05,
#             'no_plot': True
#         }

#     def _validate_gene_list(self, genes):
#         """验证基因列表是否有效"""
#         if not genes or not isinstance(genes, list):
#             raise ValueError("基因列表不能为空，且必须是一个列表。")
#         return genes

#     def perform_enrichment_analysis(self, genes, gene_set='DisGeNET', **kwargs):
#         """执行富集分析
        
#         Args:
#             genes: 输入的基因列表。
#             gene_set: 使用的基因集库，默认为 DisGeNET。
#             **kwargs: 其他传递给 gseapy.enrichr 的参数。
            
#         Returns:
#             富集分析结果的 DataFrame。
#         """
#         # 验证基因列表
#         self._validate_gene_list(genes)
        
#         # 检查基因集库是否支持
#         if gene_set not in self.gene_sets:
#             raise ValueError(f"不支持的基因集库: {gene_set}")
        
#         # 合并默认参数和用户参数
#         params = {**self.default_params, **kwargs}
        
#         try:
#             # 执行富集分析
#             enrichment_results = gp.enrichr(
#                 gene_list=genes,
#                 gene_sets=[self.gene_sets[gene_set]],
#                 **params
#             )
#             return enrichment_results.results
#         except Exception as e:
#             print(f"富集分析失败: {e}")
#             return pd.DataFrame()

#     def filter_disease_results(self, enrichment_results, disease_names):
#         """根据疾病名称筛选富集结果
        
#         Args:
#             enrichment_results: 富集分析结果的 DataFrame。
#             disease_names: 要查找的疾病名称列表。
            
#         Returns:
#             包含匹配疾病结果的 DataFrame。
#         """
#         if enrichment_results.empty:
#             return pd.DataFrame()
        
#         # 筛选包含任一疾病名称的结果
#         filtered_results = enrichment_results[
#             enrichment_results['Term'].str.contains('|'.join(disease_names), case=False, na=False)
#         ]
        
#         # 只保留所需的列
#         filtered_results = filtered_results[['Term', 'Adjusted P-value', 'Odds Ratio','Genes']]
        
#         return filtered_results

#     def get_enrichment_summary(self, genes, gene_set='DisGeNET', disease_names=None, **kwargs):
#         """获取富集分析结果的摘要
        
#         Args:
#             genes: 输入的基因列表。
#             gene_set: 使用的基因集库，默认为 DisGeNET。
#             disease_names: 要查找的疾病名称列表。
#             **kwargs: 其他传递给 gseapy.enrichr 的参数。
            
#         Returns:
#             富集分析结果的摘要（DataFrame 或字符串）。
#         """
#         # 执行富集分析
#         enrichment_results = self.perform_enrichment_analysis(genes, gene_set, **kwargs)
#         # print(enrichment_results)
#         # 如果没有疾病名称，返回所有结果
#         if not disease_names:
#             return enrichment_results[['Term', 'Adjusted P-value', 'Odds Ratio','Genes']]
        
#         # 筛选疾病结果
#         filtered_results = self.filter_disease_results(enrichment_results, disease_names)
        
#         if not filtered_results.empty:
#             return filtered_results
#         else:
#             return "未找到匹配的疾病结果。"

import pandas as pd
import gseapy as gp

class GeneEnrichmentAnalyzer:
    """用于基因富集分析的类
    
    支持多种基因集库和疾病筛选功能。
    """
    
    def __init__(self):
        # 默认参数
        self.default_params = {
            'organism': 'human',
            'cutoff': 0.05,
            'no_plot': True
        }
        self.database_map = GSEAPyDatabaseMap()
        

    def _validate_gene_list(self, genes):
        """验证基因列表是否有效"""
        if not genes or not isinstance(genes, list):
            raise ValueError("基因列表不能为空，且必须是一个列表。")
        return genes

    def perform_enrichment_analysis(self, gene_names, gene_sets=None):
        """执行富集分析
        
        Args:
            genes: 输入的基因列表。
            gene_sets: 使用的基因集库列表，默认为 ['DisGeNET']。
            **kwargs: 其他传递给 gseapy.enrichr 的参数。
            
        Returns:
            富集分析结果的字典，键为数据库名称，值为对应的 DataFrame。
        """
        # 验证基因列表
        self._validate_gene_list(gene_names)
        
        # 如果未指定 gene_sets，则默认使用 DisGeNET/GO_Biological_Process_2025
        if gene_sets is None:
            gene_sets = ['DisGeNET', 'GO_Biological_Process_2025']
        
        # 合并默认参数和用户参数
        params = {**self.default_params}
        
        # 存储所有数据库的富集分析结果
        enrichment_results = {}
        
        try:
            for gene_set in gene_sets:
                # 执行富集分析
                results = gp.enrichr(
                    gene_list=gene_names,
                    gene_sets=[gene_set],  # 直接使用用户传入的数据库名称
                    **params
                )
                # 将结果存储到字典中
                enrichment_results[gene_set] = results.results
        except Exception as e:
            print(f"富集分析失败: {e}")
            return {}
        
        return enrichment_results

    def filter_disease_results(self, enrichment_results, disease_names):
        """根据疾病名称筛选富集结果
        
        Args:
            enrichment_results: 富集分析结果的 DataFrame。
            disease_names: 要查找的疾病名称列表。
            
        Returns:
            包含匹配疾病结果的 DataFrame。
        """
        if enrichment_results.empty:
            return pd.DataFrame()
        
        # 筛选包含任一疾病名称的结果
        filtered_results = enrichment_results[
            enrichment_results['Term'].str.contains('|'.join(disease_names), case=False, na=False)
        ]
        
        # 只保留所需的列
        filtered_results = filtered_results[['Term', 'Adjusted P-value', 'Odds Ratio', 'Genes']]
        
        return filtered_results

    # def get_enrichment_summary(self, genes, gene_sets=None, disease_names=None, **kwargs):
    #     """获取富集分析结果的摘要
        
    #     Args:
    #         genes: 输入的基因列表。
    #         gene_sets: 使用的基因集库列表，默认为 ['DisGeNET']。
    #         disease_names: 要查找的疾病名称列表。
    #         **kwargs: 其他传递给 gseapy.enrichr 的参数。
            
    #     Returns:
    #         富集分析结果的摘要（字典，键为数据库名称，值为对应的 DataFrame 或字符串）。
    #     """
    #     # 执行富集分析
    #     enrichment_results = self.perform_enrichment_analysis(genes, gene_sets, **kwargs)
        
    #     # 存储每个数据库的摘要结果
    #     summary = {}
    #     print('disease_name',disease_names)
    #     for gene_set, results in enrichment_results.items():
    #         # 如果 gene_set 是 DisGeNET 且有疾病名称，则进行疾病过滤
    #         if gene_set == 'DisGeNET' and disease_names:
    #             filtered_results = self.filter_disease_results(results, disease_names)
    #             if not filtered_results.empty:
    #                 # 返回前 10 个结果
    #                 summary[gene_set] = filtered_results.head(10)
    #             else:
    #                 summary[gene_set] = f"在数据库 {gene_set} 中未找到匹配的疾病结果。"
    #         else:
    #             # 对于其他数据库，直接返回前 10 个结果
    #             summary[gene_set] = results[['Term', 'Adjusted P-value', 'Odds Ratio', 'Genes']].head(10)
        
    #     return summary


    def execute(self, **kwargs):
        """获取富集分析结果的摘要，并生成 HTML 文件链接
        
        Args:
            genes: 输入的基因列表。
            gene_sets: 使用的基因集库列表，默认为 ['DisGeNET']。
            disease_names: 要查找的疾病名称列表。
            **kwargs: 其他传递给 gseapy.enrichr 的参数。
            
        Returns:
            summary: 富集分析结果的摘要（字典，键为数据库名称，值为对应的 DataFrame 或字符串）。
            html_links: 字典，键为数据库名称，值为对应的 HTML 文件链接。
        """
        
        question = kwargs.get("question", "")
        database_name = self.database_map.get_databases(question)
        # print('-------------------------', database_name)
        disease_names = kwargs.get("disease_names", [])
        gene_names = kwargs.get("gene_names", [])
        # print('kwargs',kwargs)
        # 执行富集分析
        enrichment_results = self.perform_enrichment_analysis(gene_names, database_name)
        
        # 存储每个数据库的摘要结果
        summary = {}
        for gene_set, results in enrichment_results.items():
            # 如果 gene_set 是 DisGeNET 且有疾病名称，则进行疾病过滤
            if gene_set == 'DisGeNET' and disease_names:
                filtered_results = self.filter_disease_results(results, disease_names)
                if not filtered_results.empty:
                    # 返回前 10 个结果
                    summary[gene_set] = filtered_results.head(10)
                else:
                    summary[gene_set] = f"在数据库 {gene_set} 中未找到匹配的疾病结果。"
            else:
                # 对于其他数据库，直接返回前 10 个结果
                summary[gene_set] = results[['Term', 'Adjusted P-value', 'Odds Ratio', 'Genes']].head(20)
        
        return summary, enrichment_results


# 使用示例
def analyze_pathway_enrich(genes, disease_names=None):
    # 创建分析器实例
    analyzer = GeneEnrichmentAnalyzer()
    
    # 获取富集分析结果
    results = analyzer.get_enrichment_summary(genes, disease_names=disease_names)
    
    # 输出结果
    if isinstance(results, pd.DataFrame):
        print("富集分析结果:")
        print(results)
    else:
        print(results)

def save_dict_to_excel(enrichment_results: dict, file_path: str):
    """
    将包含多个DataFrame的字典保存到一个Excel文件的不同sheet中。
    
    参数：
    enrichment_results (dict): key是sheet名，value是对应的DataFrame。
    file_path (str): 要保存的Excel文件路径，例如 'output.xlsx'
    """
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        for sheet_name, df in enrichment_results.items():
            # 避免sheet名超过Excel限制（31个字符）和包含非法字符
            safe_sheet_name = str(sheet_name)[:31].replace('/', '_').replace('\\', '_')
            df.to_excel(writer, sheet_name=safe_sheet_name, index=False)
    print(f"保存成功：{file_path}")
    
if __name__ == "__main__":

    gpmap = GSEAPyDatabaseMap()
    user_input = "请评估复元活血汤（柴胡半两、瓜蒌根、当归各、红花、甘草、大黄、桃仁）在纤维化中的作用，以及在kegg和GO、Reactome的通路富集情况"
    databases = gpmap.get_databases(user_input)
    print("提取的数据库名称:", databases)

    # 示例基因列表
    genes = [
        "TP53", "BRCA1", "EGFR", "MYC", "AKT1", 
        "VEGFA", "PTEN", "KRAS", "CDKN2A", "IL6", 
        "TNF", "MAPK1", "STAT3", "JUN", "FOS", 
        "HIF1A", "NFKB1", "PIK3CA", "RB1", "CCND1"
    ]

    # 定义要查找的疾病名称列表
    disease_names = ['Sclerosis', 'Cancer', 'Heart']

    agent2 = GeneEnrichmentAnalyzer()
    kwargs = {"question": user_input, "disease_names": disease_names, "gene_names": genes}
    # 执行分析
    summary = agent2.execute(**kwargs)
    print(summary)