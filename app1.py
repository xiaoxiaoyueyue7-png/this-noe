import streamlit as st
from openai import OpenAI

# ==================== 1. 页面基本配置与微信精仿样式 ====================
st.set_page_config(page_title="微信", page_icon="💬", layout="centered")

# 使用 HTML/CSS 全局注入，完美还原微信网页版视觉
st.html("""
<style>
    /* 背景改为微信经典的浅灰白色 */
    .stApp { background-color: #f3f3f3; }
    /* 输入框容器背景与边框 */
    .stChatInputContainer { background-color: #f7f7f7; border-top: 1px solid #e5e5e5; }
    /* 隐藏 Streamlit 原生的聊天气泡组件，我们要用自己纯手工打造的微信气泡 */
    [data-testid="stChatMessage"] { display: none !important; }
</style>
""")

# 微信顶部绿色/灰色导航栏
st.html("""
<div style="background-color: #eeeeee; padding: 15px; text-align: center; font-size: 18px; font-weight: bold; border-bottom: 1px solid #e0e0e0; position: sticky; top: 0; z-index: 99; color: #000000;">
    AI 班主任（张老师）
</div>
""")

# ==================== 2. API 客户端与人设初始化 ====================
# 请在这里换上你的真实 DeepSeek API Key
DEEPSEEK_API_KEY = "sk-6fa94de4d045450ba1d1cda2de65d360" 
BASE_URL = "https://api.deepseek.com"

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=BASE_URL)

# 设定张老师的微信聊天风格
SYSTEM_PROMPT = "你是一位微信上的温柔女老师，说话喜欢带上符合语境的表情包（如🌹, 📝, ✨），语气亲切，多鼓励学生，回答要精炼，像在微信发消息一样，不要长篇大论。"

# 初始化会话状态，确保刷新页面时聊天记录不丢失
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": "同学你好呀！我是张老师。今天有什么不懂的作业或者想聊的话题吗？🌹", "type": "text"}
    ]

# ==================== 3. 微信对话气泡渲染核心函数 ====================
def render_wechat_msg(role, content, msg_type="text", media_url=None):
    """
    通过纯 HTML + Inline CSS 强行复刻微信的左/右气泡布局
    """
    # 微信官方风格的男女头像占位图
    teacher_avatar = "https://cdn-icons-png.flaticon.com/512/194/194938.png"  # 老师头像
    student_avatar = "https://cdn-icons-png.flaticon.com/512/147/147144.png"  # 学生头像
    
    if role == "assistant":  # 老师在左边，白色气泡
        avatar = teacher_avatar
        html_code = f"""
        <div style="display: flex; justify-content: flex-start; margin-bottom: 15px; align-items: flex-start; padding: 0 10px;">
            <img src="{avatar}" style="width: 40px; height: 40px; border-radius: 4px; margin-right: 10px;">
            <div style="background-color: #ffffff; padding: 10px 14px; border-radius: 4px; max-width: 70%; position: relative; box-shadow: 0px 1px 2px rgba(0,0,0,0.05); word-wrap: break-word; font-size: 15px; color: #000000; line-height: 1.4;">
                <div style="position: absolute; left: -6px; top: 14px; width: 0; height: 0; border-top: 6px solid transparent; border-bottom: 6px solid transparent; border-right: 6px solid #ffffff;"></div>
        """
        # 根据消息类型嵌入多媒体
        if msg_type == "text":
            html_code += f"{content}"
        elif msg_type == "audio":
            html_code += f"<div style='margin-bottom:8px;'>{content}</div><audio controls style='max-width: 100%; height: 30px;' src='{media_url}'></audio>"
        elif msg_type == "video":
            html_code += f"<div style='margin-bottom:8px;'>{content}</div><video controls style='max-width: 100%; border-radius: 4px;' src='{media_url}'></video>"
            
        html_code += "</div></div>"
        
    elif role == "user":  # 学生在右边，经典的微信绿气泡 (#95ec69)
        avatar = student_avatar
        html_code = f"""
        <div style="display: flex; justify-content: flex-end; margin-bottom: 15px; align-items: flex-start; padding: 0 10px;">
            <div style="background-color: #95ec69; padding: 10px 14px; border-radius: 4px; max-width: 70%; position: relative; box-shadow: 0px 1px 2px rgba(0,0,0,0.05); word-wrap: break-word; font-size: 15px; color: #000000; margin-right: 10px; line-height: 1.4;">
                <div style="position: absolute; right: -6px; top: 14px; width: 0; height: 0; border-top: 6px solid transparent; border-bottom: 6px solid transparent; border-left: 6px solid #95ec69;"></div>
                {content}
            </div>
            <img src="{avatar}" style="width: 40px; height: 40px; border-radius: 4px;">
        </div>
        """
    st.html(html_code)

# ==================== 4. 渲染历史聊天记录 ====================
for msg in st.session_state.messages:
    if msg.get("role") != "system":
        render_wechat_msg(
            role=msg.get("role"), 
            content=msg.get("content"), 
            msg_type=msg.get("type", "text"), 
            media_url=msg.get("media_url", None)
        )

# ==================== 5. 处理用户新输入与多媒体触发逻辑 ====================
if user_input := st.chat_input("发消息..."):
    
    # 1. 立即把学生发的消息存入历史并渲染到屏幕上
    st.session_state.messages.append({"role": "user", "content": user_input, "type": "text"})
    render_wechat_msg("user", user_input)
    
    # 2. 模拟微信多媒体触发机制（检测学生关键词）
    msg_type = "text"
    media_url = None
    
    if "视频" in user_input:
        msg_type = "video"
        # 这是一个公开可用的测试视频链接
        media_url = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"
    elif "语音" in user_input or "听" in user_input or "发声" in user_input:
        msg_type = "audio"
        # 这是一个公开可用的测试音频链接
        media_url = "https://www.w3schools.com/html/horse.mp3"

    # 3. 过滤出发送给 API 的上下文（安全使用 .get 防止 KeyError）
    api_messages = []
    for m in st.session_state.messages:
        if m.get("type", "text") == "text" or m.get("role") == "system":
            # 微信多媒体行由于带有 HTML 标签，不适合直接传给大模型，我们只传文本
            api_messages.append({"role": m.get("role"), "content": m.get("content")})
    
    # 4. 调用 DeepSeek 获取老师的文字回复
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=api_messages,
            stream=False  # 微信聊天习惯一整条蹦出来，所以不用流式
        )
        teacher_reply = response.choices[0].message.content
    except Exception as e:
        teacher_reply = "张老师这会儿手机信号有点不好 😥 刚刚没听清，你能再说一遍吗？"

    # 5. 根据触发的多媒体类型，对老师的文本做微调
    if msg_type == "video":
        teacher_reply = "【视频动态】同学，文字说不明白，老师录了个视频给你，点开看看：<br>" + teacher_reply
    elif msg_type == "audio":
        teacher_reply = "【语音消息】给你发条语音：<br>" + teacher_reply

    # 6. 把老师的最终回复（包含多媒体信息）存入历史
    st.session_state.messages.append({
        "role": "assistant", 
        "content": teacher_reply, 
        "type": msg_type, 
        "media_url": media_url
    })
    
    # 7. 强制刷新 Streamlit 页面更新视图
    st.rerun()