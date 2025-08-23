import subprocess

# 配置文件中的IP地址列表
SOUTHBOUND_SERVER_IPs = [
    '192.100.11.161', '192.100.11.162', '192.100.11.163', '192.100.11.164',
    '192.100.11.165', '192.100.11.166', '192.100.11.167', '192.100.11.168',
    '192.100.11.172', '192.100.11.173', '192.100.11.174', '192.100.11.175',
    '192.100.11.169', '192.100.11.176', '192.100.11.177', '192.100.11.170',
    '192.100.11.171'
]

def ping_ip(ip, count=1, timeout=1):
    """ 使用ping命令检查指定IP的连通性 """
    try:
        # 构建ping命令
        if subprocess.os.name == 'nt':  # Windows
            command = ['ping', '-n', str(count), '-w', str(timeout * 1000), ip]
        else:  # Linux 或其他Unix-like系统
            command = ['ping', '-c', str(count), '-W', str(timeout), ip]

        # 执行ping命令
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # 检查返回码
        if result.returncode == 0:
            print(f"成功连接到 {ip}")
            return True
        else:
            print(f"无法连接到 {ip} - {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"执行ping命令时发生错误: {e}")
        return False

# 遍历IP地址并检查连通性
for ip in SOUTHBOUND_SERVER_IPs:
    ping_ip(ip)