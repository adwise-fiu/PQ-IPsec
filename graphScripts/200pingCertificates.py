import os
import shutil
from vmware_fusion_py import VMware
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define constants
certificates = [
    "ed25519",
    "ecdsa",
    "rsa",
    "falcon512",
    "falcon1024",
    "dilithium2",
    "dilithium3",
    "dilithium5",
]
kem_proposals = ["x25519"]  # Only x25519
modes = {
    "200ping0pl": "0% Packet Loss",
    "200ping05pl": "1% Packet Loss",
    "200ping1pl": "2% Packet Loss",
    # "100ping25pl": "5% Packet Loss",
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
for mode_key in modes.keys():
    for cert in certificates:
        for kem in kem_proposals:
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
for mode_key, mode_label in modes.items():
    for cert in certificates:
        for kem in kem_proposals:
            file_name = f"{cert}_{kem}_{mode_key}.txt"
            with open(os.path.join(os.getenv("HOST_DATA_PATH"), file_name), "r") as f:
                lines = f.readlines()
                runtimes = [float(line.strip()) for line in lines]
                avg_runtime = sum(runtimes) / len(runtimes) * 1000
                print(
                    f"{file_name} took {avg_runtime:.2f}ms on average with {len(runtimes)} iterations"
                )
                results[(cert, kem, mode_key)] = avg_runtime

# Create a DataFrame from the results
data = [
    {
        "Certificate": cert,
        "KEM": kem,
        "Network Condition": modes[mode_key],
        "Runtime (ms)": results[(cert, kem, mode_key)],
    }
    for cert in certificates
    for kem in kem_proposals
    for mode_key in modes.keys()
]
df = pd.DataFrame(data)

# Create visualization
plt.figure(figsize=(20, 14))  # Increased figure size
plt.style.use("default")

# Set up the bar plot
x = np.arange(len(certificates))
width = 0.2
multiplier = 0

# Define different hatch patterns for each network condition
hatches = ["/", "\\", "x", "."]

# Plot bars for each network condition
for mode_key, mode_label in modes.items():
    runtimes = [
        df[(df["Certificate"] == cert) & (df["Network Condition"] == mode_label)][
            "Runtime (ms)"
        ].values[0]
        for cert in certificates
    ]
    offset = width * multiplier
    rects = plt.bar(
        x + offset,
        runtimes,
        width,
        label=mode_label,
        color="white",
        edgecolor="black",
        hatch=hatches[multiplier],
        linewidth=3,
    )
    multiplier += 1

# Customize the plot
plt.xlabel("Certificate", fontsize=32, fontweight="bold")
plt.ylabel("Average Runtime (ms)", fontsize=32, fontweight="bold")
plt.xticks(x + width * 1.5, certificates, rotation=45, ha="right", fontsize=28)
plt.yticks(fontsize=28)

# Increase legend font size and move it outside the plot
plt.legend(
    title="Network Condition",
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
    os.getenv("HOST_DATA_PATH"), "x25519_certificate_network_comparison_plot_bw.png"
)
plt.savefig(output_path, dpi=300, bbox_inches="tight")
print(f"Plot saved as {output_path}")

# Close the plot to free up memory
plt.close()
