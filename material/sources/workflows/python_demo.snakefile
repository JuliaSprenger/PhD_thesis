configfile: 'config.yaml'
# extract neo data format to use from configuration
data_format = config['data_format']

# restrict the data extension to use for 
wildcard_constraints:
    data_ext=data_format

# plot example data in svg and png format
rule all:
    input: expand('data.{ext}', ext=['png','svg'])

# run python script to generate data
rule create_data:
    output: 'data.{data_ext}'
    conda: 'envs/data_generation_environment.yaml'
    shell: 'python generate_data.py {output}'
    
# visualize data
rule plot_data:
    input: '{{filename}}.{dext}'.format(dext=data_format)
    output: '{filename}.{ext}'
    conda: 'envs/plotting_environment.yaml'
    shell: 'python plot_data.py {input} {output}'
    
