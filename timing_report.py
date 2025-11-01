#!/usr/bin/env python3

# Amazon Braket Setup Timing Report

print("=" * 60)
print("AMAZON BRAKET SETUP TIMING REPORT")
print("=" * 60)

# Timestamps
start_time = 1761886733  # NBI Provisioned
end_time = 1761886893    # LCC Setup Completed
total_seconds = end_time - start_time

print(f"\nOVERALL TIMING:")
print(f"Start Time (NBI Provisioned): {start_time}")
print(f"End Time (LCC Setup Completed): {end_time}")
print(f"Total Duration: {total_seconds} seconds ({total_seconds/60:.2f} minutes)")

# Component timings from timings.txt
components = [
    ("LCC Download", 22.81, 6.23, 4.15),
    ("LCC Unzip", 11.65, 9.72, 0.98),
    ("install-scripts/30-install-examples.sh", 0.00, 0.00, 0.00),
    ("install-scripts/40-install-algos.sh", 0.00, 0.00, 0.00),
    ("install-scripts/45-setup-temp-dirs.sh", 0.49, 0.15, 0.12),
    ("install-scripts/50-update_jupyter_server_config.sh", 0.00, 0.00, 0.00),
    ("install-scripts/60-update_pycodestyle_config.sh", 0.00, 0.00, 0.00),
    ("install-scripts/70-set-visual-theme.sh", 0.00, 0.00, 0.00),
    ("install-scripts/80-autostop-entry.sh", 0.00, 0.00, 0.00),
    ("parallel-scripts/10-remove-sm-kernels-conda.sh", 0.03, 0.02, 0.00),
    ("parallel-scripts/15-juypter-sys-env-update.sh", 15.08, 9.60, 0.97),
    ("parallel-scripts/20-install-braket-kernels.sh", 123.39, 18.75, 11.36),
    ("LCC Install", 124.06, 28.61, 12.51)
]

print(f"\nDETAILED COMPONENT TIMINGS:")
print(f"{'Component':<50} {'Real':<8} {'User':<8} {'Sys':<8}")
print("-" * 75)

total_real = 0
for name, real, user, sys in components:
    print(f"{name:<50} {real:<8.2f} {user:<8.2f} {sys:<8.2f}")
    total_real += real

print("-" * 75)
print(f"{'TOTAL':<50} {total_real:<8.2f}")

print(f"\nTOP TIME CONSUMERS:")
sorted_components = sorted(components, key=lambda x: x[1], reverse=True)
for i, (name, real, user, sys) in enumerate(sorted_components[:5]):
    if real > 0:
        percentage = (real / total_real) * 100
        print(f"{i+1}. {name}: {real:.2f}s ({percentage:.1f}%)")

print(f"\nSUMMARY:")
print(f"• Total setup time: {total_seconds} seconds ({total_seconds/60:.2f} minutes)")
print(f"• Longest component: install-braket-kernels.sh ({123.39:.2f}s)")
print(f"• Most components completed instantly (0.00s)")
print(f"• Setup includes Braket SDK, PennyLane, Qiskit, and CUDA-Q")