#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
政府工作报告文档处理器
负责Word文档解析、文本提取、省份识别和分段处理
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
import logging

# 导入文档处理库
from docx import Document
import jieba
from tqdm import tqdm

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DocumentChunk:
    """文档块数据结构"""
    id: str
    province: str
    content: str
    chunk_type: str  # 'title', 'content', 'target', 'summary'
    metadata: Dict
    char_count: int
    source: str = ""  # 添加source属性
    start_pos: int = 0  # 添加start_pos属性
    end_pos: int = 0  # 添加end_pos属性
    chunk_id: int = 0  # 添加chunk_id属性
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return asdict(self)

class GovernmentReportProcessor:
    """政府工作报告处理器"""
    
    def __init__(self, raw_documents_path: str, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        初始化文档处理器
        
        Args:
            raw_documents_path: 原始文档路径
            chunk_size: 分块大小
            chunk_overlap: 分块重叠大小
        """
        self.raw_documents_path = Path(raw_documents_path)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # 省份识别模式
        self.province_patterns = {
            "北京": ["北京", "京"],
            "天津": ["天津", "津"],
            "河北": ["河北", "冀"],
            "山西": ["山西", "晋"],
            "内蒙古": ["内蒙古", "内蒙", "蒙"],
            "辽宁": ["辽宁", "辽"],
            "吉林": ["吉林", "吉"],
            "黑龙江": ["黑龙江", "黑"],
            "上海": ["上海", "沪"],
            "江苏": ["江苏", "苏"],
            "浙江": ["浙江", "浙"],
            "安徽": ["安徽", "皖"],
            "福建": ["福建", "闽"],
            "江西": ["江西", "赣"],
            "山东": ["山东", "鲁"],
            "河南": ["河南", "豫"],
            "湖北": ["湖北", "鄂"],
            "湖南": ["湖南", "湘"],
            "广东": ["广东", "粤"],
            "广西": ["广西", "桂"],
            "海南": ["海南", "琼"],
            "重庆": ["重庆", "渝"],
            "四川": ["四川", "川", "蜀"],
            "贵州": ["贵州", "黔", "贵"],
            "云南": ["云南", "滇", "云"],
            "西藏": ["西藏", "藏"],
            "陕西": ["陕西", "陕", "秦"],
            "甘肃": ["甘肃", "甘", "陇"],
            "青海": ["青海", "青"],
            "宁夏": ["宁夏", "宁"],
            "新疆": ["新疆", "新"]
        }
        
        # 关键词模式（用于识别重要内容）
        self.target_keywords = [
            "主要目标", "工作目标", "发展目标", "重点任务", "主要任务",
            "工作重点", "重点工作", "重点项目", "重大项目", "重大工程",
            "产业发展", "经济发展", "社会发展", "民生改善", "生态环境"
        ]
        
        logger.info(f"📁 文档处理器初始化完成")
        logger.info(f"📂 文档路径: {self.raw_documents_path}")
        logger.info(f"📏 分块大小: {chunk_size}")
    
    def extract_province_from_filename(self, filename: str) -> Optional[str]:
        """
        从文件名中提取省份信息
        
        Args:
            filename: 文件名
            
        Returns:
            Optional[str]: 省份名称
        """
        for province, patterns in self.province_patterns.items():
            for pattern in patterns:
                if pattern in filename:
                    return province
        return None
    
    def extract_province_from_content(self, content: str) -> Optional[str]:
        """
        从内容中提取省份信息
        
        Args:
            content: 文档内容
            
        Returns:
            Optional[str]: 省份名称
        """
        # 在文档开头部分搜索省份信息
        header_content = content[:1000]  # 只检查前1000字符
        
        for province, patterns in self.province_patterns.items():
            for pattern in patterns:
                if pattern in header_content:
                    return province
        return None
    
    def read_docx_file(self, file_path: Path) -> Tuple[str, Dict]:
        """
        读取Word文档内容
        
        Args:
            file_path: 文档路径
            
        Returns:
            Tuple[str, Dict]: (文档内容, 元数据)
        """
        try:
            doc = Document(file_path)
            
            # 提取文本内容
            paragraphs = []
            for paragraph in doc.paragraphs:
                text = paragraph.text.strip()
                if text:  # 跳过空段落
                    paragraphs.append(text)
            
            content = "\n".join(paragraphs)
            
            # 提取元数据
            metadata = {
                "filename": file_path.name,
                "file_size": file_path.stat().st_size,
                "paragraph_count": len(paragraphs),
                "char_count": len(content)
            }
            
            logger.debug(f"📄 读取文档: {file_path.name} ({metadata['char_count']} 字符)")
            
            return content, metadata
            
        except Exception as e:
            logger.error(f"❌ 读取文档失败 {file_path.name}: {str(e)}")
            return "", {}
    
    def identify_content_type(self, text: str) -> str:
        """
        识别内容类型
        
        Args:
            text: 文本内容
            
        Returns:
            str: 内容类型
        """
        text_lower = text.lower()
        
        # 检查是否包含目标关键词
        for keyword in self.target_keywords:
            if keyword in text:
                return "target"
        
        # 检查是否是标题（通常较短且包含特定格式）
        if len(text) < 100 and any(char in text for char in "一二三四五六七八九十"):
            return "title"
        
        # 检查是否是摘要（通常在文档开头）
        if "摘要" in text or "概述" in text or "总体" in text:
            return "summary"
        
        return "content"
    
    def split_text_into_chunks(self, text: str, province: str, metadata: Dict) -> List[DocumentChunk]:
        """
        将文本分割为块
        
        Args:
            text: 文本内容
            province: 省份名称
            metadata: 文档元数据
            
        Returns:
            List[DocumentChunk]: 文档块列表
        """
        chunks = []
        
        # 按段落分割
        paragraphs = text.split('\n')
        
        current_chunk = ""
        chunk_id = 0
        current_pos = 0
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # 检查添加这个段落是否会超过块大小限制
            if len(current_chunk) + len(paragraph) > self.chunk_size and current_chunk:
                # 创建当前块
                chunk_content = current_chunk.strip()
                chunk = DocumentChunk(
                    id=f"{province}_{chunk_id:03d}",
                    province=province,
                    content=chunk_content,
                    chunk_type=self.identify_content_type(chunk_content),
                    metadata={
                        **metadata,
                        "chunk_index": chunk_id,
                        "paragraph_start": max(0, len(current_chunk) - self.chunk_overlap)
                    },
                    char_count=len(chunk_content),
                    source=metadata.get("filename", ""),
                    start_pos=current_pos,
                    end_pos=current_pos + len(chunk_content),
                    chunk_id=chunk_id
                )
                chunks.append(chunk)
                
                # 更新位置
                current_pos += len(chunk_content)
                
                # 开始新块（保留重叠部分）
                if self.chunk_overlap > 0 and len(current_chunk) > self.chunk_overlap:
                    overlap_text = current_chunk[-self.chunk_overlap:]
                    current_chunk = overlap_text + "\n" + paragraph
                    current_pos -= len(overlap_text)  # 回退重叠部分的位置
                else:
                    current_chunk = paragraph
                
                chunk_id += 1
            else:
                # 添加到当前块
                if current_chunk:
                    current_chunk += "\n" + paragraph
                else:
                    current_chunk = paragraph
        
        # 处理最后一个块
        if current_chunk.strip():
            chunk_content = current_chunk.strip()
            chunk = DocumentChunk(
                id=f"{province}_{chunk_id:03d}",
                province=province,
                content=chunk_content,
                chunk_type=self.identify_content_type(chunk_content),
                metadata={
                    **metadata,
                    "chunk_index": chunk_id,
                    "is_last_chunk": True
                },
                char_count=len(chunk_content),
                source=metadata.get("filename", ""),
                start_pos=current_pos,
                end_pos=current_pos + len(chunk_content),
                chunk_id=chunk_id
            )
            chunks.append(chunk)
        
        return chunks
    
    def process_single_document(self, file_path: Path) -> List[DocumentChunk]:
        """
        处理单个文档
        
        Args:
            file_path: 文档路径
            
        Returns:
            List[DocumentChunk]: 文档块列表
        """
        logger.info(f"📄 处理文档: {file_path.name}")
        
        # 读取文档内容
        content, metadata = self.read_docx_file(file_path)
        
        if not content:
            logger.warning(f"⚠️ 文档内容为空: {file_path.name}")
            return []
        
        # 识别省份
        province = self.extract_province_from_filename(file_path.name)
        if not province:
            province = self.extract_province_from_content(content)
        
        if not province:
            logger.warning(f"⚠️ 无法识别省份: {file_path.name}")
            province = "未知"
        
        # 分割文本
        chunks = self.split_text_into_chunks(content, province, metadata)
        
        logger.info(f"✅ 文档处理完成: {province} ({len(chunks)} 个块)")
        
        return chunks
    
    def process_all_documents(self) -> List[DocumentChunk]:
        """
        处理所有文档
        
        Returns:
            List[DocumentChunk]: 所有文档块列表
        """
        logger.info(f"🚀 开始处理所有文档...")
        
        if not self.raw_documents_path.exists():
            logger.error(f"❌ 文档路径不存在: {self.raw_documents_path}")
            return []
        
        # 查找所有Word文档
        doc_files = list(self.raw_documents_path.glob("*.docx"))
        doc_files.extend(self.raw_documents_path.glob("*.doc"))
        
        if not doc_files:
            logger.error(f"❌ 未找到Word文档: {self.raw_documents_path}")
            return []
        
        logger.info(f"📚 找到 {len(doc_files)} 个文档")
        
        all_chunks = []
        
        # 处理每个文档
        for file_path in tqdm(doc_files, desc="📖 处理文档"):
            chunks = self.process_single_document(file_path)
            all_chunks.extend(chunks)
        
        # 统计信息
        province_stats = {}
        for chunk in all_chunks:
            province = chunk.province
            if province not in province_stats:
                province_stats[province] = 0
            province_stats[province] += 1
        
        logger.info(f"✅ 文档处理完成!")
        logger.info(f"📊 总块数: {len(all_chunks)}")
        logger.info(f"🗺️ 省份统计: {province_stats}")
        
        return all_chunks
    
    def save_processed_data(self, chunks: List[DocumentChunk], output_path: Path) -> bool:
        """
        保存处理后的数据
        
        Args:
            chunks: 文档块列表
            output_path: 输出路径
            
        Returns:
            bool: 是否保存成功
        """
        try:
            output_path.mkdir(parents=True, exist_ok=True)
            
            # 保存为JSON格式
            json_file = output_path / "processed_chunks.json"
            
            chunks_data = [chunk.to_dict() for chunk in chunks]
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(chunks_data, f, ensure_ascii=False, indent=2)
            
            # 保存统计信息
            stats_file = output_path / "processing_stats.json"
            
            province_stats = {}
            type_stats = {}
            
            for chunk in chunks:
                # 省份统计
                province = chunk.province
                if province not in province_stats:
                    province_stats[province] = {"count": 0, "total_chars": 0}
                province_stats[province]["count"] += 1
                province_stats[province]["total_chars"] += chunk.char_count
                
                # 类型统计
                chunk_type = chunk.chunk_type
                if chunk_type not in type_stats:
                    type_stats[chunk_type] = 0
                type_stats[chunk_type] += 1
            
            stats = {
                "total_chunks": len(chunks),
                "total_documents": len(set(chunk.province for chunk in chunks)),
                "province_stats": province_stats,
                "type_stats": type_stats,
                "processing_config": {
                    "chunk_size": self.chunk_size,
                    "chunk_overlap": self.chunk_overlap
                }
            }
            
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 数据保存成功: {json_file}")
            logger.info(f"📊 统计保存成功: {stats_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 保存数据失败: {str(e)}")
            return False
    
    def load_processed_data(self, data_path: Path) -> List[DocumentChunk]:
        """
        加载已处理的数据
        
        Args:
            data_path: 数据路径
            
        Returns:
            List[DocumentChunk]: 文档块列表
        """
        try:
            json_file = data_path / "processed_chunks.json"
            
            if not json_file.exists():
                logger.warning(f"⚠️ 处理数据文件不存在: {json_file}")
                return []
            
            with open(json_file, 'r', encoding='utf-8') as f:
                chunks_data = json.load(f)
            
            chunks = []
            for chunk_data in chunks_data:
                # 确保所有必需的属性都存在，为缺失的属性提供默认值
                chunk_data.setdefault('source', chunk_data.get('metadata', {}).get('filename', ''))
                chunk_data.setdefault('start_pos', 0)
                chunk_data.setdefault('end_pos', chunk_data.get('char_count', 0))
                chunk_data.setdefault('chunk_id', chunk_data.get('metadata', {}).get('chunk_index', 0))
                
                chunk = DocumentChunk(**chunk_data)
                chunks.append(chunk)
            
            logger.info(f"📂 加载数据成功: {len(chunks)} 个块")
            
            return chunks
            
        except Exception as e:
            logger.error(f"❌ 加载数据失败: {str(e)}")
            return []

 