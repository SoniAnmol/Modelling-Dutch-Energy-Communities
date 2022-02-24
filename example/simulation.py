from model.model_code import EnergyCommunity

model = EnergyCommunity()
results = model.run_simulation(steps=10)
print(results)
