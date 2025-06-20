

# extract_clean_text_from_pdf(pdf_path, method='pdfminer') 提取并清理PDF中的文本
PDF_TEXT_EXTRACT_TOOL = {
    "type": "function",
    "function": {
        "name": "extract_clean_text_from_pdf",
        "description": "提取并清理PDF/论文/报告中的文本",
        "parameters": {
            "type": "object",
            "properties": {
                "pdf_path": {
                    "type": "string",
                    "description": "PDF文件路径",
                },
                "method": {
                    "type": "string",
                    "description": "提取文本的方法",
                },
            },
            "required": ["pdf_path", "method"],
        },
    },
    "example": '''
    用户问题:请帮我提取并清理PDF中的文本
    你的输出:
    ```json
    {{
        "tools": ["extract_clean_text_from_pdf(pdf_path='path/to/pdf', method='pdfminer')"]
    }}
    '''
}

# 必应搜索:bing_searched_result(query, max_pages=2, max_results=10)
BING_SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "bing_searched_result",
        "description": "使用必应搜索引擎搜索相关信息",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索关键词，必须用中文或者中英文混合，不能用纯英文，关键词控制在6个字以内，例如:智能体论文、大模型量化、量化投资、AI Agents",
                },
                "max_pages": {
                    "type": "integer",
                    "description": "最大搜索页数",
                },
                "max_results": {
                    "type": "integer",
                    "description": "最大搜索结果数",
                },
            },
            "required": ["query", "max_pages", "max_results"],
        },
    },
    "example": '''
    用户问题:请帮我搜索关于AI的最新资讯
    你的输出:
    ```json
    {{
        "tools": ["bing_searched_result(query='AI最新新闻', max_pages=2, max_results=5)"]
    }}
    '''
}

# 论文搜索get_arxiv_papers(keyword, max_results=5, sort_by='relevance')
ARXIV_SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "get_arxiv_papers",
        "description": "搜索arXiv上的论文",
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "搜索关键词，必须是英文，例如:AI, Agents, Reinforcement Learning, etc.",
                },
                "max_results": {
                    "type": "integer",
                    "description": "最大搜索结果数",
                },
                "sort_by": {
                    "type": "string",
                    "description": "排序方式",
                },
            },
            "required": ["keyword", "max_results", "sort_by"],
        },
    },
    "example": '''
    用户问题:请帮我搜索关于AI的最新论文
    你的输出:
    ```json
    {{
        "tools": ["get_arxiv_papers(keyword='AI', max_results=5, sort_by='relevance')"]
    }}
    '''
}

# chat(question)
CHAT_TOOL = {
    "type": "function",
    "function": {
        "name": "chat",
        "description": "当不需要使用到任何工具，仅仅是根据你的知识即可回答问题的时候调用这个工具",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "用户的问题",
                },
            },
            "required": ["question"],
        },
    },

    "example": '''
    用户问题:四物汤有哪些中药？
    你的输出:chat(question='四物汤有哪些中药？')

    用户问题:四物汤有哪几种中药组成？
    你的输出:chat(question='四物汤有哪几种中药组成？')
    '''
}

# ContentGenerateAgent
CONTENT_GENERATE_AGENT = {
    "description": "当我的问题是属于文案撰写类问题的时候，调用这个工具",
    "name": "ContentGenerateAgent",
    "example": '''
    用户问题:请帮我写一篇关于AI的文章
    你的输出:ContentGenerateAgent('AI')
    '''
}

# DataAnalysisAgent
DATA_ANALYSIS_AGENT = {
    "description": "当我的问题是属于数据分析类问题的时候，调用这个工具",
    "name": "DataAnalysisAgent",
    "example": '''
    用户问题:分析我上传的数据/文件
    你的输出:DataAnalysisAgent(model="glm-4-plus")
    '''
}

# read_file(file_path)
READ_FILE_TOOL = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "当需要读取文件内容的时候调用这个工具",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "文件路径，默认在data目录下",
                },
            },
            "required": ["file_path"],
        },
    },
    "example": '''
    用户问题:分析我的文件的数据，然后进行建模
    你的输出:read_file(file_path='path/to/file')
    '''
}


# get_compound_info(question, model)
GET_COMPOUND_INFO_TOOL = {
    "type": "function",
    "function": {
        "name": "get_compound_info",
        "description": "获取化合物的完整信息，化合物有什么效果等基础信息",
    },
    "example": '''
    用户问题:请帮我查找化合物的信息
    你的输出:get_compound_info()
    '''
}

# get_compound_target_info(question, model)
GET_COMPOUND_TARGET_INFO_TOOL = {
    "type": "function",
    "function": {
        "name": "get_compound_target_info",
        "description": "获取化合物的靶点信息",
    },
    "example": '''
    用户问题:姜黄素有哪些靶？
    你的输出:get_compound_target_info()
    '''
}


# get_molecular_sim()
GET_MOLECULAR_SIM_TOOL = {
    "type": "function",
    "function": {
        "name": "get_molecular_sim",
        "description": "获取两个分子的相似度，不需要输入参数",
    },
    "example": '''
    用户问题:请帮我计算阿司匹林和对乙酰氨基酚的相似度
    你的输出:get_molecular_sim()
    '''
}

# 结合活性search_drug_target_activity(drug_name, target_name)
SEARCH_DRUG_TARGET_ACTIVITY_TOOL = {
    "type": "function",
    "function": {
        "name": "search_drug_target_activity",
        "description": "只有在用户明确提出复方、中药、成分等，与哪些或指定的靶点靶向的问题时才调用。搜索药物与靶点的结合活性。请务必与查询中药化合物或靶点信息的工具做区分。这个工具是分析化合物与靶点的调节/靶向关系。",
        "parameters": {
            "type": "object",
            "properties": {
                "herb_names": {
                    "type": "List",
                    "description": "规范化的中药名称列表，例如 ['矮地茶', '熟地黄']。必须为中文名称。如果是中药方剂，则需输出其包含中药的规范化中文名称",
                },
                "compound_names": {
                    "type": "List",
                    "description": "药物标准命名，请提取所有药物的名称，并翻译为规范化的英文专业名词",
                },
                "target_names": {
                    "type": "List",
                    "description": "基因/蛋白的名称，请提取所有基因/靶点的名称，并翻译为规范化的基因英文缩写名。只能是蛋白或基因的名称。",
                },
            },
            "required": ["herb_names","compound_names", "target_names"],
        },
    },
    "example": '''


    用户问题:请计算黄芩苷、大黄素与BCR-ABL激酶、ACE2、IL1B的结合活性是多少？
    你的输出:search_drug_target_activity(compound_names=["Baicalin", "Emodin"], target_names=["ABL1", "ACE2", "IL1B"])

    用户问题:甘草酸、姜黄素、黄芩甘可以作用于哪些靶点？
    你的输出:search_drug_target_activity(compound_names=["Baicalin", "Emodin"])

    用户问题:四物汤有效成分与IL-6、ACE2、IL1B的靶向调节关系是什么？
    用户问题:四物汤哪些成分可以调节IL-6、ACE2、IL1B靶点？
    用户问题:请分析四物汤有效成分与IL-6、ACE2、IL1B靶点的调节关系。
    你的输出:search_drug_target_activity(herb_names=["当归", "熟地黄", "白芍", "川芎"], target_names=["IL6", "ACE2", "IL1B"])

    '''
}


QUERY_HERB_DATA_TOOL = {
    "type": "function",
    "function": {
        "name": "query_herb_data",
        "description": "仅当用户明确询问中药有哪些成分或靶点时才调用本工具，否则禁止！必须按以下规则处理并输出完整函数调用 query_herb_data(herb_names=[], query_info=[])：",
        "parameters": {
            "type": "object",
            "properties": {
                "herb_names": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "pattern": "^[\u4e00-\u9fa5]+$"
                    },
                    "description": "必须将复方/中成药拆解为标准药材名称。例如：'参松养心胶囊'需拆解为['人参'、'麦冬'、'山茱萸'、'丹参'、'酸枣仁'、'桑寄生'、'赤芍'、'土鳖虫'、'甘松'、'黄连'、'五味子'、'龙骨']等实际组成药材，禁止直接使用复方名称"
                },
                "query_info": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["query_compounds", "query_targets"]
                    },
                    "description": "需查询的靶点或化合物成分信息"
                }
            },
            "required": ["herb_names", "query_info"]
        }
    },
    "examples": [
        {
            "用户输入": "复方风湿骨痛胶囊的作用靶点有哪些？",
            "严格输出": "query_herb_data(herb_names=['川乌', '草乌', '红花', '乳香', '没药'], query_info=['query_targets'])",
            "说明": "中成药名称必须拆解为实际药材"
        },
        {
            "用户输入": "六味地黄丸的成分是什么？",
            "严格输出": "query_herb_data(herb_names=['熟地黄', '山茱萸', '山药', '泽泻', '牡丹皮', '茯苓'], query_info=['query_compounds'])"
        },
        {
            "用户输入": "丹参和川芎的靶点",
            "严格输出": "query_herb_data(herb_names=['丹参', '川芎'], query_info=['query_targets'])"
        }
    ],
    # "error_handling": {
    #     "unknown_formula": "若复方组成未知，返回：query_herb_data(herb_names=[], query_info=[]) 并提示'该复方组成未收录，请人工输入药材列表'"
    # }
}

# query_protein_interactions(proteins, min_score=0.4)
QUERY_PROTEIN_INTERACTIONS_TOOL = {
    "type": "function",
    "function": {
        "name": "query_protein_interactions",
        "description": "查询蛋白质相互作用",
        "parameters": {
            "type": "object",
            "properties": {
                "gene_names": {
                    "type": "list",
                    "description": "用户输入的一组靶点/蛋白/基因名称，请现将其进行基因名称规范化，然后输出为一个列表",
                },
                "min_score": {
                    "type": "float",
                    "description": "最小相似度分数",
                },
            },
            "required": ["gene_names"],
        },
    },
    "example": '''
    用户问题:请分析如下靶点的互作关系： vascular endothelial growth factor, PTEN, KRAS, CDKN2A, 
    你的输出:query_protein_interactions(gene_names= "VEGFA", "PTEN", "KRAS", "CDKN2A")

    用户问题:请分析如下基因的互作关系，互作关系大于0.4才纳入： VEGFA, PTEN, KRAS, cyclin dependent kinase inhibitor 2A‌‌, 
    你的输出:query_protein_interactions(gene_names= ["VEGFA", "PTEN", "KRAS", "CDKN2A"], min_score=0.4)

    '''
}



# analyze_pathway_enrich(genes, disease_names)
PATHWAY_ENRICH_TOOL = {
    "type": "function",
    "function": {
        "name": "analyze_pathway_enrich",
        "description": "执行基因富集分析，输入基因列表和目标疾病名称，输出基因列表在目标疾病中的富集得分、相关基因及其统计信息（如调整后的P值和Odds Ratio）。",
        "parameters": {
            "type": "object",
            "properties": {
                "genes": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "输入的基因列表，例如 ['TP53', 'BRCA1', 'EGFR']。"
                },
                "disease_names": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "要查找的疾病名称列表，例如 ['Cancer', 'Heart Disease']。如果提供了中文疾病名，现将其翻译为英文。如果未提供，则返回所有富集结果。"
                }
            },
            "required": ["genes"]
        }
    },
    "example": '''
    用户问题:请帮我分析这些基因在癌症中的富集情况
    你的输出:analyze_pathway_enrich(genes=['TP53', 'BRCA1', 'EGFR'], disease_names=['Cancer'])
    '''
}


HERB_TARGET_ENRICH_TOOL = {
    "type": "function",
    "function": {
        "name": "herb_target_enrichment",
        "description": "根据输入的中药名称列表，提取相应的靶点并去重。如果用户只输入了中药方剂名称，请自动生成该方剂包含中药的标准化名称，并翻译为中文标准化名称。随后执行富集分析。默认要进行疾病分析（DisGeNET）。用户可以追加其他数据库（如GO 或 KEGG）进行分析。返回与富集结果相关的 top10 结果。输出包括富集得分、相关基因及其统计信息（如调整后的P值和Odds Ratio）。如未找到匹配的富集结果，请使用chat回答，回答时请说明富集得分不显著。",
        "parameters": {
            "type": "object",
            "properties": {
                "herb_names": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "输入的中药名称列表，['矮地茶', '熟地黄']。请确保是中文名称。"
                },
                "disease_names": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "要查找的疾病名称列表，例如 ['Cancer', 'Heart Disease']。疾病名称应该为英文。如果未提供，则返回所有富集结果。"
                },
                 "database": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "要使用的数据库名称列表，例如 ['DisGeNET', 'Reactome']。默认使用 DisGeNET 数据库。其他类型数据库，疾病名称应该为英文。如果未提供，则返回所有富集结果。"
                }
            },
            "required": ["herb_names"]
        }
    },
    "example": '''
    用户问题:请帮我分析矮地茶和熟地、芍药在癌症中的疾病富集情况,以及reactome富集情况
    你的输出:herb_target_enrichment(herb_names=['矮地茶', '熟地黄', '白芍'], database = ['DisGeNET', 'reactome'], disease_names=['Cancer'])
    
    用户问题:请帮我分析四物汤在纤维化中的疾病富集情况,以及kegg富集情况
    你的输出:herb_target_enrichment(herb_names=['当归', '熟地黄', '白芍', '川芎'], database = ['DisGeNET', 'KEGG'], disease_names=['Fibrosis'])

    用户问题:请帮我分析大承气汤在纤维化中的靶点富集情况情况
    你的输出:herb_target_enrichment(herb_names=['大黄', '厚朴', '枳实', '芒硝'], database = ['DisGeNET', 'WikiPathway'], disease_names=['Fibrosis'])
    '''

}


TARGET_ENRICH_TOOL = {
    "type": "function",
    "function": {
        "name": "gene_enrichment",
        "description": "根据输入的靶点名称列表（基因或蛋白），先进行名称规范化（如将'Breast Cancer Susceptibility Gene 1'转为'BRCA1'），再执行富集分析。用户可指定数据库（如DisGeNET、KEGG、GO等）和疾病（如Fibrosis）。返回Top10富集结果，包括得分、基因列表及统计量（调整P值、Odds Ratio）。若无显著结果，需用chat说明。",
        "parameters": {
            "type": "object",
            "properties": {
                "gene_names": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "输入的靶点名称列表（支持别名，如'TP53'或'p53'），需规范化后分析。示例：['TP53', 'BRCA1']。"
                },
                "disease_names": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "目标疾病名称列表（英文），如['Fibrosis', 'Cancer']。若未提供，返回全部富集结果。"
                },
                "database": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "富集数据库列表，默认['DisGeNET']。可选：['KEGG', 'GO', 'Reactome']。"
                }
            },
            "required": ["gene_names"]
        }
    },
    "example": '''
    用户问题: 对下列靶点进行疾病、KEGG富集分析，观察与纤维化关联: "TP53", "Breast Cancer Susceptibility Gene 1", "EGFR", "MYC", "AKT1"。
    你的输出: gene_enrichment(gene_names=["TP53", "BRCA1", "EGFR", "MYC", "AKT1"], database=["DisGeNET", "KEGG"], disease_names=["Fibrosis"])

    用户问题: 分析靶点 "p53", "CDK2", "TNF-alpha" 的Reactome富集。
    你的输出: gene_enrichment(gene_names=["TP53", "CDK2", "TNF"], database=["Reactome"])
    '''
}



HERB_NORMALIZER_TOOL = {
    "type": "function",
    "function": {
        "name": "herb_name_normalizer",
        "description": "将用户输入的中药名称列表（可能是别名、简称或非标准名称）转换为标准名称。",
        "parameters": {
            "type": "object",
            "properties": {
                "herb_names": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "输入的中药名称列表，例如 ['枸杞', '生地']。"
                }
            },
            "required": ["normalized_herb_name"]
        }
    },
    "example": '''
    用户问题:请将枸杞和生地转换为标准名称
    你的输出:herb_name_normalizer(normalized_herb_name=['枸杞子', '生地黄'])

    '''
}



