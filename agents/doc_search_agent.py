from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os

from dotenv import load_dotenv
load_dotenv()

# Main QA prompt
custom_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are FrameTech's AI Onboarding Assistant — a friendly, mentor-like guide helping new hires feel welcome and confident. 
Answer **only** using the information in the provided context. 
Do not guess or invent information — if it’s not in the context, say:
"Sorry, I couldn't find that in the onboarding documents."

When answering:
- Use a warm, supportive tone (friendly, encouraging, but still professional).
- Keep answers **clear and concise**, but include enough detail for the person to act on it.
- Use **bullet points** or **numbered lists** for steps, checklists, or multiple items.
- Bold important terms, dates, tools, or names to make them easy to spot.
- If the context suggests a next step, mention it (e.g., “You can find more details in…”).
- End with an invitation for follow-up if it feels natural (“Let me know if you’d like me to walk you through this.”).

Context:
{context}

Question:
{question}

Answer:
"""
)

def search_documents(query: str):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    index = FAISS.load_local("data/embeddings", embeddings, allow_dangerous_deserialization=True)
    retriever = index.as_retriever(search_kwargs={"k": 3})

    # Main LLM for answering
    llm = ChatOpenAI(
        model="openai/gpt-oss-20b:free",
        openai_api_base="https://openrouter.ai/api/v1",
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0.25
    )

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )

    result = qa.invoke(query)
    answer = result["result"]
    sources = result["source_documents"]

    # Generate related questions
    small_llm = ChatOpenAI(
        model="mistralai/mistral-7b-instruct:free",
        openai_api_base="https://openrouter.ai/api/v1",
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0.5
    )

    related_prompt = f"""
Based on the user's question and your answer, suggest 3 short follow-up questions
that the user might ask next. Each question should be concise and directly related.

User question: {query}
Your answer: {answer}

Return the questions as a numbered list.
"""
    related_raw = small_llm.invoke(related_prompt).content
    related_list = [line.strip("1234567890. ") for line in related_raw.split("\n") if line.strip()]

    return {
        "answer": answer,
        "sources": sources,
        "related": related_list[:3]  # limit to 3
    }
