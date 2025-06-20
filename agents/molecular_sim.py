from rdkit import Chem
from rdkit import DataStructs
from rdkit.Chem import AllChem
from rdkit.Chem.Fingerprints import FingerprintMols
from rdkit.Chem import MACCSkeys
from typing import Tuple, Dict, Optional
import numpy as np

class MolecularSimilarity:
    """用于计算分子相似度的类
    
    支持多种分子指纹类型和相似度计算方法
    """
    
    def __init__(self):
        # 支持的指纹类型
        self.fp_types = {
            'morgan': self._get_morgan_fp,
            'maccs': self._get_maccs_fp,
            'topological': self._get_topological_fp,
            'atom_pairs': self._get_atom_pairs_fp
        }
        
        # 支持的相似度计算方法
        self.similarity_metrics = {
            'tanimoto': DataStructs.TanimotoSimilarity,
            'dice': DataStructs.DiceSimilarity,
            'cosine': DataStructs.CosineSimilarity,
            'sokal': DataStructs.SokalSimilarity,
            'russel': DataStructs.RusselSimilarity
        }

    def _smiles_to_mol(self, smiles: str) -> Optional[Chem.Mol]:
        """将SMILES转换为RDKit分子对象
        
        Args:
            smiles: SMILES格式的分子结构式
            
        Returns:
            RDKit分子对象，如果转换失败则返回None
        """
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError(f"无法解析SMILES: {smiles}")
        return mol

    def _get_morgan_fp(self, mol: Chem.Mol, radius: int = 2, nBits: int = 2048) -> DataStructs.ExplicitBitVect:
        """计算Morgan指纹(ECFP)"""
        return AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=nBits)

    def _get_maccs_fp(self, mol: Chem.Mol) -> DataStructs.ExplicitBitVect:
        """计算MACCS指纹"""
        return MACCSkeys.GenMACCSKeys(mol)

    def _get_topological_fp(self, mol: Chem.Mol, nBits: int = 2048) -> DataStructs.ExplicitBitVect:
        """计算拓扑指纹"""
        return FingerprintMols.FingerprintMol(mol)

    def _get_atom_pairs_fp(self, mol: Chem.Mol) -> DataStructs.ExplicitBitVect:
        """计算原子对指纹"""
        return AllChem.GetHashedAtomPairFingerprintAsBitVect(mol)

    def calculate_similarity(self, 
                           smiles1: str, 
                           smiles2: str, 
                           fp_type: str = 'morgan',
                           metric: str = 'tanimoto',
                           fp_params: Dict = None) -> float:
        """计算两个分子之间的相似度
        
        Args:
            smiles1: 第一个分子的SMILES
            smiles2: 第二个分子的SMILES
            fp_type: 指纹类型，可选['morgan', 'maccs', 'topological', 'atom_pairs']
            metric: 相似度度量方法，可选['tanimoto', 'dice', 'cosine', 'sokal', 'russel']
            fp_params: 指纹生成的额外参数，例如Morgan指纹的radius和nBits
            
        Returns:
            相似度得分(0-1之间的浮点数)
        """
        # 参数检查
        if fp_type not in self.fp_types:
            raise ValueError(f"不支持的指纹类型: {fp_type}")
        if metric not in self.similarity_metrics:
            raise ValueError(f"不支持的相似度计算方法: {metric}")
            
        # 转换SMILES到分子对象
        mol1 = self._smiles_to_mol(smiles1)
        mol2 = self._smiles_to_mol(smiles2)
        
        # 生成指纹
        if fp_params is None:
            fp_params = {}
        fp1 = self.fp_types[fp_type](mol1, **fp_params)
        fp2 = self.fp_types[fp_type](mol2, **fp_params)
        
        # 计算相似度
        similarity = self.similarity_metrics[metric](fp1, fp2)
        
        return similarity

    def get_all_similarities(self, 
                           smiles1: str, 
                           smiles2: str, 
                           fp_type: str = 'morgan') -> Dict[str, float]:
        """使用所有支持的相似度度量方法计算两个分子的相似度
        
        Args:
            smiles1: 第一个分子的SMILES
            smiles2: 第二个分子的SMILES
            fp_type: 指纹类型
            
        Returns:
            包含所有相似度度量结果的字典
        """
        results = {}
        for metric in self.similarity_metrics:
            results[metric] = self.calculate_similarity(smiles1, smiles2, fp_type, metric)
        return results

    def compare_fp_types(self, 
                        smiles1: str, 
                        smiles2: str, 
                        metric: str = 'tanimoto') -> Dict[str, float]:
        """使用所有支持的指纹类型计算两个分子的相似度
        
        Args:
            smiles1: 第一个分子的SMILES
            smiles2: 第二个分子的SMILES
            metric: 相似度度量方法
            
        Returns:
            包含所有指纹类型计算结果的字典
        """
        results = {}
        for fp_type in self.fp_types:
            results[fp_type] = self.calculate_similarity(smiles1, smiles2, fp_type, metric)
        return results

# 使用示例
def get_all_similarities(SMILES1, SMILES2):

    # 创建计算器实例
    calculator = MolecularSimilarity()
    
    results_info = ""
    # 使用默认参数计算相似度
    similarity = calculator.calculate_similarity(SMILES1, SMILES2)
    results_info += f"默认相似度(Morgan指纹, Tanimoto): {similarity:.2%}\n"
    
    # 计算所有相似度度量方法的结果
    all_similarities = calculator.get_all_similarities(SMILES1, SMILES2)
    results_info += "\n所有相似度度量方法的结果:\n"
    for metric, score in all_similarities.items():
        results_info += f"{metric}: {score:.2%}\n"
    
    # 比较不同指纹类型的结果
    fp_comparisons = calculator.compare_fp_types(SMILES1, SMILES2)
    results_info += "\n不同指纹类型的结果:\n"
    for fp_type, score in fp_comparisons.items():
        results_info += f"{fp_type}: {score:.2%}\n"

    return results_info

# 示例分子SMILES
if __name__ == "__main__":
    curcumin = "COc1cc(/C=C/C(=O)CC(=O)/C=C/c2ccc(O)c(OC)c2)ccc1O"  # 姜黄素
    baicalein = "O=c1cc(-c2ccccc2)oc2cc(O)c(O)c(O)c12"  # 黄芩素
    results_info = get_all_similarities(curcumin, baicalein)
