import streamlit as st
from langchain_ollama import ChatOllama
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import SystemMessage, HumanMessage

st.set_page_config(page_title="恋爱分析AI", page_icon="❤️", layout="wide")
st.title("❤️ 恋爱分析AI")
st.caption("MIT理科逻辑 + 哈佛文科心理学 + 微表情 + 全网搜索 | 完全本地免费")

# 侧边栏
with st.sidebar:
    st.header("⚙️ 设置")
    model_name = st.selectbox("选择Ollama模型", ["qwen2.5:7b", "llama3.2:3b"], index=0)
    temperature = st.slider("创造性 (temperature)", 0.0, 1.0, 0.7)
    enable_search = st.checkbox("✅ 启用全网搜索", value=True)
    st.info("需先安装Ollama并运行 `ollama pull qwen2.5:7b`")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

SYSTEM_PROMPT = '''你是一个世界顶级的恋爱分析智能AI。
融合MIT教授的理科严谨逻辑分析 + 哈佛大学文科教授的人文心理学洞察。
精通逻辑学、心理学（依恋理论、沟通模式）、微表情学（Paul Ekman理论）。
分析任何恋爱问题时必须：共情 + 逻辑推理 + 心理学依据 + 微表情解读 + 实用建议。
如果需要最新数据，自动使用搜索工具整合。'''

if prompt := st.chat_input("输入你的恋爱问题、聊天记录或微表情描述..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    llm = ChatOllama(model=model_name, temperature=temperature)

    search_context = ""
    if enable_search:
        try:
            search_tool = DuckDuckGoSearchRun()
            search_result = search_tool.run(prompt[:150])
            search_context = f"\n\n【全网实时搜索】：{search_result[:600]}..."
        except:
            search_context = "\n\n（搜索暂不可用，使用内置知识）"

    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    for msg in st.session_state.messages[-8:]:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(SystemMessage(content=msg["content"]))
    messages.append(HumanMessage(content=prompt + search_context))

    with st.chat_message("assistant"):
        with st.spinner("AI深度分析中... ❤️"):
            response = llm.invoke(messages)
            st.markdown(response.content)

    st.session_state.messages.append({"role": "assistant", "content": response.content})

st.success("✅ AI已就绪！仓库：https://github.com/yv5k4n2nbt-art/love-analyzer-ai")