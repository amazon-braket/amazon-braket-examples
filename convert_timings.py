#!/usr/bin/env python3

# Convert timestamps to seconds and calculate total time
start_time = 1761886733  # NBI Provisioned
end_time = 1761886893    # LCC Setup Completed

total_seconds = end_time - start_time
print(f"Total setup time: {total_seconds} seconds")
print(f"Total setup time: {total_seconds/60:.2f} minutes")