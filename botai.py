import random
import logging
logger = logging.getLogger(__name__)

import sc2
from sc2.constants import *
from sc2.units import Unit
from sc2.position import Point2, Point3
from sc2.data import  ActionResult

class BotAIModified(sc2.BotAI):

    async def build1(self, building, near, player_left_up,max_distance=5, unit=None, random_alternative=True, placement_step=2):
        """Build a building."""

        if isinstance(near, Unit):
            near = near.position.to2
        elif near is not None:
            near = near.to2

        p = await self.find_placement1(building, near.rounded,player_left_up, max_distance, random_alternative, placement_step)
        if p is None:
            return ActionResult.CantFindPlacementLocation

        unit = unit or self.select_build_worker(p)
        if unit is None:
            return ActionResult.Error
        return await self.do1(unit.build(building, p))

    # add a parameter : "is player_up_needed" pour savoir si on applique le if pour les autres buildings
    async def find_placement1(self, building, near, player_left_up,max_distance=5, random_alternative=True, placement_step=2):
        """Finds a placement location for building."""

        assert isinstance(building, (AbilityId, UnitTypeId))
        #assert self.can_afford(building)
        assert isinstance(near, Point2)
        print("NEAR : ",near)
        if isinstance(building, UnitTypeId):
            building = self._game_data.units[building.value].creation_ability
        else: # AbilityId
            building = self._game_data.abilities[building.value]

        if await self.can_place(building, near):
            return near

        if max_distance == 0:
            return None

        for distance in range(placement_step, max_distance, placement_step):
            possible_positions = [Point2(p).offset(near).to2 for p in (
                [(dx, -distance) for dx in range(-distance, distance+1, placement_step)] +
                [(dx,  distance) for dx in range(-distance, distance+1, placement_step)] +
                [(-distance, dy) for dy in range(-distance, distance+1, placement_step)] +
                [( distance, dy) for dy in range(-distance, distance+1, placement_step)]
            )]
            res = await self._client.query_building_placement(building, possible_positions)
            if player_left_up == (True,False):
                possible = [p for r, p in zip(res, possible_positions) if r == ActionResult.Success and (p[1] > near[1] and p[0] < near[0])]
            elif player_left_up == (False,False):
                possible = [p for r, p in zip(res, possible_positions) if r == ActionResult.Success and (p[1] > near[1] and p[0] > near[0])]
            elif player_left_up == (True,True):
                possible = [p for r, p in zip(res, possible_positions) if r == ActionResult.Success and (p[1] < near[1] and p[0] < near[0])]
            elif player_left_up == (False,True):
                possible = [p for r, p in zip(res, possible_positions) if r == ActionResult.Success and (p[1] < near[1] and p[0] > near[0])]
            print("Possible : ",possible)
            if not possible:
                continue

            if random_alternative:
                choice = random.choice(possible)
                print("  The chosen : ",choice)
                return choice
            else:
                return min(possible, key=lambda p: p.distance_to(near))
        return None

    async def expand_now1(self, building=None, max_distance=10, location=None):
        """Takes new expansion."""

        if not building:
            building = self.townhalls.first.type_id

        assert isinstance(building, UnitTypeId)

        if not location:
            location = await self.get_next_expansion()

        await self.build1(building, near=location, max_distance=max_distance, random_alternative=False,
                            placement_step=1)

    async def do1(self, action):
        #assert self.can_afford(action)
        r = await self._client.actions(action, game_data=self._game_data)

        if not r: # success
            cost = self._game_data.calculate_ability_cost(action.ability)
            self.minerals -= cost.minerals
            self.vespene -= cost.vespene

        else:
            logger.error(f"Error: {r} (action: {action})")

        return r