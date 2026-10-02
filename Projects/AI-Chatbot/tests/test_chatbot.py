"""Tests for the chatbot's message handling, memory, errors, and save/load.

These run without any API key or internet: a fake provider stands in for the
AI, so the tests check OUR code, not Google's servers.
"""
import json
import os
import pathlib
import sys

# Force the offline backend before app.py is imported, so no key is needed.
os.environ["PROVIDER"] = "ollama"
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import pytest  # noqa: E402

import app  # noqa: E402
from providers import _to_text  # noqa: E402


class FakeProvider:
    """Replies with how many turns it received, so memory can be checked."""

    def stream(self, model, system_prompt, history):
        yield f"got {len(history)} turns"


class BrokenProvider:
    def __init__(self, message):
        self.message = message

    def stream(self, model, system_prompt, history):
        raise Exception(self.message)


def run_respond(history, provider, model="gemini-2.5-flash"):
    app.provider = provider
    final = history
    for state in app.respond(history, "Be helpful.", model):
        final = state
    return final


# ---- _to_text: the Gradio 6 format fix --------------------------------

def test_to_text_plain_string():
    assert _to_text("hello") == "hello"


def test_to_text_gradio6_list_format():
    assert _to_text([{"text": "hello", "type": "text"}]) == "hello"


def test_to_text_joins_multiple_chunks():
    chunks = [{"text": "hel", "type": "text"}, {"text": "lo", "type": "text"}]
    assert _to_text(chunks) == "hello"


@pytest.mark.parametrize("empty", ["", [], None])
def test_to_text_empty_values(empty):
    assert _to_text(empty) == ""


# ---- adding messages ---------------------------------------------------

def test_add_user_message_appends_and_clears_box():
    box, history = app.add_user_message("hello", [])
    assert box == ""
    assert history == [{"role": "user", "content": "hello"}]


def test_blank_message_is_ignored():
    start = [{"role": "user", "content": "hi"}]
    _, history = app.add_user_message("   ", start)
    assert history == start


# ---- bots --------------------------------------------------------------

def test_there_are_three_bots():
    assert len(app.BOTS) == 3


def test_switch_bot_loads_persona_and_clears_chat():
    prompt, history = app.switch_bot("Coding Buddy")
    assert "programming tutor" in prompt
    assert history == []


def test_switch_bot_unknown_name_falls_back_to_default():
    prompt, history = app.switch_bot("Not A Real Bot")
    assert prompt == app.BOTS[app.DEFAULT_BOT]
    assert history == []


# ---- streaming and memory ---------------------------------------------

def test_reply_is_added_as_assistant_turn():
    _, history = app.add_user_message("hi", [])
    final = run_respond(history, FakeProvider())
    assert final[-1]["role"] == "assistant"
    assert final[-1]["content"] == "got 1 turns"


def test_memory_carries_across_turns():
    _, history = app.add_user_message("turn one", [])
    history = run_respond(history, FakeProvider())
    _, history = app.add_user_message("turn two", history)
    history = run_respond(history, FakeProvider())
    # user, assistant, user were sent to the model on the second call
    assert history[-1]["content"] == "got 3 turns"


# ---- friendly errors ---------------------------------------------------

@pytest.mark.parametrize(
    "raw_error, expected_hint",
    [
        ("401 unauthorized", "API key looks wrong"),
        ("429 RESOURCE_EXHAUSTED", "free tier limit"),
        ("404 model not found", "not found"),
        ("something strange", "Something went wrong"),
    ],
)
def test_errors_become_plain_english(raw_error, expected_hint):
    _, history = app.add_user_message("hi", [])
    final = run_respond(history, BrokenProvider(raw_error))
    assert expected_hint in final[-1]["content"]


# ---- save and load -----------------------------------------------------

@pytest.fixture
def save_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(app, "SAVE_DIR", str(tmp_path))
    return tmp_path


def test_save_then_load_round_trip(save_dir):
    convo = [
        {"role": "user", "content": "my name is Melvin"},
        {"role": "assistant", "content": "Hi Melvin!"},
    ]
    status, _ = app.save_chat(convo, "Helpful Assistant", "gemini-2.5-flash", "Be helpful.")
    assert status.startswith("Saved")
    filename = app.list_saves()[0]
    history, bot, model, prompt, _ = app.load_chat(filename)
    assert history == convo
    assert bot == "Helpful Assistant"
    assert model == "gemini-2.5-flash"
    assert prompt == "Be helpful."


def test_save_flattens_gradio6_list_content(save_dir):
    convo = [{"role": "assistant", "content": [{"text": "Hi!", "type": "text"}]}]
    app.save_chat(convo, "Coding Buddy", "gemini-2.5-flash", "x")
    saved = json.loads((save_dir / app.list_saves()[0]).read_text(encoding="utf-8"))
    assert saved["history"][0]["content"] == "Hi!"


def test_saving_an_empty_chat_is_refused(save_dir):
    status, _ = app.save_chat([], "Helpful Assistant", "m", "p")
    assert "Nothing to save" in status
    assert app.list_saves() == []
