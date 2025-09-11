import time

from prefect import flow, task

from cstar.orchestration.adapter import BlueprintAdapter
from cstar.orchestration.models import RomsMarblBlueprint
from cstar.simulation import Simulation


@task
def load_blueprint() -> RomsMarblBlueprint | None:
    """Deserialize the target blueprint."""
    model: RomsMarblBlueprint | None = None

    # todo: deserialize the blueprint received in the input
    if model:
        model = RomsMarblBlueprint.validate(model)

    return model


@task
def prepare_environment() -> None:
    """Run simulation setup to prepare the computing environment."""
    print("Preparing the environment starting")
    time.sleep(20)

    simulation: Simulation | None = None
    model: RomsMarblBlueprint | None = None

    if model is None:
        raise RuntimeError("Unable to continue without a blueprint")

    # TODO: need to differentiate between a fail state and a "still waiting" state for check_xxx tasks...
    adapter = BlueprintAdapter(model)
    simulation = adapter.adapt()

    simulation.setup()
    simulation.build()
    simulation.pre_run()

    print("Preparing the environment complete")


@task
def execute_simulation() -> None:
    """Run the target simulation."""
    print("Simulation execution starting")

    simulation: Simulation | None = None
    model: RomsMarblBlueprint | None = None

    if model is None:
        raise RuntimeError("Unable to continue without a blueprint")

    # TODO: need to differentiate between a fail state and a "still waiting" state for check_xxx tasks...
    adapter = BlueprintAdapter(model)
    simulation = adapter.adapt()

    simulation.run()

    time.sleep(20)
    print("Simulation execution complete")


@task
def teardown_environment() -> None:
    """Run required simulation post-processing."""
    print("Simulation teardown starting")
    time.sleep(20)

    simulation: Simulation | None = None
    model: RomsMarblBlueprint | None = None

    if model is None:
        raise RuntimeError("Unable to continue without a blueprint")

    # TODO: need to differentiate between a fail state and a "still waiting" state for check_xxx tasks...
    adapter = BlueprintAdapter(model)
    simulation = adapter.adapt()

    simulation.post_run()

    print("Simulation teardown complete")


@flow
def run_flow() -> None:
    """Execute all tasks necessary to complete a simulation."""
    print("Simulation flow starting")
    t0 = prepare_environment.submit()
    t1 = execute_simulation.submit(wait_for=[t0])
    t2 = teardown_environment.submit(wait_for=[t1])
    t2.wait()
    print("Simulation flow complete")


if __name__ == "__main__":
    run_flow()
