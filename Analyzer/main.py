import asyncio
from team.analyzer_gpt import get_analyzer_team
from config.open_ai import get_model_client
from config.dockers_utils import getDockerCommandLineExecutor,start_docker_container,stop_docker_container
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.base import TaskResult

async def main():
    model_client=get_model_client()
    docker=getDockerCommandLineExecutor()

    team=get_analyzer_team(docker,model_client)
    try:
        task="Give me description of data from the file DYCD_after-school_programs__Neighborhood_Development_Area__NDA__Family_Support.csv in the directory"

        await start_docker_container(docker)

        async for message in team.run_stream(task=task):
            print('='*40)
            if isinstance(message,TextMessage):
                print(message.source,':',message.content)
            elif isinstance(message, TaskResult) :
                print("Stop Reason :" , message.stop_reason)
           
    except Exception as e:
        print(e)

    finally:
        await stop_docker_container(docker)

    
if (__name__=='__main__'):
    asyncio.run(main())