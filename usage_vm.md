# 编译
export SDE_INSTALL_DIR=/home/gys/bf-sde-9.13.2/install
export PROGRAM_DIR=/home/gys/

sudo ${SDE_INSTALL_DIR}/bin/bf-p4c --std p4-16 --target tofino --arch tna -o ${PROGRAM_DIR}/flep_encap_with_topo/target/ -g ${PROGRAM_DIR}/flep_encap_with_topo/flep_encap.p4

sudo ${SDE_INSTALL_DIR}/bin/bf-p4c --std p4-16 --target tofino --arch tna  -o ${PROGRAM_DIR}/flep_encap_with_topo/target/ -g ${PROGRAM_DIR}/flep_encap_with_topo/flep_encap.p4

sudo cp ${PROGRAM_DIR}/flep_encap_with_topo/target/flep_encap.conf ${SDE_INSTALL_DIR}/share/p4/targets/tofino/

sudo ${SDE_INSTALL_DIR}/bin/bf-p4c --std p4-16 --target tofino --arch tna  -o ${PROGRAM_DIR}/flep_process_with_topo/target/ -g ${PROGRAM_DIR}/flep_process_with_topo/flep_process.p4

sudo cp ${PROGRAM_DIR}/flep_process_with_topo/target/flep_process.conf ${SDE_INSTALL_DIR}/share/p4/targets/tofino/


# 运行
cd $SDE
./run_tofino_model.sh -p 程序名称
./run_switchd.sh -p 程序名称
./run_bfshell.sh -b 程序名称




# 其他 
## config
SDE_INSTALL : "/home/gys/bf-sde-9.13.2/install"
SDE : "/home/gys/bf-sde-9.13.2"
PYTHON_VERSION: "python3.10"

## Table API
注意两者的程序运行方式不同
- 硬件上
p = Popen(
    "bash $SDE_INSTALL/bin/run_bfshell.sh -b " + CONFIG_PATH,
    shell=True,
    stdout=PIPE,
    stderr=PIPE,
    env={"SDE": parameter["SDE"], "SDE_INSTALL": parameter["SDE_INSTALL"]},
)

- 软件上
p = Popen(
    "bash $SDE/run_bfshell.sh -b " + CONFIG_PATH,
    shell=True,
    stdout=PIPE,
    stderr=PIPE,
    env={"SDE": parameter["SDE"], "SDE_INSTALL": parameter["SDE_INSTALL"]},
)

## p4utils
```
# start network
sudo python network.py $SDE

# controller code
mx s1 
$SDE/run_bfshell.sh -b `pwd`/controller_1.py

# controller code
mx s2
$SDE/run_bfshell.sh -b `pwd`/controller_2.py

# start receiver
mx h2
python receive.py

# send 1500 packets, and observe how only 1000 are received
mx h1 
python send.py 10.2.2.2 1500
```
## 系统环境
uname -m
### 前端依赖
node-v20.19.1-linux-arm64.tar.gz
###Linux
#替换版本号为实际最新版（如 v20.19.1）
VERSION=v20.19.1
DISTRO=linux-x64
#从ali镜像下载
wget https://mirrors.aliyun.com/nodejs-release/$VERSION/node-$VERSION-$DISTRO.tar.xz
#解压
tar -xf node-$VERSION-$DISTRO.tar.xz
#移动到系统目录（全局可用）
sudo mv node-$VERSION-$DISTRO /usr/local/nodejs
#配置环境变量
echo 'export PATH=/usr/local/nodejs/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
#验证
node -v  # 输出 v20.19.1 即成功
cd p4ss
npm install
npm run build
npm install -g serve
s
serve dist