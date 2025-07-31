import os
from autogen_agentchat.agents import CodeExecutorAgent
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
import asyncio

# REMOVED THIS LINE:
# os.environ["DOCKER_HOST"] = "unix:///Users/lavishlaller/Library/Containers/com.docker.docker/Data/docker-cli.sock"

def getCodeExecutorAgent(code_executor):
    code_executor_agent = CodeExecutorAgent(
        name='CodeExecutor',
        code_executor=code_executor
    )
    return code_executor_agent

async def main():
    docker = DockerCommandLineCodeExecutor(
        work_dir='temp',
        timeout=120
    )
    code_executor_agent = getCodeExecutorAgent(docker)

    task = TextMessage(
        content='''Here is the Python Code which you have to run
```python
print('Hello World')```
''',
    source='User'
    )

    try:
        # Start the executor only ONCE
        await docker.start()
        res = await code_executor_agent.on_messages(
            messages=[task],
            cancellation_token=CancellationToken()
        )
        print('result is :', res)

    except Exception as e:
        print(e)
    finally:
        await docker.stop()

if (__name__ == '__main__'):
    asyncio.run(main())