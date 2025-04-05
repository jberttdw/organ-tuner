import mido
from time import sleep

# Activates an instrument on the organ.
# In the case of the organ at SMMK we need to send a note on the highest MIDI channel.
class OrganInstrument:
    def __init__(self, port, channel_id, name, activation_note):
        self.port = port
        self.channel_id = channel_id
        self.name = name
        self.activation_note = activation_note
        self.current_note = -1
        if channel_id == 0:
            self._notes = list(range(36,66))
        else:
            self._notes = list(range(36,97))

    @property
    def notes(self):
        return self._notes
    
    @property
    def is_playing(self):
        return self.current_note > -1

    def activate(self):
        msg = mido.Message('note_on', channel=15, note=self.activation_note, velocity=1)
        self.port.send(msg)

    def deactivate(self):
        msg = mido.Message('note_off', channel=15, note=self.activation_note)
        self.port.send(msg)

    def play(self, note):
        if not (note in self.notes):
            raise "Note out of range"
        if (self.current_note != -1):
            msg = mido.Message('note_off', channel=self.channel_id, note=self.current_note)
            self.port.send(msg)
        sleep(0.001)
        print("Playing note {} on channel {}".format(note, self.channel_id))
        msg = mido.Message('note_on', channel=self.channel_id, note=note, velocity=127)
        self.port.send(msg)
        self.current_note = note

    def stop(self):
        if (self.current_note != -1):
            msg = mido.Message('note_off', channel=self.channel_id, note=self.current_note)
            self.port.send(msg)
            self.current_note = -1