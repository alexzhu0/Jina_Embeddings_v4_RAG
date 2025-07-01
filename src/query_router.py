#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
查询路由器
负责查询意图识别、分批处理策略和查询优化
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging

from retriever import get_retriever, RetrievalResult
from api_client import get_api_client

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class QueryPlan:
    """查询执行计划"""
    query_type: str
    batch_strategy: str
    batches: List[Dict]
    expected_provinces: List[str]
    output_format: str

class QueryRouter:
    """查询路由器"""
    
    def __init__(self):
        """初始化查询路由器"""
        self.retriever = get_retriever()
        self.api_client = get_api_client()
        
        # 输出格式模板
        self.output_templates = {
            "province_list": "省份：目标1、目标2...",
            "detailed": "详细分析报告",
            "comparison": "对比分析表格",
            "statistics": "统计汇总信息"
        }
        
        # 省份分组策略（用于批处理）
        self.province_groups = {
            "economic_zones": {
                "东部地区": ["北京", "天津", "河北", "上海", "江苏", "浙江", "福建", "山东", "广东", "海南"],
                "中部地区": ["山西", "安徽", "江西", "河南", "湖北", "湖南"],
                "西部地区": ["内蒙古", "广西", "重庆", "四川", "贵州", "云南", "西藏", "陕西", "甘肃", "青海", "宁夏", "新疆"],
                "东北地区": ["辽宁", "吉林", "黑龙江"]
            },
            "geographic": {
                "华北": ["北京", "天津", "河北", "山西", "内蒙古"],
                "华东": ["上海", "江苏", "浙江", "安徽", "福建", "江西", "山东"],
                "华中": ["河南", "湖北", "湖南"],
                "华南": ["广东", "广西", "海南"],
                "西南": ["重庆", "四川", "贵州", "云南", "西藏"],
                "西北": ["陕西", "甘肃", "青海", "宁夏", "新疆"],
                "东北": ["辽宁", "吉林", "黑龙江"]
            }
        }
        
        logger.info("🎯 查询路由器初始化完成")
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """
        分析查询并生成执行计划
        
        Args:
            query: 用户查询
            
        Returns:
            Dict: 查询分析结果
        """
        logger.info(f"🔍 分析查询: {query}")
        
        analysis = {
            "original_query": query,
            "intent": self._identify_intent(query),
            "scope": self._determine_scope(query),
            "output_format": self._determine_output_format(query),
            "complexity": self._assess_complexity(query)
        }
        
        logger.debug(f"📊 查询分析结果: {analysis}")
        return analysis
    
    def create_query_plan(self, query_analysis: Dict[str, Any]) -> QueryPlan:
        """
        创建查询执行计划
        
        Args:
            query_analysis: 查询分析结果
            
        Returns:
            QueryPlan: 查询执行计划
        """
        intent = query_analysis["intent"]
        scope = query_analysis["scope"]
        complexity = query_analysis["complexity"]
        
        # 确定批处理策略
        if intent["type"] == "all_provinces" and complexity == "high":
            batch_strategy = "province_groups"
            batches = self._create_province_group_batches(query_analysis["original_query"])
        elif intent["type"] == "all_provinces":
            batch_strategy = "single_batch"
            batches = [{"type": "all_provinces", "query": query_analysis["original_query"]}]
        elif len(intent.get("provinces", [])) > 5:
            batch_strategy = "province_chunks"
            batches = self._create_province_chunk_batches(query_analysis["original_query"], intent["provinces"])
        else:
            batch_strategy = "single_query"
            batches = [{"type": "direct", "query": query_analysis["original_query"]}]
        
        plan = QueryPlan(
            query_type=intent["type"],
            batch_strategy=batch_strategy,
            batches=batches,
            expected_provinces=intent.get("provinces", []),
            output_format=query_analysis["output_format"]
        )
        
        logger.info(f"📋 查询计划: {batch_strategy}, {len(batches)} 个批次")
        return plan
    
    def execute_query_plan(self, plan: QueryPlan) -> Dict[str, Any]:
        """
        执行查询计划
        
        Args:
            plan: 查询执行计划
            
        Returns:
            Dict: 执行结果
        """
        logger.info(f"🚀 执行查询计划: {plan.batch_strategy}")
        
        results = []
        all_provinces = set()
        total_processing_time = 0
        
        for i, batch in enumerate(plan.batches):
            logger.info(f"📦 处理批次 {i+1}/{len(plan.batches)}")
            
            try:
                batch_result = self._execute_single_batch(batch, plan.output_format)
                if batch_result["success"]:
                    results.append(batch_result)
                    all_provinces.update(batch_result.get("provinces", []))
                    total_processing_time += batch_result.get("processing_time", 0)
                else:
                    logger.warning(f"⚠️ 批次 {i+1} 执行失败: {batch_result.get('error')}")
            
            except Exception as e:
                logger.error(f"❌ 批次 {i+1} 执行异常: {str(e)}")
        
        # 聚合结果
        final_result = self._aggregate_results(results, plan)
        final_result.update({
            "total_batches": len(plan.batches),
            "successful_batches": len(results),
            "total_provinces": len(all_provinces),
            "total_processing_time": total_processing_time
        })
        
        logger.info(f"✅ 查询执行完成: {len(results)}/{len(plan.batches)} 批次成功")
        return final_result
    
    def _identify_intent(self, query: str) -> Dict[str, Any]:
        """识别查询意图"""
        intent = {
            "type": "general",
            "provinces": [],
            "topics": [],
            "actions": []
        }
        
        # 检查省份提及
        from config.config import PROVINCES
        mentioned_provinces = [p for p in PROVINCES if p in query]
        intent["provinces"] = mentioned_provinces
        
        # 检查查询类型
        if any(keyword in query for keyword in ["所有省份", "各省", "31省", "全国"]):
            intent["type"] = "all_provinces"
        elif len(mentioned_provinces) == 1:
            intent["type"] = "single_province"
        elif len(mentioned_provinces) > 1:
            intent["type"] = "multi_province"
        elif any(keyword in query for keyword in ["对比", "比较"]):
            intent["type"] = "comparison"
        elif any(keyword in query for keyword in ["统计", "汇总", "总结"]):
            intent["type"] = "statistics"
        
        # 识别主题
        topic_keywords = {
            "economic": ["经济", "GDP", "产业", "发展"],
            "social": ["社会", "民生", "教育", "医疗"],
            "environment": ["环境", "生态", "绿色"],
            "targets": ["目标", "任务", "重点", "计划"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in query for keyword in keywords):
                intent["topics"].append(topic)
        
        # 识别动作
        if any(keyword in query for keyword in ["列出", "列举", "显示"]):
            intent["actions"].append("list")
        if any(keyword in query for keyword in ["分析", "解析"]):
            intent["actions"].append("analyze")
        if any(keyword in query for keyword in ["对比", "比较"]):
            intent["actions"].append("compare")
        
        return intent
    
    def _determine_scope(self, query: str) -> str:
        """确定查询范围"""
        if any(keyword in query for keyword in ["所有", "全部", "全国", "31省"]):
            return "comprehensive"
        elif any(keyword in query for keyword in ["部分", "某些", "几个"]):
            return "partial"
        else:
            return "specific"
    
    def _determine_output_format(self, query: str) -> str:
        """确定输出格式"""
        if any(keyword in query for keyword in ["列出", "列举"]):
            return "province_list"
        elif any(keyword in query for keyword in ["详细", "具体", "深入"]):
            return "detailed"
        elif any(keyword in query for keyword in ["对比", "比较"]):
            return "comparison"
        elif any(keyword in query for keyword in ["统计", "汇总"]):
            return "statistics"
        else:
            return "province_list"  # 默认格式
    
    def _assess_complexity(self, query: str) -> str:
        """评估查询复杂度"""
        complexity_indicators = 0
        
        # 检查复杂度指标
        if any(keyword in query for keyword in ["所有省份", "31省", "全国"]):
            complexity_indicators += 2
        
        if any(keyword in query for keyword in ["对比", "分析", "统计"]):
            complexity_indicators += 1
        
        if any(keyword in query for keyword in ["详细", "深入", "全面"]):
            complexity_indicators += 1
        
        # 检查省份数量
        from config.config import PROVINCES
        mentioned_provinces = [p for p in PROVINCES if p in query]
        if len(mentioned_provinces) > 3:
            complexity_indicators += 1
        
        if complexity_indicators >= 3:
            return "high"
        elif complexity_indicators >= 1:
            return "medium"
        else:
            return "low"
    
    def _create_province_group_batches(self, query: str) -> List[Dict]:
        """创建省份分组批次"""
        batches = []
        
        # 使用经济区域分组
        for region, provinces in self.province_groups["economic_zones"].items():
            batch_query = f"请列出{region}各省份的主要工作目标：{', '.join(provinces)}"
            batches.append({
                "type": "province_group",
                "region": region,
                "provinces": provinces,
                "query": batch_query
            })
        
        return batches
    
    def _create_province_chunk_batches(self, query: str, provinces: List[str]) -> List[Dict]:
        """创建省份分块批次"""
        from config.config import QUERY_CONFIG
        batch_size = QUERY_CONFIG["batch_size"]
        
        batches = []
        for i in range(0, len(provinces), batch_size):
            batch_provinces = provinces[i:i + batch_size]
            batch_query = f"请列出以下省份的主要工作目标：{', '.join(batch_provinces)}"
            batches.append({
                "type": "province_chunk",
                "provinces": batch_provinces,
                "query": batch_query
            })
        
        return batches
    
    def _execute_single_batch(self, batch: Dict, output_format: str) -> Dict[str, Any]:
        """执行单个批次"""
        import time
        start_time = time.time()
        
        try:
            # 检索相关信息
            if batch["type"] == "all_provinces":
                retrieval_result = self.retriever.smart_retrieve(batch["query"])
            elif batch["type"] in ["province_group", "province_chunk"]:
                retrieval_result = self.retriever.retrieve_for_specific_provinces(
                    batch["query"], 
                    batch["provinces"]
                )
            else:
                retrieval_result = self.retriever.smart_retrieve(batch["query"])
            
            # 构建提示词
            context = self.retriever.format_context(retrieval_result)
            prompt = self._build_prompt(batch["query"], context, output_format)
            
            # 调用API - 使用配置文件中的超时设置
            from config.config import SILICONFLOW_CONFIG
            response = self.api_client.simple_chat(
                prompt,
                timeout=SILICONFLOW_CONFIG["timeout"],
                temperature=SILICONFLOW_CONFIG["temperature"],
                max_tokens=SILICONFLOW_CONFIG["max_tokens"]
            )
            
            processing_time = time.time() - start_time
            
            if response.success:
                return {
                    "success": True,
                    "content": response.content,
                    "provinces": list(retrieval_result.provinces),
                    "processing_time": processing_time,
                    "batch_info": batch
                }
            else:
                return {
                    "success": False,
                    "error": response.error,
                    "processing_time": processing_time,
                    "batch_info": batch
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "processing_time": time.time() - start_time,
                "batch_info": batch
            }
    
    def _build_prompt(self, query: str, context: str, output_format: str) -> str:
        """构建API提示词 - 重点提取和展示原文内容"""
        format_instructions = {
            "province_list": """请按照以下格式输出，直接引用政府工作报告的原文内容：
省份：原文内容1、原文内容2、原文内容3...

要求：
1. 直接摘录政府工作报告中的原文表述，保持原文的准确性
2. 每个省份提取8-15个相关的原文段落或句子
3. 优先选择包含具体数字、政策措施、工作目标的原文
4. 保持原文的完整性，不要随意删减或修改
5. 如果原文较长，可以摘录关键部分，但要保持语义完整""",
            
            "detailed": """请提供详细的原文摘录，按以下方式组织：
1. 直接引用政府工作报告中的相关段落
2. 保持原文的表述方式和用词
3. 按主题分类展示原文内容（如经济发展、民生保障等）
4. 每个主题下引用3-5段相关原文
5. 确保原文的上下文逻辑清晰

原文摘录要求：
- 完全按照政府工作报告的原文表述
- 不添加任何个人分析或解释
- 保持原文的数字、百分比、专业术语等准确性
- 如需连接多段原文，用"..."表示省略""",
            
            "comparison": """请以原文对比的形式展示：
1. 直接摘录各省份政府工作报告中的相关原文
2. 按对比项目分类展示原文内容
3. 每个对比项下列出各省份的原文表述
4. 保持各省份原文的独立性和完整性

原文对比格式：
【对比项目1】
省份A：原文内容...
省份B：原文内容...

【对比项目2】
省份A：原文内容...
省份B：原文内容...""",
            
            "statistics": """请提供基于原文的统计信息：
1. 摘录各省份工作报告中的相关原文
2. 按统计类别整理原文内容
3. 直接引用原文中的数字和表述
4. 保持原文的准确性和权威性

统计展示要求：
- 以原文为准，不进行二次加工
- 按省份分别列出相关原文
- 突出原文中的关键数字和政策表述
- 保持政府工作报告的官方表述风格"""
        }
        
        instruction = format_instructions.get(output_format, format_instructions["province_list"])
        
        prompt = f"""你是一个政府工作报告原文提取专家。你的任务是从政府工作报告中准确提取和展示相关的原文内容，而不是进行分析或重新表述。

【用户问题】
{query}

【输出格式要求】
{instruction}

【原文提取原则 - 严格遵守】
1. 原文优先：直接引用政府工作报告的原文，不进行改写或分析
2. 准确完整：确保摘录的原文准确无误，保持上下文完整
3. 权威性：保持政府工作报告的官方表述和用词习惯
4. 全面性：尽可能多地提取相关的原文内容
5. 真实性：绝对不能编造或修改原文内容

【原文选择标准】
- 优先选择直接回答用户问题的原文段落
- 重点提取包含具体数字、政策、目标的原文
- 选择表述清晰、信息完整的原文句子
- 保持原文的逻辑顺序和表述风格
- 如果原文很长，摘录最核心的部分

【严格禁止】
- 禁止对原文进行任何分析、解释或评论
- 禁止改写、简化或美化原文表述
- 禁止添加原文中没有的内容
- 禁止使用"根据报告"、"据了解"等分析性表述
- 禁止对数字进行计算或对比分析

【参考资料】
{context}

请严格按照上述要求，直接从参考资料中提取相关的政府工作报告原文。确保每一句话都是政府工作报告的原始表述。"""
        
        return prompt
    
    def _aggregate_results(self, results: List[Dict], plan: QueryPlan) -> Dict[str, Any]:
        """聚合批次结果"""
        if not results:
            return {
                "success": False,
                "content": "没有成功的查询结果",
                "provinces": []
            }
        
        # 合并所有成功的结果
        all_content = []
        all_provinces = set()
        
        for result in results:
            if result["success"]:
                all_content.append(result["content"])
                all_provinces.update(result.get("provinces", []))
        
        # 根据输出格式整理结果
        if plan.output_format == "province_list":
            # 合并省份列表格式的结果
            final_content = "\n".join(all_content)
        else:
            # 其他格式直接连接
            final_content = "\n\n".join(all_content)
        
        return {
            "success": True,
            "content": final_content,
            "provinces": list(all_provinces),
            "query_plan": plan,
            "batch_results": results
        }

# 全局查询路由器实例
_query_router = None

def get_query_router() -> QueryRouter:
    """获取全局查询路由器实例"""
    global _query_router
    if _query_router is None:
        _query_router = QueryRouter()
    return _query_router

 