import os
import shutil
from vmware_fusion_py import VMware
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define constants
combinations = [
    ("rsa", "x25519", "RSA + x25519"),
    ("falcon1024", "ke1_kyber3-x25519", "Dilithium 2 + Kyber1"),
]
modes = {
    "200ping0pl": "0% Packet Loss",
    "200ping05pl": "1% Packet Loss",
    "200ping1pl": "2% Packet Loss",
    # "200ping25pl": "5% Packet Loss",
}

# Check for vmrun
vmrun_path = shutil.which("vmrun")

# Set up VMware
carol = VMware(
    vmrun_path=vmrun_path,
    vm_path=os.getenv("CAROL_VM_PATH"),
)
carol.set_guest_user(os.getenv("CAROL_USER"))
carol.set_guest_password(os.getenv("CAROL_PASSWORD"))

# Download files from Carol
for cert, kem, _ in combinations:
    for mode_key in modes.keys():
        file_name = f"{cert}_{kem}_{mode_key}.txt"
        guest_path = os.path.join(os.getenv("GUEST_MEASUREMENTS_PATH"), file_name)
        host_path = os.path.join(os.getenv("HOST_DATA_PATH"), file_name)

        res = carol.copy_file_from_guest_to_host(
            guest_path=guest_path,
            host_path=host_path,
        )

        if res:
            print(f"Successfully downloaded {file_name}")
        else:
            print(f"Failed to download {file_name}")

# Process results
results = {}
for cert, kem, label in combinations:
    for mode_key, mode_label in modes.items():
        file_name = f"{cert}_{kem}_{mode_key}.txt"
        file_path = os.path.join(os.getenv("HOST_DATA_PATH"), file_name)
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                lines = f.readlines()
                runtimes = [float(line.strip()) for line in lines]
                avg_runtime = sum(runtimes) / len(runtimes) * 1000
                print(
                    f"{file_name} took {avg_runtime:.2f}ms on average with {len(runtimes)} iterations"
                )
                results[(cert, kem, mode_key)] = avg_runtime
        else:
            print(f"Warning: File not found - {file_path}")

# Create a DataFrame from the results
data = []
for cert, kem, label in combinations:
    for mode_key, mode_label in modes.items():
        if (cert, kem, mode_key) in results:
            data.append(
                {
                    "Combination": label,
                    "Network Condition": mode_label,
                    "Runtime (ms)": results[(cert, kem, mode_key)],
                }
            )
        else:
            print(f"Warning: No data for {label} in {mode_label} condition")

df = pd.DataFrame(data)

# Create visualization
plt.figure(figsize=(20, 14))  # Increased figure size
plt.style.use("default")

# Set up the bar plot
x = np.arange(len(modes))
width = 0.35

# Define hatches for each combination
hatches = ["/", "\\"]

# Plot bars for each combination
for i, (_, _, label) in enumerate(combinations):
    runtimes = []
    for mode_label in modes.values():
        runtime_data = df[
            (df["Combination"] == label) & (df["Network Condition"] == mode_label)
        ]["Runtime (ms)"]
        if not runtime_data.empty:
            runtimes.append(runtime_data.values[0])
        else:
            runtimes.append(0)  # or np.nan if you prefer
    offset = width * (i - 0.5)
    rects = plt.bar(
        x + offset,
        runtimes,
        width,
        label=label,
        color="white",
        edgecolor="black",
        hatch=hatches[i],
        linewidth=3,
    )
    # Removed the bar_label call to remove number labels on top of bars

# Customize the plot
plt.xlabel("Network Condition", fontsize=32, fontweight="bold")
plt.ylabel("Average Runtime (ms)", fontsize=32, fontweight="bold")
# Removed the title
plt.xticks(x, modes.values(), rotation=45, ha="right", fontsize=28)
plt.yticks(fontsize=28)

# Increase legend font size and move it outside the plot
plt.legend(
    title="Combination",
    title_fontsize=32,
    fontsize=28,
)

plt.grid(True, axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()

# Make the plot border thicker
for spine in plt.gca().spines.values():
    spine.set_linewidth(3)

# Save the plot as a PNG file
output_path = os.path.join(
    os.getenv("HOST_DATA_PATH"), "rsa_x25519_vs_falcon1024_kyber5_comparison_bw.png"
)
plt.savefig(output_path, dpi=300, bbox_inches="tight")
print(f"Plot saved as {output_path}")

# Close the plot to free up memory
plt.close()
