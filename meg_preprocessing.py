from mne.io import read_raw_ctf
from mne.preprocessing import find_bad_channels_maxwell
from mne import find_events
import os
import pandas as pd
import numpy as np
from mne.preprocessing import ICA, create_eog_epochs, create_ecg_epochs,compute_proj_ecg,compute_proj_eog
from mne import pick_types
from mne import concatenate_raws, Annotations, write_events
from scipy.io import loadmat
import pandas as pd
import mne
from scipy import signal as sp
from scipy.io import wavfile


#%% specify the raw MEG data folder as well as the output folder where the 
#the preprocessed data is saved to
#MEG_folder = '/project/3027013.01/raw/'  #Folder where raw MEG data are located
MEG_folder = '/project/3027013.01/raw/'
#Output_MEG_folder = '//project/3027013.01/processed/' #Folder where preprocessed MEG data are located
Output_MEG_folder = '/project/3027013.01/processed/'

subjects = [
    name for name in os.listdir(Output_MEG_folder) 
    if os.path.isdir(os.path.join(Output_MEG_folder, name)) and name.startswith('sub')
]


subjects.sort()



df_subjects = pd.read_excel('/project/3027013.01/Scripts/Presentation_order/participants_log.xlsx')

for subject in subjects:
# subject = 'sub-006' #determines which subject to preprocess, we started with sub-003
    
    
    language = df_subjects.loc[df_subjects["Sub number"] == subject, "Language"].tolist()[0] #'NL' # NL for Dutch, TR for Turkish, and ZH for Mandarin
    presentation_order = df_subjects.loc[df_subjects["Sub number"] == subject, "Presentation order"].tolist()[0] #1
    
    file_name = '/project/3027013.01/Scripts/Presentation_order/' + language + '_Presentation_order_' +str(presentation_order) +'.xlsx'
    df = pd.read_excel(file_name)
    
    
    
    #%% load the raw MEG data
    #meg system allows you to collect various types of data from various types of channels
    #in this study we only make use of stim and resp to collect behavioral data on how
    #engaged participants are during the podcasts. any other channel is irrelevant to the
    #analysis.
    ch_types = {
                # EOG
                'EEG057-4302':'eog', 
                'EEG058-4302':'eog',
                # EKG
                'EEG059-4302':'ecg',
                # Triggers
                'UPPT001':'stim', 
                'UPPT002':'resp', # response
                    }
    
    
    ds_data = os.listdir(os.path.join(MEG_folder, subject,'ses-meg01/meg'))[0]
    
    raw_file_name=os.path.join(MEG_folder, subject, 'ses-meg01/meg/', ds_data)
    
    raw = read_raw_ctf(raw_file_name, preload=True)
    
    raw = raw.set_channel_types(ch_types) 
    
    
    print(raw_file_name)
    # print(dur)
    
    
    
    #%% Find squid jumps
    
    # annotations = raw.annotations
    # all_anot = []
    # all_ch = []
    # for ch in  raw.info['ch_names']: #['MRT21-4304']: #raw.info['ch_names']: : #
    #     pick = ch
    
    #     # annot, scores = annotate_muscle_zscore(
    #     # raw,
    #     #  # picks=[pick],
    #     # threshold=4.0,
    #     # min_length_good=0.2,
    #     # filter_freq=(0.5, 40))
        
    #     anot, bad = annotate_amplitude(raw, peak=20e-13, picks=[pick], min_duration=0.005)
    
    
    
    #     if len(anot)>0:
    #         print(ch)
    #         all_anot.append(anot)
    #         all_ch.append(ch)
     
    # for i in range(len(all_ch)):
    #     for a in all_anot[i]:
    #         annotations.append(a['onset'],a['duration'],a['description'])
    
    # raw = raw.set_annotations(annotations)
    # # raw.plot_psd(fmin=0.5, fmax=40)
    # raw.plot(events)
    
    #%% Resample and filter
    #For a signal that has 1200Hz sample rate, all the possible analysis can be conducted considering the 
    #maximum frequency limit, sampling frequency/2, according to Nyquist–Shannon sampling theorem. 
    #This limit exists because of aliasing which suggests that high-frequency components might fold back and 
    #appear as false low-frequency artifacts in the signal.This happens when we try to capture too much detail 
    #with too few samples per second.
    
    #sample rate of MEG is big. We won't need such fine grained signals. Instead we need to
    #downsample the signal for both processing and memory costs.
    #this is because events annotations still assume that we collect data 1200Hz which we downsample to 200Hz.
    desired_sfreq = 100  # Hz    
    raw = raw.resample(desired_sfreq) 
    events = find_events(raw,shortest_event=1)
    #power spectrum density: shows 
    #if a one single channel has a power spike that's not normal. We need check it or remove.
    # apply notch filter to raw
    # raw.plot_psd(fmin = 0.5, fmax = 40)
    # raw.plot(events)
    
    fs = raw.info['sfreq']
    # print(dur)
    #%% annotate task response and between blocks as BAD
    #first we need to mark when a podcast starts and ends
    
    trigger_starts = [110, 120, 130, 140, 210, 220, 230, 240,  10,  20,  30,  40]
    triger_ends = [111, 121, 131, 141, 211, 221, 231, 241, 11, 21, 31, 41]
    
    if subject=='sub-001' or subject=='sub-002' or subject=='sub-003'  or subject=='sub-004' or subject=='sub-006':
        idx_rest = np.where(events[:,2]==66)[0] #find the rows with the resting start trigger
        
        if len(idx_rest) != 8: # number of blocks
            raise ValueError(f"idx_rest must have length 8, got {len(idx_rest)}")
            
            
        new_events = []
        
        for i,idx in enumerate(idx_rest): 
            new_events.append(events[idx])
            time = int(events[idx][0] + 32*desired_sfreq) #this is the 32 second break after the start of the blocks
            start = int(df['Trigger_start'].tolist()[i])
            if start>300:
                start=start-300
            
            new_events.append([time,0,start])
            
            audio_file_name =  '/project/3027013.01/Scripts/Stimuli/' + df.Stimuli[i] +'.wav'
            sample_rate, data = wavfile.read(audio_file_name)
            time_end = time + len(data)/sample_rate*desired_sfreq
            new_events.append([time_end,0,start+1])
            
        new_events = np.array(new_events)    
        new_events = new_events.astype(int) 
        
        rest_index_org = np.where(events[:,2]==66)[0]
        rest_index_new = np.where(new_events[:,2]==66)[0]
        
        new_merged_events = []
        rest_no = 0
        for i in range(len(events)):
            
            if i-1 in rest_index_org:
                if not events[i][2] in trigger_starts:
                    new_merged_events.append(new_events[rest_index_new[rest_no]+1])
                new_merged_events.append(events[i])
                rest_no = rest_no +1               
                
            elif  i < len(events)-2 and events[i+1][2] == 66:
                new_merged_events.append(events[i])
                if not events[i][2] in triger_ends:             
                    new_merged_events.append(new_events[rest_index_new[rest_no-1]+2])
                
                    
            elif i == len(events)-1 and not events[i][2] in triger_ends:
                new_merged_events.append(events[i])
                new_merged_events.append(new_events[rest_index_new[rest_no-1]+2])
                
            else:
                new_merged_events.append(events[i])
                     
                
        events=np.array(new_merged_events)       
            
    
    
    
    if subject=='sub-011': #correct the wrong button press trigger
        do=0
        for i in range(len(events)):
            if events[i,2]==40 or events[i,2]==240:
                do=1
            if events[i,2]==41 or events[i,2]==241:
                do=0
            if do==1  and not events[i,2]==40 and not events[i,2]==240:
                events[i,2]=events[i,2]-1
                
    
    
        
        
            
    #%%annotating the time between each podcast as Bad_task
    #we already marked the start and end of each podcast above
    task_start = [0]
    
    task_end = []
    
    #we do not want to include the breaks where participants move therefore we need to annotate them
    #so that we can ignore such parts when analysis is conducted.
    for i in range(len(new_events)):#goes over the list of events
        for j in range(len(triger_ends)): #also goes to the list of trigger ends which was specified above
            if new_events[i,2]==triger_ends[j]: #when event number matches the trigger number
                task_start.append(new_events[i,0]/fs+0.5) #store the start of that task in events
                
    
    for j in range(len(new_events)):
        if new_events[j,2]==66:
            task_end.append(new_events[j,0]/fs-0.5) #bad period ends just before the next resting state starts
            
            
        
    task_end.append(raw.last_samp/fs)
        
    duration = np.array(task_end)-np.array(task_start)       
    duration_task = duration.tolist()
    
    
    description_task= ['BAD_Task'] * len(task_start)
    annotations = Annotations([*task_start], [ *duration_task] , [*description_task])  
    
    raw = raw.set_annotations(annotations)
    
    # raw.plot(new_events)
    
    
    
    # print(dur)
    
    #%%applying filter
    picks = pick_types(raw.info, meg=True) #apply only to MEG channels
    
    l_freq = 0.5 # high-pass filter in Hz, apply the bandpass filter which removes low frequency drifts and high frequency noise
    h_freq = 40
    #apply high-pass filter to raw
    raw = raw.filter(l_freq, h_freq, skip_by_annotation=('edge','BAD_Task', 'BAD_Between_bloks')) #skips the annotations  
    
    # raw.plot()
    
    
    
    #%%save the annotated, resampled and filtered meg signal
    raw_fname = os.path.join(Output_MEG_folder, subject, 'meg','%s_resampled_100_Hz_filtered_05_40_Hz.fif' %(subject))
    raw.save(raw_fname, overwrite=True)
    
    event_file_name = os.path.join(Output_MEG_folder, subject, 'meg','%s-eve.fif' %(subject))
    # new_events = new_events.astype(int) #TypeError: Cannot safely write data with dtype float64 as int,I added this because thr write_events. function expects event array to be an integer not float64
    write_events(event_file_name,events)
    
