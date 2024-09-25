# 🧪 Python Scripts

The python scripts contained in this folder are designed to exercise the Ray + SLURM + Singularity pipelines.  They are called from the bash scripts after registering resources from a SLURM scheduler.  The correct order of operations is thus:

* sbatch <bash_script.sh>
    *  setup_ray_head.sh
        *  setup_ray_workers.sh
            *  **python_script**


This will deploy the script to the SLURM scheduler which will then setup Ray and execute on the python program you have designated.
