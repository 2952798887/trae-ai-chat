import requests
import json
import sseclient
from ai_response_extractor import extract_ai_response

class AIChatClient:
    def __init__(self, api_key, base_url="http://192.168.113.73/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.last_ai_response = ""
    

    
    def send_message(self, query, user, response_mode="streaming", conversation_id="", inputs={}, files=[]):
        """发送消息并处理响应"""
        url = f"{self.base_url}/chat-messages"
        payload = {
            "query": query,
            "user": user,
            "response_mode": response_mode,
            "conversation_id": conversation_id,
            "inputs": inputs,
            "files": files
        }
        
        if response_mode == "streaming":
            # 处理流式响应
            response = requests.post(url, headers=self.headers, json=payload, stream=True)
            client = sseclient.SSEClient(response)
            full_answer = ""
            
            for event in client.events():
                if event.data:
                    try:
                        data = json.loads(event.data)
                        if data.get("event") == "message":
                            full_answer += data.get("answer", "")
                        elif data.get("event") == "message_end":
                            print()
                            # 提取实际回复内容
                            actual_response = extract_ai_response(full_answer)
                            return {
                                "message_id": data.get("message_id"),
                                "conversation_id": data.get("conversation_id"),
                                "answer": full_answer,
                                "actual_answer": actual_response,
                                "metadata": data.get("metadata")
                            }
                        elif data.get("event") == "error":
                            print(f"Error: {data.get('message')}")
                            return None
                    except json.JSONDecodeError:
                        print(f"Invalid JSON: {event.data}")
        else:
            # 处理阻塞模式响应
            response = requests.post(url, headers=self.headers, json=payload)
            if response.status_code == 200:
                result = response.json()
                # 提取实际回复内容
                if "answer" in result:
                    result["actual_answer"] = extract_ai_response(result["answer"])
                return result
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None

    def get_last_ai_response(self):
        """
        获取最后一次AI的回复内容
        
        返回:
            str: 最后一次AI的回复内容
        """
        return self.last_ai_response
    
    def chat_with_ai(self, initial_message=""):
        """与AI进行交互式对话"""
        USER_ID = "test_user_123"
        conversation_id = ""
        
        print("=== AI直接交流工具 ===")
        print("输入你的问题，输入 'exit' 退出对话")
        print("输入 'last' 重复上一次AI的回复")
        print("=" * 50)
        
        last_ai_response = initial_message
        
        if initial_message:
            print(f"初始消息: {initial_message}")
            print("AI:", end=" ")
            result = self.send_message(
                query=initial_message,
                user=USER_ID,
                response_mode="streaming",
                conversation_id=conversation_id
            )
            if result:
                conversation_id = result.get("conversation_id")
                last_ai_response = result.get("actual_answer", "")
                self.last_ai_response = last_ai_response
            print()
            print("-" * 50)
        
        while True:
            # 获取用户输入
            user_input = input("你: ")
            
            # 检查是否退出
            if user_input.lower() == 'exit':
                print("对话结束，再见！")
                break
            
            # 检查是否重复上一次AI的回复
            if user_input.lower() == 'last' and last_ai_response:
                print(f"重复上一次AI回复: {last_ai_response}")
                print("AI:", end=" ")
                result = self.send_message(
                    query=last_ai_response,
                    user=USER_ID,
                    response_mode="streaming",
                    conversation_id=conversation_id
                )
            else:
                # 发送用户输入
                print("AI:", end=" ")
                result = self.send_message(
                    query=user_input,
                    user=USER_ID,
                    response_mode="streaming",
                    conversation_id=conversation_id
                )
            
            # 更新会话ID和上一次AI回复
            if result:
                conversation_id = result.get("conversation_id")
                last_ai_response = result.get("actual_answer", "")
                self.last_ai_response = last_ai_response
            
            print()
            print("-" * 50)

if __name__ == "__main__":
    # 使用用户提供的API密钥
    API_KEY = "app-U9MYpOHqM2BU9JC3NSfJUH0j"
    
    # 上一次AI的回复
    last_ai_reply = "我是疾病控制中心的AI助手，专门分析传染病相关检验结果。请上传您的检验报告，我会帮您检查是否有阳性项目。"
    
    client = AIChatClient(API_KEY)
    client.chat_with_ai(last_ai_reply)
