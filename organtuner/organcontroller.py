import mido
from organtuner.organinstrument import *


class OrganController:
    def __init__(self, port_name):
        self.port = mido.open_output(port_name)
        # Mostly for testing: use organ instrument
        for i in range(0,3):
            instrmsg = mido.Message('program_change', program=16 + i, channel=i)
            self.port.send(instrmsg)

        # Start an octave up from start of range so we don't go for super low note at start
        self.safe_start_note_index = 14
        self.current_note_index = self.safe_start_note_index

        self.cycled_notes = 0
        self._play_ref = True
        self._instrument_n = 0

        ch1flute4 = OrganInstrument(self.port, 1, "Flöte 4'", 51)
        ch1travflute8 = OrganInstrument(self.port, 1, "Travers Flöte 8'", 41)
        ch2travflute8 = OrganInstrument(self.port, 2, "Travers Flöte 8'", 41)
        ch2geige4 = OrganInstrument(self.port, 2, "Geige 4'", 109)
        ch1geige8 = OrganInstrument(self.port, 1, "Geige 8'", 39)
        ch2geige8 = OrganInstrument(self.port, 2, "Geige 8'", 102)
        # "Instruments" which don't activate anything, let console decide
        ch0spieltisch = OrganInstrument(self.port, 1, "Spieltisch Pedal", None)
        ch1spieltisch = OrganInstrument(self.port, 1, "Spieltisch Man I", None)
        ch2spieltisch = OrganInstrument(self.port, 2, "Spieltisch Man II", None)

        self._current_instrument_index = 0
        self._instruments = [
                (ch2spieltisch, ch1spieltisch),
                (ch1spieltisch, ch2spieltisch),
                (ch0spieltisch, ch1spieltisch),
                (OrganInstrument(self.port, 2, "Saxophon 8'  ", 107), ch1flute4),
                #(OrganInstrument(self.port, 1, "Saxophon 8'  ", 46), ch2geige4),
                (OrganInstrument(self.port, 2, "VoxHumana 16'", 100, range(48,97)), ch1travflute8),
                #(OrganInstrument(self.port, 2, "VoxHumana 16'", 100, range(48,97)), ch1geige8),
                (OrganInstrument(self.port, 2, "Oboe 8'", 106), ch1flute4),
                #(OrganInstrument(self.port, 1, "Oboe 8'", 44), ch2geige4),
                (OrganInstrument(self.port, 2, "Xylophon", 74, range(60,85)), ch1travflute8),
                (ch2geige4, ch1travflute8),
                (ch1flute4, ch2geige4),
                (ch1travflute8, ch2geige4),
                (OrganInstrument(self.port, 1, "Flöte 16'", 36), ch2geige8),
            ]
        
        self._instrument, self._ref_instrument = self._instruments[self._instrument_n]
 
        instrument_names = []
        for instrument in self._instruments:
            instrument_names.append(instrument[0].name)
        self._instrument_names = instrument_names

    @property
    def instrument_names(self):
        return self._instrument_names
    
    @property
    def instrument_n_active(self):
        return self._instrument_n

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
    
    @property
    def is_ref_active(self):
        return self._play_ref

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

        #note = self._instrument.notes[self.current_note_index]
        #self._instrument.play(note)
        #if self._play_ref:
        #    self._ref_instrument.play(note)

    def stop_reference(self):
        self._ref_instrument.stop()

    def toggle_pause(self):
        if self._instrument.is_playing:
            self._instrument.stop()
            self._ref_instrument.stop()
        else:
            self._play_note_at_index()

    def toggle_test(self):
        self._play_ref = not self._play_ref
        print("Playing reference: {}".format(self._play_ref))
        if not self._play_ref and self._ref_instrument.is_playing:
            self._ref_instrument.stop()
        elif self._play_ref and self._instrument.is_playing and not self._ref_instrument.is_playing:
            note = self._instrument.notes[self.current_note_index]
            self._ref_instrument.play(note)

    def _play_note_at_index(self):
        note = self._instrument.notes[self.current_note_index]
        self._instrument.play(note)
        if self._play_ref:
            self._ref_instrument.play(note)

    def _move_to_note_at_index(self):
        # TODO Trigger "ta-daa" action while sticking to end of range
        if self.current_note_index < 0:
            self.current_note_index = self.safe_start_note_index
        elif self.current_note_index >= len(self._instrument.notes):
            self.current_note_index = self.safe_start_note_index

        play_new = False
        if self._instrument.is_playing:
            self._instrument.stop()
            self._ref_instrument.stop()
            play_new = True

        if play_new:
            self._play_note_at_index()

    def play_next_note(self):
        self.current_note_index += 1
        self._move_to_note_at_index()

    def play_prev_note(self):
        self.current_note_index -= 1
        self._move_to_note_at_index()

    def stop(self):
        self._instrument.stop()
        self._ref_instrument.stop()
        self._instrument.deactivate()
        self._ref_instrument.deactivate()
        self.port.panic()
        self.port.reset()
        self.port.close()

    def switch_instrument(self, index):
        play_new = False
        if self._instrument.is_playing:
            self._instrument.stop()
            self._ref_instrument.stop()
            play_new = True

        self._instrument.deactivate()
        self._ref_instrument.deactivate()

        self.current_note_index = self.safe_start_note_index
        if index < 0 or index > len(self._instruments):
            index = 0
        self._current_instrument_index = index
        self._instrument, self._ref_instrument = self._instruments[self._current_instrument_index]

        self._instrument.activate()
        self._ref_instrument.activate()

        if play_new:
            self.toggle_pause()