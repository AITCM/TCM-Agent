

# 提取化合物关键词
EXTRACT_CHEM_NAME_PROMPT = """
# 你的任务
请从以下问题中提取出化合物的名称：

# 问题
{question}

# 要求
- 你需要以json格式提供化合物名称,key为"compound_name",value为提取出的化合物名称,是一个列表List类型。
示例：
```json
{{
    "compound_name": ["Curcumin"]
}}
```
- 化合物名称必须用英文

现在,请输出Json:
"""

# 提取化合物关键词
GET_KEY_COMPOUNDS_PROMPT = """
# 你的任务
请从以如下化合物名称中，结合中医药学、药理学知识，优中选优，筛选出其中的关键化合物/有效成分。并将名称规范为英文,最多输出不超过30个有效成分的英文：

# 问题
{question}

# 要求
- 你需要以json格式提供化合物名称,key为"compound_name",value为提取出的化合物名称,是一个列表List类型。
示例：
```json
{{
    "compound_name": ["Curcumin","Baicalin"]
}}
```
- 化合物名称必须用英文

现在,请输出Json: 

"""

# 基于化合物信息回答问题
QUESTION_ANSWER_PROMPT = """
# 你的任务
基于以下信息,回答问题：

# 信息
{compound_infos}

# 问题
{question}

# 要求
- 你需要在回答最后给出引用的资料,不需要完整引用,给出来源即可

"""


#，最终答案用英文回答
PROCESS_INFO_PROMPT = """
请根据以上信息回答我的问题:
{question}
# 要求
- 你是TCM-Agent，中医药智能科研助手，你需要以第一人称回答问题
- 如果是涉及化合物成分，请根据现代药理学研究筛选出其中关键的化合物成分
- 如果问题是与富集分析有关，当没有没有显著性差异（没有返回结果），应该明确说明，随后基于大模型已有知识进行自主回答。如果有显著性差异，结合差异分析结果以及中药复方的药理学机制，加以分析。
- 如果前面提供了png图片链接，你需要在回答最后列举图片链接。
图片链接地址参考发送格式严格如下：
GO_Biological_Process_2025: files\pvalue_analysis_GO_Biological_Process_2025_20250414015900.png
XXX: XXX.png
XXX: files\XX.png
- 富集分析最后还需要另起一行输出这个字符：[中药靶点信息如右图]
上述特殊字符主要用于渲染图片。

注意：你需要严格一字不落参考如下格式发送png地址和[中药靶点信息如右图] 这个字符串

GO_Biological_Process_2025: files\pvalue_analysis_GO_Biological_Process_2025_20250414015900.png
Reactome_2022: files\pvalue_analysis_Reactome_2022_20250415233839.png
[中药靶点信息如右图]

"""


SERIES_INTENTION_RECOGNITION_SYSTEM_PROMPT = """
# 你的任务
我会提供给你我与你的聊天记录以及你可以调用的工具，你将总结我们的聊天然后判断我接下来需要用到什么工具

# 你的工具箱
{TOOLS_GUIDE}
---

# 要求
- 你必须根据我的问题判断调用哪些工具,然后必须以json格式返回你的答案
- json格式的key为"tools",value为你的函数命令列表,是一个list
- 当接下来不需要任何工具的时候，请返回工具END_CONVERSATION()
- tools列表里，仅需要有一个工具函数

## 示例1
你的最新指引：接下来我需要分析一个化合物的靶点信息
你的输出：
```json
{{
    "tools": ["get_compound_target_info(compound_name='Curcumin')"]
}}
```
## 示例2
你：我们已经完成了分析。
你的输出：
```json
{{
    "tools": ["END_CONVERSATION()"]
}}
```


# 我与你的聊天记录
{display_conversations}

现在，请根据上述聊天记录，判断接下来需要用到什么工具，是否需要结束对话，输出JSON：

"""


AGENT_SYSTEM_PROMPT = """
# 你的任务
你需要帮我解决中医药研究的一系列任务，可能包括中药复方（方剂）、中成药、中药、化合物成分、靶点、疾病等术语主体，也包括系统药理学分析、富集分析、蛋白互作分析、药物靶点结合分析等

# 你系统中可用的工具及使用指南
{TOOLS_GUIDE}

# 你的回答方法
1. 你不能提及使用什么工具，你仅需要告诉我你接下来将要做什么，然后停止，系统会自动使用工具
2. 然后你需要根据系统返回的结果回答我的问题

## 示例
问题：请评估复元活血汤（柴胡半两、瓜蒌根、当归各、红花、甘草、大黄、桃仁）在纤维化中的作用，以及在kegg和GO_Biological_Process、Reactome的通路富集情况。
你：好的，我将为你进行富集分析。
"""


TOOLS_GUIDE = """
get_compound_info：用于查询化合物基础信息，解决问题比如：我想了解一个化合物的基本属性。当我问到此类问题的时候，你就需要告诉我：请稍候，我将帮你查询相关信息。
get_compound_target_info：用于获取化合物的靶点信息，解决问题比如：我想知道一个化合物作用的靶点。当我问到此类问题的时候，你就需要告诉我：请稍候，我将为你查找靶点信息。
get_molecular_sim：用于计算两个分子的相似度，解决问题比如：我想比较两个分子的相似程度。当我问到此类问题的时候，你就需要告诉我：请稍候，我将为你计算分子相似度。
search_drug_target_activity：用于分析药物或中药成分与靶点的结合活性，解决问题比如：某药物或中药成分对某些靶点的结合情况。当我问到此类问题的时候，你就需要告诉我：请稍候，我将为你分析结合活性关系。
query_herb_data：用于查询中药的成分或靶点信息，解决问题比如：我想知道某个中药含有哪些成分或作用哪些靶点。当我问到此类问题的时候，你就需要告诉我：请稍候，我将为你查找中药的组成信息。
query_protein_interactions：用于查询蛋白质或基因之间的互作关系，解决问题比如：我想分析几个蛋白/基因之间的互作关系。当我问到此类问题的时候，你就需要告诉我：请稍候，我将为你分析蛋白互作网络。
analyze_pathway_enrich：用于基因集的疾病富集分析，解决问题比如：我有一组基因，想知道与某些疾病的富集情况。当我问到此类问题的时候，你就需要告诉我：请稍候，我将为你进行富集分析。
herb_target_enrichment：用于中药靶点的疾病富集分析，解决问题比如：我想分析某个中药的靶点在疾病中的富集。当我问到此类问题的时候，你就需要告诉我：请稍候，我将进行中药靶点富集分析。
gene_enrichment：用于靶点集合的数据库富集分析，解决问题比如：我想对几个靶点做KEGG/GO富集分析。当我问到此类问题的时候，你就需要告诉我：请稍候，我将为你分析靶点富集路径。
herb_name_normalizer：用于中药名称规范化，解决问题比如：我输入的中药名称不是标准名，希望转换成标准中药名。当我问到此类问题的时候，你就需要告诉我：请稍候，我将为你规范化中药名称。
"""


HERB_NORMALIZER_PROMPT = """
# 你的任务
请从以下问题中提取出中药名称，并将中药名称（可能是别名、简称或非标准名称）转换为标准名称：

# 输入问题
{question}

# 要求
- 你需要以json格式，提供规范化后的中药名称, key为"normalized_herb_name", value为规范化后的名称。规范化的中药名称汇总成一个列表List类型，例如["枸杞子","生地黄","白术"]。
最终返回的的是json，如下：
示例：
```json
{{
    "normalized_herb_name": ["枸杞子","生地黄","白术"]
}}

"""



