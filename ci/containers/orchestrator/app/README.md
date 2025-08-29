## Notes

Create your allocation:

- `salloc -N 4 -q interactive -t 00:60:00 -A m4632 -J ankona -C cpu`
    - put `SLURM_JOB_ID` into `launch.json` environment args
        - in test terminal, if not @ allocation location, `export SLURM_JOB_ID="42161506"`


Get your ip for testing:

- Use: `echo http://$(ip addr show bond0 | grep 'inet ' | awk '{print $2}' | cut -d/ -f1):41357`
- Start the server and 'publish' your IP for everything to see:
    - `export CSTAR_ORCHESTRATOR_URI=http://$(ip addr show bond0 | grep 'inet ' | awk '{print $2}' | cut -d/ -f1):41357`
    - debugger | srun -n 1 --cpus-per-task 2 /global/homes/a/ankona/code/cstar/ci/containers/orchestrator/app/run.sh

Trigger 3 "mock roms" jobs via calling the roms with a shim
- `export SLURM_JOB_ID=42161506`
- `srun --jobid $SLURM_JOB_ID -n 3 podman-hpc run -i -t --rm -e SLURM_JOB_ID="$SLURM_JOB_ID" -e CSTAR_ORCHESTRATOR_URI="$CSTAR_ORCHESTRATOR_URI" -e SHIM=1 --entrypoint=/entrypoint.sh ankona/cstar-mockroms:7517650 mpirun hostname`


MANUAL Trigger

- export PATH to insert the mock mpirun
    - `export PATH="/global/homes/a/ankona/code/cstar/ci/containers/orchestrator/app/:$PATH"`
    - `export MOCKROMS=/global/homes/a/ankona/code/cstar/ci/containers/orchestrator/app/mockroms.sh`
        - just for making life easier...
- `srun -n 3 --jobid $SLURM_JOB_ID --cpus-per-task=3 mpirun -n 1 "$MOCKROMS"`
    - note: the args to mpirun
