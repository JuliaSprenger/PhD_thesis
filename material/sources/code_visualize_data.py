import neo
import quantities as pq
import matplotlib.pyplot as plt
# initializing the io as a context manager

def get_single_channel_data():
    with neo.BlackrockIO('demo_dataset_folder') as io:
        # loading the neo data structure in lazy mode
        block = io.read_block(lazy=True)

        print('Block:', block)

        # filter to select a data object
        analog_signal = block.filter(filt_dict={'name':'anasig1'}, object='AnalogSignal')[0]

        # load data from specific time into memory
        analog_data = analog_signal.load(time_slice=(0*pq.s,10*pq.s))

        # accessing corresponding spiketrains
        spike_data = analog_signal.channel_index.spiketrains

        return analog_data, spike_data


def plot_data(analogsignal, spiketrain):
    # generate plot of the data
    figure = plt.figure()
    plt.plot(analog_data.times, analog_data, label=analog_data.name)
    plt.plot(spike_data, np.ones_like(spike_data), '|')
    plt.xlabel('time [{}]'.format(spike_data.times.dimensionality.latex))
    plt.ylabel('voltage[{}]'.format(analog_data.dimensionality.latex))
    plt.savefig('demo_dataset_folder/{}_visualization.svg'.format(analog_data.name))

data = get_single_channel_data()
plot_data(data)