import sys, numpy, neo
import quantities as pq

def generate_neo_data():
    """ Generate Neo block with single AnalogSignal with random data """
    block = neo.Block(name='generated data block')
    segment = neo.Segment(name='generated data segment')
    analogsignal = neo.AnalogSignal(numpy.random.random(100)*pq.V,
                                    sampling_rate=1*pq.kHz,
                                    name='numpy random data')
    block.segments.append(segment)
    segment.analogsignals.append(analogsignal)
    
    return block
    
def save_neo_block(block, filename):
    """ Save Neo block to disc at filename"""
    with neo.get_io(filename) as io:
        io.write_block(block)
    
if __name__=='__main__':
    filename = sys.argv[1]
    block = generate_neo_data()
    save_neo_block(block, filename)
    
