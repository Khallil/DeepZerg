from pysc2.lib import actions,units
from unit_tools import get_units_by_type,unit_type_is_selected
from tools import can_do
import random

def build_pool(obs,_x,_y,larvae):
    if unit_type_is_selected(obs,units.Zerg.Drone):
        if can_do(obs,actions.FUNCTIONS.Build_SpawningPool_screen.id):
            x = random.randint(_x-10, _x+10)
            y = random.randint(_y-10, _y+10)
            return actions.FUNCTIONS.Build_SpawningPool_screen("now",(x,y))
            
    drones = get_units_by_type(obs,units.Zerg.Drone)
    if len(drones) > 0:
        drone = random.choice(drones)
        return actions.FUNCTIONS.select_point("select_all_type", (drone.x,drone.y))

    if unit_type_is_selected(obs,units.Zerg.Larva):
        if can_do(obs,actions.FUNCTIONS.Train_Drone_quick.id):
            return actions.FUNCTIONS.Train_Drone_quick("now")

    if len(larvae) > 0:
        larva = random.choice(larvae)
        return actions.FUNCTIONS.select_point("select_all_type", (larva.x,larva.y))

    return actions.FUNCTIONS.no_op()