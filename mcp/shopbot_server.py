import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mcp.server.fastmcp import FastMCP
from rag import load_rag_pipeline
from sqlalchemy import create_engine
import pandas as pd
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, "..", ".env"))
mcp=FastMCP("Shopbot_Server")
rag_chain=load_rag_pipeline()

engine=create_engine("mysql+pymysql://root:@localhost/shopbot")

@mcp.tool(name="check_order_status")
def  check_order_history(order_id:int):
    database=pd.read_sql("SELECT order_id, product, status, order_date, tracking_number from orders where order_id=%s",
                         con=engine,params=(order_id,))
    
    if database.empty:
        return f"No order found with ID {order_id}"
    row = database.iloc[0]
    return f"""
Order #{row['order_id']}
Product: {row['product']}
Status: {row['status']}
Order Date: {row['order_date']}
Tracking: {row['tracking_number'] if row['tracking_number'] else 'Not yet assigned'}
"""
    
@mcp.tool(name="search_knowledge_base")
def search_knowledge_base(question:str):
    response=rag_chain.invoke(question)
    return response

@mcp.prompt(name="classifier")
def classifier():
    return """
You are an AI classifier for ShopBot, an online clothing store customer support system.

Your ONLY job is to read the user's message and return a JSON object. Nothing else.
No explanation. No markdown. No extra text. Just pure JSON.

Available tools:
1. check_order_status — use when user mentions an order ID or asks about their order
2. search_knowledge_base — use when user asks about policies, shipping, returns, products, or anything store-related
3. none — use when the question is completely unrelated to the store

JSON formats:

Order question:
{"tool": "check_order_status", "args": {"order_id": 1005}}

Knowledge question:
{"tool": "search_knowledge_base", "args": {"question": "what is the return policy?"}}

Unrelated question:
{"tool": "none"}

Rules:
- Extract the order ID as an integer, not a string
- Rephrase vague questions into clear ones for search_knowledge_base
- If unsure between knowledge and none, use search_knowledge_base
- Never return anything except valid JSON

Now classify this message:
"""

if __name__=="__main__":
    mcp.run()