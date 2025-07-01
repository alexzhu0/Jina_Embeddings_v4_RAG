#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
基于Sentence-Transformers的Jina Embeddings v4管理器
支持GPU优化，使用SDPA加速
"""

import os
import numpy as np
from typing import List, Union, Optional
from pathlib import Path
import logging
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm
import torch

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JinaEmbeddingManagerST:
    """基于Sentence-Transformers的Jina Embedding管理器"""
    
    def __init__(self, model_name: str = "jinaai/jina-embeddings-v4", 
                 cache_dir: str = None, device: str = None, 
                 attn_implementation: str = "sdpa"):
        """
        初始化Jina Embedding管理器
        
        Args:
            model_name: 模型名称
            cache_dir: 缓存目录
            device: 设备 ('cuda', 'cpu', 或 None 自动检测)
            attn_implementation: attention实现 ('sdpa', 'eager', 'flash_attention_2')
        """
        self.model_name = model_name
        self.cache_dir = cache_dir or "./models/jina-embeddings-v4"
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.attn_implementation = attn_implementation
        self.model = None
        
        logger.info(f"初始化Jina Embedding管理器")
        logger.info(f"模型: {self.model_name}")
        logger.info(f"设备: {self.device}")
        logger.info(f"缓存目录: {self.cache_dir}")
        logger.info(f"Attention实现: {self.attn_implementation}")
        
        self._load_model()
    
    def _load_model(self):
        """加载模型"""
        try:
            logger.info("正在加载模型...")
            
            # 设置模型配置
            model_kwargs = {
                "trust_remote_code": True,
                "device": self.device,
                "model_kwargs": {"attn_implementation": self.attn_implementation}
            }
            
            # 如果指定了缓存目录，使用本地缓存
            if self.cache_dir and os.path.exists(self.cache_dir):
                model_kwargs["cache_folder"] = self.cache_dir
                logger.info(f"使用本地缓存: {self.cache_dir}")
            
            logger.info(f"使用 {self.attn_implementation} attention (GPU加速)")
            
            self.model = SentenceTransformer(self.model_name, **model_kwargs)
            
            logger.info(f"✅ 模型加载成功")
            logger.info(f"模型设备: {self.model.device}")
            
        except Exception as e:
            logger.error(f"❌ 模型加载失败: {e}")
            raise
    
    def encode_texts(self, texts: List[str], task: str = "text-matching", 
                    prompt_name: str = None, batch_size: int = 32) -> np.ndarray:
        """
        编码文本列表
        
        Args:
            texts: 文本列表
            task: 任务类型 ('retrieval', 'text-matching', 'code')
            prompt_name: 提示名称 ('query', 'passage')
            batch_size: 批处理大小
            
        Returns:
            embeddings: 嵌入向量数组
        """
        if not self.model:
            raise ValueError("模型未加载")
        
        try:
            encode_kwargs = {
                "sentences": texts,
                "task": task,
                "batch_size": batch_size,
                "show_progress_bar": True
            }
            
            # 只在retrieval和code任务中使用prompt_name
            if prompt_name and task in ["retrieval", "code"]:
                encode_kwargs["prompt_name"] = prompt_name
            
            embeddings = self.model.encode(**encode_kwargs)
            
            logger.info(f"✅ 编码完成: {len(texts)} 个文本, 形状: {embeddings.shape}")
            return embeddings
            
        except Exception as e:
            logger.error(f"❌ 编码失败: {e}")
            raise
    
    def encode_query(self, queries: List[str], task: str = "retrieval") -> np.ndarray:
        """编码查询"""
        return self.encode_texts(queries, task=task, prompt_name="query")
    
    def encode_passages(self, passages: List[str], task: str = "retrieval") -> np.ndarray:
        """编码段落"""
        return self.encode_texts(passages, task=task, prompt_name="passage")
    
    def compute_similarity(self, embeddings1: np.ndarray, embeddings2: np.ndarray) -> np.ndarray:
        """计算余弦相似度"""
        return cosine_similarity(embeddings1, embeddings2)
    
    def batch_similarity(self, texts1: List[str], texts2: List[str], 
                        task: str = "text-matching") -> np.ndarray:
        """批量计算文本相似度"""
        embeddings1 = self.encode_texts(texts1, task=task)
        embeddings2 = self.encode_texts(texts2, task=task)
        return self.compute_similarity(embeddings1, embeddings2)
    
    def find_most_similar(self, query: str, candidates: List[str], 
                         task: str = "retrieval", top_k: int = 5) -> List[tuple]:
        """
        找到最相似的候选文本
        
        Args:
            query: 查询文本
            candidates: 候选文本列表
            task: 任务类型
            top_k: 返回前k个结果
            
        Returns:
            List of (index, text, similarity_score) tuples
        """
        query_embedding = self.encode_query([query], task=task)
        candidate_embeddings = self.encode_passages(candidates, task=task)
        
        similarities = self.compute_similarity(query_embedding, candidate_embeddings)[0]
        
        # 获取top_k个最相似的结果
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append((idx, candidates[idx], similarities[idx]))
        
        return results

# 便捷函数
def create_jina_embedding_manager(cache_dir: str = None, attn_implementation: str = "sdpa") -> JinaEmbeddingManagerST:
    """创建Jina Embedding管理器的便捷函数"""
    return JinaEmbeddingManagerST(
        cache_dir=cache_dir or "./models/jina-embeddings-v4",
        attn_implementation=attn_implementation
    )

if __name__ == "__main__":
    # 测试代码
    print("测试Jina Embeddings v4管理器...")
    
    # 创建管理器
    manager = create_jina_embedding_manager()
    
    # 测试文本编码
    texts = [
        "Hello world",
        "你好世界", 
        "Bonjour le monde"
    ]
    
    embeddings = manager.encode_texts(texts, task="text-matching")
    print(f"编码结果形状: {embeddings.shape}")
    
    # 测试相似度计算
    similarities = manager.compute_similarity(embeddings, embeddings)
    print(f"相似度矩阵:\n{similarities}")
    
    print("✅ 测试完成！") 