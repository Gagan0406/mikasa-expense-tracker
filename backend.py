import sys
import os
# Add the current directory to sys.path to ensure Advisor can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import load_prompt
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.sqlite import SqliteSaver
from typing import TypedDict, Annotated, Literal
from pydantic_models import OutputSchema, OperationType, TransactionSchema, querySchema, queryEvaluatorSchema
import sqlite3
from dotenv import load_dotenv

# Import the advisor graph builder
from Advisor.graph import build_graph as build_advisor_graph

from tools import mytools

load_dotenv()

# Initialize the advisor graph
advisor_graph = build_advisor_graph()

category_of_message_prompt = load_prompt("category_of_message_prompt.json")
crud_operation_prompt = load_prompt("crud_operation_prompt.json")
transaction_info_extraction_prompt = load_prompt("transaction_info_extraction_prompt.json")
insert_query_prompt = load_prompt("insert_query_prompt.json")
update_query_prompt = load_prompt("update_query_prompt.json")
retrieve_query_prompt = load_prompt("retrieve_query_prompt.json")
delete_query_prompt = load_prompt("delete_query_prompt.json")
query_evaluator_prompt = load_prompt("query_evaluator_prompt.json")
query_optimizer_prompt = load_prompt("query_optimizer_prompt.json")

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
llm_director = llm.with_structured_output(OutputSchema)
llm_operation = llm.with_structured_output(OperationType)
llm_transaction = llm.with_structured_output(TransactionSchema)
llm_query = llm.with_structured_output(querySchema)
llm_query_evaluator = llm.with_structured_output(queryEvaluatorSchema)
llm_with_tools = llm.bind_tools(mytools)

class ActionState(TypedDict):
    operation:Literal["insert","update","delete","retrieve"]
    transaction_type: Literal["credit", "debit"]
    amount: float
    description: str
    query: str
    query_feedback: str
    query_approved: Literal["yes","no"]
        
class chatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    category : Literal["action taken","needs advice","other topic"]
    action: ActionState

def chat_llm(state: chatState):
    messages = state['messages']
    category = llm_director.invoke(category_of_message_prompt.invoke({'input':messages[-1].content})).category
    return {'category':category}

def agent_router(state: chatState)->Literal["advisor","action","chatbot"]:
    if state['category'] == "needs advice":
        return "advisor"
    elif state['category'] == "action taken":
        return "action"
    else:
        return "chatbot"
    
def advisor_func(state: chatState):
    messages = state['messages']
    user_query = messages[-1].content

    try:
        advisor_result = advisor_graph.invoke({
            "user_query": user_query
        })

        final_response = advisor_result.get(
            "final_output",
            "I apologize, but I couldn't generate a complete advisory response. Could you please rephrase your question?"
        )
        
        # Ensure we have a meaningful response
        if not final_response or final_response.strip() == "":
            final_response = "I'm having trouble processing your advisory request. Please try asking in a different way."

        return {
            "messages": [AIMessage(content=final_response)]
        }
    except Exception as e:
        print(f"Advisor error: {str(e)}")
        return {
            "messages": [AIMessage(content="I encountered an issue while processing your advisory request. Please try again or rephrase your question.")]
        }

def action_taker_func(state: chatState):
    messages = state['messages']
    operation = llm_operation.invoke(crud_operation_prompt.invoke({'user_msg':messages[-1].content})).operation
    return {'action':{'operation':operation}}

def normal_chat_func(state: chatState):
    messages = state['messages']
    response = llm_with_tools.invoke(messages)
    return {'messages':[response]}

tool_node = ToolNode(mytools)
    
def action_router(state:chatState)->Literal['insert','update','delete','retrieve']:
    op = state['action']['operation']
    if op == 'insert':
        return 'insert'
    elif op == 'update':
        return 'update'
    elif op == 'delete':
        return 'delete'
    else:
        return 'retrieve'
    

    
    
def inserter(state:chatState):
    messages = state['messages']
    transaction_info = llm_transaction.invoke(transaction_info_extraction_prompt.invoke({'user_message':messages}))
    query = llm_query.invoke(insert_query_prompt.invoke({'transaction_type':transaction_info.transaction_type,'amount':transaction_info.amount,'description':transaction_info.description})).query
    return {'action':{'transaction_type':transaction_info.transaction_type,'amount':transaction_info.amount,'description':transaction_info.description,'query':query,'operation':'insert'}}

def updater(state:chatState):
    messages = state['messages']
    query = llm_query.invoke(update_query_prompt.invoke({'user_message':messages})).query
    return {'action':{'query':query,'operation':'update'}}


def deleter(state:chatState):
    messages = state['messages']
    query = llm_query.invoke(delete_query_prompt.invoke({'user_message':messages[-1].content})).query
    return {'action':{'query':query,'operation':'delete'}}

def retriever(state:chatState):
    messages = state['messages']
    query = llm_query.invoke(retrieve_query_prompt.invoke({'user_message':messages[-1].content})).query
    return {'action':{'query':query,'operation':'retrieve'}}

def query_evaluator(state:chatState):
    messages = state['messages']
    action = state['action']
    query_elavuation = llm_query_evaluator.invoke(query_evaluator_prompt.invoke({'user_message':messages,'query':action['query']}))
    return {'action':{'query_feedback':query_elavuation.query_feedback,'query_approved':query_elavuation.query_approved,'operation':action['operation'],'query':action['query']}}
    
def query_evaluator_router(state:chatState)->Literal['query optimizer','query executor']:
    if state['action']['query_approved'] == 'yes':
        return 'query executor'
    else:
        return 'query optimizer'
    
def query_optimizer(state:chatState):
    messages = state['messages']
    action = state['action']
    optimized_query = llm_query.invoke(query_optimizer_prompt.invoke({'user_message':messages,'query':action['query'],'query_feedback':action['query_feedback']})).query
    return {'action':{'query':optimized_query,'operation':action['operation']}}

def query_executor(state:chatState):
    action = state['action']
    query = action['query']
    operation = action['operation']
    query_executor_prompt = f"""You are an expert database assistant. You have been given a SQL query to execute on the database.
    Execute the query using the query_executer_tool and return the result. it requires to know the operation type as well.
    Here is the query: {query}
    Here is the operation type: {operation}"""
    response = llm_with_tools.invoke(query_executor_prompt)
    return {'messages':[response]}




graph = StateGraph(chatState)

graph.add_node('director',chat_llm)
graph.add_node('action',action_taker_func)
graph.add_node('advisor',advisor_func)
graph.add_node('chatbot',normal_chat_func)
graph.add_node('tools',tool_node)
graph.add_node('insert',inserter)
graph.add_node('update',updater)
graph.add_node('delete',deleter)
graph.add_node('retrieve',retriever)
graph.add_node('query evaluator',query_evaluator)
graph.add_node('query optimizer',query_optimizer)
graph.add_node('query executor',query_executor)

graph.add_edge('advisor', END)
graph.add_edge(START,'director')
graph.add_conditional_edges('director',agent_router)
graph.add_conditional_edges('action',action_router)
graph.add_edge('insert','query evaluator')
graph.add_edge('update','query evaluator')
graph.add_edge('delete','query evaluator')
graph.add_edge('retrieve','query evaluator')
graph.add_conditional_edges('query evaluator',query_evaluator_router)
graph.add_edge('query optimizer','query evaluator')
graph.add_conditional_edges('query executor',tools_condition)
graph.add_conditional_edges('chatbot',tools_condition)
graph.add_edge('tools','chatbot')


conn = sqlite3.connect('chatbot.db',check_same_thread=False)
checkpoint = SqliteSaver(conn = conn)

chatbot = graph.compile(checkpointer=checkpoint)



