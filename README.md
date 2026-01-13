# 基于标签转发的定制化协议栈V1.0
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
test: 用于配置表项的命令行终端相关程序
┣ mapping.yaml: 命令行终端配置文件。
┣ testcmd.py: 命令行终端主程序。
┣ connect_test.py: 用于测试网络是否连通的测试。
┗ topo_test.py: 用于获取当前拓扑的测试。
## 开始使用
要运行flep_encap和flep_process，您需要：
- 编译P4程序（提供的软件包中已经编译，编译生成的文件在targets中）。
  - flep_encap编译相关的命令。
  sudo [SDE_INSTALL路径]/bin/bf-p4c --std p4-16 --target tofino --arch tna  -o [flep_encap_with_topo路径]/target/ -g [flep_encap_with_topo路径]/flep_encap.p4
  - flep_process编译相关的命令。
  sudo [SDE_INSTALL路径]/bin/bf-p4c --std p4-16 --target tofino --arch tna  -o [flep_process_with_topo路径]/target/ -g [flep_process_with_topo路径]/flep_process.p4
- 部署P4程序到交换机。
  - 修改编译相关文件(/targets/flep_encap.conf或/targets/flep_process.conf)中的地址信息(提供的软件包中已进行修改)，具体命令在补充中介绍。
  - 拷贝相关文件到SDE目录中。
    - encap拷贝操作
      cp /root/flep_encap_with_topo/target/flep_encap.conf $SDE_INSTALL/share/p4/targets/tofino/
      cd $SDE_INSTALL/share/tofinopd
      mkdir -p flep_encap/pipeline_profile
      cd flep_encap
      cp /root/flep_encap_with_topo/target/{bfrt.json,events.json,frontend-ir.json,source.json} .
      cp /root/flep_encap_with_topo/target/pipe/{context.json,tofino.bin} pipeline_profile/
    - process拷贝操作
      cp /root/flep_process_with_topo/target/flep_process.conf $SDE_INSTALL/share/p4/targets/tofino/
      cd $SDE_INSTALL/share/tofinopd
      mkdir -p flep_process/pipeline_profile
      cd flep_process
      cp /root/flep_process_with_topo/target/{bfrt.json,events.json,frontend-ir.json,source.json} .
      cp /root/flep_process_with_topo/target/pipe/{context.json,tofino.bin} pipeline_profile/
  - 部署相关数据库，具体命令在P4可编程开发环境V1.0数据库配置部分。
- 配置控制器程序。
  控制器相关配置在backend/configuration.xml中设定。
  - SOUTHBOUND_SERVER_IP_[index] 用于设定第index交换机对应的IP地址。
  - LOCAL_LABEL_[index] 用于设定第index交换机对应的label值。
  - PORT_LIST_[index], PORT_LIMIT_[index] 用于设定第index交换机对应的打开端口以及速率限制。
  - 其余可能修改变量（一般不需要修改）。
    -> SDE, SDE_INSTALL 用于设定sde相关路径信息。
    -> PYTHON_VERSION 用于设定sde环境所提供的python版本。
    -> SOUTHBOUND_SERVER_PORT 用于设定控制器监听端口。
    -> P4_NAME 用于设定正在运行的程序名称。
    -> DB_PORT, DB_NAME, DB_USER, DB_PASSWORD 用于设定数据库端口，数据库名，用户名，用户密码。

## 运行P4程序
- 启动swichd来运行相关P4程序。
  - flep_encap
      . /root/flep_encap_with_topo/tools/deploy_flep_encap.sh
      $SDE_INSTALL/bin/run_switchd.sh -p flep_encap
  - flep_process
      . /root/flep_process_with_topo/tools/deploy_flep_process.sh
      $SDE_INSTALL/bin/run_switchd.sh -p flep_process
- 当启动switchd后，运行控制器程序。
  - flep_encap
    python3 /root/flep_encap_with_topo/backend/deploy_backend.py [期望启动的交换机在配置文件中的index，比如1，2,...]。
  - flep_process
    python3 /root/flep_process_with_topo/backend/deploy_backend.py [期望启动的交换机在配置文件中的index]。
- 当前两者运行后，运行控制终端（可选，因为一般可以通过控制器直接控制）
    cd test
    python testcmd.py
- 补充
  可以安装screen软件实现程序的前台和后台运行切换。


## 补充
### 如何修改编译后的文件内容使得可以部署到交换机上
- 修改编译相关文件(/targets/flep_encap.conf或/targets/flep_process.conf)中的地址信息(提供的软件包中已进行修改)。
    - flep_encap相关地址
      "bfrt": share/tofinopd/flep_encap/bfrt.json
      "context": share/tofinopd/flep_encap/pipeline_profile/context.json
      "config": share/tofinopd/flep_encap/pipeline_profile/tofino.bin
      "path": "/root/flep_encap_with_topo/target/"
      "model_json_path": "/root/flep_encap_with_topo/target/share/flep_encap/aug_model.json"
    - flep_process相关地址
      "bfrt": share/tofinopd/flep_process/bfrt.json
      "context": share/tofinopd/flep_process/pipeline_profile/context.json
      "config": share/tofinopd/flep_process/pipeline_profile/tofino.bin
      "path": /root/flep_process_with_topo/target
      "model_json_path": /root/flep_process_with_topo/target/share/flep_process/aug_model.json
### 如何定制化设置程序的label值
- 修改 .p4程序中以下部分。
  const bit<16> LOCAL_LABEL = [想要设定的label值];
- 编译相关 .p4程序。
- 检查是否一致(可选)。
  可以通过以下命令检查编译结果是否和设定的程序label值一致。
  cat flep_encap_with_topo/target/flep_encap.p4pp  | grep "LOCAL_LABEL ="
  cat flep_process_with_topo/target/flep_process.p4pp  | grep "LOCAL_LABEL ="