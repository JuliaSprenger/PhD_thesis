from os.path import join
import glob

configfile: "config.yml"

FIGURES = config['figures']
CODE = config['code']
LATEX = config['latex']

def get_all_latex_files():
    return glob.glob(LATEX + '/**/*.tex', recursive=True)

print(get_all_latex_files())

subworkflow figureworkflow:
    workdir:
        "figures"
    snakefile:
        "figures/Snakefile"
    

# pdflatex --shell-escape is required for usage of svg package

rule compile_manuscript:
    input: get_all_latex_files(),
           join(LATEX, 'thesis.bib'),
           join(LATEX, 'figures', 'figures_complete.done') 
    output: LATEX + 'main.pdf'
    params: latex=LATEX
    shell: '''
            cd {params.latex}
            pdflatex --shell-escape main.tex'''
    
rule get_figures:
    input: figureworkflow(join(FIGURES.replace('figures/',''), 'figures_complete.done'))
    output: join(LATEX,'figures','figures_complete.done')
    params:
        input=FIGURES + '/.',
        output=join(LATEX, 'figures')
    shell: '''echo {params.input}
            echo {params.output}
            cp -a {params.input} {params.output}'''
  
