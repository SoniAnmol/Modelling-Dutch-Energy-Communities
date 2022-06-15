"""This file contains the DataReporter class."""

import json

from model.agents import *


def get_realised_demand(self):
    """
    Returns the total daily realised energy demand for every agent type.
    :return: Dict: total energy demand per agent type
    """
    members = [AgentType.CONSUMER, AgentType.PROSUMER]
    demand_dict = {}
    for agent in self.schedule.agents:
        if agent.agent_type in members:
            key = str(agent.member_name) + str('_') + str(agent.unique_id)
            demand_dict[key] = agent.realised_demand.sum()
    return demand_dict


def get_scheduled_demand(self):
    """
    Returns scheduled demand for each community member
    :param self:
    :return:
    """
    members = [AgentType.CONSUMER, AgentType.PROSUMER]
    demand_dict = {}
    for agent in self.schedule.agents:
        if agent.agent_type in members:
            key = str(agent.member_name) + str('_') + str(agent.unique_id)
            demand_dict[key] = agent.scheduled_demand.sum(min_count=1)
    return demand_dict


def get_shifted_load(self):
    """"
    Returns the demand shifted by the community members participating in the demand response.
    """
    members = [AgentType.CONSUMER, AgentType.PROSUMER]
    shifted_load = {}
    for agent in self.schedule.agents:
        if agent.agent_type in members:
            key = str(agent.member_name) + str('_') + str(agent.unique_id)
            shifted_load[key] = agent.shifted_load
    return json.dumps(shifted_load)


def get_generation(self):
    """
    Returns the total daily realised energy supply of assets by generator type.
    :return: a dict of total energy supply per generator type
    """
    generation_dict = {}
    for asset_category in self.all_assets.keys():
        supply = 0
        for asset in self.all_assets[asset_category]:
            supply += asset.supply_schedule.sum()
        generation_dict[str(asset_category)] = supply
    return json.dumps(generation_dict)


def get_savings(self):
    """
    Returns savings made by community member by complying to ToD schedule as a part of demand response.
    :param self: a dict of savings on energy cost through ToD compliance per timestep
    :return:
    """
    savings_dict = {}
    members = [AgentType.CONSUMER, AgentType.PROSUMER]
    for agent in self.schedule.agents:
        if agent.agent_type in members:
            key = str(agent.member_name) + str('_') + str(agent.unique_id)
            savings_dict[key] = agent.savings_ToD
    return json.dumps(savings_dict)


def get_energy_cost(self):
    """
    Returns energy cost for community member for importing electricity from the grid.
    :param self:
    :return:  a dict of energy cost for member per timestep
    """
    costs_dict = {}
    members = [AgentType.CONSUMER, AgentType.PROSUMER]
    for agent in self.schedule.agents:
        if agent.agent_type in members:
            key = str(agent.member_name) + str('_') + str(agent.unique_id)
            costs_dict[key] = agent.energy_cost
    return json.dumps(costs_dict)


def get_date(self):
    """"
    Returns the date for the model simulation
    """
    return self.date
