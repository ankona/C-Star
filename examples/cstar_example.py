"""
This is a condensed version of the `cstar_example_notebook.ipynb` designed
to be run in an interactive python session.

For more details, see ../README.md or `cstar_example_notebook.ipynb`
"""

import cstar
import os

roms_marbl_sim = cstar.Simulation.from_blueprint(
    blueprint="cstar_blueprint_yaml_test.yaml",
    caseroot="roms_marbl_example/",
    start_date="20120103 12:00:00",
    end_date="20120103 18:00:00",
)

## In a python session, execute:
roms_marbl_sim.setup()
roms_marbl_sim.build()
roms_marbl_sim.pre_run()


# Substitute your account key on any HPC system
handler = roms_marbl_sim.run(account_key=os.environ.get("ACCOUNT_KEY"))

# Use the handler to request status updates on the simulation
handler.updates(0, confirm_indefinite=True)

if handler.status != cstar.execution.handler.ExecutionStatus.RUNNING:
    print(handler.status)

if handler.status == cstar.execution.handler.ExecutionStatus.FAILED:
    print("An error occurred. See:", handler.output_file)
else:
    roms_marbl_sim.post_run()
