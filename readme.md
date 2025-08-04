# 资本杀项目 - 简易文档型数据库 api 文档

可以通过下述的 api，实现线上多人游戏系统

游戏客户端： .html

游戏后台数据： .json .csv .txt

## 概述
本项目是一个文件上传和管理系统，提供了上传文件、获取文件元数据以及读取文件内容等功能。

上传的文件目录为 /uploads

上传的类型为 html, json, csv, txt

上传大小限制为 2MB

## 1. 获取文件元数据
- **路径**: `/meta/<filename>`
- **方法**: `GET`
- **功能**: 获取指定文件的元数据信息

##### 参数
| 参数名 | 类型 | 位置 | 描述 |
|--------|------|------|------|
| filename | 字符串 | URL路径 | 要查询的文件名 |

##### 响应
- 成功 (200 OK):
```json
{
  "filename": "example.html",
  "ext": ".html",
  "size": 1024,
  "created": 1620000000.0,
  "modified": 1620000000.0
}
```
- 失败 (404 Not Found):
```
File not found
```

## 2. 读取文件内容
- **路径**: `/content/<filename>`
- **方法**: `GET`
- **功能**: 读取指定文件的内容，支持行范围查询

##### 参数
| 参数名 | 类型 | 位置 | 描述 |
|--------|------|------|------|
| filename | 字符串 | URL路径 | 要读取的文件名 |
| start | 整数 | 查询参数 | 起始行号 (从1开始) |
| end | 整数 | 查询参数 | 结束行号 |
| count | 整数 | 查询参数 | 要读取的行数 |
| reverse | 布尔值 | 查询参数 | 是否反转文件内容 (默认: false) |

##### 说明
- 如果同时指定 `start` 和 `count`，则 `end` 参数会被忽略
- 如果没有指定任何行范围参数，则返回整个文件内容

##### 响应
- 成功 (200 OK):
  返回指定范围的文件内容 (文本格式)
- 失败 (404 Not Found):
```
File not found
```

## 3. 上传文件
- **路径**: `/upload`
- **方法**: `POST`
- **功能**: 上传文件到服务器

##### 请求头
| 头部名称 | 描述 |
|----------|------|
| Content-Length | 文件大小 (不能超过 2MB) |

##### 请求体
- 格式: `multipart/form-data`
- 字段: `file` (要上传的文件)
- 字段: `replace` (是否替换已存在的文件，默认: false) (可选)

##### 限制
- 只允许上传扩展名为 `.html`, `.json`, `.csv`, `.txt` 的文件
- 文件大小不能超过 2MB

##### 响应
- 成功 (200 OK):
```
File uploaded successfully. View it at: /uploads/filename.html
```
- 失败:
  - 400 Bad Request (文件大小超过限制):
```
File size exceeds 2MB limit
```
  - 400 Bad Request (没有文件部分):
```
No file part
```
  - 400 Bad Request (没有选择文件):
```
No selected file
```
  - 400 Bad Request (文件类型不允许):
```
Only HTML, JSON, CSV, and TXT files are allowed
```

## 4. 按行更新文件内容
- **路径**: `/update/<filename>`
- **方法**: `POST`
- **功能**: 替换文件中指定行范围的内容

##### 参数
| 参数名 | 类型 | 位置 | 描述 |
|--------|------|------|------|
| filename | 字符串 | URL路径 | 要修改的文件名 |
| start | 整数 | 请求体(JSON) | 起始行号 (从1开始，默认: 1) |
| end | 整数 | 请求体(JSON) | 结束行号 (默认: 文件最后一行) |
| count | 整数 | 请求体(JSON) | 要替换的行数 (如果指定，将覆盖end参数) |
| new_content | 字符串 | 请求体(JSON) | 新的内容 |

##### 说明
- 请求体必须是 JSON 格式
- 如果同时指定 `start` 和 `count`，则 `end` 参数会被忽略
- 如果没有指定 `start`，则从第一行开始
- 如果没有指定 `end` 或 `count`，则替换到文件末尾
- 如果没有指定任何行范围参数，则替换整个文件内容，效果如同上传 /upload 文件时的 `replace=true` 参数

##### 响应
- 成功 (200 OK):
```
Content replaced successfully
```
- 失败:
  - 400 Bad Request (缺少文件名):
```
Filename is required
```
  - 400 Bad Request (缺少新内容):
```
New content is required
```
  - 404 Not Found (文件不存在):
```
File not found
```
  - 500 Internal Server Error (读取或写入文件错误):
```
Error reading file: [错误信息]
```
或
```
Error writing file: [错误信息]
```

##### 使用示例
```bash
curl -X POST -H "Content-Type: application/json" -d '{"start": 5, "count": 3, "new_content": "这是新的第5-7行内容\n包含多行\n的示例"}' http://localhost:5000/replace/example.html
```

```bash
curl -X POST -H "Content-Type: application/json" -d '{"start": 1, "end": 10, "new_content": "替换前10行内容"}' http://localhost:5000/replace/example.html
```
        

## 使用示例

### 上传文件
```bash
curl -X POST -F "file=@example.html" /upload
```

### 获取文件元数据
```bash
curl /meta/example.html
```

### 读取文件内容
```bash
curl /content/example.html?start=1&count=10
```
