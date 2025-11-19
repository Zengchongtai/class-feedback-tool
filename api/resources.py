from http.server import BaseHTTPRequestHandler
import json
import os

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """处理GET请求，返回资源列表"""
        # 设置CORS头部
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        
        try:
            # 读取资源数据文件
            file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'resources.json')
            with open(file_path, 'r', encoding='utf-8') as f:
                resources_data = json.load(f)
            
            # 返回资源列表
            self.wfile.write(json.dumps(resources_data, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            # 如果出错，返回空数组
            self.wfile.write(json.dumps([]).encode('utf-8'))

# Vercel要求
handler = Handler