from flask import Blueprint, request
from werkzeug.utils import secure_filename
import os

# 创建蓝图
upload_bp = Blueprint('upload', __name__)

# 定义上传目录
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
# 确保上传目录存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 定义允许的文件扩展名和最大文件大小 (2MB)
ALLOWED_EXTS = ('.html', '.json', '.csv', '.txt')
MAX_FILE_SIZE = 2 * 1024 * 1024

# 添加一个新的 路由，输入 文件名字，查询文件在 uploads 文件夹中的 meta 数据
@upload_bp.route('/meta/<filename>', methods=['GET'])
def get_file_meta(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        return 'File not found', 404
    # 获取文件元数据
    file_meta = {
        'filename': filename,
        'ext': os.path.splitext(filename)[1],
        'size': os.path.getsize(file_path),
        'created': os.path.getctime(file_path),
        'modified': os.path.getmtime(file_path),
    }
    return file_meta, 200

# 添加一个路由读取文件内容
@upload_bp.route('/content/<filename>', methods=['GET'])
def get_file_content(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        return 'File not found', 404

    # 获取查询参数
    start_line = request.args.get('start', type=int)
    end_line = request.args.get('end', type=int)
    line_count = request.args.get('count', type=int)
    reverse = request.args.get('reverse', type=lambda x: x.lower() == 'true', default=False)

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    if reverse:
        lines = lines[::-1]

    if start_line is not None or end_line is not None or line_count is not None:
        if start_line is None:
            start_line = 1
        if start_line < 1:
            start_line = 1

        if line_count is not None:
            end_line = start_line + line_count - 1
        elif end_line is None:
            end_line = len(lines)
    
        start_idx = start_line - 1
        end_idx = min(end_line, len(lines))
        if start_idx < end_idx:
            content = ''.join(lines[start_idx:end_idx])
        else:
            content = ''
    else:
        content = ''.join(lines)

    return content, 200

# 替换文档内容 使用 start end count 和 new_content 参数
@upload_bp.route('/update/<filename>', methods=['POST'])
def replace_content(filename):
    start_line = request.json.get('start')
    end_line = request.json.get('end')
    line_count = request.json.get('count')
    new_content = request.json.get('new_content')

    # 检查必要参数
    if not filename:
        return 'Filename is required', 400
    if new_content is None:
        return 'New content is required', 400

    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        return 'File not found', 404

    # 读取文件内容
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except Exception as e:
        return f'Error reading file: {str(e)}', 500

    # 处理参数
    if start_line is None:
        start_line = 1
    if start_line < 1:
        start_line = 1

    if line_count is not None:
        end_line = start_line + line_count - 1
    elif end_line is None:
        end_line = len(lines)

    start_idx = start_line - 1
    end_idx = min(end_line, len(lines))

    # 替换内容
    new_lines = lines[:start_idx] + new_content.splitlines(keepends=True) + lines[end_idx:]

    # 写入文件
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(new_lines)
        return 'Content replaced successfully', 200
    except Exception as e:
        return f'Error writing file: {str(e)}', 500

@upload_bp.route('/upload', methods=['POST'])
def upload_file():
    # 从请求的参数或表单数据中获取 replace 参数，默认值为 False
    replace = (request.args.get('replace', None) or request.form.get('replace', 'false')).lower() == 'true'

    # 检查文件大小是否超过限制
    if int(request.headers.get('Content-Length', 0)) > MAX_FILE_SIZE:
        return 'File size exceeds 2MB limit', 400

    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file and not file.filename.lower().endswith(ALLOWED_EXTS):
        return 'Only HTML, JSON, CSV, and TXT files are allowed', 400
    
    # 保存文件到 uploads 目录
    original_filename = file.filename
    # 对于HTML文件，我们允许中文文件名，但需要确保文件安全
    # 移除路径信息并限制文件名长度
    filename = os.path.basename(original_filename)
    if len(filename) > 100:  # 限制文件名长度
        name, ext = os.path.splitext(filename)
        filename = name[:95] + ext

    # 确保文件名安全，但保留中文字符
    filename = "".join(c for c in filename if c.isalnum() or c in (' ', '.', '_', '-', '(', ')', '[', ']', '（', '）', '【', '】'))
    filename = filename.replace(' ', '_')  # 将空格替换为下划线

    # 如果文件名为空或只有扩展名，使用时间戳
    if not filename or filename.startswith('.'):
        import time
        filename = f"upload_{int(time.time())}.html"

    file_path = os.path.join(UPLOAD_FOLDER, filename)

    if not replace and os.path.exists(file_path):
        # 如果文件已存在且不允许替换，添加数字后缀
        counter = 1
        name, ext = os.path.splitext(filename)
        while os.path.exists(file_path):
            filename = f"{name}_{counter}{ext}"
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            counter += 1

    file.save(file_path)

    # 返回成功消息和文件链接
    return f'File uploaded successfully. View it at: /uploads/{filename}', 200

# 注册路由函数
def register_upload_routes(app):
    app.register_blueprint(upload_bp)