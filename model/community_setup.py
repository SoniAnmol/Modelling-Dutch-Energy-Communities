"""This script is used to set up energy communities for the simulation."""

from model.agents import *


def create_community_configuration(community_name='groene_mient'):
    """
    This function creates a community configuration inspired by real energy communities/smart grid products.
    :param community_name: Name of the community
    :return: List: list of agents and their respective assets
    """
    if community_name == 'groene_mient':
        number_of_prosumer_households = 23
        number_of_consumer_households = 0
        asset_list = [{'agent_type': Asset,
                       'asset_type': Solar,
                       'capacity': 20,
                       'efficiency': 0.20,
                       'price': 0.15}]

        residential_agent = prepare_residential_agent_list(number_of_consumer_households=number_of_consumer_households,
                                                           number_of_prosumer_households=number_of_prosumer_households,
                                                           hh_types=None,
                                                           asset_list=asset_list)

        # Setup Non-residential member
        non_residential_agents = [{'member_type': MemberType.NON_RESIDENTIAL,
                                   'member_name': 'School',
                                   'agent_type': AgentType.PROSUMER,
                                   'demand_flexibility': 0.20,
                                   'asset_list': [{'agent_type': Asset,
                                                   'asset_type': Solar,
                                                   'capacity': 300,
                                                   'efficiency': 0.20,
                                                   'price': 0.15}]}]

    elif community_name == 'gridflex_heeten':
        number_of_prosumer_households = 40
        number_of_consumer_households = 10

        asset_list = [{'agent_type': Asset,
                       'asset_type': Solar,
                       'capacity': 20,
                       'efficiency': 0.20,
                       'price': 0.15}]

        residential_agent = prepare_residential_agent_list(number_of_consumer_households=number_of_consumer_households,
                                                           number_of_prosumer_households=number_of_prosumer_households,
                                                           hh_types=None,
                                                           asset_list=asset_list)

        # Setup Non-residential member
        non_residential_agents = [{'member_type': MemberType.NON_RESIDENTIAL,
                                   'member_name': 'Office 1',
                                   'agent_type': AgentType.PROSUMER,
                                   'demand_flexibility': 0.20,
                                   'asset_list': [
                                       {'agent_type': Asset,
                                        'asset_type': Solar,
                                        'capacity': 400,
                                        'efficiency': 0.20,
                                        'price': 0.15}]},
                                  {'member_type': MemberType.NON_RESIDENTIAL,
                                   'member_name': 'EV_charging_station',
                                   'agent_type': AgentType.CONSUMER,
                                   'demand_flexibility': 0.20,
                                   'asset_list': None}]

    coordinator = [{'member_type': MemberType.COORDINATOR}]
    agent_list = residential_agent + non_residential_agents + coordinator

    return agent_list


def prepare_residential_agent_list(number_of_consumer_households, number_of_prosumer_households, hh_types=None,
                                   asset_list=None):
    if hh_types is None:
        hh_types = ['hh1_consumption [kWh]', 'hh2_consumption [kWh]', 'hh3_consumption [kWh]']

    residential_agents = []

    for _ in range(number_of_consumer_households):
        residential_agents.append({'member_name': random.choice(hh_types),
                                   'member_type': MemberType.RESIDENTIAL,
                                   'agent_type': AgentType.CONSUMER,
                                   'demand_flexibility': 0.20,
                                   'asset_list': None})
    if asset_list is not None:
        for _ in range(number_of_prosumer_households):
            residential_agents.append({'member_name': random.choice(hh_types),
                                       'member_type': MemberType.RESIDENTIAL,
                                       'agent_type': AgentType.PROSUMER,
                                       'demand_flexibility': 0.20,
                                       'asset_list': asset_list})
    return residential_agents


def generate_agent_list():
    # Setup Residential Agents

    # Household types is chosen randomly from the list of possible household types
    number_of_households = 2
    hh_types = ['hh1_consumption [kWh]', 'hh2_consumption [kWh]', 'hh3_consumption [kWh]']
    residential_agents = []
    for _ in range(number_of_households):
        residential_agents.append({'member_name': random.choice(hh_types),
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
                               'member_name': 'School',
                               'agent_type': AgentType.CONSUMER,
                               'demand_flexibility': 0.20,
                               'asset_list': None},
                              {'member_type': MemberType.NON_RESIDENTIAL,
                               'member_name': 'EV_charging_station',
                               'agent_type': AgentType.CONSUMER,
                               'demand_flexibility': 0.20,
                               'asset_list': None}]
    coordinator = [{'member_type': MemberType.COORDINATOR}]

    # Combine residential and non-residential agents
    agent_list = residential_agents + non_residential_agents + coordinator
    return agent_list
