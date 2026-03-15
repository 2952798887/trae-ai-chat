def extract_ai_response(ai_reply):
    """
    提取AI回复的实际内容，去除<think>标签
    
    参数:
        ai_reply (str): AI的原始回复内容
    
    返回:
        str: 提取后的实际回复内容
    """
    if "<think>" in ai_reply and "</think>" in ai_reply:
        # 找到<think>标签的开始和结束位置
        start_idx = ai_reply.find("<think>") + len("<think>")
        end_idx = ai_reply.find("</think>")
        # 提取</think>标签之后的内容
        actual_response = ai_reply[end_idx + len("</think>"):].strip()
        return actual_response
    return ai_reply

if __name__ == "__main__":
    # 测试示例
    test_reply = "<think>这是思考过程</think>这是实际回复内容"
    print("原始回复:", test_reply)
    print("提取后:", extract_ai_response(test_reply))
