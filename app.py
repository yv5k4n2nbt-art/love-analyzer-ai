import streamlit as st
import sqlite3
from datetime import datetime
import ollama
from duckduckgo_search import DDGS
import json
import streamlit.components.v1 as components

st.set_page_config(page_title="恋爱分析AI ❤️ 新手版", page_icon="❤️", layout="wide")

# 初始化数据库（自我训练）
if 'db_init' not in st.session_state:
    conn = sqlite3.connect('love_knowledge.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS analyses
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  query TEXT, thinking TEXT, response TEXT, timestamp TEXT)''')
    conn.commit()
    st.session_state.db_init = True
    st.session_state.conn = conn

SYSTEM_PROMPT = '''你是一个专精恋爱分析的超级AI。
融合：MIT教授级理科逻辑 + 哈佛文科洞察 + 心理学 + 微表情学。
必须先输出<思考步骤>完整逻辑链条</思考步骤>，再给出最终温暖精准的回答。
每次分析后自动保存到知识库自我训练。
使用全网搜索最新研究。'''

def get_knowledge_context():
    conn = st.session_state.conn
    c = conn.cursor()
    c.execute("SELECT query, thinking, response FROM analyses ORDER BY timestamp DESC LIMIT 5")
    rows = c.fetchall()
    if not rows:
        return ""
    context = "\n\n【历史自我训练知识库】\n"
    for row in rows:
        context += f"过去案例：{row[0]}\n思考：{row[1]}\n洞察：{row[2][:200]}...\n---\n"
    return context

def perform_web_search(query):
    with DDGS() as ddgs:
        results = [r for r in ddgs.text(query, max_results=3)]
    return "\n".join([f"{r['title']}: {r['body']}" for r in results])

def generate_response(user_input, history):
    context = get_knowledge_context()
    search_results = perform_web_search(f"恋爱心理学 微表情 {user_input} 最新研究")
    
    full_prompt = f"""{SYSTEM_PROMPT}

历史对话：{history}
用户问题：{user_input}
全网搜索结果：{search_results}
{context}

现在开始深度思考："""
    
    response = ollama.chat(model='qwen2.5:7b', messages=[{'role': 'user', 'content': full_prompt}], stream=True)
    
    thinking = ""
    final_answer = ""
    in_thinking = False
    for chunk in response:
        content = chunk['message']['content']
        if '<思考步骤>' in content or '思考步骤' in content:
            in_thinking = True
        if '</思考步骤>' in content:
            in_thinking = False
        if in_thinking:
            thinking += content
        else:
            final_answer += content
    
    # 保存到数据库自我训练
    conn = st.session_state.conn
    c = conn.cursor()
    c.execute("INSERT INTO analyses (query, thinking, response, timestamp) VALUES (?, ?, ?, ?)",
              (user_input, thinking, final_answer, datetime.now().isoformat()))
    conn.commit()
    
    return thinking, final_answer

# ==================== 新手友好界面 ====================
st.title("❤️ 恋爱分析AI - 新手超级友好版")

# 新增介绍语（中英双语）
st.markdown("""
**介绍语 / Introduction**

因为冬天已往，雨水止住过去了。  
地上百花开放，百鸟鸣叫的时候已经来到，  
斑鸠的声音在我们境内也听见了。  
无花果树的果子渐渐成熟，  
葡萄树开花放香。

---

*For behold, the winter is past; the rain is over and gone.  
The flowers appear on the earth; the time of singing has come,  
and the voice of the turtledove is heard in our land.  
The fig tree ripens its figs,  
and the vines are in blossom; they give forth fragrance.*
""")

st.caption("🎤 语音输入 + 💾 一键保存记录 + 船游戏解压 | 零基础也能轻松玩！")

# 侧边栏船游戏（保持不变）
with st.sidebar:
    st.header("🌅 解压小游戏：夕阳海洋帆船")
    st.write("←→ 转向 | ↑ 加速 | A 自动航行 | 点击画布切换")
    st.components.v1.html('''
        <style>body { margin: 0; background: linear-gradient(#ff8c00, #ffd700, #1e90ff); } canvas { display: block; margin: 0 auto; border: 1px solid #333; }</style>
        <canvas id="boatCanvas" width="600" height="400"></canvas>
        <script>
            const canvas = document.getElementById("boatCanvas");
            const ctx = canvas.getContext("2d");
            let boatX = 100, boatY = 200, speed = 0, angle = 0;
            let autoPilot = false;
            let keys = {};
            function drawBackground() {
                ctx.fillStyle = "#ff8c00"; ctx.fillRect(0,0,600,400);
                ctx.fillStyle = "#ffd700"; ctx.fillRect(0,150,600,100);
                ctx.fillStyle = "#1e90ff"; ctx.fillRect(0,250,600,150);
                ctx.fillStyle = "#ff4500"; ctx.beginPath(); ctx.arc(450,80,40,0,Math.PI*2); ctx.fill();
                ctx.strokeStyle = "#fff"; ctx.lineWidth = 3;
                for (let i = 0; i < 5; i++) {
                    ctx.beginPath(); ctx.moveTo(0,270+i*20); ctx.quadraticCurveTo(150,260+i*20,300,280+i*20); ctx.quadraticCurveTo(450,260+i*20,600,275+i*20); ctx.stroke();
                }
            }
            function drawBoat() {
                ctx.save(); ctx.translate(boatX, boatY); ctx.rotate(angle);
                ctx.fillStyle = "#8b4513"; ctx.fillRect(-30,-10,60,20);
                ctx.fillStyle = "#fff"; ctx.beginPath(); ctx.moveTo(0,-10); ctx.lineTo(0,-50); ctx.lineTo(30,-30); ctx.fill();
                ctx.fillStyle = "#ff0000"; ctx.fillRect(25,-45,15,10); ctx.restore();
            }
            function gameLoop() {
                drawBackground();
                if (autoPilot) { boatX += 2; angle = Math.sin(Date.now()/500) * 0.1; }
                else if (keys["ArrowLeft"]) angle -= 0.05;
                else if (keys["ArrowRight"]) angle += 0.05;
                else if (keys["ArrowUp"]) speed = 3;
                boatX += Math.cos(angle) * speed;
                boatY += Math.sin(angle) * 0.5;
                if (boatX > 600) boatX = 0; if (boatX < 0) boatX = 600;
                drawBoat();
                requestAnimationFrame(gameLoop);
            }
            document.addEventListener("keydown", e => { keys[e.key] = true; if (e.key === "a" || e.key === "A") autoPilot = !autoPilot; });
            document.addEventListener("keyup", e => { keys[e.key] = false; speed = 1; });
            gameLoop();
            canvas.addEventListener("click", () => { autoPilot = !autoPilot; });
        </script>
    ''', height=450, width=620)

# 新手语音输入区
st.subheader("🎤 新手语音输入（超级简单）")
st.write("**操作方法**：点击下方按钮 → 对着麦克风说话（普通话）→ 文字自动出现 → 复制到下面聊天框发送即可")
components.v1.html('''
    <button style="font-size:18px; padding:15px 30px; background:#ff69b4; color:white; border:none; border-radius:12px; cursor:pointer;" 
            onclick="startVoice()">🎤 开始说话（中文识别）</button>
    <p id="voiceResult" style="font-size:18px; margin-top:15px; padding:10px; background:#f0f0f0; border-radius:8px; min-height:50px;"></p>
    <script>
        function startVoice() {
            const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = 'zh-CN';
            recognition.interimResults = false;
            recognition.onresult = function(event) {
                const transcript = event.results[0][0].transcript;
                document.getElementById('voiceResult').innerText = transcript;
            };
            recognition.onerror = function() {
                document.getElementById('voiceResult').innerText = "😢 识别失败，请检查麦克风权限";
            };
            recognition.start();
        }
    </script>
''', height=180)

# 聊天区（保持不变）
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("在这里粘贴语音文字，或者直接打字提问（例：她发嗯但嘴角上扬是什么意思？）"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        st.write("🧠 正在深度思考... 右侧船游戏继续玩哦～")
        history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[:-1]])
        thinking, answer = generate_response(prompt, history)
        
        with st.expander("📖 完整深度思考过程（MIT+哈佛逻辑）", expanded=True):
            st.markdown(thinking)
        st.markdown(answer)
    
    st.session_state.messages.append({"role": "assistant", "content": answer})

# 一键保存聊天记录
st.divider()
st.subheader("💾 新手一键保存聊天记录")
col1, col2 = st.columns(2)
with col1:
    if st.button("📥 保存并下载本次全部聊天记录", use_container_width=True, help="点一下就下载JSON文件，超级方便备份"):
        if st.session_state.messages:
            chat_data = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            json_str = json.dumps(chat_data, ensure_ascii=False, indent=2)
            st.download_button(
                label="✅ 下载聊天记录.json",
                data=json_str,
                file_name=f"恋爱AI聊天记录_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.json",
                mime="application/json",
                use_container_width=True
            )
        else:
            st.warning("还没有聊天记录，先聊聊看吧～")

st.success("✅ 知识库已自动自我训练！下次分析会更聪明")
st.info("**新手提示**：确保Ollama正在运行（qwen2.5:7b），语音输入需允许浏览器麦克风权限。")

    