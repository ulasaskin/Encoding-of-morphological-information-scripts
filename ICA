from mne.io import read_raw_ctf, read_raw_fif
from mne.preprocessing import find_bad_channels_maxwell
from mne import find_events, Epochs, read_events
import os
import pandas as pd
import numpy as np
from mne.preprocessing import ICA, create_eog_epochs, create_ecg_epochs,compute_proj_ecg,compute_proj_eog
from mne import pick_types
from mne import concatenate_raws, Annotations, write_events
import pandas as pd
import mne
import matplotlib.pyplot as plt


# from mne.preprocessing import annotate_amplitude

#In June there was a problem with these channels: MLO22, MLO53, MLP52, MLP31, MLP23, MLP53, MLO21,MLO41, MLP32, NLP41, MLO31, MLO51, P11, P22, P23, P12
# Sub-001, sub-003 and sub-004 maybe sub-002 are affected

#%% Independent Component Analysis
Output_MEG_folder = '/project/3027013.01/processed/' #Folder where preprocessed MEG data are located
subject = 'sub-014'
raw_fname = os.path.join(Output_MEG_folder, subject, 'meg','%s_resampled_100_Hz_filtered_05_40_Hz.fif' %(subject))

# raw_fname =  os.path.join(Output_MEG_folder, subject, 'meg','%s_resampled_filtered_05_40_Hz_ICA_eyeblink_removed.fif' %(subject))
raw  = read_raw_fif(raw_fname,preload=True )

event_file_name = os.path.join(Output_MEG_folder, subject, 'meg','%s-eve.fif' %(subject))
events = read_events(event_file_name)

picks = pick_types(raw.info, meg=True,ref_meg=False, eeg=False, eog=False,
                        stim=False)

raw = raw.pick(picks)
raw.plot(events)

raw.plot_psd(fmin = 0.5, fmax = 49)
# raw.info['bads']= ['MLT25-4304','MLP54-4304','MLC51-4304','MLC31-4304']
print(dur)

#%%
# raw.info['bads'] = []
# print('Bad channels')
# print(raw.info['bads'])
# auto_noisy_chs, auto_flat_chs, auto_scores = mne.preprocessing.find_bad_channels_maxwell(
# raw, return_scores=True, verbose=True) #cross_talk=crosstalk_file, calibration=fine_cal_file,
# bads = raw.info['bads'] + auto_noisy_chs + auto_flat_chs
# raw.info['bads'] = bads
# print('new bads')
# print(bads)


#%% Find squid jumps

annotations = raw.annotations


anot, bad = annotate_amplitude(raw, peak=20e-13, min_duration=0.005) # picks=[pick]

for a in anot:
    annotations.append(a['onset'],a['duration'],a['description'])


raw = raw.set_annotations(annotations)
raw.plot(events)


if subject =='sub-003':
    annotations.append(1203,9,'BAD')
    annotations.append(3179,8,'BAD')
    annotations.append(3804,7,'BAD')
    
    raw.info['bads'] = ['MLC62-4304']

if subject =='sub-004':
    annotations.append(1203,9,'BAD')
    annotations.append(2805,4,'BAD')



raw = raw.set_annotations(annotations)
raw.plot(events)



# annot, scores = annotate_muscle_zscore(
# raw,
#  # picks=[pick],
# threshold=4.0,
# min_length_good=0.2,
# filter_freq=(0.5, 40))




# if len(anot)>0:
#     print(ch)
#     all_anot.append(anot)
#     all_ch.append(ch)
 
# for i in range(len(all_ch)):
#     for a in all_anot[i]:
#         annotations.append(a['onset'],a['duration'],a['description'])

# raw = raw.set_annotations(annotations)
# raw.plot_psd(fmin=0.5, fmax=40)
# raw.plot(events)

# print(dur)

#%%


# data = raw.get_data(picks='meg')
# diff = np.diff(data, axis=1)

# threshold = 10 * np.std(diff)  # tune this
# jump_mask = np.abs(diff) > threshold

# times, chans = np.where(jump_mask)


# onsets = raw.times[times]
# durations = np.repeat(0.01, len(onsets))
# descriptions = ['SQUID_jump'] * len(onsets)

# annot = mne.Annotations(onsets, durations, descriptions)

# raw = raw.set_annotations(annot)
# # raw.plot_psd(fmin=0.5, fmax=40)
# raw.plot(events)

#%% Choose ICA parameters and apply ICA

method = 'fastica'
#decim = 3  # we need sufficient statistics, not all time points -> saves time
random_state = 42
ica = ICA(method=method, random_state=random_state, max_iter = 10000, n_components = 0.95)
print(ica)
ica.fit(raw,  decim=None)
# ica.fit(raw_concat, picks=picks, decim=None)
print('ICA is fitted')


ica.plot_components()
ica.plot_sources(raw, show_scrollbars=False)

# #plot for kurtosis of the ICA components. if a component reflects the neural signal, it must be gaussian-like. That is, real neural signal is not random but evenly distributed. On the other hand, random events
# #such as eye-blinks, muscle movements etc. have non-gaussian distribution reflecting clear difference between the real signal and the noise caused by muscles. 
# import matplotlib.pyplot as plt
# from scipy.stats import kurtosis
# ica_sources = ica.get_sources(raw).get_data()
# kurt = kurtosis(ica_sources, axis=1, fisher=True)
# plt.figure()
# plt.bar(range(len(kurt)), kurt)
# plt.xlabel('ICA component')
# plt.ylabel('Kurtosis')
# plt.title('Kurtosis of ICA components')
# plt.show()


# ica.plot_properties(raw, picks=[3], psd_args=dict(fmin=1, fmax=40))

#ica.plot_sources(raw_concat, show_scrollbars=False)

print(dur)
#%% Check how many epochs are found. If good exclude the components and save
eog_inds = [0,10, 17] #enter the ICA comp that you want to exclude. be careful about the component's periodicity and topography. muscle artifacts look periodic and topographically symmetric. exclude them
ica.exclude.extend(eog_inds)
raw  = ica.apply(raw)
raw.plot(events)

#%% Save the file
raw_ICA_fname = os.path.join(Output_MEG_folder, subject, 'meg','%s_resampled_filtered_05_40_Hz_ICA_eyeblink_removed.fif' %(subject))

raw.save(raw_ICA_fname, overwrite=True)
