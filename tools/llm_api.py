from openai import OpenAI
from functools import wraps

from zhipuai import ZhipuAI
from functools import wraps

from tools.llm_keys import *

'''------GLM------'''
def get_zhipu_response(zhipu_key, question, model="glm-4", temperature=0.5):
    client = ZhipuAI(api_key=zhipu_key) 
    response = client.chat.completions.create(
        model=model,  
        messages=[
            {"role": "system", "content": "你是一个乐于解答各种问题的助手，你的任务是为用户提供专业、准确、有见地的建议。"},
            {"role": "user", "content": question},
        ],
        stream=True,
        temperature=temperature
    )
    full_response = ""
    for chunk in response:
        text = chunk.choices[0].delta.content
        full_response += text
        print(text, end="")
    return full_response


def get_zhipu_yield(api_key, question, model, temperature=0.5):
    client = ZhipuAI(api_key=api_key) 
    response = client.chat.completions.create(
        model=model,  
        messages=[
            {"role": "system", "content": "你是一个人工智能助手,你叫TCM-Agent"},
            {"role": "user", "content": question},
        ],
        stream=True,
        temperature=temperature,
        max_tokens=4096
    )
    for chunk in response:
        text = chunk.choices[0].delta.content
        yield text

def get_zhipu_yield_converse(api_key, messages, model, temperature=0.5):
    client = ZhipuAI(api_key=api_key) 
    response = client.chat.completions.create(
        model=model,  
        messages=messages,
        stream=True,
        temperature=temperature
    )
    for chunk in response:
        text = chunk.choices[0].delta.content
        yield text


'''------Deepseek------'''
def get_deepseek_response_yield(deepseek_api, question, model, system_prompt= "You are a helpful assistant", temperature=0.95):
    client = OpenAI(api_key=deepseek_api, base_url="https://api.deepseek.com")
    response = client.chat.completions.create(
        model='deepseek-chat',
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        stream=True
    )
    for char in response:
        content = char.choices[0].delta.content
        yield content
        
def get_deepseek_response_yield_converse(deepseek_api, messages, model, temperature=0.95):
    client = OpenAI(api_key=deepseek_api, base_url="https://api.deepseek.com")
    response = client.chat.completions.create(
        model='deepseek-chat',
        messages=messages,
        stream=True
    )
    for char in response:
        content = char.choices[0].delta.content
        yield content



'''-------Qwen------'''
import os

def get_qwen_response_yield(qwen_api, question, model="qwen-plus", temperature=0.95):

    client = OpenAI(
        api_key=qwen_api ,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    response = client.chat.completions.create(
        model="qwen-plus",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": question},
        ],
        temperature=temperature,
        stream=True
    )
    for char in response:
        content = char.choices[0].delta.content
        yield content

def get_qwen_response_yield_converse(qwen_api, messages, model="qwen-plus", 
                                        temperature=0.95):

    client = OpenAI(
        api_key=qwen_api,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    response = client.chat.completions.create(
        model="qwen-plus",
        messages=messages,
        temperature=temperature,
        stream=True
    )
    for char in response:
        content = char.choices[0].delta.content
        yield content



'''------MoonShot------'''

from openai import OpenAI

def get_moonshot_response_yield(moonshot_api, question, model="moonshot-v1-8k", system_prompt="你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。Moonshot AI 为专有名词，不可翻译成其他语言。", temperature=0.3):

    client = OpenAI(api_key=moonshot_api, base_url="https://api.moonshot.cn/v1")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        temperature=temperature,
        stream=True
    )
    for char in response:
        content = char.choices[0].delta.content
        yield content

def get_moonshot_response_yield_converse(moonshot_api, messages, model="moonshot-v1-8k", temperature=0.3):

    client = OpenAI(api_key=moonshot_api, base_url="https://api.moonshot.cn/v1")
    response = client.chat.completions.create(
        model='moonshot-v1-8k',
        messages=messages,
        temperature=temperature,
        stream=True
    )
    for char in response:
        content = char.choices[0].delta.content
        yield content



'''------根据model选择相应接口------'''

def get_llm_answer_merge(llm_key, prompt, model, system_prompt="You are a helpful assistant", temperature=0.95):
    if model.startswith("gpt") or model.startswith("chatgpt"):
        for char in get_response_yield(llm_key, prompt, model, temperature):
            yield char
    elif model.startswith("glm"):
        for char in get_zhipu_yield(llm_key, prompt, model, temperature):
            yield char
    elif model.startswith("deepseek"):
        for char in get_deepseek_response_yield(llm_key, prompt, model, system_prompt, temperature):
            yield char 
    elif model.startswith("llama") or model.startswith("mixtral"):
        for char in get_groq_yield(llm_key, prompt, model, temperature):
            yield char
    elif "/" in model:
        for char in get_claude_yield(llm_key, prompt, model, temperature):
            yield char
    elif model.startswith("gemini"):
        for char in get_gemini_response_yield(llm_key, prompt, model, temperature):
            yield char
    elif model.startswith("meta/llama"):
        for char in get_nvidia_response_yield(llm_key, prompt, model, temperature):
            yield char
    elif model.startswith("qwen"):
        for char in get_qwen_response_yield(llm_key, prompt, model, temperature):
            yield char
    elif model.startswith("yi"):
        for char in get_yi_answer_yield(llm_key, prompt, model, temperature):
            yield char
    elif model.startswith("moonshot"):
        for char in get_moonshot_response_yield(llm_key, prompt, model, system_prompt, temperature):
            yield char 
    
            
def get_llm_answer_converse_merge(llm_key, conversations, model, temperature):
    if model.startswith("gpt") or model.startswith("chatgpt"):        
        for char in get_response_yield_converse(llm_key, conversations, model, temperature):
            yield char
    elif model.startswith("glm"):
        for char in get_zhipu_yield_converse(llm_key, conversations, model, temperature):
            yield char
    elif model.startswith("llama") or model.startswith("mixtral"):
        for char in get_groq_yield_converse(llm_key, conversations, model, temperature):
            yield char
    elif "/" in model:
        for char in get_claude_converse(llm_key, conversations, model, temperature):
            yield char
    elif model.startswith("deepseek"):
        for char in get_deepseek_response_yield_converse(llm_key, conversations, model, temperature):
            yield char
    elif model.startswith("gemini"):
        for char in get_gemini_response_yield(llm_key, conversations, model, temperature):
            yield char
    elif model.startswith("meta/llama"):
        for char in get_nvidia_response_yield_converse(llm_key, conversations, model, temperature):
            yield char
    elif model.startswith("qwen"):
        for char in get_qwen_response_yield_converse(llm_key, conversations, model, temperature):
            yield char
    elif model.startswith("moonshot"):
        for char in get_moonshot_response_yield_converse(llm_key, conversations, model, temperature):
            yield char

            
def get_llm_key(model):
    try:
        if model.startswith("gpt") or model.startswith("chatgpt"):        
            llm_key = openai_key
        elif model.startswith("glm"):
            llm_key = zhipu_key
        elif model.startswith("llama") or model.startswith("mixtral"):
            llm_key = groq_key
        elif "/" in model:
            # print("选择openrouter模型")
            llm_key = openrouter_key
        elif model.startswith("deepseek"):
            llm_key = deepseek_key
        elif model.startswith("gemini"):
            llm_key = gemini_key
        elif model.startswith("meta/llama"):
            llm_key = nvidia_key
        elif model.startswith("llama") or model.startswith("mixtral"):
            llm_key = groq_key
        elif model.startswith("qwen"):
            llm_key = qwen_key
        elif model.startswith("yi"):
            llm_key = yi_key
        elif model.startswith("moonshot"):
            llm_key = moonshot_key
        return llm_key
    except:
        print("请检查model是否正确")
        
def get_llm_answer(question, model, temperature=0.5):
    """
    支持的模型：
    - gpt-3.5-turbo
    - chatgpt-4o-latest
    - glm-4
    - llama3-70b-8192
    - mixtral-8x7b-32768
    - anthropic/claude-3-haiku
    - gemini-1.5-pro-latest
    - meta/llama3-70b-instruct
    - yi-large-turbo
    - qwen-2.5
    - moonshot-v1-8k
    """
    llm_key = get_llm_key(model)
    for char in get_llm_answer_merge(llm_key, question, model, temperature=temperature):
        yield char
        
def get_llm_answer_converse(conversations, model, temperature=0.3):
    llm_key = get_llm_key(model)
    for char in get_llm_answer_converse_merge(llm_key, conversations, model, temperature):
        yield char


