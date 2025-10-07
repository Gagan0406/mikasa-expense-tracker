from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from typing import Literal
import requests
import psycopg2
from psycopg2.extras import RealDictCursor


search_tool = DuckDuckGoSearchRun(region="us-en")

@tool
def calculator(a:float , b:float , operation:Literal["add","subtract","multiply","divide"])-> dict:
    """Perform basic airthematic operation between 2 numbers"""
    if operation == 'add':
        result = str(a+b)
    elif operation == 'subtract':
        result = str(a-b)
    elif operation == 'multiply':
        result = str(a*b)
    elif operation == 'divide':
        if b == 0:
            return {"Error":" Division by zero not allowed"}
        result = str(a/b)
    else:
        return {"Error":"Unsupported operation {operation}"}
    return {'first number': a,'second number':b,'operation':operation,'result':result}

@tool
def get_symbol(company_name:str)->dict:
    """this tool helps to get the symbol of the company so that it can be used by get_stock_price tool"""
    url = "https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={company_name}&apikey=VN3I1Y9HXDSISX9".format(company_name=company_name)
    result = requests.get(url)
    return result.json()

@tool    
def get_stock_price(symbol:str)->dict:
    """this tool returns the stock price of the given symbol representing a company"""
    url = "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=VN3I1Y9HXDSISX96".format(symbol=symbol)
    response = requests.get(url)
    return response.json()

@tool
def get_current_weather_conditions(city:str)->dict:
    """this tool helps to get current wheather conditions of a given city"""
    url = "http://api.weatherstack.com/current?access_key=8a95c7f83d8f91272c168f2f36b13375&query={city}".format(city=city)
    response = requests.get(url)
    return response.json()

@tool
def get_conversion_factor(base_currency:str,target_currency:str):
    """this tool gets the current conversion factor between given base and target currencies"""
    url = "https://v6.exchangerate-api.com/v6/d4cce5d05cd6fb11dd6b6e7d/pair/{base}/{target}".format(base = base_currency,target = target_currency)
    response = requests.get(url)
    return response.json()

@tool
def query_executer_tool(query:str,operation:str)->dict:
    """this tool executes the given postgre sql query on the database and returns the result"""
    CONN_STR = "postgresql://neondb_owner:npg_tCz7IbRPgiq1@ep-gentle-haze-a1iez8ej-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    try:
        with psycopg2.connect(CONN_STR) as conn:
            with conn.cursor(cursor_factory=RealDictCursor if operation=="retrieve" else None) as cur:
                cur.execute(query)
                if operation=="retrieve":
                    return {'retrieved_data':cur.fetchall(),'status':'retrieve operation successful'}
                conn.commit()
                return{'status':f'{operation} operation successful'}
    except Exception as e:
        print("Database Error:", e)
        return {'Error':str(e)}

    

mytools = [search_tool,get_stock_price,calculator,get_symbol,get_current_weather_conditions,get_conversion_factor,query_executer_tool]