import os, sys
import pandas as pd
import hazelbean as hb
import seals
from seals import seals_main, seals_utils, seals_initialize_project
import subprocess

def launch_magpie(p):
    
    if p.run_this:
        r_repo_dir = '../../../magpie/magpie_develop'
        
        # By default launches in interactive mode, but has the option of different environments (e.g. clusters)
        start_script_filename = 'start.R'
        
        # Magpie WD relative to python run file
        implied_wd = "../../../magpie/f_mag-seals"
        original_wd = os.getcwd()
        
        # Relative path of launch script relative to implied wd
        direct_path_from_implied = "scripts/start/seals_runs.R"
        os.chdir(implied_wd)
        
        # Check that script path exists
        hb.path_exists(direct_path_from_implied, verbose=True)
        
        # Call r_script_path via subprocess
        # HACK SHORTCUT, needs to integrate with scenario.csv
        check_path = "output/c_seals_SSP2EU-PkBudg650/fulldata.gdx"
        if not hb.path_exists(check_path):
            hb.log("Magpie not found. Running Magpie.")
            # Launch Magpie
            subprocess.run(['Rscript', direct_path_from_implied]) 
        
        # Not much is printed but could view raw log file.
        hb.log("R script complete.")
        
        # After the 30min magpie run complete, next we call the merge_SEALS_report.r script
        # This wil create a csv containing all the scenarios in scenario_definitions.csv, which will be renamed seals_scenario_config_all.csv API type
        # Note that we will need to update the seals scenario_definitions.csv 
        post_processing_script_filename = "merge_SEALS_report.r"
        post_processing_dir = "scripts/output/extra"
        post_processing_script_path = os.path.join(post_processing_dir, post_processing_script_filename)
        
        # Run it
        subprocess.run(['Rscript', post_processing_script_path])
        
        # Then, we call seals directly on that new csv
        # which will be done by the next task in the task tree
        new_implied_wd = implied_wd[2:]
        p.updated_scenarios_csv_path = os.path.join(p.user_dir, 'Files', 'magpie', 'f_mag-seals', 'output', "seals_scenario_config_all.csv")
        hb.path_exists(p.updated_scenarios_csv_path, verbose=True)
        hb.path_copy(p.updated_scenarios_csv_path, p.scenario_definitions_path)
        
        df = pd.read_csv(p.scenario_definitions_path)
        
        # Change the aoi column to RWA for all rows
        df['aoi'] = 'RWA'
        
        
        
        # Make the secound column in the counterfactual_label column be c_seals_SSP2EU-PkBudg650
        df.loc[1, 'counterfactual_label'] = 'c_seals_SSP2EU-Ref'
        df.loc[2, 'counterfactual_label'] = 'c_seals_SSP2EU-PkBudg650'


        df.to_csv(p.scenario_definitions_path, index=False)


        # 
        # c_seals_SSP2EU-Ref
        

        
        # Reload scenario_definitions_path and set all derived attributes
        p.scenarios_df = pd.read_csv(p.scenario_definitions_path)
        for index, row in p.scenarios_df.iterrows():
            seals_utils.assign_df_row_to_object_attributes(p, row)
            seals_utils.set_derived_attributes(p)
        
        