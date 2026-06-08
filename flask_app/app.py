import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
import asyncio
import json
from google import genai 
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import sys
import re
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
app=Flask(__name__)


async def get_bot_response(user_message):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    params = StdioServerParameters(
        command="python3",
        args=[os.path.join(BASE_DIR, "mcp/shopbot_server.py")]
    )
    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            
            prompt_result = await session.get_prompt("classifier", {})
            prompt_text = prompt_result.messages[0].content.text.strip()
            
            response = await asyncio.to_thread(
                        client.models.generate_content,
                        model="gemini-2.5-flash",
                        contents=prompt_text + "\n" + user_message
                                )
            result_text = response.text.strip()
            
          
            
            result_text = re.sub(r"^```(?:json)?\s*", "", result_text)
            result_text = re.sub(r"\s*```$", "", result_text)
            
            parsed = json.loads(result_text)
            
            if parsed["tool"] in ["check_order_status", "search_knowledge_base"]:
                tool_result = await session.call_tool(parsed["tool"], parsed["args"])
                return tool_result.content[0].text
            elif parsed["tool"] == "none":
                direct = await asyncio.to_thread(
                            client.models.generate_content,
                            model="gemini-2.5-flash",
                            contents=user_message
                        )
                return direct.text
            else:
                return "I'm not sure how to help with that. Can you rephrase?"

import traceback

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "Missing message"}), 400
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(get_bot_response(user_message))
        return jsonify({"response": result})
    except Exception as e:
        traceback.print_exc()  # prints FULL error to terminal
        return jsonify({"response": "I'm sorry, I couldn't process that request."}), 200
    finally:
        loop.close()
        
@app.route('/')
def index():
    return render_template('index.html')


if __name__=="__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)




