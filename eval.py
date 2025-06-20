from agent import TCMAgent
import time
import os
import pandas as pd
from pathlib import Path
import json

# 模型选择
model_1, model_2, model_3 = "deepseek", "glm-4-plus", "qwen-plus" #, "moonshot"
model = model_3

# 初始化代理
agent = TCMAgent(main_model=model, tool_model=model, flash_model=model)

# 进度记录文件路径
PROGRESS_FILE = "progress.json"

def load_progress():
    """加载进度记录"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_progress(progress):
    """保存进度记录"""
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=4)

def process_question(question, progress_key):
    """处理单个问题并记录执行时间"""
    start_time = time.time()
    
    try:
        intention_tools = agent.get_conversation_intention_tools(question)
        print(intention_tools)

        ans = ''
        for char in agent.work_flow(question, intention_tools):
            if char:
                print(char, end="", flush=True)
                ans += char

        end_time = time.time()
        exec_time = end_time - start_time
        print(f"\n程序执行时间: {exec_time:.4f} 秒")
        
        return {
            "answer": ans,
            "execution_time": exec_time,
            "status": "completed"
        }
    except Exception as e:
        end_time = time.time()
        return {
            "answer": f"处理出错: {str(e)}",
            "execution_time": end_time - start_time,
            "status": "error"
        }

def process_tcm_questions(input_folder, output_folder):
    """处理指定文件夹中的所有Excel文件，支持断点续接"""
    # 创建输出文件夹
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    
    # 加载进度
    progress = load_progress()
    
    # 获取所有Excel文件
    excel_files = [f for f in os.listdir(input_folder) if f.endswith('.xlsx')]
    
    for file in excel_files:
        input_path = os.path.join(input_folder, file)
        output_path = os.path.join(output_folder, file)
        
        # 检查是否已完成
        if progress.get(file, {}).get('status') == 'completed':
            print(f"文件 {file} 已处理过，跳过...")
            continue
        
        # 读取Excel文件
        df = pd.read_excel(input_path, engine='openpyxl')
        
        # 初始化结果列
        if 'TCM-Agent' not in df.columns:
            df['TCM-Agent'] = ''
        if 'Execution_Time' not in df.columns:
            df['Execution_Time'] = ''
        if 'Status' not in df.columns:
            df['Status'] = ''
        
        # 更新进度记录
        if file not in progress:
            progress[file] = {"processed_rows": 0, "status": "processing"}
        
        # 处理每个问题
        for idx, row in df.iterrows():
            # 跳过已处理的行
            if idx < progress[file]["processed_rows"]:
                continue
                
            question = row['Question']
            if pd.notna(question) and isinstance(question, str):
                print(f"\n处理文件 {file} 第 {idx+1} 行: {question[:50]}...")
                
                # 处理问题并获取结果
                result = process_question(question, f"{file}_{idx}")
                
                # 更新DataFrame
                df.at[idx, 'TCM-Agent'] = result["answer"]
                df.at[idx, 'Execution_Time'] = result["execution_time"]
                df.at[idx, 'Status'] = result["status"]
                
                # 实时保存结果
                df.to_excel(output_path, index=False, engine='openpyxl')
                
                # 更新进度
                progress[file]["processed_rows"] = idx + 1
                save_progress(progress)
        
        # 标记文件完成
        progress[file]["status"] = "completed"
        save_progress(progress)
        print(f"成功处理并保存: {file}")

if __name__ == "__main__":
    input_folder = r"E:\1-在研工作\2025-系统药理学Agent\Results\遴选的20篇"
    output_folder = r"E:\1-在研工作\2025-系统药理学Agent\Results\遴选的20篇-结果"
    
    # 确保输出文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    process_tcm_questions(input_folder, output_folder)



# genes = [
#     "TP53", "BRCA1", "EGFR", "MYC", "AKT1", 
#     "VEGFA", "PTEN", "KRAS", "CDKN2A", "IL6", 
#     "TNF", "MAPK1", "STAT3", "JUN", "FOS", 
#     "HIF1A", "NFKB1", "PIK3CA", "RB1", "CCND1"
# ]


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







