from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.messages import HumanMessage
from dotenv import load_dotenv
load_dotenv()
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3
)

def query_rewrite_node(state):
    user_query = state["user_query"]

    prompt = f"""
Rewrite the following user query into 5 semantically diverse search queries.
Preserve the original intent.Try to extract exact needs from the user query.

User Query:
"{user_query}"

Return one query per line.
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    queries = response.content.strip().split("\n")

    return {
        "rewritten_queries": [q.strip("- ").strip() for q in queries if q.strip()]
    }
