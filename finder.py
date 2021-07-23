import sqlite3, re, subprocess


def fined(playlist):
    """ Returns a list of songs"""
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


if __name__ == '__main__':
    
    import pickle
    
    
    with open('pan_scrapings.pkl', 'rb') as file:
        db = pickle.load(file)

    for key in db.keys():
        d = fined(key)
        print()
        print(key)
        print('FOUND:', str(len(d['found'])), sep='\t')
        print('NOT FOUND:', str(len(d['not_found'])), sep='\t')