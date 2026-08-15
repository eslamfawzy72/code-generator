import html
import re
import time
from typing import Any

import requests
import streamlit as st

BACKEND_URL = "http://127.0.0.1:8004/api/v1/orchestrator"
LEARN_URL = "http://127.0.0.1:8004/api/v1/learn"
VOICE_ANALYSIS_URL = "http://127.0.0.1:8004/api/v1/voice_pipeline"


def has_arabic_text(value: str | None) -> bool:
    return bool(value and re.search(r"[\u0600-\u06FF]", value))


def format_file_size(size: int | None) -> str:
    if size is None:
        return "Unknown size"

    if size < 1024:
        return f"{size} B"

    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"

    return f"{size / (1024 * 1024):.1f} MB"


def format_result_value(value: Any) -> str:
    if value is None:
        return ""

    if isinstance(value, bool):
        return "Yes" if value else "No"

    if isinstance(value, int) and not isinstance(value, bool):
        return f"{value:,}"

    if isinstance(value, float):
        return f"{value:,.2f}"

    return str(value)


def extract_audio_payload(audio_file: Any) -> tuple[str, bytes, str]:
    filename = getattr(audio_file, "name", None) or "voice_input.wav"
    mime_type = getattr(audio_file, "type", None) or "audio/wav"
    audio_bytes = audio_file.getvalue()
    return filename, audio_bytes, mime_type


def build_result_table(result: Any) -> str | None:
    if not isinstance(result, list) or len(result) != 2:
        return None

    headers, rows = result

    if not isinstance(headers, list) or not isinstance(rows, list):
        return None

    header_cells = "".join(
        f'<th style="text-align:left;padding:0.75rem 1rem;border-bottom:1px solid rgba(148,163,184,0.25);background:rgba(15,23,42,0.72);">{html.escape(str(header))}</th>'
        for header in headers
    )

    row_markup: list[str] = []

    for row in rows:
        if isinstance(row, dict):
            row_values = [row.get(header) for header in headers]
        elif isinstance(row, (list, tuple)):
            row_values = list(row)

            if len(row_values) < len(headers):
                row_values.extend([None] * (len(headers) - len(row_values)))
            elif len(row_values) > len(headers):
                row_values = row_values[: len(headers)]
        else:
            continue

        cells = "".join(
            f'<td style="padding:0.75rem 1rem;border-bottom:1px solid rgba(148,163,184,0.16);vertical-align:top;">{html.escape(format_result_value(value))}</td>'
            for value in row_values
        )
        row_markup.append(f"<tr>{cells}</tr>")

    if not row_markup:
        return None

    return f'''
    <div style="overflow-x:auto;border:1px solid rgba(148,163,184,0.22);border-radius:18px;background:rgba(15,23,42,0.42);">
        <table style="width:100%;border-collapse:collapse;color:#e5eefb;direction:ltr;">
            <thead><tr>{header_cells}</tr></thead>
            <tbody>{''.join(row_markup)}</tbody>
        </table>
    </div>
    '''


def render_text_block(title: str, content: str | None) -> None:
    value = content or "No text returned."
    direction = "rtl" if has_arabic_text(value) else "ltr"
    alignment = "right" if direction == "rtl" else "left"

    st.markdown(
        f"""
        <div style="
            border: 1px solid rgba(148, 163, 184, 0.22);
            border-radius: 18px;
            padding: 1rem 1.1rem;
            background: rgba(15, 23, 42, 0.42);
            color: #e5eefb;
            direction: {direction};
            text-align: {alignment};
            white-space: pre-wrap;
            word-break: break-word;
        ">
            <div style="
                font-size: 0.82rem;
                letter-spacing: 0.04em;
                text-transform: uppercase;
                color: #9fb3c8;
                margin-bottom: 0.45rem;
            ">{html.escape(title)}</div>
            <div style="font-size: 1rem; line-height: 1.7;">{html.escape(value)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def reset_voice_inputs() -> None:
    for key in ("voice_recorded_audio", "voice_uploaded_audio"):
        if key in st.session_state:
            del st.session_state[key]


def render_voice_sql_page() -> None:
    st.title("🎤 Voice SQL Assistant")
    st.caption(
        "Ask your database in Arabic or English using either a live browser recording or an uploaded audio file."
    )

    st.markdown(
        """
        <style>
            .voice-hero {
                border-radius: 24px;
                padding: 1.2rem 1.3rem;
                margin-bottom: 1rem;
                background: linear-gradient(135deg, rgba(15, 118, 110, 0.22), rgba(37, 99, 235, 0.18));
                border: 1px solid rgba(148, 163, 184, 0.22);
            }
            .voice-stage-list {
                margin: 0.2rem 0 0 1rem;
                line-height: 1.75;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="voice-hero">
            <div style="font-size: 1.35rem; font-weight: 700; margin-bottom: 0.35rem;">Voice Database Query</div>
            <div style="opacity: 0.9; line-height: 1.6;">
                Record from your microphone or upload an audio file, then send it to the existing voice pipeline for transcription, normalization, SQL generation, and database execution.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    input_mode = st.radio(
        "Choose input method",
        ["Record voice", "Upload audio file"],
        horizontal=True,
        label_visibility="collapsed",
        key="voice_input_mode",
    )

    selected_audio = None

    if input_mode == "Record voice":
        st.subheader("🎙 Start Recording")

        if hasattr(st, "audio_input"):
            recorded_audio = st.audio_input(
                "Start Recording",
                key="voice_recorded_audio",
            )
        else:
            st.error(
                "Your installed Streamlit version does not expose browser audio recording. Please upload an audio file instead."
            )
            recorded_audio = None

        if recorded_audio is not None:
            selected_audio = recorded_audio

            st.success("Recording captured. You can preview it below before analyzing.")

            col_info, col_actions = st.columns([3, 1])

            with col_info:
                st.markdown(f"**File:** {html.escape(getattr(recorded_audio, 'name', 'recording.wav'))}")
                st.caption(
                    f"Size: {format_file_size(getattr(recorded_audio, 'size', None))} • Type: {getattr(recorded_audio, 'type', 'audio/wav') or 'audio/wav'}"
                )

            with col_actions:
                if st.button("Remove recording", use_container_width=True, key="voice_remove_recording"):
                    reset_voice_inputs()
                    st.rerun()

            st.audio(
                recorded_audio.getvalue(),
                format=getattr(recorded_audio, "type", None) or "audio/wav",
            )

    else:
        st.subheader("Upload Audio File")

        uploaded_audio = st.file_uploader(
            "Upload Audio File",
            type=["m4a", "wav", "mp3", "webm", "ogg", "mp4"],
            accept_multiple_files=False,
            key="voice_uploaded_audio",
        )

        if uploaded_audio is not None:
            selected_audio = uploaded_audio

            st.success("Audio file selected. You can preview it below before analyzing.")

            col_info, col_actions = st.columns([3, 1])

            with col_info:
                st.markdown(f"**File:** {html.escape(uploaded_audio.name)}")
                st.caption(
                    f"Size: {format_file_size(getattr(uploaded_audio, 'size', None))} • Type: {uploaded_audio.type or 'audio/wav'}"
                )

            with col_actions:
                if st.button("Remove file", use_container_width=True, key="voice_remove_upload"):
                    reset_voice_inputs()
                    st.rerun()

            st.audio(
                uploaded_audio.getvalue(),
                format=uploaded_audio.type or "audio/wav",
            )

    can_analyze = selected_audio is not None

    if not can_analyze:
        st.info("Provide a recording or an audio file to enable analysis.")

    analyze_clicked = st.button(
        "Analyze Voice",
        type="primary",
        use_container_width=True,
        disabled=not can_analyze,
    )

    if not analyze_clicked:
        return

    if selected_audio is None:
        st.error("Please provide audio before analyzing.")
        return

    try:
        filename, audio_bytes, mime_type = extract_audio_payload(selected_audio)
    except Exception as exc:
        st.error("Unable to read the selected audio file.")
        st.caption(str(exc))
        return

    if not audio_bytes:
        st.error("The selected audio is empty. Please try another file or record again.")
        return

    progress_card = st.container(border=True)

    with progress_card:
        st.subheader("Analyzing your voice...")
        st.markdown(
            """
            <div class="voice-stage-list">
                <div>1. 🎤 Transcribing audio</div>
                <div>2. 🧠 Understanding request</div>
                <div>3. 📝 Generating SQL</div>
                <div>4. 🗄️ Querying database</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    try:
        with st.spinner("Analyzing your voice..."):
            response = requests.post(
                VOICE_ANALYSIS_URL,
                files={
                    "audio": (filename, audio_bytes, mime_type),
                },
                timeout=180,
            )
    except requests.RequestException as exc:
        st.error("Unable to process the audio right now.")
        st.caption(str(exc))
        return

    try:
        payload = response.json()
    except ValueError:
        st.error("Unable to process the audio.")
        st.caption(f"Backend returned an invalid response ({response.status_code}).")
        return

    if response.status_code >= 400 or payload.get("status") == "error":
        backend_error = payload.get("error") or payload.get("detail") or "The voice pipeline returned an error."

        st.error("Unable to process the audio.")
        st.caption(backend_error)
        return

    st.success("Voice analysis completed.")

    st.markdown("### 🎤 What I heard")
    render_text_block("Transcription", payload.get("transcription"))

 

    st.markdown("### 📝 Generated SQL")
    sql_query = payload.get("sql_query")

    if sql_query:
        st.code(sql_query, language="sql")
    else:
        st.info("No SQL query was returned by the backend.")

    st.markdown("### 🗄️ Database Result")
    result_table = build_result_table(payload.get("result"))

    if result_table is None:
        st.info("No tabular result was returned by the backend.")
    else:
        st.markdown(result_table, unsafe_allow_html=True)

    if payload.get("detected_language"):
        st.caption(f"Detected language: {payload['detected_language']}")

    if payload.get("error"):
        st.warning(payload["error"])

    return

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

if "learning_required" not in st.session_state:
    st.session_state.learning_required = False

if "learning_problem" not in st.session_state:
    st.session_state.learning_problem = ""

if "learning_message" not in st.session_state:
    st.session_state.learning_message = ""

# ============================================================
# Sidebar
# ============================================================

with st.sidebar:

    st.title("🤖 AI Code Assistant")

    page_choice = st.radio(
        "Navigation",
        ["Code Assistant", "Voice SQL"],
        key="main_navigation",
    )

    st.divider()

    if page_choice == "Voice SQL":
        st.subheader("🎤 Voice SQL Assistant")
        st.caption("Record voice or upload audio, then analyze it against the database.")

        if st.button("Reset Voice Inputs", use_container_width=True):
            reset_voice_inputs()
            st.rerun()

    else:
        st.subheader("🧠 Recent Conversation")

if page_choice == "Voice SQL":
    render_voice_sql_page()
    st.stop()

if not st.session_state.memory:
    st.info("Start chatting to build conversation memory.")
else:
    for item in st.session_state.memory[-8:]:

        preview = item["content"].replace("\n", " ")

        if len(preview) > 55:
            preview = preview[:55] + "..."

        icon = "👤" if item["role"] == "user" else "🤖"

        with st.container(border=True):
            st.markdown(f"**{icon} {preview}**")

    st.divider()

    if st.button("🗑 Clear Chat", use_container_width=True):
        st.session_state.messages.clear()
        st.session_state.memory.clear()
        st.session_state.learning_required = False
        st.session_state.learning_problem = ""
        st.session_state.learning_message = ""
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
# Learning Mode Panel
# ============================================================

if st.session_state.learning_required:

    with st.chat_message("assistant"):

        st.warning(st.session_state.learning_message)

        with st.form("learning_upload_form", clear_on_submit=False):

            uploaded_file = st.file_uploader(
                "Upload the correct Python solution",
                type=["py"],
                accept_multiple_files=False,
            )

            submitted = st.form_submit_button("Learn")

            if submitted:

                if uploaded_file is None:
                    st.error("Please upload a .py file before learning.")
                else:
                    try:
                        response = requests.post(
                            LEARN_URL,
                            data={"problem": st.session_state.learning_problem},
                            files={
                                "file": (
                                    uploaded_file.name,
                                    uploaded_file.getvalue(),
                                    uploaded_file.type or "text/x-python",
                                )
                            },
                            timeout=120,
                        )
                        response.raise_for_status()

                        result = response.json()

                        st.success(result.get("message", "Knowledge stored successfully."))

                        st.session_state.learning_required = False
                        st.session_state.learning_problem = ""
                        st.session_state.learning_message = ""

                        st.rerun()

                    except Exception as e:
                        st.error(str(e))

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

    if result.get("needs_learning"):

        learning_message = result["message"]

        with st.chat_message("assistant"):
            st.warning(learning_message)

        # Set learning state and immediately rerun so the upload form
        # appears in the same interaction instead of after another message.
        st.session_state.learning_required = True
        st.session_state.learning_problem = prompt
        st.session_state.learning_message = learning_message
        st.rerun()

        st.session_state.messages.append(
            {
                "role": "assistant",
                "type": "text",
                "content": learning_message,
            }
        )

        st.session_state.memory.append(
            {
                "role": "assistant",
                "content": learning_message,
            }
        )

    elif "generation" not in result:

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