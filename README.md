[Home](https://sonianmol.com/)

# Exploring demand response opportunities in Dutch energy communities

This is an agent-based simulation model created for evaluating the effect of demand response on the self-sufficiency and expenditure on electricity import for the modeled community.

## Background

With an exponential increase in distributed renewable energy, optimisation of local electricity consumption and generation is required to avoid congestion and overstressing in the distribution network. Recent literature suggests that Energy Communities along with smart-grid applications can effectively optimise local consumption and generation of electricity and stablise the distribution network. 

Energy communities are bottoms-up citizen-driven initiatives involved in generating and consuming electricity from renewable sources (e.g. Solar PV, Wind farms). Traditionally these communities constitute only residential members using electricity mostly in the morning and evening. Whereas, non-residential community members (such as schools, office buildings, etc.) located in the neighbourhood use electricity mostly during the work hours. Thus, this complementary electricity consumption profile by residential and non-residential buildings can be utilised through demand response. Demand response is an incentive-based policy instrument that rewards consumers for regulating their electricity consumption based on the availability and pricing. Thus, demand response not only stabilises the local distribution network but also is a step toward an inclusive, affordable and sustainable energy system.

This model allows the user to model an energy community (including both residential and non-residential members) and perform experiments to analyse the performance of a community using demand response. The current version of the model has electricity consumption data of different residential and non-residential Dutch buildings for the year 2021. Additional datasets from other locations can be added to the model if required.

This model was a part of the master's thesis project for  M.Sc. Engineering and Policy Analysis at TU Delft. This thesis project was done in collaboration with [Croonwolter&Dros](https://croonwolterendros.nl/).

**Note: The thesis report is available on the TU Delft repository and can be downloaded from this [link](https://repository.tudelft.nl/islandora/object/uuid:018c9e3f-9a64-469f-99a8-d9a0cf79308f).**

## Current state

This document is not complete and will be updated shortly.

## Model

This model is an agent-based simulation model of a typical energy community. User need to specify the community configuration comprising of members and thier respective generation assets (such as solar PV/Wind). The model is simulated for one year where each time step is equivalent to 1 day. Electricity consumption data and weather data used in the model is from Netherlands recorded in the year 2021.

### System Relationship

The following system relationship is captured in the model. The figure below dipicts a typical energy community. The dotted line represents the system boundary of the complex adaptive system. Community members and generation assets exchange information and this information is collected by the coordinator. This information is used by the coordinator to prepare the day-ahead schedule and facilitate demand response. Levers box on the left showcase the interventions in the system. Uncertainties box on the top showcase the uncertainties used in this model for the analysis. Lastly, the box placed on the right contains the performance matrices used to evaluate the performance of the model.

<img src="images/Model-System-relationships.png">

### XLRM Framework

This model has adapted the following XLRM framework for facilitating virtual experimentation. In this framework Levers and Uncertainties are model inputs which are varied during different simulation runs. The outcome of the model is evaluated by recording and analysing the performance matrices under different input parameters. These results are further analysed to derive useful conclusions and recommendations.

<img src="images/Model-XLRM.png" alt="xlrm_diagram">

## Community members

This model has following demand profiles for simulating electricity consumption. These demand profiles can be combined in different
permutations and cobinations for creating unique community configurations.

- Three demand profiles for residential community members
- Four demand profiles for non-residential community members (office buildings)
- Demand profile of a School (MBO)
- Demand profile of an EV charging station with three slow chargers

## Repository structure

```angular2html
./Modelling-Dutch-Energy-Communities/
│
├───data                         # contains the data for the model
│   ├───processed                # contains cleaned and processed data used by the model
│   └───raw                      # contains raw data acquired from the source
├───evidence_files               # contains verification and validation evidence files
│   ├───figures_validation       # contains the plots generated from validation tests
│   └───figures_verification     # contains the plots generated from verification tests
├───example                      # contains an example simulation run script and results
├───experiments                  # contains experiment setup and script for performing experiments with the model
│   └───figures                  # contains figures generated from experiment results
│       ├───groene_mient         # contains results generated from the results of experiments performed on Groene Mint
│       └───gridflex             # contains results generated from the results of experiments performed on GridFlex
├───images                       # contains figures and illustrations for the model
│   └───UML                      # contains UML diagrams of the model
├───model                        # contains the model and agent scripts
│   └───__pycache__
└───results                      # contains the script for extracting results from the model outputs

```
## Using the model

Clone this repository on your device/simulation machine. Detailed documentation is available [here](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository).

### Initialisation

This model requires an agent list to initialise an energy community. Currently this model uses two real life inspired energy community configurations. These communities only have residential community member therefore a hypothetical non-residential member is introduce to showcase the effect of complementarty demand profile for demand response. Two existing community configurations are 'groene_mient' or 'gridflex_heeten'. These configurations are further described in `Modelling-Dutch-Energy-Communities/model/community_setup.py`. Agent list is a `list` of dictionaries 'dict' where each `dict` contains information of an agent.
Following is an example of agent list.

```agent_list =   [{'member_type': MemberType.NON_RESIDENTIAL, # agent 1
                 'member_name': 'Office 1',
                 'agent_type': AgentType.PROSUMER,
                 'demand_flexibility': 0.20,
                 'asset_list': [{'agent_type': Asset,  # generation asset
                                 'asset_type': Solar,
                                 'capacity': 100,
                                 'efficiency': 0.20,
                                 'price': 0.15}]},
                # agent 2
                {'member_type': MemberType.NON_RESIDENTIAL, 
                 'member_name': 'EV_charging_station',
                 'agent_type': AgentType.CONSUMER,
                 'demand_flexibility': 0.20,
                 'asset_list': [{'agent_type': Asset,  # generation asset
                                 'asset_type': Solar,
                                 'capacity': 400,
                                 'efficiency': 0.20,
                                 'price': 0.15}]}]```

### Simulation

### Results

## Analysis

## Author

- [@SoniAnmol](https://www.github.com/SoniAnmol) - Anmol Soni
