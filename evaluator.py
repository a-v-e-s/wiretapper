#!/usr/bin/env python3

import os
import sqlite3
import pickle
import eyed3
import pydub
import tkinter as tk
from tkinter.filedialog import askopenfilename, askdirectory
from sys import exc_info
from functools import partial


def listen(src):
    os.popen('xdg-open ' + src.get())


def convert_to_mp3(src, dst):
    transitional = pydub.AudioSegment.from_mp3(src)
    transitional.export(dst, format='mp3')


def meta_data_tag(fn, title, artist, album, genre):
    file = eyed3.load(fn)
    file.tag.title = title
    file.tag.artist = artist
    file.tag.album = album
    file.tag.genre = genre

    file.tag.save()


def update_db(genres, emotions, others, source, destination):
    conn = sqlite3.Connection('music_db.sqlite')
    curs = conn.cursor()

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

    statement = 'INSERT INTO Songs(filepath, title, artist, album, length, '

    for col in columns:
        statement += (col + ', ')
    statement = statement[:-2] + ') VALUES ("'+fn+'", "'+title.get()+'", "'+artist.get()+'", "'+album.get()+'", '+str(length.get())+', '
    for col in columns:
        statement += '1, '
    statement = statement[:-2] + ');'

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

    conn = sqlite3.Connection('music_db.sqlite')
    curs = conn.cursor()
    table_info = curs.execute('pragma table_info(Songs);').fetchall()
    curs.close(); conn.close()

    emotion_attrs = ['romantic', 'funny', 'melancholy', 'angry', 'happy', 'hypnotic']
    other_attrs = ['cerebral', 'foreign_language', 'instrumental', 'confirmed']
    genre_attrs = [
        'synth', 'hard_rock', 'metal', 'gothish', 'indie', 'pop', 'dance', 'disco', 'house', 'trance',
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
    tk.Button(files, text='Browse', command=(lambda x=src: [x.delete(0, len(x.get())), x.insert(0, askopenfilename())])).grid(row=2, column=2)

    destination = tk.StringVar()
    tk.Label(files, text='Destination:').grid(row=3, column=1, columnspan=2)
    dst = tk.Entry(files, bg='white', width=72, textvariable=destination)
    dst.grid(row=4, column=1)
    tk.Button(files, text='Browse', command=(lambda x=dst: [x.delete(0, len(x.get())), x.insert(0, askdirectory())])).grid(row=4, column=2)

    files.grid(row=1, column=1)

    attributes = tk.LabelFrame(root, text='Attributes:')

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
            #raise LookupError(data)
            o_rownum += 1
            if o_rownum % 7 == 0:
                o_rownum = 1
                o_colnum += 2
            others[data] = var
            tk.Label(other_frame, text=data[1]).grid(row=o_rownum, column=o_colnum)
            tk.Checkbutton(other_frame, variable=var, offvalue=0, onvalue=1).grid(row=o_rownum, column=o_colnum)

    genre_frame.grid(row=1, column=1)
    emotion_frame.grid(row=1, column=2)
    other_frame.grid(row=1, column=3)

    attributes.grid(row=2, column=1)

    functions = tk.LabelFrame(root, text='Fuctions:')
    
    tk.Button(functions, text='Listen', command=partial(listen, src)).grid(row=1, column=1)
    tk.Button(functions, text='Update!', command=partial(update_db, genres, emotions, others, source, destination))

    functions.grid(row=3, column=1)

    root.mainloop()