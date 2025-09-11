import abc
import typing as t

from pydantic import BaseModel

from cstar.base.additional_code import AdditionalCode
from cstar.marbl.external_codebase import MARBLExternalCodeBase
from cstar.orchestration import models
from cstar.roms import ROMSSimulation
from cstar.roms.discretization import ROMSDiscretization
from cstar.roms.external_codebase import ROMSExternalCodeBase
from cstar.roms.input_dataset import (
    ROMSBoundaryForcing,
    ROMSInitialConditions,
    ROMSModelGrid,
    ROMSRiverForcing,
    ROMSSurfaceForcing,
    ROMSTidalForcing,
)

_Tin = t.TypeVar("_Tin", bound=BaseModel)
_Tout = t.TypeVar("_Tout")

# TODO: consider doing a straight up JSON conversion of the model to a format
# that would deserialize into the target "native" object instead of this?


class ModelAdapter(t.Generic[_Tin, _Tout], abc.ABC):
    model: _Tin

    def __init__(self, model: _Tin) -> None:
        self.model = model

    @abc.abstractmethod
    def convert(self) -> _Tout: ...


class DiscretizationAdapter(ModelAdapter[models.Blueprint, ROMSDiscretization]):
    """Convert a blueprint model to a concrete instance."""

    # def __init__(self, model: models.Blueprint) -> None:
    #     self.model = model

    @t.override
    def convert(self) -> ROMSDiscretization:
        return ROMSDiscretization(
            time_step=1,
            n_procs_x=self.model.partitioning.n_procs_x,
            n_procs_y=self.model.partitioning.n_procs_y,
        )


class AddtlCodeAdapter(ModelAdapter[models.Blueprint, AdditionalCode]):
    """Convert a blueprint model to a concrete instance."""

    def __init__(self, model: models.Blueprint, key: str) -> None:
        super().__init__(model)
        self.key = key

    @t.override
    def convert(self) -> AdditionalCode:
        code_attr: models.CodeRepository = getattr(self.model.code, self.key)

        return AdditionalCode(
            location=(self.model.runtime_params.output_dir / "runtime").as_posix(),
            subdir=(str(code_attr.filter.directory) if code_attr.filter else ""),
            checkout_target=code_attr.commit or code_attr.branch,
            files=(code_attr.filter.files if code_attr.filter else []),
        )


class CodebaseAdapter(ModelAdapter[models.Blueprint, ROMSExternalCodeBase]):
    """Convert a blueprint model to a concrete instance."""

    @t.override
    def convert(self) -> ROMSExternalCodeBase:
        return ROMSExternalCodeBase(
            source_repo=str(self.model.code.roms.url),
            checkout_target=self.model.code.roms.commit or self.model.code.roms.branch,
        )


class MARBLAdapter(ModelAdapter[models.Blueprint, MARBLExternalCodeBase]):
    """Convert a blueprint model to a concrete instance."""

    @t.override
    def convert(self) -> MARBLExternalCodeBase:
        if self.model.code.marbl is None:
            msg = "MARBL codebase not found"
            raise RuntimeError(msg)

        return MARBLExternalCodeBase(
            source_repo=str(self.model.code.marbl.url),
            checkout_target=self.model.code.marbl.commit
            or self.model.code.marbl.branch,
        )


class GridAdapter(ModelAdapter[models.Blueprint, ROMSModelGrid]):
    """Convert a blueprint model to a concrete instance."""

    @t.override
    def convert(self) -> ROMSModelGrid:
        if self.model.code.marbl is None:
            msg = "MARBL codebase not found"
            raise RuntimeError(msg)

        return ROMSModelGrid(
            location=str(self.model.runtime_params.output_dir / "model_grid"),
            # WARNING - path is not valid...
            file_hash="",
            start_date=self.model.runtime_params.start_date,
            end_date=self.model.runtime_params.start_date,
        )


class ConditionAdapter(ModelAdapter[models.Blueprint, ROMSInitialConditions]):
    """Convert a blueprint model to a concrete instance."""

    @t.override
    def convert(self) -> ROMSInitialConditions:
        return ROMSInitialConditions(
            location=str(
                self.model.runtime_params.output_dir / "initial_conditions",
            ),
            # WARNING - path is not valid...
            start_date=self.model.runtime_params.start_date,
            end_date=self.model.runtime_params.start_date,
        )


class TidalForcingAdapter(ModelAdapter[models.Blueprint, ROMSTidalForcing]):
    """Convert a blueprint model to a concrete instance."""

    # def __init__(self, model: models.Blueprint, key: str) -> None:
    #     super().__init__(model)
    #     self.key = key

    @t.override
    def convert(self) -> ROMSTidalForcing:
        # code_attr: models.Forcing = getattr(self.model.code, self.key)

        return ROMSTidalForcing(
            location=str(
                self.model.runtime_params.output_dir / "forcing/tidal",
            ),
            # WARNING - path is not valid...
            start_date=self.model.runtime_params.start_date,
            end_date=self.model.runtime_params.start_date,
        )


class RiverForcingAdapter(ModelAdapter[models.Blueprint, ROMSRiverForcing]):
    """Convert a blueprint model to a concrete instance."""

    # def __init__(self, model: models.Blueprint, key: str) -> None:
    #     super().__init__(model)
    #     self.key = key

    @t.override
    def convert(self) -> ROMSRiverForcing:
        # code_attr: models.Forcing = getattr(self.model.code, self.key)

        return ROMSRiverForcing(
            location=str(
                self.model.runtime_params.output_dir / "forcing/river",
            ),
            # WARNING - path is not valid...
            start_date=self.model.runtime_params.start_date,
            end_date=self.model.runtime_params.start_date,
        )


class BoundaryForcingAdapter(ModelAdapter[models.Blueprint, ROMSBoundaryForcing]):
    """Convert a blueprint model to a concrete instance."""

    # def __init__(self, model: models.Blueprint, key: str) -> None:
    #     super().__init__(model)
    #     self.key = key

    @t.override
    def convert(self) -> ROMSBoundaryForcing:
        # code_attr: models.Forcing = getattr(self.model.code, self.key)

        return ROMSBoundaryForcing(
            location=str(
                self.model.runtime_params.output_dir / "forcing/boundary",
            ),
            # WARNING - path is not valid...
            start_date=self.model.runtime_params.start_date,
            end_date=self.model.runtime_params.start_date,
        )


class SurfaceForcingAdapter(ModelAdapter[models.Blueprint, ROMSSurfaceForcing]):
    """Convert a blueprint model to a concrete instance."""

    # def __init__(self, model: models.Blueprint, key: str) -> None:
    #     super().__init__(model)
    #     self.key = key

    @t.override
    def convert(self) -> ROMSSurfaceForcing:
        # code_attr: models.Forcing = getattr(self.model.code, self.key)

        return ROMSSurfaceForcing(
            location=str(
                self.model.runtime_params.output_dir / "forcing/surface",
            ),
            # WARNING - path is not valid...
            start_date=self.model.runtime_params.start_date,
            end_date=self.model.runtime_params.start_date,
        )


class BlueprintAdapter(ModelAdapter[models.Blueprint, ROMSSimulation]):
    """Convert a blueprint model to a concrete instance."""

    def __init__(self, model: models.Blueprint) -> None:
        self.model = model

    @t.override
    def convert(self) -> ROMSSimulation:
        return ROMSSimulation(
            name=self.model.name,
            directory=self.model.runtime_params.output_dir,
            discretization=DiscretizationAdapter(self.model).convert(),
            runtime_code=AddtlCodeAdapter(self.model, "run_time").convert(),
            compile_time_code=AddtlCodeAdapter(self.model, "compile_time").convert(),
            codebase=CodebaseAdapter(self.model).convert(),
            start_date=self.model.runtime_params.start_date,
            end_date=self.model.runtime_params.end_date,
            valid_start_date=self.model.valid_start_date,
            valid_end_date=self.model.valid_end_date,
            marbl_codebase=(
                MARBLAdapter(self.model).convert() if self.model.code.marbl else None
            ),
            model_grid=GridAdapter(self.model).convert(),
            initial_conditions=ConditionAdapter(self.model).convert(),
            tidal_forcing=TidalForcingAdapter(self.model).convert(),
            river_forcing=RiverForcingAdapter(self.model).convert(),
            boundary_forcing=[
                # WARNING - current schema does not take into account a forcing LIST
                BoundaryForcingAdapter(self.model).convert(),
            ],
            surface_forcing=[
                # WARNING - current schema does not take into account a forcing LIST
                SurfaceForcingAdapter(self.model).convert(),
            ],
        )
