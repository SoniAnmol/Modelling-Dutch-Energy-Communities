"""This script simulates a single simulation run for specified parameters"""

from model.model_code import EnergyCommunity
from model.community_setup import *

# Select the community to run the simulation 'groene_mient' or 'gridflex_heeten'
agents_list = create_community_configuration(community_name='gridflex_heeten')

# Setup model
model = EnergyCommunity(agents_list=agents_list)

# Run simulation
results = model.run_simulation(steps=365, time_tracking=True)

# Save results
results.to_csv('../results/simulation_results.csv', index=False)
