import mido
from organinstrument import *


class OrganController:
    def __init__(self, port_name):
        self.port = mido.open_output(port_name)
        # Mostly for testing: use organ instrument
        for i in range(0,3):
            instrmsg = mido.Message('program_change', program=16 + i, channel=i)
            self.port.send(instrmsg)

        # Start somewhere in the middle of a range so we don't go for super low note at start
        self.current_note_index = 14
        self.play_ref = True

        # TODO Make a list of instruments and expose it

        self.instrument = OrganInstrument(self.port, 0, "Saxophon 8'", 33)
        self.ref_instrument = OrganInstrument(self.port, 1, "Flöte 4'", 51)


        #self.instrument = OrganInstrument(self.port, 1, "Oboe 8'", 44)
        #self.ref_instrument = OrganInstrument(self.port, 2, "Geige 8'", 102)

        #self.instrument = OrganInstrument(self.port, 2, "Xylophon", 74)
        #self.ref_instrument = OrganInstrument(self.port, 1, "Flöte 4'", 51) 

    @classmethod
    def _get_note_name(cls, currentNote):
        note_names = ['C','C#','D','D#','E','F','F#','G','G#','A','Bb','B']
        # Helmholtz / German notation. Octave indication works differently though
        # note_names = ['c','c#','d','d#','e','f','f#','g','g#','a','b','h']
        root_note = 60
        octave_offset = 2 # Assumption that middle C is C3, lowest is C-2
        index = (currentNote) % 12
        octave = int(currentNote / 12) - octave_offset
        return '{}{}'.format(note_names[index], octave)
    
    @property
    def instrument_name(self):
        return self.instrument.name

    @property
    def ref_instrument_name(self):
        return self.ref_instrument.name
    
    @property
    def is_playing(self):
        return self.instrument.is_playing
    
    def get_note_name(self):
        note_name = self._get_note_name(self.current_note_index)
        return '{:<3} - {}'.format(note_name, self.current_note_index)

    def start(self):
        self.instrument.activate()
        self.ref_instrument.activate()
        note = self.instrument.notes[self.current_note_index]
        self.instrument.play(note)
        self.ref_instrument.play(note)

    def stop_reference(self):
        self.ref_instrument.stop()

    def toggle_pause(self):
        if self.instrument.is_playing:
            self.instrument.stop()
            self.ref_instrument.stop()
        else:
            self._play_note_at_index(self.play_ref)

    def toggle_test(self):
        self.play_ref = not self.play_ref
        print("Playing reference: {}".format(self.play_ref))
        if not self.play_ref and self.ref_instrument.is_playing:
            self.ref_instrument.stop()
        elif self.play_ref and self.instrument.is_playing and not self.ref_instrument.is_playing:
            note = self.instrument.notes[self.current_note_index]
            self.ref_instrument.play(note)

    def stop(self):
        self.instrument.stop()
        self.ref_instrument.stop()
        self.instrument.deactivate()
        self.ref_instrument.deactivate()
        self.port.panic()
        self.port.reset()
        self.port.close()

    def _play_note_at_index(self, play_reference):
        if self.current_note_index < 0:
            self.current_note_index = len(self.instrument.notes) - 1
        elif self.current_note_index >= len(self.instrument.notes):
            self.current_note_index = 0
        self.instrument.stop()
        self.ref_instrument.stop()

        note = self.instrument.notes[self.current_note_index]
        self.instrument.play(note)
        if play_reference:
            self.ref_instrument.play(note)

    def play_next_note(self):
        self.current_note_index += 1
        self._play_note_at_index(self.ref_instrument.is_playing)

    def play_prev_note(self):
        self.current_note_index -= 1
        self._play_note_at_index(self.ref_instrument.is_playing)

    # # Similar to play next note, just doesn't play the reference instrument
    # def test_next_note(self):
    #     self.current_note_index += 1
    #     self._play_note_at_index(False)

    # def test_prev_note(self):
    #     self.current_note_index -= 1
    #     self._play_note_at_index(False)