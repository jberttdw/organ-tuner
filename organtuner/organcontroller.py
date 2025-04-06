import mido
from organtuner.organinstrument import *


class OrganController:
    def __init__(self, port_name):
        self.port = mido.open_output(port_name)
        # Mostly for testing: use organ instrument
        for i in range(0,3):
            instrmsg = mido.Message('program_change', program=16 + i, channel=i)
            self.port.send(instrmsg)

        # Start somewhere in the middle of a range so we don't go for super low note at start
        self.current_note_index = 14

        self.cycled_notes = 0
        self._play_ref = True

        flute4 = OrganInstrument(self.port, 1, "Flöte 4'", 51)
        travflute8 = OrganInstrument(self.port, 1, "Travers Flöte 8'", 41)

        self._current_instrument_index = 0
        self._instruments = [
                (OrganInstrument(self.port, 2, "Saxophon 8'  ", 107), flute4),
                (OrganInstrument(self.port, 2, "VoxHumana 16'", 100), travflute8),
                (OrganInstrument(self.port, 2, "Oboe 8'", 106), flute4),
                (OrganInstrument(self.port, 2, "Xylophon", 74), flute4),
            ]
        
        self._instrument, self._ref_instrument = self._instruments[0]
 
        instrument_names = []
        for instrument in self._instruments:
            instrument_names.append(instrument[0].name)
        self._instrument_names = instrument_names

    @property
    def instrument_names(self):
        return self._instrument_names

    @property
    def instrument_name(self):
        return self._instrument.name

    @property
    def ref_instrument_name(self):
        return self._ref_instrument.name
    
    @property
    def is_playing(self):
        return self._instrument.is_playing
    
    @property
    def is_ref_playing(self):
        return self._ref_instrument.is_playing

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
    
    def get_note_name(self):
        note = self._instrument.notes[self.current_note_index]
        note_name = self._get_note_name(note)
        return '{:<3} - {}'.format(note_name, note)

    def start(self):
        self._instrument.activate()
        self._ref_instrument.activate()
        note = self._instrument.notes[self.current_note_index]
        self._instrument.play(note)
        if self._play_ref:
            self._ref_instrument.play(note)

    def stop_reference(self):
        self._ref_instrument.stop()

    def toggle_pause(self):
        if self._instrument.is_playing:
            self._instrument.stop()
            self._ref_instrument.stop()
        else:
            self._play_note_at_index(self._play_ref)

    def toggle_test(self):
        self._play_ref = not self._play_ref
        print("Playing reference: {}".format(self._play_ref))
        if not self._play_ref and self._ref_instrument.is_playing:
            self._ref_instrument.stop()
        elif self._play_ref and self._instrument.is_playing and not self._ref_instrument.is_playing:
            note = self._instrument.notes[self.current_note_index]
            self._ref_instrument.play(note)

    def _play_note_at_index(self, play_reference):
        if self.current_note_index < 0:
            self.current_note_index = len(self._instrument.notes) - 1
        elif self.current_note_index >= len(self._instrument.notes):
            self.current_note_index = 0
        self._instrument.stop()
        self._ref_instrument.stop()

        note = self._instrument.notes[self.current_note_index]
        self._instrument.play(note)
        if play_reference:
            self._ref_instrument.play(note)

    def play_next_note(self):
        self.current_note_index += 1
        self._play_note_at_index(self._ref_instrument.is_playing)

    def play_prev_note(self):
        self.current_note_index -= 1
        self._play_note_at_index(self._ref_instrument.is_playing)

    def stop(self):
        self._instrument.stop()
        self._ref_instrument.stop()
        self._instrument.deactivate()
        self._ref_instrument.deactivate()
        self.port.panic()
        self.port.reset()
        self.port.close()

    def switch_instrument(self, index):
        self.stop()
        if index < 0 or index > len(self._instruments):
            self._current_instrument_index = 0
        self._instrument, self._ref_instrument = self._instruments[self._current_instrument_index]
        self.start()