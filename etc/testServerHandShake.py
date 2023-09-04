# -*- coding: utf-8 -*-
import PipelineTools
import sys
import zmq
if sys.argv[-1] == 'client':

    reqsock = zmq.Context().socket(zmq.REQ)
    reqsock.connect('tcp://127.0.0.1:5555')
    reqsock.send('Hello from client!')
    recv = reqsock.recv()

else:

    repsock = zmq.Context().socket(zmq.REP)
    repsock.bind('tcp://127.0.0.1:5555')
    recv = repsock.recv()

    repsock.send('Hello from server!')
