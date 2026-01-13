#!/bin/bash

SWITCHES=(
  "10.0.0.11:encap"
  "10.0.0.12:process"
  "10.0.0.13:encap"
)

REMOTE_USER="ruijie"

echo "开始同步 YAML 配置文件..."

for ENTRY in "${SWITCHES[@]}"; do
    IFS=':' read -r IP TYPE <<< "$ENTRY"
    
    [[ "$TYPE" == "encap" ]] && DIR_NAME="flep_encap_with_topo" || DIR_NAME="flep_process_with_topo"

    # 1. 首先获取远程的 PROGRAM_DIR 路径
    R_PROG_DIR=$(ssh $REMOTE_USER@$IP "source ~/.bashrc && echo \$PROGRAM_DIR")

    echo ">>> [交换机 $IP] 同步至 $R_PROG_DIR..."

    CONFIG_FILES=(
        "backend/configuration.yml"
        "target/configuration.yml"
    )

    for FILE in "${CONFIG_FILES[@]}"; do
        LOCAL_PATH="${DIR_NAME}/${FILE}"
        REMOTE_PATH="${R_PROG_DIR}/${DIR_NAME}/${FILE}"
        
        # 创建远程目录并拷贝
        ssh $REMOTE_USER@$IP "mkdir -p \$(dirname ${REMOTE_PATH})"
        scp "$LOCAL_PATH" "$REMOTE_USER@$IP:$REMOTE_PATH"
    done
done