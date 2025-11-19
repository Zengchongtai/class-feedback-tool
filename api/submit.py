from http.server import BaseHTTPRequestHandler
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header
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
        """处理POST请求"""
        try:
            # 设置响应头
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # 获取请求数据
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            content = data.get('content', '').strip()
            feedback_type = data.get('type', 'feedback')
            
            # 验证数据
            if not content:
                response_data = {"error": "反馈内容不能为空"}
                self.wfile.write(json.dumps(response_data).encode('utf-8'))
                return
            
            logger.info(f"收到{feedback_type}反馈，内容长度: {len(content)}")
            
            # 尝试发送邮件
            email_sent = False
            email_error = None
            
            try:
                email_sent = self.send_email_notification(content, feedback_type)
            except Exception as e:
                email_error = str(e)
                logger.error(f"邮件发送失败: {email_error}")
            
            # 返回响应
            if email_sent:
                response_data = {
                    "message": "反馈提交成功！我们已收到您的灵感。",
                    "status": "success",
                    "email_sent": True
                }
            else:
                response_data = {
                    "message": "反馈提交成功！但邮件通知发送失败，我们会尽快检查。",
                    "status": "success", 
                    "email_sent": False,
                    "email_error": email_error
                }
            
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            logger.info(f"请求处理完成，邮件发送状态: {email_sent}")
            
        except Exception as e:
            # 错误处理
            error_msg = f"服务器错误: {str(e)}"
            logger.error(error_msg)
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {
                "error": "提交失败，请稍后重试",
                "debug_info": error_msg
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))

    def send_email_notification(self, content, feedback_type):
        """发送邮件通知"""
        try:
            # 从环境变量获取配置
            smtp_server = os.environ.get('SMTP_SERVER')
            smtp_port = int(os.environ.get('SMTP_PORT', 587))
            sender_email = os.environ.get('SENDER_EMAIL')
            sender_password = os.environ.get('SENDER_PASSWORD')
            receiver_email = os.environ.get('RECEIVER_EMAIL', sender_email)
            
            # 检查必要的环境变量
            if not all([smtp_server, sender_email, sender_password]):
                logger.error("缺少必要的邮件环境变量")
                return False
            
            # 根据反馈类型设置主题
            if feedback_type == 'resource_request':
                subject = "📥 新的资源申请 - 班级工具箱"
            else:
                subject = "💡 新的灵感反馈 - 班级工具箱"
            
            # 构建邮件内容
            body = f"""
            有用户通过班级工具箱提交了新的内容：
            
            内容类型：{'资源申请' if feedback_type == 'resource_request' else '灵感反馈'}
            提交时间：{self.date_time_string()}
            
            内容详情：
            {content}
            
            ---
            此邮件由班级公众号工具箱系统自动发送
            """
            
            msg = MIMEText(body, 'plain', 'utf-8')
            msg['Subject'] = Header(subject, 'utf-8')
            msg['From'] = sender_email
            msg['To'] = receiver_email
            
            # 连接SMTP服务器并发送邮件
            logger.info(f"尝试连接SMTP服务器: {smtp_server}:{smtp_port}")
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()  # 启用安全连接
            logger.info("SMTP连接成功，尝试登录...")
            server.login(sender_email, sender_password)
            logger.info("SMTP登录成功，发送邮件...")
            server.sendmail(sender_email, [receiver_email], msg.as_string())
            server.quit()
            logger.info("邮件发送成功")
            
            return True
            
        except Exception as e:
            logger.error(f"邮件发送过程出错: {str(e)}")
            return False

# Vercel要求
handler = Handler