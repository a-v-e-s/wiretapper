import sqlite3, re, subprocess, pickle


def fined(playlist):
    """ 
    Returns a dictionary of songs from a playlist
    in one of two lists depending on whether or not
    they were found in a search of the sound_files directory
    """

    conn = sqlite3.Connection('music_db.sqlite')
    curs = conn.cursor()
    pl = curs.execute('select title, artist from Pickle where playlist="'+playlist+'";').fetchall()

    songs = list()
    for item in pl:
        part1 = re.sub(r'[^a-zA-Z0-9]', '', re.sub(r'\s\(.+?\)', '', item[0]))
        part2 = re.sub(r'[^a-zA-Z0-9]', '', re.sub(r'\s\(.+?\)', '', item[1]))
        name = '_'.join([part1, part2])
        songs.append(name)
    
    return_dict = dict()
    return_dict['found'] = list()
    return_dict['not_found'] = list()
    for song in songs:
        command = ['find', 'sound_files/', '-type', 'f', '-iname', song+'*']
        p = subprocess.Popen(command, stdout=subprocess.PIPE)
        line = p.stdout.readline()
        if len(line) > 0:
            return_dict['found'].append((song, line))
        else:
            return_dict['not_found'].append((song,))
    
    return return_dict


def update_sqlite_from_pickle():
    """
    I used something like this to update the Pickle table 
    of the Sqlite DB from the Pickle file in one fell swoop.

    I thought I should save it because it might be
    useful again later if I do mess something up...
    """

    conn = sqlite3.Connection('music_db.sqlite')
    curs = conn.cursor()

    unsafe_chars = re.compile(r'[^a-zA-Z0-9]')
    parens = re.compile(r'\s\(.+?\)')

    with open('pan_scrapings.pkl', 'rb') as file:
        db = pickle.load(file)

    for playlist in list(db.keys()):
        for item in db[playlist]:

            part1 = re.sub(unsafe_chars, '', re.sub(parens, '', item[0]))
            part2 = re.sub(unsafe_chars, '', re.sub(parens, '', item[1]))
            name = '_'.join([part1, part2])

            command = ['find', 'sound_files/', '-type', 'f', '-iname', name+'*']
            p = subprocess.Popen(command, stdout=subprocess.PIPE)
            line = p.stdout.readline().rstrip(b'\n').decode('utf8')

            if len(line) > 0:

                if line.startswith('sound_files/mp3s/'):
                    sql_statement = 'UPDATE Pickle set downloaded=1, converted=1 WHERE title="'+item[0]+'";'
                    curs.execute(sql_statement)
                    print('#'*50, sql_statement, sep='\n')
                    
                elif line.startswith('sound_files/wavs/'):
                    sql_statement = 'UPDATE Pickle set downloaded=1 WHERE title="'+item[0]+'";'
                    curs.execute(sql_statement)
                    print('-'*50, sql_statement, sep='\n')


    conn.commit()
    curs.close(); conn.close()



if __name__ == '__main__':    
    
    with open('pan_scrapings.pkl', 'rb') as file:
        db = pickle.load(file)

    for key in db.keys():
        d = fined(key)
        print()
        print(key)
        print('FOUND:', str(len(d['found'])), sep='\t')
        print('NOT FOUND:', str(len(d['not_found'])), sep='\t')