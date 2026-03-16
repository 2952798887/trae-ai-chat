import tkinter as tk
from tkinter import ttk
import uuid
import threading
import time
from datetime import datetime
from ai_chat import AIChatClient

class ChatWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("聊天应用")
        self.root.geometry("1000x800")
        self.root.resizable(True, True)
        
        # 设置窗口图标（可选）
        # self.root.iconbitmap("icon.ico")
        
        # 初始化AI对话客户端
        self.api_key = "app-U9MYpOHqM2BU9JC3NSfJUH0j"
        self.ai_client = AIChatClient(self.api_key)
        self.last_ai_response = "admin:大家先进行自我介绍"
        
        # 每个AI用户的会话ID字典
        self.conversation_ids = {}
        
        # 对话历史
        self.chat_history = []
        
        # 轮训相关变量
        self.is_running = False
        self.current_user_index = 0
        self.after_id = None
        self.is_concurrent_running = False
        self.concurrent_after_id = None
        self.last_admin_message = "admin:大家先进行自我介绍"
        
        # 文件保存相关变量
        self.chat_file_path = ""
        self.initialize_chat_file()
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建分割窗口
        self.paned_window = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        # 左侧对话框区域
        self.chat_frame = ttk.LabelFrame(self.paned_window, text="对话框", padding=(10, 5))
        self.paned_window.add(self.chat_frame, weight=3)
        
        # 右侧用户列表区域
        self.user_frame = ttk.LabelFrame(self.paned_window, text="AI用户列表", padding=(10, 5))
        self.paned_window.add(self.user_frame, weight=1)
        
        # 初始化对话框区域
        self.init_chat_area()
        
        # 初始化用户列表区域
        self.init_user_area()
        
        # 初始化轮训控制区域
        self.init_control_area()
        
    def init_chat_area(self):
        """初始化对话框区域"""
        # 字体大小调整按钮框架
        self.font_frame = ttk.Frame(self.chat_frame)
        self.font_frame.pack(fill=tk.X, pady=(0, 5))
        
        # 字体大小调整按钮
        self.font_up_button = ttk.Button(self.font_frame, text="放大字体", command=self.increase_font_size)
        self.font_up_button.pack(side=tk.RIGHT, padx=(5, 0))
        self.font_down_button = ttk.Button(self.font_frame, text="缩小字体", command=self.decrease_font_size)
        self.font_down_button.pack(side=tk.RIGHT, padx=(5, 5))
        
        # 聊天内容区域（带滚动条）
        self.font_size = 10  # 默认字体大小
        
        # 创建滚动条框架
        self.chat_scroll_frame = ttk.Frame(self.chat_frame)
        self.chat_scroll_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建滚动条
        self.chat_scrollbar = ttk.Scrollbar(self.chat_scroll_frame, orient=tk.VERTICAL)
        self.chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 创建文本框并关联滚动条
        self.chat_text = tk.Text(self.chat_scroll_frame, wrap=tk.WORD, state=tk.DISABLED, 
                               font=("Arial", self.font_size), yscrollcommand=self.chat_scrollbar.set)
        self.chat_scrollbar.config(command=self.chat_text.yview)
        
        # 添加发送者名字的样式
        self.chat_text.tag_config("sender", font=("Arial", self.font_size, "bold"), foreground="blue")
        self.chat_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 输入区域
        self.input_frame = ttk.Frame(self.chat_frame)
        self.input_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.input_text = tk.Text(self.input_frame, height=3, wrap=tk.WORD)
        self.input_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # 发送按钮
        self.send_button = ttk.Button(self.input_frame, text="发送", width=10, command=self.send_message)
        self.send_button.pack(side=tk.RIGHT, padx=(0, 5))
        
    def init_user_area(self):
        """初始化用户列表区域"""
        # 用户列表
        self.user_list = tk.Listbox(self.user_frame)
        self.user_list.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 添加用户按钮
        self.add_user_button = ttk.Button(self.user_frame, text="添加用户", command=self.add_user)
        self.add_user_button.pack(fill=tk.X, pady=(0, 5))
        
    def add_user(self):
        """添加用户，生成唯一ID"""
        # 生成唯一用户ID
        user_id = str(uuid.uuid4())[:8]  # 取前8位作为用户ID
        user_name = f"AI_{user_id}"
        
        # 添加到用户列表
        self.user_list.insert(tk.END, user_name)
    
    def initialize_chat_file(self):
        """初始化聊天文件"""
        # 生成当前日期时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 生成文件名
        self.chat_file_path = f"chat_{timestamp}.txt"
        print(f"聊天记录将保存到: {self.chat_file_path}")
    
    def init_control_area(self):
        """初始化轮训控制区域"""
        # 创建控制框架
        self.control_frame = ttk.Frame(self.chat_frame)
        self.control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 开始按钮
        self.start_button = ttk.Button(self.control_frame, text="开始轮训", command=self.start_loop)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 开始并发按钮
        self.start_concurrent_button = ttk.Button(self.control_frame, text="开始轮询（并发）", command=self.start_concurrent_loop)
        self.start_concurrent_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 暂停按钮
        self.pause_button = ttk.Button(self.control_frame, text="暂停轮训", command=self.pause_loop, state=tk.DISABLED)
        self.pause_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 停止按钮
        self.stop_button = ttk.Button(self.control_frame, text="停止轮训", command=self.stop_loop, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        

    
    def start_loop(self):
        """开始轮训"""
        if not self.is_running:
            self.is_running = True
            self.start_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.NORMAL)
            # 暂停后重新开始时，保持原来的current_user_index
            # 只有在第一次开始时才重置为0
            # self.current_user_index = 0
            self.run_loop()
    
    def start_concurrent_loop(self):
        """开始并发轮询"""
        if not self.is_concurrent_running:
            self.is_concurrent_running = True
            self.start_concurrent_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.NORMAL)
            self.run_concurrent_loop()
    
    def pause_loop(self):
        """暂停轮训"""
        if self.is_running:
            self.is_running = False
            if self.after_id:
                self.root.after_cancel(self.after_id)
                self.after_id = None
            self.start_button.config(state=tk.NORMAL)
        if self.is_concurrent_running:
            self.is_concurrent_running = False
            if self.concurrent_after_id:
                self.root.after_cancel(self.concurrent_after_id)
                self.concurrent_after_id = None
            self.start_concurrent_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
    
    def stop_loop(self):
        """停止轮训"""
        self.is_running = False
        self.is_concurrent_running = False
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        if self.concurrent_after_id:
            self.root.after_cancel(self.concurrent_after_id)
            self.concurrent_after_id = None
        self.start_button.config(state=tk.NORMAL)
        self.start_concurrent_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)
        self.current_user_index = 0
        # 清空对话历史和会话ID
        self.chat_history = []
        self.conversation_ids = {}
        # 重新初始化聊天文件，下次开始时会使用新文件
        self.initialize_chat_file()
    
    def run_loop(self):
        """运行轮训"""
        if not self.is_running:
            return
        
        # 获取用户列表
        user_count = self.user_list.size()
        if user_count < 2:
            self.stop_loop()
            self.display_message("系统", "AI用户列表至少需要2个用户才能开始轮训")
            return
        
        # 确保当前用户索引有效，如果无效则重置为0
        if self.current_user_index >= user_count:
            self.current_user_index = 0
        
        # 获取当前用户
        current_user = self.user_list.get(self.current_user_index)
        
        # 使用多线程处理AI API调用，避免UI线程阻塞
        def process_ai_response():
            # 构建最近的对话历史，只保留相关AI的最近发言
            user_count = self.user_list.size()
            if user_count > 0:
                # 获取所有AI用户
                all_users = [self.user_list.get(i) for i in range(user_count)]
                
                # 确定当前用户的前两个发言者
                # 例如：轮训顺序是A→B→C→A→B→C...
                # 当轮到A时，前两个是C和B
                # 当轮到B时，前两个是A和C
                # 当轮到C时，前两个是B和A
                prev1_index = (self.current_user_index - 1) % user_count
                prev2_index = (self.current_user_index - 2) % user_count
                prev_users = [all_users[prev1_index], all_users[prev2_index]]
                
                # 收集最近的对话历史，保留所有AI和admin的最近发言
                recent_history = []
                user_last_message = {}
                
                # 倒序遍历对话历史，收集每个用户的最近发言
                for msg in reversed(self.chat_history):
                    # 提取发送者
                    if ":" in msg:
                        sender = msg.split(":", 1)[0].strip()
                        # 收集所有AI用户和admin的消息
                        if (sender in all_users or sender == "admin") and sender not in user_last_message:
                            user_last_message[sender] = msg
                            recent_history.insert(0, msg)
                    
                    # 收集了所有用户的消息后停止
                    if len(user_last_message) >= len(all_users) + 1:  # +1 是为了包含admin
                        break
                
                if recent_history:
                    # 直接使用对话历史，不添加引导语，去除每条消息末尾的换行符
                    query = "\n".join([msg.rstrip() for msg in recent_history])
                else:
                    # 如果没有对话历史，使用默认的初始消息
                    query = self.last_ai_response
            else:
                # 如果没有用户，使用默认的初始消息
                query = self.last_ai_response
            
            # 获取当前用户的会话ID，如果不存在则为空
            user_conversation_id = self.conversation_ids.get(current_user, "")
            
            # 打印输入给AI的查询内容
            print(f"\n=== 输入给 {current_user} 的内容 ===")
            print(query)
            print("====================================")
            
            result = self.ai_client.send_message(
                query=query,
                user=current_user,
                response_mode="streaming",
                conversation_id=user_conversation_id
            )
            
            if result:
                # 更新当前用户的会话ID和最后回复
                self.conversation_ids[current_user] = result.get("conversation_id")
                self.last_ai_response = result.get("actual_answer", "")
                
                # 显示AI回复（在UI线程中执行）
                self.root.after(0, lambda: self.display_message(current_user, self.last_ai_response))
            
            # 更新用户索引
            self.current_user_index = (self.current_user_index + 1) % user_count
            
            # 继续轮训
            self.root.after(1000, self.run_loop)  # 1秒后继续
        
        # 启动线程处理AI API调用
        thread = threading.Thread(target=process_ai_response)
        thread.daemon = True
        thread.start()
    
    def run_concurrent_loop(self):
        """运行并发轮询"""
        if not self.is_concurrent_running:
            return
        
        user_count = self.user_list.size()
        if user_count < 2:
            self.stop_loop()
            self.display_message("系统", "AI用户列表至少需要2个用户才能开始轮询")
            return
        
        all_users = [self.user_list.get(i) for i in range(user_count)]
        completed_count = 0
        lock = threading.Lock()
        
        def worker(user):
            nonlocal completed_count
            try:
                query = self.build_context_for_user(user)
                print(f"\n=== 输入给 {user} 的内容 ===")
                print(query)
                print("====================================")
                
                user_conversation_id = self.conversation_ids.get(user, "")
                result = self.ai_client.send_message(
                    query=query,
                    user=user,
                    response_mode="streaming",
                    conversation_id=user_conversation_id
                )
                
                if result:
                    with lock:
                        self.conversation_ids[user] = result.get("conversation_id")
                        answer = result.get("actual_answer", "")
                    self.root.after(0, lambda u=user, a=answer: self.display_message(u, a))
            except Exception as e:
                print(f"AI用户 {user} 处理失败: {e}")
            finally:
                with lock:
                    completed_count += 1
                    if completed_count >= user_count:
                        self.root.after(1000, self.run_concurrent_loop)
        
        for user in all_users:
            thread = threading.Thread(target=worker, args=(user,))
            thread.daemon = True
            thread.start()
    
    def build_context_for_user(self, current_user):
        """构建上下文字符串
        
        Args:
            current_user: 当前AI用户的名称
            
        Returns:
            由其他AI用户最后发言 + （如果有）admin当前轮发言组成的查询字符串
        """
        user_count = self.user_list.size()
        if user_count <= 0:
            return ""
        
        all_users = [self.user_list.get(i) for i in range(user_count)]
        
        recent_history = []
        user_last_message = {}
        admin_in_current_round = False
        
        # 检查当前轮是否有admin发言 - 检查最后AI数量+1条消息
        if self.chat_history:
            # 确定需要检查的消息数量：AI用户数量 + 1（可能的admin发言）
            check_count = user_count + 1
            # 获取最后check_count条消息
            recent_messages = self.chat_history[-check_count:]
            # 检查这些消息中是否有admin的发言
            for msg in recent_messages:
                if msg.startswith("admin:"):
                    admin_in_current_round = True
                    break
        
        for msg in reversed(self.chat_history):
            if ":" in msg:
                sender = msg.split(":", 1)[0].strip()
                # 只包含其他AI用户的发言
                if sender in all_users and sender != current_user and sender not in user_last_message:
                    user_last_message[sender] = msg
                    recent_history.insert(0, msg)
                # 只在当前轮有admin发言时才包含admin的消息
                elif sender == "admin" and sender not in user_last_message and admin_in_current_round:
                    user_last_message[sender] = msg
                    recent_history.insert(0, msg)
            
            if len(user_last_message) >= (len(all_users) - 1) + (1 if admin_in_current_round else 0):
                break
        
        if recent_history:
            query = "\n".join([msg.rstrip() for msg in recent_history])
        else:
            # 刚开始时，发送初始消息
            query = "admin:大家介绍一下自己"
        
        return query
    
    def send_message(self):
        """发送用户消息"""
        # 获取输入框中的文本
        message = self.input_text.get(1.0, tk.END).strip()
        if message:
            # 更新最后一条admin消息
            self.last_admin_message = f"admin: {message}"
            # 以admin身份显示消息
            self.display_message("admin", message)
            # 清空输入框
            self.input_text.delete(1.0, tk.END)
    
    def save_chat_history(self):
        """保存聊天记录到文件"""
        def save_in_background():
            try:
                # 首先读取现有文件内容，以保留完整历史
                existing_content = []
                try:
                    with open(self.chat_file_path, 'r', encoding='utf-8') as f:
                        existing_content = f.readlines()
                except FileNotFoundError:
                    # 文件不存在，创建新文件
                    pass
                
                # 合并现有内容和当前聊天历史
                # 去重，避免重复消息
                all_messages = set()
                for line in existing_content:
                    all_messages.add(line.strip())
                for msg in self.chat_history:
                    all_messages.add(msg)
                
                # 写入完整的聊天历史
                with open(self.chat_file_path, 'w', encoding='utf-8') as f:
                    for msg in all_messages:
                        f.write(msg + '\n')
            except Exception as e:
                print(f"保存聊天记录失败: {e}")
        
        # 在后台线程中执行保存操作，避免阻塞UI
        thread = threading.Thread(target=save_in_background)
        thread.daemon = True
        thread.start()
    
    def display_message(self, sender, message):
        """在聊天窗口中显示消息"""
        # 只将实际的回复消息添加到对话历史，跳过状态消息
        if "正在思考..." not in message:
            self.chat_history.append(f"{sender}: {message}")
            # 限制聊天历史长度，只保留最近的2倍用户数量的消息
            user_count = self.user_list.size()
            max_history = user_count * 2
            if len(self.chat_history) > max_history:
                self.chat_history = self.chat_history[-max_history:]
            # 保存聊天记录到文件
            self.save_chat_history()
        
        # 显示到聊天窗口
        self.chat_text.config(state=tk.NORMAL)
        # 先插入发送者名字并应用样式
        self.chat_text.insert(tk.END, f"{sender}: ", "sender")
        # 再插入消息内容
        self.chat_text.insert(tk.END, f"{message}\n\n")
        self.chat_text.config(state=tk.DISABLED)
        self.chat_text.see(tk.END)
    
    def increase_font_size(self):
        """放大字体"""
        if self.font_size < 20:  # 设置最大字体大小
            self.font_size += 1
            self.update_font_size()
    
    def decrease_font_size(self):
        """缩小字体"""
        if self.font_size > 6:  # 设置最小字体大小
            self.font_size -= 1
            self.update_font_size()
    
    def update_font_size(self):
        """更新字体大小"""
        # 更新发送者标签的字体大小
        self.chat_text.tag_config("sender", font=("Arial", self.font_size, "bold"), foreground="blue")
        # 更新整个文本的字体大小
        self.chat_text.config(font=("Arial", self.font_size))
        
if __name__ == "__main__":
    root = tk.Tk()
    app = ChatWindow(root)
    root.mainloop()
