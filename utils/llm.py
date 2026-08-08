from dotenv import load_dotenv
import os

from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)

def ask_llm(prompt: str):

    response = llm.invoke(prompt)

    return response.content