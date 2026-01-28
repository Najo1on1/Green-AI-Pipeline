import sys
import os
import time
import statistics

# --- Import from Project 2 ---
# Add the Green-Ops folder to path so we can reuse the EnergyMonitor
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '02_green_ops')))

try:
    from meter import EnergyMonitor
except ImportError:
    print("❌ Error: Could not find meter.py in ../02_green_ops/")
    sys.exit(1)

class QuantLab:
    def __init__(self):
        self.monitor = EnergyMonitor(output_dir=".")

    def run_benchmark(self, model_name="Mistral-7B-AWQ", iterations=5):
        print(f"\n🔬 INITIALIZING QUANTIZATION LAB: {model_name}")
        print(f"   Target: Calculate Joules Per Token (J/tok)")
        
        prompt = "Write a detailed technical paragraph about the benefits of 4-bit quantization in Neural Networks."
        
        # We assume 1 word ~= 1.3 tokens for estimation
        total_tokens_generated = 0
        latencies = []
        
        # We start the energy tracker ONCE for the whole batch to get a stable reading
        # (Starting/Stopping it too fast can be noisy)
        self.monitor.router = self.monitor.router # Ensure router is ready
        
        print(f"   🚀 Starting Stress Test ({iterations} iterations)...")
        
        # Start Tracking Energy
        # Note: We access the internal tracker logic from EnergyMonitor manually 
        # or we just use the class's method if it supported batching. 
        # For simplicity, we wrap the loop in a new tracker instance here.
        from codecarbon import EmissionsTracker
        tracker = EmissionsTracker(project_name="quant_lab_benchmark", output_dir=".", measure_power_secs=1)
        tracker.start()
        
        start_time = time.time()
        
        try:
            for i in range(iterations):
                req_start = time.time()
                # Force "easy" complexity to ensure LOCAL GPU usage
                # (Remember: router logic says Easy -> Local)
                response = self.monitor.router.route_query(prompt, model_complexity="easy")
                req_time = time.time() - req_start
                
                # Estimate tokens
                # A rough heuristic: len(text) / 4 chars per token
                tokens = len(response) / 4
                total_tokens_generated += tokens
                latencies.append(req_time)
                
                print(f"     [Iter {i+1}] {tokens:.0f} tokens in {req_time:.2f}s ({(tokens/req_time):.1f} tok/s)")

        finally:
            emissions = tracker.stop()
            total_time = time.time() - start_time

        # --- Analysis ---
        energy_kwh = tracker.final_emissions_data.energy_consumed
        energy_joules = energy_kwh * 3_600_000  # Convert kWh to Joules
        
        avg_tps = total_tokens_generated / total_time
        joules_per_token = energy_joules / total_tokens_generated if total_tokens_generated > 0 else 0

        print(f"\n📊 BENCHMARK RESULTS: {model_name}")
        print(f"   ----------------------------------------")
        print(f"   Total Time:      {total_time:.2f} s")
        print(f"   Total Tokens:    {total_tokens_generated:.0f}")
        print(f"   Speed (TPS):     {avg_tps:.2f} tokens/sec")
        print(f"   Total Energy:    {energy_joules:.2f} Joules")
        print(f"   ----------------------------------------")
        print(f"   ⚡ EFFICIENCY SCORE: {joules_per_token:.4f} Joules/Token")
        print(f"   ----------------------------------------")

if __name__ == "__main__":
    lab = QuantLab()
    lab.run_benchmark()