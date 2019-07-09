from os.path import join
import glob

configfile: "config.yml"

FIGURES = config['figures']
CODE = config['code']
LATEX = config['latex']

#include: './figures/Snakefile'

subworkflow figureworkflow:
    workdir:
        "figures"
    snakefile:
        "figures/Snakefile"
    

rule compile_manuscript:
    input: LATEX + 'main.tex',
           join(LATEX, 'figures', 'figures_complete.done') 
    output: LATEX + 'main.pdf'
    shell: 'xelatex {input}'
    
rule get_figures:
    input: figureworkflow(join(FIGURES.replace('figures/',''), 'figures_complete.done'))
    output: join(LATEX,'figures','figures_complete.done')
    params:
        input=FIGURES + '/.',
        output=join(LATEX, 'figures')
    shell: '''echo {params.input}
            echo {params.output}
            cp -a {params.input} {params.output}'''
  
