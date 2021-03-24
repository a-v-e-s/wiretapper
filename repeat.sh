#!/bin/bash

kill `pidof sox` `pidof pacat`

if [[ -n "$1" ]]; then
  rm "$1"
fi