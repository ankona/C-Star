import subprocess
import sys
import typing as t

import typer
from rich import print

app = typer.Typer()


@app.command()
def check(
    path: t.Annotated[str, typer.Argument(help="Path to the workplan")],
) -> bool:
    """Perform content validation on the workplan supplied by the user.

    Returns
    -------
    bool
        `True` if valid
    """
    rc = 0

    try:
        entrypoint = "cstar.entrypoint.cli.check_model"
        args = " ".join(["--path", str(path), "--model", "workplan"])

        completed_process = subprocess.run(
            f"{sys.executable} -m {entrypoint} {args}".split(),
            capture_output=True,
            text=True,
        )

        rc = completed_process.returncode
        print(completed_process.stdout.strip())
    except Exception as ex:
        print(ex)

    return rc == 0
