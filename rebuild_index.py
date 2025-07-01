#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
重建向量索引 - 解决维度不匹配问题
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "src"))

def rebuild_index():
    print("🔧 开始重建向量索引...")
    
    try:
        # 导入必要模块
        from config.config import ensure_directories, DATA_PATHS, DOCUMENT_CONFIG
        from src.data_processor import GovernmentReportProcessor
        from src.vector_store import VectorStore
        from src.embedding_manager import get_embedding_manager
        
        # 确保目录存在
        ensure_directories()
        
        # 1. 检查当前embedding维度
        print("📏 检查embedding维度...")
        embedding_manager = get_embedding_manager()
        current_dim = embedding_manager.get_embedding_dimension()
        print(f"✅ 当前embedding维度: {current_dim}")
        
        # 2. 加载已处理的文档数据
        print("📚 加载文档数据...")
        processor = GovernmentReportProcessor(
            raw_documents_path=DATA_PATHS["raw_documents"],
            chunk_size=DOCUMENT_CONFIG["chunk_size"],
            chunk_overlap=DOCUMENT_CONFIG["chunk_overlap"]
        )
        
        chunks = processor.load_processed_data(DATA_PATHS["processed_data"])
        
        if not chunks:
            print("❌ 没有找到已处理的文档数据")
            print("🔄 开始处理原始文档...")
            chunks = processor.process_all_documents()
            
            if not chunks:
                print("❌ 文档处理失败")
                return False
            
            # 保存处理结果
            processor.save_processed_data(chunks, DATA_PATHS["processed_data"])
        
        print(f"✅ 加载了 {len(chunks)} 个文档块")
        
        # 3. 删除旧索引文件
        print("🗑️ 清理旧索引文件...")
        vector_store_path = Path(DATA_PATHS["vector_store"])
        for file in vector_store_path.glob("*"):
            if file.is_file():
                file.unlink()
                print(f"   删除: {file.name}")
        
        # 4. 创建新的向量存储
        print(f"🏗️ 创建新的向量存储 (维度: {current_dim})...")
        vector_store = VectorStore(
            store_path=str(DATA_PATHS["vector_store"]),
            embedding_dim=current_dim
        )
        
        # 5. 构建新索引
        print("🔨 构建新的向量索引...")
        if vector_store.build_index(chunks, embedding_manager=embedding_manager):
            print("✅ 索引构建成功")
            
            # 6. 保存索引
            print("💾 保存索引...")
            if vector_store.save_index():
                print("✅ 索引保存成功")
                
                # 7. 验证索引
                print("🔍 验证索引...")
                stats = vector_store.get_statistics()
                print(f"📊 索引统计:")
                print(f"   总块数: {stats['total_chunks']}")
                print(f"   省份数: {stats['total_provinces']}")
                print(f"   向量维度: {stats['embedding_dimension']}")
                
                # 8. 测试搜索
                print("🧪 测试搜索功能...")
                results = vector_store.search("经济发展", top_k=3)
                if results:
                    print(f"✅ 搜索测试成功，找到 {len(results)} 个结果")
                    for i, (chunk, score) in enumerate(results):
                        print(f"   {i+1}. {chunk.province}: {chunk.content[:50]}... (相似度: {score:.3f})")
                else:
                    print("⚠️ 搜索测试未找到结果")
                
                return True
            else:
                print("❌ 索引保存失败")
                return False
        else:
            print("❌ 索引构建失败")
            return False
            
    except Exception as e:
        print(f"❌ 重建索引失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = rebuild_index()
    if success:
        print("\n🎉 索引重建完成！现在可以正常使用RAG系统了。")
    else:
        print("\n❌ 索引重建失败，请检查错误信息。") 