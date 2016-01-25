# requires:
# midi==0.2.3
# pyalsaaudio==0.8.2

import model
import time
import launchpad
import sounds
import os

# get the number of the sample bank we're opening
last_played_file = None
if not os.path.exists("last_played_id"):
    last_played_file = open("last_played_id","w")
    last_played_file.close()
last_played_file = open("last_played_id")
last_played = last_played_file.read()
if len(last_played) > 0:
    last_id = int(last_played)
else:
    last_id = -1
last_played_file.close()
this_id = last_id + 1
if not os.path.exists("samples/%d/" % this_id):
    this_id = 0

# remember which one we played this time
last_played_write = open("last_played_id", "w")
last_played_write.write(str(this_id))
last_played_write.close()

# find the tempo
tempo_file = open("samples/%d/tempo" % (this_id,))
tempo_string = tempo_file.read()
tempo = 120
if len(tempo_string) > 0:
    tempo = int(tempo_string)
tempo_file.close()
iteration_period = 60.0/tempo
total_iterations = 300/iteration_period

# create the objects
play_objects = [sounds.PlayoutObject("samples/%d/%d.wav" % (this_id, n)) for n in range(0, 6)]
lpd = launchpad.Launchpad()

try:
    os.setpriority(os.PRIO_PROCESS, os.getpid(), -8)
except:
    pass

start_time = time.time()
iteration = -1
while iteration < total_iterations:
    iteration += 1
    current_column = iteration % 8

    # start making the right combination of noises
    for n in range(0, model.Model.rows):
        if lpd.selected(current_column, n):
            play_objects[n].reset()

    # loop until it's time not to
    loops = int((48000.0*iteration_period)/1024.0)
    while loops:

        # render
        lpd.new_column(current_column)

        # give the playback objects a timeslice
        for n in range(0, model.Model.rows):
            play_objects[n].playout_loop()

        # check for button presses
        press = lpd.button_press()
        while press is not None:
            lpd.flip(press[0], press[1])
            lpd.refresh(press[0], press[1])
            press = lpd.button_press()

        loops -= 1