#coding:utf-8

import random
#import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
#from sc2.constants import LARVA,DRONE,OVERLORD,HATCHERY,EXTRACTOR,SPAWNINGPOOL,QUEEN
from sc2.constants import *
from sc2.data import Race
from botai import BotAIModified
from sc2.pixel_map import PixelMap
from math import sqrt
from sc2.position import Point2,Point3
from sc2.unit import Unit
import time
import sys

class SmartBot2(BotAIModified):

    def __init__(self):
        self.max_expand = 2
        self.iteration = 0
        self.assimilator_order = 0
        self.worker_tag_gas = 0
        self.count = 0
        self.player_left_up = None

    async def on_step(self, iteration):
        self.iteration = iteration
        if self.iteration == 0:
            #self.game_info.pathing_grid.print()
            self.player_left_up = await self.get_position()
        if iteration % (20*22.4) == 0:
            await self.print_result()

        #print(blank_points)
        #self.state.visibility.print()

        #await self.train_overlord() # basic function
        #await self.train_workers() # basic function
        #await self.distribute_workers() # basic function
        #await self.build_assimilator() # basic function
        #await self.build_pool() # basic function
        #await self.get_creep()
        #await self.train_queens() # basic function
        #await self.queen_inject() # basic function
        #await self.expand() # Macro strat

    async def display_labels_lol(self):
        text = "CREEP"
        width = self.state.creep.width
        height = self.state.creep.height
        positions = {Point2((x, y)) for x in range(width) for y in range(height)}
        creepPositions = [p for p in positions if self.hasCreep(p)] # not 0 means there is creep! 
        print(creepPositions)
        print("AMOUNT OF POSITIONS: {}".format(len(creepPositions)))
        await self._client.debug_text(text, creepPositions)

    def hasCreep(self, pos):
        # returns True if there is creep at position
        assert isinstance(pos, (Point2, Point3, Unit))
        pos = pos.position.to2.rounded
        return self.state.creep[pos] != 0 # not 0 means there is creep

    async def print_result(self):            
        creep_points, best_xy  = await self.clean_trash_blank_points()
        h,w = await self.get_height_width()
        step_points = await self.get_step_points(h,w)
        blank_points,points_scanned = await self.get_blank_points()   
        # open un nouveau fichier

        with open("file_{:d}.txt".format(self.count),"a+") as file :
            for y in range(self.state.creep.height):
                for x in range(self.state.creep.width):
                    if (x,y) in step_points:
                        file.write("+")
                    elif (x,y) == best_xy:
                        file.write("X")
                    elif (x,y) in creep_points:
                        file.write("#")
                    elif (x,y) in points_scanned:
                        file.write("o")
                    else:
                        file.write(" ")
                file.write("\n")
        self.count +=1

    async def get_distance(self):
        overlords = self.units(OVERLORD).ready
        for o in overlords:
            #print(o.position)
            x = int(o.position[0])
            y = int(o.position[1])
           # print(self.game_info.terrain_height.__getitem__((x,y)))

    async def get_height_width(self):
        creep_coor = list()
        i = 0
        while i < len(self.state.creep.data):
            if self.state.creep.data[i] == 1:
                y = i / self.state.creep.width
                x = i - (self.state.creep.width * int(y))
                creep_coor.append((x,int(y)))
            i+=1
        x = [creep[0] for creep in creep_coor]
        y = [creep[1] for creep in creep_coor]
        width = (max(x) - min(x)) +1
        height = (max(y) - min(y)) +1
        if self.player_left_up == (False,False):
            width_supp = self.state.creep.width - max(x)
            height_supp = self.state.creep.height - max(y)
        else: #self.player_left_up == (True,True):
            width_supp = min(x) 
            height_supp = min(y)
        return height*2+height_supp,width*2+width_supp

    async def get_step_points(self,h,w):
        creep_d = 20
        hypothenuse = sqrt((pow(h,2)+pow(w,2)))
        iterations = int(hypothenuse / creep_d)
        j = 0
        # de combien je dois me deplacer en x,y a chaque iteration
        i_x = w * creep_d / (w + h)
        i_y = h * creep_d / (w + h)
        x = 0
        y = 0
        if self.player_left_up == (True,False): # OK
            x = 0
            y = self.state.creep.height- h
        elif self.player_left_up == (False,False): #OK
            x = self.state.creep.width
            i_x = - i_x
            y = self.state.creep.height- h
        elif self.player_left_up == (False,True): #OK
            x = self.state.creep.width - w
            y = 0
        elif self.player_left_up == (True,True): #OK
            x = w
            y = 0
            i_x = - i_x
        step_points = list()
        step_points.append((int(x),int(y)))
        for it in range(iterations+1):
            x = x +  i_x
            y = y + i_y
            step_points.append((int(x),int(y)))
        return step_points

    async def get_blank_points(self):
        h,w = await self.get_height_width()
        step_points = await self.get_step_points(h,w)
        blank_points = list()
        points_scanned = list()
        i = 1
        if self.player_left_up == (True,False) or self.player_left_up == (False,True):
            while i < len(step_points):
                x = step_points[i][0]
                y = step_points[i][1]
                prev_x = step_points[i-1][0]
                prev_y = step_points[i-1][1]
                while x > prev_x:
                    while y > prev_y:
                        if (self.state.creep.__getitem__((x,y)) == 0 and
                        self.state.visibility.__getitem__((x,y)) and
                        self.game_info.placement_grid.__getitem__((x,y))):
                            blank_points.append((x,y))
                        y-=1
                    y = step_points[i][1]
                    x-=1
                i+=1

        if self.player_left_up == (False,False) or self.player_left_up == (True,True):
            while i < len(step_points):
                x = step_points[i][0]
                y = step_points[i][1]
                prev_x = step_points[i-1][0]
                prev_y = step_points[i-1][1]
                while x < prev_x:
                    while y > prev_y:
                        points_scanned.append((x, y))
                        if (self.state.creep.__getitem__((x,y)) == 0 and
                        self.state.visibility.__getitem__((x,y)) and
                        self.game_info.placement_grid.__getitem__((x,y))):
                            blank_points.append((x,y))
                        y-=1
                    y = step_points[i][1]
                    x+=1
                i+=1
        return blank_points,points_scanned

    async def get_creep_points(self,blank_points):
        around = [(-1,0),(-1,-1),(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1)]
        htable = dict()
        creep_points = list()
        for point in blank_points:
            x = point[0]
            y = point[1]
            for a in around:
                key = (x+a[0],y+a[1])
                if htable.get(key) == None:
                    if self.state.creep.__getitem__(key):
                        creep_points.append(key)
                    htable[key] = True
        return creep_points

    async def get_earners_creep_points(self,creep_points):
        earners_creep_points= list()
        max_tilt = 0
        best_x_y = (0,0)
        tilt = 25
        self.game_info.placement_grid.print()
        for point in creep_points:
            x = point[0] - 1
            y = point[1]
            count = 0
            while (x > 0 and 
                self.game_info.placement_grid.__getitem__((x,y)) and 
                self.state.creep.__getitem__((x,y)) == 0):
                count+=1
                x-=1
            if count > max_tilt:
                max_tilt = count
                best_x_y = point
            if count >= tilt:
                earners_creep_points.append((point[0],point[1]))
                continue
            
            x = point[0] + 1
            y = point[1]
            count = 0
            while (x < self.state.creep.width and 
                self.game_info.placement_grid.__getitem__((x,y)) and 
                self.state.creep.__getitem__((x,y)) == 0):
                count+=1
                x+=1
            if count > max_tilt:
                max_tilt = count
            if count >= tilt:
                earners_creep_points.append((point[0],point[1]))
                continue
            
            x = point[0]
            y = point[1] -1
            count = 0
            while (y > 0 and 
                self.game_info.placement_grid.__getitem__((x,y)) and 
                self.state.creep.__getitem__((x,y)) == 0):
                count+=1
                y-=1
            if count > max_tilt:
                max_tilt = count
                best_x_y = point         
            if count >= tilt:
                earners_creep_points.append((point[0],point[1]))
                continue

            x = point[0]
            y = point[1] +1
            count = 0
            while (y < self.state.creep.height and 
                self.game_info.placement_grid.__getitem__((x,y)) and 
                self.state.creep.__getitem__((x,y)) == 0):
                count+=1
                y+=1
            if count > max_tilt:
                max_tilt = count
                best_x_y = point
            if count >= tilt:
                earners_creep_points.append((point[0],point[1]))
                continue
        print("Max tilt : ",max_tilt)
        return best_x_y

    async def clean_trash_blank_points(self):
        '''
        I. On tri les points en regardant si y'a bien du creep autour sinon c'est un point
            blanc au milieu d'un point blanc qui n'a aucun intérêt
        II. On regarde pour chaque point restant si au moins une distance gauche,droite,haut, bas
            vaut la peine qu'on expand le creep sur ce point
        III. Si aucun point n'est retenu il faut prendre le point le plus bas droite, etc, dépends
            de la position de départ, et on vérifie ce point avec l'étape II. Si ce point est invalide 
            on en prends un autre, etc. Si aucun n'est valide on reprends le point qui a le plus de valeur
            en fonction des résultats de l'étape II.
        '''
        blank_points,points_scanned = await self.get_blank_points()
        
        #I.
        creep_points = await self.get_creep_points(blank_points)
        print("CREEP_POINTS : ",creep_points)
        #II.
        #creep_points = await self.get_earners_creep_points(creep_points)
        best_xy = await self.get_earners_creep_points(creep_points)
        overlords = self.units(OVERLORD).ready

        # Le move inverse le y, le y part du bas alors que le point que je donne par du haut
        await self.do1(overlords[0].move(Point2( (best_xy[0],self.state.creep.height - best_xy[1])) ))

        return creep_points,best_xy
        #III.

    '''

    Etapes:
        {Get height,width}
            On mets tous les indexs qui sont du creep dans un tableau
            On converti chaque index en coordonées
                y = index / len(width)
                x =  (index - (len(width) * y))
            On get le min y On get le max y
            height = (max_y - min_y) + 1
            On get le min x On get le max x
            width = (max_x - min_x) + 1

        {Get step_points}
            On calcule l'hypothenuse
            iterations = hypothenuse / diametre_creep
            j = 0
            while j < iterations:
                A chaque étape on ferait : 
                    i_x = (width * diametre_creep) / (width + height)
                    i_y = (heigth * diametre_creep) / (width + height)
                    si top_left: 0 + i_x, y - i_y
                    si top_righ: x + i_x, 0 + i_y
                    si down_lef: 0 + i_x, y + i_y
                    si down_rig: x + i_x, y + i_y
                    ajoute le (x,y) dans "step_points"

        {Get blank_points}
         Ensuite on parcourse step_points et pour chaque point (step_x,step_y):
            on cree un grand tableau "blank_points" qui va save tous les points
            non creep + terre visitable + terre visible qui sont dans le cadre :
            si down_left : 
                start x = step_x
                start y = step_y
                while x > 0 || x > last_step_x:
                    x--
                    while y < first_y || y < last_step_y:
                        y --
                        si point == blank_point:
                            blank_points.append(blank_point)
        
        {Get creep_points}
            on regarde chaque pixel autour 
                si hashmap[x,y] == False:
                    on check si creep dessus
                    on ajoute le point du creep dans creep_points
                    on set le hashmap[x,y] = True
                sinon:
                    on regarde le pixel suivant
        
            pour chaque creep_points:
                on calcule la distance euclidienne entre c_x,c_y et step_x,_step_y
                on save le creep point qui a max distance

        {Expand Creep with queen or creep tumor}
    '''

    async def get_position(self):
        if self.iteration == 0:
            hatchery = self.units(HATCHERY).ready
            if len(hatchery) > 0:
                position = hatchery[0].position
                print("creep on Hatch : ",self.state.creep.__getitem__( (int(position[0]),self.state.creep.height - int(position[1])))) # get item est foireux
                print("visi on Hatch : ",self.state.visibility.__getitem__( (int(position[0]),self.state.creep.height - int(position[1]))))
                print("Position : ",position)
                x = False if position[0] > 70 else True
                y = False if position[1] < 70 else True
                '''for y in range(self.state.visibility.height):
                    for x in range(self.state.visibility.width):
                        print(self.state.visibility.__getitem__((x,y)),end="")
                    print("")'''
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
                    await self.build1(SPAWNINGPOOL, near=mineral.position, player_left_up=self.player_left_up)

run_game(maps.get("CatalystLE"), [
    Bot(Race.Zerg, SmartBot2()),
    Computer(Race.Terran, Difficulty.Easy)
], realtime=True)
#], realtime=False,step_time_limit=1)
