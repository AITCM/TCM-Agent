import re
import json

def get_func_name(text):
    # 正则表达式，匹配函数名
    pattern = r'([a-zA-Z_]\w*)\('

    # 使用正则表达式提取函数名
    function_name = re.search(pattern, text)

    # 提取到的函数名
    extracted_function_name = function_name.group(1) if function_name else None

    return extracted_function_name

def extract_params_to_json(function_call: str) -> str:
    # 正则表达式匹配参数部分
    param_pattern = r'\((.*)\)'

    # 提取参数字符串
    params_match = re.search(param_pattern, function_call)
    params_str = params_match.group(1) if params_match else None

    # 将参数字符串转换为字典
    params_dict = {}
    if params_str:
        # 处理参数中包含列表的情况
        params_list = split_params(params_str)
        for param in params_list:
            key, value = param.split('=', 1)
            key = key.strip()
            value = value.strip()
            # 检查并解析列表
            if value.startswith('[') and value.endswith(']'):
                # 提取列表内容
                list_content = value[1:-1].strip()
                if list_content:  # 确保列表不为空
                    # 分割列表元素，考虑元素中可能包含逗号的情况
                    list_elements = split_list_elements(list_content)
                    # 去除元素两边的引号
                    list_elements = [elem.strip().strip("'\"") for elem in list_elements]
                    params_dict[key] = list_elements
                else:
                    params_dict[key] = []
            else:
                # 去掉引号
                value = value.strip("'\"")
                params_dict[key] = value

    # 转换为JSON格式
    return json.dumps(params_dict, indent=4)

def split_params(params_str: str) -> list:
    """分割参数字符串，考虑参数值中可能包含逗号的情况"""
    params_list = []
    depth = 0
    start = 0
    for i, char in enumerate(params_str):
        if char == ',' and depth == 0:
            params_list.append(params_str[start:i])
            start = i + 1
        elif char == '[':
            depth += 1
        elif char == ']':
            depth -= 1
    params_list.append(params_str[start:])
    return params_list

def split_list_elements(list_content: str) -> list:
    """分割列表内容，考虑元素中可能包含逗号的情况"""
    elements = []
    depth = 0
    start = 0
    for i, char in enumerate(list_content):
        if char == ',' and depth == 0:
            elements.append(list_content[start:i])
            start = i + 1
        elif char == '[':
            depth += 1
        elif char == ']':
            depth -= 1
    elements.append(list_content[start:])
    return elements

# 示例使用
if __name__ == '__main__':
    test_function_call = "extract_clean_text_from_pdf(pdf_path='path/to/pdf', method='pdfminer')"
    extracted_json = extract_params_to_json(test_function_call)
    print(extracted_json)
    
    test_function_call_with_list = "query_protein_interactions(protein_list=['protein1', 'protein2', 'protein3'], min_score=0.4)"
    extracted_json_with_list = extract_params_to_json(test_function_call_with_list)
    print(extracted_json_with_list)