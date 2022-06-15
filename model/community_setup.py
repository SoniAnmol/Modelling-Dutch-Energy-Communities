"""This script is used to set up agents for the simulation."""

from model.agents import *


def generate_agent_list():
    # Setup Residential Agents

    # Household types is chosen randomly from the list of possible household types
    number_of_households = 2
    hh_type = ['hh1_consumption [kWh]', 'hh2_consumption [kWh]', 'hh3_consumption [kWh]']
    residential_agents = []
    for _ in range(number_of_households):
        residential_agents.append({'member_name': random.choice(hh_type),
                                   'member_type': MemberType.RESIDENTIAL,
                                   'agent_type': AgentType.CONSUMER,
                                   'demand_flexibility': 0.20,
                                   'asset_list': None})

    # Setup non-residential agents
    non_residential_agents = [{'member_type': MemberType.NON_RESIDENTIAL,
                               'member_name': 'Office 1',
                               'agent_type': AgentType.PROSUMER,
                               'demand_flexibility': 0.20,
                               'asset_list': [
                                   {'agent_type': Asset,
                                    'asset_type': Solar,
                                    'capacity': 100,
                                    'efficiency': 0.20,
                                    'price': 0.15}]},
                              {'member_type': MemberType.NON_RESIDENTIAL,
                               'member_name': 'Office 2',
                               'agent_type': AgentType.PROSUMER,
                               'demand_flexibility': 0.20,
                               'asset_list': [
                                   {'agent_type': Asset,
                                    'asset_type': Solar,
                                    'capacity': 200,
                                    'efficiency': 0.20,
                                    'price': 0.15}]},
                              {'member_type': MemberType.NON_RESIDENTIAL,
                               'member_name': 'school_mbo',
                               'agent_type': AgentType.CONSUMER,
                               'demand_flexibility': 0.20,
                               'asset_list': None},
                              {'member_type': MemberType.NON_RESIDENTIAL,
                               'member_name': 'EV_bus_charging_station',
                               'agent_type': AgentType.CONSUMER,
                               'demand_flexibility': 0.20,
                               'asset_list': None}]
    coordinator = [{'member_type': MemberType.COORDINATOR}]

    # Combine residential and non-residential agents
    agent_list = residential_agents + non_residential_agents + coordinator
    return agent_list
