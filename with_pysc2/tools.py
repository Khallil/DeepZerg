from pysc2.lib import features

def get_both_position(obs):
    # Get Ennemy Location
        player_y, player_x = (obs.observation.feature_minimap.player_relative == features.PlayerRelative.SELF).nonzero()
        xmean = player_x.mean()
        ymean = player_y.mean()

        # Sample64
        if xmean <= 31 and ymean <= 31:
            return [(45, 45),(21,21)]
        else:
            return [(21,21),(45,45)]

def can_do(obs,action):
    return action in obs.observation.available_actions

