snakemake --use-conda
snakemake --dag | dot -Tsvg > dag.svg
