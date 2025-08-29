## Notes

Create your allocation:

- `salloc -N 4 -q interactive -t 00:60:00 -A m4632 -J ankona -C cpu`
    - put `SLURM_JOB_ID` into `launch.json` environment args
        - in test terminal, if not @ allocation location, `export SLURM_JOB_ID="42161506"`

Find the ip for the orchestrator service:

- Use: `echo http://$(ip addr show bond0 | grep 'inet ' | awk '{print $2}' | cut -d/ -f1):41357`
- Start the server and 'publish' add the IP to the env so subsequent commands can read it
    - `export CSTAR_ORCHESTRATOR_URI=http://$(ip addr show bond0 | grep 'inet ' | awk '{print $2}' | cut -d/ -f1):41357`
    - debugger | srun -n 1 --cpus-per-task 2 /global/homes/a/ankona/code/cstar/ci/containers/orchestrator/app/run.sh
    - `export SLURM_JOB_ID=42161506`

Trigger 3 "mock roms" jobs via calling the roms with a shim (see: SHIM=1)

- `srun --jobid $SLURM_JOB_ID -n 3 podman-hpc run -i -t --rm -e SLURM_JOB_ID="$SLURM_JOB_ID" -e CSTAR_ORCHESTRATOR_URI="$CSTAR_ORCHESTRATOR_URI" -e SHIM=1 --entrypoint=/entrypoint.sh ankona/cstar-mockroms:eca3c73 mpirun hostname`
