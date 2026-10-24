import json
import os
import uuid
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv, set_key, unset_key
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

APP_NAME = "Vesper"

BASE_DIR = Path(__file__).parent
ENV_PATH = BASE_DIR / ".env"
HISTORY_PATH = BASE_DIR / "chats.json"

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🌙",
    layout="centered",
)

load_dotenv(ENV_PATH, override=True)

# ---------- NIGHT THEME ----------
STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif&family=DM+Sans:wght@400;500;600&display=swap');

:root {
    --paper: #090D1B;
    --paper-light: #10172A;
    --ink: #E9E8F7;
    --muted: #929CB9;
    --plum: #0C1021;
    --plum-soft: #1A2340;
    --accent: #8174F9;
    --line: #29334F;
    --input: #121A2E;
}

/* Main night sky */
.stApp {
    background:
        radial-gradient(
            circle at 82% 13%,
            rgba(215, 222, 255, 0.12) 0px,
            rgba(170, 185, 235, 0.06) 48px,
            transparent 115px
        ),
        radial-gradient(
            circle at 82% 13%,
            #D8DDF0 0px,
            #C2CBE4 1px,
            #8998BD 2px,
            rgba(99, 116, 162, 0.3) 42px,
            transparent 60px
        ),
        radial-gradient(
            ellipse at 75% 0%,
            #1B2542 0%,
            transparent 48%
        ),
        linear-gradient(160deg, #11162A 0%, #090D1B 58%, #101020 100%);
    color: var(--ink);
    font-family: 'DM Sans', sans-serif;
    isolation: isolate;
}

/* Rain overlay */
.stApp::after {
    content: "";
    position: fixed;
    inset: 0;
    z-index: -1;
    pointer-events: none;
    opacity: 0.23;
    background-image:
        repeating-linear-gradient(
            104deg,
            transparent 0px,
            transparent 37px,
            rgba(176, 198, 255, 0.38) 38px,
            transparent 39px,
            transparent 79px
        ),
        repeating-linear-gradient(
            104deg,
            transparent 0px,
            transparent 72px,
            rgba(176, 198, 255, 0.20) 73px,
            transparent 74px,
            transparent 145px
        );
    background-size: 100% 180px, 100% 260px;
    animation: rainfall 1.8s linear infinite;
}

@keyframes rainfall {
    from { background-position: 0 0, 0 0; }
    to   { background-position: -20px 180px, 18px 260px; }
}

[data-testid="stAppViewContainer"] {
    background: transparent;
}

[data-testid="stHeader"] {
    background: transparent;
}

#MainMenu, footer {
    visibility: hidden;
}

.block-container {
    max-width: 760px;
    padding-top: 3rem;
    padding-bottom: 6rem;
}

/* Typography */
.wordmark {
    font-family: 'Instrument Serif', serif;
    font-size: 2.6rem;
    color: #F0EDFF;
    margin: 0.2rem 0 1.2rem;
    letter-spacing: 0.5px;
    text-shadow: 0 0 22px rgba(153, 143, 255, 0.18);
}

.hero {
    margin-top: 12vh;
}

.hero h1 {
    font-family: 'Instrument Serif', serif;
    font-weight: 400;
    font-size: 2.9rem;
    line-height: 1.1;
    color: #F0EDFF;
    padding: 0;
}

.hero p {
    color: var(--muted);
    font-size: 1.05rem;
    max-width: 34rem;
    line-height: 1.7;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D1225, #090D1A);
    border-right: 1px solid rgba(151, 164, 210, 0.12);
}

[data-testid="stSidebar"] .wordmark {
    color: #F0EDFF;
    font-size: 2.1rem;
    margin: 0 0 0.8rem;
}

[data-testid="stSidebarContent"] {
    overflow-y: auto;
}

[data-testid="stSidebarUserContent"] {
    padding-top: 1rem;
    padding-bottom: 2rem;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
    color: #C6CBE0;
}

[data-testid="stSidebar"] .stButton > button {
    background: rgba(255, 255, 255, 0.025);
    color: #D5D9EF;
    border: 1px solid transparent;
    border-radius: 0.7rem;
    padding: 0.55rem 0.8rem;
    transition: background 0.2s, border-color 0.2s;
}

[data-testid="stSidebar"] .stButton > button p {
    color: inherit;
    text-align: left;
    width: 100%;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: #1A2340;
    border-color: #384363;
    color: white;
}

[data-testid="stSidebar"] button[kind="primary"],
[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] {
    background: #222746;
    color: white;
    border-color: #514C83;
}

/* New chat */
.st-key-new_chat button {
    background: linear-gradient(135deg, #8174F9, #6253CF) !important;
    color: white !important;
    justify-content: center !important;
    margin-bottom: 0.8rem;
    border: none !important;
    box-shadow: 0 4px 18px rgba(110, 95, 235, 0.18);
}

.st-key-new_chat button p {
    text-align: center !important;
    color: white !important;
}

/* Sidebar system prompt: fixed size, violet-tinted box */
[data-testid="stSidebar"] textarea {
    background: #1F1A3F !important;
    color: #EDE9FF !important;
    border: 1px solid #5B4FC4 !important;
    border-radius: 0.8rem !important;
    line-height: 1.65 !important;
    padding: 0.8rem !important;
    caret-color: #C4BBFF;
    resize: none !important;
    transition: border-color 0.2s;
}

[data-testid="stSidebar"] textarea:focus {
    border-color: #B3A8FF !important;
    box-shadow: 0 0 0 1px #B3A8FF !important;
}

/* Other input fields */
input, textarea {
    color: #E8E9FA !important;
}

[data-testid="stTextInput"] input {
    background: #121A2E !important;
    border: 1px solid #384363 !important;
    border-radius: 0.7rem !important;
}

[data-testid="stTextInput"] input:focus {
    border-color: #9285FF !important;
    box-shadow: 0 0 0 1px #9285FF !important;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: transparent;
    padding: 0.6rem 0;
    line-height: 1.75;
    color: var(--ink);
}

[data-testid="stChatMessageAvatarUser"],
[data-testid="stChatMessageAvatarAssistant"] {
    display: none;
}

[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    flex-direction: row-reverse;
    margin-left: auto;
    width: fit-content;
    max-width: 80%;
    background: linear-gradient(135deg, #7164E8, #5748BC);
    border: 1px solid rgba(185, 176, 255, 0.18);
    border-radius: 1.2rem 1.2rem 0.3rem 1.2rem;
    padding: 0.7rem 1.1rem;
    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.12);
}

[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) * {
    color: #FFFFFF !important;
}

/* Chat input bar */
[data-testid="stBottom"],
[data-testid="stBottom"] > div {
    background: #090D1B !important;
}

[data-testid="stChatInput"] {
    background: #121A2E !important;
    border: 1px solid #343F60 !important;
    border-radius: 1.2rem !important;
    box-shadow: 0 6px 28px rgba(0, 0, 0, 0.3);
}

[data-testid="stChatInput"] > div {
    background: #121A2E !important;
    border: none !important;
    border-radius: 1.2rem !important;
}

[data-testid="stChatInput"] textarea {
    color: #F0EDFF !important;
    caret-color: #A99DFF;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #7883A3 !important;
}

/* Custom lavender thinking spinner */
[data-testid="stSpinner"] {
    color: #B7ACFF !important;
}

[data-testid="stSpinner"] p {
    color: #C7C1F5 !important;
}

[data-testid="stSpinner"] svg {
    stroke: #A99DFF !important;
    color: #A99DFF !important;
}

[data-testid="stSpinner"] svg circle {
    stroke: #A99DFF !important;
}

/* Buttons */
.stButton > button,
.stFormSubmitButton > button {
    border-radius: 0.75rem;
    transition: all 0.2s;
}

.stButton > button[kind="primary"],
.stFormSubmitButton > button {
    background: linear-gradient(135deg, #8174F9, #6253CF);
    color: white;
    border: none;
}

.stButton > button[kind="primary"]:hover,
.stFormSubmitButton > button:hover {
    border: 1px solid #B0A5FF;
    box-shadow: 0 0 16px rgba(129, 116, 249, 0.2);
}

/* API key form */
[data-testid="stForm"] {
    background: rgba(17, 24, 44, 0.94);
    border: 1px solid #343F60;
    border-radius: 1rem;
    padding: 1.5rem;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.18);
}

/* Dividers */
hr {
    border-color: #28324D !important;
}

/* Scrollbars */
::-webkit-scrollbar {
    width: 7px;
}

::-webkit-scrollbar-track {
    background: #0B1020;
}

::-webkit-scrollbar-thumb {
    background: #384363;
    border-radius: 10px;
}
</style>
"""

st.markdown(STYLE, unsafe_allow_html=True)


# ---------- API KEY SCREEN ----------
if not os.getenv("OPENAI_API_KEY"):
    st.markdown(
        f"""
        <div class="hero">
            <div class="wordmark">{APP_NAME} 🌙</div>
            <h1>A little quiet in the noise.</h1>
            <p>
                A personal AI chat for your thoughts, questions,
                and everything in between. Enter your API key to begin.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("api_key_form"):
        key = st.text_input("OpenAI API key", type="password")
        submitted = st.form_submit_button(
            "Enter Vesper",
            use_container_width=True,
        )

    if submitted:
        if key.strip():
            ENV_PATH.touch(exist_ok=True)
            set_key(str(ENV_PATH), "OPENAI_API_KEY", key.strip())
            os.environ["OPENAI_API_KEY"] = key.strip()
            st.rerun()
        else:
            st.warning("Please enter your API key.")

    st.stop()


# ---------- CHAT STORAGE ----------
def load_chats():
    if HISTORY_PATH.exists():
        try:
            return json.loads(
                HISTORY_PATH.read_text(encoding="utf-8")
            )
        except (json.JSONDecodeError, OSError):
            st.error("Could not read chats.json. Check the file.")
    return {}


def save_chats(chats):
    HISTORY_PATH.write_text(
        json.dumps(chats, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


if "chats" not in st.session_state:
    st.session_state.chats = load_chats()

if "current" not in st.session_state:
    st.session_state.current = str(uuid.uuid4())

if "system_role" not in st.session_state:
    st.session_state.system_role = "You are a helpful assistant"

chats = st.session_state.chats
current = st.session_state.current


# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown(
        f'<div class="wordmark">{APP_NAME} 🌙</div>',
        unsafe_allow_html=True,
    )

    if st.button(
        "＋  New chat",
        key="new_chat",
        use_container_width=True,
    ):
        st.session_state.current = str(uuid.uuid4())
        st.rerun()

    st.caption("YOUR CONVERSATIONS")

    with st.container(height=170, border=False):
        for chat_id, chat_data in reversed(list(chats.items())):
            is_open = chat_id == current

            if st.button(
                chat_data.get("title", "New conversation"),
                key=f"chat_{chat_id}",
                use_container_width=True,
                type="primary" if is_open else "secondary",
            ):
                st.session_state.current = chat_id
                st.rerun()

    st.divider()

    st.caption("PERSONALIZE VESPER")

    # Fixed-size box: long prompts scroll inside it instead of resizing it.
    system_message = st.text_area(
        "System prompt",
        key="system_role",
        height=120,
        help="Describe how Vesper should behave.",
        placeholder="You are a helpful assistant...",
    )

    st.caption("Changes apply to your next message.")

    if current in chats:
        if st.button(
            "Delete this chat",
            use_container_width=True,
        ):
            del chats[current]
            save_chats(chats)
            st.session_state.current = str(uuid.uuid4())
            st.rerun()

    st.divider()

    # Log out: remove the saved key and return to the API key screen.
    if st.button(
        "↪  Log out",
        key="logout",
        use_container_width=True,
    ):
        if ENV_PATH.exists():
            unset_key(str(ENV_PATH), "OPENAI_API_KEY")

        os.environ.pop("OPENAI_API_KEY", None)

        # Clear session state so the next login starts fresh.
        for key_name in (
            "system_role",
            "chats",
            "current",
        ):
            st.session_state.pop(key_name, None)

        st.rerun()


# ---------- MAIN CHAT ----------
history = chats.get(current, {}).get("messages", [])

if not history:
    st.markdown(
        f"""
        <div class="hero">
            <div class="wordmark">{APP_NAME}</div>
            <h1>What are we working on?</h1>
            <p>
                A quiet corner of the internet, just for you.
                Ask anything, explore an idea, or simply think out loud.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

for msg in history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ---------- MODEL ----------
llm = ChatOpenAI(
    model="gpt-5.2",
    temperature=0.5,
)


# ---------- SEND MESSAGE ----------
if prompt := st.chat_input("Send a message into the night..."):

    if current not in chats:
        chats[current] = {
            "title": prompt[:30],
            "messages": [],
        }

    history = chats[current]["messages"]
    history.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    lc_messages = [
        SystemMessage(content=system_message),
    ]

    for msg in history:
        if msg["role"] == "user":
            lc_messages.append(
                HumanMessage(content=msg["content"])
            )
        else:
            lc_messages.append(
                AIMessage(content=msg["content"])
            )

    with st.chat_message("assistant"):
        try:
            with st.spinner("Vesper is thinking..."):
                response = llm.invoke(lc_messages)
                reply = response.content

            st.markdown(reply)

        except Exception as e:
            history.pop()
            st.error(f"Request failed: {e}")

        else:
            history.append({
                "role": "assistant",
                "content": reply,
            })
            save_chats(chats)
            st.rerun()