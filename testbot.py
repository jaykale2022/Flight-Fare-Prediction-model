import os
import asyncio
import base64
import json
import numpy as np
import sounddevice as sd
import websockets
from dotenv import load_dotenv
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.tools import tool
from langchain.messages import HumanMessage
from uuid import uuid4
from dataclasses import dataclass
from openai import OpenAI

# 1. Use your Gemini API Key here
# 2. Add the base_url pointing to Google's OpenAI-compatible endpoint
# client = OpenAI(
#     api_key="AIzaSyDWF0B1jvvUQFEIsrE7mV6VuziD3PnQY-M",
#     base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
# )
# load_dotenv()

# --- Configurations ---
# Updated WS_URL with VAD strategy and a fast (minimal) silence threshold
WS_URL = (
    "wss://api.elevenlabs.io/v1/speech-to-text/realtime"
    "?model_id=scribe_v2_realtime"
    "&encoding=pcm_16000"
    "&language_code=en"
    "&commit_strategy=vad"              # Enable Voice Activity Detection
    "&vad_silence_threshold_secs=0.6"   # Trigger commit after only 300ms of silence
)
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK = 4096
# Replace with your actual key or use os.getenv("ELEVENLABS_API_KEY")
XI_API_KEY = "sk_f6c57d4f8dc242b9c73a339ca77078d244b74cfc899578ce" 

@dataclass
class AgentChunkEvent:
    text: str

# --- Tools ---
@tool
def example_tool(query: str) -> str:
    """Example tool for agent actions."""
    return f"Processed: {query}"

# --- Agent Setup ---
# Note: Ensure you have the necessary provider packages installed (e.g., langchain-anthropic)
# For this example, I am using a placeholder structure as 'create_agent' syntax varies by LangChain version
# If using newer LangGraph, you'd typically use 'create_react_agent'
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI







# model = ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash-lite-preview", 
#     google_api_key="AIzaSyCAOg3D3xua2-B9QhNWgVct5_lGPIxCZ3I",
#     temperature=0.7
# )
NVI=""
# from langchain_nvidia_ai_endpoints import ChatNVIDIA


# Try a smaller, more efficient model
from langchain_groq import ChatGroq

client = ChatGroq(
    model="llama-3.1-8b-instant",  # Make sure you use the "8b" version
    api_key=NVI,
    temperature=0.7
)

agent = create_agent(client, tools=[example_tool], checkpointer=InMemorySaver())


async def run_agent_for_transcript(thread_id, transcript, queue):
    
    

    response = client.chat.completions.create(
      model="llama-3.1-8b-instant",
       messages=[{"role":"system","content":"You are a Professional Property Liaison. "
    "AVOID: Cutesy language, 'digital world' metaphors, or sounding like a toy. "
    "EMBRACE: Transparency, industry terms (site logs, inspections, framing), and "
    "acknowledging the customer's emotional and financial investment. "
    "Your warmth comes from your reliability, not from being 'chatty'."+
    transcript}])

  

    print(f"Response ID: {response.id}")
    print(response.output_text)   
    inp=response.choices[0].message.content
    
    try:
        # Using the standard LangGraph/LangChain invocation
        inputs = {"messages": [HumanMessage(content=inp)]}
        config = {"configurable": {"thread_id": thread_id}}
        
        async for event in agent.astream(inputs, config=config, stream_mode="values"):
            # Get the last message from the agent
            if event["messages"]:
                last_msg = event["messages"][-1]
                if hasattr(last_msg, "content") and last_msg.type == "ai":
                    await queue.put(AgentChunkEvent(text=last_msg.content))
    except Exception as e:
        await queue.put(AgentChunkEvent(text=f"[agent error: {e}]"))

async def main():
    # print(response.choices[0].message.content)
    loop = asyncio.get_running_loop()
    audio_queue = asyncio.Queue()
    agent_result_queue = asyncio.Queue()
    agent_tasks = set()
    stop_event = asyncio.Event()

    def sd_callback(indata, frames, time, status):
        if status:
            print(f"[sounddevice] {status}", flush=True)
        pcm = (indata[:, 0] * 32767).astype(np.int16).tobytes()
        loop.call_soon_threadsafe(audio_queue.put_nowait, pcm)

    async def send_audio(ws):
        while not stop_event.is_set():
            try:
                pcm = await asyncio.wait_for(audio_queue.get(), timeout=0.5)
                msg = {
                    "message_type": "input_audio_chunk",
                    "audio_base_64": base64.b64encode(pcm).decode(),
                }
                await ws.send(json.dumps(msg))
            except asyncio.TimeoutError:
                continue

    async def receive_transcripts(ws):
        thread_id = str(uuid4())
        async for raw in ws:
            data = json.loads(raw)
            msg_type = data.get("message_type", "")

            if msg_type == "session_started":
                print("✅ Session started — speak now!\n")
                

            elif msg_type == "committed_transcript":
                transcript_text = str(data.get("text", ""))
                if transcript_text:
                    print(f"\n[Final STT] {transcript_text}")
                    # Trigger the Agent
                    task = asyncio.create_task(
                        run_agent_for_transcript(thread_id, transcript_text, agent_result_queue)
                    )
                    agent_tasks.add(task)
                    task.add_done_callback(agent_tasks.discard)

            elif msg_type == "error":
                print(f"\n[ERROR] {data}")
                stop_event.set()
                break
            
            # Print agent results as they come in
            while not agent_result_queue.empty():
                res = await agent_result_queue.get()
                print(f"🤖 [Agent Response]: {res.text}")

    # --- Execution ---
    print("🔌 Connecting to ElevenLabs...")
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype="float32", blocksize=CHUNK, callback=sd_callback):
        try:
            async with websockets.connect(
                WS_URL,
                additional_headers={"xi-api-key": XI_API_KEY},
                ping_interval=20,
                ping_timeout=60,
            ) as ws:
                await asyncio.gather(send_audio(ws), receive_transcripts(ws))
        except KeyboardInterrupt:
            print("\n🛑 Stopped by user.")
        finally:
            stop_event.set()

if __name__ == "__main__":
    async def run():
        try:
            await main()
        except Exception as e:
            print(f"Fatal error: {e}")
    
    asyncio.run(run())