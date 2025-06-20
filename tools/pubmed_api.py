import requests
from time import sleep
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional, Union
from datetime import datetime
import logging
from ratelimit import limits, sleep_and_retry
import os
from dotenv import load_dotenv
import time

# 加载环境变量
load_dotenv()

# 设置日志级别
logging.basicConfig(level=logging.INFO)

class PubMedFetcher:
    """
    PubMed论文检索和数据获取类
    
    提供了完整的PubMed论文检索功能，包括:
    - 基于关键词的论文搜索
    - 完整摘要获取
    - 详细的元数据提取
    - 请求频率限制
    - 错误处理和重试机制
    """
    
    # PubMed API 每秒最多允许3个请求
    REQUESTS_PER_SECOND = 3
    
    def __init__(self, api_key: str, logger: Optional[logging.Logger] = None):
        """
        初始化PubMedFetcher
        
        Args:
            api_key: PubMed API密钥
            logger: 可选的日志记录器
        """
        self.api_key = api_key
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.logger = logger or logging.getLogger(__name__)
        
        # 配置日志格式
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    @sleep_and_retry
    @limits(calls=REQUESTS_PER_SECOND, period=1)
    def _make_request(self, endpoint: str, params: Dict) -> requests.Response:
        """
        发送API请求，包含频率限制和重试机制
        
        Args:
            endpoint: API端点
            params: 请求参数
        
        Returns:
            requests.Response对象
        
        Raises:
            requests.exceptions.RequestException: 当请求失败时
        """
        url = f"{self.base_url}/{endpoint}"
        params["api_key"] = self.api_key
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API请求失败: {str(e)}")
            raise

    def _get_complete_abstract(self, article: ET.Element) -> Dict[str, str]:
        """
        从文章XML中提取完整的摘要信息
        
        Args:
            article: XML文章元素
        
        Returns:
            包含完整摘要信息的字典，包括结构化和非结构化部分
        """
        abstract_info = {
            "complete": "",
            "structured": False,
            "sections": {}
        }
        
        abstract = article.find(".//Abstract")
        if abstract is None:
            return abstract_info
            
        abstract_parts = []
        
        # 处理结构化摘要
        for abstract_text in abstract.findall("AbstractText"):
            label = abstract_text.get("Label")
            nlm_category = abstract_text.get("NlmCategory")
            text = abstract_text.text or ""
            
            if label or nlm_category:
                abstract_info["structured"] = True
                section_title = label or nlm_category
                abstract_info["sections"][section_title] = text
                abstract_parts.append(f"{section_title}: {text}")
            else:
                abstract_parts.append(text)
        
        # 处理非结构化摘要
        if not abstract_parts and abstract.text:
            abstract_parts.append(abstract.text)
            
        abstract_info["complete"] = "\n\n".join(filter(None, abstract_parts))
        return abstract_info

    def _extract_paper_info(self, article: ET.Element) -> Dict:
        """
        从文章XML中提取所有相关信息
        
        Args:
            article: XML文章元素
        
        Returns:
            包含文章完整信息的字典
        """
        try:
            # 提取基本信息
            pmid = article.find(".//PMID").text
            title = article.find(".//ArticleTitle").text or "无标题"
            
            # 提取作者信息
            authors = []
            author_list = article.findall(".//Author")
            for author in author_list:
                author_info = {}
                
                # 获取姓名
                last_name = author.find("LastName")
                fore_name = author.find("ForeName")
                author_info["last_name"] = last_name.text if last_name is not None else ""
                author_info["fore_name"] = fore_name.text if fore_name is not None else ""
                
                # 获取作者单位
                affiliations = []
                for aff in author.findall(".//Affiliation"):
                    if aff is not None and aff.text:
                        affiliations.append(aff.text)
                author_info["affiliations"] = affiliations
                
                authors.append(author_info)
            
            # 提取期刊信息
            journal_info = {}
            journal = article.find(".//Journal")
            if journal is not None:
                journal_info["title"] = journal.find("Title").text if journal.find("Title") is not None else ""
                journal_info["iso_abbreviation"] = journal.find("ISOAbbreviation").text if journal.find("ISOAbbreviation") is not None else ""
                
                # 提取发布日期
                pub_date = journal.find(".//PubDate")
                if pub_date is not None:
                    date_parts = {}
                    for elem in pub_date:
                        date_parts[elem.tag] = elem.text
                    journal_info["pub_date"] = date_parts
            
            # 提取DOI和其他ID
            article_ids = {}
            for id_elem in article.findall(".//ArticleId"):
                id_type = id_elem.get("IdType")
                if id_type:
                    article_ids[id_type] = id_elem.text
            
            # 获取完整摘要
            abstract_info = self._get_complete_abstract(article)
            

            # 提取关键词
            keywords = []
            for keyword in article.findall(".//Keyword"):
                if keyword.text:
                    keywords.append(keyword.text)
            
            # 组装完整的文章信息
            paper_info = {
                "pmid": pmid,
                "title": title,
                "authors": authors,
                "journal": journal_info,
                "abstract": abstract_info,
                "keywords": keywords,
                "article_ids": article_ids,
                "urls": {
                    "pubmed": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    "doi": f"https://doi.org/{article_ids.get('doi')}" if article_ids.get('doi') else None,
                    "pmc": f"https://www.ncbi.nlm.nih.gov/pmc/articles/{article_ids.get('pmc')}/" if article_ids.get('pmc') else None
                },
                "metadata": {
                    "is_open_access": any("Open Access" in pub_type.text 
                                       for pub_type in article.findall(".//PublicationType")),
                    "fetch_time": datetime.now().isoformat()
                }
            }
            
            return paper_info
            
        except Exception as e:
            self.logger.error(f"提取文章信息时出错 (PMID: {pmid if 'pmid' in locals() else 'unknown'}): {str(e)}")
            raise

    def search(self, 
              query: str, 
              max_results: int = 10,
              start: int = 0,  # 添加起始位置参数
              sort: str = "relevance",
              retries: int = 3) -> Dict:
        """
        搜索PubMed文章
        
        Args:
            query: 搜索查询字符串
            max_results: 每页返回结果数
            start: 起始位置
            sort: 排序方式 ("relevance", "pub_date")
            retries: 失败时的重试次数
            
        Returns:
            包含文章信息和搜索元数据的字典
        """
        papers = []
        attempt = 0
        
        while attempt < retries:
            try:
                # 执行搜索获取文章ID
                search_params = {
                    "db": "pubmed",
                    "term": query,
                    "retmax": max_results,
                    "retstart": start,  # 添加起始位置
                    "usehistory": "y",
                    "sort": "relevance" if sort == "relevance" else "pub+date"
                }
                
                search_response = self._make_request("esearch.fcgi", search_params)
                search_root = ET.fromstring(search_response.content)
                
                # 获取搜索结果的元数据
                total_results = int(search_root.find('.//Count').text)
                query_key = search_root.find('.//QueryKey').text
                web_env = search_root.find('.//WebEnv').text
                
                pmids = [id_elem.text for id_elem in search_root.findall('.//Id')]
                
                if not pmids:
                    self.logger.info("未找到相关文章")
                    return {
                        "papers": [],
                        "metadata": {
                            "total_results": 0,
                            "current_page": start // max_results + 1,
                            "results_per_page": max_results,
                            "query": query
                        }
                    }
                
                self.logger.info(f"找到 {len(pmids)} 篇文章")
                
                # 获取文章详细信息
                fetch_params = {
                    "db": "pubmed",
                    "id": ",".join(pmids),
                    "retmode": "xml"
                }
                
                fetch_response = self._make_request("efetch.fcgi", fetch_params)
                fetch_root = ET.fromstring(fetch_response.content)
                
                # 处理每篇文章
                for article in fetch_root.findall(".//PubmedArticle"):
                    try:
                        paper_info = self._extract_paper_info(article)
                        papers.append(paper_info)
                    except Exception as e:
                        self.logger.error(f"处理文章时出错: {str(e)}")
                        continue
                
                # 返回文章列表和元数据
                return {
                    "papers": papers,
                    "metadata": {
                        "total_results": total_results,
                        "current_page": start // max_results + 1,
                        "results_per_page": max_results,
                        "query": query,
                        "query_key": query_key,
                        "web_env": web_env
                    }
                }
                
            except Exception as e:
                attempt += 1
                if attempt < retries:
                    self.logger.warning(f"第 {attempt} 次尝试失败: {str(e)}，准备重试...")
                    sleep(2 ** attempt)  # 指数退避
                else:
                    self.logger.error(f"所有重试都失败: {str(e)}")
                    raise

    def get_paper_by_pmid(self, pmid: str) -> Optional[Dict]:
        """
        通过PMID获取单篇文章信息
        
        Args:
            pmid: PubMed文章ID
            
        Returns:
            包含文章信息的字典，如果未找到返回None
        """
        try:
            fetch_params = {
                "db": "pubmed",
                "id": pmid,
                "retmode": "xml"
            }
            
            response = self._make_request("efetch.fcgi", fetch_params)
            root = ET.fromstring(response.content)
            
            article = root.find(".//PubmedArticle")
            if article is not None:
                return self._extract_paper_info(article)
            else:
                self.logger.warning(f"未找到PMID为 {pmid} 的文章")
                return None
                
        except Exception as e:
            self.logger.error(f"获取文章信息失败 (PMID: {pmid}): {str(e)}")
            raise

# 使用示例
if __name__ == "__main__":
    fetcher = PubMedFetcher(api_key=os.getenv("PUBMED_API_KEY"))
    
    # 搜索参数
    query = "machine learning"
    results_per_page = 10
    max_pages = 100  # 获取前5页的结果
    sleep_time = 3  # 每页之间暂停3秒
    
    try:
        # 获取第一页结果以了解总结果数
        first_page = fetcher.search(query=query, max_results=results_per_page, start=0)
        total_results = first_page["metadata"]["total_results"]
        total_pages = min(max_pages, (total_results + results_per_page - 1) // results_per_page)
        
        print(f"共找到 {total_results} 篇文章，将获取 {total_pages} 页结果")
        
        # 处理第一页结果
        for paper in first_page["papers"]:
            print(f"\n处理文章: {paper['title']}")
            # 在这里处理文章数据...
        
        # 获取后续页面
        for page in range(1, total_pages):
            print(f"\n获取第 {page + 1} 页...")
            time.sleep(sleep_time)  # 在请求之间暂停
            
            start_index = page * results_per_page
            result = fetcher.search(
                query=query,
                max_results=results_per_page,
                start=start_index
            )
            
            for paper in result["papers"]:
                print(f"\n处理文章: {paper['title']}")
                # 在这里处理文章数据...
                
    except Exception as e:
        print(f"发生错误: {str(e)}")




