# MYSQL
注意配置一下 mysql
# 启动网卡
sudo bash $SDE/tools/vetn_setup.sh
export SDE
export SDE_INSTALL
uname -a
# 首先获取
$SDE
$SDE_INSTALL
uname -a
cat $SDE_INSTALL/lib/python{}
cat $SDE_INSTALL/lib/python{}/site-packages/tofino/bfrt_grpc/

# 编译
export SDE_INSTALL_DIR=/home/gys/bf-sde-9.13.2/install
export PROGRAM_DIR=/home/gys/
python 3.9

sudo ${SDE_INSTALL_DIR}/bin/bf-p4c --std p4-16 --target tofino --arch tna -o ${PROGRAM_DIR}/flep_encap_with_topo/target/ -g ${PROGRAM_DIR}/flep_encap_with_topo/flep_encap.p4

sudo cp ${PROGRAM_DIR}/flep_encap_with_topo/target/flep_encap.conf ${SDE_INSTALL_DIR}/share/p4/targets/tofino/

sudo ${SDE_INSTALL_DIR}/bin/bf-p4c --std p4-16 --target tofino --arch tna  -o ${PROGRAM_DIR}/flep_process_with_topo/target/ -g ${PROGRAM_DIR}/flep_process_with_topo/flep_process.p4

sudo cp ${PROGRAM_DIR}/flep_process_with_topo/target/flep_process.conf ${SDE_INSTALL_DIR}/share/p4/targets/tofino/

cat ${PROGRAM_DIR}/flep_encap_with_topo/target/flep_encap.conf
这里的修改

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


SDE : "/home/ruijie/onl-bf-sde"
SDE_INSTALL : "/home/ruijie/onl-bf-sde/install"
PYTHON_VERSION: "python3.9"

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
## 系统软件
### 版本
uname -m
#### Debian 11
cat > /etc/apt/sources.list << EOF
deb https://mirrors.aliyun.com/debian/ bullseye main non-free contrib
deb-src https://mirrors.aliyun.com/debian/ bullseye main non-free contrib
deb https://mirrors.aliyun.com/debian-security/ bullseye-security main
deb-src https://mirrors.aliyun.com/debian-security/ bullseye-security main
deb https://mirrors.aliyun.com/debian/ bullseye-updates main non-free contrib
deb-src https://mirrors.aliyun.com/debian/ bullseye-updates main non-free contrib
#deb https://mirrors.aliyun.com/debian/ bullseye-backports main non-free contrib
#deb-src https://mirrors.aliyun.com/debian/ bullseye-backports main non-free contrib
EOF

#### Debian 9
cat <<EOL > multistrap-debian.list
deb [arch=amd64] https://mirrors.aliyun.com/debian-archive/debian stretch main contrib non-free
#deb [arch=amd64] https://mirrors.aliyun.com/debian-archive/debian stretch-proposed-updates main non-free contrib
#deb [arch=amd64] https://mirrors.aliyun.com/debian-archive/debian stretch-backports main non-free contrib
deb [arch=amd64] https://mirrors.aliyun.com/debian-archive/debian-security stretch/updates main contrib non-free
deb-src [arch=amd64] https://mirrors.aliyun.com/debian-archive/debian stretch main contrib non-free
#deb-src [arch=amd64] https://mirrors.aliyun.com/debian-archive/debian stretch-proposed-updates main contrib non-free
#deb-src [arch=amd64] https://mirrors.aliyun.com/debian-archive/debian stretch-backports main contrib non-free
deb-src [arch=amd64] https://mirrors.aliyun.com/debian-archive/debian-security stretch/updates main contrib non-free
EOL

### screen 
apt install -y screen
### mysql
apt update
apt install -y mysql-server
apt install -y mariadb-server

echo "Configuring MySQL databases..."
mysql -u root <<EOF
CREATE DATABASE IF NOT EXISTS flep_encap_db;
CREATE DATABASE IF NOT EXISTS flep_db;

USE flep_encap_db;
SOURCE ./flep_encap_with_topo/tools/encap_database.sql;

USE flep_db;
SOURCE ./flep_process_with_topo/tools/process_database.sql;

SET PASSWORD FOR 'root'@'localhost' = PASSWORD('123456');
USE mysql;
UPDATE user SET plugin='mysql_native_password' WHERE User='root';
FLUSH PRIVILEGES;
EOF

service mysql restart

### Python 软件
pip3 install requests -i https://pypi.tuna.tsinghua.edu.cn/simple/ --trusted-host pypi.tuna.tsinghua.edu.cn
pip3 install flask -i http://mirrors.aliyun.com/pypi/simple/  --trusted-host mirrors.aliyun.com
pip3 install pymysql==0.9.3 -i http://mirrors.aliyun.com/pypi/simple/  --trusted-host mirrors.aliyun.com
pip3 install pyotp -i http://mirrors.aliyun.com/pypi/simple/  --trusted-host mirrors.aliyun.com
pip3 install wheel -i http://mirrors.aliyun.com/pypi/simple/  --trusted-host mirrors.aliyun.com
pip3 install scapy -i https://pypi.tuna.tsinghua.edu.cn/simple/ --trusted-host pypi.tuna.tsinghua.edu.cn
pip3 install PyYAML==5.4.1 -i https://pypi.tuna.tsinghua.edu.cn/simple/ --trusted-host pypi.tuna.tsinghua.edu.cn
pip3 install flask-cors -i https://mirrors.aliyun.com/pypi/simple/

### 前端依赖
uname -m
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
serve dist
