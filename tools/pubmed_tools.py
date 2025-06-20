from typing import List, Optional
import json
from tools.llm_api import *
from tools.json_tool import *
from typing import List, Dict
from tqdm import tqdm
import time
import pandas as pd
from tools.pubmed_api import PubMedFetcher


def build_pubmed_query(
    keywords: List[str],
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    use_mesh: bool = True
) -> str:
    """
    动态生成PubMed检索式，支持时间范围和智能术语分组
    
    Args:
        keywords: 关键词列表（至少1个）
        start_year: 开始年份（如2019）
        end_year: 结束年份（如2023）
        use_mesh: 是否优先使用MeSH术语
    
    Returns:
        完整的PubMed检索式字符串
    """
    if not keywords:
        raise ValueError("关键词列表不能为空")
    
    # 1. 处理核心术语（第一个关键词强制AND）
    core_term = f'"{keywords[0]}"[Title/Abstract]'
    
    # 2. 处理其他术语（自动分组为OR逻辑）
    other_terms = []
    for term in keywords[1:]:
        term = term.strip('"')  # 移除用户可能自带的引号
        # 智能选择字段标签
        if use_mesh and " " not in term:
            other_terms.append(f"{term}[MeSH]")
        else:
            other_terms.append(f'"{term}"[Title/Abstract]')
    
    # 3. 组合基础检索式
    if other_terms:
        query = f"{core_term} AND ({' OR '.join(other_terms)})"
    else:
        query = core_term
    
    # 4. 添加时间范围限定
    if start_year is not None and end_year is not None:
        query += f' AND ("{start_year}"[Date - Publication] : "{end_year}"[Date - Publication])'
    elif start_year is not None:  # 仅限定开始年份
        query += f' AND ("{start_year}"[Date - Publication] : "3000"[Date - Publication])'
    elif end_year is not None:  # 仅限定结束年份
        query += f' AND ("0000"[Date - Publication] : "{end_year}"[Date - Publication])'
    
    return query

def fetch_all_pages(
    fetcher,
    query: str,
    max_pages: int = 15,
    results_per_page: int = 50,
    sleep_time: int = 3,
    output_file: Optional[str] = None
) -> Dict:
    """
    获取多页PubMed搜索结果并整合到一个字典中
    
    Args:
        fetcher: PubMedFetcher实例
        query: 搜索查询字符串
        max_pages: 最大获取页数
        results_per_page: 每页结果数0
        sleep_time: 页面间暂停时间(秒)
        output_file: 可选的输出JSON文件路径
    
    Returns:
        包含所有文章和元数据的字典
    """
    all_results = {
        "papers": [],
        "metadata": {}
    }
    
    try:
        # 获取第一页以获取总结果数
        first_page = fetcher.search(
            query=query,
            max_results=results_per_page,
            start=0
        )
        
        total_results = first_page["metadata"]["total_results"]
        total_pages = min(max_pages, (total_results + results_per_page - 1) // results_per_page)
        
        print(f"找到 {total_results} 篇文章，将获取 {total_pages} 页")
        
        # 添加第一页结果
        all_results["papers"].extend(first_page["papers"])
        all_results["metadata"] = {
            "total_results": total_results,
            "pages_retrieved": total_pages,
            "results_per_page": results_per_page,
            "query": query,
            "total_papers_retrieved": len(first_page["papers"])
        }
        
        # 获取剩余页面
        if total_pages > 1:
            with tqdm(range(1, total_pages), desc="获取页面") as pbar:
                for page in pbar:
                    time.sleep(sleep_time)  # 在请求之间暂停
                    
                    start_index = page * results_per_page
                    try:
                        result = fetcher.search(
                            query=query,
                            max_results=results_per_page,
                            start=start_index
                        )
                        
                        all_results["papers"].extend(result["papers"])
                        all_results["metadata"]["total_papers_retrieved"] = len(all_results["papers"])
                        
                        pbar.set_postfix({
                            "已获取文章": len(all_results["papers"]),
                            "当前页文章数": len(result["papers"])
                        })
                        
                    except Exception as e:
                        print(f"\n获取第 {page + 1} 页时出错: {str(e)}")
                        continue
        
        # 如果指定了输出文件，保存结果
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_results, f, ensure_ascii=False, indent=2)
            print(f"\n结果已保存至: {output_file}")
        
        return all_results
        
    except Exception as e:
        print(f"获取过程中出错: {str(e)}")
        return all_results
    


def format_results(paper):    
    temp_df = pd.DataFrame()
    temp_df['title'] = [paper['title']]
    temp_df['pmid'] = [paper['pmid']]
    temp_df['journal'] = [paper['journal']['title']]
    authors = ""
    for author in paper['authors']:
        authors += f"{author['fore_name']} {author['last_name']}, "
        if author['affiliations']:
            temp_df['affiliations'] = [author['affiliations'][0]]
        else:
            temp_df['affiliations'] = [None]
    temp_df['authors'] = [authors]
    if paper['abstract']['structured']:
        for section, text in paper['abstract']['sections'].items():
            temp_df[section] = [text]
    else:
        temp_df['abstract'] = [paper['abstract']['complete']]
    
    if paper['keywords']:
        temp_df['keywords'] = [", ".join(paper['keywords'])]
    else:
        temp_df['keywords'] = [None]
    
    for url_type, url in paper['urls'].items():
        if url:
            temp_df[url_type] = [url]
    if paper['metadata']:
        temp_df['metadata'] = [paper['metadata']]
    else:
        temp_df['metadata'] = [None]
    
    temp_df['is_open_access'] = [paper['metadata']['is_open_access']]

    temp_df['fetch_time'] = [paper['metadata']['fetch_time']]
    return temp_df


def get_keywords(content, model="deepseek-chat"):
    PROMPT = """
            # 你的任务
            基于我下面提供的大模型给出的答案，提取核心科学问题有关的的关键词

            # 关键词要求
            - 关键词必须是英文
            - 关键词控制在5个以内
            - 涉及到药物的必须要有相关药物的关键词，比如：中药复方的名称、疾病、关键成分、关键靶点、具体通路名称等
            - 你的输出必须是JSON，key必须是"keywords"

            # 示例
            用户问题：冠心宁注射液（丹参、川芎）治疗心力衰竭（Heart Failure, HF）的系统药理学分析，包括关键成分、关键靶点和KEGG、WikiPathways通路，系统解读分析药理机制结果
            你的输出：
            ```json
            {{
            "keywords": ["Guanxinning Injection", "Heart Failure", "Tanshinone Compounds (e.g., Tanshinone IIA)"]
            }}
            ```

            # 内容
            {content}

            现在，请输出关键词JSON：

            """

    prompt = PROMPT.format(content=content)
    ans = ""
    for char in get_llm_answer(prompt, model, temperature=0.3):
        print(char, end="", flush=True)
        ans += char
    print()
    keywords = get_json(ans)["keywords"]
    return keywords


# 获取搜索结果文本。修改了检索方式，设置检索词，而不是原先for循环遍历关键词的模式    
def get_search_results(keywords):
    query = build_pubmed_query(keywords=keywords, start_year=2000, end_year=2025)
    print(query)
    fetcher = PubMedFetcher(api_key=os.getenv("PUBMED_API_KEY"))
    results = fetch_all_pages(
        fetcher,
        query=query,
        max_pages=5,
        results_per_page=100,
        sleep_time=3,
        output_file="files\pubmed_results.json"
    )
    # search_results_all获取每篇论文的标题及链接
    searched_results = ""
    for paper in results["papers"]:
        title = paper["title"]
        pubmed_url = paper["urls"]["pubmed"]
        searched_results += f"title：{title}\npubmed_url：{pubmed_url}\n===\n"
    if searched_results == "":
        searched_results = "未找到相关文献支持"
    return searched_results 



# 基于问题、AI回答、搜索结果文本，筛选出与问题相关的论文，展示论文标题及链接，markdown格式
def get_related_papers_yield(content, searched_results):
    SELECT_PAPER_PROMPT = """
                        # 你的任务
                        基于我下面提供的聊天记录中的最后一轮对话，筛选大模型推理中医药医学的答案相关的论文（最多5篇），以markdown格式展示论文标题及链接，
                        如果没有找到相关文献支持，则直接说明该没有查到相关文献,不要自己随意生成文献！
                        ### 聊天记录如下
                        {content}  

                        ### 搜索结果文本如下
                        {searched_results}

                        现在，请判断搜索结果中哪些论文与问题相关，以markdown格式展示论文标题及链接，示例格式：[论文标题](论文链接)
                        如有搜索结果你的输出格式如下：
                        # 相关论文
                        1. [论文标题][PMID: PMID号](论文链接)
                        2. [论文标题][PMID: PMID号](论文链接)
                        ...
                        如搜索结果文本中没有论文，直接说明没有查找到相关论文，返回“未找到相关论文”
                        """
    prompt = SELECT_PAPER_PROMPT.format(content=content, searched_results=searched_results)
    ans = ""
    for char in get_llm_answer(prompt, model="glm-4-plus", temperature=0.3):
        ans += char
        yield char 
    yield "\n"