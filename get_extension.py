from pathlib import Path

def get_all_extensions(folder_path, recursive=True):
    """
    获取文件夹中所有文件的扩展名（去重）
    
    Args:
        folder_path (str): 文件夹路径
        recursive (bool): 是否递归子目录，默认 True
    
    Returns:
        set: 所有唯一的扩展名（小写，包含点号，如 '.py'）
    """
    path = Path(folder_path)
    if not path.exists() or not path.is_dir():
        raise ValueError(f"路径不存在或不是目录: {folder_path}")
    
    if recursive:
        files = path.rglob('*')
    else:
        files = path.glob('*')
    
    extensions = set()
    for file_path in files:
        if file_path.is_file():
            ext = file_path.suffix.lower()
            if ext:  # 忽略没有扩展名的文件
                extensions.add(ext)
    
    return extensions

# 使用示例
if __name__ == "__main__":
    folder = "."  # 当前目录
    exts = get_all_extensions(folder)
    print("所有扩展名:", sorted(exts))