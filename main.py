#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
政府工作报告RAG系统主程序
解决知识库内容过多，模型一次性返回信息有限的问题
"""

import sys
import time
import logging
from pathlib import Path

# 添加src目录到路径
sys.path.append(str(Path(__file__).parent / "src"))

from config.config import ensure_directories
from src.data_processor import GovernmentReportProcessor
from src.vector_store import get_vector_store
from src.query_router import get_query_router
from src.result_aggregator import get_result_aggregator
from src.api_client import get_api_client

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/government_rag.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GovernmentReportRAG:
    """政府工作报告RAG系统主类"""
    
    def __init__(self):
        """初始化RAG系统"""
        logger.info("🚀 初始化政府工作报告RAG系统...")
        
        # 确保目录存在
        ensure_directories()
        
        # 初始化组件
        self.vector_store = get_vector_store()
        self.query_router = get_query_router()
        self.result_aggregator = get_result_aggregator()
        self.api_client = get_api_client()
        
        # 系统状态
        self.is_ready = False
        
        logger.info("✅ RAG系统初始化完成")
    
    def setup_system(self, force_rebuild: bool = False) -> bool:
        """
        设置系统（处理文档、构建索引）
        
        Args:
            force_rebuild: 是否强制重建索引
            
        Returns:
            bool: 是否设置成功
        """
        logger.info("🔧 开始设置系统...")
        
        try:
            # 检查是否需要重建索引
            if force_rebuild or not self.vector_store.is_built():
                logger.info("📚 需要构建向量索引...")
                
                # 初始化文档处理器
                from config.config import DATA_PATHS, DOCUMENT_CONFIG
                processor = GovernmentReportProcessor(
                    raw_documents_path=DATA_PATHS["raw_documents"],
                    chunk_size=DOCUMENT_CONFIG["chunk_size"],
                    chunk_overlap=DOCUMENT_CONFIG["chunk_overlap"]
                )
                
                # 尝试加载已处理的数据
                chunks = processor.load_processed_data(DATA_PATHS["processed_data"])
                
                if not chunks or force_rebuild:
                    logger.info("📖 处理原始文档...")
                    chunks = processor.process_all_documents()
                    
                    if not chunks:
                        logger.error("❌ 文档处理失败，没有找到有效的文档")
                        return False
                    
                    # 保存处理结果
                    processor.save_processed_data(chunks, DATA_PATHS["processed_data"])
                
                # 构建向量索引
                logger.info("🔨 构建向量索引...")
                if not self.vector_store.build_index(chunks):
                    logger.error("❌ 向量索引构建失败")
                    return False
                
                # 保存索引
                if not self.vector_store.save_index():
                    logger.error("❌ 向量索引保存失败")
                    return False
            
            else:
                logger.info("📂 加载已有的向量索引...")
                if not self.vector_store.load_index():
                    logger.error("❌ 向量索引加载失败")
                    return False
            
            # 测试API连接
            logger.info("🔍 测试API连接...")
            if not self.api_client.test_connection():
                logger.error("❌ API连接测试失败")
                return False
            
            self.is_ready = True
            logger.info("✅ 系统设置完成，可以开始查询")
            
            # 显示系统统计信息
            stats = self.vector_store.get_statistics()
            logger.info(f"📊 系统统计: {stats}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 系统设置失败: {str(e)}")
            return False
    
    def query(self, user_query: str) -> dict:
        """
        处理用户查询
        
        Args:
            user_query: 用户查询文本
            
        Returns:
            dict: 查询结果
        """
        if not self.is_ready:
            return {
                "success": False,
                "error": "系统未就绪，请先运行setup_system()",
                "content": ""
            }
        
        logger.info(f"🔍 处理查询: {user_query}")
        start_time = time.time()
        
        try:
            # 1. 分析查询意图
            query_analysis = self.query_router.analyze_query(user_query)
            logger.info(f"🎯 查询分析: {query_analysis['intent']['type']}")
            
            # 2. 创建查询计划
            query_plan = self.query_router.create_query_plan(query_analysis)
            logger.info(f"📋 查询计划: {query_plan.batch_strategy} ({len(query_plan.batches)} 批次)")
            
            # 3. 执行查询计划
            execution_result = self.query_router.execute_query_plan(query_plan)
            
            if not execution_result["success"]:
                return {
                    "success": False,
                    "error": "查询执行失败",
                    "content": execution_result.get("content", ""),
                    "processing_time": time.time() - start_time
                }
            
            # 4. 聚合结果
            if len(query_plan.batches) > 1:
                logger.info("📊 聚合多批次结果...")
                aggregated_result = self.result_aggregator.aggregate_batch_results(
                    execution_result["batch_results"],
                    query_plan.output_format
                )
                final_content = aggregated_result.content
                provinces = aggregated_result.provinces
                processing_stats = aggregated_result.processing_stats
            else:
                final_content = execution_result["content"]
                provinces = execution_result.get("provinces", [])
                processing_stats = {
                    "success_rate": 1.0,
                    "total_batches": 1,
                    "successful_batches": 1
                }
            
            # 5. 优化输出长度
            if len(final_content) > 6000:  # 如果内容过长
                final_content = self.result_aggregator.optimize_for_token_limit(
                    final_content, max_tokens=4000
                )
            
            processing_time = time.time() - start_time
            
            logger.info(f"✅ 查询完成 ({processing_time:.2f}s): {len(provinces)} 个省份")
            
            return {
                "success": True,
                "content": final_content,
                "provinces": provinces,
                "query_type": query_analysis["intent"]["type"],
                "output_format": query_plan.output_format,
                "processing_time": processing_time,
                "processing_stats": processing_stats,
                "query_plan": {
                    "strategy": query_plan.batch_strategy,
                    "batches": len(query_plan.batches)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ 查询处理异常: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "content": "",
                "processing_time": time.time() - start_time
            }
    
    def get_system_status(self) -> dict:
        """获取系统状态信息"""
        status = {
            "is_ready": self.is_ready,
            "vector_store_built": self.vector_store.is_built() if self.vector_store else False,
            "api_available": False
        }
        
        if self.vector_store and self.vector_store.is_built():
            status["vector_stats"] = self.vector_store.get_statistics()
        
        # 测试API可用性
        try:
            if self.api_client:
                status["api_available"] = self.api_client.test_connection()
        except:
            status["api_available"] = False
        
        return status

def main():
    """主函数 - 命令行交互界面"""
    print("🏛️ 政府工作报告RAG系统")
    print("=" * 50)
    
    # 初始化系统
    rag_system = GovernmentReportRAG()
    
    # 设置系统
    print("\n🔧 正在设置系统...")
    if not rag_system.setup_system():
        print("❌ 系统设置失败，请检查配置和数据")
        return
    
    print("\n✅ 系统就绪！可以开始查询")
    print("\n💡 示例查询:")
    print("  - 列出各省的主要工作目标")
    print("  - 北京市的经济发展重点是什么")
    print("  - 对比广东和江苏的产业发展")
    print("  - 统计各省的环境保护措施")
    print("\n输入 'quit' 或 'exit' 退出系统")
    print("-" * 50)
    
    # 交互循环
    while True:
        try:
            user_input = input("\n🔍 请输入查询: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '退出']:
                print("👋 再见！")
                break
            
            if not user_input:
                continue
            
            print(f"\n⏳ 处理中...")
            
            # 执行查询
            result = rag_system.query(user_input)
            
            if result["success"]:
                print(f"\n📝 查询结果:")
                print(f"类型: {result.get('query_type', 'unknown')}")
                print(f"格式: {result.get('output_format', 'unknown')}")
                print(f"省份数: {len(result.get('provinces', []))}")
                print(f"处理时间: {result.get('processing_time', 0):.2f}s")
                print("-" * 30)
                print(result["content"])
                
                # 显示处理统计
                if "processing_stats" in result:
                    stats = result["processing_stats"]
                    print(f"\n📊 处理统计:")
                    print(f"成功率: {stats.get('success_rate', 0):.1%}")
                    print(f"批次: {stats.get('successful_batches', 0)}/{stats.get('total_batches', 0)}")
            else:
                print(f"\n❌ 查询失败: {result.get('error', '未知错误')}")
                if result.get('content'):
                    print(f"部分结果: {result['content']}")
        
        except KeyboardInterrupt:
            print("\n\n👋 用户中断，再见！")
            break
        except Exception as e:
            print(f"\n❌ 系统错误: {str(e)}")

if __name__ == "__main__":
    main() 