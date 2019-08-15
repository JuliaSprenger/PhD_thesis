configfile: 'config.yaml'
data_format = config['data_format']

# descriptors always have to start with 'descriptor_*'
wildcard_constraints:
    data_ext=data_format

# plot example data in svg and png format
rule all:
    input: expand('data.{ext}', ext=['png','svg'])

# run python script to generate data
rule create_data:
    output: 'data.{data_ext}'
    conda: 'data_generation_environment.yaml'
    shell: 'python generate_data.py {output}'
    
# visualize data
rule plot_data:
    input: '{{filename}}.{data_ext}'.format(data_ext=data_format)
    output: '{filename}.{ext}'
    conda: 'envs/plotting_environment.yaml'
    shell: 'python plot_data.py {input} {output}'
    
