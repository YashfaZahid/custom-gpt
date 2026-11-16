# Vesper

Vesper is a personal chat workspace with a night-sky UI. You enter an OpenAI key, then talk. Threads are saved in `chats.json`.

## What it does

- API key gate before the chat
- A single default model set in code (`ChatOpenAI` in `app.py`)
- Multi-turn history kept in the session and written to `chats.json`
- A dark theme (Instrument Serif and DM Sans) with no extra frontend build

The key gate writes the key into a local `.env` via `python-dotenv`. That file must stay untracked. Do not commit it, and do not commit a `chats.json` you would not want public.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

If `.env` already contains `OPENAI_API_KEY`, the gate is skipped.

## Layout

```text
app.py            UI and the chat call
requirements.txt  openai, langchain, streamlit
chats.json        Saved threads
```

## Limits

There is no retrieval and no tool use. Change the model string in `app.py` if the default name is not available on your account. For a sidebar where the role, model, and temperature are editable, see Origin in `RAG-Chatbot`.
