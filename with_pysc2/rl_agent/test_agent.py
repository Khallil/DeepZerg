from pysc2.agents import base_agent
from pysc2.lib import actions
from time import sleep
from threading import Thread
import signal
import sys

haveCheckBases = False
thread_pause = False

def signal_handler(signal, frame):
    global thread_pause
    print('You pressed Ctrl+C!')
    #thread_pause = True
    exit(0)

signal.signal(signal.SIGINT, signal_handler)

def changeCheckBases():
    global thread_pause
    global haveCheckBases
    while True:
        while not thread_pause:
            sleep(10)
            print("change haveCheckBase to False")
            haveCheckBases = False

class TestAgent(base_agent.BaseAgent):

    def __init__(self):
        super(TestAgent, self).__init__()
        self.thread = Thread(target = changeCheckBases)
        self.thread.setDaemon(True)
        self.thread.start()

    def step(self, obs):
        global haveCheckBases
        global thread_pause

        super(TestAgent, self).step(obs)
        if obs.first():
            thread_pause = False

        if obs.last():
            thread_pause = True

        if haveCheckBases == False:
            # set un boolean pour savoir quand on fini les obs print("Set haveCheckBases to True")
            # run les mises a jour des cc_group si on_base = True
                # pour eviter de surcharger les groupes de controles
                    # pendant qu'on est sur les bases on verifie si essential_bat exist
            # set un boolean pour savoir quand on fini les obs
            # si boolean = True on set haveCheckBases a True
            # si haveCheckBases est set a True
            # on bouge la cam on se balade
            haveCheckBases = True

        return actions.FUNCTIONS.no_op()