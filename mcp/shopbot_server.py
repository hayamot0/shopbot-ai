import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mcp.server.fastmcp import FastMCP
from rag import load_rag_pipeline
from sqlalchemy import create_engine
import pandas as pd

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

if __name__=="__main__":
    mcp.run()