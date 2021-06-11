#!/usr/bin/env python3

import os
import re
import sqlite3
import eyed3
import pydub
import tkinter as tk
from tkinter.filedialog import askopenfilename, askdirectory
from sys import exc_info
from functools import partial
from random import choice


def listen(src):
    # listen to the song to evaluate the file:
    clear_all()
    os.popen('xdg-open ' + src.get())


def clear_all():
    for _dict in [genres, emotions, others]:
        for value in _dict.values():
            value.set(0)
    
    length.set('1')
    genre_tag.set('')


def parse_filepath(path):
    # regex for splitting camelcase (I cheated and found this online):
    camel_pattern = re.compile(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)')
    # get song information from filename:
    fn = os.path.basename(path)
    t, r, m = fn.split('_')
    m = m[:-4]
    #
    val = ' '.join(re.findall(camel_pattern, t))
    title = val if val else t
    val = ' '.join(re.findall(camel_pattern, r))
    artist = val if val else r
    val = ' '.join(re.findall(camel_pattern, m))
    album = val if val else m

    return fn, title, artist, album


def convert_to_mp3(src, dst):
    # convert to mp3 format:
    transitional = pydub.AudioSegment.from_mp3(src)
    transitional.export(dst, format='mp3')
    os.remove(src)


def meta_data_tag(*tags):
    fn, title, artist, album, genre = tags

    file = eyed3.load(fn)
    file.tag.title = title
    file.tag.artist = artist
    file.tag.album = album
    file.tag.genre = genre

    file.tag.save()


def update_db(genres, emotions, others, source, destination, length, genre_tag):
    #
    assert others['confirmed'].get() == 1 or alert('unconfirmed')
    assert int(length.get()) > 1 or alert('invalid length')
    assert genre_tag.get() or alert('empty genre_tag')
    # get filepath and song info from filename:
    source = source.get()
    fn, title, artist, album = parse_filepath(source)

    # move and convert file to mp3 format:
    target = os.path.join(destination.get(), fn[:-3]+'mp3')
    relpath = os.path.relpath(target)
    convert_to_mp3(source, target)

    # tag mp3 file with metadata:
    meta_data_tag(target, title, artist, album, genre_tag.get())

    #connect do db:
    conn = sqlite3.Connection('music_db.sqlite')
    curs = conn.cursor()
    
    # get song attributes to store with value 1 indicating true:
    columns = []
    for k, v in genres.items():
        if v.get() == 1:
            columns.append(k)
    for k, v in emotions.items():
        if v.get() == 1:
            columns.append(k)
    for k, v in others.items():
        if v.get() == 1:
            columns.append(k)
    
    # build the INSERT statement:
    statement = 'INSERT INTO Songs(filepath, title, artist, album, length, '
    for col in columns:
        statement += (col + ', ')
    statement = statement[:-2] + ') VALUES ("'+relpath+'", "'+title+'", "'+artist+'", "'+album+'", '+length.get()+', '
    for col in columns:
        statement += '1, '
    statement = statement[:-2] + ');'
    
    # display and store the INSERT statement:
    print(statement)
    with open('statements.txt', 'a') as statements:
        statements.write(statement+'\n')
    
    # execute the statement:
    curs.execute(statement)
    conn.commit()
    curs.close(); conn.close()


def alert(text):
    alert = tk.Toplevel()
    alert.title(text)
    tk.Label(alert, text=text).pack()
    tk.Button(alert, text='Okay', command=alert.destroy).pack()


def remove(source):
    target = source.get()
    unconfirmed = tk.Toplevel()
    unconfirmed.title('Delete?')
    tk.Label(unconfirmed, text='Really delete '+target+'??').pack()
    tk.Button(unconfirmed, text='Delete!', command=partial(os.remove, target)).pack()
    tk.Button(unconfirmed, text="Don't Delete!", command=unconfirmed.destroy).pack()

if __name__ == '__main__':

    conn = sqlite3.Connection('music_db.sqlite')
    curs = conn.cursor()
    table_info = curs.execute('pragma table_info(Songs);').fetchall()
    curs.close(); conn.close()

    emotion_attrs = ['romantic', 'funny', 'melancholy', 'angry', 'happy', 'hypnotic']
    other_attrs = ['cerebral', 'foreign_language', 'instrumental', 'confirmed']
    genre_attrs = [
        'synth', 'hard_rock', 'metal', 'gothish', 'indie', 'pop', 'dance', 'disco', 'house', 'trance', 'folk',
        'industrial', 'new_age', 'ambient', 'classical', 'contemporary', 'emo', 'classic_rock', 'alt_rock', 'reggae',
        'hip_hop', 'hardcore_rap', 'rb', 'psychedelic', 'country', 'classic_rb', 'triphop', 'light_rock'
    ]

    root = tk.Tk()
    root.title('Evaluator')

    files = tk.LabelFrame(root, text='File:')

    source = tk.StringVar()
    tk.Label(files, text='Source:').grid(row=1, column=1, columnspan=2)
    src = tk.Entry(files, bg='white', width=72, textvariable=source)
    src.grid(row=2, column=1)
    tk.Button(files, text='Browse', command=(
        lambda x=src: [
            x.delete(0, len(x.get())),
            x.insert(0, askopenfilename())
        ]
    )).grid(row=2, column=2)
    dirr = 'sound_files/wavs/'
    tk.Button(files, text='Random Choice', command=(
        lambda x=src: [
            x.delete(0, len(x.get())),
            x.insert(0, os.path.join(dirr, choice(os.listdir(dirr))))
        ]
    )).grid(row=2, column=3)

    destination = tk.StringVar()
    tk.Label(files, text='Destination:').grid(row=3, column=1, columnspan=2)
    dst = tk.Entry(files, bg='white', width=72, textvariable=destination)
    dst.grid(row=4, column=1)
    tk.Button(files, text='Browse', command=(
        lambda x=dst: [
            x.delete(0, len(x.get())),
            x.insert(0, askdirectory())
        ]
    )).grid(row=4, column=2)

    files.grid(row=1, column=1)

    attributes = tk.LabelFrame(root, text='Attributes:')

    length = tk.StringVar()
    tk.Label(attributes, text='Length').grid(row=1, column=1)
    tk.Spinbox(attributes, width=8, from_=1, to=3600, textvariable=length).grid(row=1, column=2)

    genre_tag = tk.StringVar()
    tk.Label(attributes, text='Primary Genre (mp3 tag):').grid(row=2, column=1)
    gt = tk.Entry(attributes, bg='white', width=24, textvariable=genre_tag)
    gt.grid(row=2, column=2)

    genre_frame = tk.LabelFrame(attributes, text='Genres:')
    emotion_frame = tk.LabelFrame(attributes, text='Emotions:')
    other_frame = tk.LabelFrame(attributes, text='Other:')

    genres, emotions, others = dict(), dict(), dict()
    g_rownum, g_colnum, e_rownum, e_colnum, o_rownum, o_colnum = 0, 0, 0, 0, 0, 0
    for data in table_info:
        if data[1] in ['filepath', 'title', 'artist', 'album', 'length']:
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
            raise LookupError(data)
            #o_rownum += 1
            #if o_rownum % 7 == 0:
            #    o_rownum = 1
            #    o_colnum += 2
            #others[data] = var
            #tk.Label(other_frame, text=data[1]).grid(row=o_rownum, column=o_colnum)
            #tk.Checkbutton(other_frame, variable=var, offvalue=0, onvalue=1).grid(row=o_rownum, column=o_colnum)

    genre_frame.grid(row=3, column=1, columnspan=2)
    emotion_frame.grid(row=3, column=3, columnspan=2)
    other_frame.grid(row=3, column=5, columnspan=2)

    attributes.grid(row=2, column=1)

    functions = tk.LabelFrame(root, text='Fuctions:')
    
    tk.Button(functions, text='Listen', command=partial(listen, source)).grid(row=1, column=1)
    tk.Button(functions, text='Convert to mp3 and Update DB!', command=partial(
        update_db, genres, emotions, others, source, destination, length, genre_tag)
    ).grid(row=1, column=2)
    tk.Button(functions, text='Delete!', command=partial(remove, source)).grid(row=1, column=3)
    tk.Button(functions, text='Quit', command=root.destroy).grid(row=1, column=4)

    functions.grid(row=3, column=1)

    root.mainloop()