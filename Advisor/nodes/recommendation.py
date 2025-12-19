from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.messages import HumanMessage

from dotenv import load_dotenv
load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.4
)

def recommendation_node(state):
    user_query = state["user_query"]
    context = state["rag_context"]

    prompt = f"""
You are an expert financial policy advisor.

User Query:
{user_query}

Retrieved Context:
{context}

Produce a structured recommendation.

FORMAT STRICTLY AS:

-------------------------
USER NEED ANALYSIS
- ...

RECOMMENDED POLICIES
1. Policy Name
   - Category:
   - Why it fits:
   - Estimated affordability:

2. Policy Name
   - Category:
   - Why it fits:
   - Estimated affordability:

FINAL SUGGESTION
- ...
-------------------------

Rules:
- Don't use unncessary markdown symbols 
- Do NOT output JSON
- Do NOT hallucinate policies
- If User need to know about a particular policy then don't give new policy just explain what user wants to know.
"""

    response = llm.invoke([HumanMessage(content=prompt)])

    return {
        "final_output": response.content.strip()
    }
