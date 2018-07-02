import random

from pysc2.lib import actions,units
from unit_tools import get_units_by_type


IS_SELECTED = 0
INDEX = 1
K_NUMBER = 2
UNITS_POS = 3 

class ControlGroup:

    def __init__(self):
        self.dico = dict()
        self.pass_array = [
            [units.Zerg.Hatchery,"hatch",0,False],
            [units.Zerg.Overlord,"overlord",False],
            [units.Zerg.Drone,"drone",False]]


    #dico[unit_name] = [is_selected,index,k_number,[pos_des units]]
    def update_control_group(self,obs,unit_name,c_name,index):
        dico_unit = self.dico.get(c_name)
        if dico_unit == None: # if dico don't exist
            self.dico[c_name] = [False,index,0,[]]
            dico_unit = self.dico.get(c_name)
        else:
            if dico_unit[IS_SELECTED]: # if we already selected during last pass
                dico_unit[IS_SELECTED] = False
                return True,actions.FUNCTIONS.select_control_group("append", index)

        dico_unit[K_NUMBER] = obs.observation.control_groups[index][1] #len of my cc_group of this unit
        
        # pour que ça marche il faut constamment que mon
        # dico_unit[whatever qui representer une unit unique]
            # soit mis a jour en prenant les infos du groupe de controle
            # pour ça il faut que je fasse un recall du group
            # que je fasse un get_units_by_select
            # après je peux lire le groupe

        units = get_units_by_type(obs, unit_name) #my units
        unit = random.choice(units) # I take one for the selection action            
        print("RETURN SELECT HATCH")
        dico_unit[IS_SELECTED] = True
        return False,actions.FUNCTIONS.select_point("select_all_type", (unit.x,unit.y))            

        '''nb_unit_to_add = 0
        for unit in units: # if units that I see are not in my cc_group
            unit_pos = (unit.x,unit.y)
            if unit_pos not in dico_unit[UNITS_POS]:
                nb_unit_to_add+=1
                dico_unit[UNITS_POS].append(unit_pos)
        if nb_unit_to_add > 0:
            dico_unit[K_NUMBER]+= nb_unit_to_add
            dico_unit[IS_SELECTED] = True
            unit = random.choice(units) # I take one for the selection action            
            return k_number,actions.FUNCTIONS.select_point("select_all_type", (unit.x,unit.y))            
        '''
        #return "no_action"
        '''
            Doc
            si dans ma vision j'ai plus d'item que mon "nombre connu"
                j'update mon nombre connu
                append vision_units in control_group

            si la taille de mon control_group est plus petit que mon nombre connu
                j'update mon nombre connu
            
            tout le temps
            pour chaque unit que je vois:
                si unit coor == unit coor dans mon dico de position de group de controle
                    on fait rien
                sinon
                    append toute les units dans mon group
                return "no_action"

            + creer un dict pour savoir quel index de control group est quelle unit
            pool : 0, du coup on ferais, 
                update_control_group(units.Zerg.SpawningPool,dict[pool],k_number)
        '''
