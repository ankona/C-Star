#!/bin/bash
# ############################### 
# Run the orchestrator python app
# ############################### 
# source /etc/profile
module load conda
conda activate runner
# exec "$@"
# fastapi dev /global/homes/a/ankona/code/cstar/ci/containers/orchestrator/app/orchestrator.py
uvicorn orchestrator:app --host 0.0.0.0 --port 41357
