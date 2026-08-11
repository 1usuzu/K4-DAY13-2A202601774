import streamlit as st
import requests
import uuid

# Configuration
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI Chat Demo", page_icon="🤖", layout="wide")

# Initialize session state for user/session ID and chat history
if "session_id" not in st.session_state:
    st.session_state.session_id = f"demo-session-{uuid.uuid4().hex[:8]}"
if "user_id" not in st.session_state:
    st.session_state.user_id = "demo-user"
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar: Control Panel ---
with st.sidebar:
    st.title("🛠️ Control Panel")
    st.write("Dùng để kích hoạt/tắt các sự cố (Incidents) theo thời gian thực.")
    
    st.divider()
    
    # Fetch current health to set initial toggle states
    try:
        health_res = requests.get(f"{API_URL}/health", timeout=2).json()
        incidents = health_res.get("incidents", {})
        api_status = "🟢 Online"
    except Exception:
        incidents = {"rag_slow": False, "tool_fail": False, "cost_spike": False}
        api_status = "🔴 Offline"
        
    st.write(f"**API Status:** {api_status}")
    
    st.subheader("🔥 Inject Incidents")
    
    def toggle_incident(incident_name, current_state):
        action = "disable" if current_state else "enable"
        try:
            requests.post(f"{API_URL}/incidents/{incident_name}/{action}")
        except Exception as e:
            st.error(f"Failed to {action} {incident_name}: {e}")

    rag_slow = st.toggle("RAG Slow (Latency Spike)", value=incidents.get("rag_slow", False))
    if rag_slow != incidents.get("rag_slow", False):
        toggle_incident("rag_slow", incidents.get("rag_slow", False))
        st.rerun()
        
    tool_fail = st.toggle("Tool Fail (500 Errors)", value=incidents.get("tool_fail", False))
    if tool_fail != incidents.get("tool_fail", False):
        toggle_incident("tool_fail", incidents.get("tool_fail", False))
        st.rerun()
        
    cost_spike = st.toggle("Cost Spike (Tokens x4)", value=incidents.get("cost_spike", False))
    if cost_spike != incidents.get("cost_spike", False):
        toggle_incident("cost_spike", incidents.get("cost_spike", False))
        st.rerun()

    st.divider()
    st.write(f"**Session ID:** `{st.session_state.session_id}`")
    st.write(f"**User ID:** `{st.session_state.user_id}`")
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# --- Main Area: Chat UI ---
st.title("🤖 Chat Demo (Observability)")

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "meta" in msg:
            st.caption(f"⏱️ **Latency**: {msg['meta']['latency_ms']}ms | 🪙 **Cost**: ${msg['meta']['cost_usd']:.4f} | 📝 **Tokens**: {msg['meta']['tokens_in']} In / {msg['meta']['tokens_out']} Out | 🔍 **ID**: `{msg['meta']['correlation_id']}`")
        if "error" in msg:
            st.error(msg["error"])

# Chat input
if prompt := st.chat_input("Nhập câu hỏi của bạn (VD: What is your refund policy?)"):
    # Add user message to state and display
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Call API
    with st.chat_message("assistant"):
        with st.spinner("Đang suy nghĩ..."):
            payload = {
                "user_id": st.session_state.user_id,
                "session_id": st.session_state.session_id,
                "feature": "monitoring",
                "message": prompt
            }
            try:
                res = requests.post(f"{API_URL}/chat", json=payload)
                if res.status_code == 200:
                    data = res.json()
                    answer = data.get("answer", "")
                    st.write(answer)
                    
                    meta = {
                        "latency_ms": data.get("latency_ms"),
                        "cost_usd": data.get("cost_usd"),
                        "tokens_in": data.get("tokens_in"),
                        "tokens_out": data.get("tokens_out"),
                        "correlation_id": data.get("correlation_id")
                    }
                    st.caption(f"⏱️ **Latency**: {meta['latency_ms']}ms | 🪙 **Cost**: ${meta['cost_usd']:.4f} | 📝 **Tokens**: {meta['tokens_in']} In / {meta['tokens_out']} Out | 🔍 **ID**: `{meta['correlation_id']}`")
                    st.session_state.messages.append({"role": "assistant", "content": answer, "meta": meta})
                else:
                    err_msg = f"API Error: {res.status_code} - {res.text}"
                    st.error(err_msg)
                    st.session_state.messages.append({"role": "assistant", "content": "⚠️ Đã xảy ra lỗi hệ thống.", "error": err_msg})
            except Exception as e:
                err_msg = f"Connection Error: {str(e)}"
                st.error(err_msg)
                st.session_state.messages.append({"role": "assistant", "content": "⚠️ Mất kết nối tới API.", "error": err_msg})
