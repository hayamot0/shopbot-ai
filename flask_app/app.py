import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import asyncio
import json
import google.generativeai as genai
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")
app=Flask(__name__)


async def get_bot_response(user_message):
    params = StdioServerParameters(
        command="python3",
        args=[os.path.join(BASE_DIR, "mcp/shopbot_server.py")]
    )

    async with stdio_client(params) as (reader,writer):
        async with ClientSession(reader,writer) as session:
            await session.initialize()
            prompt_result= await session.get_prompt("classifier",{})
            prompt_text=prompt_result.messages[0].content.text.strip()
            response=model.generate_content(prompt_text+ "\n"+ user_message)
            result_text = response.text.strip()
            parsed=json.loads(result_text)

            if parsed["tool"] in ["check_order_status", "search_knowledge_base"]:
                tool_result = await session.call_tool(parsed["tool"], parsed["args"])
                return tool_result.content[0].text

            elif parsed["tool"]=="none":
                direct=model.generate_content(user_message)
                return direct.text

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(get_bot_response(user_message))
    finally:
        loop.close()
    return jsonify({"response": result})


if __name__=="__main__":
    app.run(debug=True)




