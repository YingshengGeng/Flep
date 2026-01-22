
# 可靠通信验证软硬件平台

## 项目简介

可靠通信验证软硬件平台基于 P4 可编程交换机开发，设计并实现了一种非 IP 标签转发协议。该平台支持基于 IPv4、IPv6、TCP、UDP 等多种协议报文头字段定义标签转发策略，绕过传统路由决策过程，实现路径的快速指定与传输处理。平台包含可视化拓扑与图形化操作界面，用于监控网络和配置策略 。

## 代码组织
README.md: 使用文档。
┣ flep_encaps.p4: 针对路径封装节点的P4代码。
┣ tests: 用于测试功能正确性的程序。
  ->encap_api_test.py: 用于测试路径封装节点控制器对外API的功能正确性。
  ->sync_time.sh: 用于同步系统时间。
  ->typo_test.py: 用于测试获取拓扑功能是否正确。
┣ flep_encap.p4: 针对路径封装节点的P4代码。
┣ backend: 交换机控制器相关程序。
┣ target: 程序编译后生成的相关文件。
┗ tools: 辅助脚本。
  ->deploy_flep_encap.sh: 用于检查是否有占用switchd所需端口的进程，并kill掉。
  ->encap_database.sql: 路径封装节点控制器所需的数据库配置。
  ->sync_time.sh: 用于同步系统时间。
flep_process_with_topo: 用于标签转发的节点代码库。
┣ flep_process.p4: 针对标签转发节点的P4代码。
┣ tests: 用于测试功能正确性的程序。
  ->process_api_test.py: 用于测试标签转发节点控制器对外API的功能正确性。
┣ backend: 交换机控制器相关程序。
┣ target: 程序编译后生成的相关文件。
┗ tools: 辅助脚本。
  ->deploy_flep_process.sh: 用于检查是否有占用switchd所需端口的进程，并kill掉。
  ->process_database.sql 标签转发节点控制器所需的数据库配置。
  ->sync_time.sh: 用于同步系统时间。
p4ss: 集成控制器前端


## 安装部署流程

### 1. 基础环境初始化

在服务器及交换机上执行以下配置：

1. 
**配置 Apt 镜像源**：修改 `/etc/apt/sources.list` 使用阿里云镜像 。


2. **安装系统工具与数据库**：
```bash
apt update
apt install -y screen mariadb-server

```


3. **配置管理网络**：
修改 `/etc/network/interfaces` 配置管理口 IP (如 10.0.0.13)，并重启网络服务 。



### 2. 依赖安装

#### Python 后端依赖

```bash
pip3 install --upgrade pip
pip3 install requests flask flask-cors
pip3 install pymysql==0.9.3
pip3 install pyotp wheel
pip3 install PyYAML==5.4.1
pip3 install scapy -i https://pypi.tuna.tsinghua.edu.cn/simple/

```



#### Node.js 前端环境

```bash
# 下载并解压
wget https://mirrors.aliyun.com/nodejs-release/v20.19.1/node-v20.19.1-linux-x64.tar.xz
tar -xf node-v20.19.1-linux-x64.tar.xz
sudo mv node-v20.19.1-linux-x64 /usr/local/nodejs

# 配置环境变量 (写入 ~/.bashrc)
export PATH=/usr/local/nodejs/bin:$PATH

```



### 3. 环境变量配置

在用户目录 (`~/.bashrc`) 配置 SDE 和项目路径：

```bash
export SDE=/home/ruijie/onl-bf-sde
export SDE_INSTALL=$SDE/install
export SDE_INSTALL_DIR=$SDE_INSTALL
export PROGRAM_DIR=/home/ruijie/onl-bf-sde/code_latency
export LD_LIBRARY_PATH=$SDE_INSTALL/lib:$LD_LIBRARY_PATH

```



### 4. 软件编译与数据库初始化

#### P4 程序编译

使用 `bf-p4c` 编译封装 (Encap) 和转发 (Process) 程序：

```bash
# 编译 Encap
sudo ${SDE_INSTALL_DIR}/bin/bf-p4c --std p4-16 --target tofino --arch tna \
-o ${PROGRAM_DIR}/flep_encap_with_topo/target/ \
-g ${PROGRAM_DIR}/flep_encap_with_topo/flep_encap.p4

# 编译 Process
sudo ${SDE_INSTALL_DIR}/bin/bf-p4c --std p4-16 --target tofino --arch tna \
-o ${PROGRAM_DIR}/flep_process_with_topo/target/ \
-g ${PROGRAM_DIR}/flep_process_with_topo/flep_process.p4

```



#### 数据库初始化

进入 MySQL/MariaDB 执行初始化 SQL：

```sql
CREATE DATABASE IF NOT EXISTS flep_encap_db;
CREATE DATABASE IF NOT EXISTS flep_db;
USE flep_encap_db;
SOURCE ./flep_encap_with_topo/tools/encap_database.sql;
USE flep_db;
SOURCE ./flep_process_with_topo/tools/process_database.sql;
SET PASSWORD FOR 'root'@'localhost' = PASSWORD('123456');
FLUSH PRIVILEGES;

```



---

## 配置文件说明

### 后端配置 (`backend/configuration.yml`)

需根据设备逻辑编号 `[index]` 修改以下关键参数：

* 
`SOUTHBOUND_SERVER_IP_[index]`: 交换机管理 IP 。


* 
`LOCAL_LABEL_[index]`: 设备本地标签值 (Hex) 。


* 
`PORT_LIST_[index]`: 端口映射列表 (硬件端口号:逻辑端口ID) 。


* 
`SDE_INSTALL`: SDE 安装路径 。



### 前端配置 (`p4ss/public/front_config.json`)

* 
`SOUTHBOUND_SERVER_IP`: 定义节点 IP 映射，需与后端一致 。


* 
`Router_List`: 定义节点角色 (`TYPE`: "fz" 或 "zf") 及标签 。



---

## 启动运行

### 1. 启动后端服务

根据设备角色选择启动命令：

* **封装节点 (Encap)**:
```bash
bash ${SDE}/run_switchd.sh -p flep_encap
python3 ${PROGRAM_DIR}/flep_encap_with_topo/backend/deploy_backend.py

```


* **转发节点 (Process)**:
```bash
bash ${SDE}/run_switchd.sh -p flep_process
python3 ${PROGRAM_DIR}/flep_process_with_topo/backend/deploy_backend.py

```



### 2. 端口配置

通过后端 CLI 或 `bf_shell` 激活端口：

```bash
port-del 1/0        # 清理旧配置
port-add 1/0 100G RS # 添加端口
port-enb 1/0        # 使能端口

```


### 3. 启动前端服务

```bash
serve dist

```

## 开发者信息

**开发方**：科大国创软件股份有限公司 