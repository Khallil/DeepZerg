from pysc2.env import sc2_env
from pysc2.lib import actions, features, units
from absl import app
#from zerg_agent import ZergAgent
from rl_agent.smart_agent import SmartAgent
from rl_agent.test_agent import TestAgent

def main(unused_argv):
  #agent = ZergAgent()
  agent = SmartAgent()
  #agent = TestAgent()
  try:
    while True:
      with sc2_env.SC2Env(
        map_name="Simple64",
        players=[sc2_env.Agent(sc2_env.Race.zerg), # our Bot
                #sc2_env.Agent(sc2_env.Race.zerg)],
                sc2_env.Bot(sc2_env.Race.protoss,sc2_env.Difficulty.very_easy)], # Blizzard bot
        agent_interface_format=features.AgentInterfaceFormat( # Interface parameters
            feature_dimensions=features.Dimensions(screen=64, minimap=64),use_feature_units=True),
        step_mul=1, # steps before our Agent take a decision 8=300APM, 16=150
        game_steps_per_episode=0, #run game as long as necessary
        visualize=True) as env:
        agent.setup(env.observation_spec(), env.action_spec())

        timesteps = env.reset()
        agent.reset()

        while True: 
          step_actions = [agent.step(timesteps[0])]
          if timesteps[0].last():
            break
          timesteps = env.step(step_actions)

  except KeyboardInterrupt:
    pass

if __name__ == "__main__":
    app.run(main)