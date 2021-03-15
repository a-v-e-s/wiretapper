#!/bin/bash

sqlite3 $$_`date +%s`.sqlite "CREATE TABLE Songs( \
title text primary key, \
artist text, \
album text, \
length real, \
synth int default 0, \
hard_rock int default 0, \
metal int default 0, \
gothish int default 0, \
indie int default 0, \
pop int default 0, \
cerebral int default 0, \
dance int default 0, \
disco int default 0, \
house int default 0, \
trance int default 0, \
industrial int default 0, \
new_age int default 0, \
ambient int default 0, \
classical int default 0, \
contemporary int default 0, \
emo int default 0, \
classic_rock int default 0, \
alt_rock int default 0, \
romantic int default 0, \
funny int default 0, \
melancholy int default 0, \
angry int default 0, \
happy int default 0, \
hypnotic int default 0, \
reggae int default 0, \
hip_hop int default 0, \
hardcore_rap int default 0, \
rb int default 0, \
psychedelic int default 0, \
country int default 0, \
classic_rb int default 0, \
instrumental int default 0, \
foreign_language int default 0 \
)" || exit $?