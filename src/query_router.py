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
        """构建API提示词 - 平衡数据与文本信息的完整性"""
        format_instructions = {
            "province_list": """请按照以下格式详细输出，每个省份包含丰富的信息内容：
省份：【重点工作1】具体措施和目标、【重点工作2】具体措施和目标、【重点工作3】具体措施和目标...

内容要求：
1. 既要包含具体数字数据（如增长率、投资额、项目数量等），也要包含重要的文字描述
2. 详细描述政策措施、发展方向、具体举措和实施方案
3. 每个省份至少包含8-12个重点内容，涵盖经济、社会、民生等各个方面
4. 准确引用原文中的关键表述和重要政策描述
5. 平衡展示量化指标和定性描述，两者同样重要""",
            
            "detailed": """请提供全面详细的分析报告，内容应包含：
1. 重要的数字指标（GDP、投资额、增长率等）及其背景解释
2. 详细的政策措施、发展理念和战略规划的完整描述
3. 具体项目的名称、建设内容、意义和影响
4. 重要的时间节点、实施步骤和推进计划
5. 深入的背景分析、发展趋势和政策导向
6. 完整的工作重点、改革举措和创新做法

分析要求：
- 数字数据和文字描述并重，提供完整的信息图景
- 深入解读政策背景、实施路径和预期效果
- 突出重要的政策创新和特色做法
- 全面展现政府工作的战略思路和具体安排""",
            
            "comparison": """请以全面的对比形式展示，包含：
1. 关键指标的数字对比，并解释背后的政策差异
2. 政策措施、发展理念和战略重点的深度比较
3. 工作重点、改革方向和创新举措的对比分析
4. 发展模式、推进路径和实施策略的差异
5. 特色做法、亮点工作和经验做法的比较

对比要求：
- 既要有数据对比，也要有政策理念和实施方式的对比
- 深入分析不同地区的发展特色和政策特点
- 突出各地的创新做法和特色亮点
- 全面展现不同发展模式和政策选择""",
            
            "statistics": """请提供全面的统计汇总信息，包含：
1. 重要指标的数字统计和趋势分析
2. 政策措施的分类汇总和特点分析
3. 工作重点的统计分布和共性特征
4. 发展方向的整体趋势和规律总结
5. 改革举措的类型统计和创新特色

统计要求：
- 数据统计与政策分析并重
- 既要有量化统计，也要有定性总结
- 深入分析共性特征和差异化特点
- 全面展现整体发展态势和政策导向"""
        }
        
        instruction = format_instructions.get(output_format, format_instructions["province_list"])
        
        prompt = f"""你是一个资深的政府工作报告综合分析专家。你的任务是基于提供的政府工作报告内容，为用户提供最全面、最深入、最准确的分析。

【用户问题】
{query}

【输出格式要求】
{instruction}

【核心分析原则 - 必须严格遵守】
1. 信息完整性：充分利用参考资料中的所有信息，包括数字数据和文字描述
2. 内容平衡性：数字指标和政策文本同样重要，需要平衡展示
3. 分析深度性：不仅要提取信息，还要解读背景、意义和影响
4. 准确性原则：所有内容都必须准确引用原文，不得编造或推测
5. 全面性要求：涵盖经济、社会、民生、改革等各个方面的内容

【信息挖掘重点】
- 重要的数字指标：GDP、投资、增长率、项目数量等量化数据
- 关键的政策措施：具体的政策安排、改革举措、工作部署
- 发展理念导向：发展思路、战略重点、工作方向
- 具体实施方案：推进步骤、时间安排、责任分工
- 创新特色做法：亮点工作、经验做法、特色举措

【分析深度要求】
- 不仅要列出"是什么"，还要分析"为什么"和"怎么做"
- 既要关注具体数据，也要理解政策背景和实施路径
- 重视政策的系统性、连贯性和创新性
- 突出不同地区的特色和差异化发展

【参考资料】
{context}

请基于以上参考资料，提供最全面、最深入的专业分析。确保数字数据和文字信息并重，充分展现政府工作报告的丰富内容。"""
        
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

 