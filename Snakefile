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
    


            
rule compile_manuscript:
    input: get_all_latex_files(),
           join(LATEX, 'main.tex'),
           join(LATEX, 'thesis.bib'),
           join(LATEX, 'cover.pdf'),
           join(LATEX, 'figures', 'figures_complete.done') 
    output: join(LATEX,'main.pdf')
    params: latex=LATEX,
            latex_params = '-shell-escape -interaction=batchmode',
            # pdflatex --shell-escape is required for usage of svg package
            compiler = 'pdflatex'
    shell: '''
            cd {params.latex}
            {params.compiler} {params.latex_params} main.tex
            biber main
            {params.compiler} {params.latex_params} main.tex
            {params.compiler} {params.latex_params} main.tex'''        

    
rule generate_cover:
    input: join(LATEX, 'template', 'cover.tex')
    output: join(LATEX, 'cover.pdf')
    params: dir=LATEX
    shell: '''
           pdflatex -output-directory {params.dir} {input}
           '''
    
rule get_figures:
    input: figureworkflow(join(FIGURES[len(subworkdir)+1:], 'figures_complete.done'))
    output: join(LATEX,'figures','figures_complete.done')
    params:
        input=join(FIGURES,'.'),
        output=join(LATEX, 'figures')
    shell: '''
           cp -a {params.input} {params.output}
           '''

rule clean:
    params:
        tmp_figures = FIGURES,
        tmp_latex = expand(join(LATEX, '{f}'), f=['main.aux', 'main.bcf', 'main.locodeenv', 'main.lof', 'main.log', 'main.lot', 'main.out', 'main.pdf', 'main.run.xml', 'main.sta', 'main.toc', 'figures', '_minted-main', 'svg-inkscape'])
    shell: 
        '''
        rm -rf {params.tmp_figures}
        rm -rf {params.tmp_latex}
        '''
    
