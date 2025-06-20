import requests
from datetime import datetime   

import warnings
warnings.filterwarnings("ignore")
import json
from pathlib import Path
from typing import List, Dict
import os
import numpy as np
import pandas as pd

from tools.llm_api import *
from tools.json_tool import *
from tools.function_call_toolbox import extract_params_to_json, get_func_name
from tools.pubmed_tools import *
from tools.plot_tools import *

from data.compound_info import PubChemAPI

# 获取TTD数据库的数据：药物-靶点关系
from agents.molecular_sim import MolecularSimilarity
from agents.search_target_activity import search_drug_target_activity, df_to_dict_and_print, convert_drug_target_to_json
from agents.protein_interaction import query_protein_interactions, analyze_protein_network
from agents.pathway_enrich import GeneEnrichmentAnalyzer, save_dict_to_excel

import time
import json
from typing import Dict, List, Optional

import os
import pandas as pd

# 获取提示词
from prompts.chem_agent_prompts import (
    EXTRACT_CHEM_NAME_PROMPT,
    GET_KEY_COMPOUNDS_PROMPT,
    SERIES_INTENTION_RECOGNITION_SYSTEM_PROMPT,
    PROCESS_INFO_PROMPT,
    HERB_NORMALIZER_PROMPT
)

# 加载工具配置
from tools_configs import (
    CHAT_TOOL,
    GET_COMPOUND_INFO_TOOL,
    GET_MOLECULAR_SIM_TOOL,
    QUERY_HERB_DATA_TOOL, # 查询中药化合物或把靶点
    SEARCH_DRUG_TARGET_ACTIVITY_TOOL,
    QUERY_PROTEIN_INTERACTIONS_TOOL,
    TARGET_ENRICH_TOOL,  # 靶点直接富集分析
    HERB_TARGET_ENRICH_TOOL, # 导入中药靶点富集分析工具配置
)



# tool:获取化合物信息
class GetCompoundInfo():
    def execute(self, **kwargs):
        question = kwargs.get('question', 'What is the chemical structure of aspirin?')
        compound_names = TCMAgent.get_compound_name(question)
        compound_infos = []
        for compound_name in compound_names:
            cid, search_url = TCMAgent.get_cid_by_name(compound_name)
            api = PubChemAPI()
            # print("\n*Searching...*\n")
            compound_info = api.get_compound_info(cid)
            compound_info.source_url = search_url
            compound_infos.append(compound_info)

        return compound_infos


# 计算相似度
class CalculateSimilarity():
    def execute(self, **kwargs):
        print("Analyzing the similarity between two compounds...")
        question = kwargs.get('question', 'What is the chemical structure of aspirin')
        compound_names = TCMAgent.get_compound_name(question)

        smiles = {}
        for i, compound_name in enumerate(compound_names):
            cid, _ = TCMAgent.get_cid_by_name(compound_name)
            api = PubChemAPI()
            compound_info = api.get_compound_info(cid)
            smiles[f"SMILES_{i+1}"] = compound_info.canonical_smiles

        calculator = MolecularSimilarity()
        results_info = ""
        # 使用默认参数计算相似度
        similarity = calculator.calculate_similarity(smiles["SMILES_1"], smiles["SMILES_2"])
        results_info += f"默认相似度(Morgan指纹, Tanimoto): {similarity:.2%}\n"

        # 计算所有相似度度量方法的结果
        all_similarities = calculator.get_all_similarities(smiles["SMILES_1"], smiles["SMILES_2"])
        results_info += "\n所有相似度度量方法的结果:\n"
        for metric, score in all_similarities.items():
            results_info += f"{metric}: {score:.2%}\n"

        # 比较不同指纹类型的结果
        fp_comparisons = calculator.compare_fp_types(smiles["SMILES_1"], smiles["SMILES_2"])
        results_info += "\n不同指纹类型的结果:\n"
        for fp_type, score in fp_comparisons.items():
            results_info += f"{fp_type}: {score:.2%}\n"

        return results_info


class QueryHerbData():  # TODO 完善
    def __init__(self):
        pass
    
    @staticmethod
    def _load_herb_compounds(herb_names: List[str]) -> List[str]:
        herb_compounds = {}
        unique_compounds = set()

        """加载中药化合物信息"""
        herb_compounds_path = Path(r"data/herb_components.json")
        if not herb_compounds_path.exists():
            raise FileNotFoundError(f"文件 {herb_compounds_path} 不存在")
        with open(herb_compounds_path, "r", encoding="utf-8") as f:
            herb_compounds_database = json.load(f)

        for herb_name in herb_names:
            if herb_name not in herb_compounds_database:
                pass
                # raise ValueError(f"未找到中药 {herb_name} 的化合物成分信息")  # TODO 以后没找到中药化合物信息，搜索在线数据库找
            
            compounds = herb_compounds_database.get(herb_name, [])
            herb_compounds[herb_name] = compounds
            unique_compounds.update([compound['Component name'] for compound in compounds])
            
        print('unique_compounds', list(unique_compounds)[:3])
        return list(unique_compounds)
    
    @staticmethod
    def _load_herb_targets(herb_names: List[str]) -> List[str]:
        herb_targets={}
        unique_targets = set()
        
        """加载中药靶点信息"""
        herb_targets_db_path = Path("data/herb_targets_db.json")
        if not herb_targets_db_path.exists():
            raise FileNotFoundError(f"文件 {herb_targets_db_path} 不存在")
        
        with open(herb_targets_db_path, "r", encoding="utf-8") as f:
            herb_targets_database = json.load(f)

        """根据中药名称列表，获取{中药：靶点}保存为json，以及去重后的靶点列表"""
        
        for herb_name in herb_names:
            if herb_name not in herb_targets_database:
                raise ValueError(f"未找到中药 {herb_name} 的靶点信息")  # TODO 以后没找到中药靶点信息，搜索在线数据库找
            
            targets = herb_targets_database[herb_name]
            herb_targets[herb_name] = targets
            unique_targets.update([target["Target name"] for target in targets])
            # # 生成三元组
            # for target in targets:
            #     self.herb_targets.append({
            #         "herb": herb_name,
            #         "target": target,
            #         "relation": "contains"
            #     })

        # # 将herb_targets写入network_plot.json文件，用于展示网络图
        # with open("client/public/data/network_plot.json", "w", encoding="utf-8") as f:
        #     json.dump(self.herb_targets, f, ensure_ascii=False)

        # # 保存herb_names到json
        # herb_names_path = Path("data/herb_names.json")
        # with open(herb_names_path, "w", encoding="utf-8") as f:
        #     json.dump(herb_names, f, ensure_ascii=False)
        # # print('herb_names', herb_names)
        return list(unique_targets)

    def execute(self, **kwargs):        
        # compound_names = kwargs.get('compound_names', [])
        # target_names = kwargs.get('target_names', [])

        herb_names = kwargs.get("herb_names", [])
        query_info = kwargs.get("query_info", [])

        summary = ''
        if 'query_compounds' in query_info:
            unique_compounds = self._load_herb_compounds(herb_names)
            summary += f'中药化合物包括：{unique_compounds}'
        if 'query_targets' in query_info:
            unique_targets = self._load_herb_targets(herb_names)
            summary += f'中药靶点包括：{unique_targets}'

        # # compound_target_activities
        # print(compound_names, target_names)
        # drug_target_df = search_drug_target_activity(compound_names, target_names)

        # # 将PPI写入network_plot.json文件，用于展示网络图
        # drug_target_json  = convert_drug_target_to_json(drug_target_df)
        # with open("client/public/data/network_plot.json", "w", encoding="utf-8") as f:
        #     json.dump(drug_target_json, f, ensure_ascii=False)


        # drug_target_str = df_to_dict_and_print(drug_target_df) 
        # summary_with_link = plot_compound_target_activity(drug_target_df, drug_target_str)

        return summary


# 药物与靶点的结合活性
class QueryCompoundTargetActivity():
    def __init__(self):
        self.query_herb_info = QueryHerbData()
        
    def execute(self, **kwargs):
        herb_names = kwargs.get('herb_names', [])    
        compound_names = kwargs.get('compound_names', [])
        target_names = kwargs.get('target_names', [])
        if herb_names:
            unique_compounds = self.query_herb_info._load_herb_compounds(herb_names)
            compound_info = f'中药化合物包括：{unique_compounds}'
            compound_names = TCMAgent.get_key_compound_name(compound_info)
            
        # compound_target_activities
        print(compound_names, target_names)
        drug_target_df = search_drug_target_activity(compound_names, target_names)

        # 将PPI写入network_plot.json文件，用于展示网络图
        drug_target_json = convert_drug_target_to_json(drug_target_df)
        with open("client/public/data/network_plot.json", "w", encoding="utf-8") as f:
            json.dump(drug_target_json, f, ensure_ascii=False)


        drug_target_str = df_to_dict_and_print(drug_target_df) 
        summary_with_link = plot_compound_target_activity(drug_target_df, drug_target_str)

        return summary_with_link


# 蛋白-蛋白互作分析

class QueryProteinInteractions():
    def execute(self, **kwargs):
        gene_names = kwargs.get('gene_names', ['P00533', 'P04626'])
        min_score = kwargs.get('min_score', 0.4)
        interactions_json = query_protein_interactions(gene_names, min_score)
        # 将PPI写入network_plot.json文件，用于展示网络图
        with open("client/public/data/network_plot.json", "w", encoding="utf-8") as f:
            json.dump(interactions_json, f, ensure_ascii=False)

        result = analyze_protein_network(interactions_json)

        return result

# 基因富集分析
class GeneEnrichment:
    def __init__(self):
        # 加载中药靶点信息
        self.gene_enrich = GeneEnrichmentAnalyzer()

    def execute(self, **kwargs):
        gene_names = kwargs.get("gene_names", [])

        """执行蛋白互作分析"""
        
        print("Starting protein interaction query...")
        interactions_json = query_protein_interactions(gene_names, min_score=0.4)

        # 将PPI写入network_plot.json文件，用于展示网络图
        with open("client/public/data/network_plot.json", "w", encoding="utf-8") as f:
            json.dump(interactions_json, f, ensure_ascii=False)

        """执行靶点富集分析"""

        summary, enrichment_results = self.gene_enrich.execute(**kwargs)
        summary_with_link = plot_enrichment(summary, enrichment_results)

        return summary_with_link


class HerbTargetEnrichment:
    def __init__(self):
        # 加载中药靶点信息
        self.gene_enrich = GeneEnrichmentAnalyzer()

        # 初始化用户问题涉及的中药-靶点字典herb_targets，以及用于富集分析的靶点集合unique_targets
        self.herb_targets = {}  #TODO 回头改为list 存储三元组的列表 {    "herb": "黄芪",    "target": "ACE2",    "relation": "contains"  }
        self.unique_targets = set()

    def _load_herb_targets(self, herb_names: List[str]) -> List[str]:
        """加载中药靶点信息"""
        herb_targets_db_path = Path("data/herb_targets_db.json")
        if not herb_targets_db_path.exists():
            raise FileNotFoundError(f"文件 {herb_targets_db_path} 不存在")
        
        with open(herb_targets_db_path, "r", encoding="utf-8") as f:
            herb_targets_database = json.load(f)

        """根据中药名称列表，获取{中药：靶点}保存为json，以及去重后的靶点列表"""
        
        for herb_name in herb_names:
            if herb_name not in herb_targets_database:
                raise ValueError(f"未找到中药 {herb_name} 的靶点信息")  # TODO 以后没找到中药靶点信息，搜索在线数据库找
            
            targets = herb_targets_database[herb_name]
            self.herb_targets[herb_name] = targets
            self.unique_targets.update([target["Target name"] for target in targets])

            # # 生成三元组
            # for target in targets:
            #     self.herb_targets.append({
            #         "herb": herb_name,
            #         "target": target["Target name"],
            #         "relation": "contains"
            #     })

        # 将herb_targets写入network_plot.json文件，用于展示网络图
        with open("client/public/data/network_plot.json", "w", encoding="utf-8") as f:
            json.dump(self.herb_targets, f, ensure_ascii=False)

        # 保存herb_names到json
        herb_names_path = Path("data/herb_names.json")
        with open(herb_names_path, "w", encoding="utf-8") as f:
            json.dump(herb_names, f, ensure_ascii=False)
        # print('herb_names', herb_names)

        # 保存unique_targets到json
        unique_targets =  list(self.unique_targets)  # unique_targets从集合改为列表形式 

        unique_targets_path = Path(r"data/unique_targets.json")
        with open(unique_targets_path, "w", encoding="utf-8") as f:
            json.dump(unique_targets, f, ensure_ascii=False)

        return unique_targets

    def execute(self, **kwargs):
        """执行靶点富集分析"""

        herb_names = kwargs.get("herb_names", [])
        unique_targets = self._load_herb_targets(herb_names)  # 加载本轮对话涉及的中药及靶点信息，更新 self.herb_targets，self.unique_targets
        kwargs['gene_names'] = unique_targets
        # print('unique_targets', unique_targets)
        # 执行富集分析
        summary, enrichment_results = self.gene_enrich.execute(**kwargs)
        summary_with_link = plot_enrichment(summary, enrichment_results)

        return summary_with_link

class TCMAgent():

    def __init__(self, main_model, tool_model, flash_model):
        self.main_model = main_model
        self.tool_model = tool_model
        self.flash_model = flash_model
        self.agents = {
        }
        self.tools = {     # 通过字典的键值对映射，将工具名称与对应的工具实例关联起来
            "get_compound_info": GetCompoundInfo(),
            "get_molecular_sim": CalculateSimilarity(),
            "query_herb_data":QueryHerbData(),
            "query_protein_interactions": QueryProteinInteractions(),
            "search_drug_target_activity": QueryCompoundTargetActivity(),
            "gene_enrichment":GeneEnrichment(),  # 基因富集分析（直接以靶点列表为输入）
            "herb_target_enrichment": HerbTargetEnrichment(),  # 中药靶点富集分析工具
        }
        self.tools_prompt_config = [  # 将之前加载的工具配置，编为列表
            CHAT_TOOL,
            GET_COMPOUND_INFO_TOOL,
            GET_MOLECULAR_SIM_TOOL,
            QUERY_HERB_DATA_TOOL,
            SEARCH_DRUG_TARGET_ACTIVITY_TOOL,
            QUERY_PROTEIN_INTERACTIONS_TOOL,
            TARGET_ENRICH_TOOL,  # 面向靶点列表的基因富集分析
            HERB_TARGET_ENRICH_TOOL  # 面向中药的靶点富集分析工具配置

        ]
        # 创建Files文件夹
        Path("files").mkdir(parents=True, exist_ok=True)

        self.conversations = [{"role": "system", "content": "You must follow my instructions."}]
        self.tool_conversations = [{"role": "system", "content": "You must follow my instructions."}]
        
    def get_conversation_intention_tools(self, question):
        self.tool_conversations.append({"role": "user", "content": question})
        sys_prompt_latest = SERIES_INTENTION_RECOGNITION_SYSTEM_PROMPT.format(
            tools=self.tools_prompt_config
        )
        self.tool_conversations[0]["content"] = sys_prompt_latest
        ans = ""
        for char in get_llm_answer_converse(self.tool_conversations, model=self.tool_model):
            ans += char
            # print(char, end="", flush=True)
        self.tool_conversations.append({"role": "assistant", "content": ans})
        try:
            intention_tools = get_json(ans)["tools"]  # 不稳定，总会报错：TypeError: 'NoneType' object is not subscriptable
        except:
            intention_tools = [f"chat(question='{question}')"]  # 
        # print(intention_tools)
        return intention_tools

    @staticmethod   #备注：静态类的功能，无需实例化：可以直接通过类名调用静态方法，而不需要创建类的实例。
    def get_compound_name(question):
        prompt = EXTRACT_CHEM_NAME_PROMPT.format(question=question)
        ans = ""
        for char in get_llm_answer(prompt, model="glm-4-plus"):
            ans += char
        ans = get_json(ans)
        compound_names = ans["compound_name"]
        return compound_names

    # 基于化合物英文名称获取cid
    @staticmethod
    def get_cid_by_name(name):
        search_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/cids/JSON"
        response = requests.get(search_url)
        cid = response.json()['IdentifierList']['CID'][0]
        return cid,search_url
    
    # 提取中药的标准化名称
    @staticmethod
    def get_herb_name(question):
        """通过大语言模型将用户输入的中药名称规范化"""
        prompt = HERB_NORMALIZER_PROMPT.format(question=question)
        ans = ""
        for char in get_llm_answer(prompt, model="glm-4-plus"):  # 模型名称由 TCMAgent 统一管理
            ans += char
        ans = get_json(ans)
        herb_names = ans['normalized_herb_name']
        return herb_names
    
    @staticmethod   #备注：静态类的功能，无需实例化：可以直接通过类名调用静态方法，而不需要创建类的实例。
    def get_key_compound_name(question):
        prompt = GET_KEY_COMPOUNDS_PROMPT.format(question=question)
        ans = ""
        for char in get_llm_answer(prompt, model="qwen", temperature=0.2):
            ans += char
        ans = get_json(ans)
        compound_names = ans["compound_name"]
        return compound_names

    # 富集分析中提取在gseapy中对应的数据库名称
    @staticmethod
    def get_gseapy_database_name(question):
        """通过大语言模型将用户输入的富集分析对应的数据库名称规范化"""
        prompt = HERB_NORMALIZER_PROMPT.format(question=question)
        ans = ""
        for char in get_llm_answer(prompt, model="glm-4-plus"):  # 模型名称由 TCMAgent 统一管理
            ans += char
        ans = get_json(ans)
        herb_names = ans['normalized_herb_name']
        return herb_names

    # 保存聊天记录为json文件
    def save_conversation(self, conversation):
        with open("data/conversation.json", "w", encoding="utf-8") as f:
            json.dump(conversation, f, ensure_ascii=False)

    # 组装LLM聊天记录信息，用于提取关键词
    def combine_context(self, human_question, llm_answer):
        # llm_ans = self.conversations[-1]["content"]
        # human_question = self.conversations[-4]["content"]
        content = f"""
human_question：
{human_question}
---
llm_answer:
{llm_answer}
"""
        return content

    def work_flow(self, question, intention_tools):
        self.conversations.append({"role": "user", "content": question})
        for tool_name in intention_tools:
            func_name = get_func_name(tool_name)
            tool_kwargs = json.loads(extract_params_to_json(tool_name))
            tool_kwargs["func_name"] = func_name
            tool_kwargs["question"] = question
            tool_kwargs["model"] = self.main_model
            if func_name in list(self.agents.keys()):
                ans = ""
                for char in self.agents[func_name].execute(**tool_kwargs): 
                    yield char
                    ans += char
                yield "\n"
                self.conversations.append({"role": "assistant", "content": ans})
                self.tool_conversations.append({"role": "assistant", "content": ans[:5000]})                
            elif func_name == "chat":
                ans = ""
                for char in get_llm_answer(question, model=self.main_model):
                    yield char
                    ans += char
                self.conversations.append({"role": "assistant", "content": ans})
                self.tool_conversations.append({"role": "assistant", "content": ans[:5000]})
            else:
                info = self.tools[func_name].execute(**tool_kwargs)
                yield "__Contemplating...__\n\n"
                llm_info = f""""
以下是TCM-Agent系统的分析结果：\n{info}\n
"""
                self.conversations.append({"role": "assistant", "content": llm_info})
                process_info_prompt = PROCESS_INFO_PROMPT.format(question=question)  # 在workflow中，只有此处的prompt
                self.conversations.append({"role": "user", "content": process_info_prompt})
                self.tool_conversations.append({"role": "assistant", "content": llm_info[:5000]})  # TODO 思考这个代码的是否有必要
                ans = ""
                for char in get_llm_answer_converse(self.conversations, model=self.main_model):
                    yield char
                    ans += char
                yield "\n"
                content = self.combine_context(question, ans)    # TODO content应该与最后的ans有关
                keywords = get_keywords(content)
                yield "\n\n*Searching related papers...*\n\n"
                searched_results = get_search_results(keywords)  
                for char in get_related_papers_yield(ans, searched_results):
                    yield char
                yield "\n"
                self.conversations.append({"role": "assistant", "content": ans})
                self.tool_conversations.append({"role": "assistant", "content": ans[:5000]})
        self.save_conversation(self.conversations)



if __name__ == "__main__":

    import time
    genes = [
        "TP53", "BRCA1", "EGFR", "MYC", "AKT1", 
        "VEGFA", "PTEN", "KRAS", "CDKN2A", "IL6", 
        "TNF", "MAPK1", "STAT3", "JUN", "FOS", 
        "HIF1A", "NFKB1", "PIK3CA", "RB1", "CCND1"
    ]

    model_1, model_2, model_3, model_4 = "deepseek", "glm-4-plus", "qwen-plus", "moonshot"
    model = model_3
    start_time = time.time()
    agent = TCMAgent(main_model=model, tool_model=model, flash_model=model)
    # question = "请评估复元活血汤（柴胡半两、瓜蒌根、当归各、红花、甘草、大黄、桃仁）在纤维化中的作用，以及在kegg和GO_Biological_Process、Reactome的通路富集情况。"
    # question = '金叶败毒颗粒（金银花、连翘、 黄芩、板蓝根）治疗甲型流感病毒（Influenza A Virus, IAV）感染的系统药理学分析，包括关键化合物成分、关键靶点和KEGG、GO通路，系统解读分析结果'
    # question = "丹灯通脑软胶囊（丹参、灯盏细辛、川芎、葛根）治疗脑缺血再灌注损伤的系统药理学分析，包括关键化合物成分、关键靶点和KEGG、GO通路，系统解读分析结果"
    # question = '瓜蒌薤白汤（瓜蒌、薤白、白酒）治疗II型心肾综合征（Cardiorenal Syndrome Type II, CRS II）的系统药理学分析，包括关键化合物成分、关键靶点和KEGG、WikiPathways通路富集分析，系统解读分析药理机制结果'
    # question = '冠心宁注射液（丹参、川芎）治疗心力衰竭（Heart Failure, HF）的系统药理学分析，包括关键成分、关键靶点和KEGG、WikiPathways通路，系统解读分析药理机制结果'
    # question = '金叶败毒颗粒的KEGG通路富集分析中，哪些通路与抗病毒和抗炎相关？'
    # question = '丹灯通脑软胶囊（DDTNC）由哪些中药组成'
    # question = '请评估四物汤在肝纤维化中的作用，以及在kegg的通路富集情况。'

    # question = f"请分析下列化合物和靶点的结合活性，甘草酸、姜黄素、黄芩甘，MMP9、IL-6、IL1B"
    # question = f"请分析下列化合物的靶点，人参皂苷、槲皮素"
    # question = '​​System Pharmacology Mechanisms of 四逆散（Si-ni San） in Treating Liver Fibrosis, and Enrichment Analysis of KEGG, Reactome, GO, and Wikipedia Pathways'
    # question = f"请对下列基因进行PPI分析{genes}"
    # question = f'请分析四逆散有哪些主要成分与{genes}靶点间存在靶向调节关系'
    # question = '安喘颗粒（麻黄、葶苈子、乌梅、苦参、巴戟天、甘草和灵芝）中哪些化合物是核心活性成分？'
    formula = ''
    # question = f'瓜蒌薤白汤（GXD）能否干预PI3K/AKT/NF-κB通路？'
    # question = '金叶败毒颗粒(金银花、大青叶、蒲公英和鱼腥草能否干预IL-6和NF-κB靶点？'
    # question = '大承气汤有哪些中药组成？' # model 3
    question = '丹灯通脑软胶囊（川芎、葛根、丹参、灯盏细辛）的网络药理学分析揭示了哪些KEGG关键通路？ '


    intention_tools = agent.get_conversation_intention_tools(question)
    print(intention_tools)

    for char in agent.work_flow(question, intention_tools):
        if char:
            print(char, end="", flush=True)

    end_time = time.time()
    print(f"\n程序执行时间: {end_time - start_time:.4f} 秒")

