from pysc2.agents import base_agent
from pysc2.lib import actions,features,units
import random
from tools_functions import get_enemy_position,get_units_by_type,can_do
from supply_block import build_overlord

class ZergAgent(base_agent.BaseAgent):

    def __init__(self):
        super(ZergAgent, self).__init__()
        self.attack_coordinates = None
        self.nb_overlord = 1
        self.overlord_coming = False

    def step(self, obs):
        super(ZergAgent, self).step(obs)
        
        if obs.first():
            self.attack_coordinates = get_enemy_position(obs)

        overlords = get_units_by_type(obs, units.Zerg.Overlord)
        if len(overlords) > self.nb_overlord:
            self.overlord_coming = False
            self.nb_overlord = len(overlords)

        # Create POOL
        spawning_pools = get_units_by_type(obs, units.Zerg.SpawningPool)
        if len(spawning_pools) == 0:
            if self.unit_type_is_selected(obs, units.Zerg.Drone):
                if can_do(obs,actions.FUNCTIONS.Build_SpawningPool_screen.id):
                    x = random.randint(0, 83)
                    y = random.randint(0, 83)
                    return actions.FUNCTIONS.Build_SpawningPool_screen("now", (x, y))

            drones = get_units_by_type(obs,units.Zerg.Drone)
            if len(drones) > 0:
                drone = random.choice(drones)
                return actions.FUNCTIONS.select_point("select_all_type", (drone.x,drone.y))

        # Create UNIT
        if self.unit_type_is_selected(obs, units.Zerg.Larva):
            # if supply_block soon
            if build_overlord(obs,self.overlord_coming,actions.FUNCTIONS.Train_Overlord_quick.id):
                self.overlord_coming = True
                return actions.FUNCTIONS.Train_Overlord_quick("now")
            
            if can_do(obs,actions.FUNCTIONS.Train_Zergling_quick.id):
                return actions.FUNCTIONS.Train_Zergling_quick("now")

        # Select Larva
        larvae = get_units_by_type(obs,units.Zerg.Larva)
        if len(larvae) > 0:
            larva = random.choice(larvae)
            return actions.FUNCTIONS.select_point("select", (larva.x,larva.y))

        # Attack
        zerglings = get_units_by_type(obs, units.Zerg.Zergling)
        if len(zerglings) > 10:
            if self.unit_type_is_selected(obs, units.Zerg.Zergling):
                if can_do(obs, actions.FUNCTIONS.Attack_minimap.id):
                    return actions.FUNCTIONS.Attack_minimap("now", self.attack_coordinates)
        if len(zerglings) > 10:
            if can_do(obs, actions.FUNCTIONS.select_army.id):
                return actions.FUNCTIONS.select_army("select")

        return actions.FUNCTIONS.no_op()

    def unit_type_is_selected(self, obs, unit_type):
        if (len(obs.observation.single_select) > 0 and
            obs.observation.single_select[0].unit_type == unit_type):
            return True
        
        if (len(obs.observation.multi_select) > 0 and
            obs.observation.multi_select[0].unit_type == unit_type):
            return True
        
        return False
