import time
import requests
import streamlit as st

BACKEND_URL = "http://127.0.0.1:8004/api/v1/orchestrator"

st.set_page_config(
    page_title="AI Code Assistant",
    page_icon="🤖",
    layout="wide"
)

# ----------------------------
# Session State
# ----------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "memory" not in st.session_state:
    st.session_state.memory = []

# ----------------------------
# Sidebar
# ----------------------------

with st.sidebar:

    st.title("🤖 AI Code Assistant")

    uploaded_file = st.file_uploader(
        "Upload Python File (Optional)",
        type=["py"]
    )

    source_code = ""

    if uploaded_file is not None:
        source_code = uploaded_file.read().decode("utf-8")

    st.divider()

    st.subheader("Conversation Memory")

    if st.session_state.memory:

        for item in st.session_state.memory[-5:]:

            with st.expander(item["role"].capitalize()):
                st.write(item["content"])

    else:
        st.caption("No conversation yet.")

    st.divider()

    if st.button("Clear Chat"):

        st.session_state.messages.clear()
        st.session_state.memory.clear()
        st.rerun()

# ----------------------------
# Title
# ----------------------------

st.title("💻 AI Code Assistant")

st.caption(
    "Explain code or generate Python solutions."
)

# ----------------------------
# Display Chat History
# ----------------------------

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        if msg["type"] == "text":

            st.markdown(msg["content"])

        elif msg["type"] == "code":

            st.code(msg["content"], language="python")

        elif msg["type"] == "execution":

            st.success(
                "Execution Successful"
                if msg["content"]["success"]
                else "Execution Failed"
            )

            st.write(
                f"Execution Time: "
                f"{msg['content']['execution_time']:.3f}s"
            )

            st.write(
                f"Exit Code: "
                f"{msg['content']['exit_code']}"
            )

            if msg["content"]["stdout"]:
                st.subheader("stdout")
                st.code(msg["content"]["stdout"])

            if msg["content"]["stderr"]:
                st.subheader("stderr")
                st.code(msg["content"]["stderr"])
        elif msg["type"] == "explanation":

            st.markdown(msg["content"]["summary"])

            if msg["content"].get("lines"):

                st.markdown("---")
                st.subheader("📖 Line by Line Explanation")

                for item in msg["content"]["lines"]:

                    with st.expander(f"Line {item['line_number']}"):

                        st.code(
                            item["line"],
                            language="python"
                        )

                        st.write(
                            item["explanation"]
                        )

# ----------------------------
# Chat Input
# ----------------------------

prompt = st.chat_input("Ask anything...")

if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "type": "text",
            "content": prompt
        }
    )

    st.session_state.memory.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    payload = {
        "user_prompt": prompt,
        "source_code": source_code
    }

    try:

        response = requests.post(
            BACKEND_URL,
            json=payload,
            timeout=120
        )

        response.raise_for_status()

        result = response.json()

    except Exception as e:

        with st.chat_message("assistant"):
            st.error(str(e))

        st.stop()

 # ----------------------------------------
# Explain Path
# ----------------------------------------

    if "generation" not in result:

        summary = result.get("summary", "")
        lines = result.get("lines", [])

        with st.chat_message("assistant"):

            # Stream the summary
            placeholder = st.empty()
            streamed = ""

            for ch in summary:
                streamed += ch
                placeholder.markdown(streamed)
                time.sleep(0.003)

            # Show line-by-line explanation
            if lines:
                st.markdown("---")
                st.subheader("📖 Line by Line Explanation")

                for item in lines:
                    with st.expander(f"Line {item['line_number']}"):

                        st.code(
                            item["line"],
                            language="python"
                        )

                        st.write(
                            item["explanation"]
                        )

        # Save the whole response to chat history
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
        # ----------------------------------------
        # Generate Path
        # ----------------------------------------

    else:

        generation = result["generation"]
        execution = result["execution"]

        with st.chat_message("assistant"):

            st.subheader("Generated Code")

            st.code(
                generation["code"],
                language="python"
            )

            if generation.get("explanation"):

                st.info(
                    generation["explanation"]
                )

            if st.button(
                "▶ Execute Code",
                key=f"execute_{len(st.session_state.messages)}"
            ):

                if execution["success"]:
                    st.success("Execution Successful")
                else:
                    st.error("Execution Failed")

                st.write(
                    f"Execution Time: "
                    f"{execution['execution_time']:.3f}s"
                )

                st.write(
                    f"Exit Code: "
                    f"{execution['exit_code']}"
                )

                if execution["stdout"]:
                    st.subheader("stdout")
                    st.code(execution["stdout"])

                if execution["stderr"]:
                    st.subheader("stderr")
                    st.code(execution["stderr"])

        st.session_state.messages.append(
            {
                "role": "assistant",
                "type": "code",
                "content": generation["code"]
            }
        )

        st.session_state.memory.append(
            {
                "role": "assistant",
                "content": generation["code"]
            }
        )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "type": "execution",
                "content": execution
            }
        )