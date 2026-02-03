# Stage 1: Build frontend
FROM node:20-slim AS frontend-builder

WORKDIR /app/frontend

# Copy package files
COPY frontend-vue/package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY frontend-vue/ ./

# Build frontend
RUN npm run build

# Stage 2: Production
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖和中文字体
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY backend/ .

# 复制工具脚本
COPY tools/ /app/tools/

# 复制构建好的前端代码
COPY --from=frontend-builder /app/frontend/dist /app/frontend

# 创建可写的配置目录
RUN mkdir -p /config

# 暴露端口
EXPOSE 8000

# 启动（禁用Uvicorn访问日志，减少日志噪音）
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
