import typing as t
from enum import StrEnum, auto

import typer

# from rich import print
from cstar.execution.file_system import local_copy
from cstar.orchestration.models import RomsMarblBlueprint, Workplan
from cstar.orchestration.serialization import deserialize

app = typer.Typer()


class CheckableModel(StrEnum):
    WORKPLAN = auto()
    ROMS_MARBL = auto()


ModelTypes: t.TypeAlias = type[Workplan] | type[RomsMarblBlueprint]


@app.command()
def main(
    path: t.Annotated[str, typer.Option(help="Path to the workplan")],
    model: t.Annotated[
        CheckableModel, typer.Option(help="The model type to be validated")
    ],
) -> bool:
    """Perform content validation on the workplan supplied by the user.

    Returns
    -------
    bool
        `True` if valid
    """
    entity: Workplan | RomsMarblBlueprint | None = None
    friendly_name: str = "not-set"
    status: str = "not-set"

    try:
        with local_copy(path) as document_path:
            match model:
                case CheckableModel.ROMS_MARBL:
                    friendly_name = "ROMS-MARBL blueprint"
                    entity = deserialize(document_path, RomsMarblBlueprint)
                case CheckableModel.WORKPLAN:
                    friendly_name = "workplan"
                    entity = deserialize(document_path, Workplan)
    except ValueError:
        status = "is [bold red]invalid[/bold red]"
        # result = f"The {friendly_name} is invalid: {ex}"
    except FileNotFoundError:
        status = f"was [bold red]not found[/bold red] at path: [red]{path}[/red]"
    else:
        status = "is [bold green]valid[/bold green]"

    print(f"[bold blue]{friendly_name}[/bold blue] {status}")
    if entity is None:
        typer.Exit(1)

    return entity is not None


if __name__ == "__main__":
    typer.run(main)
