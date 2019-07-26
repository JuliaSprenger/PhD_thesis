import sys, neo, odml

def pretty_print_dict(dictionary):
    """Print individual entries of a dictionary in truncated, individual lines"""
    for k, v in dictionary.items():
        res = '  {}: {}'.format(k, str(v))
        print(res[:75] + '...' if len(res) > 75 else res)

def print_annotations(obj, mode='annotations'):
    """Print annotations / array_annotations of a Neo object"""
    print(type(obj).__name__)
    if mode == 'annotations':
        pretty_print_dict(obj.annotations)
    elif mode == 'array_annotations':
        pretty_print_dict(obj.array_annotations)
    else:
        raise ValueError('Unknown annotation type {}'.format(mode))

def print_annotation_examples(block):
    """ Print some example annotations & array annotations """
    print('Annotations\n---------------')
    print_annotations(block)
    print_annotations(block.segments[0].spiketrains[0])
    print_annotations(block.channel_indexes[0])
    print('Array Annotations\n--------------------')
    print_annotations(block.segments[0].analogsignals[-1], mode='array_annotations')

def generate_annotations_from_odml(block, odml_filename):
    """ Extract mapping information from the odml sheet and  add it as array annotation to the data """
    # loading odml file and extract electrode id mapping
    doc = odml.load(odml_filename)
    electrode_secs = doc.itersections(filter_func=lambda x: x.name.startswith('Electrode_'))
    mapping = {sec.properties['ID'].values[0]: sec.properties['ConnectorAlignedID'].values[0] for sec in electrode_secs}

    # extract id present in neo block and create new annotation based on mapping
    original_ids = block.segments[0].analogsignals[-1].array_annotations['channel_ids']
    connector_ids = [mapping[oid] for oid in original_ids]
    block.segments[0].analogsignals[-1].array_annotate(connector_aligned_ids=connector_ids)

# extracting command line parameters, loading data and print default annotations
data_location, odml_filename = sys.argv[1:]
io = neo.BlackrockIO(data_location)
block = io.read_block()
print_annotation_examples(block)
# extract metadata from odml, add new annotations and print annotations
generate_annotations_from_odml(block, odml_filename)
print('\n\nArray annotations AFTER annotation generation')
print_annotations(block.segments[0].analogsignals[-1], mode='array_annotations')
