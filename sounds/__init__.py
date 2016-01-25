import alsaaudio
import wave


class PlayoutObject:

    def __init__(self, playout_fname):
        pw = wave.open(playout_fname, 'rb')
        self.raw_nframes = pw.getnframes()
        self.wavearray = bytearray(self.raw_nframes*4+4096)  # silence at the end
        incoming = pw.readframes(self.raw_nframes)  # copied into the start of the buffer
        self.wavearray[:self.raw_nframes*4] = incoming[:self.raw_nframes*4]
        self.byte = self.raw_nframes*4  # initially silent
        pw.close()

        self.device = alsaaudio.PCM()
        self.device.setchannels(2)
        self.device.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        self.device.setrate(48000)
        self.device.setperiodsize(1024)

    def reset(self):
        self.byte = 0

    def playout_loop(self):
        self.device.write(self.wavearray[self.byte:self.byte+4096])
        self.byte += 4096
        if self.byte > self.raw_nframes*4:  # align with silence in buffer
            self.byte = self.raw_nframes*4
