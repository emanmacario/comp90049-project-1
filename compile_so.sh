#!/usr/bin/env bash
gcc -shared -Wl,-soname,edit_distance -o edit_distance.so -fPIC edit_distance.c