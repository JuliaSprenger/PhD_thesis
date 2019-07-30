from os.path import join
import glob

configfile: "config.yml"

FIGURES = config['figures']
CODE = config['code']
LATEX = config['latex']

subworkdir = 'material'

def get_all_latex_files():
    return glob.glob(LATEX + '/**/*.tex', recursive=True)


subworkflow figureworkflow:
    workdir:
        subworkdir
    snakefile:
        join(subworkdir,"Snakefile")
    

# pdflatex --shell-escape is required for usage of svg package


rule compile_manuscript:
    input: get_all_latex_files(),
           join(LATEX, 'main.tex'),
           join(LATEX, 'thesis.bib'),
           join(LATEX, 'figures', 'figures_complete.done') 
    output: join(LATEX,'main.pdf')
    params: latex=LATEX
    shell: '''
            cd {params.latex}
            pdflatex --shell-escape main.tex'''
            
rule compile_manuscript4:
    input: get_all_latex_files(),
           join(LATEX, 'main.tex'),
           join(LATEX, 'thesis.bib'),
           join(LATEX, 'figures', 'figures_complete.done') 
    output: join(LATEX,'main.pdf')
    params: latex=LATEX,
            latex_params = '-shell-escape -interaction=nonstopmode'
    shell: '''
            cd {params.latex}
            latex {params.latex_params} main.tex
            bibtex main.tex
            latex {params.latex_params} main.tex
            latex {params.latex_params} main.tex'''        

    
rule get_figures:
    input: figureworkflow(join(FIGURES[len(subworkdir)+1:], 'figures_complete.done'))
    output: join(LATEX,'figures','figures_complete.done')
    params:
        input=join(FIGURES,'.'),
        output=join(LATEX, 'figures')
    shell: '''echo {params.input}
            echo {params.output}
            cp -a {params.input} {params.output}'''

rule clean:
    params:
        tmp_figures = FIGURES,
        tmp_latex = expand(join(LATEX, '{f}'), f=['main.aux', 'main.bcf', 'main.locodeenv', 'main.lof', 'main.log', 'main.lot', 'main.out', 'main.pdf', 'main.run.xml', 'main.sta', 'main.toc', 'figures', '_minted-main', 'svg-inkscape'])
    shell: 
        '''
        rm -rf {params.tmp_figures}
        rm -rf {params.tmp_latex}
        '''
    
