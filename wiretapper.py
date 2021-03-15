#!/usr/bin/env python3

import os
import re
import time
import threading
from functools import partial


DEVICE = 'alsa_output.pci-0000_00_1f.3.analog-stereo.monitor'
COMMAND = 'pacat --record -d ' + DEVICE + ' | sox -t raw -r 44100 -L -e signed-integer -S -b 16 -c 2 - "output.wav"'


def wiretap(title, artist, album, length, delay, target_dir):

    if not type(title) == str:
        title, artist, album, target_dir = title.get(), artist.get(), album.get(), target_dir.get()

    fn_pattern = re.compile(r'([0-9a-zA-Z_]+)(\.wav)')
    possible_fn = title + '_' + artist + '_' + album + '.wav'
    if not re.fullmatch(fn_pattern, possible_fn):
        group_pattern = re.compile(r'(.*)(\.wav)')
        prefix = re.match(group_pattern, possible_fn).group(1)
        unsafe_characters = re.compile(r'[^0-9a-zA-Z_]{1,1}')
        fn = re.sub(unsafe_characters, '', prefix) + '.wav'
    else:
        fn = possible_fn

    t = threading.Thread(target=os.popen, args=(COMMAND,))
    time.sleep(int(delay.get()))
    t.start()
    time.sleep(int(length.get()))
    os.popen('kill `pidof sox`')
    os.popen('kill `pidof pacat`')
    target = target_dir + '/' + fn
    print('os.popen("mv output.wav " + ' + target)      # meta debug statement
    os.popen('mv output.wav ' + target)


if __name__ == '__main__':

    import tkinter as tk
    from tkinter.filedialog import askdirectory
    from sqlite3 import Connection

    root = tk.Tk()
    root.title('Wiretapper')

    title = tk.StringVar()
    artist = tk.StringVar()
    album = tk.StringVar()
    length = tk.StringVar()
    delay = tk.StringVar()
    target_dir = tk.StringVar()

    tapper = tk.Frame(root, borderwidth=2)

    tk.Label(tapper, text='Song Name:').grid(row=1, column=1)
    tk.Entry(tapper, bg='white', width=48, textvariable=title).grid(row=1, column=2)

    tk.Label(tapper, text='Artist:').grid(row=2, column=1)
    tk.Entry(tapper, bg='white', width=48, textvariable=artist).grid(row=2, column=2)

    tk.Label(tapper, text='Album:').grid(row=3, column=1)
    tk.Entry(tapper, bg='white', width=48, textvariable=album).grid(row=3, column=2)

    tk.Label(tapper, text='Length: (seconds)').grid(row=4, column=1)
    tk.Spinbox(tapper, from_=1, to=3600, textvariable=length).grid(row=4, column=2)
    length.set(300)

    tk.Label(tapper, text='Recording Delay: (seconds)').grid(row=5, column=1)
    tk.Spinbox(tapper, from_=0, to=60, textvariable=delay).grid(row=5, column=2)
    delay.set(2)

    tk.Label(tapper, text='Save Location:').grid(row=6, column=1)
    # directory needs to be defined and the assigned to the grid
    # for its button to work!!
    directory = tk.Entry(tapper, width=48, textvariable=target_dir)
    directory.grid(row=7, column=1)
    tk.Button(
        tapper, text='Browse', command=(lambda x=directory: [x.delete(0, len(x.get())), x.insert(0, askdirectory())])
    ).grid(row=7, column=2)

    tk.Button(tapper, text='Quit', command=root.destroy).grid(row=8, column=1)
    tk.Button(
        tapper, text='Wiretap!',
        command=partial(wiretap, title, artist, album, length, delay, target_dir)
    ).grid(row=8, column=2)

    tapper.pack()
    """
    attributes = tk.Frame(root, borderwidth=2)

    genres = [
        'synth',
        'hard_rock',
        'metal',
        'gothish',
        'indie',
        'pop',
        'dance',
        'disco',
        'house',
        'trance',
        'industrial',
        'new_age',
        'ambient',
        'classical',
        'contemporary',
        'emo',
        'classic_rock',
        'alt_rock',
        'reggae',
        'hip_hop',
        'hardcore_rap',
        'rb',
        'psychedelic',
        'country',
        'classic_rb',
    ]
    emotions = [
        'romantic',
        'funny',
        'melancholy',
        'angry',
        'happy',
        'hypnotic',
    ]
    others = [
        'foreign_language',
        'instrumental',
    ]

    conn = Connection('music_db.sqlite')
    curs = conn.cursor()
    table_info = curs.execute('pragma table_info(Songs);').fetchall()

    for data in table_info:
        if data[1] in ['title', 'artist', 'album', 'length']:
            continue
        elif data[1] in genres:
            pass
        elif data[1] in emotions:
            pass
        elif data[1] in others:
            pass
        else:
            raise Exception

    tk.LabelFrame(attributes, text='Genres:').grid(row=1, column=1, columnwidth=4)

    tk.LabelFrame(attributes, text='Genres:').grid(row=2, column=1, columnwidht=2)

    tk.LabelFrame(attributes, text='Emotions:').grid(row=2, column=3, columnwidth=2)

    tk.LabelFrame(attributes, text='Other:').grid(row=3, column=1, columnwidth=2)

    attributes.pack()
    """
    root.mainloop()
