import time
import model
import midi
import midi.sequencer as sequencer


class Launchpad:
    def __init__(self):
        #get some MIDI ports together
        client, port = sequencer.SequencerHardware().get_client_and_port("Launchpad S", "Launchpad S MIDI 1")
        self.__seq = sequencer.SequencerDuplex()  # sequencer_stream=sequencer.sequencer_alsa.SND_SEQ_NONBLOCK)
        self.__seq.subscribe_read_port(client, port)
        self.__seq.subscribe_write_port(client, port)
        self.__model = model.Model()
        self.__current_column = 0
        self.__old_column = 0
        self.blank()

    def __del__(self):
        self.__current_column = -1
        self.blank()

    def __led_note(self, x, y):
        """returns the value to be used as a 'note' in the MIDI event"""
        return 0x20 + 0x10 * (5-y) + x

    def __led_velocity(self, x, y):
        """returns the value to be used as 'velocity' in the MIDI event"""
        vel = 0x00
        if self.__current_column == x:
            vel += 0x03
        if self.__model.leds[y][x]:
            vel += 0x30
        return vel

    def __led_x_y(self, n):
        n -= 0x20
        y = 5-((0xF0 & n) >> 4)
        x = 0x0F & n
        return x, y

    def blank(self):
        self.__model.zero()
        for col in range(0, self.__model.columns):
            self.__render_column(col)

    def refresh(self, x, y):
        command = midi.NoteOnEvent()
        command.set_pitch(self.__led_note(x, y))
        command.set_velocity(self.__led_velocity(x, y))
        self.__seq.event_write(command, direct=True)

    def __render_column(self, x):
        """colours lights for an entire column at once"""
        for y in range(0, model.Model.rows):
            self.refresh(x, y)

    def new_column(self, column):
        self.__current_column = column
        self.__render_column(self.__current_column)
        self.__render_column(self.__old_column)
        self.__old_column = self.__current_column

    def button_press(self):
        global event
        event = self.__seq.event_read()
        while event is not None:
            if isinstance(event, midi.NoteOnEvent):
                if event.velocity != 0:  # only on key down
                    possibly = self.__led_x_y(event.pitch)
                    if possibly[0] < 0 or possibly[1] < 0 or possibly[0] >= model.Model.columns or possibly[1] >= model.Model.rows:
                        event = self.__seq.event_read()
                        continue
                    return possibly
            event = self.__seq.event_read()
        return None

    def flip(self, x, y):
        self.__model.flip(x, y)

    def selected(self, x, y):
        return self.__model.leds[y][x]
