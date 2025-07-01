#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
政府工作报告RAG系统配置文件示例
复制此文件为 config.py 并填入您的实际配置
"""

import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 硅基流动API配置
SILICONFLOW_CONFIG = {
    "api_key": "your-api-key-here",  # 请替换为您的硅基流动API密钥
    "base_url": "https://api.siliconflow.cn/v1",
    "model": "Tongyi-Zhiwen/QwenLong-L1-32B",  # 使用支持更长上下文的模型
    "temperature": 0.3,  # 降低温度以获得更准确的数据输出
    "max_tokens": 8192,  # 调整为模型支持的最大值8192
    "timeout": 180  # 进一步增加超时时间到180秒，适应长上下文处理
}

# Embedding模型配置
EMBEDDING_CONFIG = {
    "model_name": "jinaai/jina-embeddings-v4",
    "model_path": PROJECT_ROOT / "models" / "jina-embeddings-v4",
    "max_length": 8192,
    "trust_remote_code": True,
    "device": "cuda"  # 使用GPU，如果没有GPU可改为"cpu"
}

# 数据路径配置
DATA_PATHS = {
    "raw_documents": r"您的文档路径",  # 请替换为您的政府工作报告文档路径
    "processed_data": PROJECT_ROOT / "data" / "processed",
    "vector_store": PROJECT_ROOT / "data" / "vectors",
    "models": PROJECT_ROOT / "models"
}

# 文档处理配置
DOCUMENT_CONFIG = {
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "min_chunk_length": 100
}

# RAG检索配置（已优化）
RETRIEVAL_CONFIG = {
    "top_k": 60,  # 从20增加到60，提升通用检索能力
    "similarity_threshold": 0.7,
    "max_contexts_per_query": 100000,  # 大幅增加到100K字符，充分利用长上下文
    
    # 单省份查询配置
    "single_province": {
        "top_k_per_province": 30,  # 从10增加到30个块，确保信息完整
        "max_chars": 40000  # 从12000增加到40000字符
    },
    
    # 多省份查询配置
    "multi_province": {
        "top_k_per_province": 15,  # 从6增加到15个块
        "max_chars": 60000  # 从15000增加到60000字符
    },
    
    # 全省份查询配置
    "all_provinces": {
        "top_k_per_province": 8,  # 从3增加到8个块，31省份共248个块
        "max_chars": 80000  # 从20000增加到80000字符
    },
    
    # 对比查询配置
    "comparison": {
        "top_k_per_province": 25,  # 从8增加到25个块
        "max_total": 150,  # 从50增加到150个块
        "max_chars": 100000  # 从18000增加到100000字符
    },
    
    # 主题查询配置
    "topic": {
        "top_k": 120,  # 从60增加到120个块
        "max_chars": 80000  # 从16000增加到80000字符
    }
}

# 查询处理配置
QUERY_CONFIG = {
    "batch_size": 8,  # 每批处理的省份数量
    "max_retries": 3,
    "timeout": 120  # 从30秒增加到120秒，适应长上下文处理
}

# 省份列表
PROVINCES = [
    "北京", "天津", "河北", "山西", "内蒙古", "辽宁", "吉林", "黑龙江",
    "上海", "江苏", "浙江", "安徽", "福建", "江西", "山东", "河南",
    "湖北", "湖南", "广东", "广西", "海南", "重庆", "四川", "贵州",
    "云南", "西藏", "陕西", "甘肃", "青海", "宁夏", "新疆"
]

# 创建必要的目录
def ensure_directories():
    """确保所有必要的目录存在"""
    for path in DATA_PATHS.values():
        if isinstance(path, Path):
            path.mkdir(parents=True, exist_ok=True) 