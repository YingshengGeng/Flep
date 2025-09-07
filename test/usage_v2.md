# 0.编译部分
# 0.1 编译
<!-- sudo /home/gys/bf-sde-9.13.2/install/bin/bf-p4c --std p4-16 --target tofino --arch tna  -o /home/gys/submit_v4/sw1/flep_encap_with_topo/target/ -g /home/gys/submit_v4/sw1/flep_encap_with_topo/flep_encap.p4

sudo /home/gys/bf-sde-9.13.2/install/bin/bf-p4c --std p4-16 --target tofino --arch tna  -o /home/gys/submit_v4/sw1/flep_process_with_topo/target/ -g /home/gys/submit_v4/sw1/flep_process_with_topo/flep_process.p4 -->
# 0.2 检查编译
<!-- .p4app，查看变量 -->
cat flep_encap_with_topo/target/flep_encap.p4pp  | grep "LOCAL_LABEL ="
cat flep_process_with_topo/target/flep_process.p4pp  | grep "LOCAL_LABEL ="

# 1.安装部分 
ifconfig eth0 192.168.137.50 netmask 255.255.255.0 && route add default gw 192.168.137.1
ping -c 1 192.168.137.1
scp 22472@192.168.137.1:/D:/下载/ONL-master+_ONL-OS9_2024-07-31.1146-2d36941.tgz /tmp/


<!-- scp -O "D:\下载\ONL-master+_ONL-OS9_2024-07-31.1146-2d36941.tgz" root@192.168.137.50:/tmp/ -->

cd /tmp/
tar -xvf ONL-master+_ONL-OS9_2024-07-31.1146-2d36941.tgz
chmod u+x ONL-master+_ONL-OS9_2024-07-31.1146-2d36941_AMD64_INSTALLED_INSTALLER
./ONL-master+_ONL-OS9_2024-07-31.1146-2d36941_AMD64_INSTALLED_INSTALLER

# 2.系统配置

# 2.1 设备布局部分
echo "Configuring network interfaces..."
echo "auto ma1
iface ma1 inet dhcp" | tee /etc/network/interfaces > /dev/null

echo "Enabling root login via SSH..."
echo "PermitRootLogin yes" | tee -a /etc/ssh/sshd_config > /dev/null

echo "Restarting networking service..."
/etc/init.d/networking restart

ifconfig ma1

或者直接重启，或者
ifconfig ma1 down 
/etc/init.d/networking restart
ifconfig ma1 up

# 2.2 传输文件
ifconfig 
cd swx
scp -r -O flep_encap_with_topo flep_process_with_topo root@192.168.137.184:~

# 2.3 环境变量
vi ~/.bashrc
export SDE=/usr/local/sde/bf-sde-9.7.4
export SDE_INSTALL=/usr/local/sde
export PATH=$SDE_INSTALL/bin:$PATH
export LD_LIBRARY_PATH=$SDE_INSTALL/lib:$LD_LIBRARY_PATH

source ~/.bashrc

# 2.4 内核与platform
./quick-start.sh
cd $SDE_INSTALL/bin
./xt-cfgen.sh
bf_kdrv_mod_load /usr/local/sde
之后可以运行测试代码

# 2.5 进行时间同步
chmod u+x /root/flep_process_with_topo/tools/sync_time.sh
. /root/flep_process_with_topo/tools/sync_time.sh

# 2.6 库安装
pip3 install requests -i https://pypi.tuna.tsinghua.edu.cn/simple/ --trusted-host pypi.tuna.tsinghua.edu.cn
pip3 install flask -i http://mirrors.aliyun.com/pypi/simple/  --trusted-host mirrors.aliyun.com
pip3 install pymysql==0.9.3 -i http://mirrors.aliyun.com/pypi/simple/  --trusted-host mirrors.aliyun.com
pip3 install pyotp -i http://mirrors.aliyun.com/pypi/simple/  --trusted-host mirrors.aliyun.com
pip3 install wheel -i http://mirrors.aliyun.com/pypi/simple/  --trusted-host mirrors.aliyun.com
pip3 install scapy -i https://pypi.tuna.tsinghua.edu.cn/simple/ --trusted-host pypi.tuna.tsinghua.edu.cn
pip3 install PyYAML==5.4.1 -i https://pypi.tuna.tsinghua.edu.cn/simple/ --trusted-host pypi.tuna.tsinghua.edu.cn
# 2.6.1 数据库配置
# 软件源替换
echo "Replacing software sources..."
cd /etc/apt/sources.list.d
echo "Clearing content of multistrap-onl.list and multistrap-debian.list..."
> multistrap-onl.list
> multistrap-debian.list

echo "Replacing software source in multistrap-debian.list..."
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
# 数据库下载
apt update
apt install -y mysql-server
# 数据库配置
echo "Configuring MySQL databases..."
mysql -u root <<EOF
CREATE DATABASE IF NOT EXISTS flep_encap_db;
CREATE DATABASE IF NOT EXISTS flep_db;

USE flep_encap_db;
SOURCE /root/flep_encap_with_topo/tools/database.sql;

USE flep_db;
SOURCE /root/flep_process_with_topo/tools/database.sql;

SET PASSWORD FOR 'root'@'localhost' = PASSWORD('123456');
USE mysql;
UPDATE user SET plugin='mysql_native_password' WHERE User='root';
FLUSH PRIVILEGES;
EOF

service mysql restart

# 2.7 文件修改与拷贝
# encap数据移动操作
echo "Copying encap data..."

cp /root/flep_encap_with_topo/target/flep_encap.conf $SDE_INSTALL/share/p4/targets/tofino/
cd $SDE_INSTALL/share/tofinopd
mkdir -p flep_encap/pipeline_profile
cd flep_encap
cp /root/flep_encap_with_topo/target/{bfrt.json,events.json,frontend-ir.json,source.json} .
cp /root/flep_encap_with_topo/target/pipe/{context.json,tofino.bin} pipeline_profile/

# process数据移动操作
echo "Copying process data..."
cp /root/flep_process_with_topo/target/flep_process.conf $SDE_INSTALL/share/p4/targets/tofino/
cd $SDE_INSTALL/share/tofinopd
mkdir -p flep_process/pipeline_profile
cd flep_process
cp /root/flep_process_with_topo/target/{bfrt.json,events.json,frontend-ir.json,source.json} .
cp /root/flep_process_with_topo/target/pipe/{context.json,tofino.bin} pipeline_profile/

echo "Configuration completed."

# 3. 运行
# encap
# 1 有shell
. /root/flep_encap_with_topo/tools/deploy_flep_encap.sh
$SDE_INSTALL/bin/run_switchd.sh -p flep_encap

python3 /root/flep_encap_with_topo/backend/deploy_backend.py sw_index
# 2 后台运行
. /root/flep_encap_with_topo/tools/deploy_flep_encap.sh 
nohup $SDE_INSTALL/bin/run_switchd.sh -p flep_encap > /dev/null 2>&1 & nohup 

python3 /root/flep_encap_with_topo/backend/deploy_backend.py index > /dev/null 2>&1 &
# process
# 1 有shell
. /root/flep_process_with_topo/tools/deploy_flep_process.sh
$SDE_INSTALL/bin/run_switchd.sh -p flep_process

python3 /root/flep_process_with_topo/backend/deploy_backend.py sw_index
# 2 后台运行
. /root/flep_process_with_topo/tools/deploy_flep_process.sh
nohup $SDE_INSTALL/bin/run_switchd.sh -p flep_process > /dev/null 2>&1 &

nohup python3 /root/flep_process_with_topo/backend/deploy_backend.py index > /dev/null 2>&1 &