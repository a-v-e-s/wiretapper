#!/usr/bin/env python3

import os
import re
import time
import threading
import sqlite3
import pickle
from functools import partial
from sys import exc_info
from difflib import SequenceMatcher


# the secret sauce I found on stack overflow:
DEVICE = 'alsa_output.pci-0000_00_1f.3.analog-stereo.monitor'
COMMAND = 'pacat --record -d ' + DEVICE + ' | sox -t raw -r 44100 -L -e signed-integer -S -b 16 -c 2 - "output.wav"'


def test_if_exists(test_string, dirs, match=0.95):
    #
    start_time = time.time()
    #
    for dir in dirs:
        for file in os.listdir(dir):
            file_string = '_'.join(file.split('_')[:2]).lower()
            if SequenceMatcher(None, test_string, file_string).ratio() > match:
                raise FileExistsError(test_string + ' too closely resembles ' + file_string)
    #
    stop_time = time.time()
    print('filename matching took '+str(stop_time-start_time)+' seconds')


def assassinate(delay, target_dir, fn):
    #
    time.sleep(int(delay))
    os.popen('kill `pidof sox`')
    os.popen('kill `pidof pacat`')
    target = target_dir + '/' + fn
    os.rename('output.wav', target)


def wiretap(*args):

    title, artist, album, length, delay, target_dir = args

    try:
        os.nice(-16)        # we do not want lag in our audio recording.
    except PermissionError:
        print('tried to raise process priority,')
        print('but lack root permissions')

    fn_pattern = re.compile(r'([0-9a-zA-Z_]+)(\.wav)')
    possible_fn = title.get() + '_' + artist.get() + '_' + album.get() + '.wav'
    if not re.fullmatch(fn_pattern, possible_fn):
        group_pattern = re.compile(r'(.*)(\.wav)')
        prefix = re.match(group_pattern, possible_fn).group(1)
        unsafe_characters = re.compile(r'[^0-9a-zA-Z_]{1,1}')
        fn = re.sub(unsafe_characters, '', prefix) + '.wav'
    else:
        fn = possible_fn

    match_test = '_'.join(re.split('_', fn)[:2]).lower()
    test_if_exists(match_test, ['sound_files/wavs', 'sound_files/mp3s'])

    time.sleep(int(delay.get()))
    t1 = threading.Thread(target=os.popen, args=(COMMAND,))
    t2 = threading.Thread(target=assassinate, args=(length.get(), target_dir.get(), fn))
    t1.start(); t2.start()

    conn = sqlite3.Connection('music_db.sqlite')
    curs = conn.cursor()

    statement = 'INSERT INTO Songs(filepath, title, artist, album, length) VALUES ('

    statement = statement + '"'+fn+'", "'+title.get()+'", "'+artist.get()+'", "'+album.get()+'", '+str(length.get())+');'

    print(statement)

    try:
        with open('statements.pkl', 'rb') as pkl:
            statements = pickle.load(pkl)
            statements.append(statement)
    except (FileNotFoundError, EOFError):
        print(exc_info())
        print(' +*+*+  CAUGHT AND HANDLED  +*+*+ ')
        statements = [statement]
    finally:
        try:
            with open('statements.pkl', 'wb') as pkl:
                pickle.dump(statements, pkl)
        except Exception:
            print(exc_info())

    try:
        curs.execute(statement)
    except Exception:
        print(exc_info())
    else:
        conn.commit()
    finally:
        curs.close(); conn.close()


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

    buttons = tk.Frame(root)

    args = [title, artist, album, length, delay, target_dir]
    tk.Button(buttons, text='Quit', command=root.destroy).grid(row=1, column=1)
    tk.Button(
        buttons, text='Wiretap!',
        command=partial(wiretap, *args)
    ).grid(row=1, column=2)

    buttons.grid(row=3, column=1)

    root.mainloop()