#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Jina Embeddings v4 模型管理器
负责模型下载、加载和文本向量化
"""

import os
import numpy as np
from typing import List, Union
from pathlib import Path
import torch
from transformers import AutoModel
from tqdm import tqdm
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JinaEmbeddingManager:
    """Jina Embeddings v4 模型管理器"""
    
    def __init__(self, model_name: str = "jinaai/jina-embeddings-v4", 
                 cache_dir: str = None, device: str = None):
        """
        初始化Jina Embedding管理器
        
        Args:
            model_name: 模型名称
            cache_dir: 缓存目录
            device: 设备类型 ('cuda', 'cpu', None自动选择)
        """
        self.model_name = model_name
        
        # 使用项目本地的缓存目录
        if cache_dir is None:
            from config.config import EMBEDDING_CONFIG
            self.cache_dir = str(EMBEDDING_CONFIG["model_path"])
        else:
            self.cache_dir = cache_dir
        
        # 自动选择设备 - 优先使用GPU
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        self.model = None
        
        logger.info(f"🚀 初始化Jina Embedding管理器")
        logger.info(f"📱 设备: {self.device}")
        if self.device == "cuda":
            logger.info(f"🎮 GPU: {torch.cuda.get_device_name(0)}")
        logger.info(f"🔤 模型: {model_name}")
        logger.info(f"📁 缓存目录: {self.cache_dir}")
    
    def download_and_load_model(self) -> bool:
        """
        下载并加载模型
        
        Returns:
            bool: 是否成功加载
        """
        try:
            logger.info(f"📥 开始加载模型: {self.model_name}")
            
            # 设置环境变量强制禁用FlashAttention
            os.environ['FLASH_ATTENTION_FORCE_DISABLE'] = '1'
            
            # 使用官方推荐的方式加载模型
            self.model = AutoModel.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                cache_dir=self.cache_dir,
                attn_implementation="eager"  # 强制使用eager attention
            )
            
            # 移动到指定设备
            self.model = self.model.to(self.device)
            self.model.eval()  # 设置为评估模式
            
            logger.info(f"✅ 模型加载成功！")
            logger.info(f"📊 模型参数量: {sum(p.numel() for p in self.model.parameters()):,}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 模型加载失败: {str(e)}")
            return False
    
    def encode_texts(self, texts: Union[str, List[str]], 
                    task: str = "retrieval",
                    prompt_name: str = "passage",
                    batch_size: int = 32, 
                    show_progress: bool = True) -> np.ndarray:
        """
        将文本编码为向量 - 使用官方API
        
        Args:
            texts: 单个文本或文本列表
            task: 任务类型 ("retrieval", "text-matching", "code")
            prompt_name: 提示名称 ("query", "passage")
            batch_size: 批处理大小
            show_progress: 是否显示进度条
            
        Returns:
            np.ndarray: 文本向量数组
        """
        if self.model is None:
            raise ValueError("模型未加载，请先调用 download_and_load_model()")
        
        # 处理单个文本的情况
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = []
        
        # 批处理编码
        batches = [texts[i:i + batch_size] for i in range(0, len(texts), batch_size)]
        
        with torch.no_grad():
            for batch in tqdm(batches, desc="🔄 编码文本", disable=not show_progress):
                try:
                    # 使用官方API进行编码
                    batch_embeddings = self.model.encode_text(
                        texts=batch,
                        task=task,
                        prompt_name=prompt_name
                    )
                    
                    # encode_text返回的是list，需要处理每个元素
                    if isinstance(batch_embeddings, list):
                        # 转换list中的每个tensor
                        numpy_batch = []
                        for emb in batch_embeddings:
                            if isinstance(emb, torch.Tensor):
                                numpy_batch.append(emb.detach().cpu().numpy())
                            else:
                                numpy_batch.append(emb)
                        batch_embeddings = np.array(numpy_batch)
                    elif isinstance(batch_embeddings, torch.Tensor):
                        batch_embeddings = batch_embeddings.detach().cpu().numpy()
                    
                    embeddings.append(batch_embeddings)
                    
                except Exception as e:
                    logger.error(f"❌ 批次编码失败: {str(e)}")
                    raise
        
        # 合并所有批次的结果
        if embeddings:
            # 确保所有embeddings都是numpy数组
            numpy_embeddings = []
            for emb in embeddings:
                if isinstance(emb, torch.Tensor):
                    numpy_embeddings.append(emb.cpu().numpy())
                else:
                    numpy_embeddings.append(emb)
            
            result = np.vstack(numpy_embeddings)
            logger.info(f"✅ 编码完成，形状: {result.shape}")
            return result
        else:
            raise ValueError("编码失败，没有生成任何向量")
    
    def encode_query(self, query: str) -> np.ndarray:
        """
        编码查询文本
        
        Args:
            query: 查询文本
            
        Returns:
            np.ndarray: 查询向量
        """
        return self.encode_texts(
            texts=[query],
            task="retrieval",
            prompt_name="query",
            show_progress=False
        )[0]
    
    def encode_passages(self, passages: List[str], 
                       batch_size: int = 32,
                       show_progress: bool = True) -> np.ndarray:
        """
        编码文档段落
        
        Args:
            passages: 文档段落列表
            batch_size: 批处理大小
            show_progress: 是否显示进度条
            
        Returns:
            np.ndarray: 文档向量数组
        """
        return self.encode_texts(
            texts=passages,
            task="retrieval", 
            prompt_name="passage",
            batch_size=batch_size,
            show_progress=show_progress
        )
    
    def encode_for_matching(self, texts: List[str],
                           batch_size: int = 32,
                           show_progress: bool = True) -> np.ndarray:
        """
        编码文本用于匹配任务
        
        Args:
            texts: 文本列表
            batch_size: 批处理大小
            show_progress: 是否显示进度条
            
        Returns:
            np.ndarray: 文本向量数组
        """
        return self.encode_texts(
            texts=texts,
            task="text-matching",
            batch_size=batch_size,
            show_progress=show_progress
        )
    
    def get_embedding_dimension(self) -> int:
        """
        获取向量维度
        
        Returns:
            int: 向量维度
        """
        if self.model is None:
            raise ValueError("模型未加载")
        
        # 使用一个测试文本获取维度
        test_embedding = self.encode_texts(
            texts=["test"], 
            task="retrieval", 
            prompt_name="passage",
            show_progress=False
        )
        return test_embedding.shape[1]
    
    def calculate_similarity(self, embedding1: np.ndarray, 
                           embedding2: np.ndarray) -> float:
        """
        计算两个向量的余弦相似度
        
        Args:
            embedding1: 向量1
            embedding2: 向量2
            
        Returns:
            float: 相似度分数
        """
        from sklearn.metrics.pairwise import cosine_similarity
        
        # 确保向量是二维的
        if embedding1.ndim == 1:
            embedding1 = embedding1.reshape(1, -1)
        if embedding2.ndim == 1:
            embedding2 = embedding2.reshape(1, -1)
            
        similarity = cosine_similarity(embedding1, embedding2)[0][0]
        return float(similarity)
    
    def is_model_loaded(self) -> bool:
        """检查模型是否已加载"""
        return self.model is not None
    
    def get_model_info(self) -> dict:
        """获取模型信息"""
        if self.model is None:
            return {"loaded": False}
        
        return {
            "loaded": True,
            "model_name": self.model_name,
            "device": self.device,
            "parameter_count": sum(p.numel() for p in self.model.parameters()),
            "embedding_dimension": self.get_embedding_dimension()
        }

def get_embedding_manager() -> JinaEmbeddingManager:
    """
    获取全局的embedding管理器实例
    
    Returns:
        JinaEmbeddingManager: embedding管理器实例
    """
    if not hasattr(get_embedding_manager, '_instance'):
        get_embedding_manager._instance = JinaEmbeddingManager()
        
        # 自动加载模型
        if not get_embedding_manager._instance.download_and_load_model():
            raise RuntimeError("无法加载embedding模型")
    
    return get_embedding_manager._instance

 