from os.path import join
import glob

configfile: "config.yml"

FIGURES = config['figures']
CODE = config['code']
LATEX = config['latex']

subworkdir = 'material'

def get_all_latex_files():
    return glob.glob(LATEX + '/**/*.tex', recursive=True)

print(get_all_latex_files())

subworkflow figureworkflow:
    workdir:
        subworkdir
    snakefile:
        join(subworkdir,"Snakefile")
    

# pdflatex --shell-escape is required for usage of svg package

rule compile_manuscript:
    input: get_all_latex_files(),
           join(LATEX, 'thesis.bib'),
           join(LATEX, 'figures', 'figures_complete.done') 
    output: join(LATEX,'main.pdf')
    params: latex=LATEX
    shell: '''
            cd {params.latex}
            pdflatex --shell-escape main.tex'''
    
rule get_figures:
    input: figureworkflow(join(FIGURES[len(subworkdir)+1:], 'figures_complete.done'))
    output: join(LATEX,'figures','figures_complete.done')
    params:
        input=join(FIGURES,'.'),
        output=join(LATEX, 'figures')
    shell: '''echo {params.input}
            echo {params.output}
            cp -a {params.input} {params.output}'''
  
