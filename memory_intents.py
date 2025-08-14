# memory_intents.py
from datetime import datetime
from typing import Optional
from memory_store import MemoryStore
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

SUMMARY_PROMPT = ChatPromptTemplate.from_template("""
You are a concise note-taker. Summarize the conversation notes below as bullet points with actionable clarity.
- Keep names, decisions, blockers, and next steps.
- Max 10 bullets.

Conversation:
{conversation}
""")

WHAT_DID_WE_COVER_PROMPT = ChatPromptTemplate.from_template("""
Create a brief recap of what has been covered so far in this session.
Include: topics, decisions, and any open questions.

Conversation:
{conversation}
""")

def summarize_text(chunks: list[str]) -> str:
    # Fall back to trivial join if very small
    text = "\n".join(chunks)
    return llm.invoke(SUMMARY_PROMPT.format_messages(conversation=text)).content

def recap_text(chunks: list[str]) -> str:
    text = "\n".join(chunks)
    return llm.invoke(WHAT_DID_WE_COVER_PROMPT.format_messages(conversation=text)).content

class MemoryIntents:
    def __init__(self, store: MemoryStore):
        self.store = store

    def handle_recap(self, session_id: str, user_id: str) -> str:
        msgs = self.store.get_messages(session_id=session_id)
        convo = [f"{m['role']}: {m['content']}" for m in msgs]
        if not convo: return "We haven’t covered anything yet."
        return recap_text(convo)

    def handle_remind_what_person_said_yesterday(
        self, session_id: str, user_id: str, person_name: Optional[str]="João"
    ) -> str:
        start, end = self.store.yesterday_window()
        msgs = self.store.get_messages(session_id=session_id, since=start, until=end, role="user")
        if person_name:
            # naive filter – improve with regex or entity extraction if needed
            msgs = [m for m in msgs if person_name.lower() in m["content"].lower()]
        convo = [f"user: {m['content']}" for m in msgs]
        if not convo:
            return f"I don’t have anything from {person_name} yesterday."
        return summarize_text(convo)
