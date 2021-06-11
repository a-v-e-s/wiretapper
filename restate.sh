#!/bin/bash

counter=0
while read line; do
    let counter++
    if [[ "${line:0:6}" = INSERT ]]; then
        echo "$line"
        sqlite3 music_db.sqlite "$line"
    else
        echo -e "\nLine #$counter does not appear to be an INSERT statement:"
        echo "$line"
        echo -e "Skipping...\n"
    fi
done< <(cat statements.txt)