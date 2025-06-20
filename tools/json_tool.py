import json
import re

def get_json(text):
    try:
        # 尝试直接解析整个文本
        json_obj = json.loads(text)
        return json_obj
    except json.JSONDecodeError:
        # 使用正则表达式提取包含```json的整个块
        matches = re.findall(r"```json\n([\s\S]*?)\n```", text)
        # 使用正则表达式提取直接以{开头，以}结束的文本
        direct_json_match = re.search(r"\{([\s\S]*?)\}", text)
        
        if matches:
            try:
                response_json = json.loads(matches[0])
                return response_json
            except json.JSONDecodeError as e:
                print("解析错误：", e)
        elif direct_json_match:
            try:
                response_json = json.loads(direct_json_match.group(0))
                return response_json
            except json.JSONDecodeError as e:
                print("解析错误：", e)
        else:
            print("未找到JSON数据。")

# 示例使用
if __name__ == "__main__":
    text_with_json =''' ```json
{{
    "tools": ["get_bing_searched_results(keyword='AI', max_results=5)"]
}}
```'''
    # text_with_json = "这是一个包含JSON的文本：{ \"key\": \"value\" }"
    print(text_with_json)

    json_obj = get_json(text_with_json)
    print(json_obj, type(json_obj))
