import sys, neo
import matplotlib.pyplot as plt

def load_neo_block(filename):
    """ Load data from file into Neo structure """
    with neo.get_io(filename) as io:
        return neo.load_block()

def plot_analogsignal(block, filename)
    """ Plot first AnalogSignal of Neo block """
    anasig = block.segments[0].analogsignals[0]
    plt.plot(anasig.times, anasig.magnitude, label=anasig.name)
    plt.legend(True)
    plt.xlabel('Time [{}]'.format(anasig.times.dimensionality.latex))
    plt.ylabel('Amplitude [{}]'.format(anasig.dimensionality.latex))
    plot.save_fig(filename)
    
if __name__=='__main__':
    neo_filename, plot_filename = sys.argv[1:]
    block = load_neo_block(neo_filename)
    plot_analogsignal(block, plot_filename)



