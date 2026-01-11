import subprocess

# 配置文件中的IP地址列表
SOUTHBOUND_SERVER_IPs = [
    '10.0.0.11','10.0.0.12','10.0.0.13'
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