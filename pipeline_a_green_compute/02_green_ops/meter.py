import sys
import os
import time
from codecarbon import EmissionsTracker

# --- 1. Import the Router from Project 1 ---
# We add the previous folder to the system path so Python can find 'router.py'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '01_eco_route')))

try:
    from router import EcoRouter
except ImportError:
    print("❌ Error: Could not find router.py in ../01_eco_route/")
    sys.exit(1)

# --- 2. The Green-Ops Monitor Class ---
class EnergyMonitor:
    def __init__(self, output_dir="."):
        self.router = EcoRouter()
        self.output_dir = output_dir

    def run_audit(self, prompt, complexity, iterations=3):
        """
        Runs the router multiple times while measuring energy.
        """
        project_name = f"audit_{complexity}_{int(time.time())}"
        
        # Initialize the tracker
        # We explicitly track the GPU energy (pynvml) and CPU energy
        tracker = EmissionsTracker(
            project_name=project_name,
            output_dir=self.output_dir,
            measure_power_secs=1,  # Measure every second for precision
            save_to_file=True
        )

        print(f"\n🔌 STARTING ENERGY AUDIT: '{prompt}' ({complexity})")
        tracker.start()
        
        try:
            for i in range(iterations):
                print(f"   [Step {i+1}/{iterations}] Routing query...")
                # The actual work happens here
                result = self.router.route_query(prompt, model_complexity=complexity)
                # print(f"   ---> Result snippet: {result[:50]}...") 
        finally:
            # Always stop the tracker, even if the code crashes
            emissions = tracker.stop()
        
        print(f"✅ AUDIT COMPLETE.")
        print(f"   Total Emissions: {emissions:.6f} kg CO2eq")
        print(f"   Energy Consumed: {tracker.final_emissions_data.energy_consumed:.6f} kWh")
        print(f"   Data saved to: {os.path.join(self.output_dir, 'emissions.csv')}")

# --- 3. Execution ---
if __name__ == "__main__":
    monitor = EnergyMonitor()

    # Scenario A: Local Heavy Lift (Dirty Grid or Easy Task)
    # Note: To force GPU usage, run this when your mock grid is "High"
    # or just trust the easy task logic.
    monitor.run_audit("Write a poem about rust programming", complexity="easy", iterations=2)
    
    # Scenario B: Cloud Offload (Green Grid + Hard Task)
    # This consumes almost ZERO local energy because it just hits the mock API.
    monitor.run_audit("Calculate the trajectory of a rocket", complexity="hard", iterations=2)