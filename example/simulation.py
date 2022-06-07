from model.model_code import EnergyCommunity

model = EnergyCommunity()
results = model.run_simulation(steps=30, time_tracking=True)
# results.to_csv('../results/simulation_results.csv', index=False)
