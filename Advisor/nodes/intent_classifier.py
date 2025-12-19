from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.messages import HumanMessage
from dotenv import load_dotenv
load_dotenv()
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.0
)

def intent_classifier_node(state):
    query = state["user_query"]

    prompt = f"""
Classify the user's intent into ONE of the following categories:

1. policy_recommendation
   - Choosing insurance, health policies, government schemes
   - Comparing policies
   - Finding affordable coverage

2. financial_knowledge
   - Mutual funds
   - SIP, NAV, ELSS, index funds
   - Explaining financial or policy-related terms

User Query:
"{query}"

Respond with ONLY ONE WORD:
policy_recommendation OR financial_knowledge
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    intent = response.content.strip().lower()

    if intent not in ["policy_recommendation", "financial_knowledge"]:
        intent = "policy_recommendation"  # safe fallback

    return {"intent": intent}
