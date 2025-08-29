from contextlib import asynccontextmanager
from dataclasses import dataclass
import os
import pathlib
import uuid
import shutil
from fastapi import Depends, FastAPI, Request
from pydantic import BaseModel, Field

import typing as t
import subprocess as sp
import asyncio


def clean_log_path() -> None:
    raw_path = os.environ.get("LOG_PATH", "")
    if not raw_path:
        raise RuntimeError("The root log path must be specified")

    log_dir = pathlib.Path(raw_path)
    if log_dir.exists():
        shutil.rmtree(log_dir)

    log_dir.mkdir(parents=True, exist_ok=True)


def generate_log_path() -> pathlib.Path:
    raw_path = os.environ.get("LOG_PATH", "")
    if not raw_path:
        raise RuntimeError("The root log path must be specified")

    log_dir = pathlib.Path(raw_path)
    log_dir.mkdir(parents=True, exist_ok=True)

    return log_dir / f"{uuid.uuid4()}.log"


@asynccontextmanager
async def app_lifespan(app: FastAPI) -> t.AsyncGenerator:
    clean_log_path()
    yield
    ...


app = FastAPI(lifespan=app_lifespan)


@dataclass
class SubmissionResult:
    return_code: int
    pid: int
    logs: pathlib.Path | None


class SubmissionRequest(BaseModel):
    command: t.Annotated[str, Field(min_length=1)]


class SubmissionResponse(BaseModel):
    return_code: int
    task_id: str
    logs: str


class ProxyRequestTransformer:
    request: SubmissionRequest
    original_exe: str
    params: str

    def __init__(self, request: SubmissionRequest) -> None:
        self.request = request

        exe, params = request.command.split(" ", maxsplit=1)
        self.original_exe = exe
        self.params = params

    def command(self, job_id: str) -> str:
        return f"srun --jobid={job_id} podman-hpc run --rm -e SHIM=0 ankona/cstar-mockroms:latest {self.params}"


async def submit_job(
    request: SubmissionRequest,
) -> SubmissionResult:
    print(f"Processing proxy submission: {request.command}")

    slurm_job_id = os.environ.get("SLURM_JOB_ID", "")
    if not slurm_job_id:
        raise RuntimeError("No allocation available")

    transformer = ProxyRequestTransformer(request)
    log_path = generate_log_path()

    try:
        with log_path.open("+a") as log_stream:
            cmd = transformer.command(slurm_job_id)
            popen = sp.Popen(cmd.split(), stdout=log_stream, stderr=log_stream)
            rc = popen.wait(timeout=5000)

        return SubmissionResult(rc, popen.pid, log_path)
    except Exception as ex:
        print(f"ex: {ex}")

    return SubmissionResult(99, 0, None)


@app.get("/")
async def root():
    return {"version": "0.1.0"}


tasks = []


@app.post("/task")
async def create_task(request: Request, item: SubmissionRequest) -> SubmissionResponse:
    task = asyncio.create_task(submit_job(item))

    result = await task
    response = SubmissionResponse(
        return_code=result.pid,
        task_id=f"task-{result.return_code}",
        logs=result.logs.as_posix() if result.logs else "",
    )
    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("orchestrator:app", host="0.0.0.0", port=41357, reload=True)
