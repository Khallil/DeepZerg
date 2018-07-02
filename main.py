import random

import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
#from sc2.constants import LARVA,DRONE,OVERLORD,HATCHERY,EXTRACTOR,SPAWNINGPOOL,QUEEN
from sc2.constants import *


class SmartBot(sc2.BotAI):

    def __init__(self):
        self.max_expand = 2
        self.iteration = 0

    async def on_step(self, iteration):
        #await self.check_distance()
        self.iteration = iteration
        await self.train_overlord()
        await self.build_workers()
        await self.distribute_workers() # TODO parfois 1 worker qui fait rien a cote du gaz aller editer la fonction et la mettre en local pour ne plus l'utiliser
        await self.build_assimilator()        
        await self.expand()
        #await self.build_pool()  
        #await self.train_queens()
        #await self.queen_inject()   

    async def check_distance(self):
        for hatch in self.units(HATCHERY).ready:
            if self.units(OVERLORD).closer_than(25.0, hatch).exists:
                print("25")
            elif self.units(OVERLORD).closer_than(30.0, hatch).exists:
                print("30")
            elif self.units(OVERLORD).closer_than(35.0, hatch).exists:
                print("35")
        
    async def train_queens(self):
        # train 2 queen sur B2 je sais pas pourquoi
        for hatch in self.units(HATCHERY).ready:
            if not self.units(QUEEN).closer_than(15.0, hatch).exists and hatch.noqueue and self.iteration % 6 == 0:
                if self.can_afford(QUEEN):
                    await self.do(hatch.train(QUEEN))

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
                    await self.do(v_queen(EFFECT_INJECTLARVA,hatch))

    async def build_workers(self):
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
                        await self.do(larva.train(DRONE))
                
    async def train_overlord(self):
        if len(self.workers.idle) > 0:
            print("Idle Worker ! ")
        else:
            print("pas d'idle worker")

        if self.supply_left < 2 and not self.already_pending(OVERLORD):
            if len(self.units(LARVA).ready.noqueue) > 0:
                larva = self.units(LARVA).ready.noqueue[0]
                if self.can_afford(OVERLORD):
                    await self.do(larva.train(OVERLORD))

    async def expand(self):
        if self.units(HATCHERY).amount < self.max_expand and self.can_afford(HATCHERY):
            await self.expand_now()
    
    async def build_assimilator(self):
        # pour debuger le truc
        #if self.units(SPAWNINGPOOL).ready.exists or self.already_pending(SPAWNINGPOOL):
        for hatch in self.units(HATCHERY).ready:
            vaspenes = self.state.vespene_geyser.closer_than(15.0, hatch)
            for vaspene in vaspenes:
                if not self.can_afford(EXTRACTOR):
                    break
                worker = self.select_build_worker(vaspene.position)
                if worker is None:
                    break
                if not self.units(EXTRACTOR).closer_than(1.0, vaspene).exists:
                    await self.do(worker.build(EXTRACTOR, vaspene))
        
    async def build_pool(self):
        if not self.units(SPAWNINGPOOL).ready.exists:
            if len(self.units(HATCHERY).ready) == 2 or self.already_pending(HATCHERY):
                if self.units(HATCHERY).ready.exists:
                    hatch = self.units(HATCHERY).ready[0]
                    if self.can_afford(SPAWNINGPOOL) and not self.already_pending(SPAWNINGPOOL):
                        if len(self.state.mineral_field.closer_than(10.0, hatch)) > 0:
                            mineral = random.choice(self.state.mineral_field.closer_than(10.0, hatch))
                            await self.build(SPAWNINGPOOL, near=mineral.position)
    

run_game(maps.get("CatalystLE"), [
    Bot(Race.Zerg, SmartBot()),
    Computer(Race.Terran, Difficulty.Hard)
], realtime=True)