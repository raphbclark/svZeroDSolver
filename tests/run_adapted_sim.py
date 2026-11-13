import pysvzerod
import pandas as pd

def run_adapted_model():
    config_file = "cases/CRL_closed_loop.json"
    print(f"Loading {config_file} and initializing pysvzerod...")
    
    # Initialize the solver using the JSON configuration
    solver = pysvzerod.Solver(config_file)
    
    # Run the simulation
    solver.run()
    
    # Retrieve the full result as a pandas DataFrame
    df = solver.get_full_result()
    
    output_filename = "adapted_simulation_results.csv"
    df.to_csv(output_filename, index=False)
    
    print(f"Success! Data saved to {output_filename}")

if __name__ == "__main__":
    run_adapted_model()