#!/usr/bin/env python3

import os
import re
import time
import threading
from functools import partial
from sys import exc_info
from difflib import SequenceMatcher


# the secret sauce I found on stack overflow:
DEVICE = 'alsa_output.pci-0000_00_1f.3.analog-stereo.monitor'
COMMAND = 'pacat --record -d ' + DEVICE + ' | sox -t raw -r 44100 -L -e signed-integer -S -b 16 -c 2 - "output.wav"'


def test_if_exists(test_string, dirs, match=0.95):
    # 
    start_time = time.time()
    # look through all files and raise exception
    # if we have this already:
    for dir in dirs:
        for file in os.listdir(dir):
            file_string = '_'.join(file.split('_')[:2]).lower()
            if SequenceMatcher(None, test_string, file_string).ratio() > match:
                raise FileExistsError(test_string + ' too closely resembles ' + file_string)
    # make sure this isn't taking too long:
    stop_time = time.time()
    print('filename matching took '+str(stop_time-start_time)+' seconds')


def assassinate(delay, target_dir, fn):
    # wait for preset time, then stop recording:
    time.sleep(int(delay))
    os.popen('kill `pidof sox`')
    os.popen('kill `pidof pacat`')
    target = target_dir + '/' + fn
    time.sleep(1)
    # rename and move file:
    os.rename('output.wav', target)


def wiretap(*args):

    # unpack arguments:
    title, artist, album, length, delay, target_dir = args

    # we do not want lag in our audio recording.
    try:
        os.nice(-16)
    except PermissionError:
        print('tried to raise process priority,')
        print('but lack root permissions')

    # build filename:
    fn_pattern = re.compile(r'([0-9a-zA-Z_]+)(\.wav)')
    possible_fn = title.get() + '_' + artist.get() + '_' + album.get() + '.wav'
    if not re.fullmatch(fn_pattern, possible_fn):
        group_pattern = re.compile(r'(.*)(\.wav)')
        prefix = re.match(group_pattern, possible_fn).group(1)
        unsafe_characters = re.compile(r'[^0-9a-zA-Z_]{1,1}')
        fn = re.sub(unsafe_characters, '', prefix) + '.wav'
    else:
        fn = possible_fn

    # make sure we don't already have this song,
    # raises Exception if we do:
    match_test = '_'.join(re.split('_', fn)[:2]).lower()
    test_if_exists(match_test, ['sound_files/wavs', 'sound_files/mp3s'])

    # start recording thread and stop recording thread:
    time.sleep(int(delay.get()))
    t1 = threading.Thread(target=os.popen, args=(COMMAND,))
    t2 = threading.Thread(target=assassinate, args=(length.get(), target_dir.get(), fn))
    t1.start(); t2.start()


if __name__ == '__main__':

    import tkinter as tk
    from tkinter.filedialog import askdirectory
    
    # begin building gui:
    root = tk.Tk()
    root.title('Wiretapper')
    
    # data points:
    title = tk.StringVar()
    artist = tk.StringVar()
    album = tk.StringVar()
    length = tk.StringVar()
    delay = tk.StringVar()
    target_dir = tk.StringVar()
    
    # song info will be input here:
    tapper = tk.Frame(root, borderwidth=2)
    #
    tk.Label(tapper, text='Song Name:').grid(row=1, column=1)
    tk.Entry(tapper, bg='white', width=72, textvariable=title).grid(row=1, column=2)
    #
    tk.Label(tapper, text='Artist:').grid(row=2, column=1)
    tk.Entry(tapper, bg='white', width=72, textvariable=artist).grid(row=2, column=2)
    #
    tk.Label(tapper, text='Album:').grid(row=3, column=1)
    tk.Entry(tapper, bg='white', width=72, textvariable=album).grid(row=3, column=2)
    #
    tk.Label(tapper, text='Length: (seconds)').grid(row=4, column=1)
    tk.Spinbox(tapper, from_=1, to=3600, textvariable=length).grid(row=4, column=2)
    length.set(300)
    #
    tk.Label(tapper, text='Recording Delay: (seconds)').grid(row=5, column=1)
    tk.Spinbox(tapper, from_=0, to=60, textvariable=delay).grid(row=5, column=2)
    delay.set(2)
    #
    tk.Label(tapper, text='Save Location:').grid(row=6, column=1)
    # the directory Entry object needs to be assigned to a variable,
    # and then assigned to the grid for its button to work!!
    directory = tk.Entry(tapper, width=72, textvariable=target_dir)
    directory.grid(row=7, column=2)
    # button to find save directory:
    tk.Button(
        tapper, text='Browse', command=(
            lambda x=directory: [
                x.delete(0, len(x.get())),
                x.insert(0, askdirectory())
            ]
        )
    ).grid(row=7, column=1)
    
    tapper.grid(row=1, column=1)
    
    # buttons to control operation:
    buttons = tk.Frame(root)
    # ugly button definition:
    args = [title, artist, album, length, delay, target_dir]
    tk.Button(
        buttons, text='Wiretap!',
        command=partial(wiretap, *args)
    ).grid(row=1, column=1)
    #
    tk.Button(buttons, text='Quit', command=root.destroy).grid(row=1, column=2)
    #
    buttons.grid(row=3, column=1)
    #
    # run it!
    root.mainloop()