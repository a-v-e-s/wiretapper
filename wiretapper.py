#!/usr/bin/env python3

import os
import re
import time
import threading
from functools import partial


# the secret sauce I found on stack overflow:
DEVICE = 'alsa_output.pci-0000_00_1f.3.analog-stereo.monitor'
COMMAND = 'pacat --record -d ' + DEVICE + ' | sox -t raw -r 44100 -L -e signed-integer -S -b 16 -c 2 - "output.wav"'


def wiretap(title, artist, album, length, delay, target_dir, genres, emotions, others):

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

    print(); print()
    for genre in genres.keys():
        print(genre, str(genres[genre].get()))
    print(); print()
    for emotion in emotions.keys():
        print(emotion, str(emotions[emotion].get()))
    print(); print()
    for other in others.keys():
        print(other, str(others[other].get()))
    print(); print()


if __name__ == '__main__':


    import tkinter as tk
    from tkinter.filedialog import askdirectory
    from sqlite3 import Connection


    genre_attrs = [
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
    emotion_attrs = [
        'romantic',
        'funny',
        'melancholy',
        'angry',
        'happy',
        'hypnotic',
    ]
    other_attrs = [
        'cerebral',
        'foreign_language',
        'instrumental',
    ]


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
    tk.Entry(tapper, bg='white', width=72, textvariable=title).grid(row=1, column=2)

    tk.Label(tapper, text='Artist:').grid(row=2, column=1)
    tk.Entry(tapper, bg='white', width=72, textvariable=artist).grid(row=2, column=2)

    tk.Label(tapper, text='Album:').grid(row=3, column=1)
    tk.Entry(tapper, bg='white', width=72, textvariable=album).grid(row=3, column=2)

    tk.Label(tapper, text='Length: (seconds)').grid(row=4, column=1)
    tk.Spinbox(tapper, from_=1, to=3600, textvariable=length).grid(row=4, column=2)
    length.set(300)

    tk.Label(tapper, text='Recording Delay: (seconds)').grid(row=5, column=1)
    tk.Spinbox(tapper, from_=0, to=60, textvariable=delay).grid(row=5, column=2)
    delay.set(2)

    tk.Label(tapper, text='Save Location:').grid(row=6, column=1)
    # the directory Entry object needs to be assigned to a variable,
    # and then assigned to the grid for its button to work!!
    directory = tk.Entry(tapper, width=72, textvariable=target_dir)
    directory.grid(row=7, column=2)
    tk.Button(
        tapper, text='Browse', command=(lambda x=directory: [x.delete(0, len(x.get())), x.insert(0, askdirectory())])
    ).grid(row=7, column=1)

    tapper.grid(row=1, column=1)

    attributes = tk.LabelFrame(root, text='Attributes:')

    conn = Connection('music_db.sqlite')
    curs = conn.cursor()
    table_info = curs.execute('pragma table_info(Songs);').fetchall()

    genre_frame = tk.LabelFrame(attributes, text='Genres:')

    emotion_frame = tk.LabelFrame(attributes, text='Emotions:')

    other_frame = tk.LabelFrame(attributes, text='Other:')

    genres, emotions, others = dict(), dict(), dict()
    g_rownum, g_colnum, e_rownum, e_colnum, o_rownum, o_colnum = 0, 0, 0, 0, 0, 0
    for data in table_info:
        if data[1] in ['title', 'artist', 'album', 'length']:
            continue
        else:
            var = tk.IntVar()

        if data[1] in genre_attrs:
            g_rownum += 1
            if g_rownum % 7 == 0:
                g_rownum = 1
                g_colnum += 2
            genres[data[1]] = var
            tk.Label(genre_frame, text=data[1]).grid(row=g_rownum, column=g_colnum)
            tk.Checkbutton(genre_frame, variable=var, offvalue=0, onvalue=1).grid(row=g_rownum, column=g_colnum+1)
        elif data[1] in emotion_attrs:
            e_rownum += 1
            if e_rownum % 7 == 0:
                e_rownum = 1
                e_colnum += 2
            emotions[data[1]] = var
            tk.Label(emotion_frame, text=data[1]).grid(row=e_rownum, column=e_colnum)
            tk.Checkbutton(emotion_frame, variable=var, offvalue=0, onvalue=1).grid(row=e_rownum, column=e_colnum+1)
        elif data[1] in other_attrs:
            o_rownum += 1
            if o_rownum % 7 == 0:
                o_rownum = 1
                o_colnum += 2
            others[data[1]] = var
            tk.Label(other_frame, text=data[1]).grid(row=o_rownum, column=o_colnum)
            tk.Checkbutton(other_frame, variable=var, offvalue=0, onvalue=1).grid(row=o_rownum, column=o_colnum+1)
        else:
            #raise LookupError(data)
            o_rownum += 1
            if o_rownum % 7 == 0:
                o_rownum = 1
                o_colnum += 2
            o[data] = var
            tk.Label(other_frame, text=data[1]).grid(row=o_rownum, column=o_colnum)
            tk.Checkbutton(other_frame, variable=var, offvalue=0, onvalue=1).grid(row=o_rownum, column=o_colnum)

    genre_frame.grid(row=1, column=1)
    emotion_frame.grid(row=1, column=2)
    other_frame.grid(row=1, column=3)

    attributes.grid(row=2, column=1)

    buttons = tk.Frame(root)

    tk.Button(buttons, text='Quit', command=root.destroy).grid(row=1, column=1)
    tk.Button(
        buttons, text='Wiretap!',
        command=partial(wiretap, title, artist, album, length, delay, target_dir, genres, emotions, others)
    ).grid(row=1, column=2)

    buttons.grid(row=3, column=1)

    root.mainloop()
