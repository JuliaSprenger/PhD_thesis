# -*- coding: utf-8 -*-
"""
Example code for loading and processing of a recording of the reach-
to-grasp experiments conducted at the Institute de Neurosciences de la Timone
by Thomas Brochier and Alexa Riehle.

Authors: Julia Sprenger, Lyuba Zehl, Michael Denker


Copyright (c) 2017, Institute of Neuroscience and Medicine (INM-6),
Forschungszentrum Juelich, Germany
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.
* Neither the names of the copyright holders nor the names of the contributors
may be used to endorse or promote products derived from this software without
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

# This loads the Neo and odML libraries shipped with this code. For production
# use, please use the newest releases of odML and Neo.
import load_local_neo_odml_elephant

import os

import numpy as np
import matplotlib.pyplot as plt

import quantities as pq

from neo import Block, Segment
from elephant.signal_processing import butter

from reachgraspio import reachgraspio
from neo_utils import add_epoch, cut_segment_by_epoch, get_events


# =============================================================================
# Load data
#
# As a first step, we partially load the data file into memory as a Neo object.
# =============================================================================

# Specify the path to the recording session to load, eg,
# '/home/user/l101210-001'
session_name = os.path.join('..', 'datasets', 'i140703-001')
# session_name = os.path.join('..', 'datasets', 'l101210-001')
odml_dir = os.path.join('..', 'datasets')

# Open the session for reading
session = reachgraspio.ReachGraspIO(session_name, odml_directory=odml_dir)

# Read the first 300s of data (time series at 1000Hz (ns2) and 30kHz (ns6)
# scaled to units of voltage, sorted spike trains, spike waveforms and events)
# from electrode 62 of the recording session and return it as a Neo Block. The
# time shift of the ns2 signal (LFP) induced by the online filter is
# automatically corrected for by a heuristic factor stored in the metadata
# (correct_filter_shifts=True).
data_block = session.read_block(
    nsx_to_load='all',
    n_starts=None, n_stops=300 * pq.s,
    channels=[62], units='all',
    load_events=True, load_waveforms=True, scaling='voltage',
    correct_filter_shifts=True)

# Access the single Segment of the data block, reaching up to 300s.
assert len(data_block.segments) == 1
data_segment = data_block.segments[0]


# =============================================================================
# Create offline filtered LFP
#
# Here, we construct one offline filtered LFP from each ns5 (monkey L) or ns6
# (monkey N) raw recording trace. For monkey N, this filtered LFP can be
# compared to the LFPs in the ns2 file (note that monkey L contains only
# behavioral signals in the ns2 file). Also, we assign telling names to each
# Neo AnalogSignal, which is used for plotting later on in this script.
# =============================================================================

filtered_anasig = []
# Loop through all AnalogSignal objects in the loaded data
for anasig in data_block.segments[0].analogsignals:
    if anasig.annotations['nsx'] == 2:
        # AnalogSignal is LFP from ns2
        anasig.name = 'LFP (online filter, ns%i)' % anasig.annotations['nsx']
    elif anasig.annotations['nsx'] in [5, 6]:
        # AnalogSignal is raw signal from ns5 or ns6
        anasig.name = 'raw (ns%i)' % anasig.annotations['nsx']

        # Use the Elephant library to filter the analog signal
        f_anasig = butter(
                anasig,
                highpass_freq=None,
                lowpass_freq=250 * pq.Hz,
                order=4)
        f_anasig.name = 'LFP (offline filtered ns%i)' % \
            anasig.annotations['nsx']
        filtered_anasig.append(f_anasig)
# Attach all offline filtered LFPs to the segment of data
data_block.segments[0].analogsignals.extend(filtered_anasig)


# =============================================================================
# Construct analysis epochs
#
# In this step we extract and cut the data into time segments (termed analysis
# epochs) that we wish to analyze. We contrast these analysis epochs to the
# behavioral trials that are defined by the experiment as occurrence of a Trial
# Start (TS-ON) event in the experiment. Concretely, here our analysis epochs
# are constructed as a cutout of 25ms of data around the TS-ON event of all
# successful behavioral trials.
# =============================================================================

# Get Trial Start (TS-ON) events of all successful behavioral trials
# (corresponds to performance code 255, which is accessed for convenience and
# better legibility in the dictionary attribute performance_codes of the
# ReachGraspIO class).
#
# To this end, we filter all event objects of the loaded data to match the name
# "TrialEvents", which is the Event object containing all Events available (see
# documentation of ReachGraspIO). From this Event object we extract only events
# matching "TS-ON" and the desired trial performance code (which are
# annotations of the Event object).
start_events = get_events(
    data_segment,
    properties={
        'name': 'TrialEvents',
        'trial_event_labels': 'TS-ON',
        'performance_in_trial': session.performance_codes['correct_trial']})

# Extract single Neo Event object containing all TS-ON triggers
assert len(start_events) == 1
start_event = start_events[0]

# Construct analysis epochs from 10ms before the TS-ON of a successful
# behavioral trial to 15ms after TS-ON. The name "analysis_epochs" is given to
# the resulting Neo Epoch object. The object is not attached to the Neo
# Segment. The parameter event2 of add_epoch() is left empty, since we are
# cutting around a single event, as opposed to cutting between two events.
pre = -10 * pq.ms
post = 15 * pq.ms
epoch = add_epoch(
    data_segment,
    event1=start_event, event2=None,
    pre=pre, post=post,
    attach_result=False,
    name='analysis_epochs')

# Create new segments of data cut according to the analysis epochs of the
# 'analysis_epochs' Neo Epoch object. The time axes of all segments are aligned
# such that each segment starts at time 0 (parameter reset_times); annotations
# describing the analysis epoch are carried over to the segments. A new Neo
# Block named "data_cut_to_analysis_epochs" is created to capture all cut
# analysis epochs.
cut_trial_block = Block(name="data_cut_to_analysis_epochs")
cut_trial_block.segments = cut_segment_by_epoch(
    data_segment, epoch, reset_time=True)

# =============================================================================
# Plot data
# =============================================================================

# Determine the first existing trial ID i from the Event object containing all
# start events. Then, by calling the filter() function of the Neo Block
# "data_cut_to_analysis_epochs" containing the data cut into the analysis
# epochs, we ask to return all Segments annotated by the behavioral trial ID i.
# In this case this call should return one matching analysis epoch around TS-ON
# belonging to behavioral trial ID i. For monkey N, this is trial ID 1, for
# monkey L this is trial ID 2 since trial ID 1 is not a correct trial.
trial_id = int(np.min(start_event.annotations['trial_id']))
trial_segments = cut_trial_block.filter(
    targdict={"trial_id": trial_id}, objects=Segment)
assert len(trial_segments) == 1
trial_segment = trial_segments[0]

# Create figure
fig = plt.figure(facecolor='w')
time_unit = pq.CompoundUnit('1./30000*s')
amplitude_unit = pq.microvolt
nsx_colors = ['b', 'k', 'r']

# Loop through all analog signals and plot the signal in a color corresponding
# to its sampling frequency (i.e., originating from the ns2/ns5 or ns2/ns6).
for i, anasig in enumerate(trial_segment.analogsignals):
        plt.plot(
            anasig.times.rescale(time_unit),
            anasig.squeeze().rescale(amplitude_unit),
            label=anasig.name,
            color=nsx_colors[i])

# Loop through all spike trains and plot the spike time, and overlapping the
# wave form of the spike used for spike sorting stored separately in the nev
# file.
for st in trial_segment.spiketrains:
    color = np.random.rand(3,)
    for spike_id, spike in enumerate(st):
        # Plot spike times
        plt.axvline(
            spike.rescale(time_unit).magnitude,
            color=color,
            label='Unit ID %i' % st.annotations['unit_id'])
        # Plot waveforms
        waveform = st.waveforms[spike_id, 0, :]
        waveform_times = np.arange(len(waveform))*time_unit + spike
        plt.plot(
            waveform_times.rescale(time_unit).magnitude,
            waveform.rescale(amplitude_unit),
            '--',
            linewidth=2,
            color=color,
            zorder=0)

# Loop through all events
for event in trial_segment.events:
    if event.name == 'TrialEvents':
        for ev_id, ev in enumerate(event):
                plt.axvline(
                    ev,
                    alpha=0.2,
                    linewidth=3,
                    linestyle='dashed',
                    label='event ' + event.annotations[
                        'trial_event_labels'][ev_id])

# Finishing touches on the plot
plt.autoscale(enable=True, axis='x', tight=True)
plt.xlabel(time_unit.name)
plt.ylabel(amplitude_unit.name)
plt.legend(loc=4, fontsize=10)

# Save plot
fname = 'example_plot'
for file_format in ['eps', 'png', 'pdf']:
    fig.savefig(fname + '.%s' % file_format, dpi=400, format=file_format)
