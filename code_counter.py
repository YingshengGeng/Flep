from pathlib import Path

# ==============================
# 配置区域
# ==============================

# 你关心的扩展名列表
TARGET_EXTENSIONS = {
    '.bfa', '.bin', '.cjs', '.css', '.development',
    '.html', '.idx', '.ipynb', '.log', '.md', '.mjs', '.p4',
    '.pack','.production', '.py', '.rev', '.sample',
    '.scss', '.sh', '.sql', '.ts', '.vue', '.yaml', '.yml'
}
# TARGET_EXTENSIONS = {
#     '.py', '.ts', '.js', '.cjs', '.mjs', '.json'
#     '.sh', '.sql', '.p4'
#     '.html', '.css', '.scss', '.vue'
# }

# 已知的二进制或非文本扩展名，将被跳过
BINARY_EXTENSIONS = {'.bin', '.docx', '.pdf', '.png', '.svg', '.pack', '.idx', '.rev', '.bfa', '.p4pp', '.dot'}

# ==============================
# 核心逻辑
# ==============================

def classify_lines_by_content(lines, file_ext):
    """
    根据文件扩展名，使用不同的规则分类代码行、注释行和空白行。
    """
    code_lines = 0
    comment_lines = 0
    blank_lines = 0

    # --- 为不同语言定义注释符号 ---
    if file_ext in {'.py'}:
        single_comment = '#'
        multi_start = '"""'
        multi_end = '"""'
        alt_multi_start = "'''"
        alt_multi_end = "'''"
    elif file_ext in {'.js', '.ts', '.cjs', '.mjs', '.jsx', '.tsx', '.css', '.scss'}:
        single_comment = '//'
        multi_start = '/*'
        multi_end = '*/'
        alt_multi_start = None
        alt_multi_end = None
    elif file_ext in {'.html', '.vue'}:
        single_comment = None
        multi_start = '<!--'
        multi_end = '-->'
        alt_multi_start = None
        alt_multi_end = None
    elif file_ext in {'.sh'}:
        single_comment = '#'
        multi_start = None
        multi_end = None
        alt_multi_start = None
        alt_multi_end = None
    elif file_ext in {'.sql'}:
        single_comment = '--'
        multi_start = '/*'
        multi_end = '*/'
        alt_multi_start = None
        alt_multi_end = None
    elif file_ext in {'.yaml', '.yml', '.conf'}:
        single_comment = '#'
        multi_start = None
        multi_end = None
        alt_multi_start = None
        alt_multi_end = None
    elif file_ext in {'.json', '.log', '.md', '.sample', '.development', '.production'}:
        # JSON 无注释，日志/Markdown等按纯文本处理，无单行注释符
        single_comment = None
        multi_start = None
        multi_end = None
        alt_multi_start = None
        alt_multi_end = None
    else:
        # Fallback: treat as plain text
        single_comment = None
        multi_start = None
        multi_end = None
        alt_multi_start = None
        alt_multi_end = None

    in_multiline_comment = False
    in_alt_multiline = False

    for line in lines:
        stripped = line.rstrip('\n\r')  # 保留左侧空格以判断缩进
        lstriped = stripped.lstrip()
        
        # 1. 判断空白行
        if not lstriped:
            blank_lines += 1
            continue

        # 2. 处理交替多行注释 (如 Python 的 ''')
        if in_alt_multiline:
            comment_lines += 1
            if alt_multi_end and alt_multi_end in stripped:
                in_alt_multiline = False
            continue

        # 3. 处理标准多行注释 (如 /* ... */)
        if in_multiline_comment:
            comment_lines += 1
            if multi_end and multi_end in stripped:
                in_multiline_comment = False
            continue

        # 4. 检查是否是交替多行注释的开始
        if alt_multi_start and lstriped.startswith(alt_multi_start):
            comment_lines += 1
            if alt_multi_end not in stripped[len(alt_multi_start):]:
                in_alt_multiline = True
            continue

        # 5. 检查是否是标准多行注释的开始
        if multi_start and lstriped.startswith(multi_start):
            comment_lines += 1
            if multi_end not in stripped[len(multi_start):]:
                in_multiline_comment = True
            continue

        # 6. 检查单行注释
        if single_comment and lstriped.startswith(single_comment):
            comment_lines += 1
            continue

        # 7. 其余均为代码行
        code_lines += 1

    return code_lines, comment_lines, blank_lines


def analyze_codebase(folder_path, recursive=True):
    """
    分析代码库，统计代码行、注释行、空白行。
    """
    path = Path(folder_path)
    if not path.exists() or not path.is_dir():
        raise ValueError(f"路径不存在或不是目录: {folder_path}")
    
    # 获取所有文件
    files = path.rglob('*') if recursive else path.glob('*')
    
    total_code = 0
    total_comment = 0
    total_blank = 0
    total_files = 0

    for file_path in files:
        if not file_path.is_file():
            continue
            
        ext = file_path.suffix.lower()
        # 1. 检查是否在目标扩展名中
        if ext not in TARGET_EXTENSIONS:
            continue
        # 2. 检查是否是二进制文件
        if ext in BINARY_EXTENSIONS:
            continue
        
        total_files += 1
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except (UnicodeDecodeError, OSError):
            # 如果无法作为文本读取，跳过此文件
            print(f"警告: 无法读取文件 {file_path}，已跳过。")
            continue
        
        # 3. 分类统计
        code, comment, blank = classify_lines_by_content(lines, ext)
        total_code += code
        total_comment += comment
        total_blank += blank

    total_lines = total_code + total_comment + total_blank
    return {
        'files_processed': total_files,
        'code_lines': total_code,
        'comment_lines': total_comment,
        'blank_lines': total_blank,
        'total_lines': total_lines
    }


# ==============================
# 主程序入口
# ==============================
if __name__ == "__main__":
    # folder = "."  # 默认分析当前目录
    folder = "./"  # 默认分析当前目录
    result = analyze_codebase(folder)
    
    print("=" * 50)
    print("代码统计分析报告")
    print("=" * 50)
    print(f"已处理文件数量: {result['files_processed']}")
    print(f"代码行 (Code):   {result['code_lines']}")
    print(f"注释行 (Comment): {result['comment_lines']}")
    print(f"空白行 (Blank):  {result['blank_lines']}")
    print("-" * 50)
    print(f"总行数 (Total):  {result['total_lines']}")
    print("=" * 50)