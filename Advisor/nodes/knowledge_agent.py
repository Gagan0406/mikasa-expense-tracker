from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.messages import HumanMessage
from dotenv import load_dotenv
load_dotenv()
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.4
)

def knowledge_agent_node(state):
    query = state["user_query"]

    prompt = f"""
You are a financial knowledge assistant.

User Question:
{query}

Explain clearly and concisely.
Use simple language.
If applicable, include examples.

FORMAT:

-------------------------
CONCEPT EXPLANATION
- ...

KEY POINTS
- Don't use markdown symbols.


PRACTICAL EXAMPLE (if applicable)
- ...

-------------------------
"""

    response = llm.invoke([HumanMessage(content=prompt)])

    return {
        "final_output": response.content.strip()
    }
