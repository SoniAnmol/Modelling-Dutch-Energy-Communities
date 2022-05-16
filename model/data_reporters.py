"""This file contains the DataReporter class."""

import json

from model.agents import *


def get_energy_expenses(self):
    """Returns the current energy prices."""
    return None


def get_average_demand(self):
    """
    Returns the average daily realised energy demand for every agent type.
    :return: Dict: average energy demand per agent type
    """
    agent_list = [Residential, NonResidential, EVChargingStation]
    demand_dict = {}
    for agent_type in agent_list:
        demand_array = np.arange(0, 96)
        for agent in self.all_agents[agent_type]:
            demand = agent.demand_realized
            demand_array = np.c_[demand_array, demand]
        demand = demand_array[:, 1:].mean(axis=1)
        demand = demand.tolist()
        demand_dict[str(agent_type)] = demand
    return json.dumps(demand_dict)


def get_total_demand(self):
    """
    Returns the total daily realised energy demand for every agent type.
    :return: Dict: total energy demand per agent type
    """
    agent_list = [Residential, NonResidential, EVChargingStation]
    demand_dict = {}
    for agent_type in agent_list:
        demand_array = np.arange(0, 96)
        for agent in self.all_agents[agent_type]:
            demand = agent.demand_realized
            demand_array = np.c_[demand_array, demand]
        demand = demand_array[:, 1:].sum(axis=1)
        demand = demand.tolist()
        demand_dict[str(agent_type)] = demand
    return json.dumps(demand_dict)


def get_average_supply(self):
    """
    Returns the average daily realised energy supply of assets by generator type.
    :return: a dict of average energy supply per generator type
    """
    generator_list = [Solar]
    supply_dict = {}
    for generator in generator_list:
        supply_array = np.arange(0, 96)
        for asset in self.all_assets[generator]:
            supply = asset.supply_schedule
            supply_array = np.c_[supply_array, supply]
        supply = supply_array[:, 1:].mean(axis=1)
        supply = supply.tolist()
        supply_dict[str(generator)] = supply
    return json.dumps(supply_dict)


def get_total_supply(self):
    """
    Returns the total daily realised energy supply of assets by generator type.
    :return: a dict of total energy supply per generator type
    """
    generator_list = [Solar]
    supply_dict = {}
    for generator in generator_list:
        supply_array = np.arange(0, 96)
        for asset in self.all_assets[generator]:
            supply = asset.supply_schedule
            supply_array = np.c_[supply_array, supply]
        supply = supply_array[:, 1:].sum(axis=1)
        supply = supply.tolist()
        supply_dict[str(generator)] = supply
    return json.dumps(supply_dict)
