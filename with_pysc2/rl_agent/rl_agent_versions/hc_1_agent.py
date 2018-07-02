import random
import math

from pysc2.agents import base_agent
from pysc2.lib import actions,features,units
from tools_functions import get_both_position,get_units_by_type,can_do
from supply_block import build_overlord
from qlearning_table import QLearningTable

# HANDCRAFT V1 : 
# Train d'overlord
# Build pool

ACTION_DO_NOTHING = 'donothing'
ACTION_SELECT_LARVA = 'selectlarva'
ACTION_BUILD_ZERGLING = 'buildzergling'
ACTION_SELECT_ARMY = 'selectarmy'
ACTION_ATTACK = 'attack'

smart_actions = [
    ACTION_DO_NOTHING,
    ACTION_SELECT_LARVA,
    ACTION_BUILD_ZERGLING,
    ACTION_SELECT_ARMY,
    ACTION_ATTACK,
]

KILL_UNIT_REWARD = 0.2
KILL_BUILDING_REWARD = 0.5
PRODUCE_ARMY_UNIT = 0.3
UNIT_DEATH = -0.3

# Without handcraft rules
class SmartAgent(base_agent.BaseAgent):

    def __init__(self):
        super(SmartAgent, self).__init__()
        self.attack_coordinates = None
        self.ppmean = None
        self.base_top_left = None
        self.qlearn = QLearningTable(actions=list(range(len(smart_actions))))
        self.drone_selected = False

        self.previous_killed_unit_score = 0
        self.previous_killed_building_score = 0
        self.previous_army_supply = 0
        self.previous_action = None
        self.previous_state = None
        
        self.nb_overlord = 1
        self.overlord_coming = False
    
    def transformLocation(self, x, x_distance, y, y_distance):
        if not self.base_top_left:
            return [x - x_distance, y - y_distance]
        return [x + x_distance, y + y_distance]
    
    def step(self, obs):
        super(SmartAgent, self).step(obs)

        # init position variable at the first obs
        if obs.first():
            print("\nQLearn : \n")
            print(self.qlearn.q_table)
            both_pos = get_both_position(obs)
            self.attack_coordinates = both_pos[0]
            self.ppmean = both_pos[1]
            self.base_top_left = 1 if self.ppmean[1] <= 31 else 0

            with open("screen.txt",'w') as file:
                for item in obs.observation.feature_minimap.player_relative:
                    file.write(str(item)+"\n")

        overlords = get_units_by_type(obs, units.Zerg.Overlord)

        if len(overlords) > self.nb_overlord:
            self.overlord_coming = False
            self.nb_overlord = len(overlords)
        
        # Set state 
        army_supply = obs.observation.player.food_army

        current_state = [
            army_supply,
        ]

        # Catch if units or building have been killed
        reward = 0
        killed_unit_score = obs.observation.score_cumulative.killed_value_units
        killed_building_score = obs.observation.score_cumulative.killed_value_structures

        # We handle the POOL
        spawning_pools = get_units_by_type(obs, units.Zerg.SpawningPool)
        if len(spawning_pools) == 0:
            if self.unit_type_is_selected(obs,units.Zerg.Drone):
                if can_do(obs,actions.FUNCTIONS.Build_SpawningPool_screen.id):
                    _x = self.ppmean[1]
                    _y = self.ppmean[0]
                    x = random.randint(_x-10, _x+10) #a optimiser
                    y = random.randint(_y-10, _y+10) #a optimiser
                    return actions.FUNCTIONS.Build_SpawningPool_screen("now",(x,y))
                    
            drones = get_units_by_type(obs,units.Zerg.Drone)
            if len(drones) > 0:
                drone = random.choice(drones)
                return actions.FUNCTIONS.select_point("select_all_type", (drone.x,drone.y))

            if self.unit_type_is_selected(obs,units.Zerg.Larva):
                if can_do(obs,actions.FUNCTIONS.Train_Drone_quick.id):
                    return actions.FUNCTIONS.Train_Drone_quick("now")

            larvae = get_units_by_type(obs,units.Zerg.Larva)
            if len(larvae) > 0:
                larva = random.choice(larvae)
                return actions.FUNCTIONS.select_point("select_all_type", (larva.x,larva.y))
        
            return actions.FUNCTIONS.no_op()

        # We handle the Supply  
        if build_overlord(obs,self.overlord_coming,actions.FUNCTIONS.Train_Overlord_quick.id):
            if self.unit_type_is_selected(obs,units.Zerg.Larva):
                self.overlord_coming = True
                return actions.FUNCTIONS.Train_Overlord_quick("now")
            
            larvae = get_units_by_type(obs,units.Zerg.Larva)
            if len(larvae) > 0:
                larva = random.choice(larvae)
                return actions.FUNCTIONS.select_point("select_all_type", (larva.x,larva.y))
            
            return actions.FUNCTIONS.no_op()
     
        # Learn from state
        if self.previous_action is not None:
            if killed_unit_score > self.previous_killed_unit_score:
                reward += KILL_UNIT_REWARD
            
            if killed_building_score > self.previous_killed_building_score:
                reward += KILL_BUILDING_REWARD

            if army_supply > self.previous_army_supply:
                reward += PRODUCE_ARMY_UNIT

            if army_supply < self.previous_army_supply:
                reward += UNIT_DEATH
            
            self.qlearn.learn(str(self.previous_state), self.previous_action, reward, str(current_state))
        
        # Choose action
        rl_action = self.qlearn.choose_action(str(current_state))
        smart_action = smart_actions[rl_action]
        
        # Update state
        self.previous_killed_unit_score = killed_unit_score
        self.previous_killed_building_score = killed_building_score
        self.previous_army = army_supply
        self.previous_state = current_state
        self.previous_action = rl_action

        # if p_smart_action == attack
            # means that army is already selected
            # Learn from state
            # Choose action
            # Update state
            # return attack

        # if smart_action = attack
            # p_smart_action = attack
            # return select_army
        


        if smart_action == ACTION_DO_NOTHING:
            return actions.FUNCTIONS.no_op()
        elif smart_action == ACTION_SELECT_LARVA:
            larvae = get_units_by_type(obs,units.Zerg.Larva)
            if len(larvae) > 0:
                larva = random.choice(larvae)
                return actions.FUNCTIONS.select_point("select", (larva.x,larva.y))
        elif smart_action == ACTION_BUILD_ZERGLING:
            if self.unit_type_is_selected(obs,units.Zerg.Larva):
                if can_do(obs,actions.FUNCTIONS.Train_Zergling_quick.id):
                    return actions.FUNCTIONS.Train_Zergling_quick("now")
        elif smart_action == ACTION_SELECT_ARMY:
            if can_do(obs, actions.FUNCTIONS.select_army.id):
                return actions.FUNCTIONS.select_army("select")
        elif smart_action == ACTION_ATTACK:
            if self.unit_type_is_selected(obs, units.Zerg.Zergling):
                if can_do(obs, actions.FUNCTIONS.Attack_minimap.id):
                    return actions.FUNCTIONS.Attack_minimap("now", self.attack_coordinates)

        return actions.FUNCTIONS.no_op()

    def unit_type_is_selected(self, obs, unit_type):
        if (len(obs.observation.single_select) > 0 and
            obs.observation.single_select[0].unit_type == unit_type):
            return True
        
        if (len(obs.observation.multi_select) > 0 and
            obs.observation.multi_select[0].unit_type == unit_type):
            return True
        return False