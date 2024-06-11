import os, sys
import hazelbean as hb
import subprocess

def launch_magpie(p):
    
    if p.run_this:
        r_repo_dir = '../../../magpie/magpie_develop'
        start_script_filename = 'start.R'
        r_script_path = os.path.join(r_repo_dir, start_script_filename)
        
        # Call r_script_path via subprocess
        hb.path_exists(r_script_path, verbose=True)
        subprocess.run(['Rscript', r_script_path]) 
        