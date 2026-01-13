#!/bin/bash

# ==========================================
# 1. 配置信息: "IP地址:目标Label:角色(encap/process)"
# ==========================================
SWITCHES=(
  "10.0.0.11:0x2501:encap"
  "10.0.0.12:0x2502:process"
  "10.0.0.13:0x2503:encap"
)

REMOTE_USER="ruijie"

echo "🚀 开始全自动化部署: 同步 -> 遍历所有P4 -> 修改 -> 编译 -> 部署"
echo "--------------------------------------------------------"

for ENTRY in "${SWITCHES[@]}"; do
    IFS=':' read -r IP TARGET_LABEL TYPE <<< "$ENTRY"
    
    # 确定要处理的目录
    [[ "$TYPE" == "encap" ]] && DIR_NAME="flep_encap_with_topo" || DIR_NAME="flep_process_with_topo"

    echo ">>> [交换机 $IP] 正在处理目录: $DIR_NAME"

    # --- 步骤 1: 同步文件夹 ---
    R_PROG_DIR=$(ssh $REMOTE_USER@$IP "source ~/.bashrc && echo \$PROGRAM_DIR")
    ssh $REMOTE_USER@$IP "mkdir -p $R_PROG_DIR"
    rsync -avz --delete "./$DIR_NAME/" "$REMOTE_USER@$IP:$R_PROG_DIR/$DIR_NAME/"

    # --- 步骤 2: 远程批量处理目录下所有 .p4 文件 ---
    ssh -t $REMOTE_USER@$IP << EOF
        source ~/.bashrc
        cd \$PROGRAM_DIR/$DIR_NAME

        # 获取当前目录下所有的 .p4 文件列表
        P4_FILES=\$(ls *.p4 2>/dev/null)

        if [ -z "\$P4_FILES" ]; then
            echo "    [Error] 文件夹中未找到任何 .p4 文件！"
            exit 1
        fi

        for FILE in \$P4_FILES; do
            # 获取不带后缀的文件名，用于 .conf 匹配
            BASE_NAME=\${FILE%.p4}
            
            echo "    --- 正在处理: \$FILE ---"

            # 1. 修改 Label (对所有文件执行)
            CURRENT_VALUE=\$(grep "const bit<16> LOCAL_LABEL =" "\$FILE" | grep -oE "0x[0-9a-fA-F]+")
            if [ ! -z "\$CURRENT_VALUE" ]; then
                sed -i "s/const bit<16> LOCAL_LABEL = \$CURRENT_VALUE/const bit<16> LOCAL_LABEL = $TARGET_LABEL/g" "\$FILE"
                echo "        [1] Label 修改成功: \$CURRENT_VALUE -> $TARGET_LABEL"
            fi

            # 2. 执行编译
            echo "        [2] 开始编译 (bf-p4c)..."
            sudo SDE_INSTALL_DIR=\$SDE_INSTALL_DIR PROGRAM_DIR=\$PROGRAM_DIR \
            \$SDE_INSTALL_DIR/bin/bf-p4c --std p4-16 --target tofino --arch tna \
            -o ./target/ -g ./\$FILE

            # 3. 部署对应的 .conf 文件
            if [ -f "./target/\${BASE_NAME}.conf" ]; then
                echo "        [3] 部署 \${BASE_NAME}.conf 至 SDE 目录"
                sudo cp ./target/\${BASE_NAME}.conf \$SDE_INSTALL_DIR/share/p4/targets/tofino/
            else
                echo "        [!] 未找到生成的 .conf 文件: \${BASE_NAME}.conf"
            fi
        done
        
        echo "✅ [交换机 $IP] 目录下所有程序均已更新并编译！"
EOF
    echo "--------------------------------------------------------"
done

echo "🎉 恭喜！所有交换机的全量 P4 程序已同步并部署完毕。"