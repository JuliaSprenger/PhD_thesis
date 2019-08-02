import os.path, glob
import odmltables as odt

def csv_to_odml(csv_file):
    """ Convert a score sheet from csv to odML format. """
    # initialize an OdmlTable object for handling metadata
    table = odt.OdmlTable()
    # specify headers used in the score sheet csv files (here: Section, Measure, Unit and Type)
    table.change_header(Path=1, PropertyName=2, Value=3, DataUnit=4, odmlDatatype=5)
    table.change_header_titles(Path='Section',PropertyName='Measure', DataUnit='Unit', odmlDatatype='Type')
    # load from csv format and save in odML format
    table.load_from_csv_table(csv_file)
    table.write2odml(csv_file[:-4] + '.odml')
    
def merge_odml_files(file1, file2, overwrite_values=False):
    """ Merge one odML file (file2) into another odML file (file1) """
    # load first odML file
    table1 = odt.OdmlTable(file1)
    # merge file2 into table1
    table1.merge(odt.OdmlTable(file2), overwrite_values=overwrite_values)
    # overwrite file1 with the merged score sheets
    table1.write2odml(file1)

def visualize_as_xls(odML_file):
    """ Generate an xls version of an odML file for visualization purposes """
    table = odt.OdmlXlsTable(odML_file)
    # optional: change the color options in the output table
    table.first_marked_style.fontcolor = 'dark_green'
    table.second_marked_style.fontcolor = 'dark_teal'
    table.highlight_defaults = True
    # write to xls format
    table.write2file(os.path.splitext(odML_file)[0] + '.xls')
    
def generate_overview(odML_file):
    """ Compare entries with same structure across an odML file """
    table = odt.compare_section_xls_table.CompareSectionXlsTable()
    table.load_from_file(odML_file)
    # specify all score sheet sections to be compared here
    table.choose_sections('Scores_2000-01-01', 'Scores_2000-01-02')
    # save to different odML file
    table.write2file(os.path.splitext(odML_file)[0] + '_overview.xls')
    
# extract all metadata files present in this metadata folder
folder = 'mymetadatacollection/'
source_files = sorted(glob.glob(folder + '/*.csv'))

# convert all source files
for source_file in source_files:
    csv_to_odml(source_file)
# merge score sheets into animal info document
for score_sheet in sorted(glob.glob(folder + '/score_sheet*.odml')):
    merge_odml_files(folder + '/animal_info.odml', score_sheet, overwrite_values=True)
    
# create visualization and comparison tables
visualize_as_xls(folder + '/animal_info.odml')
generate_overview(folder + '/animal_info.odml')