# import asyncio
# import os
# from pathlib import Path
#
# from prefect import flow
#
# from cstar.orchestration.models import Workplan
# from cstar.orchestration.planning import GraphPlanner
# from cstar.orchestration.serialization import deserialize
# from cstar.orchestration.tasks.request import (
#     PlanWorkplanRequest,
#     ValidateWorkplanRequest,
# )
# from cstar.orchestration.tasks.response import (
#     PlanWorkplanResponse,
#     ValidateWorkplanResponse,
# )
#
# ACTION_NAME = "validate workplan"
# PLAN_ACTION_NAME = "plan workplan"
#
#
# async def validate_workplan(
#     request: ValidateWorkplanRequest,
# ) -> ValidateWorkplanResponse:
#     """Validate a workplan.
#
#     Parameters
#     ----------
#     request: ValidateWorkplanRequest
#         Request specifying a workplan to validate
#
#     Returns
#     -------
#     ValidateWorkplanResponse
#     """
#     print(f"{ACTION_NAME.capitalize()} action is starting")
#     is_valid = False
#     error_msg = ""
#
#     try:
#         if _ := deserialize(request.path, Workplan):
#             # Workplan.model_validate(workplan)
#             is_valid = True
#     except ValueError as ex:
#         print(f"Error occurred: {ex}")
#
#     response = ValidateWorkplanResponse(
#         request_id=request.request_id,
#         success=is_valid,
#         error=error_msg,
#     )
#
#     print(f"{ACTION_NAME.capitalize()} action is complete: {response}")
#     return response
#
#
# async def plan_workplan(
#     request: PlanWorkplanRequest,
# ) -> PlanWorkplanResponse:
#     """Generate the execution plan for a workplan.
#
#     Parameters
#     ----------
#     request: PlanWorkplanRequest
#         Request specifying a workplan to plan
#
#     Returns
#     -------
#     PlanWorkplanResponse
#     """
#     print(f"{PLAN_ACTION_NAME.capitalize()} action is starting")
#     plan_path: Path | None = None
#
#     try:
#         if workplan := deserialize(request.path, Workplan):
#             planner = GraphPlanner(workplan)
#             plan_path = planner.render(
#                 planner.graph,
#                 planner.color_map,
#                 planner.name_map,
#                 workplan.name,
#                 Path.cwd(),
#             )
#         else:
#             print(f"The workplan at `{request.path}` could not be loaded")
#
#     except ValueError as ex:
#         print(f"Error occurred: {ex}")
#
#     if plan_path is None:
#         raise ValueError("no plan could be generated")
#
#     response = PlanWorkplanResponse(
#         request_id=request.request_id,
#         plan_path=plan_path,
#     )
#
#     print(f"{PLAN_ACTION_NAME.capitalize()} action is complete: {response}")
#     return response
#
#
# @flow(log_prints=True)
# async def run_plan_workplan_flow(
#     request: PlanWorkplanRequest,
# ) -> PlanWorkplanResponse:
#     """Generate an execution plan for a workplan within a flow.
#
#     Parameters
#     ----------
#     request: PlanWorkplanRequest
#         Request specifying a workplan to plan
#
#     Returns
#     -------
#     PlanWorkplanResponse
#     """
#     print(f"{PLAN_ACTION_NAME.capitalize()} flow is starting")
#
#     response = await plan_workplan(request)
#
#     print(f"{PLAN_ACTION_NAME.capitalize()} flow is complete: {response}")
#     return response
#
#
# @flow(log_prints=True)
# async def run_validate_workplan_flow(
#     request: ValidateWorkplanRequest,
# ) -> ValidateWorkplanResponse:
#     """Validate a workplan within a flow.
#
#     Parameters
#     ----------
#     request: ValidateWorkplanRequest
#         Request specifying a workplan to validate
#
#     Returns
#     -------
#     ValidateWorkplanRequest
#     """
#     print(f"{ACTION_NAME.capitalize()} flow is starting")
#
#     # validation_task = task(validate_workplan, log_prints=True)
#     # response = await validation_task(request)
#
#     response = await validate_workplan(request)
#
#     print(f"{ACTION_NAME.capitalize()} flow is complete: {response}")
#     return response
#
#
# async def main() -> None:
#     """Execute the validation flow using arguments passed via environment variables.
#
#     Required Environment Variables:
#     - CSTAR_WORKPLAN_PATH
#     """
#     print(f"{ACTION_NAME.capitalize()} main is starting")
#
#     path = os.getenv("CSTAR_WORKPLAN_PATH", "")
#
#     request = ValidateWorkplanRequest(path=Path(path))
#     validation_result = await run_validate_workplan_flow(request)
#
#     print(f"{ACTION_NAME.capitalize()} main is complete: {validation_result}")
#
#
# if __name__ == "__main__":
#     """Execute a validation flow."""
#     asyncio.run(main())
