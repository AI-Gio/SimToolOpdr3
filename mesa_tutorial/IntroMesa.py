from mesa import Agent, Model
from mesa.time import RandomActivation
import matplotlib.pyplot as plt
from mesa.space import MultiGrid
import numpy as np
from mesa.datacollection import DataCollector
from mesa.batchrunner import BatchRunner

def compute_ini(model):
    agent_wealths = [agent.wealth for agent in model.schedule.agents]
    x = sorted(agent_wealths)
    N = model.num_agents
    B = sum( xi * (N-i) for i,xi in enumerate(x) ) / (N*sum(x))
    return (1 + (1 / N) - 2 * B)

class MoneyAgent(Agent):
    """An agent with fixed initial wealth"""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.wealth = 1
    def step(self):
        self.move()
        if self.wealth > 0:
            self.give_money()
        else:
            self.take_money()

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False)
        new_pos = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_pos)

    def give_money(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        if len(cellmates) > 1:
            other = self.random.choice(cellmates)
            other.wealth += 1
            self.wealth -= 1

    def take_money(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        if len(cellmates) > 1:
            other = self.random.choice(cellmates)
            # When an other
            if other.wealth > 3:
                other.wealth -= 3
                self.wealth += 3
            # when
            elif 4 > other.wealth > 0:
                other.wealth -= 1
                self.wealth += 1

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






# fixed_params = {"width": 10,
#                 "height": 10,}
# variable_params = {"N": range(10, 500, 10)}
#
# batch_run = BatchRunner(MoneyModel,
#                         variable_params,
#                         fixed_params,
#                         iterations=5,
#                         max_steps=100,
#                         model_reporters={"Gini": compute_ini})
# batch_run.run_all()
#
# run_data = batch_run.get_model_vars_dataframe()
# print(run_data.head())
# plt.scatter(run_data.N, run_data.Gini)
# plt.show()
#
# data_col_agents = batch_run.get_collector_agents()
# data_col_agents[(10,2)]
#
# data_col_model = batch_run.get_collector_model()
# data_col_model[(10,1)]
