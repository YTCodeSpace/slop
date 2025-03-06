import time
import numpy as np
from itertools import combinations_with_replacement
from ortools.linear_solver import pywraplp

# ✅ Define stock length and piece sizes as floats
# Define the stock length
stock_length = 6000

# Define piece sizes and their demand
sizes = [300.5, 450.2, 250.7,1002.8,2050,580.2,1785.9]
demand = [505, 300, 600,200,100,100,250]

# ⏳ Step 1: Generate valid cutting patterns
def generate_patterns(sizes, stock_length, tolerance=1e-6):
    patterns = []
    for r in range(1, int(stock_length // min(sizes)) + 2):  # Max items that can fit
        for comb in combinations_with_replacement(sizes, r):
            total_length = sum(comb)
            if total_length <= stock_length + tolerance:  # Allow small float precision errors
                pattern = [comb.count(size) for size in sizes]
                if pattern not in patterns:
                    patterns.append(pattern)
    return patterns

start_time = time.time()
patterns = generate_patterns(sizes, stock_length)
pattern_gen_time = time.time() - start_time

# ✅ Step 2: Set up the OR-Tools solver (Mixed Integer Linear Programming)
solver = pywraplp.Solver.CreateSolver("SCIP")
if not solver:
    raise Exception("SCIP Solver not available.")

# ✅ Step 3: Define decision variables (how many times each pattern is used)
x = [solver.IntVar(0, solver.infinity(), f'Pattern_{i}') for i in range(len(patterns))]

# ✅ Step 4: Objective Function: Minimize stock sheets used
solver.Minimize(solver.Sum(x))

# ✅ Step 5: Add constraints to satisfy demand
for j in range(len(sizes)):
    solver.Add(solver.Sum(patterns[i][j] * x[i] for i in range(len(patterns))) >= demand[j])

# ✅ Step 6: Solve the problem
solve_start_time = time.time()
status = solver.Solve()
solve_time = time.time() - solve_start_time

# ✅ Step 7: Print results
if status == pywraplp.Solver.OPTIMAL:
    print("\n✅ Optimal Cutting Patterns:")
    for i, var in enumerate(x):
        if var.solution_value() > 0:
            print(f"Use pattern {patterns[i]} → {int(var.solution_value())} times")
    print(f"\n🔹 Minimum sheets needed: {int(solver.Objective().Value())}")
else:
    print("❌ No optimal solution found.")

# 🕒 Print Performance Metrics
print(f"\n⏳ Pattern Generation Time: {pattern_gen_time:.4f} sec")
print(f"⚡ Solver Time: {solve_time:.4f} sec")
print(f"🔹 Total Patterns Generated: {len(patterns)}")
