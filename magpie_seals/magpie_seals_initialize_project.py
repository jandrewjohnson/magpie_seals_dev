import os, sys
import hazelbean as hb
from hazelbean import cloud_utils

import seals
from seals import seals_main
from seals import seals_generate_base_data
from seals import seals_process_coarse_timeseries
from seals import seals_visualization_tasks
from seals import config
from seals.seals_utils import download_google_cloud_blob

import magpie_integration


def run(p):   
    hb.log('Created ProjectFlow object at ' + p.project_dir + '\n    from script ' + p.calling_script + '\n    with base_data set at ' + p.base_data_dir)
       
    # initialize and set all basic variables. Sadly this is still needed even for a SEALS run until it's extracted.
    # p.combined_block_lists_paths = None # This will be smartly determined in either calibration or allocation


    ###--------------- Additional options (could make advanced options in the UI eventually) ----------------

    # Determine if overviews should be written.
    p.write_global_lulc_overviews_and_tifs = True    

    # Specifies which sigmas should be used in a gaussian blur of the class-presence tifs in order to regress on adjacency.
    # Note this will have a huge impact on performance as full-extent gaussian blurs for each class will be generated for
    # each sigma.
    # TODOO Figure out how this relates to the coefficients csv. I could probably derive these values from that csv.
    p.gaussian_sigmas_to_test = [1, 5]

    # There are still multiple ways to do the allocation. Unless we input a fully-defined
    # change matrix, there will always be ambiguities. One way of lessening them is to 
    # switch from the default allocation method (just do positive allocation requests)
    # to one that also increases the total goal when some other class
    # goes on it. Allowing it leads to a greater amount of the requested allocation
    # happening, but it can lead to funnylooking total-flip cells.
    p.allow_contracting = 0

    # Change how many generations of training to allow. A generation is an exhaustive search so relatievely few generations are required to get to a point
    # where no more improvements can be found.
    p.num_generations = 1

    # If True, will load that which was calculated in the calibration run.
    p.use_calibration_created_coefficients = 0

    
    # Sometimes runs fail mid run. This checks for that and picks up where there is a completed file for that zone. 
    # However doing so can cause confusing cache-invalidation situations for troubleshooting so it's off by default.
    p.skip_created_downscaling_zones = 0

    # For testing,it may be useful to just run the first element of each iterator for speed.
    p.run_only_first_element_of_each_iterator = 0


    ##--------------- Pyramid path references.  ----------------
    
    # To easily convert between per-ha and per-cell terms, these very accurate ha_per_cell maps are defined.
    p.ha_per_cell_10sec_ref_path = os.path.join('pyramids', "ha_per_cell_10sec.tif")
    p.ha_per_cell_300sec_ref_path = os.path.join('pyramids', "ha_per_cell_300sec.tif")
    p.ha_per_cell_900sec_ref_path = os.path.join('pyramids', "ha_per_cell_900sec.tif")
    p.ha_per_cell_1800sec_ref_path = os.path.join('pyramids', "ha_per_cell_1800sec.tif")
    p.ha_per_cell_3600sec_ref_path = os.path.join('pyramids', "ha_per_cell_3600sec.tif")


    p.ha_per_cell_ref_paths = {}
    p.ha_per_cell_ref_paths[10.0] = p.ha_per_cell_10sec_ref_path
    p.ha_per_cell_ref_paths[300.0] = p.ha_per_cell_300sec_ref_path
    p.ha_per_cell_ref_paths[900.0] = p.ha_per_cell_900sec_ref_path
    p.ha_per_cell_ref_paths[1800.0] = p.ha_per_cell_1800sec_ref_path
    p.ha_per_cell_ref_paths[3600.0] = p.ha_per_cell_3600sec_ref_path

    # To easily convert between per-ha and per-cell terms, these very accurate ha_per_cell maps are defined.
    p.ha_per_cell_10sec_path = os.path.join(p.base_data_dir, 'pyramids', "ha_per_cell_10sec.tif")
    p.ha_per_cell_300sec_path = os.path.join(p.base_data_dir, 'pyramids', "ha_per_cell_300sec.tif")
    p.ha_per_cell_900sec_path = os.path.join(p.base_data_dir, 'pyramids', "ha_per_cell_900sec.tif")
    p.ha_per_cell_1800sec_path = os.path.join(p.base_data_dir, 'pyramids', "ha_per_cell_1800sec.tif")
    p.ha_per_cell_3600sec_path = os.path.join(p.base_data_dir, 'pyramids', "ha_per_cell_3600sec.tif")

    p.ha_per_cell_paths = {}
    p.ha_per_cell_paths[10.0] = p.ha_per_cell_10sec_path
    p.ha_per_cell_paths[300.0] = p.ha_per_cell_300sec_path
    p.ha_per_cell_paths[900.0] = p.ha_per_cell_900sec_path
    p.ha_per_cell_paths[1800.0] = p.ha_per_cell_1800sec_path
    p.ha_per_cell_paths[3600.0] = p.ha_per_cell_3600sec_path

    # The ha per cell paths also can be used when writing new tifs as the match path.
    p.match_10sec_path = p.ha_per_cell_10sec_path
    p.match_300sec_path = p.ha_per_cell_300sec_path
    p.match_900sec_path = p.ha_per_cell_900sec_path
    p.match_1800sec_path = p.ha_per_cell_1800sec_path
    p.match_3600sec_path = p.ha_per_cell_3600sec_path

    p.match_paths = {}
    p.match_paths[10.0] = p.match_10sec_path
    p.match_paths[300.0] = p.match_300sec_path
    p.match_paths[900.0] = p.match_900sec_path
    p.match_paths[1800.0] = p.match_1800sec_path
    p.match_paths[3600.0] = p.match_3600sec_path

    p.ha_per_cell_column_10sec_path = os.path.join(p.base_data_dir, 'pyramids', "ha_per_cell_column_10sec.tif")
    p.ha_per_cell_column_300sec_path = os.path.join(p.base_data_dir, 'pyramids', "ha_per_cell_column_300sec.tif")
    p.ha_per_cell_column_900sec_path = os.path.join(p.base_data_dir, 'pyramids', "ha_per_cell_column_900sec.tif")
    p.ha_per_cell_column_1800sec_path = os.path.join(p.base_data_dir, 'pyramids', "ha_per_cell_column_1800sec.tif")
    p.ha_per_cell_column_3600sec_path = os.path.join(p.base_data_dir, 'pyramids', "ha_per_cell_column_3600sec.tif")

    # If you're willing to assume the world is a sphere, it's faster to just load the columns
    p.ha_per_cell_column_paths = {}
    p.ha_per_cell_column_paths[10.0] = p.ha_per_cell_column_10sec_path
    p.ha_per_cell_column_paths[300.0] = p.ha_per_cell_column_300sec_path
    p.ha_per_cell_column_paths[900.0] = p.ha_per_cell_column_900sec_path
    p.ha_per_cell_column_paths[1800.0] = p.ha_per_cell_column_1800sec_path
    p.ha_per_cell_column_paths[3600.0] = p.ha_per_cell_column_3600sec_path

    # On the stitched_lulc_simplified_scenarios task, optionally clip it to the aoi. Be aware that this
    # means you can no longer user it in Pyramid-style operations (basically all besides zonal stats).
    p.clip_to_aoi = 1
    
    ### ------------------- SET UNUSED ATTRIBUTES TO NONE ------------------- ###
    
    if not hasattr(p, 'subset_of_blocks_to_run'):
        p.subset_of_blocks_to_run = None # No subset


    ### ------------------- Build paths to download ------------------- ###
    p.static_regressor_paths = {}
    p.static_regressor_paths['sand_percent'] = os.path.join(p.base_data_dir, 'seals', 'static_regressors', 'sand_percent.tif')
    p.static_regressor_paths['silt_percent'] = os.path.join(p.base_data_dir, 'seals', 'static_regressors', 'silt_percent.tif')
    p.static_regressor_paths['soil_bulk_density'] = os.path.join(p.base_data_dir, 'seals', 'static_regressors', 'soil_bulk_density.tif')
    p.static_regressor_paths['soil_cec'] = os.path.join(p.base_data_dir, 'seals', 'static_regressors', 'soil_cec.tif')
    p.static_regressor_paths['soil_organic_content'] = os.path.join(p.base_data_dir, 'seals', 'static_regressors', 'soil_organic_content.tif')
    p.static_regressor_paths['strict_pa'] = os.path.join(p.base_data_dir, 'seals', 'static_regressors', 'strict_pa.tif')
    p.static_regressor_paths['temperature_c'] = os.path.join(p.base_data_dir, 'seals', 'static_regressors', 'temperature_c.tif')
    p.static_regressor_paths['travel_time_to_market_mins'] = os.path.join(p.base_data_dir, 'seals', 'static_regressors', 'travel_time_to_market_mins.tif')
    p.static_regressor_paths['wetlands_binary'] = os.path.join(p.base_data_dir, 'seals', 'static_regressors', 'wetlands_binary.tif')
    p.static_regressor_paths['alt_m'] = os.path.join(p.base_data_dir, 'seals', 'static_regressors', 'alt_m.tif')
    p.static_regressor_paths['carbon_above_ground_mg_per_ha_global'] = os.path.join(p.base_data_dir, 'seals', 'static_regressors', 'carbon_above_ground_mg_per_ha_global.tif')
    p.static_regressor_paths['clay_percent'] = os.path.join(p.base_data_dir, 'seals', 'static_regressors', 'clay_percent.tif')
    p.static_regressor_paths['ph'] = os.path.join(p.base_data_dir, 'seals', 'static_regressors', 'ph.tif')
    p.static_regressor_paths['pop'] = os.path.join(p.base_data_dir, 'seals', 'static_regressors', 'pop.tif')
    p.static_regressor_paths['precip_mm'] = os.path.join(p.base_data_dir, 'seals', 'static_regressors', 'precip_mm.tif')

    # # Create list of paths that need to be downloaded
    # p.required_base_data_paths = []
    # p.required_base_data_paths.append(p.countries_iso3_path)
    # p.required_base_data_paths.append(p.base_year_lulc_path)
    # p.required_base_data_paths.append(p.calibration_parameters_source)
    # p.required_base_data_paths.append(p.coarse_projections_input_path)
    # p.required_base_data_paths.append(p.lulc_correspondence_path)
    # p.required_base_data_paths.append(p.coarse_correspondence_path)

    # p.required_base_data_paths.extend(p.static_regressor_paths.values())


    p.fine_resolution_degrees = hb.pyramid_compatible_resolutions[p.fine_resolution_arcseconds]
    p.coarse_resolution_degrees = hb.pyramid_compatible_resolutions[p.coarse_resolution_arcseconds]
    p.fine_resolution = p.fine_resolution_degrees
    p.coarse_resolution = p.coarse_resolution_degrees

    p.fine_ha_per_cell_path = p.ha_per_cell_paths[p.fine_resolution_arcseconds]
    p.fine_match_path = p.fine_ha_per_cell_path

    p.coarse_ha_per_cell_path = p.ha_per_cell_paths[p.coarse_resolution_arcseconds]
    p.coarse_match_path = p.coarse_ha_per_cell_path


    p.execute()


def project_aoi(p):
    """
    Generate the area of interest (AOI) of the current project based on the inputs defined in the run file.

    This task must be run first because it defines how all subsequent data will be extracted (based on the bounding box of the AOI)

    """ 
    download_urls = {}   
    # download_urls[p.countries_iso3_path] = p.countries_iso3_path.split(p.base_data_dir)[1].replace('\\', '/')
    # download_urls[p.ha_per_cell_paths[p.fine_resolution_arcseconds]] = p.ha_per_cell_paths[p.fine_resolution_arcseconds].split(p.base_data_dir)[1].replace('\\', '/')
    # download_urls[p.ha_per_cell_paths[p.coarse_resolution_arcseconds]] = p.ha_per_cell_paths[p.coarse_resolution_arcseconds].split(p.base_data_dir)[1].replace('\\', '/')
    p.countries_iso3_path
    p.countries_iso3_path = p.get_path(p.countries_iso3_path)
    p.ha_per_cell_coarse_path = p.get_path(p.ha_per_cell_ref_paths[p.coarse_resolution_arcseconds])
    p.ha_per_cell_fine_path = p.get_path(p.ha_per_cell_ref_paths[p.fine_resolution_arcseconds])
    
    # TODO This references something in initialize_project in seals. But, we only download the ones that are needed given the resolutions
    # p.ha_per_cell_paths[p.fine_resolution_arcseconds] = p.get_path(p.ha_per_cell_paths[p.fine_resolution_arcseconds])
 
    # for download_path, download_url in download_urls.items():
    #     if not hb.path_exists(download_path): # Check one last time to ensure that it wasn't added twice.
    #         cloud_utils.download_google_cloud_blob(p.input_bucket_name, download_url, p.data_credentials_path, download_path)
    
    
    # Note that here there is a little bit more logic outside the run_this block. But it only references the things that it assumes had been made sometime else.
    if isinstance(p.aoi, str):
        if p.aoi == 'global':
            p.aoi_path = p.countries_iso3_path
            p.aoi_label = 'global'
            p.bb_exact = hb.global_bounding_box
            p.bb = p.bb_exact

            ### TODO Start here. aoi_ha... is the clipped, but still need to have the global one seperate so it can download it.
            p.aoi_ha_per_cell_coarse_path = p.get_path(p.ha_per_cell_ref_paths[p.coarse_resolution_arcseconds])
            p.aoi_ha_per_cell_fine_path = p.get_path(p.ha_per_cell_ref_paths[p.fine_resolution_arcseconds])
        
        elif isinstance(p.aoi, str):
            if len(p.aoi) == 3: # Then it might be an ISO3 code. For now, assume so.
                p.aoi_path = os.path.join(p.cur_dir, 'aoi_' + str(p.aoi) + '.gpkg')
                p.aoi_label = p.aoi
            else: # Then it's a path to a shapefile.
                p.aoi_path = p.aoi
                p.aoi_label = os.path.splitext(os.path.basename(p.aoi))[0]

            for current_aoi_path in hb.list_filtered_paths_nonrecursively(p.cur_dir, include_strings='aoi'):
                if current_aoi_path != p.aoi_path:
                    raise NameError('There is more than one AOI in the current directory. This means you are trying to run a project in a new area of interst in a project that was already run in a different area of interest. This is not allowed! You probably want to create a new project directory and set the p = hb.ProjectFlow(...) line to point to the new directory.')
                

            if not hb.path_exists(p.aoi_path):
                hb.extract_features_in_shapefile_by_attribute(p.countries_iso3_path, p.aoi_path, 'iso3', p.aoi.upper())
            p.bb_exact = hb.spatial_projection.get_bounding_box(p.aoi_path)
            p.bb = hb.pyramids.get_pyramid_compatible_bb_from_vector_and_resolution(p.aoi_path, p.processing_resolution_arcseconds)
            p.aoi_ha_per_cell_fine_path = os.path.join(p.cur_dir, 'pyramids', 'aoi_ha_per_cell_fine.tif')
            p.aoi_ha_per_cell_coarse_path = os.path.join(p.cur_dir, 'pyramids', 'aoi_ha_per_cell_coarse.tif')
        else:
            p.bb_exact = hb.spatial_projection.get_bounding_box(p.aoi_path)
            p.bb = hb.pyramids.get_pyramid_compatible_bb_from_vector_and_resolution(p.aoi_path, p.processing_resolution_arcseconds)
            p.aoi_ha_per_cell_fine_path = os.path.join(p.cur_dir, 'pyramids', 'aoi_ha_per_cell_fine.tif')
            p.aoi_ha_per_cell_coarse_path = os.path.join(p.cur_dir, 'pyramids', 'aoi_ha_per_cell_coarse.tif')
    else:
        raise NameError('Unable to interpret p.aoi.')


    if p.run_this:

        if isinstance(p.aoi, str):

            if p.aoi == 'global':
                pass

            elif isinstance(p.aoi, str):
                if len(p.aoi) == 3:                     
                    pass
                else:
                    pass

                if not hb.path_exists(p.aoi_ha_per_cell_fine_path):
                    hb.create_directories(p.aoi_ha_per_cell_fine_path)
                    hb.clip_raster_by_bb(p.ha_per_cell_paths[p.fine_resolution_arcseconds], p.bb, p.aoi_ha_per_cell_fine_path)

                if not hb.path_exists(p.aoi_ha_per_cell_coarse_path):
                    hb.clip_raster_by_bb(p.ha_per_cell_paths[p.coarse_resolution_arcseconds], p.bb, p.aoi_ha_per_cell_coarse_path)

        else:
            raise NameError('Unable to interpret p.aoi.')

def build_task_tree_by_name(p, task_tree_name):
    full_task_tree_name = 'build_' + task_tree_name + '_task_tree'
    target_function = globals()[full_task_tree_name]
    print('Launching SEALS. Building task tree: ' + task_tree_name)

    target_function(p)


def build_magpie_seals_task_tree(p):

    # Define the project AOI
    p.project_aoi_task = p.add_task(project_aoi)
    
    p.magpie_task = p.add_task(magpie_integration.launch_magpie)
    
    # Process the IUCN-specific data to be used in SEALS
    p.biodiversity_task = p.add_task(seals_generate_base_data.biodiversity)
    p.kbas_task = p.add_task(seals_generate_base_data.kba, parent=p.biodiversity_task)
    p.star_task = p.add_task(seals_generate_base_data.star, parent=p.biodiversity_task)

    ##### FINE PROCESSED INPUTS #####    
    p.fine_processed_inputs_task = p.add_task(seals_generate_base_data.fine_processed_inputs)
    p.generated_kernels_task = p.add_task(seals_generate_base_data.generated_kernels, parent=p.fine_processed_inputs_task, creates_dir=False)
    p.lulc_clip_task = p.add_task(seals_generate_base_data.lulc_clip, parent=p.fine_processed_inputs_task, creates_dir=False)
    p.lulc_simplifications_task = p.add_task(seals_generate_base_data.lulc_simplifications, parent=p.fine_processed_inputs_task, creates_dir=False)
    p.lulc_binaries_task = p.add_task(seals_generate_base_data.lulc_binaries, parent=p.fine_processed_inputs_task, creates_dir=False)
    p.lulc_class_ha_task = p.add_task(seals_generate_base_data.lulc_class_ha, parent=p.fine_processed_inputs_task, creates_dir=False)
    p.lulc_convolutions_task = p.add_task(seals_generate_base_data.lulc_convolutions, parent=p.fine_processed_inputs_task, creates_dir=False)

    ##### COARSE CHANGE #####
    p.coarse_change_task = p.add_task(seals_process_coarse_timeseries.coarse_change, skip_existing=0)
    p.extraction_task = p.add_task(seals_process_coarse_timeseries.coarse_extraction, parent=p.coarse_change_task, run=1, skip_existing=0)
    p.coarse_simplified_task = p.add_task(seals_process_coarse_timeseries.coarse_simplified_proportion, parent=p.coarse_change_task, skip_existing=0)
    p.coarse_simplified_ha_task = p.add_task(seals_process_coarse_timeseries.coarse_simplified_ha, parent=p.coarse_change_task, skip_existing=0)
    p.coarse_simplified_ha_difference_from_previous_year_task = p.add_task(seals_process_coarse_timeseries.coarse_simplified_ha_difference_from_previous_year, parent=p.coarse_change_task, skip_existing=0)

    # IUCN SPECIFIC
    p.iucn_30by30_scenarios_task = p.add_task(seals_main.iucn_30by30_scenarios)     
    p.pa_zonal_sums_task = p.add_task(seals_main.pa_zonal_sums, parent=p.iucn_30by30_scenarios_task)
    p.ag_value_task = p.add_task(seals_main.ag_value, parent=p.iucn_30by30_scenarios_task)
    p.luh_seals_baseline_adjustment_task = p.add_task(seals_main.luh_seals_baseline_adjustment, parent=p.iucn_30by30_scenarios_task)
    p.coarse_simplified_projected_ha_difference_from_previous_year_task = p.add_task(seals_main.coarse_simplified_projected_ha_difference_from_previous_year, parent=p.iucn_30by30_scenarios_task)


    ##### ALLOCATION #####
    p.allocations_task = p.add_iterator(seals_main.allocations)
    p.allocation_zones_task = p.add_iterator(seals_main.allocation_zones, run_in_parallel=p.run_in_parallel, parent=p.allocations_task)
    p.allocation_task = p.add_task(seals_main.allocation, parent=p.allocation_zones_task, skip_existing=1)

    ##### STITCH ZONES #####
    p.stitched_lulc_simplified_scenarios_task = p.add_task(seals_main.stitched_lulc_simplified_scenarios)



def build_iucn_multiscenario_task_tree(p):

    # Define the project AOI
    p.project_aoi_task = p.add_task(project_aoi)
    
    # Process the IUCN-specific data to be used in SEALS
    p.biodiversity_task = p.add_task(seals_generate_base_data.biodiversity)
    p.kbas_task = p.add_task(seals_generate_base_data.kba, parent=p.biodiversity_task)
    p.star_task = p.add_task(seals_generate_base_data.star, parent=p.biodiversity_task)

    ##### FINE PROCESSED INPUTS #####    
    p.fine_processed_inputs_task = p.add_task(seals_generate_base_data.fine_processed_inputs)
    p.generated_kernels_task = p.add_task(seals_generate_base_data.generated_kernels, parent=p.fine_processed_inputs_task, creates_dir=False)
    p.lulc_clip_task = p.add_task(seals_generate_base_data.lulc_clip, parent=p.fine_processed_inputs_task, creates_dir=False)
    p.lulc_simplifications_task = p.add_task(seals_generate_base_data.lulc_simplifications, parent=p.fine_processed_inputs_task, creates_dir=False)
    p.lulc_binaries_task = p.add_task(seals_generate_base_data.lulc_binaries, parent=p.fine_processed_inputs_task, creates_dir=False)
    p.lulc_class_ha_task = p.add_task(seals_generate_base_data.lulc_class_ha, parent=p.fine_processed_inputs_task, creates_dir=False)
    p.lulc_convolutions_task = p.add_task(seals_generate_base_data.lulc_convolutions, parent=p.fine_processed_inputs_task, creates_dir=False)

    ##### COARSE CHANGE #####
    p.coarse_change_task = p.add_task(seals_process_coarse_timeseries.coarse_change, skip_existing=0)
    p.extraction_task = p.add_task(seals_process_coarse_timeseries.coarse_extraction, parent=p.coarse_change_task, run=1, skip_existing=0)
    p.coarse_simplified_task = p.add_task(seals_process_coarse_timeseries.coarse_simplified_proportion, parent=p.coarse_change_task, skip_existing=0)
    p.coarse_simplified_ha_task = p.add_task(seals_process_coarse_timeseries.coarse_simplified_ha, parent=p.coarse_change_task, skip_existing=0)
    p.coarse_simplified_ha_difference_from_previous_year_task = p.add_task(seals_process_coarse_timeseries.coarse_simplified_ha_difference_from_previous_year, parent=p.coarse_change_task, skip_existing=0)

    # IUCN SPECIFIC
    p.iucn_30by30_scenarios_task = p.add_task(seals_main.iucn_30by30_scenarios)     
    p.pa_zonal_sums_task = p.add_task(seals_main.pa_zonal_sums, parent=p.iucn_30by30_scenarios_task)
    p.ag_value_task = p.add_task(seals_main.ag_value, parent=p.iucn_30by30_scenarios_task)
    p.luh_seals_baseline_adjustment_task = p.add_task(seals_main.luh_seals_baseline_adjustment, parent=p.iucn_30by30_scenarios_task)
    p.coarse_simplified_projected_ha_difference_from_previous_year_task = p.add_task(seals_main.coarse_simplified_projected_ha_difference_from_previous_year, parent=p.iucn_30by30_scenarios_task)


    ##### ALLOCATION #####
    p.allocations_task = p.add_iterator(seals_main.allocations)
    p.allocation_zones_task = p.add_iterator(seals_main.allocation_zones, run_in_parallel=p.run_in_parallel, parent=p.allocations_task)
    p.allocation_task = p.add_task(seals_main.allocation, parent=p.allocation_zones_task, skip_existing=1)

    ##### STITCH ZONES #####
    p.stitched_lulc_simplified_scenarios_task = p.add_task(seals_main.stitched_lulc_simplified_scenarios)

    ##### VIZUALIZE EXISTING DATA #####
    p.visualization_task = p.add_task(seals_visualization_tasks.visualization)
    p.coarse_change_with_class_change_task = p.add_task(seals_visualization_tasks.coarse_change_with_class_change, parent=p.visualization_task)
    p.plot_full_change_matrices_task = p.add_task(seals_main.full_change_matrices, parent=p.visualization_task)
    p.plot_full_change_matrices_task = p.add_task(seals_visualization_tasks.full_change_matrices_pngs, parent=p.visualization_task)
    p.lulc_pngs_task = p.add_task(seals_visualization_tasks.lulc_pngs, parent=p.visualization_task)
    p.coarse_fine_with_report_task = p.add_task(seals_visualization_tasks.coarse_fine_with_report, parent=p.visualization_task)
    
    
    # For each class, plot the coarse and fine data
    p.create_full_change_matrices_task = p.add_task(seals_main.full_change_matrices, parent=p.visualization_task)
    
    # For each class, plot the coarse and fine data
    p.target_zones_matrices_task = p.add_task(seals_main.target_zones_matrices, parent=p.visualization_task)
    
    # For each class, plot the coarse and fine data
    p.plot_full_change_matrices_pngs_task = p.add_task(seals_visualization_tasks.full_change_matrices_pngs, parent=p.visualization_task)
    
    # For each class, plot the coarse and fine data
    p.plot_target_zones_matrices_pngs_task = p.add_task(seals_visualization_tasks.target_zones_matrices_pngs, parent=p.visualization_task)



