configfile: 'config.yaml'
print(config)
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
    conda: 'data_generation_environment.yml'
    shell: 'python generate_data.py {output}'
    
# visualize data
rule plot_data:
    input: '{{filename}}.{data_ext}'
    output: '{filename}.{ext}'
    params: format = data_format
    conda: 'plotting_environment.yml'
    shell: 'python plot_data.py {input} {output}'
    
