#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
结果聚合器
负责多次查询结果的合并、去重、格式化和优化
"""

import re
from typing import List, Dict, Any, Set, Tuple
from dataclasses import dataclass
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AggregatedResult:
    """聚合结果数据结构"""
    content: str
    provinces: List[str]
    total_targets: int
    format_type: str
    processing_stats: Dict[str, Any]

class ResultAggregator:
    """结果聚合器"""
    
    def __init__(self):
        """初始化结果聚合器"""
        
        # 省份别名映射（用于去重和标准化）
        self.province_aliases = {
            "京": "北京", "津": "天津", "冀": "河北", "晋": "山西", "蒙": "内蒙古",
            "辽": "辽宁", "吉": "吉林", "黑": "黑龙江", "沪": "上海", "苏": "江苏",
            "浙": "浙江", "皖": "安徽", "闽": "福建", "赣": "江西", "鲁": "山东",
            "豫": "河南", "鄂": "湖北", "湘": "湖南", "粤": "广东", "桂": "广西",
            "琼": "海南", "渝": "重庆", "川": "四川", "蜀": "四川", "黔": "贵州",
            "贵": "贵州", "滇": "云南", "云": "云南", "藏": "西藏", "陕": "陕西",
            "秦": "陕西", "甘": "甘肃", "陇": "甘肃", "青": "青海", "宁": "宁夏",
            "新": "新疆"
        }
        
        # 目标关键词（用于提取和分类）
        self.target_keywords = [
            "目标", "任务", "重点", "计划", "规划", "工程", "项目", "举措",
            "推进", "发展", "建设", "完善", "提升", "增长", "实现", "达到"
        ]
        
        logger.info("📊 结果聚合器初始化完成")
    
    def aggregate_batch_results(self, batch_results: List[Dict[str, Any]], 
                              output_format: str = "province_list") -> AggregatedResult:
        """
        聚合批次结果
        
        Args:
            batch_results: 批次结果列表
            output_format: 输出格式
            
        Returns:
            AggregatedResult: 聚合后的结果
        """
        logger.info(f"🔄 开始聚合 {len(batch_results)} 个批次结果")
        
        # 提取所有成功的结果
        successful_results = [r for r in batch_results if r.get("success", False)]
        
        if not successful_results:
            return AggregatedResult(
                content="抱歉，没有获取到有效的查询结果。",
                provinces=[],
                total_targets=0,
                format_type=output_format,
                processing_stats={"success_rate": 0, "total_batches": len(batch_results)}
            )
        
        # 解析和标准化省份信息
        all_provinces = set()
        province_contents = {}
        
        for result in successful_results:
            content = result.get("content", "")
            provinces = result.get("provinces", [])
            
            # 解析内容中的省份信息
            parsed_info = self._parse_province_content(content)
            
            for province, targets in parsed_info.items():
                normalized_province = self._normalize_province_name(province)
                if normalized_province:
                    all_provinces.add(normalized_province)
                    
                    if normalized_province not in province_contents:
                        province_contents[normalized_province] = []
                    
                    province_contents[normalized_province].extend(targets)
        
        # 去重和优化内容
        for province in province_contents:
            province_contents[province] = self._deduplicate_targets(province_contents[province])
        
        # 根据格式要求生成最终结果
        if output_format == "province_list":
            final_content = self._format_as_province_list(province_contents)
        elif output_format == "detailed":
            final_content = self._format_as_detailed_report(province_contents)
        elif output_format == "comparison":
            final_content = self._format_as_comparison_table(province_contents)
        elif output_format == "statistics":
            final_content = self._format_as_statistics(province_contents)
        else:
            final_content = self._format_as_province_list(province_contents)
        
        # 统计信息
        total_targets = sum(len(targets) for targets in province_contents.values())
        
        processing_stats = {
            "success_rate": len(successful_results) / len(batch_results),
            "total_batches": len(batch_results),
            "successful_batches": len(successful_results),
            "provinces_found": len(all_provinces),
            "total_targets_extracted": total_targets
        }
        
        logger.info(f"✅ 聚合完成: {len(all_provinces)} 个省份, {total_targets} 个目标")
        
        return AggregatedResult(
            content=final_content,
            provinces=sorted(list(all_provinces)),
            total_targets=total_targets,
            format_type=output_format,
            processing_stats=processing_stats
        )
    
    def _parse_province_content(self, content: str) -> Dict[str, List[str]]:
        """
        解析内容中的省份和目标信息
        
        Args:
            content: 原始内容
            
        Returns:
            Dict[str, List[str]]: 省份到目标列表的映射
        """
        province_info = {}
        
        # 按行分割内容
        lines = content.split('\n')
        current_province = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检查是否是省份标题行
            province_match = self._extract_province_from_line(line)
            if province_match:
                current_province = province_match
                if current_province not in province_info:
                    province_info[current_province] = []
                
                # 提取同行的目标信息
                targets_in_line = self._extract_targets_from_line(line)
                if targets_in_line:
                    province_info[current_province].extend(targets_in_line)
            
            elif current_province:
                # 当前行属于某个省份的内容
                targets_in_line = self._extract_targets_from_line(line)
                if targets_in_line:
                    province_info[current_province].extend(targets_in_line)
        
        return province_info
    
    def _extract_province_from_line(self, line: str) -> str:
        """从行中提取省份名称"""
        from config.config import PROVINCES
        
        # 检查标准省份名称
        for province in PROVINCES:
            if province in line:
                return province
        
        # 检查省份别名
        for alias, full_name in self.province_aliases.items():
            if alias in line:
                return full_name
        
        # 使用正则表达式匹配省份模式
        province_pattern = r'([^：:]+)(?:省|市|自治区)?[：:]'
        match = re.search(province_pattern, line)
        if match:
            potential_province = match.group(1).strip()
            # 验证是否是有效的省份名称
            for province in PROVINCES:
                if province in potential_province or potential_province in province:
                    return province
        
        return None
    
    def _extract_targets_from_line(self, line: str) -> List[str]:
        """从行中提取目标信息"""
        targets = []
        
        # 移除省份名称前缀
        clean_line = line
        for province in ["北京", "天津", "河北", "山西", "内蒙古", "辽宁", "吉林", "黑龙江",
                        "上海", "江苏", "浙江", "安徽", "福建", "江西", "山东", "河南",
                        "湖北", "湖南", "广东", "广西", "海南", "重庆", "四川", "贵州",
                        "云南", "西藏", "陕西", "甘肃", "青海", "宁夏", "新疆"]:
            clean_line = re.sub(f'^{province}[：:]?', '', clean_line)
        
        # 按分隔符分割目标
        separators = ['、', '，', ',', '；', ';', '。', '|']
        
        for sep in separators:
            if sep in clean_line:
                parts = clean_line.split(sep)
                for part in parts:
                    part = part.strip()
                    if part and len(part) > 3:  # 过滤太短的内容
                        targets.append(part)
                break
        else:
            # 没有找到分隔符，整行作为一个目标
            clean_line = clean_line.strip()
            if clean_line and len(clean_line) > 3:
                targets.append(clean_line)
        
        # 过滤和清理目标
        cleaned_targets = []
        for target in targets:
            target = re.sub(r'^[0-9]+\.?\s*', '', target)  # 移除序号
            target = target.strip()
            
            # 检查是否包含目标关键词
            if any(keyword in target for keyword in self.target_keywords) or len(target) > 10:
                cleaned_targets.append(target)
        
        return cleaned_targets
    
    def _normalize_province_name(self, province: str) -> str:
        """标准化省份名称"""
        if not province:
            return None
        
        # 移除常见后缀
        province = re.sub(r'(省|市|自治区|特别行政区)$', '', province)
        
        # 检查别名映射
        if province in self.province_aliases:
            return self.province_aliases[province]
        
        # 检查是否是标准省份名称
        from config.config import PROVINCES
        for std_province in PROVINCES:
            if province == std_province or province in std_province:
                return std_province
        
        return province
    
    def _deduplicate_targets(self, targets: List[str]) -> List[str]:
        """去重和优化目标列表"""
        if not targets:
            return []
        
        # 去除完全重复的项
        unique_targets = list(dict.fromkeys(targets))
        
        # 去除高度相似的项
        final_targets = []
        for target in unique_targets:
            is_duplicate = False
            for existing in final_targets:
                # 计算相似度
                if self._calculate_similarity(target, existing) > 0.8:
                    is_duplicate = True
                    # 保留更长的版本
                    if len(target) > len(existing):
                        final_targets.remove(existing)
                        final_targets.append(target)
                    break
            
            if not is_duplicate:
                final_targets.append(target)
        
        return final_targets
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的相似度"""
        # 简单的字符级相似度计算
        if not text1 or not text2:
            return 0.0
        
        # 计算公共字符数
        common_chars = sum(1 for c in text1 if c in text2)
        max_length = max(len(text1), len(text2))
        
        return common_chars / max_length if max_length > 0 else 0.0
    
    def _format_as_province_list(self, province_contents: Dict[str, List[str]]) -> str:
        """格式化为省份列表格式"""
        lines = []
        
        for province in sorted(province_contents.keys()):
            targets = province_contents[province]
            if targets:
                targets_str = "、".join(targets[:5])  # 限制每个省份最多5个目标
                if len(targets) > 5:
                    targets_str += f"等{len(targets)}项"
                lines.append(f"{province}：{targets_str}")
            else:
                lines.append(f"{province}：信息不足")
        
        return "\n".join(lines)
    
    def _format_as_detailed_report(self, province_contents: Dict[str, List[str]]) -> str:
        """格式化为详细报告格式"""
        sections = []
        
        sections.append("# 各省政府工作报告主要目标汇总\n")
        
        for province in sorted(province_contents.keys()):
            targets = province_contents[province]
            sections.append(f"## {province}")
            
            if targets:
                for i, target in enumerate(targets, 1):
                    sections.append(f"{i}. {target}")
            else:
                sections.append("暂无具体目标信息")
            
            sections.append("")  # 空行分隔
        
        return "\n".join(sections)
    
    def _format_as_comparison_table(self, province_contents: Dict[str, List[str]]) -> str:
        """格式化为对比表格格式"""
        lines = []
        lines.append("| 省份 | 主要工作目标 | 目标数量 |")
        lines.append("|------|-------------|---------|")
        
        for province in sorted(province_contents.keys()):
            targets = province_contents[province]
            target_count = len(targets)
            
            if targets:
                main_targets = "、".join(targets[:3])
                if len(targets) > 3:
                    main_targets += "..."
            else:
                main_targets = "信息不足"
                target_count = 0
            
            lines.append(f"| {province} | {main_targets} | {target_count} |")
        
        return "\n".join(lines)
    
    def _format_as_statistics(self, province_contents: Dict[str, List[str]]) -> str:
        """格式化为统计信息格式"""
        total_provinces = len(province_contents)
        total_targets = sum(len(targets) for targets in province_contents.values())
        provinces_with_targets = sum(1 for targets in province_contents.values() if targets)
        
        # 目标类型统计
        target_types = {}
        for targets in province_contents.values():
            for target in targets:
                for keyword in self.target_keywords:
                    if keyword in target:
                        target_types[keyword] = target_types.get(keyword, 0) + 1
        
        lines = []
        lines.append("# 政府工作报告统计分析")
        lines.append("")
        lines.append("## 基本统计")
        lines.append(f"- 总省份数：{total_provinces}")
        lines.append(f"- 有目标信息的省份：{provinces_with_targets}")
        lines.append(f"- 总目标数量：{total_targets}")
        lines.append(f"- 平均每省目标数：{total_targets/total_provinces:.1f}")
        lines.append("")
        
        if target_types:
            lines.append("## 目标类型分布")
            sorted_types = sorted(target_types.items(), key=lambda x: x[1], reverse=True)
            for target_type, count in sorted_types[:10]:
                lines.append(f"- {target_type}：{count} 次")
        
        return "\n".join(lines)
    
    def optimize_for_token_limit(self, content: str, max_tokens: int = 4000) -> str:
        """
        优化内容以适应token限制
        
        Args:
            content: 原始内容
            max_tokens: 最大token数（粗略估算）
            
        Returns:
            str: 优化后的内容
        """
        # 粗略估算：1个token约等于1.5个中文字符
        max_chars = max_tokens * 1.5
        
        if len(content) <= max_chars:
            return content
        
        logger.info(f"🔧 优化内容长度: {len(content)} -> {max_chars} 字符")
        
        # 按行分割并保留重要信息
        lines = content.split('\n')
        optimized_lines = []
        current_chars = 0
        
        # 优先保留省份标题行
        for line in lines:
            if any(province in line for province in ["北京", "天津", "河北", "山西", "内蒙古", 
                                                   "辽宁", "吉林", "黑龙江", "上海", "江苏", 
                                                   "浙江", "安徽", "福建", "江西", "山东", 
                                                   "河南", "湖北", "湖南", "广东", "广西", 
                                                   "海南", "重庆", "四川", "贵州", "云南", 
                                                   "西藏", "陕西", "甘肃", "青海", "宁夏", "新疆"]):
                if current_chars + len(line) <= max_chars:
                    optimized_lines.append(line)
                    current_chars += len(line) + 1  # +1 for newline
                else:
                    # 截断最后一行
                    remaining_chars = max_chars - current_chars
                    if remaining_chars > 10:
                        optimized_lines.append(line[:remaining_chars] + "...")
                    break
        
        return '\n'.join(optimized_lines)

# 全局结果聚合器实例
_result_aggregator = None

def get_result_aggregator() -> ResultAggregator:
    """获取全局结果聚合器实例"""
    global _result_aggregator
    if _result_aggregator is None:
        _result_aggregator = ResultAggregator()
    return _result_aggregator

 