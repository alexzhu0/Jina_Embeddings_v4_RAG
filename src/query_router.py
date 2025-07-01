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
        """构建API提示词 - 强化完整性和准确性要求"""
        format_instructions = {
            "province_list": """请按照以下格式详细输出，每个省份包含尽可能多的具体数据：
省份：具体数据1（包含数字、百分比）、具体数据2（包含数字、百分比）、具体数据3（包含数字、百分比）...

严格要求：
1. 必须包含参考资料中的所有具体数字和百分比，不得遗漏
2. 每个省份至少列出8-15个具体数据点（包含增长率、总量、投资额等）
3. 所有数据必须准确引用原文，不得编造或估算
4. 如果某省份信息较少，明确说明"该省份信息有限"
5. 优先展示量化指标：GDP、投资额、项目数量、增长率、完成率等""",
            
            "detailed": """请提供极其详细的分析报告，必须包含：
1. 所有具体数字数据（GDP、投资额、增长率、项目数量等）
2. 详细的政策措施和完整的实施方案
3. 具体的项目名称、建设内容、投资规模
4. 明确的时间节点和量化目标指标
5. 每个省份的深入对比分析
6. 完整的统计表格和数据汇总

数据完整性要求：
- 不得省略任何参考资料中的重要信息
- 必须展示所有可用的数字和百分比
- 如信息不足，明确指出缺失的数据类型""",
            
            "comparison": """请以极其详细的对比形式展示，包含：
1. 所有关键指标的具体数字对比（制作详细表格）
2. 政策措施的全面差异分析
3. 发展重点的深度比较
4. 投资规模、项目数量的精确对比
5. 增长率、完成率等关键指标对比

对比要求：
- 必须使用表格形式展示数据
- 每个对比项都要有具体数字支撑
- 不得遗漏任何可对比的数据点
- 明确标注数据来源和时间""",
            
            "statistics": """请提供极其详细的统计汇总信息，包含：
1. 所有指标的完整数字统计（制作统计表）
2. 详细的增长趋势和精确变化幅度
3. 完整的排名和全面对比分析
4. 深入的总体特点和规律分析
5. 各省份的详细数据汇总

统计要求：
- 必须包含所有可统计的数据
- 制作详细的统计表格
- 计算平均值、最大值、最小值
- 分析数据分布和趋势特征"""
        }
        
        instruction = format_instructions.get(output_format, format_instructions["province_list"])
        
        prompt = f"""你是一个资深的政府工作报告数据分析专家。你的任务是基于提供的政府工作报告内容，为用户提供最详细、最完整、最准确的回答。

【用户问题】
{query}

【输出格式要求】
{instruction}

【核心要求 - 必须严格遵守】
1. 信息完整性：必须充分利用参考资料中的所有信息，不得遗漏任何重要数据
2. 数据准确性：所有数字、百分比、具体措施都必须准确引用原文，绝不编造
3. 详细程度：回答必须详尽，包含所有可用的具体数据和信息
4. 量化优先：优先展示具体的数字指标、百分比、增长率等量化数据
5. 完整性验证：在回答结束前，确认是否已充分利用了所有参考资料

【信息利用检查】
- 是否已经提取了所有省份的相关信息？
- 是否已经包含了所有可用的数字数据？
- 是否已经涵盖了所有重要的政策措施？
- 是否已经展示了所有相关的项目和投资信息？

【参考资料】
{context}

请基于以上参考资料，提供最详细、最完整的专业分析。确保充分利用所有可用信息，不要简化或省略任何重要内容。"""
        
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

 