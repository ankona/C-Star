import enum
import typing as t
from pathlib import Path

from pydantic import BaseModel, ValidationError
from yaml import safe_load

from cstar.orchestration import models
from cstar.roms import ROMSSimulation


class PersistenceMode(enum.StrEnum):
    """Supported serialization engines."""

    json = enum.auto()
    yaml = enum.auto()
    auto = enum.auto()


def _bp_to_sim(model: models.RomsMarblBlueprint) -> ROMSSimulation | None: ...


def _wp_to_sim(model: models.Workplan) -> ROMSSimulation | None:
    """This doesn't make sense unless the mapping functions return an iterable
    that can be used to iterate over all the underlying simulations...

    Do I really want this in deserialization?
    """


_T = t.TypeVar("_T", bound=BaseModel)


def _read_json(path: Path, klass: type[_T]) -> _T | None:
    """Attempt to read JSON from a document.

    Parameters
    ----------
    path : Path
        Path to a document containing JSON
    klass : type[_T]
        The type to deserialize the JSON into

    Returns
    -------
    _T : The instance deserialized from the document
    """
    try:
        with path.open("r", encoding="utf-8") as fp:
            return klass.model_validate_json(json_data=fp.read())
    except ValidationError:
        msg = f"Invalid content in json document: {path}"
        print(msg)
    except ValueError:
        msg = f"Unable to read model from json document: {path}"

    return None


def _read_yaml(path: Path, klass: type[_T]) -> _T | None:
    """Attempt to read YAML from a document.

    Parameters
    ----------
    path : Path
        Path to a document containing YAML
    klass : type[_T]
        The type to deserialize the YAML into

    Returns
    -------
    _T : The instance deserialized from the document
    """
    try:
        with path.open("r", encoding="utf-8") as fp:
            model_dict = safe_load(fp)
            return klass.model_validate(model_dict)
    except ValidationError:
        msg = f"Invalid content in yaml document: {path}"
        print(msg)
    except ValueError:
        msg = f"Unable to read model from yaml document: {path}"

    return None


adapter_map: dict[
    type[models.RomsMarblBlueprint | models.Workplan],
    t.Callable[[models.RomsMarblBlueprint], ROMSSimulation | None]
    | t.Callable[[models.Workplan], ROMSSimulation | None],
] = {
    models.RomsMarblBlueprint: _bp_to_sim,
    models.Workplan: _wp_to_sim,
}

_DT = t.TypeVar("_DT", models.RomsMarblBlueprint, models.Workplan)


def deserialize(
    path: Path,
    klass: type[_DT],
    mode: PersistenceMode = PersistenceMode.auto,
) -> _DT:
    """Deserialize a blueprint into a Simulation instance.

    Parameters
    ----------
    path : Path
        The location of the blueprint
    mode : t.Literal["json", "yaml", "auto"]
        The type of serializer used to create the file.

        The default value of `auto` selects based on the file extension.

    Raises
    ------
    FileNotFoundError:
        If the blueprint file does not exist
    ValueError
        If the blueprint cannot be deserialized with the desired mode

    Returns
    -------
    Simulation
        The deserialized Simulation instance.

    """
    if not path.exists():
        msg = f"A blueprint file could not be found at the path `{path}`"
        raise FileNotFoundError(msg)

    model: _DT | None = None
    ext = path.suffix
    is_auto = mode == PersistenceMode.auto
    use_json = (is_auto and ext == ".json") or mode == PersistenceMode.json
    use_yaml = (is_auto and (ext in {".yaml", ".yml"})) or mode == PersistenceMode.yaml

    if use_json:
        model = _read_json(path, klass)
    elif use_yaml:
        model = _read_yaml(path, klass)

    if model is None:
        msg = f"Unable to deserialize the blueprint at `{path}` with mode `{mode}`"
        raise ValueError(msg)

    return model
