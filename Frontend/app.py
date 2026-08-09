import time
import requests
import streamlit as st

BACKEND_URL = "http://127.0.0.1:8004/api/v1/orchestrator"

st.set_page_config(
    page_title="AI Code Assistant",
    page_icon="🤖",
    layout="wide",
)

# ============================================================
# Session State
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "memory" not in st.session_state:
    st.session_state.memory = []

# ============================================================
# Sidebar
# ============================================================

with st.sidebar:

    st.title("🤖 AI Code Assistant")

    st.markdown("### Conversation Memory")

    if st.session_state.memory:

        for idx, item in enumerate(reversed(st.session_state.memory[-10:]), 1):

            preview = item["content"].replace("\n", " ")

            if len(preview) > 60:
                preview = preview[:60] + "..."

            icon = "👤" if item["role"] == "user" else "🤖"

            st.markdown(
                f"""
**{icon} {item["role"].capitalize()}**

{preview}

---
"""
            )

    else:
        st.caption("No conversation yet.")

    st.divider()

    if st.button("🗑 Clear Chat", use_container_width=True):
        st.session_state.messages.clear()
        st.session_state.memory.clear()
        st.rerun()

# ============================================================
# Header
# ============================================================

st.title("💻 AI Code Assistant")

st.caption(
    "Generate Python code, explain source code, and execute generated solutions."
)

# ============================================================
# Render Previous Messages
# ============================================================

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        if msg["type"] == "text":

            st.markdown(msg["content"])

        elif msg["type"] == "explanation":

            st.markdown(f"### 📌 Summary")

            st.info(msg["content"]["summary"])

            if msg["content"]["lines"]:

                st.markdown("### 📖 Line by Line Explanation")

                for line in msg["content"]["lines"]:

                    cols = st.columns([1, 3])

                    with cols[0]:
                        st.markdown(
                            f"**Line {line['line_number']}**"
                        )

                    with cols[1]:
                        st.code(
                            line["line"],
                            language="python",
                        )

                        st.caption(line["explanation"])

        elif msg["type"] == "code":

            st.markdown("### Generated Code")

            st.code(
                msg["content"],
                language="python",
            )

        elif msg["type"] == "execution":

            execution = msg["content"]

            if execution["success"]:
                st.success("✅ Execution Successful")
            else:
                st.error("❌ Execution Failed")

            col1, col2 = st.columns(2)

            col1.metric(
                "Execution Time",
                f"{execution['execution_time']:.3f}s",
            )

            col2.metric(
                "Exit Code",
                execution["exit_code"],
            )

            if execution["stdout"]:

                st.markdown("#### stdout")

                st.code(
                    execution["stdout"],
                    language="text",
                )

            if execution["stderr"]:

                st.markdown("#### stderr")

                st.code(
                    execution["stderr"],
                    language="text",
                )

# ============================================================
# Chat Input
# ============================================================

prompt = st.chat_input("Ask something...")

if prompt:

    # ---------------- USER ----------------

    st.session_state.messages.append(
        {
            "role": "user",
            "type": "text",
            "content": prompt,
        }
    )

    st.session_state.memory.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    # ---------------- REQUEST ----------------

    try:

        response = requests.post(
            BACKEND_URL,
            json={
                "user_prompt": prompt,
            },
            timeout=120,
        )

        response.raise_for_status()

        result = response.json()

    except Exception as e:

        with st.chat_message("assistant"):
            st.error(str(e))

        st.stop()

    # ========================================================
    # Explain Path
    # ========================================================

    if "generation" not in result:

        summary = result["summary"]
        lines = result.get("lines", [])

        with st.chat_message("assistant"):

            placeholder = st.empty()

            streamed = ""

            for ch in summary:

                streamed += ch

                placeholder.markdown(streamed)

                time.sleep(0.003)

            if lines:

                st.markdown("---")

                st.markdown("## 📖 Line by Line Explanation")

                for line in lines:

                    cols = st.columns([1, 3])

                    with cols[0]:

                        st.markdown(
                            f"**Line {line['line_number']}**"
                        )

                    with cols[1]:

                        st.code(
                            line["line"],
                            language="python",
                        )

                        st.caption(
                            line["explanation"]
                        )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "type": "explanation",
                "content": result,
            }
        )

        st.session_state.memory.append(
            {
                "role": "assistant",
                "content": summary,
            }
        )

    # ========================================================
    # Generate Path
    # ========================================================

    else:

        generation = result["generation"]
        execution = result["execution"]

        with st.chat_message("assistant"):

            st.markdown("## 💻 Generated Code")

            st.code(
                generation["code"],
                language="python",
            )

            if generation.get("explanation"):

                st.info(generation["explanation"])

            if st.button(
                "▶ Execute Code",
                use_container_width=True,
                key=f"run_{len(st.session_state.messages)}",
            ):

                if execution["success"]:
                    st.success("Execution Successful")
                else:
                    st.error("Execution Failed")

                col1, col2 = st.columns(2)

                col1.metric(
                    "Execution Time",
                    f"{execution['execution_time']:.3f}s",
                )

                col2.metric(
                    "Exit Code",
                    execution["exit_code"],
                )

                if execution["stdout"]:

                    st.markdown("#### stdout")

                    st.code(
                        execution["stdout"],
                        language="text",
                    )

                if execution["stderr"]:

                    st.markdown("#### stderr")

                    st.code(
                        execution["stderr"],
                        language="text",
                    )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "type": "code",
                "content": generation["code"],
            }
        )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "type": "execution",
                "content": execution,
            }
        )

        st.session_state.memory.append(
            {
                "role": "assistant",
                "content": generation["code"],
            }
        )