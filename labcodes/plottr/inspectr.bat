:: in a conda environment where qcodes and plottr are installed (qcodes_sandbox), call a script, passing all arguments %*

call conda activate qcodes_sandbox
python inspectr_launch.py %*
call conda deactivate
