# import asyncio
# from pathlib import Path
#
# from prefect import flow, task
#
# from cstar.execution.handler import ExecutionHandler, ExecutionStatus
# from cstar.orchestration.adapter import BlueprintAdapter
# from cstar.orchestration.models import RomsMarblBlueprint
# from cstar.orchestration.serialization import deserialize
# from cstar.simulation import Simulation
#
# ACTION_NAME = "run blueprint"
#
#
# @task
# async def load_blueprint(path: Path) -> RomsMarblBlueprint:
#     """Deserialize the target blueprint.
#
#     Parameters
#     ----------
#     path : Path
#         Path to a blueprint
#
#     Returns
#     -------
#     RomsMarblBlueprint | None
#         A deserialized instance of the blueprint when a valid blueprint is supplied.
#
#     Raises
#     ------
#     ValueError
#         If the blueprint is invalid
#     FileNotFoundError
#         If the path does not point to an existing blueprint
#     """
#     if not path.exists():
#         raise FileNotFoundError(f"No blueprint file found at `{path}`")
#
#     try:
#         if model := deserialize(path, RomsMarblBlueprint):
#             model = RomsMarblBlueprint.model_validate(model)
#
#             print(f"Deserialized model: {model}")
#             return model
#     except ValueError as ex:
#         print(f"Exception occurred: {ex}")
#
#     raise ValueError(f"Unable to load blueprint at `{path}`")
#
#
# @flow
# @task
# async def prepare_environment(blueprint: RomsMarblBlueprint) -> None:
#     """Run simulation setup to prepare the computing environment.
#
#     Parameters
#     ----------
#     blueprint : RomsMarblBlueprint
#         The blueprint specifying environment characteristics
#
#     """
#     print("Preparing the environment starting")
#     # time.sleep(20)
#
#     simulation: Simulation | None = None
#
#     if blueprint is None:
#         raise RuntimeError("Unable to continue without a blueprint")
#
#     # TODO: need to differentiate between a fail state and a "still waiting" state for check_xxx tasks...
#     adapter = BlueprintAdapter(blueprint)
#     simulation = adapter.adapt()
#
#     simulation.setup()
#     simulation.build()
#     simulation.pre_run()
#
#     print("Preparing the environment complete")
#
#
# def is_simulation_done(handler: ExecutionHandler) -> bool:
#     """Evaluate the status of the task related to the execution handler, returning
#     `True` for any completed status.
#     """
#     return handler.status in [
#         ExecutionStatus.COMPLETED,
#         ExecutionStatus.CANCELLED,
#         ExecutionStatus.FAILED,
#         ExecutionStatus.UNKNOWN,
#     ]
#
#
# @task
# async def execute_simulation(blueprint: RomsMarblBlueprint | None) -> None:
#     """Run the target simulation.
#
#     Parameters
#     ----------
#     blueprint : RomsMarblBlueprint
#         The blueprint to execute
#     """
#     print(f"{ACTION_NAME.capitalize()} action is starting")
#
#     if blueprint is None:
#         raise RuntimeError("Unable to continue without a blueprint")
#
#     # TODO: need to differentiate between a fail state and a "still waiting" state for check_xxx tasks...
#     # - does is_simulation_done solve the issue of the original todo?
#     adapter = BlueprintAdapter(blueprint)
#     simulation = adapter.adapt()
#
#     handle = simulation.run()
#
#     # TODO: perform the same raise/retry behavior as workplan status checking.
#     # - should re-use the existing status task...
#     while not is_simulation_done(handle):
#         # await asyncio.sleep(90)
#         handle.updates(0)
#
#     print(f"{ACTION_NAME.capitalize()} action is complete")
#
#
# @task
# async def on_simulation_complete(blueprint: RomsMarblBlueprint) -> None:
#     """Run required simulation post-processing.
#
#     Parameters
#     ----------
#     blueprint : RomsMarblBlueprint
#         The blueprint to execute
#     """
#     print("Simulation teardown starting")
#
#     if blueprint is None:
#         raise RuntimeError("Unable to continue without a blueprint")
#
#     # TODO: need to differentiate between a fail state and a "still waiting" state for check_xxx tasks...
#     adapter = BlueprintAdapter(blueprint)
#     simulation = adapter.adapt()
#
#     simulation.post_run()
#
#     print("Simulation teardown complete")
#
#
# @flow
# async def run_simulation_flow(path: Path) -> None:
#     """Execute all tasks necessary to complete a simulation.
#
#     Parameters
#     ----------
#     path: Path
#         The path to a blueprint
#     """
#     print("Simulation flow starting")
#
#     blueprint = await load_blueprint(path)
#
#     await prepare_environment(blueprint)
#     await execute_simulation(blueprint)
#     await on_simulation_complete(blueprint)
#
#     print("Simulation flow complete")
#     # TODO: must return something....
#     # - should probably make run_simulation_flow the thing that's _scheduled_
#     #   by the orchestrator when it's iterating through available steps.
#
#
# if __name__ == "__main__":
#     asyncio.run(run_simulation_flow(Path.cwd()))
