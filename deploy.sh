#!/bin/bash

# ================= 配置区域 =================
declare -A SERVERS
SERVERS["10.0.0.11"]="0x2501"
SERVERS["10.0.0.12"]="0x2502"
SERVERS["10.0.0.13"]="0x2503"

REMOTE_USER="root"
REMOTE_PATH="/home/ruijie/onl-bf-sde/code_latency"

# ================= 逻辑区域 =================

TEMP_DIR=$(mktemp -d)
echo "📦 创建构建环境: $TEMP_DIR"

for IP in "${!SERVERS[@]}"; do
    LABEL=${SERVERS[$IP]}
    echo "--------------------------------------------------"
    echo "🚀 目标服务器: $IP | 设定 Label: $LABEL"

    # A. 使用 cp 代替 rsync
    mkdir -p "$TEMP_DIR/$IP"
    # 复制所有内容
    cp -rp . "$TEMP_DIR/$IP/"
    # 手动排除不需要的文件
    rm -rf "$TEMP_DIR/$IP/.git"
    rm -f "$TEMP_DIR/$IP/deploy.sh"

    # B. 修改 .p4 文件中的 Label
    echo "    🔧 正在扫描并修改 .p4 文件..."
    find "$TEMP_DIR/$IP" -type f -name "*.p4" | while read -r FILE; do
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s/LOCAL_LABEL = 0x[0-9a-fA-F]\{4\}/LOCAL_LABEL = $LABEL/g" "$FILE"
        else
            sed -i "s/LOCAL_LABEL = 0x[0-9a-fA-F]\{4\}/LOCAL_LABEL = $LABEL/g" "$FILE"
        fi
        
        MATCH=$(grep "LOCAL_LABEL" "$FILE" | head -n 1)
        [ ! -z "$MATCH" ] && echo "      ✅ $(basename "$FILE") -> $MATCH"
    done

    # C. 发送并覆盖到远程目录
    echo "    📤 正在覆盖同步到 $IP:$REMOTE_PATH ..."
    ssh "$REMOTE_USER@$IP" "mkdir -p $REMOTE_PATH"
    
    # 使用 /. 确保拷贝的是目录内的内容
    scp -r -q "$TEMP_DIR/$IP/." "$REMOTE_USER@$IP:$REMOTE_PATH"
    
    if [ $? -eq 0 ]; then
        echo "    ✨ $IP 部署完成!"
    else
        echo "    ❌ $IP 同步失败。"
    fi
done

rm -rf "$TEMP_DIR"
echo "--------------------------------------------------"
echo "✅ 所有文件已同步至: $REMOTE_PATH"