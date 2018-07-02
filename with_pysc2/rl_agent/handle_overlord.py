from unit_tools import unit_type_is_selected
import random
from tools import can_do
from pysc2.lib import actions,units


def is_supply_block(obs,is_coming):
    free_supply = (obs.observation.player.food_cap - obs.observation.player.food_used)
    if free_supply < 3:
        if is_coming == False:
            return True

'''
    TODO
    # for handle the case if lot of overlords has been killed
    # # free_supply would be negative
    supply_by_overlord = 8
    nb_overlord_to_create = abs(free_supply)/supply_by_overlord + 1
    # si le nombre n'est pas suffisant pour fill le nb_overlord_to_create
    # on garde overlord_coming a false jusqu'a que ce soit bon

+ Prendre en compte que ces units comptent aussi : 
    OverlordTransport = 893
    OverlordTransportCocoon = 892
    Overseer = 129
    OverseerCocoon = 128
    OverseerOversightMode = 1912
'''


def train_overlord(obs,larvae,action):
    if unit_type_is_selected(obs,units.Zerg.Larva):
        if can_do(obs,action):
            return True,actions.FUNCTIONS.Train_Overlord_quick("now")
        else:
            return False,actions.FUNCTIONS.no_op()

    if len(larvae) > 0:
        larva = random.choice(larvae)
        return False,actions.FUNCTIONS.select_point("select_all_type", (larva.x,larva.y))
    
    return False,actions.FUNCTIONS.no_op()