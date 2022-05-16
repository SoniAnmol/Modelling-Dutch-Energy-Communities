"""This script is used to set up agents for the simulation."""

from model.agents import *


def generate_agent_list():
    # Setup Residential Agents

    # Household types is chosen randomly from the list of possible household types
    number_of_households = 10
    hh_type = ['hh1_consumption [kWh]', 'hh2_consumption [kWh]', 'hh3_consumption [kWh]']
    residential_agents = []
    for _ in range(number_of_households):
        residential_agents.append({'member_name': random.choice(hh_type),
                                   'agent_type': Residential,
                                   'member_type': MemberType.CONSUMER,
                                   'asset_list': None})

    # Setup non-residential agents
    non_residential_agents = [{'agent_type': NonResidential,
                               'member_name': 'drink_packaging_sme',
                               'member_type': MemberType.PROSUMER,
                               'asset_list': [
                                   {'agent_type': Asset,
                                    'asset_type': Solar,
                                    'capacity': 1285,
                                    'efficiency': 0.20,
                                    'price': 0.15}]},
                              {'agent_type': NonResidential,
                               'member_name': 'food_packaging_sme',
                               'member_type': MemberType.PROSUMER,
                               'asset_list': [
                                   {'agent_type': Asset,
                                    'asset_type': Solar,
                                    'capacity': 2000,
                                    'efficiency': 0.20,
                                    'price': 0.15}]},
                              {'agent_type': NonResidential,
                               'member_name': 'school_mbo',
                               'member_type': MemberType.CONSUMER,
                               'asset_list': None},
                              {'agent_type': EVChargingStation,
                               'member_name': 'EV_bus_charging_station',
                               'member_type': MemberType.CONSUMER,
                               'asset_list': None}]

    # Combine residential and non-residential agents
    agent_list = [{'agent_type': Coordinator}] + residential_agents + non_residential_agents
    return agent_list
