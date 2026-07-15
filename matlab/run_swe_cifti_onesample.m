function run_swe_cifti_onesample()

%% 1. USER CONFIGURATION

cfg.spm_dir = '/home/groups/markett/software/matlab/spm12';
cfg.swe_dir = '/home/noemerka/toolboxes/SwE-toolbox';

cfg.input_dir   = '/home/groups/markett/hcpcrit/hcp_test';
cfg.output_dir  = '/home/noemerka/criticality_project/swe_results/test';
cfg.file_pattern = '*.dscalar.nii';

cfg.left_surface  = '/home/noemerka/criticality_project/surfaces/S1200.L.midthickness_MSMAll.32k_fs_LR.surf.gii';
cfg.right_surface = '/home/noemerka/criticality_project/surfaces/S1200.R.midthickness_MSMAll.32k_fs_LR.surf.gii';
cfg.left_area     = '/home/noemerka/criticality_project/surfaces/S1200.L.midthickness_MSMAll.32k_fs_LR_area.func.gii';
cfg.right_area    = '/home/noemerka/criticality_project/surfaces/S1200.R.midthickness_MSMAll.32k_fs_LR_area.func.gii';

cfg.swe_small_sample_adjustment = 4;
cfg.dof_method = 3;

cfg.run_wild_bootstrap = true;
cfg.n_bootstraps = 999;
cfg.wb_small_sample_adjustment = 4;
cfg.wb_swe_type = 0;
cfg.inference_type = 'voxelwise';

cfg.allow_existing_output_directory = true;

%% 2. INITIALISE

fprintf('\n============================================================\n');
fprintf('Initialising SPM and SwE\n');
fprintf('============================================================\n');

addpath(cfg.spm_dir);
addpath(cfg.swe_dir);
spm('Defaults', 'fMRI');
spm_jobman('initcfg');

required_functions = {'swe_run_smodel','swe_run_rmodel','swe_read_cifti_info','swe_cp'};
for i = 1:numel(required_functions)
    assert(exist(required_functions{i}, 'file') == 2, ...
        'Required SwE function not found: %s', required_functions{i});
end
fprintf('SPM and SwE initialised OK.\n');

%% 3. VALIDATE FILES

assert(isfolder(cfg.input_dir),    'Input directory not found: %s', cfg.input_dir);
assert(isfile(cfg.left_surface),   'Left surface not found: %s',    cfg.left_surface);
assert(isfile(cfg.right_surface),  'Right surface not found: %s',   cfg.right_surface);
assert(isfile(cfg.left_area),      'Left area not found: %s',       cfg.left_area);
assert(isfile(cfg.right_area),     'Right area not found: %s',      cfg.right_area);

%% 4. OUTPUT DIRECTORY

if ~isfolder(cfg.output_dir)
    mkdir(cfg.output_dir);
end

existing_swe_mat = fullfile(cfg.output_dir, 'SwE.mat');
if isfile(existing_swe_mat)
    error('SwE.mat already exists in output dir. Remove it first: %s', existing_swe_mat);
end

%% 5. FIND INPUT FILES

file_listing = dir(fullfile(cfg.input_dir, cfg.file_pattern));
assert(~isempty(file_listing), 'No files found matching: %s', cfg.file_pattern);
[~, sort_index] = sort({file_listing.name});
file_listing = file_listing(sort_index);
n_scans = numel(file_listing);
scans = cell(n_scans, 1);
for i = 1:n_scans
    scans{i} = fullfile(file_listing(i).folder, file_listing(i).name);
end
fprintf('\nFound %d CIFTI files.\n', n_scans);
fprintf('First: %s\n', scans{1});
fprintf('Last:  %s\n', scans{end});

%% 6. INSPECT CIFTI

fprintf('\nInspecting first CIFTI file...\n');
[cifti_surfaces, cifti_volume, cifti_volumes] = swe_read_cifti_info(scans{1});
fprintf('Surface structures: %d\n', numel(cifti_surfaces));
fprintf('CIFTI inspection OK.\n');

%% 7. OBSERVATION STRUCTURE

subjects = (1:n_scans)';
visits   = ones(n_scans, 1);
groups   = ones(n_scans, 1);

%% 8. DESIGN MATRIX

intercept      = ones(n_scans, 1);
design_matrix  = intercept;
design_names   = {'Intercept'};
t_contrast     = 1;

fprintf('\nDesign: %d observations, intercept-only, one-sample T contrast.\n', n_scans);

%% 9. BUILD JOB

job = struct();
job.dir   = {cfg.output_dir};
job.scans = scans;

job.ciftiAdditionalInfo.ciftiGeomFile(1).brainStructureLabel = 'CIFTI_STRUCTURE_CORTEX_LEFT';
job.ciftiAdditionalInfo.ciftiGeomFile(1).geomFile  = {cfg.left_surface};
job.ciftiAdditionalInfo.ciftiGeomFile(1).areaFile  = {cfg.left_area};

job.ciftiAdditionalInfo.ciftiGeomFile(2).brainStructureLabel = 'CIFTI_STRUCTURE_CORTEX_RIGHT';
job.ciftiAdditionalInfo.ciftiGeomFile(2).geomFile  = {cfg.right_surface};
job.ciftiAdditionalInfo.ciftiGeomFile(2).areaFile  = {cfg.right_area};

job.ciftiAdditionalInfo.volRoiConstraint = 1;

job.type.modified.groups  = groups;
job.type.modified.visits  = visits;
job.type.modified.ss      = cfg.swe_small_sample_adjustment;
job.type.modified.dof_mo  = cfg.dof_method;

job.subjects = subjects;

job.cov        = struct([]);
job.cov(1).c     = intercept;
job.cov(1).cname = 'Intercept';
job.multi_cov  = struct([]);

job.masking.tm.tm_none    = 1;
job.masking.im            = 1;
job.masking.em            = {''};

job.WB.WB_yes.WB_ss  = cfg.wb_small_sample_adjustment;
job.WB.WB_yes.WB_nB  = cfg.n_bootstraps;
job.WB.WB_yes.WB_SwE = cfg.wb_swe_type;
job.WB.WB_yes.WB_stat.WB_T.WB_T_con = t_contrast;
job.WB.WB_yes.WB_infType.WB_voxelwise = 0;

job.globalc.g_omit            = 1;
job.globalm.gmsca.gmsca_no    = 1;
job.globalm.glonorm           = 1;

%% 10. SPECIFY MODEL

fprintf('\n============================================================\n');
fprintf('Specifying SwE model\n');
fprintf('============================================================\n');

original_directory = pwd;
try
    swe_run_smodel(job);
catch ME
    cd(original_directory);
    rethrow(ME);
end
cd(original_directory);

swe_mat = fullfile(cfg.output_dir, 'SwE.mat');
assert(isfile(swe_mat), 'SwE.mat was not created: %s', swe_mat);
fprintf('SwE.mat created: %s\n', swe_mat);

%% 11. ESTIMATE MODEL

fprintf('\n============================================================\n');
fprintf('Estimating SwE model\n');
fprintf('============================================================\n');

run_job.des = {swe_mat};
try
    swe_run_rmodel(run_job);
catch ME
    cd(original_directory);
    rethrow(ME);
end
cd(original_directory);

%% 12. DONE

fprintf('\n============================================================\n');
fprintf('Completed. Output in:\n%s\n', cfg.output_dir);
output_listing = dir(cfg.output_dir);
for i = 1:numel(output_listing)
    if ~output_listing(i).isdir
        fprintf('  %s\n', output_listing(i).name);
    end
end
fprintf('\nDone.\n');

end
