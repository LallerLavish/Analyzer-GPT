from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor
from config.constants import TIMEOUT_DOCKER,WORK_DIR_DOCKER
def getDockerCommandLineExecutor():
    docker = DockerCommandLineCodeExecutor(
        work_dir=WORK_DIR_DOCKER,
        timeout=TIMEOUT_DOCKER
    )
    return docker

async def start_docker_container(docker):
    print("Starting Docker")
    await docker.start()
    print("Docker started")

async def stop_docker_container(docker):
    print("Stopping Docker")
    await docker.stop()
    print("Docker Stopped")