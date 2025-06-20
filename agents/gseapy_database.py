import re
import gseapy as gp
from typing import List, Dict

class GSEAPyDatabaseAgent:
    def __init__(self):
        # 获取 gseapy 支持的所有数据库名称
        self.all_databases = gp.get_library_name()
        # 动态生成数据库名称的映射（用户输入 -> gseapy 数据库名称）
        self.database_mapping = self._generate_database_mapping()

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
            "kegg": "KEGG_2021_Human",  # 使用 gseapy 支持的 KEGG 数据库
            "go": "GO_Biological_Process_2023",  # 使用 gseapy 支持的 GO 数据库
            "reactome": "Reactome_2022",  # 使用 gseapy 支持的 Reactome 数据库
            "wikipathways": "WikiPathways_2024_Human",  # 使用 gseapy 支持的 WikiPathways 数据库
            "msigdb": "MSigDB_Hallmark_2020",  # 使用 gseapy 支持的 MSigDB Hallmark
            "disgenet": "DisGeNET",  # DisGeNET 没有年份信息
        })
        return mapping

    def get_latest_database(self, databases: List[str]) -> Dict[str, str]:
        """
        从数据库列表中提取年份最近的数据库。
        返回一个字典，键为数据库类别（如 KEGG），值为最新的数据库名称。
        """
        latest_db = {}
        for db in databases:
            # 提取数据库类别和年份
            match = re.match(r"([a-zA-Z_]+)(?:_(\d{4}))?", db)
            if match:
                db_category, year = match.groups()
                # 如果没有年份，则直接使用数据库名称
                if not year:
                    latest_db[db_category] = db
                else:
                    # 如果已有该类别，则比较年份
                    if db_category in latest_db:
                        existing_db = latest_db[db_category]
                        existing_year = re.search(r"_(\d{4})", existing_db).group(1)
                        if int(year) > int(existing_year):
                            latest_db[db_category] = db
                    else:
                        latest_db[db_category] = db
        return latest_db

    def extract_database_names(self, user_input: str) -> List[str]:
        """
        从用户输入中提取数据库名称。
        """
        # 将用户输入转换为小写，方便匹配
        user_input = user_input.lower()
        # 使用正则表达式匹配数据库名称
        matched_databases = []
        for key in self.database_mapping:
            if re.search(r'\b' + re.escape(key) + r'\b', user_input):
                matched_databases.append(self.database_mapping[key])
        # 如果未匹配到任何数据库，则返回默认的 DisGeNET
        if not matched_databases:
            matched_databases.append("DisGeNET")
        return matched_databases

    def validate_databases(self, databases: List[str]) -> List[str]:
        """
        验证提取的数据库名称是否在 gseapy 的支持列表中。
        """
        valid_databases = []
        for db in databases:
            if db in self.all_databases:
                valid_databases.append(db)
            else:
                print(f"警告: 数据库 '{db}' 不在 gseapy 的支持列表中，已忽略。")
        return valid_databases

    def get_databases(self, user_input: str) -> List[str]:
        """
        根据用户输入获取有效的数据库名称列表。
        """
        # 提取数据库名称
        databases = self.extract_database_names(user_input)
        # 验证数据库名称
        valid_databases = self.validate_databases(databases)
        return valid_databases
    
# 示例调用
if __name__ == "__main__":
    agent = GSEAPyDatabaseAgent()
    user_input = "请帮我分析矮地茶和熟地黄在癌症中的疾病富集情况，并使用 KEGG 和 GO 数据库。"
    databases = agent.get_databases(user_input)
    print("提取的数据库名称:", databases)