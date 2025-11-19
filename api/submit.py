from http.server import BaseHTTPRequestHandler
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """处理预检请求（CORS）"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        """处理POST请求 - 简化版本"""
        try:
            # 设置响应头
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # 获取请求数据
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                content = data.get('content', '')
                logger.info(f"收到反馈: {content[:100]}...")  # 只记录前100个字符
            else:
                content = ""
            
            # 返回成功响应（不发送邮件）
            response_data = {
                "message": "反馈提交成功！",
                "status": "success",
                "received_length": len(content)
            }
            
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            logger.info("成功返回响应")
            
        except Exception as e:
            # 详细的错误处理
            error_msg = f"服务器错误: {str(e)}"
            logger.error(error_msg)
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {
                "error": error_msg,
                "type": type(e).__name__
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))

# ⭐⭐⭐ 重要：这行必须在文件末尾，没有缩进！⭐⭐⭐
handler = Handler