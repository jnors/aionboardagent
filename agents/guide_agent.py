from agents.doc_search_agent import search_documents
from agents.scheduler_agent import try_schedule_event

def ask_onboarding_agent(query: str) -> str:
    if "schedule" in query.lower():
        return try_schedule_event(query)
    else:
        return search_documents(query)
