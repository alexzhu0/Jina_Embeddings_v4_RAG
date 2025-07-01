#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RAG检索引擎
负责智能检索、结果排序和上下文构建
"""

import re
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
import logging

from data_processor import DocumentChunk
from vector_store import get_vector_store
from api_client import get_api_client

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RetrievalResult:
    """检索结果数据结构"""
    chunks: List[DocumentChunk]
    provinces: Set[str]
    total_chars: int
    query_type: str
    retrieval_strategy: str

class RAGRetriever:
    """RAG检索引擎"""
    
    def __init__(self, vector_store=None):
        """
        初始化检索引擎
        
        Args:
            vector_store: 向量存储实例
        """
        self.vector_store = vector_store or get_vector_store()
        
        # 查询意图关键词
        self.intent_keywords = {
            "all_provinces": ["所有省份", "全部省份", "各省", "31省", "全国"],
            "single_province": [],  # 将通过省份名称动态识别
            "comparison": ["对比", "比较", "差异", "区别", "异同"],
            "statistics": ["统计", "数量", "总计", "汇总", "分析"],
            "targets": ["目标", "任务", "重点", "计划", "规划"],
            "economic": ["经济", "GDP", "产业", "发展", "增长"],
            "social": ["社会", "民生", "教育", "医疗", "就业"],
            "environment": ["环境", "生态", "绿色", "污染", "碳"]
        }
        
        # 省份名称列表（用于意图识别）
        from config.config import PROVINCES, RETRIEVAL_CONFIG
        self.provinces = PROVINCES
        self.config = RETRIEVAL_CONFIG
        
        logger.info("🔍 RAG检索引擎初始化完成")
    
    def get_adjacent_chunks(self, chunk: DocumentChunk, window: int = 1) -> List[DocumentChunk]:
        """
        获取指定文档块的相邻块
        
        Args:
            chunk: 目标文档块
            window: 前后窗口大小（默认前后各1个块）
            
        Returns:
            List[DocumentChunk]: 相邻块列表（不包含原始块）
        """
        try:
            # 获取同一文档的所有块
            same_doc_chunks = []
            for stored_chunk in self.vector_store.chunks:
                if (stored_chunk.source == chunk.source and 
                    stored_chunk.province == chunk.province):
                    same_doc_chunks.append(stored_chunk)
            
            # 按chunk_id排序
            same_doc_chunks.sort(key=lambda x: getattr(x, 'chunk_id', 0))
            
            # 找到目标块的位置
            target_index = -1
            for i, stored_chunk in enumerate(same_doc_chunks):
                if (stored_chunk.content == chunk.content and 
                    stored_chunk.start_pos == chunk.start_pos):
                    target_index = i
                    break
            
            if target_index == -1:
                logger.warning(f"⚠️ 未找到目标块的位置")
                return []
            
            # 获取相邻块
            adjacent_chunks = []
            start_idx = max(0, target_index - window)
            end_idx = min(len(same_doc_chunks), target_index + window + 1)
            
            for i in range(start_idx, end_idx):
                if i != target_index:  # 排除原始块
                    adjacent_chunks.append(same_doc_chunks[i])
            
            logger.debug(f"🔗 获取到 {len(adjacent_chunks)} 个相邻块")
            return adjacent_chunks
            
        except Exception as e:
            logger.warning(f"⚠️ 获取相邻块失败: {str(e)}")
            return []
    
    def identify_query_intent(self, query: str) -> Dict[str, any]:
        """
        识别查询意图
        
        Args:
            query: 查询文本
            
        Returns:
            Dict: 查询意图信息
        """
        intent = {
            "type": "general",
            "provinces": [],
            "topics": [],
            "scope": "general"
        }
        
        query_lower = query.lower()
        
        # 检查是否查询所有省份
        for keyword in self.intent_keywords["all_provinces"]:
            if keyword in query:
                intent["type"] = "all_provinces"
                intent["scope"] = "comprehensive"
                break
        
        # 检查特定省份
        mentioned_provinces = []
        for province in self.provinces:
            if province in query:
                mentioned_provinces.append(province)
        
        if mentioned_provinces:
            intent["provinces"] = mentioned_provinces
            if len(mentioned_provinces) == 1:
                intent["type"] = "single_province"
            else:
                intent["type"] = "multi_province"
        
        # 检查对比意图
        for keyword in self.intent_keywords["comparison"]:
            if keyword in query:
                intent["type"] = "comparison"
                break
        
        # 检查统计意图
        for keyword in self.intent_keywords["statistics"]:
            if keyword in query:
                intent["type"] = "statistics"
                break
        
        # 识别主题
        topics = []
        for topic, keywords in self.intent_keywords.items():
            if topic in ["targets", "economic", "social", "environment"]:
                for keyword in keywords:
                    if keyword in query:
                        topics.append(topic)
                        break
        
        intent["topics"] = topics
        
        logger.debug(f"🎯 查询意图: {intent}")
        return intent
    
    def retrieve_for_all_provinces(self, query: str, top_k_per_province: int = None) -> RetrievalResult:
        """
        为所有省份检索信息
        
        Args:
            query: 查询文本
            top_k_per_province: 每个省份返回的块数
            
        Returns:
            RetrievalResult: 检索结果
        """
        if top_k_per_province is None:
            top_k_per_province = self.config["all_provinces"]["top_k_per_province"]
            
        logger.info(f"🌏 为所有省份检索: {query} (每省{top_k_per_province}块)")
        
        all_chunks = []
        provinces_found = set()
        
        # 为每个省份单独检索
        for province in self.provinces:
            province_chunks = self.vector_store.search(
                query, 
                top_k=top_k_per_province * 4,  # 从3倍增加到4倍，搜索更多结果用于过滤
                province_filter=province
            )
            
            # 取前N个结果
            for chunk, score in province_chunks[:top_k_per_province]:
                all_chunks.append(chunk)
                provinces_found.add(province)
        
        total_chars = sum(chunk.char_count for chunk in all_chunks)
        
        logger.info(f"✅ 检索完成: {len(provinces_found)} 个省份, {len(all_chunks)} 个块")
        
        return RetrievalResult(
            chunks=all_chunks,
            provinces=provinces_found,
            total_chars=total_chars,
            query_type="all_provinces",
            retrieval_strategy="province_based"
        )
    
    def retrieve_for_specific_provinces(self, query: str, provinces: List[str], 
                                      top_k_per_province: int = None) -> RetrievalResult:
        """
        为特定省份检索信息
        
        Args:
            query: 查询文本
            provinces: 省份列表
            top_k_per_province: 每个省份返回的块数
            
        Returns:
            RetrievalResult: 检索结果
        """
        # 根据省份数量选择配置
        if top_k_per_province is None:
            if len(provinces) == 1:
                top_k_per_province = self.config["single_province"]["top_k_per_province"]
            else:
                top_k_per_province = self.config["multi_province"]["top_k_per_province"]
        
        logger.info(f"🎯 为特定省份检索: {provinces} (每省{top_k_per_province}块)")
        
        all_chunks = []
        provinces_found = set()
        
        for province in provinces:
            if province not in self.provinces:
                logger.warning(f"⚠️ 未知省份: {province}")
                continue
            
            province_chunks = self.vector_store.search(
                query,
                top_k=top_k_per_province * 3,  # 从2倍增加到3倍
                province_filter=province
            )
            
            for chunk, score in province_chunks[:top_k_per_province]:
                all_chunks.append(chunk)
                provinces_found.add(province)
        
        total_chars = sum(chunk.char_count for chunk in all_chunks)
        
        return RetrievalResult(
            chunks=all_chunks,
            provinces=provinces_found,
            total_chars=total_chars,
            query_type="specific_provinces",
            retrieval_strategy="targeted"
        )
    
    def retrieve_for_comparison(self, query: str, provinces: List[str] = None, 
                              top_k: int = None) -> RetrievalResult:
        """
        为对比分析检索信息
        
        Args:
            query: 查询文本
            provinces: 要对比的省份（可选）
            top_k: 返回结果数
            
        Returns:
            RetrievalResult: 检索结果
        """
        if top_k is None:
            top_k = self.config["comparison"]["max_total"]
        
        top_k_per_province = self.config["comparison"]["top_k_per_province"]
        
        logger.info(f"⚖️ 对比检索: {query} (每省{top_k_per_province}块)")
        
        if provinces:
            # 对比特定省份
            all_chunks = []
            provinces_found = set()
            
            for province in provinces:
                province_chunks = self.vector_store.search(
                    query,
                    top_k=top_k_per_province * 3,  # 从2倍增加到3倍，搜索更多用于筛选
                    province_filter=province
                )
                
                # 取前N个结果
                for chunk, score in province_chunks[:top_k_per_province]:
                    all_chunks.append(chunk)
                    provinces_found.add(province)
        else:
            # 全局对比检索
            search_results = self.vector_store.search(query, top_k=top_k)
            all_chunks = [chunk for chunk, score in search_results]
            provinces_found = set(chunk.province for chunk in all_chunks)
        
        total_chars = sum(chunk.char_count for chunk in all_chunks)
        
        return RetrievalResult(
            chunks=all_chunks,
            provinces=provinces_found,
            total_chars=total_chars,
            query_type="comparison",
            retrieval_strategy="comparative"
        )
    
    def retrieve_by_topic(self, query: str, chunk_type: str = "target", 
                         top_k: int = None) -> RetrievalResult:
        """
        按主题检索信息
        
        Args:
            query: 查询文本
            chunk_type: 块类型过滤
            top_k: 返回结果数
            
        Returns:
            RetrievalResult: 检索结果
        """
        if top_k is None:
            top_k = self.config["topic"]["top_k"]
            
        logger.info(f"📋 主题检索: {query} (类型: {chunk_type}, top_k={top_k})")
        
        search_results = self.vector_store.search(
            query,
            top_k=top_k,
            chunk_type_filter=chunk_type
        )
        
        all_chunks = [chunk for chunk, score in search_results]
        provinces_found = set(chunk.province for chunk in all_chunks)
        total_chars = sum(chunk.char_count for chunk in all_chunks)
        
        return RetrievalResult(
            chunks=all_chunks,
            provinces=provinces_found,
            total_chars=total_chars,
            query_type="topic",
            retrieval_strategy="topic_based"
        )
    
    def smart_retrieve(self, query: str, max_context_chars: int = None) -> RetrievalResult:
        """
        智能检索 - 根据查询意图选择最佳检索策略
        
        Args:
            query: 查询文本
            max_context_chars: 最大上下文字符数（可选，将根据查询类型自动选择）
            
        Returns:
            RetrievalResult: 检索结果
        """
        logger.info(f"🧠 智能检索: {query}")
        
        # 识别查询意图
        intent = self.identify_query_intent(query)
        
        # 根据意图选择检索策略和上下文限制
        if intent["type"] == "all_provinces":
            # 查询所有省份
            result = self.retrieve_for_all_provinces(query)
            if max_context_chars is None:
                max_context_chars = self.config["all_provinces"]["max_chars"]
        
        elif intent["type"] == "single_province":
            # 查询特定省份
            result = self.retrieve_for_specific_provinces(query, intent["provinces"])
            if max_context_chars is None:
                max_context_chars = self.config["single_province"]["max_chars"]
        
        elif intent["type"] == "multi_province":
            # 查询多个省份
            result = self.retrieve_for_specific_provinces(query, intent["provinces"])
            if max_context_chars is None:
                max_context_chars = self.config["multi_province"]["max_chars"]
        
        elif intent["type"] == "comparison":
            # 对比查询
            result = self.retrieve_for_comparison(query, intent["provinces"])
            if max_context_chars is None:
                max_context_chars = self.config["comparison"]["max_chars"]
        
        elif intent["type"] == "statistics":
            # 统计查询
            result = self.retrieve_by_topic(query, chunk_type="target")
            if max_context_chars is None:
                max_context_chars = self.config["topic"]["max_chars"]
        
        else:
            # 通用检索 - 大幅增加检索数量
            search_results = self.vector_store.search(query, top_k=60)  # 从25增加到60
            primary_chunks = [chunk for chunk, score in search_results]
            
            # 应用相邻块聚合策略
            enhanced_chunks = []
            seen_chunks = set()
            
            for chunk in primary_chunks:
                # 添加原始块
                chunk_key = (chunk.source, chunk.start_pos, chunk.content[:50])
                if chunk_key not in seen_chunks:
                    enhanced_chunks.append(chunk)
                    seen_chunks.add(chunk_key)
                
                # 获取相邻块并添加
                adjacent_chunks = self.get_adjacent_chunks(chunk, window=1)
                for adj_chunk in adjacent_chunks:
                    adj_key = (adj_chunk.source, adj_chunk.start_pos, adj_chunk.content[:50])
                    if adj_key not in seen_chunks:
                        enhanced_chunks.append(adj_chunk)
                        seen_chunks.add(adj_key)
            
            provinces_found = set(chunk.province for chunk in enhanced_chunks)
            total_chars = sum(chunk.char_count for chunk in enhanced_chunks)
            
            result = RetrievalResult(
                chunks=enhanced_chunks,
                provinces=provinces_found,
                total_chars=total_chars,
                query_type="general",
                retrieval_strategy="semantic_with_adjacent"
            )
            if max_context_chars is None:
                max_context_chars = self.config["max_contexts_per_query"]
        
        # 如果结果过长，进行截断
        if result.total_chars > max_context_chars:
            result = self._truncate_results(result, max_context_chars)
        
        logger.info(f"✅ 检索完成: {len(result.chunks)} 个块, {len(result.provinces)} 个省份, {result.total_chars} 字符")
        
        return result
    
    def _truncate_results(self, result: RetrievalResult, max_chars: int) -> RetrievalResult:
        """
        截断检索结果以适应上下文限制
        
        Args:
            result: 原始检索结果
            max_chars: 最大字符数
            
        Returns:
            RetrievalResult: 截断后的结果
        """
        if result.total_chars <= max_chars:
            return result
        
        logger.info(f"✂️ 截断结果: {result.total_chars} -> {max_chars} 字符")
        
        # 按省份平均分配字符数
        if result.query_type == "all_provinces":
            chars_per_province = max_chars // len(result.provinces)
            
            truncated_chunks = []
            province_chars = {}
            
            for chunk in result.chunks:
                province = chunk.province
                if province not in province_chars:
                    province_chars[province] = 0
                
                if province_chars[province] + chunk.char_count <= chars_per_province:
                    truncated_chunks.append(chunk)
                    province_chars[province] += chunk.char_count
        else:
            # 改进的截断策略：优先保留信息密度高的块
            # 按字符数与相关性的综合评分排序
            def chunk_score(chunk):
                # 综合评分：字符数适中且内容丰富的块得分更高
                char_score = min(chunk.char_count / 500, 2.0)  # 500字符左右得分最高
                content_score = len(chunk.content.split()) / 100  # 词数越多得分越高
                return char_score + content_score
            
            sorted_chunks = sorted(result.chunks, key=chunk_score, reverse=True)
            
            truncated_chunks = []
            current_chars = 0
            
            for chunk in sorted_chunks:
                if current_chars + chunk.char_count <= max_chars:
                    truncated_chunks.append(chunk)
                    current_chars += chunk.char_count
                else:
                    # 如果还有空间，尝试截取部分内容
                    remaining_chars = max_chars - current_chars
                    if remaining_chars > 200:  # 至少保留200字符才有意义
                        truncated_content = chunk.content[:remaining_chars-50] + "..."
                        truncated_chunk = DocumentChunk(
                            id=chunk.id + "_truncated",
                            province=chunk.province,
                            content=truncated_content,
                            chunk_type=chunk.chunk_type,
                            metadata=chunk.metadata,
                            char_count=len(truncated_content),
                            source=chunk.source,
                            start_pos=chunk.start_pos,
                            end_pos=chunk.start_pos + len(truncated_content),
                            chunk_id=chunk.chunk_id
                        )
                        truncated_chunks.append(truncated_chunk)
                    break
        
        return RetrievalResult(
            chunks=truncated_chunks,
            provinces=set(chunk.province for chunk in truncated_chunks),
            total_chars=sum(chunk.char_count for chunk in truncated_chunks),
            query_type=result.query_type,
            retrieval_strategy=result.retrieval_strategy + "_truncated"
        )
    
    def format_context(self, result: RetrievalResult) -> str:
        """
        格式化检索结果为上下文文本
        
        Args:
            result: 检索结果
            
        Returns:
            str: 格式化的上下文文本
        """
        if not result.chunks:
            return "未找到相关信息。"
        
        context_parts = []
        
        # 按省份分组
        province_chunks = {}
        for chunk in result.chunks:
            province = chunk.province
            if province not in province_chunks:
                province_chunks[province] = []
            province_chunks[province].append(chunk)
        
        # 格式化每个省份的信息
        for province, chunks in province_chunks.items():
            context_parts.append(f"\n=== {province} ===")
            
            for chunk in chunks:
                # 简化内容，移除多余的换行和空格
                content = re.sub(r'\s+', ' ', chunk.content.strip())
                context_parts.append(content)
        
        context = "\n".join(context_parts)
        
        logger.debug(f"📝 上下文格式化完成: {len(context)} 字符")
        
        return context

# 全局检索器实例
_retriever = None

def get_retriever() -> RAGRetriever:
    """获取全局检索器实例"""
    global _retriever
    if _retriever is None:
        _retriever = RAGRetriever()
    return _retriever

 