import requests
import time
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
import json

@dataclass
class CompoundInfo:
    cid: str
    molecular_formula: Optional[str] = None
    molecular_weight: Optional[float] = None
    iupac_name: Optional[str] = None
    synonyms: List[str] = None
    descriptions: List[Dict[str, str]] = None
    inchi: Optional[str] = None
    inchikey: Optional[str] = None
    canonical_smiles: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}

class PubChemAPI:
    """PubChem API客户端"""
    
    def __init__(self):
        self.base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 Chemical Information Retrieval Tool v1.0'
        }
        # 请求间隔（秒）
        self.request_delay = 0.2
        
    def _make_request(self, url: str) -> Dict:
        """发送API请求并处理响应"""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            time.sleep(self.request_delay)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {url}: {str(e)}")
            return {}

    def get_compound_properties(self, cid: str) -> Dict:
        """获取化合物的基本属性"""
        # 分开请求不同的属性组
        basic_properties = [
            "MolecularFormula",
            "MolecularWeight",
            "IUPACName"
        ]
        
        structure_properties = [
            "InChI",
            "InChIKey",
            "CanonicalSMILES"
        ]
        
        # 获取基本属性
        url_basic = f"{self.base_url}/compound/cid/{cid}/property/{','.join(basic_properties)}/JSON"
        basic_response = self._make_request(url_basic)
        
        # 获取结构属性
        url_structure = f"{self.base_url}/compound/cid/{cid}/property/{','.join(structure_properties)}/JSON"
        structure_response = self._make_request(url_structure)
        
        # 合并结果
        properties = {}
        if 'PropertyTable' in basic_response:
            properties.update(basic_response['PropertyTable'].get('Properties', [{}])[0])
        if 'PropertyTable' in structure_response:
            properties.update(structure_response['PropertyTable'].get('Properties', [{}])[0])
            
        return properties

    def get_compound_synonyms(self, cid: str) -> List[str]:
        """获取化合物的同义词"""
        url = f"{self.base_url}/compound/cid/{cid}/synonyms/JSON"
        response = self._make_request(url)
        if 'InformationList' in response:
            info = response['InformationList'].get('Information', [{}])[0]
            return info.get('Synonym', [])
        return []

    def get_compound_descriptions(self, cid: str) -> List[Dict[str, str]]:
        """获取化合物的描述信息"""
        url = f"{self.base_url}/compound/cid/{cid}/description/JSON"
        response = self._make_request(url)
        descriptions = []
        description = response["InformationList"]["Information"][1]["Description"]
        DescriptionSourceName = response["InformationList"]["Information"][1]["DescriptionSourceName"]
        descriptions.append({"source": DescriptionSourceName, "description": description})
        return descriptions

    def get_compound_info(self, cid: str) -> CompoundInfo:
        """获取化合物的完整信息"""
        # 获取基本属性
        properties = self.get_compound_properties(cid)
        
        # 获取同义词
        # synonyms = self.get_compound_synonyms(cid)
        
        # 获取描述
        descriptions = self.get_compound_descriptions(cid)
        # 创建CompoundInfo对象
        return CompoundInfo(
            cid=cid,
            molecular_formula=properties.get('MolecularFormula'),
            molecular_weight=properties.get('MolecularWeight'),
            iupac_name=properties.get('IUPACName'),
            # synonyms=synonyms,
            descriptions=descriptions,
            inchi=properties.get('InChI'),
            inchikey=properties.get('InChIKey'),
            canonical_smiles=properties.get('CanonicalSMILES')
        )

    def save_compound_info(self, cid: str, output_file: str):
        """获取化合物信息并保存到文件"""
        info = self.get_compound_info(cid)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(info.to_dict(), f, indent=2, ensure_ascii=False)

