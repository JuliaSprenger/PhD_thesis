configfile: "config.yaml"

import sys
import glob
import re
from os import listdir
from os.path import basename, join, splitext, normpath, abspath
from snakemake.utils import min_version

# to use this as a package
sys.path.append('.')

min_version("5.0")

DATALOC = config['data_location']
# writing data to user defined location if possible, otherwise use data location
if 'output_location' in config:
    OUTPUTLOC = config['output_location']
else:
    OUTPUTLOC = DATALOC
if 'gin_output_repo' in config:
    OUTPUTREPO = config['gin_output_repo']
else:
    OUTPUTREPO = None
# using all subfolders in data_location as sessions if not specified differently
session_regex = '\S\d{6}-\S{4}-\d{3}'
if 'sessions' in config:
    SESSIONS = config['sessions']
else:
    SESSIONS = [basename(dir) for dir  in listdir(DATALOC) if re.match(session_regex,basename(dir))]
# operation modes: full (use all data) and small (use only some data)
FLAVOURS = ['small', 'full'] # TODO: add full when running on server. This is to heavy for laptops

app_regex = "app_\w*"
MAPPS = [basename(dir)[:-3] for dir  in listdir('./scripts/metadata_apps')  if re.match(app_regex+'.py',basename(dir))]
DAPPS = [basename(dir)[:-3] for dir  in listdir('./scripts/data_apps')  if re.match(app_regex+'.py',basename(dir))]
APPS = MAPPS + DAPPS

# path to utility module
UTILDIR = 'scripts/utilities'

# descriptors always have to start with 'descriptor_*'
wildcard_constraints:
    descriptor="descriptor_\w*",
    session=session_regex,
    app=app_regex

ruleorder: integrate_app_results > integrate_descriptors > csv_to_odml

def get_avail_odml_descriptors(wildcards):
    ''' Returns a list of all potential odml descriptors for the session defined by wildcards'''
    csv_files = glob.glob(join(DATALOC, wildcards.session, 'descriptor_*.csv'))
    descriptors = [splitext(basename(f))[0] for f in csv_files]
    odml_files = [join(OUTPUTLOC, wildcards.session, 'descriptors', 'odMLs', f + '.odml') for f in descriptors]
    return odml_files

def get_recording_files(wildcards):
    ''' Return list of data files available for this session'''
    target_formats = ['.ccf', '.nev', '.ns2', '.ns6']
    files = [f for f in listdir(join(DATALOC, wildcards.session)) if splitext(f)[1] in target_formats]
    files = [join(DATALOC, wildcards.session, f) for f in files]
    return files

def get_recording_sets(wildcards):
    files = get_recording_files(wildcards)
    setnames = list(set([splitext(f)[0] for f in files]))
    return setnames


rule all:
    input:
        [join(OUTPUTLOC, session, session + '_{}.nix'.format(flavour))
        for session in SESSIONS for flavour in FLAVOURS]


rule clean:
    params:
        output_dir = OUTPUTLOC
    shell:
        '''
        rm -r {params.output_dir}
        '''

############ METADATA HANDLING #####################

rule all_descriptors:
    input:
        [join(OUTPUTLOC, session, 'descriptors', 'odMLs', 'descriptor_session_integrated.odml') for session in
        SESSIONS]

rule integrate_descriptors:
    input:
        get_avail_odml_descriptors,
        main_odml = join(OUTPUTLOC, '{session}', 'descriptors', 'odMLs', 'descriptor_session.odml'),
        script = 'scripts/utilities/app_integrate_descriptors.py'
    output:
        full_odml = join(OUTPUTLOC, '{session}', 'descriptors', 'odMLs', 'descriptor_session_integrated.odml')
    conda:
        'envs/metadata_env.yaml'
    shell:
        'python {input.script} {input.main_odml}'

rule csv_to_odml:
    input:
        join('{folder}', 'odMLs', 'odml.xsl'),
        csv_file = join('{folder}', 'csv', '{filename}.csv'),
    output:
        join('{folder}', 'odMLs', '{filename}.odml')
    conda:
        'envs/metadata_env.yaml'
    shell:
        'python scripts/utilities/app_csv_to_odml.py {input.csv_file} {output}'

rule copy_descriptors:
    input:
        join(DATALOC, '{session}', '{descriptor}.csv')
    output:
        join(OUTPUTLOC, '{session}', 'descriptors', 'csv', '{descriptor}.csv')
    shell:
        'cp {input} {output}'

rule add_odML_style_sheet:
    output:
        join('{folder}', 'odml.xsl')
    params:
        session_folder = join('{folder}')
    shell:
        '''
        cd {params.session_folder}
        wget --tries=10 https://raw.githubusercontent.com/G-Node/odml-terminologies/master/v1.1/odml.xsl
        '''

########## ENRICHMENT AND APPS ####################

rule all_apps:
    input:
        [join(OUTPUTLOC, session, 'app_stats', 'preprocessing_complete.done') for session in SESSIONS]


rule run_all_preprocessing_apps:
    input:
        [join(OUTPUTLOC, '{session}', 'app_stats', a + '.done') for a in MAPPS+DAPPS]
    output:
        join(OUTPUTLOC, '{session}', 'app_stats', 'preprocessing_complete.done')
    shell:
        'touch {output}'


rule run_metadata_app:
    input:
        script = 'scripts/metadata_apps/{app}.py',
        original_data = join(DATALOC, '{session}'),
        utils = UTILDIR,
    output:
        join(OUTPUTLOC, '{session}', 'app_stats', '{app}.done'),
        csv_path = join(OUTPUTLOC, '{session}', 'app_results', 'csv', '{app}.csv')
    conda:
        'envs/metadata_env.yaml'
    shell:
        '''
        export PYTHONPATH={input.utils}
        python {input.script} {input.original_data} {output.csv_path}
        touch {output}
        '''

rule run_data_app:
    input:
        script = 'scripts/data_apps/{app}.py',
        original_data = join(DATALOC, '{session}'),
        nix_data = join(OUTPUTLOC, '{session}', '{session}_original.nix')
    output:
        join(OUTPUTLOC, '{session}', 'app_stats', '{app}.done'),
        csv_path = join(OUTPUTLOC, '{session}', 'app_results', 'csv', '{app}.csv')
    conda:
        'envs/metadata_env.yaml'
    shell:
        '''
        python {input.script} {input.original_data} {input.nix_data} {output.csv_path}
        touch {output}
        '''

rule integrate_app_results:
    input:
        join(OUTPUTLOC, '{session}', 'app_stats', 'preprocessing_complete.done'),
        [join(OUTPUTLOC, '{session}', 'app_results', 'odMLs', a + '.odml') for a in APPS],
        script = 'scripts/utilities/app_integrate_odmls.py'
    output:
        full_odml = join(OUTPUTLOC, '{session}', 'app_results', 'odMLs', 'preprocessing_integrated.odml')
    params:
        tmp_odml = join(OUTPUTLOC, '{session}', 'app_results', 'odMLs', 'preprocessing.odml')
    conda:
        'envs/metadata_env.yaml'
    shell:
        '''
        python {input.script} {params.tmp_odml}
        '''

rule integrate_descriptors_and_app_results:
    input:
        file1 = join(OUTPUTLOC, '{session}', 'app_results', 'odMLs', 'preprocessing_integrated.odml'),
        file2 = join(OUTPUTLOC, '{session}', 'descriptors', 'odMLs', 'descriptor_session_integrated.odml')
    output:
        join(OUTPUTLOC, '{session}', 'metadata_complete.odml')
    params:
        tmp_folder = join(OUTPUTLOC, '{session}', 'tmp')
    conda:
        'envs/metadata_env.yaml'
    shell:
        '''
        mkdir {params.tmp_folder}
        cp {input.file1} {params.tmp_folder}
        cp {input.file2} {params.tmp_folder}
        python scripts/utilities/app_integrate_odmls.py {params.tmp_folder}/metadata_complete.odml
        cp {params.tmp_folder}/metadata_complete_integrated.odml {output}
        rm -r {params.tmp_folder}
        '''


########## DATA HANDLING ###################

rule data_to_nix:
    input:
        get_recording_files,
        utils = UTILDIR
    output:
        join(OUTPUTLOC, '{session}', '{session}' + '_original.nix')
    params:
        data_sets = get_recording_sets
    conda:
        'envs/metadata_env.yaml'
    shell:
        '''
export PYTHONPATH={input.utils}
#!/bin/bash
a='{params.data_sets}'
for s in {params.data_sets}; do
    python scripts/utilities/app_data_to_nix.py $s.nev {output}
done
        '''




################## DATA & METADATA INTEGRATION ################

rule integrate_metadata:
    input:
        datafile = join(OUTPUTLOC, '{session}', '{session}_original.nix'),
        metadatafile = join(OUTPUTLOC, '{session}', 'metadata_complete.odml')
    output:
        touch(join(OUTPUTLOC, '{session}', 'odmlINnix.done')),
        datafile = join(OUTPUTLOC, '{session}', '{session}.nix'),
    conda:
        'envs/metadata_env.yaml'
    shell:
        '''
        cp {input.datafile} {output.datafile}
        python scripts/utilities/app_integrate_metadata.py {input.metadatafile} {output.datafile}
        '''

rule link_metadata:
    input:
        join(OUTPUTLOC, '{session}', 'odmlINnix.done')
    output:
        touch(join(OUTPUTLOC, '{session}', 'linkedNix.done'))
    conda:
        'envs/metadata_env.yaml'
    params:
        nixfile = join(OUTPUTLOC, '{session}', '{session}.nix')
    shell:
        '''
        python scripts/utilities/app_link_nix.py {params.nixfile}
        '''



################# DATA REDUCTION (FLAVOURING) ###################

rule create_small: # TODO: This is a dummy implementation and needs to be replaced.
    input:
        join(OUTPUTLOC, '{session}', 'linkedNix.done'),
        script = 'scripts/utilities/app_reduce_to_small.py',
        datafile = join(OUTPUTLOC, '{session}', '{session}.nix')
    output:
        join(OUTPUTLOC, '{session}', '{session}_small.nix')
    conda:
        'envs/metadata_env.yaml'
    shell:
        '''
        python {input.script} {input.datafile} {output}
        '''


rule create_full:
    input:
        join(OUTPUTLOC, '{session}', 'linkedNix.done'),
        datafile = join(OUTPUTLOC, '{session}', '{session}.nix')
    output:
        join(OUTPUTLOC, '{session}', '{session}_full.nix')
    shell:
        '''
        ln -s {input.datafile} {output}
        '''


############### DEPLOYMENT ###################################

# this assumes git-annex to be installed
rule setup_gin:
    output:
        join(OUTPUTLOC, 'software', 'gin')
    params:
        software_folder = join(OUTPUTLOC, 'software')
    shell:
        '''
        cd {params.software_folder}
        wget --tries=10 -O gin.deb https://web.gin.g-node.org/G-Node/gin-cli-releases/raw/master/gin-cli-latest.deb
        mkdir tmp
        dpkg -x gin.deb ./installs
        ln ./installs/opt/gin/bin/gin ./gin
        rm gin.deb
        '''

# TBRemoved
'''
cd {params.software_folder}
wget --tries=10 -O gin.tar.gz https://web.gin.g-node.org/G-Node/gin-cli-releases/raw/master/gin-cli-latest-linux-amd64.tar.gz
tar xzf {params.software_folder}/gin.tar.gz
rm {params.software_folder}/gin.tar.gz
# PATH={params.software_folder}:$PATH
'''

rule initialize_repo:
    input:
        join(OUTPUTLOC, 'software', 'gin')
    output:
        join(OUTPUTLOC, '.git')
    params:
        gin = join(OUTPUTLOC, 'software', 'gin')
    shell:
        '''
        cd {OUTPUTLOC}
        {params.gin} get {OUTPUTREPO}
        '''


rule upload_to_gin: # TODO: This is incomplete.
    input:
        metadatafile = join(OUTPUTLOC, '{session}', 'metadata_complete.odml'),
        datafiles = [join(OUTPUTLOC, '{session}', '{session}' + '_{flavour}.nix'.format(flavour=f)) for f in FLAVOURS],
        gin = join(OUTPUTLOC, 'software', 'gin'),
        repo = join(OUTPUTLOC, '.git')
    params:
        gin = join(OUTPUTLOC, 'software', 'gin')
    output:
        touch(join(OUTPUTLOC, '{session}', 'app_stats', 'uploaded_to_gin.done'))
    shell:
        '''
        {params.gin} upload {input.metadatafile}
        '''


