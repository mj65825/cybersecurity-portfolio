"""
Free AI Chatbot
- 3 bots with different personalities
- Model picker
- Save and load conversations
- Editable system prompt
- Conversation memory
- Clear button
- Streaming replies

Run:  python app.py
Then open the link it prints in your browser.
"""
import os
import json
import re
import datetime as dt

import gradio as gr
from dotenv import load_dotenv
from providers import get_provider

load_dotenv()

PROVIDER_NAME = os.getenv("PROVIDER", "gemini").lower()

# Start the provider — show a clear message if the key is missing
try:
    provider = get_provider(PROVIDER_NAME)
    STARTUP_ERROR = None
except Exception as e:
    provider = None
    STARTUP_ERROR = str(e)

SAVE_DIR = "conversations"
os.makedirs(SAVE_DIR, exist_ok=True)

# ---------------------------------------------------------------
# YOUR 3 BOTS
# To add more: just add another line below in the same format.
# To change a personality: edit the text after the colon.
# ---------------------------------------------------------------
BOTS = {
    "Helpful Assistant": "You are a helpful, concise assistant. Answer clearly and stay friendly.",
    "Coding Buddy":      "You are an expert programming tutor. Give short correct code examples and explain them simply. Prefer Python unless asked otherwise.",
    "Sarcastic Pirate":  "You are a witty pirate. Always answer correctly but in pirate dialect with playful sarcasm. Say Arrr a lot.",
}
DEFAULT_BOT = list(BOTS.keys())[0]

if PROVIDER_NAME == "gemini":
    MODEL_CHOICES = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.5-pro"]
else:
    MODEL_CHOICES = ["llama3.1", "qwen2.5", "mistral", "gemma2"]
DEFAULT_MODEL = MODEL_CHOICES[0]


# ---------------------------------------------------------------
# Chat functions
# ---------------------------------------------------------------

def add_user_message(message, history):
    """Add the user's message to history and clear the input box."""
    if not message or not message.strip():
        return "", history
    return "", history + [{"role": "user", "content": message}]


def respond(history, system_prompt, model):
    """Stream the reply. Sends full history every call — that is memory."""

    # Show startup error inside the chat instead of crashing
    if STARTUP_ERROR:
        yield history + [{"role": "assistant", "content":
            f"Setup error: {STARTUP_ERROR}\n\n"
            "Fix: open your .env file and make sure GEMINI_API_KEY is set correctly."}]
        return

    history = history + [{"role": "assistant", "content": ""}]
    try:
        for chunk in provider.stream(model, system_prompt, history[:-1]):
            history[-1]["content"] += chunk
            yield history
    except Exception as e:
        err = str(e)
        # Give a plain English hint for the most common errors
        if "API_KEY" in err.upper() or "401" in err or "403" in err:
            hint = "Your API key looks wrong. Check your .env file."
        elif "quota" in err.lower() or "429" in err:
            hint = "You hit the free tier limit. Wait a few minutes and try again."
        elif "not found" in err.lower() or "404" in err:
            hint = f"Model '{model}' not found. Switch to gemini-2.5-flash in the Model dropdown."
        else:
            hint = "Something went wrong — see detail below."
        history[-1]["content"] = f"{hint}\n\nDetail: {err}"
        yield history


def switch_bot(bot_name):
    """Load the selected bot's personality and clear the chat."""
    return BOTS.get(bot_name, BOTS[DEFAULT_BOT]), []


# ---------------------------------------------------------------
# Save / Load
# ---------------------------------------------------------------

def list_saves():
    files = [f for f in os.listdir(SAVE_DIR) if f.endswith(".json")]
    return sorted(files, reverse=True)


def save_chat(history, bot_name, model, system_prompt):
    if not history:
        return "Nothing to save — have a chat first.", gr.update()
    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    safe = re.sub(r"[^A-Za-z0-9]+", "-", bot_name).strip("-").lower()
    filename = f"{safe}_{timestamp}.json"

    # Normalize content to plain strings before saving
    clean = []
    for m in history:
        c = m["content"]
        if isinstance(c, list):
            c = "".join(p.get("text","") if isinstance(p,dict) else str(p) for p in c)
        clean.append({"role": m["role"], "content": c})

    data = {"bot": bot_name, "model": model,
            "system_prompt": system_prompt, "history": clean}
    with open(os.path.join(SAVE_DIR, filename), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return f"Saved: {filename}", gr.update(choices=list_saves(), value=filename)


def load_chat(filename):
    if not filename:
        return [], DEFAULT_BOT, DEFAULT_MODEL, BOTS[DEFAULT_BOT], "Pick a file to load."
    with open(os.path.join(SAVE_DIR, filename), encoding="utf-8") as f:
        data = json.load(f)
    bot   = data.get("bot", DEFAULT_BOT)
    bot   = bot if bot in BOTS else DEFAULT_BOT
    model = data.get("model", DEFAULT_MODEL)
    sysp  = data.get("system_prompt", BOTS[bot])
    hist  = data.get("history", [])
    return hist, bot, model, sysp, f"Loaded: {filename}"


# ---------------------------------------------------------------
# UI
# ---------------------------------------------------------------

CSS = """
.gradio-container { max-width: 900px !important; margin: auto; }
#chatbox { height: 460px; }
footer { display: none !important; }
"""

with gr.Blocks(title="My Chatbot") as demo:

    gr.Markdown(
        "## My Chatbot\n"
        f"Engine: **{PROVIDER_NAME}** &nbsp;|&nbsp; "
        "Pick a bot, pick a model, start chatting."
    )

    if STARTUP_ERROR:
        gr.Markdown(
            f"> ⚠️ **Setup issue:** {STARTUP_ERROR}\n\n"
            "> Open your `.env` file and make sure `GEMINI_API_KEY=your_key_here` is set."
        )

    with gr.Row():
        bot_picker = gr.Dropdown(
            choices=list(BOTS.keys()),
            value=DEFAULT_BOT,
            label="Bot",
            scale=1,
        )
        model_picker = gr.Dropdown(
            choices=MODEL_CHOICES,
            value=DEFAULT_MODEL,
            label="Model",
            allow_custom_value=True,
            scale=1,
        )

    with gr.Accordion("Edit bot personality", open=False):
        system_prompt_box = gr.Textbox(
            value=BOTS[DEFAULT_BOT],
            label="System prompt",
            lines=3,
            info="Change the personality here. Takes effect on your next message.",
        )

    chatbot = gr.Chatbot(elem_id="chatbox", show_label=False)

    with gr.Row():
        msg_box  = gr.Textbox(
            placeholder="Type a message and press Enter...",
            show_label=False, scale=8, autofocus=True,
        )
        send_btn  = gr.Button("Send",  variant="primary", scale=1, min_width=80)
        clear_btn = gr.Button("Clear", scale=1, min_width=80)

    with gr.Row():
        save_btn = gr.Button("Save conversation", scale=1)
        load_dd  = gr.Dropdown(choices=list_saves(),
                               label="Saved conversations", scale=2)
        load_btn = gr.Button("Load", scale=1)

    status_box = gr.Markdown("")

    # Send on Enter key
    msg_box.submit(
        add_user_message, [msg_box, chatbot], [msg_box, chatbot]
    ).then(respond, [chatbot, system_prompt_box, model_picker], chatbot)

    # Send button click
    send_btn.click(
        add_user_message, [msg_box, chatbot], [msg_box, chatbot]
    ).then(respond, [chatbot, system_prompt_box, model_picker], chatbot)

    # Clear
    clear_btn.click(lambda: ([], ""), None, [chatbot, msg_box], queue=False)

    # Switch bot
    bot_picker.change(switch_bot, [bot_picker], [system_prompt_box, chatbot])

    # Save / Load
    save_btn.click(
        save_chat,
        [chatbot, bot_picker, model_picker, system_prompt_box],
        [status_box, load_dd],
    )
    load_btn.click(
        load_chat, [load_dd],
        [chatbot, bot_picker, model_picker, system_prompt_box, status_box],
    )

if __name__ == "__main__":
    demo.launch(
        theme=gr.themes.Soft(primary_hue="indigo", neutral_hue="slate"),
        css=CSS,
    )
