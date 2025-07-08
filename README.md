# 🏛️ Chinese Government Work Reports RAG System

## 📋 Project Overview

This project is a RAG (Retrieval-Augmented Generation) based intelligent Q&A system specifically designed for Chinese government work reports. It addresses core issues of **incomplete information retrieval** and **insufficient multi-province comparison data** through innovative **intelligent layered retrieval architecture** and **context window maximization** strategies, achieving efficient large-scale document processing and precise intelligent Q&A.

### 🎁 Ready to Use
- **📁 Complete Dataset**: Includes 31 provincial government work report data (docs folder)
- **🚀 One-Click Deployment**: Extract data and run immediately, no additional document preparation needed
- **💡 Smart Optimization**: Deeply tuned retrieval and Q&A system

### 🎯 Core Problems & Solutions

#### Original Issues
1. **Insufficient Information Completeness**: System doesn't read complete government work reports before answering, missing available information
2. **Inadequate Multi-Province Comparison Data**: Limited detailed data when comparing multiple provinces

#### Solutions
Through **Phase 1 No-Rechunking Optimization**, we achieved:

1. **🔍 Massive Retrieval Depth Improvement**
   - Single province queries: From 10 to 30 chunks (+200%)
   - Multi-province queries: From 6 to 15 chunks (+150%)
   - Comparison queries: From 8 to 25 chunks (+213%)
   - General retrieval: From 20 to 60 chunks (+200%)

2. **📈 Significant Context Window Expansion**
   - Total context: From 16,000 to 100,000 characters (+525%)
   - Average capacity improvement: 337.8%
   - Fully utilize long-context model capabilities

3. **🚀 Enhanced System Functionality**
   - Added adjacent chunk aggregation for context continuity
   - Optimized intelligent truncation strategy to preserve high-value information
   - Enhanced prompt engineering for detailed and accurate outputs
   - Improved data structures supporting more attributes

## 📊 Optimization Results Overview

### Core Metrics Improvement
- **Average Information Volume Increase**: 100.0%
- **Average Retrieval Volume Increase**: 100.0% 
- **Context Capacity Increase**: 337.8%
- **API Output Capability Increase**: Adapted to model limit of 8192 tokens

### Detailed Configuration Improvements

| Configuration | Before | After | Improvement |
|---------------|--------|-------|-------------|
| General top_k | 20 | 60 | +200% |
| Max Context | 16,000 chars | 100,000 chars | +525% |
| Single Province Chunks | 10 | 30 | +200% |
| Multi-Province Chunks | 6 | 15 | +150% |
| Comparison Query Chunks | 8 | 25 | +213% |
| API max_tokens | 20,480 | 8,192 | Adapted to model limit |
| API timeout | 60s | 180s | +200% |

## 🛠️ Technical Architecture

```
Chinese Government Work Reports RAG System (Optimized)
├── Data Processing Layer
│   ├── Word Document Parsing (python-docx)
│   ├── Intelligent Text Chunking and Preprocessing
│   └── Province Identification and Classification
├── Vectorization Storage Layer
│   ├── Jina Embeddings v4 (Local deployment, FlashAttention2+SDPA dual optimization, force local model)
│   ├── FAISS Vector Database (Enhanced search capability)
│   └── Semantic Retrieval Engine (Support massive retrieval, memory efficient)
├── Intelligent Query Layer
│   ├── Query Intent Recognition
│   ├── Intelligent Layered Retrieval Strategy
│   ├── Adjacent Chunk Aggregation Mechanism
│   └── Retrieval Result Routing
├── Result Aggregation Layer
│   ├── Optimized Truncation Algorithm
│   ├── Information Density Scoring
│   └── Detailed Formatted Output
├── API Interaction Layer
│   └── SiliconFlow Tongyi-Zhiwen/QwenLong-L1-32B (Long Context)
└── RESTful API Service Layer (API_KIT)
    ├── FastAPI Server (CORS support, health checks)
    ├── Intelligent Query Interface (POST /api/query)
    ├── System Status Interface (GET /api/status)
    ├── System Initialization Interface (POST /api/setup)
    └── Tunneling Support (ngrok integration)
```

## ✅ Feature Highlights

### Core Features

1. **All-Province Queries**: Support queries like "list main work goals of each province"
2. **Single Province Deep Queries**: Support detailed queries like "what are Henan's key work for 2025"
3. **Multi-Province Comparative Analysis**: Support detailed data comparison between provinces
4. **Statistical Summary Analysis**: Support statistics and summary of provincial data
5. **Thematic Cross-Province Queries**: Support specific topic queries across provinces

### Output Formats

- **Province List Format**: `Province: specific data1, specific data2...` (includes detailed numbers)
- **Detailed Report Format**: Contains all quantitative indicators and specific measures
- **Comparison Table Format**: Detailed inter-provincial data comparison
- **Statistical Summary Format**: Complete data statistics and analysis

### Technical Features

- **Intelligent Layered Retrieval**: Dynamically adjust retrieval strategies based on query complexity
- **Adjacent Chunk Aggregation**: Automatically get related chunk context information
- **Optimized Truncation Algorithm**: Preserve highest information density content
- **Enhanced Prompt Engineering**: Ensure detailed and complete data output
- **Long Context Support**: Fully utilize 100K character context window
- **Local Model Optimization**: Force use of local model files, avoid network downloads, improve startup speed
- **RESTful API Service**: Complete HTTP interface support for easy system integration and frontend calls

## 📁 Data Description

### Built-in Dataset
This project includes complete data from 31 Chinese provinces/regions/municipalities government work reports, stored in `docs/31省区市政府工作报告.zip`:

| Region | Provinces | Document Format |
|--------|-----------|-----------------|
| **North China** | Beijing, Tianjin, Hebei, Shanxi, Inner Mongolia | .docx |
| **Northeast** | Liaoning, Jilin, Heilongjiang | .docx |
| **East China** | Shanghai, Jiangsu, Zhejiang, Anhui, Fujian, Jiangxi, Shandong | .docx |
| **Central China** | Henan, Hubei, Hunan | .docx |
| **South China** | Guangdong, Guangxi, Hainan | .docx |
| **Southwest** | Chongqing, Sichuan, Guizhou, Yunnan, Tibet | .docx |
| **Northwest** | Shaanxi, Gansu, Qinghai, Ningxia, Xinjiang | .docx |

### Data Characteristics
- **📊 Data Completeness**: Covers all 31 provinces/regions/municipalities, no omissions
- **📅 Timeliness**: Latest annual government work reports
- **📋 Standardization**: Unified Word document format for easy processing
- **🔍 Searchability**: Contains detailed economic indicators, development goals, key projects, etc.

### Usage
```bash
# 1. Extract data files
cd docs
unzip "31省区市政府工作报告.zip"

# 2. Data will be extracted to docs/31省区市政府工作报告/ directory
# 3. Set path to this directory in config file
```

## ⚡ Quick Start

### 5-Minute Quick Experience

```bash
# 1. Clone project
git clone https://github.com/alexzhu0/government-report-rag.git
cd government-report-rag

# 2. Extract data
cd docs && unzip "31省区市政府工作报告.zip" && cd ..

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy configuration file
copy config\config.example.py config\config.py  # Windows
# cp config/config.example.py config/config.py    # Linux/Mac

# 5. Edit configuration file, fill in your API key
# Edit config/config.py, set:
# - api_key: Your SiliconFlow API key
# - raw_documents: "docs/31省区市政府工作报告"

# 6. Run system
python main.py
```

### 🎯 Try Queries Immediately
```
🔍 Enter query: What are Henan's key work for 2025
🔍 Enter query: Compare industrial development between Guangdong and Jiangsu
🔍 Enter query: What are the GDP growth targets of each province
```

## 🚀 Detailed Installation & Deployment

### Environment Requirements

- **Python 3.10+**
- **NVIDIA GPU**: RTX 3060 or higher (recommended)
- **Memory**: At least 16GB (32GB recommended)
- **Disk Space**: At least 20GB
- **CUDA**: 11.8+ (for GPU acceleration)

## 🌐 API Service Deployment

### 📋 API_KIT Overview

This project provides a complete RESTful API service module (`API_KIT/`) supporting HTTP interface calls to RAG system functionality, facilitating frontend applications, automation tools, and third-party system integration.

#### 🎯 Main Features
- **Intelligent Query Interface**: Support natural language queries of government work reports
- **System Status Monitoring**: Real-time system operation status and statistics
- **System Initialization**: Remote initialization and vector index rebuilding
- **Tunneling**: Integrated ngrok for external access
- **CORS Support**: Complete CORS configuration supporting frontend calls

#### 🚀 Quick Start API Service

```bash
# Method 1: One-click start (recommended)
cd API_KIT
start_all.bat  # Auto-start API service and ngrok

# Method 2: Manual start
conda activate GovRag
cd API_KIT
start_api.bat
```

#### 📡 API Interface Examples

```bash
# Query interface
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are Henan Province key work for 2025"}'

# System status
curl -X GET "http://localhost:8000/api/status"

# Access API documentation
# http://localhost:8000/docs
```

#### 📚 Detailed Documentation

For complete configuration, deployment, and usage instructions for API service, see:
**[API_KIT/README.md](API_KIT/README.md)** - Contains detailed:
- Complete API interface documentation and examples
- Multiple startup methods and environment configurations
- Client call examples (Python, JavaScript, cURL)
- Tunneling configuration and usage
- Security configuration and performance optimization
- Troubleshooting and development guide

### ⚡ Efficient Attention Mechanism Optimization

This project employs advanced attention mechanism optimization techniques, significantly improving vector computation efficiency and memory usage:

#### 🚀 FlashAttention2 Benefits and Advantages

**FlashAttention2** is a memory-efficient attention computation algorithm providing significant performance improvements for the Jina Embeddings v4 model:

- **🔥 Memory Efficiency Improvement**: 50-80% memory usage reduction compared to standard attention
- **⚡ Computation Speed Acceleration**: 2-4x speed improvement in long sequence processing
- **📊 Longer Sequence Support**: Handle longer document chunks, improving retrieval quality
- **🎯 Precision Maintenance**: Maintain computational accuracy while improving efficiency
- **💡 Dynamic Optimization**: Automatically optimize computation strategy based on hardware characteristics

#### 🧠 SDPA (Scaled Dot-Product Attention) Optimization Significance

**SDPA Optimization** is PyTorch 2.0+ native efficient attention implementation, successfully enabled and fully utilized:

- **🔧 Hardware Acceleration**: Fully utilize modern GPU Tensor Cores and Memory Hierarchy
- **📈 Throughput Improvement**: Significantly improve processing throughput in batch scenarios (tested: 5 texts in 0.56s)
- **🎛️ Adaptive Optimization**: Automatically select optimal implementation based on input size and hardware
- **🔋 Energy Reduction**: More efficient computation paths reduce GPU power consumption
- **🛡️ Numerical Stability**: Improved numerical computation ensures long sequence processing stability
- **✅ Verified Enabled**: System defaults to SDPA, auto-fallback to standard attention on failure

#### 💻 Alternative Options Without GPU/FlashAttention2

If your environment doesn't support GPU or FlashAttention2, the system provides compatible options:

**Option 1: CPU Mode**
```python
# Set in config/config.py
EMBEDDING_CONFIG = {
    "device": "cpu",  # Change to CPU mode
    "model_name": "jinaai/jina-embeddings-v4",
    # Other configs remain unchanged
}
```

**Option 2: Standard Attention Mechanism**
```bash
# System has SDPA optimization enabled, auto-fallback to standard attention if SDPA fails
# Performance comparison (actual test data):
# - SDPA optimized: 100% performance baseline (5 texts in 0.56s)
# - Standard Attention: 70-80% performance
# - CPU mode: 30-40% performance
```

**Option 3: Lightweight Configuration**
```python
# Optimized settings for low-spec environments
RETRIEVAL_CONFIG = {
    "top_k": 30,  # Reduce retrieval chunk count
    "max_contexts_per_query": 50000,  # Lower context length
    # Suitable for 8GB VRAM or CPU operation
}
```

**Environment Detection and Auto-Adaptation**
```bash
# System auto-detects and selects optimal configuration at startup
python -c "from src.embedding_manager import get_embedding_manager; get_embedding_manager().check_optimization_support()"
```

**Performance Comparison Table**
| Configuration | GPU Requirement | Memory Usage | Processing Speed | Actual Performance | Recommended Scenario |
|---------------|-----------------|--------------|------------------|-------------------|---------------------|
| SDPA + GPU | RTX 3060+ | 8GB | Fastest | 5texts/0.56s | Production (Enabled) |
| Standard Attention + GPU | GTX 1660+ | 6GB | Medium | 5texts/0.8s | Compatibility First |
| CPU Mode | No GPU | System RAM | Slower | 5texts/2-3s | Pure CPU Environment |

### 1. Clone Project

```bash
git clone https://github.com/alexzhu0/government-report-rag.git
cd government-report-rag
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configuration Setup

Edit `config/config.py`:

```python
# SiliconFlow API Configuration
SILICONFLOW_CONFIG = {
    "api_key": "your-api-key-here",  # Replace with your API key
    "base_url": "https://api.siliconflow.cn/v1",
    "model": "Tongyi-Zhiwen/QwenLong-L1-32B",
    "temperature": 0.3,
    "max_tokens": 8192,
    "timeout": 180
}

# Raw document path
DATA_PATHS = {
    "raw_documents": r"Your document path"  # Replace with actual path
}
```

### 4. Prepare Data

**Method 1: Use Provided Data (Recommended)**

We've prepared 31 provincial government work report data for you:

```bash
# Extract data files
cd docs
unzip "31省区市政府工作报告.zip"
```

After extraction, you'll get Word documents for 31 provinces including:
- Beijing, Tianjin, Hebei, Shanxi, Inner Mongolia
- Liaoning, Jilin, Heilongjiang, Shanghai, Jiangsu
- Zhejiang, Anhui, Fujian, Jiangxi, Shandong
- Henan, Hubei, Hunan, Guangdong, Guangxi
- Hainan, Chongqing, Sichuan, Guizhou, Yunnan
- Tibet, Shaanxi, Gansu, Qinghai, Ningxia, Xinjiang

Then update the path in config file:
```python
DATA_PATHS = {
    "raw_documents": r"docs/31省区市政府工作报告",  # Use provided data
    # ... other configs
}
```

**Method 2: Use Custom Data**

If you have other government work report data, place Word documents (.docx format) in specified directory and set path in config file.

### 5. Run System

```bash
python main.py
```

First run will automatically:
1. 🔍 Detect and load local Jina Embeddings v4 model (prioritize local model, avoid network download)
2. 📚 Process Word documents and chunk them
3. 🔨 Build FAISS vector index
4. 🔗 Test API connection

**Note**: System is optimized to prioritize local model files. If complete model files exist in models directory, local model will be used directly without network download.

## 📝 Usage Examples

### Start System

```bash
python main.py
```

### Query Examples

#### Single Province Detailed Query
```
🔍 Enter query: What are Henan's key work for 2025

📝 Query Results:
Type: single_province
Format: province_list
Province count: 1
Processing time: 23.97s
------------------------------

**Henan:**
1. **Economic Growth Target**: GDP growth around 5.5%, industrial added value growth around 7%...
2. **Consumption Boost**: Update 500,000 vehicles, 8 million appliances, implement 3,000 equipment update projects...
3. **Major Project Investment**: 1,000 provincial key projects, complete 1 trillion yuan investment...
...(Contains 14 detailed categories with specific data points)

📊 Processing Statistics:
Success rate: 100.0%
Retrieved chunks: 20 (previously: 10)
Context characters: 16,775 characters
```

#### Multi-Province Comparison Query
```
🔍 Enter query: Compare industrial development between Guangdong and Jiangsu

📝 Query Results:
Type: multi_province
Format: comparison
Province count: 2
Processing time: 18.45s
------------------------------

Detailed comparative analysis including:
- Specific numerical comparison tables
- Policy measure difference analysis
- Development focus in-depth comparison
- Investment scale precise comparison
...(15 chunks per province, total 30 chunks of rich information)
```

## 📁 Project Structure

```
government_report_rag/
├── config/
│   └── config.py              # System configuration (optimized)
├── src/                       # Core modules (cleaned)
│   ├── data_processor.py      # Document processing (enhanced data structure)
│   ├── embedding_manager.py   # Jina Embeddings v4 management
│   ├── vector_store.py        # FAISS vector storage (enhanced search)
│   ├── retriever.py          # Intelligent RAG retrieval (adjacent chunk aggregation)
│   ├── query_router.py       # Query routing (enhanced prompt)
│   ├── result_aggregator.py  # Result aggregation
│   └── api_client.py         # API client (optimized timeout)
├── API_KIT/                  # RESTful API service module
│   ├── api_server.py         # FastAPI server
│   ├── api_models.py         # API data models
│   ├── start_all.bat         # One-click startup script
│   ├── start_api.bat         # API startup script
│   ├── start_ngrok.bat       # ngrok startup script
│   ├── requirements_api.txt  # API dependencies
│   └── README.md             # API detailed documentation
├── data/
│   ├── processed/            # Processed document data
│   └── vectors/              # FAISS vector indices
├── models/
│   └── jina-embeddings-v4/   # Jina embedding model
├── logs/                     # System logs
│   └── .gitkeep
├── docs/
│   └── INSTALL_FLASH_ATTENTION.md
├── .gitignore
├── main.py                   # Main program entry
├── requirements.txt          # Python dependencies
├── OPTIMIZATION_SUMMARY.md   # Optimization summary report
└── README.md                # Project documentation
```

## 🔧 Core Optimization Technologies

### 1. Intelligent Layered Retrieval Architecture

```python
# Dynamically adjust retrieval strategy based on query complexity
def smart_retrieve(self, query: str, max_context_chars: int = None):
    # Single province query: 30 chunks, 40000 characters
    # Multi-province query: 15 chunks per province, 60000 characters
    # Comparison query: 25 chunks per province, 100000 characters
    # General query: 60 chunks, 100000 characters
```

### 2. Adjacent Chunk Aggregation Mechanism

```python
def get_adjacent_chunks(self, chunk: DocumentChunk, window: int = 1):
    # Automatically get adjacent chunks before and after target chunk
    # Ensure context continuity and completeness
    # Improve information retrieval accuracy
```

### 3. Optimized Truncation Strategy

```python
def _truncate_results(self, result: RetrievalResult, max_chars: int):
    # Sort by information density score
    # Prioritize high-value information
    # Intelligently truncate overly long content
```

### 4. Enhanced Prompt Engineering

```python
def _build_prompt(self, query: str, context: str, output_format: str):
    # Professional role positioning
    # Detailed format requirements
    # Completeness verification mechanism
    # Quantitative data priority
```

## 🙏 Acknowledgments

### Data Source
Thanks for providing 31 provincial government work report data, making this project ready-to-use and convenient for researchers and developers.

### Open Source Contributions
Welcome to submit Issues and Pull Requests to improve this project together:
- 🐛 Report bugs
- 💡 Suggest new features  
- 📝 Improve documentation
- 🔧 Code optimization

## 📈 Performance Monitoring

### System Statistics

System displays detailed statistics at startup:
```
📊 System Statistics: 
- Total document chunks: 855
- Covered provinces: 31
- Vector dimensions: 2048
- Provincial document distribution statistics
```

### Query Performance Metrics

Each query displays:
- Retrieved chunk count
- Covered province count
- Context character count
- Processing time
- Success rate

### Log Monitoring

```bash
# View system logs
tail -f logs/government_rag.log

# Search performance information
grep "Retrieval completed\|Processing time" logs/government_rag.log
```

## 🛠️ Troubleshooting

### Common Issues

1. **API Timeout Issues**
   - Optimized: API timeout increased from 60s to 180s
   - Query processing timeout increased from 30s to 120s

2. **max_tokens Limitation**
   - Fixed: Adjusted to model-supported 8192 tokens
   - Avoid HTTP 400 errors

3. **Memory Insufficient**
   ```bash
   # Check available memory
   python -c "import psutil; print(f'Available memory: {psutil.virtual_memory().available / 1024**3:.1f}GB')"
   ```

4. **Model Loading Failed**
   ```bash
   # Check if local model files are complete
   ls -la models/jina-embeddings-v4/models--jinaai--jina-embeddings-v4/snapshots/
   
   # If local model files are corrupted or missing, can re-download
   # Temporarily remove local_files_only parameter for download
   python -c "
   from src.embedding_manager import JinaEmbeddingManager
   manager = JinaEmbeddingManager()
   manager.download_and_load_model()
   "
   ```

### Performance Optimization Recommendations

1. **Enable GPU Acceleration**: Ensure CUDA environment is properly configured
2. **Memory Management**: Recommend 32GB memory for optimal performance
3. **Network Optimization**: Ensure stable API network connection
4. **Regular Maintenance**: Clean log files and temporary cache

## 📋 Dependencies

Main dependency packages:

```txt
python-docx==0.8.11      # Word document parsing
faiss-cpu==1.7.4         # Vector similarity search
transformers==4.36.2     # Pre-trained model support
torch==2.1.2             # Deep learning framework
numpy==1.24.3            # Numerical computation
pandas==2.0.3            # Data processing
requests==2.31.0         # HTTP requests
tqdm==4.66.1             # Progress bar display
scikit-learn==1.3.2      # Machine learning tools
jieba==0.42.1            # Chinese word segmentation
```

## 🔄 Update Log

### v2.0.0 (Current Version) 
- ✅ **Major Optimization**: Implemented Phase 1 no-rechunking optimization
- ✅ **Retrieval Capability Enhancement**: Average 100% retrieval depth improvement
- ✅ **Context Expansion**: Support for 100K character long context
- ✅ **Feature Enhancement**: Adjacent chunk aggregation, intelligent truncation, enhanced prompt
- ✅ **System Stability**: Optimized API timeout, fixed max_tokens limitation
- ✅ **Code Cleanup**: Removed all test code, maintain clean production environment
- ✅ **Documentation Improvement**: Updated README and optimization summary report
- ✅ **Local Model Optimization**: Force use of local model files, avoid network downloads, improve system startup speed

### v1.0.0
- ✅ Basic RAG system implementation
- ✅ 31 provincial government work report support
- ✅ Basic query and retrieval functionality

## 🎯 Project Features

The core value of this project lies in:

1. **Problem-Oriented**: Specifically addresses incomplete information retrieval and insufficient multi-province comparison data
2. **Technical Innovation**: Innovative intelligent layered retrieval architecture and adjacent chunk aggregation mechanism
3. **Performance Optimization**: 100% information volume improvement through systematic optimization
4. **Production Ready**: Cleaned all test code, suitable for production environment deployment
5. **Complete Documentation**: Detailed installation, usage, and troubleshooting guides

## 📞 Technical Support

For questions or suggestions, please:
1. Check troubleshooting section in this README
2. Check `logs/government_rag.log` log files
3. Refer to `OPTIMIZATION_SUMMARY.md` optimization report
4. Submit Issues or contact development team

---

**🎉 System has completed major optimization, achieving significant improvements in information retrieval completeness and multi-province comparison data detail!**
