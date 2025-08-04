from flask import Flask, send_from_directory, request
from werkzeug.utils import secure_filename
import os
from router.upload import register_upload_routes
from markdown_render import render_markdown

app = Flask(__name__)

# Get the current working directory
current_dir = os.getcwd()

@app.route('/')
def serve_index():
    # Serve index.html as the default page
    return send_from_directory(current_dir, 'index.html')

# 定义禁止的文件扩展名列表
BANNED_EXTS = ('.py', '.log', '.db')

@app.route('/<path:filename>')
def serve_file(filename):
    # 检查文件扩展名是否在禁止列表中
    if filename.lower().endswith(BANNED_EXTS):
        return "File type not allowed", 403

    # ban any file name start with .
    if filename.startswith('.'):
        return "File name not allowed", 403

    # 检测是否为 .md 文件，若是则渲染为 HTML
    if filename.lower().endswith('.md'):
        try:
            with open(os.path.join(current_dir, filename), 'r', encoding='utf-8') as f:
                md_content = f.read()
            html_content = render_markdown(md_content)
        except Exception as e:
            return str(e), 500
        return html_content

    # 从当前目录提供普通文件服务
    return send_from_directory(current_dir, filename)

# 注册上传路由
register_upload_routes(app)

if __name__ == '__main__':
    print(f"Serving HTML files from: {current_dir}")
    print("Server running at http://0.0.0.0:80")
    app.run(host='0.0.0.0', port=80, debug=True)
