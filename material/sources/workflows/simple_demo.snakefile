# define rule order to first use simple rules if possible
rule_order:
    simple_creation_rule > create_file > simple_copy_rule > copy_file

# simple rules using explicit file names
rule simple_creation_rule:
   output: 'file.md'
   shell: 'touch {output}'
   
rule simple_copy_rule:
    input: 'file.md'
    output: 'file.txt'
    shell: 'cp {input} {output}'
    
# flexible rules using wildcards to handle file names
rule create_file:
    output: '{filename}.txt'
    shell: 'touch {output}'
   
rule copy_file:
    input: '{filename}.md'
    output: '{filename}.txt'
    shell: 'cp {input} {output}'

