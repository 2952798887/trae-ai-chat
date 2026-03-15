import requests
import json
import sseclient

class WorkflowChatAPI:
    def __init__(self, api_key, base_url="http://192.168.113.73/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def send_message(self, query, user, response_mode="streaming", conversation_id="", inputs={}, files=[]):
        """发送对话消息"""
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
                            print(data.get("answer"), end="", flush=True)
                            full_answer += data.get("answer", "")
                        elif data.get("event") == "message_end":
                            print()
                            return {
                                "message_id": data.get("message_id"),
                                "conversation_id": data.get("conversation_id"),
                                "answer": full_answer,
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
                return response.json()
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
    
    def upload_file(self, file_path, user):
        """上传文件"""
        url = f"{self.base_url}/files/upload"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        with open(file_path, 'rb') as f:
            files = {
                'file': f
            }
            data = {
                'user': user
            }
            response = requests.post(url, headers=headers, files=files, data=data)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
    
    def get_conversations(self, user, limit=20, last_id="", pinned=None, sort_by="-updated_at"):
        """获取会话列表"""
        url = f"{self.base_url}/conversations"
        params = {
            "user": user,
            "limit": limit,
            "last_id": last_id,
            "sort_by": sort_by
        }
        if pinned is not None:
            params["pinned"] = pinned
        
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    
    def get_messages(self, conversation_id, user, limit=20, first_id=""):
        """获取会话历史消息"""
        url = f"{self.base_url}/messages"
        params = {
            "conversation_id": conversation_id,
            "user": user,
            "limit": limit,
            "first_id": first_id
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

def interactive_chat():
    """交互式对话功能"""
    # 使用用户提供的API密钥
    API_KEY = "app-U9MYpOHqM2BU9JC3NSfJUH0j"
    USER_ID = "test_user_123"
    
    api = WorkflowChatAPI(API_KEY)
    conversation_id = ""
    
    print("=== 工作流编排对话型应用 ===")
    print("输入你的问题，输入 'exit' 退出对话")
    print("=" * 50)
    
    while True:
        # 获取用户输入
        user_input = input("你: ")
        
        # 检查是否退出
        if user_input.lower() == 'exit':
            print("对话结束，再见！")
            break
        
        # 发送消息
        print("AI:", end=" ")
        result = api.send_message(
            query=user_input,
            user=USER_ID,
            response_mode="streaming",
            conversation_id=conversation_id
        )
        
        # 更新会话ID，保持对话上下文
        if result:
            conversation_id = result.get("conversation_id")
        
        print()
        print("-" * 50)

if __name__ == "__main__":
    interactive_chat()
