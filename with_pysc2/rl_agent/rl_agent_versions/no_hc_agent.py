import random
import math

from pysc2.agents import base_agent
from pysc2.lib import actions,features,units
from tools_functions import get_enemy_position,get_units_by_type,can_do
from supply_block import build_overlord
from qlearning_table import QLearningTable

# FULL RLearning, 0 handcraft rules

ACTION_DO_NOTHING = 'donothing'
ACTION_SELECT_LARVA = 'selectlarva'
ACTION_SELECT_DRONE = 'selectdrone'
ACTION_BUILD_OVERLORD = 'buildoverlord'
ACTION_BUILD_POOL = 'buildpool'
ACTION_BUILD_ZERGLING = 'buildzergling'
ACTION_SELECT_ARMY = 'selectarmy'
ACTION_ATTACK = 'attack'

smart_actions = [
    ACTION_DO_NOTHING,
    ACTION_SELECT_LARVA,
    ACTION_SELECT_DRONE,
    ACTION_BUILD_OVERLORD,
    ACTION_BUILD_POOL,
    ACTION_BUILD_ZERGLING,
    ACTION_SELECT_ARMY,
    ACTION_ATTACK,
]

KILL_UNIT_REWARD = 0.2
KILL_BUILDING_REWARD = 0.5
PRODUCE_ARMY_UNIT = 0.5

# Without handcraft rules
class SmartAgent(base_agent.BaseAgent):

    def __init__(self):
        super(SmartAgent, self).__init__()
        self.attack_coordinates = None
        self.player_pos = None
        self.base_top_left = None
        self.qlearn = QLearningTable(actions=list(range(len(smart_actions))))

        self.previous_killed_unit_score = 0
        self.previous_killed_building_score = 0
        self.previous_army_supply = 0
        self.previous_action = None
        self.previous_state = None
    
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
            self.attack_coordinates = get_enemy_position(obs)
            self.player_pos = (obs.observation.feature_minimap.player_relative ==
                        features.PlayerRelative.SELF).nonzero()

            self.base_top_left = 1 if self.player_pos[0].any() and self.player_pos[0].mean() <= 31 else 0

        # Set state 
        overlord_count = len(get_units_by_type(obs,units.Zerg.Overlord))
        pool_count = len(get_units_by_type(obs,units.Zerg.SpawningPool))
        supply_limit = obs.observation.player.food_cap
        army_supply = obs.observation.player.food_army

        current_state = [
            overlord_count,
            pool_count,
            supply_limit,
            army_supply,
        ]

        # Catch if units or building have been killed
        reward = 0
        killed_unit_score = obs.observation.score_cumulative.killed_value_units
        killed_building_score = obs.observation.score_cumulative.killed_value_structures

        if self.previous_action is not None:
            if killed_unit_score > self.previous_killed_unit_score:
                reward += KILL_UNIT_REWARD
            
            if killed_building_score > self.previous_killed_building_score:
                reward += KILL_BUILDING_REWARD

            if army_supply > self.previous_army_supply:
                reward += PRODUCE_ARMY_UNIT

            self.qlearn.learn(str(self.previous_state), self.previous_action, reward, str(current_state))
        
        #random : smart_action = smart_actions[random.randrange(0, len(smart_actions) - 1)]
        rl_action = self.qlearn.choose_action(str(current_state))
        smart_action = smart_actions[rl_action]

        self.previous_killed_unit_score = killed_unit_score
        self.previous_killed_building_score = killed_building_score
        self.previous_army = army_supply
        self.previous_state = current_state
        self.previous_action = rl_action

        if smart_action == ACTION_DO_NOTHING:
            return actions.FUNCTIONS.no_op()
        elif smart_action == ACTION_SELECT_LARVA:
            larvae = get_units_by_type(obs,units.Zerg.Larva)
            if len(larvae) > 0:
                larva = random.choice(larvae)
                return actions.FUNCTIONS.select_point("select", (larva.x,larva.y))
        elif smart_action == ACTION_SELECT_DRONE:
            drones = get_units_by_type(obs,units.Zerg.Drone)
            if len(drones) > 0:
                drone = random.choice(drones)
                return actions.FUNCTIONS.select_point("select", (drone.x,drone.y))
        elif smart_action == ACTION_BUILD_OVERLORD:
            if self.unit_type_is_selected(obs,units.Zerg.Larva):
                if can_do(obs,actions.FUNCTIONS.Train_Overlord_quick.id):
                    return actions.FUNCTIONS.Train_Overlord_quick("now")
        elif smart_action == ACTION_BUILD_POOL:
            if self.unit_type_is_selected(obs,units.Zerg.Drone):
                if can_do(obs,actions.FUNCTIONS.Build_SpawningPool_screen.id):
                    x = random.randint(0, 83)
                    y = random.randint(0, 83)
                    return actions.FUNCTIONS.Build_SpawningPool_screen("now", (x, y))
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