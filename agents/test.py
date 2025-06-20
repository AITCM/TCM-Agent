import re

# 假设这是通过 gseapy.get_library_name() 获取的数据库列表
databases = {
    "kegg": "KEGG_2019_Human",
    "go": "GO_Biological_Process_2021",
    "reactome": "Reactome_2016",
    "wikipathways": "WikiPathways_2019_Human",
    "msigdb": "MSigDB_Hallmark_2020",
    "disgenet": "DisGeNET",
}

# 动态生成正则表达式，匹配数据库名称中的核心关键词
pattern = re.compile(
    '|'.join(re.escape(re.sub(r'_\d{4}.*', '', db_name.lower())) for db_name in databases.values()),
    re.IGNORECASE
)

def select_database(input_text):
    """
    根据输入文本选择对应的数据库
    :param input_text: 用户输入的文本
    :return: 匹配到的数据库名称，如果未匹配到则返回 None
    """
    match = pattern.search(input_text)
    if match:
        matched_keyword = match.group(0).lower()  # 提取匹配的关键词
        # 遍历数据库，找到名称中包含匹配关键词的数据库
        for db_name in databases.values():
            if matched_keyword in db_name.lower():
                return db_name
    return None

# 示例输入
input_texts = [
    "请评估复元活血汤在纤维化中的作用，以及在KEGG通路的富集情况",
    "我想做GO富集分析",
    "Reactome数据库中有哪些通路？",
    "MSigDB的分析结果如何？",
    "这个数据可以用WikiPathways分析吗？",
    "DisGeNET的相关信息是什么？",
    "这个文本没有关键词",
]

# 测试
for text in input_texts:
    database = select_database(text)
    if database:
        print(f"输入: '{text}' → 匹配到数据库: {database}")
    else:
        print(f"输入: '{text}' → 未匹配到关键词")