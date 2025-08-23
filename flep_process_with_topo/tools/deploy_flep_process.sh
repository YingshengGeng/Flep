
#!/bin/bash
# 定义端口号
PORTS=(8008 9090)

# 函数：终止占用端口的进程
function kill_processes {
    for port in "${PORTS[@]}"; do
        echo "Checking for processes on port $port..."
        PROCESSES=$(sudo lsof -i :$port -t)
        if [ -n "$PROCESSES" ]; then
            for PID in $PROCESSES; do
                echo "Killing process with PID $PID on port $port..."
                sudo kill -9 $PID
            done
        fi
    done
}

TOFINO_BIN=$SDE_INSTALL/bin

$TOFINO_BIN/bf_kdrv_mod_load /usr/local/sde

# 编译 P4 程序
# $TOFINO_BIN/bf-p4c --std p4-16 --target tofino --arch tna -o $OUTPUT_DIR -g $P4_FILE

# 复制配置文件到 SDE 共享目录
# sudo cp $CONF_FILE $TOFINO_SHARE/


# # 数据库用户名和密码
# DB_USER="root"
# DB_PASS="123456"

# # 定义SQL命令
# MYSQL_CMD="mysql -u $DB_USER -p$DB_PASS"

# # 执行SQL命令并退出MySQL
# eval $MYSQL_CMD <<EOF
# CREATE DATABASE IF NOT EXISTS flep_db;
# USE flep_db;

# CREATE TABLE IF NOT EXISTS forward_port (
#     ingress_port SMALLINT UNSIGNED NOT NULL,
#     port SMALLINT UNSIGNED NOT NULL,
#     PRIMARY KEY (ingress_port)
# );

# CREATE TABLE IF NOT EXISTS flep_encaping (
#     label INT NOT NULL,
#     port SMALLINT UNSIGNED NOT NULL,
#     PRIMARY KEY (label)
# );

# CREATE TABLE IF NOT EXISTS key_match_tbl (
#     \`key_index\` INT NOT NULL,
#     \`key\` VARCHAR(255),
#     PRIMARY KEY (\`key_index\`)
# );
# EOF

# CREATE TABLE IF NOT EXISTS flep_ipv4_classifier (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     ipv4_src VARCHAR(15) NOT NULL,
#     ipv4_dst VARCHAR(15) NOT NULL,
#     tp ENUM('tcp', 'udp') NOT NULL,
#     tp_src VARCHAR(15) NOT NULL,
#     tp_dst VARCHAR(15) NOT NULL,
#     key_index INT NOT NULL,
#     \`key\` VARCHAR(255) NOT NULL,
#     label_list TEXT NOT NULL
# );

# CREATE TABLE IF NOT EXISTS flep_ipv6_classifier (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     ipv6_src VARCHAR(45) NOT NULL,
#     ipv6_dst VARCHAR(45) NOT NULL,
#     tp ENUM('tcp', 'udp') NOT NULL,
#     tp_src VARCHAR(15) NOT NULL,
#     tp_dst VARCHAR(15) NOT NULL,
#     key_index INT NOT NULL,
#     \`key\` VARCHAR(255) NOT NULL,
#     label_list TEXT NOT NULL
# );

# 启动 SwitchD

# 主程序
kill_processes

# $SDE_PATH/run_switchd.sh -p flep_encap &
# nohup $SDE_PATH/run_switchd.sh -p flep_encap &

echo "Deployment completed."