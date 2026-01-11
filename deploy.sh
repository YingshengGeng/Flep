#!/bin/bash

# ================= 配置区域 =================

# 1. 定义服务器 IP 和对应的 Label 值
declare -A SERVERS
SERVERS["10.0.0.11"]="0x2501"
SERVERS["10.0.0.12"]="0x2502"
SERVERS["10.0.0.13"]="0x2503"

# 2. 远程服务器配置
REMOTE_USER="root"              # 目标路径是 /root/..., 所以必须用 root
REMOTE_PATH="/root/code_latency" # 指定的远程目标目录

# ================= 逻辑区域 =================

# 创建临时构建目录
TEMP_DIR=$(mktemp -d)
echo "📦 创建构建环境: $TEMP_DIR"

# 遍历每台服务器
for IP in "${!SERVERS[@]}"; do
    LABEL=${SERVERS[$IP]}
    echo "--------------------------------------------------"
    echo "🚀 目标服务器: $IP | 设定 Label: $LABEL"

    # A. 【关键】全量复制
    # 将当前目录(.)下的所有内容复制到临时目录
    # --exclude 排除 git 目录和脚本本身，避免死循环或传输垃圾文件
    mkdir -p "$TEMP_DIR/$IP"
    rsync -av --exclude='.git' --exclude='deploy.sh' . "$TEMP_DIR/$IP" > /dev/null

    # B. 仅修改 .p4 文件中的 Label
    echo "   🔧 正在扫描并修改 .p4 文件..."
    find "$TEMP_DIR/$IP" -type f -name "*.p4" | while read -r FILE; do
        # 提取文件名用于显示
        FNAME=$(basename "$FILE")
        
        # 替换逻辑 (兼容 Mac 和 Linux)
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s/LOCAL_LABEL = 0x[0-9a-fA-F]\{4\}/LOCAL_LABEL = $LABEL/g" "$FILE"
        else
            sed -i "s/LOCAL_LABEL = 0x[0-9a-fA-F]\{4\}/LOCAL_LABEL = $LABEL/g" "$FILE"
        fi
        
        # 验证修改（仅打印匹配行）
        MATCH=$(grep "LOCAL_LABEL" "$FILE" | head -n 1)
        if [ ! -z "$MATCH" ]; then
             echo "      ✅ $FNAME -> $MATCH"
        fi
    done

    # C. 发送并覆盖到远程目录
    echo "   📤 正在覆盖同步到 $IP:$REMOTE_PATH ..."
    
    # 1. 确保远程目录存在
    ssh "$REMOTE_USER@$IP" "mkdir -p $REMOTE_PATH"
    
    # 2. 传输文件 (使用 SCP 覆盖)
    # "$TEMP_DIR/$IP/"* 这里的星号确保只拷贝目录里的内容，而不是目录本身
    scp -r -q "$TEMP_DIR/$IP/"* "$REMOTE_USER@$IP:$REMOTE_PATH"
    
    if [ $? -eq 0 ]; then
        echo "   ✨ $IP 部署完成!"
    else
        echo "   ❌ $IP 连接失败，请检查网络或 SSH Key。"
    fi
done

# 清理临时文件
rm -rf "$TEMP_DIR"
echo "--------------------------------------------------"
echo "✅ 所有文件已覆盖传输至 /root/code_latency"