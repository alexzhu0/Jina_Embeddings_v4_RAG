# 🌐 Chinese Government Work Reports RAG System API Service

## 📋 Overview

API_KIT is the RESTful API service module for the Chinese Government Work Reports RAG system, providing standardized HTTP interfaces for frontend applications, automation tools, and third-party system integration.

### 🎯 Main Features
- **Intelligent Query Interface**: Support natural language queries of government work reports
- **System Status Monitoring**: Real-time system operation status
- **System Initialization**: Remote initialization and index rebuilding
- **Health Checks**: Service availability detection
- **CORS Support**: Support frontend application calls
- **Tunneling**: Integrated ngrok for external access

## 🏗️ Architecture Components

```
API_KIT/
├── api_server.py           # FastAPI server main program
├── api_models.py           # Pydantic data model definitions
├── requirements_api.txt    # API service dependencies
├── start_all.bat          # One-click startup script (API+ngrok)
├── start_api.bat          # API service startup script
├── start_ngrok.bat        # ngrok tunneling startup script
├── ngrok-v3-stable-windows-amd64/  # Tunneling tool
│   └── ngrok.exe
└── README.md              # This documentation
```

## 🚀 Quick Start

### Environment Requirements
- **Python 3.10+**
- **Conda Environment**: Recommended to use conda environment named `GovRag`
- **Dependencies**: Main system and API service dependencies installed

### 1. Environment Setup
```bash
# Create and activate conda environment
conda create -n GovRag python=3.10
conda activate GovRag

# Install main system dependencies
pip install -r ../requirements.txt

# Install API service dependencies
pip install -r requirements_api.txt
```

### 2. Startup Methods

#### Method 1: One-Click Start (Recommended)
```bash
# Windows users - One-click start API service and ngrok
start_all.bat
```

This script will automatically:
1. Start API server (background)
2. Wait 15 seconds for server startup
3. Call system initialization API
4. Start ngrok tunneling

#### Method 2: Start API Service Only
```bash
# Windows users
start_api.bat

# Or manual start
conda activate GovRag
cd ..
uvicorn API_KIT.api_server:app --host 0.0.0.0 --port 8000 --reload
```

#### Method 3: Production Environment Start
```bash
conda activate GovRag
cd ..
uvicorn API_KIT.api_server:app --host 0.0.0.0 --port 8000 --workers 4
```

### 3. Access API Documentation
After startup, visit these addresses:
- **API Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **OpenAPI Specification**: http://localhost:8000/openapi.json

## 📡 API Interface Documentation

### 1. Intelligent Query Interface
**POST** `/api/query`

Query government work report content with intelligent analysis and multiple query types support.

#### Request Parameters
```json
{
  "query": "What are Henan Province's key work for 2025"
}
```

#### Response Example
```json
{
  "success": true,
  "data": {
    "content": "Henan Province's key work for 2025 includes:\n1. Economic Development: GDP growth target 6.5%...",
    "provinces": ["Henan"],
    "query_type": "single_province",
    "output_format": "detailed",
    "processing_time": 2.34,
    "processing_stats": {
      "success_rate": 1.0,
      "total_batches": 1,
      "successful_batches": 1
    }
  },
  "message": "Query successful"
}
```

#### Intelligent Query Types
System automatically identifies query types and applies corresponding retrieval strategies:

- **Single Province Query**: "Henan Province's economic development focus"
  - Retrieval Strategy: Deep retrieval for single province (30 chunks)
  - Output Format: Detailed analysis report

- **Multi-Province Query**: "Compare industrial development between Guangdong and Jiangsu"
  - Retrieval Strategy: Balanced multi-province retrieval (15 chunks per province)
  - Output Format: Comparative analysis table

- **All Provinces Query**: "GDP growth targets of each province"
  - Retrieval Strategy: Global thematic retrieval
  - Output Format: Province list summary

- **Statistical Query**: "Statistics of provincial investment plans"
  - Retrieval Strategy: Statistical analysis retrieval
  - Output Format: Statistical summary information

#### System Optimization Features
- **Intelligent Layered Retrieval**: Automatically select optimal retrieval strategy based on query type
- **Adjacent Chunk Aggregation**: Ensure context continuity and completeness
- **Context Window Maximization**: Support maximum 100,000 character context
- **Intelligent Truncation**: Preserve high-value information, optimize output length

### 2. System Status Interface
**GET** `/api/status`

Get system operation status and detailed statistics.

#### Response Example
```json
{
  "success": true,
  "data": {
    "is_ready": true,
    "vector_store_built": true,
    "api_available": true,
    "vector_stats": {
      "total_chunks": 855,
      "total_provinces": 31,
      "index_size": "245MB",
      "embedding_dimension": 1024
    }
  }
}
```

### 3. System Initialization Interface
**POST** `/api/setup`

Initialize system or rebuild vector index.

#### Request Parameters
```json
{
  "force_rebuild": false
}
```

#### Response Example
```json
{
  "success": true,
  "data": {
    "is_ready": true,
    "vector_store_built": true,
    "api_available": true,
    "vector_stats": {
      "total_chunks": 855,
      "total_provinces": 31
    }
  }
}
```

### 4. Health Check Interface
**GET** `/api/health`

Check if API service is running normally.

#### Response Example
```json
{
  "status": "ok"
}
```

## 🔧 Configuration Instructions

### Server Configuration
```python
# Configuration in api_server.py
app = FastAPI(
    title="Chinese Government Work Reports RAG API",
    description="Provide standardized interfaces for AI frontends and automation tools",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Allow all origins
    allow_credentials=True,       # Allow credentials
    allow_methods=["*"],          # Allow all methods
    allow_headers=["*"],          # Allow all headers
)
```

### Port Configuration
- **Default Port**: 8000
- **Development Environment**: Support hot reload (`--reload`)
- **Production Environment**: Multi-process deployment (`--workers 4`)

### Conda Environment Configuration
```bash
# Recommended conda environment configuration
conda create -n GovRag python=3.10
conda activate GovRag

# Install CUDA support (if GPU available)
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia

# Install other dependencies
pip install -r requirements_api.txt
pip install -r ../requirements.txt
```

## 🌍 Tunneling (ngrok)

### 1. Install ngrok (First Use)
⚠️ **Important**: Due to GitHub file size limitations, need to manually download ngrok.exe

Please refer to: **[INSTALL_NGROK.md](INSTALL_NGROK.md)** to complete ngrok installation and configuration

### 2. Auto-Start ngrok
```bash
# Use one-click startup script
start_all.bat

# Or start ngrok separately
start_ngrok.bat
```

### 2. Manual ngrok Configuration
```bash
# Enter ngrok directory
cd ngrok-v3-stable-windows-amd64

# Add authtoken (need to register ngrok account)
ngrok.exe authtoken YOUR_AUTHTOKEN

# Start tunneling
ngrok.exe http 8000
```

### 3. Get Public Address
After ngrok starts, it will display public address, for example:
```
Forwarding    https://abc123.ngrok.io -> http://localhost:8000
```

### 4. External Access
- **API Documentation**: https://abc123.ngrok.io/docs
- **Query Interface**: https://abc123.ngrok.io/api/query

## 💻 Client Call Examples

### Python Client
```python
import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def query_government_report(query_text):
    """Query government work reports"""
    url = f"{BASE_URL}/api/query"
    payload = {
        "query": query_text
    }
    
    response = requests.post(url, json=payload)
    return response.json()

def check_system_status():
    """Check system status"""
    url = f"{BASE_URL}/api/status"
    response = requests.get(url)
    return response.json()

def initialize_system(force_rebuild=False):
    """Initialize system"""
    url = f"{BASE_URL}/api/setup"
    payload = {
        "force_rebuild": force_rebuild
    }
    
    response = requests.post(url, json=payload)
    return response.json()

# Usage example
if __name__ == "__main__":
    # Check system status
    status = check_system_status()
    print(f"System status: {status}")
    
    # If system not ready, initialize first
    if not status.get("data", {}).get("is_ready", False):
        print("Initializing system...")
        init_result = initialize_system()
        print(f"Initialization result: {init_result}")
    
    # Query example
    result = query_government_report("What are Henan Province's key work for 2025")
    print(json.dumps(result, indent=2, ensure_ascii=False))
```

### JavaScript Client
```javascript
// Query government work reports
async function queryGovernmentReport(queryText) {
    const response = await fetch('http://localhost:8000/api/query', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            query: queryText
        })
    });
    
    return await response.json();
}

// Check system status
async function checkSystemStatus() {
    const response = await fetch('http://localhost:8000/api/status');
    return await response.json();
}

// Initialize system
async function initializeSystem(forceRebuild = false) {
    const response = await fetch('http://localhost:8000/api/setup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            force_rebuild: forceRebuild
        })
    });
    
    return await response.json();
}

// Usage example
async function main() {
    try {
        // Check system status
        const status = await checkSystemStatus();
        console.log('System status:', status);
        
        // If system not ready, initialize first
        if (!status.data?.is_ready) {
            console.log('Initializing system...');
            const initResult = await initializeSystem();
            console.log('Initialization result:', initResult);
        }
        
        // Execute query
        const result = await queryGovernmentReport('What are Henan Province key work for 2025');
        console.log('Query result:', result);
    } catch (error) {
        console.error('Operation failed:', error);
    }
}

main();
```

### cURL Examples
```bash
# Check system status
curl -X GET "http://localhost:8000/api/status"

# Initialize system
curl -X POST "http://localhost:8000/api/setup" \
  -H "Content-Type: application/json" \
  -d '{"force_rebuild": false}'

# Query interface
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are Henan Province key work for 2025"}'

# Health check
curl -X GET "http://localhost:8000/api/health"
```

## 🔒 Security Configuration

### 1. Production Environment Security
```python
# Recommended production environment configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Restrict origin domains
    allow_credentials=True,
    allow_methods=["GET", "POST"],             # Restrict HTTP methods
    allow_headers=["*"],
)
```

### 2. API Key Authentication (Optional Extension)
```python
# Add API key middleware
@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    api_key = request.headers.get("X-API-Key")
    if not api_key or api_key != "your-secret-key":
        return JSONResponse(
            status_code=401,
            content={"error": "Invalid API key"}
        )
    response = await call_next(request)
    return response
```

### 3. Request Rate Limiting
```python
# Use slowapi for rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/query")
@limiter.limit("10/minute")  # Maximum 10 requests per minute
async def query_api(request: Request, query_request: QueryRequest):
    # ... query logic
```

## 📊 Performance Optimization

### 1. Server Optimization
```bash
# Production environment startup configuration
uvicorn API_KIT.api_server:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --max-requests 1000 \
  --max-requests-jitter 100
```

### 2. Memory Management
- RAG system uses singleton pattern, avoid repeated initialization
- Vector index cached in memory, improve query speed
- Regular GPU memory cache cleanup
- Support CUDA-accelerated Jina Embeddings v4 model

### 3. Concurrent Processing
- Support multi-process deployment
- Asynchronous processing for long-running queries
- Connection pool management for database connections

### 4. System Optimization Features
- **Intelligent Layered Retrieval Architecture**: Automatically select optimal strategy based on query type
- **Context Window Maximization**: Support 100,000 character large context processing
- **Adjacent Chunk Aggregation**: Ensure information continuity and completeness
- **Intelligent Truncation Strategy**: Preserve high-value information, optimize output length

## 🚨 Error Handling

### Common Error Codes
- **400**: Request parameter error
- **401**: Authentication failed (if API key enabled)
- **500**: Internal server error
- **503**: Service temporarily unavailable

### Error Response Format
```json
{
  "success": false,
  "error": "System not ready, please initialize first",
  "message": null,
  "data": null
}
```

## 🔧 Troubleshooting

### 1. Service Startup Failed
```bash
# Check port usage
netstat -ano | findstr :8000

# Check dependency installation
pip list | grep fastapi

# Check main system configuration
python -c "from main import GovernmentReportRAG; print('Import successful')"

# Check conda environment
conda info --envs
conda activate GovRag
```

### 2. Query Returns Error
- Check if system is initialized (`/api/status`)
- Confirm configuration file is set correctly
- Check if API key is valid
- View server logs
- Confirm main system dependencies are installed

### 3. Tunneling Issues
- Confirm ngrok authtoken is set
- Check firewall settings
- Confirm local service is running normally
- Check ngrok configuration file

### 4. Environment Issues
```bash
# Check conda environment
conda list -n GovRag

# Recreate environment
conda remove -n GovRag --all
conda create -n GovRag python=3.10
conda activate GovRag
pip install -r requirements_api.txt
pip install -r ../requirements.txt
```

## 📝 Development Guide

### 1. Add New Interface
```python
@app.post("/api/new-endpoint")
async def new_endpoint(request: NewRequest):
    try:
        # Processing logic
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### 2. Modify Data Models
```python
# Add new model in api_models.py
class NewRequest(BaseModel):
    parameter: str
    options: Optional[Dict] = None
```

### 3. Middleware Development
```python
@app.middleware("http")
async def custom_middleware(request: Request, call_next):
    # Pre-request processing
    response = await call_next(request)
    # Post-response processing
    return response
```

## 📋 Deployment Checklist

### Development Environment
- [ ] Install Python 3.10+
- [ ] Create conda environment (GovRag)
- [ ] Install dependency packages
- [ ] Configure config.py
- [ ] Start API service
- [ ] Test interface functionality

### Production Environment
- [ ] Configure reverse proxy (Nginx)
- [ ] Set up HTTPS certificates
- [ ] Configure firewall rules
- [ ] Set up system services
- [ ] Configure log rotation
- [ ] Set up monitoring alerts

## 🤝 Contribution Guide

1. Fork project
2. Create feature branch
3. Submit changes
4. Push to branch
5. Create Pull Request

## 📄 License

This project follows the LICENSE file in the project root directory.

## 🆘 Technical Support

For questions, please:
1. Check this README documentation
2. Check API documentation (http://localhost:8000/docs)
3. Check project main README
4. Check `logs/government_rag.log` log files
5. Refer to `OPTIMIZATION_SUMMARY.md` optimization report
6. Submit Issues to project repository

## 📈 Performance Metrics

### System Optimization Results
- **Average Information Volume Increase**: 100.0%
- **Average Retrieval Volume Increase**: 100.0% 
- **Context Capacity Increase**: 337.8%
- **API Output Capability Increase**: 60.0%

### Retrieval Capability Enhancement
- **Single Province Query**: From 10 to 30 chunks (+200%)
- **Multi-Province Query**: From 6 to 15 chunks (+150%)
- **Comparison Query**: From 8 to 25 chunks (+213%)
- **General Retrieval**: From 20 to 60 chunks (+200%)

---

**Last Updated**: July 2025
**Version**: 1.0.0 