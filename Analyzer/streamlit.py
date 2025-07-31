import streamlit as st
import asyncio
import os
from team.analyzer_gpt import get_analyzer_team

from autogen_agentchat.messages import TextMessage
from autogen_agentchat.base import TaskResult

from config.open_ai import get_model_client
from config.dockers_utils import getDockerCommandLineExecutor, start_docker_container, stop_docker_container

# --- Page Configuration ---
st.set_page_config(
    page_title="Analyzer Agent",
    page_icon="🤖",
    layout="wide"
)

# --- Session State Initialization ---
# This ensures that the session state keys exist when the app starts.
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'autogen_team_state' not in st.session_state:
    st.session_state.autogen_team_state = None
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None

# --- Agent Display Mapping ---
# A dictionary to map agent names to user-friendly names and avatars
AGENT_AVATARS = {
    "user": "👨",
    "Data_Analyzer_Agent": "🤖",
    "CodeExecutor": "🧑🏻‍💻",
    "task_result": "✅"
}

# --- Core Functions ---
async def run_analyzer_gpt(docker, openai_model_client, task):
    """
    Runs the AutoGen analysis team asynchronously and streams the output to the Streamlit UI.
    """
    try:
        await start_docker_container(docker)
        team = get_analyzer_team(docker, openai_model_client)

        if st.session_state.autogen_team_state is not None:
            await team.load_state(st.session_state.autogen_team_state)

        async for message in team.run_stream(task=task):
            if isinstance(message, TextMessage):
                # Extract source and content
                source = message.source.name if hasattr(message.source, 'name') else 'user'
                content = message.content.strip()
                
                # Create a message dictionary to store
                msg_data = {"role": source, "content": content}
                st.session_state.messages.append(msg_data)

                # Display the message in the chat UI
                with st.chat_message(name=source, avatar=AGENT_AVATARS.get(source, "❓")):
                    st.markdown(content)

            elif isinstance(message, TaskResult):
                result_content = f"**Task Complete**: {message.stop_reason}"
                st.session_state.messages.append({"role": "task_result", "content": result_content})
                with st.chat_message(name="task_result", avatar=AGENT_AVATARS["task_result"]):
                    st.success(result_content)

        # Save the final state of the AutoGen team
        st.session_state.autogen_team_state = await team.save_state()
        return None  # No error
    except Exception as e:
        st.error(f"An error occurred during analysis: {e}")
        return e
    finally:
        await stop_docker_container(docker)

# --- UI Rendering ---

# --- Sidebar for Controls ---
with st.sidebar:
    st.header("📊 Controls")
    
    uploaded_file = st.file_uploader(
        'Upload your CSV file',
        type='csv',
        help="Upload the data file you want to analyze."
    )

    if st.button("✨ New Analysis"):
        # Clear all session state to start fresh
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

    if uploaded_file is not None:
        # Save the uploaded file to a temporary location
        if not os.path.exists('temp'):
            os.makedirs('temp')
        
        file_path = f'temp/{uploaded_file.name}'
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        # Store file name in session state to persist it
        st.session_state.uploaded_file_name = uploaded_file.name
        st.success(f"Uploaded `{uploaded_file.name}` successfully!")
    
    # Display the name of the file currently in use
    if st.session_state.uploaded_file_name:
        st.info(f"**Current File:** `{st.session_state.uploaded_file_name}`")

# --- Main Chat Interface ---
st.title("🤖 Analyzer GPT")
st.caption("Your AI-powered assistant for digital data analysis")

# Display existing chat messages from history
for msg in st.session_state.messages:
    with st.chat_message(name=msg["role"], avatar=AGENT_AVATARS.get(msg["role"], "❓")):
        st.markdown(msg["content"])

# Handle new chat input from the user
prompt = st.chat_input(
    "Enter your task here...", 
    disabled=not st.session_state.uploaded_file_name,
    key="chat_input"
)

if prompt:
    # Display user's new message immediately
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=AGENT_AVATARS["user"]):
        st.markdown(prompt)

    # Prepare and run the analysis
    openai_model_client = get_model_client()
    docker = getDockerCommandLineExecutor()

    # The task sent to autogen should mention the file path
    full_task_prompt = f"{prompt} (The data is in the file named '{st.session_state.uploaded_file_name}')"

    with st.spinner("🧠 The agents are thinking... Please wait."):
        error = asyncio.run(run_analyzer_gpt(docker, openai_model_client, full_task_prompt))

    # After the run, check for and display any generated image
    if os.path.exists('temp/output.png'):
        st.image('temp/output.png', caption='Generated Analysis Chart')

    # Rerun to ensure the UI state is consistent after the async operation
    st.rerun()

# Show a warning if no file has been uploaded yet
if not st.session_state.uploaded_file_name:
    st.warning("Please upload a CSV file using the sidebar to begin the analysis.")