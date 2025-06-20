'''
一些数据处理的函数
'''
path = r'F:\1-在研工作\2025-DeepTCM 2.0\data\数据集.xlsx'
def formula_set_process():
    import pandas as pd
    import random
    # 设置随机数种子
    random.seed(42)  # 42 是一个常用的随机数种子，可以替换为其他整数

    # 读取文件并指定编码（假设文件编码为 GBK）
    data = pd.read_excel(path)

    # 定义一些随机的提示词模板
    instruction_templates = [
        "请使用DeepTCM分析如下中药复方的功效、根据证素学对该功效进行拆解，结果以json的形式返回。",
        "根据DeepTCM模型，分析以下中药复方的功效，并拆解其证素病位和病性，结果以json格式返回。",
        "使用DeepTCM对以下中药复方进行功效分析，并拆解其证素病位和病性，结果以json形式返回。",
        "请使用DeepTCM模型分析以下中药复方的功效，并根据证素学拆解其病位和病性，结果以json格式返回。"
    ]

    # 创建一个空的DataFrame来存储结果
    result_df = pd.DataFrame(columns=['instruction', 'input', 'output'])

    # 遍历每一行数据
    for index, row in data.iterrows():
        # 随机选择一个提示词模板
        instruction = random.choice(instruction_templates)
        
        # 获取复方、功效、病位、病性
        formula = row['复方']
        effect = row['功效']
        disease_location = row['病位'] if pd.notna(row['病位']) else 'NA'
        disease_nature = row['病性'] if pd.notna(row['病性']) else 'NA'
        
        # 构建input
        input_text = f"复方: {formula}"
        
        # 构建output
        output_json = {
            '功效': effect,
            '证素病位': disease_location,
            '证素病性': disease_nature
        }
        
        # 将结果添加到DataFrame中
        new_row = pd.DataFrame({
            'instruction': [instruction],
            'input': [input_text],
            'output': [output_json]
        })
        result_df = pd.concat([result_df, new_row], ignore_index=True)
    
    # 对结果数据进行随机排序
    result_df = result_df.sample(frac=1, random_state=42).reset_index(drop=True)
    # 保存结果到CSV文件
    result_df.to_csv('output_formula_dataset.csv', index=False, encoding='utf-8-sig')  # 使用 utf-8-sig 避免 Excel 打开乱码

    print("数据集生成完成，已保存为 output_formula_dataset.csv")


def sydrome_set_process():
    import pandas as pd
    import random
    path = r'F:\1-在研工作\2025-DeepTCM 2.0\data\数据集.xlsx'
    # 读取 WPS 文件（假设为 Excel 文件）
    data = pd.read_excel(path, sheet_name='证候')  # 如果是 CSV 文件，使用 pd.read_csv('your_file.csv', encoding='GBK')

    # 定义一些随机的提示词模板
    instruction_templates = [
        "请使用DeepTCM对中医证候进行证素学拆解，结果以json的形式返回。",
        "根据DeepTCM模型，对以下中医证候进行证素学拆解，结果以json格式返回。",
        "使用DeepTCM对以下中医证候进行证素学分析，结果以json形式返回。",
        "请使用DeepTCM模型对以下中医证候进行证素学拆解，结果以json格式返回。",
        "请分析以下中医证候的证素病位和病性，结果以json格式返回。"
    ]

    # 创建一个空的DataFrame来存储结果
    result_df = pd.DataFrame(columns=['instruction', 'input', 'output'])

    # 遍历每一行数据
    for index, row in data.iterrows():
        # 随机选择一个提示词模板
        instruction = random.choice(instruction_templates)
        
        # 获取中医证候名、病位、病性
        syndrome = row['中医证候名（原）']
        disease_location = row['病位'] if pd.notna(row['病位']) else 'NA'
        disease_nature = row['病性'] if pd.notna(row['病性']) else 'NA'
        
        # 构建input
        input_text = f"中医证候: {syndrome}"
        
        # 构建output
        output_json = {
            '证候': syndrome,
            '证素病位': disease_location,
            '证素病性': disease_nature
        }
        
        # 将结果添加到DataFrame中
        new_row = pd.DataFrame({
            'instruction': [instruction],
            'input': [input_text],
            'output': [output_json]
        })
        result_df = pd.concat([result_df, new_row], ignore_index=True)

    # 对结果数据进行随机排序
    result_df = result_df.sample(frac=1, random_state=42).reset_index(drop=True)
    # 保存结果到CSV文件
    result_df.to_csv('output_sydrome_dataset.csv', index=False, encoding='utf-8-sig')  # 使用 utf-8-sig 避免 Excel 打开乱码

    print("数据集生成完成，已保存为 output_sydrome_dataset.csv")



if __name__ == "__main__":
    formula_set_process()