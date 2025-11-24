import typing as t
from datetime import datetime

from cstar.orchestration.models import RomsMarblBlueprint, Step
from cstar.orchestration.serialization import deserialize


class Splitter(t.Protocol):
    """Protocol for a class that splits a step into multiple sub-steps."""

    def split(self, step: Step) -> t.Iterable[Step]:
        """Split a step into multiple sub-steps.

        Parameters
        ----------
        step : Step
            The step to split.

        Returns
        -------
        Iterable[Step]
            The sub-steps.
        """
        ...


TRANSFORMS: dict[str, Splitter] = {}


def register_transform(application: str, transform: Splitter) -> None:
    """Register a splitter for an application.

    Parameters
    ----------
    application : str
        The application name.
    transform : Splitter
        The transform instance.
    """
    TRANSFORMS[application] = transform


def get_transform(application: str) -> Splitter | None:
    """Retrieve a transform for an application.

    Parameters
    ----------
    application : str
        The application name.

    Returns
    -------
    Splitter | None
        The transform instance, or None if not found.
    """
    return TRANSFORMS.get(application)


def get_time_slices(
    start_date: datetime, end_date: datetime
) -> t.Iterable[tuple[datetime, datetime]]:
    """Get the time slices for the given start and end dates."""
    current_date = datetime(start_date.year, start_date.month, 1)

    time_slices = []
    while current_date < end_date:
        month_start = current_date

        if month_start.month == 12:
            month_end = datetime(current_date.year + 1, 1, 1)
        else:
            month_end = datetime(
                current_date.year,
                month_start.month + 1,
                1,
                hour=0,
                minute=0,
                second=0,
            )

        time_slices.append((month_start, month_end))
        current_date = month_end

    # adjust when the start date is not the first day of the month
    if start_date > time_slices[0][0]:
        time_slices[0] = (start_date, time_slices[0][1])

    # adjust when the end date is not the last day of the month
    if end_date < time_slices[-1][1]:
        time_slices[-1] = (time_slices[-1][0], end_date)

    return time_slices


class RomsMarblTimeSplitter(Splitter):
    """A splitter used to split a step into multiple sub-steps
    based on the timespan covered by the simulation.
    """

    def split(self, step: Step) -> t.Iterable[Step]:
        """Split a step into multiple sub-steps.

        Parameters
        ----------
        step : Step
            The step to split.

        Returns
        -------
        Iterable[Step]
            The sub-steps.
        """
        blueprint = deserialize(step.blueprint, RomsMarblBlueprint)
        start_date = blueprint.runtime_params.start_date
        end_date = blueprint.runtime_params.end_date

        if end_date <= start_date:
            raise ValueError("end_date must be after start_date")

        time_slices = get_time_slices(start_date, end_date)

        depends_on = step.depends_on
        for time_slice in time_slices:
            step_name = f"{step.name}_{time_slice[0].strftime('%Y:%m:%d')}-{time_slice[1].strftime('%Y:%m:%d')}"

            # TODO: follow-up with Dafydd/Nora to understand how to pass
            # input/output files to each new step
            attributes = step.model_dump()

            updates = {
                "name": step_name,
                "blueprint_overrides": {
                    "runtime_params": {
                        "start_date": time_slice[0].strftime("%Y-%m-%d %H:%M:%S"),
                        "end_date": time_slice[1].strftime("%Y-%m-%d %H:%M:%S"),
                        "checkpoint_frequency": "1m",
                    }
                },
                "depends_on": depends_on,
            }
            attributes.update(updates)

            yield Step(**attributes)

            # use dependency on the prior substep to chain all the dynamic steps
            depends_on = [step_name]


register_transform("roms", RomsMarblTimeSplitter())
register_transform("roms_marbl", RomsMarblTimeSplitter())
