from scapy.all import Ether, sendp
import time

def send_raw_hex_packet(hex_data, count=1, interval=0.1, iface=None):
    """
    基于原始十六进制数据生成并发送二层数据包（含完整以太网头）
    
    参数说明：
        hex_data: str - 原始十六进制数据（可含偏移量标识、空格，会自动清理）
        count: int - 发送数据包的总次数，默认1次
        interval: float - 每次发送的时间间隔（秒），默认0.1秒
        iface: str - 发送数据包的目标网卡（如veth1、eth0），必须指定
    返回：
        None
    异常：
        ValueError - 网卡未指定、十六进制格式错误、数据长度异常时抛出
    """
    # 1. 验证必要参数
    if not iface:
        raise ValueError("错误：必须通过 'iface' 参数指定发送网卡（如veth1、eth0）")
    if not isinstance(hex_data, str) or len(hex_data.strip()) == 0:
        raise ValueError("错误：原始十六进制数据不能为空")

    # 2. 清理原始十六进制数据（去除偏移量、空格、换行）
    # 示例输入清理前："0000  01 1D 49 ... 00" → 清理后："011D49...00"
    clean_lines = []
    for line in hex_data.strip().split("\n"):
        # 去除每行开头的偏移量（如"0000  "、"0010  "），保留后面的十六进制部分
        # hex_part = line.split("  ")[-1] if "  " in line else line
        # 去除十六进制部分中的空格
        clean_hex_part = line.replace(" ", "")
        if clean_hex_part:  # 跳过空行
            clean_lines.append(clean_hex_part)
    final_clean_hex = "".join(clean_lines)

    # 3. 验证清理后的十六进制格式（长度必须为偶数，仅含0-9、a-f、A-F）
    if len(final_clean_hex) % 2 != 0:
        raise ValueError(f"错误：清理后的十六进制数据长度为奇数（{len(final_clean_hex)}），格式无效")
    valid_chars = set("0123456789abcdefABCDEF")
    if not all(c in valid_chars for c in final_clean_hex):
        invalid_chars = [c for c in final_clean_hex if c not in valid_chars]
        raise ValueError(f"错误：十六进制数据包含无效字符：{set(invalid_chars)}（仅允许0-9、a-f、A-F）")

    # 4. 十六进制转二进制字节流（核心步骤）
    try:
        raw_binary = bytes.fromhex(final_clean_hex)
    except ValueError as e:
        raise ValueError(f"错误：十六进制转二进制失败：{str(e)}")

    # 5. 构造Scapy二层数据包（解析以太网头）
    try:
        packet = Ether(raw_binary)
    except Exception as e:
        raise ValueError(f"错误：解析二进制为以太网数据包失败：{str(e)}（可能是数据结构不完整）")

    # 6. 打印数据包信息（供验证）
    print("=" * 60)
    print("原始数据处理完成，信息如下：")
    print(f"清理后的纯十六进制长度：{len(final_clean_hex)} 字符")
    print(f"转换后的二进制长度：{len(raw_binary)} 字节")
    print("\n解析后的数据包结构：")
    packet.show()  # 显示详细的各层协议字段（以太网、IP、TCP等）
    print("=" * 60)

    # 7. 循环发送数据包
    print(f"\n开始发送数据包（网卡：{iface}，总次数：{count}，间隔：{interval}秒）...")
    for i in range(count):
        try:
            # 用sendp发送二层数据包（确保从指定网卡发出，verbose=0关闭冗余日志）
            sendp(packet, iface=iface, verbose=0)
            print(f"发送进度：{i+1}/{count} （成功）")
        except Exception as e:
            print(f"发送进度：{i+1}/{count} （失败：{str(e)}）")
        
        # 最后一个包不需要间隔
        if i < count - 1:
            time.sleep(interval)
    
    print("\n所有数据包发送任务完成！")


# ------------------- 核心配置区（请根据你的需求修改） -------------------
if __name__ == "__main__":
    # 1. 你的原始十六进制数据（直接复制，无需手动清理）
    ORIGINAL_HEX_DATA = """
        01 1D 49 59 04 90 01 1D 46 F6 AA 90 12 12 00 00  
        FF FF FF FF 00 08 00 02 00 25 02 25 03 25 05 45 00 00  
        28 00 01 00 00 40 06 63 C9 0A 01 01 02 0A 02 02  
        02 07 D1 07 D2 00 00 00 00 00 00 00 00 50 02 20  
        00 69 39 00 00 00 00 00 00 00 00
    """

    # 2. 发送参数配置（必须修改网卡名称！）
    SEND_COUNT = 10          # 发送总次数（根据需求调整，如10次、100次）
    SEND_INTERVAL = 0.01     # 每次发送间隔（秒，如0.01=10ms，0.1=100ms）
    TARGET_INTERFACE = "veth1"  # 替换为你的实际网卡（用ip link show查看）

    # 3. 执行发送（捕获并显示异常）
    try:
        send_raw_hex_packet(
            hex_data=ORIGINAL_HEX_DATA,
            count=SEND_COUNT,
            interval=SEND_INTERVAL,
            iface=TARGET_INTERFACE
        )
    except Exception as main_e:
        print(f"\n程序异常终止：{str(main_e)}")