# 🌐 ngrok 安装配置指南

## 📋 说明

由于GitHub对单个文件大小的限制（25MB），`ngrok.exe`文件无法直接包含在仓库中。请按照以下步骤手动下载和配置ngrok。

## 📥 下载ngrok

### 方式1：官方下载（推荐）
1. 访问 [ngrok官网](https://ngrok.com/download)
2. 选择Windows版本下载
3. 解压后将`ngrok.exe`文件放入`API_KIT/ngrok-v3-stable-windows-amd64/`目录

### 方式2：直接下载链接
```bash
# 下载Windows版本
curl -o ngrok.zip https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip

# 解压到指定目录
unzip ngrok.zip -d API_KIT/ngrok-v3-stable-windows-amd64/
```

## 🔧 配置ngrok

### 1. 注册ngrok账号
1. 访问 [ngrok官网](https://ngrok.com/)
2. 注册免费账号
3. 获取您的authtoken

### 2. 配置authtoken
```bash
# 进入ngrok目录
cd API_KIT/ngrok-v3-stable-windows-amd64

# 配置authtoken（替换为您的实际token）
ngrok.exe authtoken YOUR_AUTHTOKEN_HERE
```

### 3. 测试ngrok
```bash
# 测试ngrok是否正常工作
ngrok.exe http 8000
```

## 🚀 使用方式

配置完成后，您可以：

### 自动启动（推荐）
```bash
# 使用一键启动脚本
start_all.bat
```

### 手动启动
```bash
# 单独启动ngrok
start_ngrok.bat

# 或直接使用命令
cd API_KIT/ngrok-v3-stable-windows-amd64
ngrok.exe http 8000
```

## 📁 目录结构

配置完成后，目录结构应该如下：
```
API_KIT/
└── ngrok-v3-stable-windows-amd64/
    ├── ngrok.exe          # 您下载的ngrok可执行文件
    └── .ngrok2/           # ngrok配置目录（自动生成）
        └── ngrok.yml      # ngrok配置文件
```

## 🔒 安全说明

- **authtoken保护**：请妥善保管您的authtoken，不要在公共代码中暴露
- **免费限制**：ngrok免费版有连接数和带宽限制
- **HTTPS支持**：ngrok提供免费的HTTPS隧道

## 🆘 故障排除

### 常见问题

1. **ngrok.exe不存在**
   - 确认已下载ngrok.exe到正确目录
   - 检查文件权限是否正确

2. **authtoken未配置**
   - 运行`ngrok.exe authtoken YOUR_TOKEN`配置
   - 检查`~/.ngrok2/ngrok.yml`文件是否存在

3. **端口冲突**
   - 确认API服务运行在8000端口
   - 可以修改为其他端口：`ngrok.exe http 其他端口`

4. **网络连接问题**
   - 检查防火墙设置
   - 确认网络连接正常

### 获取帮助

如果遇到问题，请：
1. 查看ngrok官方文档
2. 检查API_KIT/README.md中的详细说明
3. 在项目中提交Issue

---

**注意**：这是一个一次性配置，配置完成后可以正常使用所有API_KIT功能。 