import sys
from os.path import join
import glob
import csv

def combine_files(filename_list):
    for filename in filename_list:
        years =

if __name__=='__main__':
    data_folder, output_filename = sys.argv[1:]
    files = glob.glob(join(data_folder, 'timeline*.csv'))
    combine_files(files)