from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from MoneyAgent import *

def compute_ini(model):
    agent_wealths = [agent.wealth for agent in model.schedule.agents]
    x = sorted(agent_wealths)
    N = model.num_agents
    B = sum( xi * (N-i) for i,xi in enumerate(x) ) / (N*sum(x))
    return (1 + (1 / N) - 2 * B)

class MoneyModel(Model):
    """A model with some number of agents"""
    def __init__(self, N, width, height):
        self.num_agents = N
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.running = True

        # Create agents
        for i in range(self.num_agents):
            a = MoneyAgent(i, self)
            # add a money agent to the schedule
            self.schedule.add(a)

            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        self.datacollector = DataCollector(
            model_reporters = {"Gini": compute_ini},
            agent_reporters = {"Wealth":"wealth"}
        )

    def step(self):
        """goes step by step through the schedule"""
        self.datacollector.collect(self)
        self.schedule.step()