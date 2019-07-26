import numpy as np
import sys, neo
import quantities as pq
import matplotlib.pyplot as plt


def load_single_channel_data(data_location, selected_channel):
    """ Loading AnalogSignal and SpikeTrains from a single electrode. """
    # initialize the io and loade the Neo data structure in lazy mode
    io = neo.BlackrockIO(data_location)
    block = io.read_block(lazy=True)
    # filter to select spiketrains from specific channel
    spiketrains = block.filter(targdict={'channel_id': selected_channel})
    # extract corresponding AnalogSignal and trace id
    for analogsignal in block.segments[0].analogsignals:
        if selected_channel in analogsignal.array_annotations['channel_ids']:
            id = np.where(analogsignal.array_annotations['channel_ids'] == selected_channel)[0]
            break
    # load analog and spiking data for 10 seconds of recording time
    analog_data = analogsignal.load(channel_indexes=id, time_slice=(10 * pq.s, 20 * pq.s))
    spike_data = [st.load(time_slice=(10 * pq.s, 20 * pq.s)) for st in spiketrains]
    return analog_data, spike_data


def plot_data(analog_data, spike_datas, plot_location):
    """ Visualize a single AnalogSignal trace with multiple SpikeTrains """
    # parameters for axis scaling
    time_scale, voltage_scale = pq.s, pq.microvolt
    # plot single analogsignal and all spiketrain data
    plt.plot(analog_data.times.rescale(time_scale), analog_data.rescale(voltage_scale).magnitude, lw=1, label='AnalogSignal')
    ymax = max(analog_data.rescale(voltage_scale)).magnitude
    for spike_data in spike_datas:
        unit_id = spike_data.annotations['unit_id']
        plt.plot(spike_data.rescale(time_scale), np.ones_like(spike_data) * unit_id * ymax / 6, '|', ms=20, mew=1.5, label='Spikes Unit {}'.format(unit_id))
    # configure plot labels and add legend
    plt.xlabel('Time [{}]'.format(time_scale.dimensionality.latex))
    plt.ylabel('Voltage[{}]'.format(voltage_scale.dimensionality.latex))
    plt.legend(title='Channel {}'.format(analog_data.array_annotations['channel_ids'][0]), markerscale=0.4, title_fontsize=7, loc=1, prop={'size': 6})
    # export plot to svg format
    plt.savefig('{}.svg'.format(plot_location))


# Calling main functions to load data and plot data specified via command line arguments
data_location, selected_channel = sys.argv[1:]
channel_data = load_single_channel_data(data_location, int(selected_channel))
plot_data(*channel_data, data_location.split('/')[-1])
