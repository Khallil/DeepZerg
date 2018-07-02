from tools import can_do

def unit_type_is_selected(obs, unit_type,n_unit):
    if (len(obs.observation.single_select) > 0 and
        obs.observation.single_select[0].unit_type == unit_type):
        return True
    
    if n_unit > 0:
        if (len(obs.observation.multi_select) == n_unit and
            obs.observation.multi_select[0].unit_type == unit_type):
            return True
    return False

def get_units_by_select(obs, unit_type):
    return 

def get_units_by_type(obs,unit_type):
    return [unit for unit in obs.observation.feature_units
                if unit.unit_type == unit_type]

def get_base_position(obs,unit_type):
    units = [unit for unit in obs.observation.feature_units
                if unit.unit_type == unit_type]
    base = units[0]
    return base.x,base.y