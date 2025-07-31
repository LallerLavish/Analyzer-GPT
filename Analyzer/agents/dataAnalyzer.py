from autogen_agentchat.agents import AssistantAgent
from agents.prompts.dataAnalyzerPrompts import DATA_ANALYZER_MSG

def getDataAnalyzer(model_client):
    data_agent=AssistantAgent(
        name='Data_Analyzer_Agent',
        description='An agent helps with solving data analysis task and give us the code as well.',
        model_client=model_client,
        system_message=DATA_ANALYZER_MSG
    )

    return data_agent