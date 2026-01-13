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

echo "🚀 开始全自动化部署: 同步 -> 严谨检查Label -> 批量编译 -> 部署"
echo "--------------------------------------------------------"

for ENTRY in "${SWITCHES[@]}"; do
    IFS=':' read -r IP TARGET_LABEL TYPE <<< "$ENTRY"
    
    # 确定要处理的目录名
    [[ "$TYPE" == "encap" ]] && DIR_NAME="flep_encap_with_topo" || DIR_NAME="flep_process_with_topo"

    echo ">>> [交换机 $IP] 正在处理角色: $TYPE"

    # --- 步骤 1: 获取远程路径并同步整个项目文件夹 ---
    R_PROG_DIR=$(ssh $REMOTE_USER@$IP "source ~/.bashrc && echo \$PROGRAM_DIR")
    
    echo "    [1/4] 同步文件夹至 $R_PROG_DIR..."
    ssh $REMOTE_USER@$IP "mkdir -p $R_PROG_DIR"
    rsync -avz --delete "./$DIR_NAME/" "$REMOTE_USER@$IP:$R_PROG_DIR/$DIR_NAME/"

    # --- 步骤 2: 远程批量处理（包含严谨检查逻辑） ---
    ssh -t $REMOTE_USER@$IP << EOF
        source ~/.bashrc
        cd \$PROGRAM_DIR/$DIR_NAME

        # 获取当前目录下所有的 .p4 文件 (包含普通版和 _latency 版)
        P4_FILES=\$(ls *.p4 2>/dev/null)

        for FILE in \$P4_FILES; do
            BASE_NAME=\${FILE%.p4}
            echo "    --- 处理文件: \$FILE ---"

            # 【核心检查逻辑】
            # 提取当前文件中的 LOCAL_LABEL 值
            CURRENT_VALUE=\$(grep "const bit<16> LOCAL_LABEL =" "\$FILE" | grep -oE "0x[0-9a-fA-F]+")
            
            if [ -z "\$CURRENT_VALUE" ]; then
                echo "        [!] 跳过: \$FILE 中未找到 LOCAL_LABEL 定义"
            elif [ "\$CURRENT_VALUE" == "$TARGET_LABEL" ]; then
                echo "        [OK] 标签已是 $TARGET_LABEL，无需修改"
            else
                echo "        [Update] 发现旧标签 \$CURRENT_VALUE -> 正在写入 $TARGET_LABEL"
                sed -i "s/const bit<16> LOCAL_LABEL = \$CURRENT_VALUE/const bit<16> LOCAL_LABEL = $TARGET_LABEL/g" "\$FILE"
            fi

            # --- 步骤 3: 编译 ---
            echo "        [Build] 正在编译 \$FILE..."
            sudo SDE_INSTALL_DIR=\$SDE_INSTALL_DIR PROGRAM_DIR=\$PROGRAM_DIR \
            \$SDE_INSTALL_DIR/bin/bf-p4c --std p4-16 --target tofino --arch tna \
            -o ./target/ -g ./\$FILE

            # --- 步骤 4: 分发配置 ---
            if [ -f "./target/\${BASE_NAME}.conf" ]; then
                echo "        [Deploy] 拷贝 \${BASE_NAME}.conf 至 SDE 目录"
                sudo cp ./target/\${BASE_NAME}.conf \$SDE_INSTALL_DIR/share/p4/targets/tofino/
            fi
        done
        
        echo "✅ [交换机 $IP] 处理完毕"
EOF
    echo "--------------------------------------------------------"
done

echo "🎉 全量部署任务已顺利完成！"