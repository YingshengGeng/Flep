#!/bin/bash

# 1. 定义一个索引变量
index=3

# 2. 设定文件路径变量
# path_p4="../flep_process_with_topo/flep_process.p4"
path_p4="../flep_encap_with_topo/flep_encap.p4"
path_settings="../flep_process_with_topo/backend/configuration.yml"

# 3. 从设定文件中提取对应索引的 LOCAL_LABEL 值
#    这里使用 awk，并利用变量来动态匹配行
NEW_LABEL=$(awk -v idx="$index" '$0 ~ "LOCAL_LABEL_"idx {print $3}' "$path_settings" | tr -d "'")

# 4. 检查是否成功提取到值
if [ -z "$NEW_LABEL" ]; then
    echo "未在 ${path_settings} 中找到 LOCAL_LABEL_${index} 的设定。"
else
    # 5. 使用 sed 替换目标文件中的 LOCAL_LABEL 值
    #    注意，这里使用双引号来让 shell 解释器展开变量
    sed -i '' "s/const bit<16> LOCAL_LABEL = .*;/const bit<16> LOCAL_LABEL = ${NEW_LABEL};/" "$path_p4"
    echo "已成功将文件 ${path_p4} 中的 LOCAL_LABEL 值替换为 ${NEW_LABEL}。"
fi