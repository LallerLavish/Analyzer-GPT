from agents.codeExecutor import getCodeExecutorAgent
from agents.dataAnalyzer import getDataAnalyzer
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
def get_analyzer_team(docker,model_client):

    code_executor_agent=getCodeExecutorAgent(docker)
    data_analyzer_agent=getDataAnalyzer(model_client)
    text_mention_tem=TextMentionTermination('STOP')
    team=RoundRobinGroupChat(
        participants=[data_analyzer_agent,code_executor_agent],
        max_turns=10,
        termination_condition=text_mention_tem

    )
    return team


