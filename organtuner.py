#!/usr/bin/env python3

# Don't forget to run `pip install mido rtmidi`
# Also, connecting a remote shutter might take some work, maybe even the 'evdev' package:
# https://stackoverflow.com/questions/54745576/detecting-the-buttons-on-a-bluetooth-remote-hid-over-gatt

import mido
#import evdev
import argparse
import time

# How long to wait between notes when holding down a key
progressDelay = 0.2

ports = mido.get_output_names()

portinfo = "Available ports:\n" + ''.join(map(lambda port: "- " + port + "\n", ports))
print(portinfo)

argparser = argparse.ArgumentParser(prog="organtuner")
#argparser.add_argument("-trigger", help="File path to /dev/input/X to which this script will listen. Leave out for keyboard trigger.")
argparser.add_argument("port", help="Name of port corresponding to the device to which MIDI notes are sent. ")
argparser.add_argument("channel", help="MIDI channel to send to.", type=int, choices=range(1, 4))

args = argparser.parse_args()

port = mido.open_output(args.port)
print(f"Port {args.port} opened")



# Based on https://stackoverflow.com/a/510404 to be able to test this on Windows
class _Getch:
    """Gets a single character from standard input.  Does not echo to the screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getwch().encode()
    
def get_note_name(currentNote):
    note_names = ['C','C#','D','D#','E','F','F#','G','G#','A','Bb','B']
    # Helmholtz / German notation. Octave indication works differently though
    # note_names = ['c','c#','d','d#','e','f','f#','g','g#','a','b','h']
    root_note = 60
    octave_offset = 2 # Assumption that middle C is C3, lowest is C-2
    index = (currentNote) % 12
    octave = int(currentNote / 12) - octave_offset
    return '{}{}'.format(note_names[index], octave)


getch = _Getch()

outChannel = (args.channel - 1)

if (args.channel == 0):
    notes = list(range(36,66))
    currentNoteIndex = 14
else:
    notes = list(range(36,97))
    currentNoteIndex = 14

maxNoteIndex = len(notes)
currentNote = notes[currentNoteIndex]
currentNoteName = get_note_name(currentNote)

# Mostly for testing: use organ instrument
instrmsg = mido.Message('program_change', program=16, channel=outChannel)
port.send(instrmsg)

try:

    # Program can only be interrupted by Ctrl+C
    while True:
        msg = mido.Message('note_on', channel=outChannel, note=currentNote)
        port.send(msg)
        print('Sounding {:<3} - {}'.format(currentNoteName, currentNote))

        time.sleep(progressDelay)

        char = getch()
        # For Windows, Linux might raise a keyboard interrupt exception anyway
        if (char[0] == 3):
            raise KeyboardInterrupt()

        msg = mido.Message('note_off', channel=outChannel, note=currentNote)
        port.send(msg)

        currentNoteIndex += 1
        if (currentNoteIndex >= maxNoteIndex):
            currentNoteIndex = 0
        currentNote = notes[currentNoteIndex]
        currentNoteName = get_note_name(currentNote)

finally:
        print("Turning off all notes")
        port.panic()
        port.reset()
        port.close()

