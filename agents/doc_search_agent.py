# doc_search_agent.py

import os
import streamlit as st
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI  # Import Google's model
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from dotenv import load_dotenv
load_dotenv()

# Main QA prompt (no changes needed here)
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

    # --- LLM Definitions with Fallback ---

    # 1. Primary LLM (OpenRouter)
    primary_llm = ChatOpenAI(
        model="openai/gpt-3.5-turbo", # Example model
        openai_api_base="https://openrouter.ai/api/v1",
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0.25
    )

    # 2. Fallback LLM (Google Gemini)
    fallback_llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.25,
        convert_system_message_to_human=True # Helps with compatibility
    )
    
    # --- Main QA Chain ---
    try:
        print("Attempting to use primary LLM (OpenRouter)...")
        qa_chain = RetrievalQA.from_chain_type(
            llm=primary_llm,
            retriever=retriever,
            return_source_documents=True
        )
        result = qa_chain.invoke(query)

    except Exception as e:
        # If a rate limit error occurs, fall back to Gemini
        if "429" in str(e):
            print("Primary LLM failed (429). Switching to fallback LLM (Gemini)...")
            st.warning("OpenRouter daily limit reached. Switching to Google Gemini for this request.", icon="⚠️")
            
            qa_chain = RetrievalQA.from_chain_type(
                llm=fallback_llm,
                retriever=retriever,
                return_source_documents=True,
                # Pass the custom prompt to the chain
                chain_type_kwargs={"prompt": custom_prompt}
            )
            result = qa_chain.invoke(query)
        else:
            # For any other error, re-raise it
            raise e

    answer = result["result"]
    sources = result["source_documents"]

    # --- Related Questions Generation ---
    related_prompt = f"""
Based on the user's question and your answer, suggest 3 short follow-up questions
that the user might ask next. Each question should be concise and directly related.

User question: {query}
Your answer: {answer}

Return the questions as a numbered list.
"""
    
    try:
        print("Attempting to generate related questions with primary LLM...")
        # Use the primary LLM for related questions as well
        related_raw = primary_llm.invoke(related_prompt).content
    except Exception as e:
         if "429" in str(e):
            print("Primary LLM failed for related questions (429). Using fallback...")
            # If it fails, use the fallback LLM
            related_raw = fallback_llm.invoke(related_prompt).content
         else:
             raise e

    related_list = [line.strip("1234567890. ") for line in related_raw.split("\n") if line.strip()]

    return {
        "answer": answer,
        "sources": sources,
        "related": related_list[:3]
    }