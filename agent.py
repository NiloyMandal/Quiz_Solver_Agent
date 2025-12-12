from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tools import get_rendered_html, download_file, post_request, run_code, add_dependencies, transcribe_audio
from typing import TypedDict, Annotated, List, Any
from langchain.chat_models import init_chat_model
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
import os
from dotenv import load_dotenv
load_dotenv()

EMAIL = os.getenv("EMAIL")
SECRET = os.getenv("SECRET")
AI_PIPE_TOKEN = os.getenv("AI_PIPE")
RECURSION_LIMIT =  5000
# -------------------------------------------------
# STATE
# -------------------------------------------------
class AgentState(TypedDict):
    messages: Annotated[List, add_messages]


TOOLS = [run_code, get_rendered_html, download_file, post_request, add_dependencies, transcribe_audio]


# -------------------------------------------------
# AI PIPE LLM (Using GPT-4o-mini via OpenRouter)
# -------------------------------------------------
# Note: Rate limiting is handled by AI Pipe, no need for local rate limiter

# Use AI Pipe with OpenRouter
llm = ChatOpenAI(
    model="openai/gpt-4o",
    base_url="https://aipipe.org/openrouter/v1",
    api_key=AI_PIPE_TOKEN,
    temperature=0.3,
    max_retries=2,
    timeout=90
).bind_tools(TOOLS)   


# -------------------------------------------------
# SYSTEM PROMPT
# -------------------------------------------------
SYSTEM_PROMPT = f"""
You are an autonomous quiz-solving agent. You MUST solve tasks and submit answers.

Your job is to:
1. Load the quiz page from the given URL using get_rendered_html.
2. Extract ALL instructions, required parameters, submission rules, and the submit endpoint.
3. Solve the task exactly as required.
4. Submit the answer using post_request to the endpoint specified on the current page.
5. Read the server response and:
   - If it contains a new quiz URL → fetch it immediately and continue.
   - If no new URL is present → return "END".

STRICT RULES — FOLLOW EXACTLY:

GENERAL RULES:
- NEVER stop early. Continue solving tasks until no new URL is provided.
- NEVER hallucinate URLs, endpoints, fields, values, or JSON structure.
- NEVER shorten or modify URLs. Always submit the full URL.
- NEVER re-submit unless the server explicitly allows or it's within the 3-minute limit.
- ALWAYS inspect the server response before deciding what to do next.
- ALWAYS use the tools provided to fetch, scrape, download, render HTML, or send requests.
- DO NOT fetch the same page multiple times - once you have the HTML, solve the task and submit.
- AFTER using get_rendered_html, IMMEDIATELY solve the task and call post_request to submit.

AUDIO TRANSCRIPTION RULES:
- If the task mentions "audio", "transcribe", "spoken phrase", or "passphrase":
  1. Look for an audio file link on the page (usually .mp3, .wav, .m4a, .flac)
  2. Use the transcribe_audio tool with the audio file URL
  3. Submit the transcribed text EXACTLY as transcribed
  4. NEVER guess audio content - always use the transcribe_audio tool
- The transcribe_audio tool automatically downloads and transcribes the audio file

DATA PROCESSING RULES:
- If the task involves CSV, JSON, data transformation, or file processing:
  1. Use download_file to get the data file
  2. Use run_code to write Python code that processes the data EXACTLY as specified
  3. ALWAYS read the task instructions carefully for:
     - Required output format (JSON, CSV, etc.)
     - Date formats (ISO-8601 means YYYY-MM-DD for dates without time, or YYYY-MM-DDTHH:MM:SS with time)
     - Sorting requirements (sort by which field, ascending/descending)
     - Data type requirements (integer, string, etc.)
     - Key naming conventions (snake_case, camelCase, etc.)
  4. For CSV to JSON conversion:
     - Parse ALL date formats in the CSV (MM/DD/YY, YYYY-MM-DD, D Mon YYYY, etc.)
     - Convert column names to required case (snake_case = lowercase with underscores)
     - Strip whitespace from values
     - Convert numeric fields to proper types (int, float)
     - Use json.dumps(data, separators=(',', ':')) for compact JSON (no spaces)
  5. Test your code logic before submitting
  6. Submit the EXACT output from your code - do not modify it manually

TIME LIMIT RULES:
- Each task has a hard 3-minute limit.
- The server response includes a "delay" field indicating elapsed time.
- If your answer is wrong retry again.

STOPPING CONDITION:
- Only return "END" when a server response explicitly contains NO new URL.
- DO NOT return END under any other condition.

ADDITIONAL INFORMATION YOU MUST INCLUDE WHEN REQUIRED:
- Email: {EMAIL}
- Secret: {SECRET}

YOUR JOB:
- Follow pages exactly.
- Extract data reliably.
- Never guess.
- Submit correct answers.
- Continue until no new URL.
- Then respond with: END
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="messages")
])

llm_with_prompt = prompt | llm


# -------------------------------------------------
# AGENT NODE
# -------------------------------------------------
def agent_node(state: AgentState):
    result = llm_with_prompt.invoke({"messages": state["messages"]})
    return {"messages": state["messages"] + [result]}


# -------------------------------------------------
# GRAPH
# -------------------------------------------------
def route(state):
    last = state["messages"][-1]
    # support both objects (with attributes) and plain dicts
    tool_calls = None
    if hasattr(last, "tool_calls"):
        tool_calls = getattr(last, "tool_calls", None)
    elif isinstance(last, dict):
        tool_calls = last.get("tool_calls")

    if tool_calls:
        return "tools"
    # get content robustly
    content = None
    if hasattr(last, "content"):
        content = getattr(last, "content", None)
    elif isinstance(last, dict):
        content = last.get("content")

    if isinstance(content, str) and content.strip() == "END":
        return END
    if isinstance(content, list) and content[0].get("text").strip() == "END":
        return END
    return "agent"
graph = StateGraph(AgentState)

graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(TOOLS))



graph.add_edge(START, "agent")
graph.add_edge("tools", "agent")
graph.add_conditional_edges(
    "agent",    
    route       
)

app = graph.compile()


# -------------------------------------------------
# TEST
# -------------------------------------------------
def run_agent(url: str) -> str:
    app.invoke({
        "messages": [{"role": "user", "content": url}]},
        config={"recursion_limit": RECURSION_LIMIT},
    )
    print("Tasks completed succesfully")

