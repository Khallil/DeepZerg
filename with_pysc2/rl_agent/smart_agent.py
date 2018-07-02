import random
import signal
from threading import Thread
from time import sleep

from pysc2.agents import base_agent
from pysc2.lib import actions,features,units

from unit_tools import get_units_by_type,unit_type_is_selected,get_base_position
from tools import can_do,get_both_position
from .handle_pool import build_pool
from .handle_overlord import is_supply_block,train_overlord
from .handle_queen import is_need_queen,train_queen
from .qlearning_table import QLearningTable
from .control_group import ControlGroup

#from .control_group import ControlGroup

# HANDCRAFT V2 : 
# Train d'overlord
# Building pool
# Select Larva and Army units before specific smart_actions
# Train Queen
# Inject Larvae

# Debug : python -m pysc2.bin.play --map Simple64

ACTION_DO_NOTHING = 'donothing'
ACTION_BUILD_ZERGLING = 'buildzergling'
ACTION_ATTACK = 'attack'

smart_actions = [
    ACTION_DO_NOTHING,
    ACTION_BUILD_ZERGLING,
    ACTION_ATTACK,
]

KILL_UNIT_REWARD = 0.1
KILL_BUILDING_REWARD = 0.2
PRODUCE_ARMY_UNIT = 0.5
UNIT_DEATH = -0.5

UNIT_NAME = 0
C_NAME = 1
IS_DONE = 2

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
            sleep(5)
            haveCheckBases = False

# Without handcraft rules
class SmartAgent(base_agent.BaseAgent):

    def __init__(self):
        super(SmartAgent, self).__init__()
        self.cc_group = ControlGroup()
        self.thread = Thread(target = changeCheckBases)
        self.thread.setDaemon(True)
        self.thread.start()
        self.on_base = True # set a False quand la camera est pas sur une base
        self.pass_array_i = 0
        self.ppmean = None
        '''self.attack_coordinates = None
        self.base_top_left = None
        self.qlearn = QLearningTable(actions=list(range(len(smart_actions))))
        self.previous_killed_unit_score = 0
        self.previous_killed_building_score = 0
        self.previous_army_supply = 0
        self.previous_action = None
        self.previous_state = None
        self.p_smart_action = None
        self.cc_group = None

        self.nb_overlord = 0
        self.nb_queens = 0
        self.nb_hatches = 0

        self.queen_coming = False
        self.overlord_coming = False
        '''
    def step(self, obs):
        super(SmartAgent, self).step(obs)
        global haveCheckBases
        global thread_pause

        # init position variable at the first obs
        if obs.first():
            both_pos = get_both_position(obs)
            thread_pause = False
            self.ppmean = get_base_position(obs,units.Zerg.Hatchery)
            '''self.attack_coordinates = both_pos[0]
            self.base_top_left = 1 if self.ppmean[1] <= 31 else 0
            self.previous_killed_unit_score = 0
            self.previous_killed_building_score = 0
            self.previous_army_supply = 0 
            self.previous_action = None
            self.preivous_state = None
            self.p_smart_action = None
            # units/bats count
            self.nb_overlord = 0
            self.nb_queens = 0
            self.nb_hatches = 0
            # x_coming booleans
            self.cc_group = ControlGroup()
            self.overlord_coming = False
            self.queen_coming = False
            self.overlord_added = False
            '''
        
        if obs.last():
            thread_pause = True
            # add unit in control_groups
                # add hatch
                # add larvae
                # add overlord
        
        if self.pass_array_i == (len(self.cc_group.pass_array) - 1):
            haveCheckBases = True
            self.pass_array_i = 0

        return actions.FUNCTIONS.move_camera(self.ppmean)
        # si camera a bougé (my interaction)
            # on base = False
        # si changement de position par return(program)
            # on base = True
        '''
        if haveCheckBases == False:  
            # switch camera on base
            if self.on_base == True: # run les mises a jour des cc_group si on_base = True
                 # TODO pour eviter de surcharger les groupes de controles
                        # pendant qu'on est sur les bases on verifie si essential_bat existe
                self.set_cc_group = True # set un boolean pour savoir quand on fini les obs
                # Add Hatcheries !s
                unit_name = self.cc_group.pass_array[self.pass_array_i][UNIT_NAME]
                c_name = self.cc_group.pass_array[self.pass_array_i][C_NAME]
                is_done, action = self.cc_group.update_control_group(obs,unit_name,c_name,self.pass_array_i)
                if is_done == True:
                    self.pass_array_i+=1
                return action
                    #self.cc_group.pass_array[self.pass_array_i][IS_DONE] = True
        '''
        # si haveCheckBases est set a True
        # on bouge la cam on se balade


        #print(obs.observation.multi_select)
        #cc_group.update_control_group(units.Zerg.Hatcher,"hatch",0)

        #hatches = get_units_by_type(obs, units.Zerg.Drone)
        #hatche = hatches[0]
        #return actions.FUNCTIONS.select_point("select_all_type", (hatche.x,hatche.y))

        '''if len(hatches) > self.nb_hatches:
            init_control_group(units.Zerg.Hatchery,0)
            self.nb_hatches = len(hatches)
        
        overlords = get_units_by_type(obs, units.Zerg.Overlord)
        if len(overlords) > self.nb_overlord:
            init_control_group(units.Zerg.Overlord,1)
            self.nb_overlord = len(overlords)
        
        
        init_control_group(units.Zerg.Overlord)
        print(obs.observation.available_actions)
    '''

        # add hatch in control group
        # get away
        # try to select all my larva (might be in available action)

        # add larva to base
        # 
        '''init_control_group(units.Zerg.Hatchery,0)
        init_control_group(units.Zerg.Larvae,0)
         
        print(obs.observation.control_groups)     
       
        
        if self.overlord_added == False:
            if unit_type_is_selected(obs,units.Zerg.Overlord):
                print("we add Overord in group[0]")
                self.overlord_added = True
                return actions.FUNCTIONS.select_control_group("append", 0) 
            _units = get_units_by_type(obs, units.Zerg.Overlord)
            _unit = random.choice(_units) # mandatory de faire solo ?
            print("we select Overlord")
            return actions.FUNCTIONS.select_point("select", (_unit.x,_unit.y))

        print(obs.observation.control_groups)  
        if units.Zerg.Overlord not in obs.observation.control_groups[0]: 

        return actions.FUNCTIONS.select_control_group("recall",0)
       
        # append un autre truc dedans
        # select all
        # si queen is selected
        # get que un des truc et return
        print(obs.observation.control_groups)     
        print("it's in")
        exit(0)
        

        # Overlords
        overlords = get_units_by_type(obs, units.Zerg.Overlord)
        #print(len(overlords))
        if len(overlords) > self.nb_overlord:
            self.overlord_coming = False
            self.nb_overlord = len(overlords)
        
        # Queens
        queens = get_units_by_type(obs, units.Zerg.Queen)
        if len(queens) > self.nb_queens:
            self.queen_coming = False
        self.nb_queens = len(queens)
        
        hatches = get_units_by_type(obs, units.Zerg.Hatchery)

        # Set state 
        army_supply = obs.observation.player.food_army
        larvae = get_units_by_type(obs,units.Zerg.Larva)

        current_state = [
            army_supply,
            len(larvae)
        ]
        
        # Catch if units or building have been killed
        reward = 0
        killed_unit_score = obs.observation.score_cumulative.killed_value_units
        killed_building_score = obs.observation.score_cumulative.killed_value_structures


        # HC : Build the POOL
        spawning_pools = get_units_by_type(obs, units.Zerg.SpawningPool)
        if len(spawning_pools) == 0:
            #print("pas de pool")
            return build_pool(obs,self.ppmean[1],self.ppmean[0],larvae)
        

        # HC : Train Overlord  
        if is_supply_block(obs,self.overlord_coming):
            self.overlord_coming,action = train_overlord(obs,larvae,actions.FUNCTIONS.Train_Overlord_quick.id) 
            return action
        
        # HC : Build Queen
        if is_need_queen(obs,self.nb_queens,len(hatches),self.queen_coming):
            self.queen_coming,action = train_queen(obs,hatches,actions.FUNCTIONS.Train_Queen_quick.id)
            return action   
    
        # HC : Inject
        if self.nb_queens > 0:
            queen = random.choice(queens)
            if queen.energy >= 25:
                if unit_type_is_selected(obs,units.Zerg.Queen):
                    # TODO faire un calcul pour savoir quelle base est la plus proche
                    hatch = random.choice(hatches)
                    return actions.FUNCTIONS.Effect_InjectLarva_screen("now",(hatch.x,hatch.y))
                else:
                    return actions.FUNCTIONS.select_point("select", (queen.x,queen.y))

        if self.p_smart_action == ACTION_ATTACK:
            smart_action = self.p_smart_action
            self.p_smart_action = None
        elif self.p_smart_action == ACTION_BUILD_ZERGLING:
            smart_action = self.p_smart_action
            self.p_smart_action = None
        else : 
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
            
            # Update state to get the reward
            self.previous_killed_unit_score = killed_unit_score
            self.previous_killed_building_score = killed_building_score
            self.previous_army_supply = army_supply
            
            # Update for the qlearn
            self.previous_state = current_state
            self.previous_action = rl_action

            # Catch for handling select by ourself
            if smart_action == ACTION_ATTACK:
                # SELECT_ARMY
                self.p_smart_action = smart_action
                if can_do(obs, actions.FUNCTIONS.select_army.id):
                    return actions.FUNCTIONS.select_army("select")
                return actions.FUNCTIONS.no_op()
            
            if smart_action == ACTION_BUILD_ZERGLING:
                # SELECT_LARVA
                self.p_smart_action = smart_action
                if len(larvae) > 0:
                    larva = random.choice(larvae)
                    return actions.FUNCTIONS.select_point("select_all_type", (larva.x,larva.y))
   
        if smart_action == ACTION_DO_NOTHING:
            return actions.FUNCTIONS.no_op()
        elif smart_action == ACTION_BUILD_ZERGLING:
            if unit_type_is_selected(obs,units.Zerg.Larva):
                if can_do(obs,actions.FUNCTIONS.Train_Zergling_quick.id):
                    return actions.FUNCTIONS.Train_Zergling_quick("now")
        elif smart_action == ACTION_ATTACK:
            if unit_type_is_selected(obs, units.Zerg.Zergling):
                if can_do(obs, actions.FUNCTIONS.Attack_minimap.id):
                    return actions.FUNCTIONS.Attack_minimap("now", self.attack_coordinates)
        '''
        return actions.FUNCTIONS.no_op()

