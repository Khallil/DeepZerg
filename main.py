import random

#import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
#from sc2.constants import LARVA,DRONE,OVERLORD,HATCHERY,EXTRACTOR,SPAWNINGPOOL,QUEEN
from sc2.constants import *
from sc2.data import Race
from botai import BotAIModified
from sc2.pixel_map import PixelMap

class SmartBot2(BotAIModified):

    def __init__(self):
        self.max_expand = 2
        self.iteration = 0
        self.assimilator_order = 0
        self.worker_tag_gas = 0
        self.position_left_up = None

    async def on_step(self, iteration):
        self.iteration = iteration
        if self.iteration == 0:
            self.position_left_up = await self.get_position()
        #await self.train_overlord() # basic function
        #await self.train_workers() # basic function
        #await self.distribute_workers() # basic function
        #await self.build_assimilator() # basic function
        await self.build_pool() # basic function
        #await self.train_queens() # basic function
        #await self.queen_inject() # basic function
        #await self.expand() # Macro strat 

    async def get_creep(self):
        #print("visi : ",self.state.visibility)
        #print("creep : ",self.state.creep)
        #self.state.creep.print()
        #print("creep : ",self.state.creep.__getitem__((20,20)))
        #print("creep_proto : ",self.state.creep._proto)
        print("creep_data : ",self.state.creep.data[0])
        print("self.state.wh : ", self.state.creep.width,self.state.creep.height)
        map_width = self.state.creep.width
        i = 0
        for d in self.state.creep.data:
            if d == 1:
                print(i)
            i+=1
        print("creep on Hatch : ",self.state.creep.__getitem__( (int(position[0]),map_width - int(position[1])))) # get item est foireux

        '''

        Etapes:
            On get la hauteur maximale du creep - height (on utilise les bits pour get plus vite)
                Get la distance entre le plus petit y et le plus grand y
                convertir l'index en corrdone y
            On get la largeur maximale du creep - width
                Get la distance entre le plus petit x et le plus grand x
                convertir l'index en coordonee x
            On calcule l'hypothenuse
            iterations = hypothenuse / diametre_creep
            x = 0
            while x < iterations:
                A chaque étape on ferait : 
                    i_x = (width * diametre_creep) / (width + height)
                    i_y = (heigth * diametre_creep) / (width + height)
                    si top_left: 0 + i_x, y - i_y
                    si top_righ: x + i_x, 0 + i_y
                    si down_lef: 0 + i_x, y + i_y
                    si down_rig: x + i_x, y - i_y
                    ajoute le (x,y) dans une array
        '''

    async def get_position(self):
        if self.iteration == 0:
            hatchery = self.units(HATCHERY).ready
            if len(hatchery) > 0:
                position = hatchery[0].position
                print("Position : ",position)
                x = False if position[0] > 70 else True
                y = False if position[1] < 70 else True
                return(x,y)
            return (False,False)

    '''
        ATTACK Priority:
            Set un focus building:
            Si dans champs de vision pluieurs focus building, focus
            aller taper celui qui a le moins de vie
    
    '''
    async def train_queens(self):
        # train 2 queen sur B2 je sais pas pourquoi
        for hatch in self.units(HATCHERY).ready:
            if self.units(SPAWNINGPOOL).ready.exists and not self.units(QUEEN).closer_than(15.0, hatch).exists and hatch.noqueue and self.iteration % 6 == 0:
                if self.can_afford(QUEEN): # no bug here ?
                    await self.do1(hatch.train(QUEEN))

    async def queen_inject(self):
        for hatch in self.units(HATCHERY).ready:
            if self.units(QUEEN).closer_than(15.0, hatch).exists:
                # si plusieurs queens autour de la base
                queens = self.units(QUEEN).closer_than(15.0, hatch)
                # on prends les/la queens qui a de l'energie
                v_queens = [queen for queen in queens if AbilityId.EFFECT_INJECTLARVA in await self.get_available_abilities(queen)]
                # si queens disponible
                if len(v_queens) > 0:
                    v_queen = random.choice(v_queens)
                    await self.do1(v_queen(EFFECT_INJECTLARVA,hatch))

    async def train_workers(self):
        if self.supply_left > 1 or self.already_pending(OVERLORD):
            for hatch in self.units(HATCHERY).ready:
                drones = self.units(DRONE).closer_than(15.0,hatch)
                drones_building = self.already_pending(DRONE)
                drones_needed = 20 - (len(drones) + drones_building)
                i = 0
                for larva in self.units(LARVA).ready.noqueue:
                    if i >= drones_needed:
                        break
                    if self.can_afford(DRONE):
                        i+=1
                        await self.do1(larva.train(DRONE))
                
    async def train_overlord(self):
        if self.supply_left < 2 and not self.already_pending(OVERLORD):
            if len(self.units(LARVA).ready.noqueue) > 0:
                larva = self.units(LARVA).ready.noqueue[0]
                if self.can_afford(OVERLORD):
                    await self.do1(larva.train(OVERLORD))

    async def expand(self):
        if self.units(HATCHERY).amount < self.max_expand and self.minerals >= 300:
            await self.expand_now1()
    
    async def build_assimilator(self):
        if self.units(SPAWNINGPOOL).ready.exists or self.already_pending(SPAWNINGPOOL):
            if len(self.units(HATCHERY).ready) == (len(self.units(EXTRACTOR)) / 2):
                self.assimilator_order = 0
                self.worker_tag_gas = 0
            for hatch in self.units(HATCHERY).ready:
                vaspenes = self.state.vespene_geyser.closer_than(15.0, hatch)
                if self.assimilator_order < len(vaspenes) / 2:
                    for vaspene in vaspenes:
                        if self.minerals < 25 : #if not self.can_afford(EXTRACTOR):
                            break
                        worker = self.select_build_worker(vaspene.position)
                        if worker is None:
                            break
                        if self.assimilator_order > 0 and worker.tag == self.worker_tag_gas: # si le worker est deja busy
                            break
                        if not self.units(EXTRACTOR).closer_than(1.0, vaspene).exists:
                            if await self.do1(worker.build(EXTRACTOR, vaspene)) == None: # if no error
                                self.worker_tag_gas = worker.tag
                                self.assimilator_order +=1

    async def build_pool(self):
        if not self.units(SPAWNINGPOOL).ready.exists:
            #if len(self.units(HATCHERY).ready) == 2 or self.already_pending(HATCHERY):
            #    if self.units(HATCHERY).ready.exists:
            hatch = self.units(HATCHERY).ready[0]
            if self.minerals >= 200 and not self.already_pending(SPAWNINGPOOL):
                # TODO Si base top left build1 pool au dessus du minerai 
                # Si bas down right build1 pool en dessous du minerai
                if len(self.state.mineral_field.closer_than(10.0, hatch)) > 0:
                    mineral = random.choice(self.state.mineral_field.closer_than(10.0, hatch))
                    await self.build1(SPAWNINGPOOL, near=mineral.position, player_left_up=self.position_left_up)

run_game(maps.get("CatalystLE"), [
    Bot(Race.Zerg, SmartBot2()),
    Computer(Race.Terran, Difficulty.Easy)
], realtime=True)
#], realtime=False,step_time_limit=1)
