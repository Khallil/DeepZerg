from tools import can_do
from pysc2.lib import actions,units
from unit_tools import unit_type_is_selected
import random

def is_need_queen(obs,nb_queen,nb_hatches, is_coming):
    if nb_queen < nb_hatches:
        if is_coming == False:
                return True

def train_queen(obs,hatches,action):
    if unit_type_is_selected(obs,units.Zerg.Hatchery):
        print("HATCH BUILD QUEUE : ", obs.observation.build_queue)
        if can_do(obs,action):        
            return True,actions.FUNCTIONS.Train_Queen_quick("now")
        else:
            return False,actions.FUNCTIONS.no_op()

    if len(hatches) > 0:
        hatch = random.choice(hatches)
        return False,actions.FUNCTIONS.select_point("select", (hatch.x,hatch.y))
    
    return False,actions.FUNCTIONS.no_op()