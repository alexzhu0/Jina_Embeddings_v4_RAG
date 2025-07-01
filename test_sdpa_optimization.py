#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试SDPA优化是否正常工作
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "src"))

import torch
import time
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_sdpa_optimization():
    """测试SDPA优化"""
    print("🚀 测试SDPA优化")
    print("=" * 50)
    
    try:
        # 检查CUDA可用性
        print(f"🎮 CUDA可用: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"🎮 GPU设备: {torch.cuda.get_device_name(0)}")
            print(f"🎮 GPU内存: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        
        # 检查SDPA支持
        print(f"⚡ SDPA可用: {hasattr(torch.nn.functional, 'scaled_dot_product_attention')}")
        
        # 1. 测试SDPA实现
        print("\n📋 测试1: SDPA实现")
        from src.embedding_manager import JinaEmbeddingManager
        
        sdpa_manager = JinaEmbeddingManager(attn_implementation="sdpa")
        print(f"✅ SDPA Manager创建成功")
        print(f"⚡ Attention实现: {sdpa_manager.attn_implementation}")
        
        # 加载模型
        print("📥 加载模型...")
        start_time = time.time()
        success = sdpa_manager.download_and_load_model()
        load_time = time.time() - start_time
        
        if success:
            print(f"✅ 模型加载成功 ({load_time:.2f}s)")
            print(f"⚡ 最终使用的attention: {sdpa_manager.attn_implementation}")
        else:
            print("❌ 模型加载失败")
            return False
        
        # 2. 测试编码性能
        print("\n📋 测试2: 编码性能")
        test_texts = [
            "政府工作报告中提到的经济发展目标",
            "推进高质量发展，加快构建新发展格局",
            "深化改革开放，激发市场主体活力",
            "保障和改善民生，增进人民福祉",
            "加强生态文明建设，推动绿色发展"
        ]
        
        # 编码测试
        print("🔄 编码测试文本...")
        start_time = time.time()
        embeddings = sdpa_manager.encode_texts(test_texts, show_progress=True)
        encode_time = time.time() - start_time
        
        print(f"✅ 编码完成 ({encode_time:.2f}s)")
        print(f"📐 向量形状: {embeddings.shape}")
        print(f"📊 平均每个文本: {encode_time/len(test_texts):.3f}s")
        
        # 3. 测试查询编码
        print("\n📋 测试3: 查询编码")
        query = "经济发展政策有哪些？"
        
        start_time = time.time()
        query_embedding = sdpa_manager.encode_query(query)
        query_time = time.time() - start_time
        
        print(f"✅ 查询编码完成 ({query_time:.3f}s)")
        print(f"📐 查询向量形状: {query_embedding.shape}")
        
        # 4. 测试相似度计算
        print("\n📋 测试4: 相似度计算")
        similarities = []
        for i, text in enumerate(test_texts):
            similarity = sdpa_manager.calculate_similarity(query_embedding, embeddings[i])
            similarities.append((text, similarity))
            print(f"   {text[:30]}... : {similarity:.3f}")
        
        # 排序显示最相似的
        similarities.sort(key=lambda x: x[1], reverse=True)
        print(f"🏆 最相似: {similarities[0][0][:50]}... ({similarities[0][1]:.3f})")
        
        # 5. 内存使用情况
        if torch.cuda.is_available():
            print(f"\n📊 GPU内存使用:")
            print(f"   已分配: {torch.cuda.memory_allocated() / 1024**2:.1f} MB")
            print(f"   已缓存: {torch.cuda.memory_reserved() / 1024**2:.1f} MB")
        
        # 6. 模型信息
        print(f"\n📋 模型信息:")
        model_info = sdpa_manager.get_model_info()
        for key, value in model_info.items():
            if key == "parameter_count":
                print(f"   {key}: {value:,}")
            else:
                print(f"   {key}: {value}")
        
        print("\n🎉 SDPA优化测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_attention_comparison():
    """比较不同attention实现的性能"""
    print("\n🔄 比较不同attention实现")
    print("=" * 50)
    
    test_texts = ["测试文本" + str(i) for i in range(10)]
    results = {}
    
    for attn_type in ["sdpa", "eager"]:
        print(f"\n📋 测试 {attn_type} attention:")
        
        try:
            from src.embedding_manager import JinaEmbeddingManager
            manager = JinaEmbeddingManager(attn_implementation=attn_type)
            
            # 加载模型
            start_time = time.time()
            success = manager.download_and_load_model()
            load_time = time.time() - start_time
            
            if not success:
                print(f"❌ {attn_type} 模型加载失败")
                continue
            
            print(f"✅ 模型加载: {load_time:.2f}s")
            print(f"⚡ 实际使用的attention: {manager.attn_implementation}")
            
            # 编码性能测试
            start_time = time.time()
            embeddings = manager.encode_texts(test_texts, show_progress=False)
            encode_time = time.time() - start_time
            
            results[attn_type] = {
                "load_time": load_time,
                "encode_time": encode_time,
                "actual_attention": manager.attn_implementation,
                "success": True
            }
            
            print(f"✅ 编码时间: {encode_time:.3f}s")
            print(f"📊 平均每文本: {encode_time/len(test_texts):.4f}s")
            
        except Exception as e:
            print(f"❌ {attn_type} 测试失败: {e}")
            results[attn_type] = {"success": False, "error": str(e)}
    
    # 比较结果
    print(f"\n📊 性能比较:")
    print("-" * 50)
    for attn_type, result in results.items():
        if result.get("success"):
            print(f"{attn_type:10} | 加载: {result['load_time']:6.2f}s | 编码: {result['encode_time']:6.3f}s | 实际: {result['actual_attention']}")
        else:
            print(f"{attn_type:10} | ❌ 失败: {result.get('error', 'Unknown')}")

if __name__ == "__main__":
    print("🧪 SDPA优化测试套件")
    print("=" * 60)
    
    # 基础测试
    success = test_sdpa_optimization()
    
    if success:
        # 性能比较测试
        test_attention_comparison()
    
    print("\n" + "=" * 60)
    print("🏁 测试完成") 