import os, sys

from eff_word_net.streams import SimpleMicStream
from eff_word_net.engine import HotwordDetector
from eff_word_net.audio_processing import Resnet50_Arc_loss
from eff_word_net import samples_loc

import websockets.protocol
import websockets.exceptions
import websockets.sync.server

import threading
import queue

#hotword = 'mycroft'
#json_path = os.path.join(samples_loc, "mycroft_ref.json")
hotword = 'autobot'
json_path = 'autobot/autobot_ref.json'
msg = 'Ciao, dimmi tutto, ti ascolto'

do_run = True
do_respond = '--do_respond' in sys.argv

def audio_fun():
    global clients_q
    base_model = Resnet50_Arc_loss()

    hw = HotwordDetector(
        hotword=hotword,
        model = base_model,
        reference_file=json_path,
        threshold=0.7,
        relaxation_time=2
    )

    mic_stream = SimpleMicStream(
        window_length_secs=1.5,
        sliding_window_secs=0.75,
    )

    mic_stream.start_stream()

    print("Say", hotword[0].upper() + hotword[1:])

    while do_run:
        frame = mic_stream.getFrame()
        result = hw.scoreFrame(frame)

        if result==None :
            #no voice activity
            continue

        if(result["match"]):
            # Magic word (probably) found!
            print("Wakeword uttered",result["confidence"])
            for l, q in enumerate(clients_q):
                print('advice client', l)
                q.put(hotword)

            if do_respond:
                os.system(f'curl -X POST --data-urlencode "text={msg}" "http://127.0.0.1:5002/api/tts" --output - | aplay')

server = None
client_id = 0
clients_q = []
timeout_sec = 1

def echo_fun(websocket):
    global client_id
    global timeout_sec
    global clients_q

    l = client_id
    client_id += 1
    msg_num = 0
    client_alive = True
    q = queue.Queue()
    clients_q.append(q)

    while True:
        # Always print the state.
        print('fsm', l, 'msg:', msg_num, websocket.state, websocket.close_code, websocket.close_reason)

        if not (do_run and client_alive):
            break

        # Check if the client is still there
        if websocket.state != websockets.protocol.State.OPEN:
            print('fsm', l, 'exiting')
            break

        try:
            # Echo part, left for testing.
            try:
                # Read messages and
                message = websocket.recv(timeout = 0) # sec
                # sent it back,
                websocket.send(message)
            except TimeoutError:
                # sleep in the meanwhile.
                pass

            # Signal the magic word detection.
            try:
                item = q.get(timeout = timeout_sec)
                msg_num += 1
                websocket.send(hotword)
            except queue.Empty:
                # no magic word detected
                pass

        except websockets.exceptions.ConnectionClosedError:
            # Client left, we too...
            client_alive = False

    clients_q.remove(q)

def websock_fun():
    global server
    with websockets.sync.server.serve(echo_fun, "localhost", 8765) as server:
        server.serve_forever()

t_audio = threading.Thread(target = audio_fun)
t_audio.start()

t_websock = threading.Thread(target = websock_fun)
t_websock.start()

input('Press [Enter] to quit\n')
do_run = False
t_audio.join()
server.shutdown()
t_websock.join()
