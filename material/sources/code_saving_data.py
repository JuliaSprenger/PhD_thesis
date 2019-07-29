import sys, neo, odml, nixio
from nixodmlconverter.convert import nixwrite, get_odml_doc, nix_to_odml_recurse

def save_neo_to_nix(block, nix_filename, **kwargs):
    """ save Neo structure in Nix format """
    io = neo.NixIO(nix_filename, **kwargs)
    io.write_block(block)

def save_odml_to_nix(odml_filename, nix_filename, **kwargs):
    """ save odml tree in Nix format """
    odml_doc = odml.load(odml_filename)
    nixwrite(odml_doc, nix_filename, **kwargs)

def load_odml_from_nix(nix_filename):
    """ load odml document from nix """
    with nixio.File.open(nix_filename, nixio.FileMode.ReadOnly) as nix_file:
        odml_doc, nix_sections = get_odml_doc(nix_file)
        nix_to_odml_recurse(nix_sections, odml_doc)
    return odml_doc

def load_neo_block_from_nix(nix_filename):
    """ loading neo structure from nix using rawio implementation """
    io = neo.NixIO(nix_filename)
    return io.read_block()

# extracting command line parameters and loading original Blackrock data
data_location, odml_filename, nix_filename = sys.argv[1:]
io = neo.BlackrockIO(data_location)
block = io.read_block(lazy=True)

# save odml and neo block in single nix file
save_neo_to_nix(block, nix_filename, mode='ow')
save_odml_to_nix(odml_filename, nix_filename, mode='overwrite metadata')

# extract odml document and neo block from nix file
odml_document = load_odml_from_nix(nix_filename)
block2 = load_neo_block_from_nix(nix_filename)






