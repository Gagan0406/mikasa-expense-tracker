from pydantic import BaseModel, Field
from typing import Literal

class OutputSchema(BaseModel):
    category: Literal["action taken","needs advice","other topic"] = Field(description="the category of user message , it can be one of the three categories action taken , needs advice , other topic")
    

class OperationType(BaseModel):
    operation: Literal["insert","update","delete","retrieve"] = Field(discription="opeation can be one of the four operations - insert upate delete retrieve")
    
class TransactionSchema(BaseModel):
    transaction_type: Literal["credit", "debit"] = Field(description="Type of transaction: 'credit' if money received, 'debit' if money spent")
    amount: float = Field(description="Amount of money in the transaction")
    description: str = Field(description="Description of the transaction (spent on / received from)")
    
class querySchema(BaseModel):
    query: str = Field(description="the sql query to be executed")
    
class queryEvaluatorSchema(BaseModel):
    query_feedback: str = Field(description="Feedback of the query , covers about syntax correct logic according to the user message")
    query_approved: Literal["yes", "no"] = Field(description="Whether the query was approved or not,no if feedback is negative else yes")

class amountIndirectSchema(BaseModel):
    amount: Literal["yes","no"] = Field(description="whether the amount is mentioned directly or indirectly in the user message,if indirectly then yes else no")