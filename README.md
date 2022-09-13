[Home](https://sonianmol.com/)

# Exploring demand response opportunities in Dutch energy communities

This is an agent-based simulation model created for evaluating the effect of demand response on the self-sufficiency and expenditure on electricity import for the modeled community.

## Contents

1. [Background](#Background)
2. [Model](#Model)
3. [Repository structure](#Repository structure)
4. [Using the model](#Using the model)
5. [Author](#Author)


## Background

With an exponential increase in distributed renewable energy, optimisation of local electricity consumption and generation is required to avoid congestion and overstressing in the distribution network. Recent literature suggests that Energy Communities along with smart-grid applications can effectively optimise local consumption and generation of electricity and stablise the distribution network. 

Energy communities are bottoms-up citizen-driven initiatives involved in generating and consuming electricity from renewable sources (e.g. Solar PV, Wind farms). Traditionally these communities constitute only residential members using electricity mostly in the morning and evening. Whereas, non-residential community members (such as schools, office buildings, etc.) located in the neighbourhood use electricity mostly during the work hours. Thus, this complementary electricity consumption profile by residential and non-residential buildings can be utilised through demand response. Demand response is an incentive-based policy instrument that rewards consumers for regulating their electricity consumption based on the availability and pricing. Thus, demand response not only stabilises the local distribution network but also is a step toward an inclusive, affordable and sustainable energy system.

This model allows the user to model an energy community (including both residential and non-residential members) and perform experiments to analyse the performance of a community using demand response. The current version of the model has electricity consumption data of different residential and non-residential Dutch buildings for the year 2021. Additional datasets from other locations can be added to the model if required.

This model was a part of the master's thesis project for  M.Sc. Engineering and Policy Analysis at TU Delft. This thesis project was done in collaboration with [Croonwolter&Dros](https://croonwolterendros.nl/).

**Note: The thesis report is available on the TU Delft repository and can be downloaded from this [link](https://repository.tudelft.nl/islandora/object/uuid:018c9e3f-9a64-469f-99a8-d9a0cf79308f).**

## Model

This model is an agent-based simulation model of a typical energy community. User need to specify the community configuration comprising of members and thier respective generation assets (such as solar PV/Wind). The model is simulated for one year where each time step is equivalent to 1 day. Electricity consumption data and weather data used in the model is from Netherlands recorded in the year 2021.

### System Relationship

The following system relationship is captured in the model. The figure below dipicts a typical energy community. The dotted line represents the system boundary of the complex adaptive system. Community members and generation assets exchange information and this information is collected by the coordinator. This information is used by the coordinator to prepare the day-ahead schedule and facilitate demand response. Levers box on the left showcase the interventions in the system. Uncertainties box on the top showcase the uncertainties used in this model for the analysis. Lastly, the box placed on the right contains the performance matrices used to evaluate the performance of the model.

<img src="images/Model-System-relationships.png">

### XLRM Framework

This model has adapted the following XLRM framework for facilitating virtual experimentation. In this framework Levers and Uncertainties are model inputs which are varied during different simulation runs. The outcome of the model is evaluated by recording and analysing the performance matrices under different input parameters. These results are further analysed to derive useful conclusions and recommendations.

<img src="images/Model-XLRM.png" alt="xlrm_diagram">

### Community members

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
│   
└───results                      # contains the script for extracting results from the model outputs

```
## Using the model

Clone this repository on your device/simulation machine. Detailed documentation is available [here](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository).

### Initialisation

This model requires an agent list to initialise an energy community. Currently, this model uses two real-life inspired energy community configurations. These communities only have residential community members therefore a hypothetical non-residential member is introduced to showcase the effect of complementary demand profile for demand response. Two existing community configurations are 'groene_mient' or 'gridflex_heeten'. These configurations are further described in `Modelling-Dutch-Energy-Communities/model/community_setup.py`. Agent list is a `list` of dictionaries 'dict' where each `dict` contains information about an agent.

Following is the example of an agent list.

```
agent_list =   [{'member_type': MemberType.NON_RESIDENTIAL, # agent 1
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
                                 'price': 0.15}]}]
```

The energy community can be initialised by `create_community_configuration` function and specifying either 'gridflex_heeten' or 'groene_mient' as the community name (`community_name`).

```
# Select the community to run the simulation 'groene_mient' or 'gridflex_heeten'
agents_list = create_community_configuration(community_name='gridflex_heeten')

# Setup model
model = EnergyCommunity(agents_list=agents_list)
```

### Simulation

An example simulation with default policy lever and uncertainty values is shown in `Modelling-Dutch-Energy-Communities/example/simulation.py `. Following code snippet simulates the model for 365 time steps (i.e. one year) and stores the simulation results in `results`.

```
# Run simulation
results = model.run_simulation(steps=365, time_tracking=True)
```
Default values of input parameters are shown below:

|Input parameter | Value | Description|
|-----------------|---|---------------------------------------------------------------------------------------------|
|Uncertainty `X1` |0.30| Minimum percentage of flexible demand available for demand response on a single day (Social)|
|Uncertainty `X2` |0.75| Maximum percentage of flexible demand available for demand response on a single day (Social)|
|Uncertainty `X3` |0.80| Percentage accuracy of day-ahead generation projections from renewable assets (Technical) |
|Lever `L1` |0.50| Percentage of members participating in the demand response program (Social) |
|Lever `L2` |0.20| Percentage of flexible (shift-able)  demand for residential community members (Technical) |
|Lever `L3` |0.30| Percentage of flexible (shift-able)  demand for non-residential community members (Technical) |

### Results

This model reports results in form of a dataframe. An example of extracting and visualising results is shown in `Modelling-Dutch-Energy-Communities/example/check_results.ipynb`.

### Analysis

For facilitating model-based decision-making, this model is simulated multiple times with different values of input parameters. Further details of performing these experiments are explained in `Modelling-Dutch-Energy-Communities/experiments/`. The outcome of these experiments is further analysed. Firstly, the most influential input parameters are identified using feature scoring. Secondly, the quantitative range of these influential parameters is identified through scenario discovery. Lastly, this information is used to formulate recommendations for the modelled community. An example of this analysis is shown in `Modelling-Dutch-Energy-Communities/results/plotting_results.ipynb`.

## Author

- [@SoniAnmol](https://www.github.com/SoniAnmol) - Anmol Soni
