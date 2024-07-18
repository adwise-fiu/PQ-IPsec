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
kem_proposals = [
    "x25519",
    "ke1_kyber1-x25519",
    "ke1_kyber3-x25519",
    "ke1_kyber5-x25519",
    "ke1_kyber3-ke2_bike3-ke3_hqc3-x25519",
]
modes = {
    "unlimited": "0% Packet Loss",
    "05pl": "1% Packet Loss",
    "0ping1pl": "2% Packet Loss",
    "0ping25pl": "5% Packet Loss",
    # "0ping5pl": "5% Packet Loss",
}

# Check for vmrun
vmrun_path = shutil.which("vmrun")
if not vmrun_path:
    print(
        f"Could not find vmrun. Install vmrun from {''.format('', 'https://www.vmware.com/products/desktop-hypervisor.html', 'VMware')}"
    )
    exit()

# Set up VMware
carol = VMware(
    vmrun_path=vmrun_path,
    vm_path=os.getenv("CAROL_VM_PATH"),
)
carol.set_guest_user(os.getenv("CAROL_USER"))
carol.set_guest_password(os.getenv("CAROL_PASSWORD"))

# Process results
results = {}
for mode_key, mode_label in modes.items():
    for cert in certificates:
        for kem in kem_proposals:
            file_name = f"{cert}_{kem}_{mode_key}.txt"
            # Copy file from guest to host
            # res = carol.copy_file_from_guest_to_host(
            #     guest_path=os.path.join(
            #         os.getenv("GUEST_MEASUREMENTS_PATH"), file_name
            #     ),
            #     host_path=os.path.join(os.getenv("HOST_DATA_PATH"), file_name),
            # )
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

# Create multi-KEM visualization
plt.style.use("default")
fig, axs = plt.subplots(3, 2, figsize=(20, 30))
axs = axs.flatten()

width = 0.15
x = np.arange(len(certificates))

# Define a vibrant color palette
colors = ["#58508d", "#bc5090", "#ff6361", "#ffa600"]

for idx, kem in enumerate(kem_proposals):
    ax = axs[idx]
    kem_data = df[df["KEM"] == kem]

    for i, (mode_key, mode_label) in enumerate(modes.items()):
        runtimes = [
            kem_data[
                (kem_data["Certificate"] == cert)
                & (kem_data["Network Condition"] == mode_label)
            ]["Runtime (ms)"].values[0]
            for cert in certificates
        ]
        ax.bar(
            x + (i - len(modes) / 2 + 0.5) * width,
            runtimes,
            width,
            label=mode_label,
            color=colors[i],  # Use the vibrant colors
            edgecolor="black",
            linewidth=0.5,
        )

    ax.set_facecolor("#F0F0F0")  # Light gray background
    ax.set_xticks(x)
    ax.set_xticklabels(certificates, rotation=45, ha="right")
    ax.set_xlabel("Certificate", fontsize=10, fontweight="bold")
    ax.set_ylabel("Average Runtime (ms)", fontsize=10, fontweight="bold")
    ax.yaxis.grid(True, linestyle="--", alpha=0.7, color="white")

    ax.set_title(
        f"Runtime Analysis: Network Condition Comparison using {kem}",
        fontsize=12,
        fontweight="bold",
        pad=20,
    )

    if idx == 0:
        ax.legend(
            title="Network Condition",
            title_fontsize="10",
            fontsize="8",
            loc="upper left",
        )

    for i, mode_key in enumerate(modes.keys()):
        for j, cert in enumerate(certificates):
            v = kem_data[
                (kem_data["Certificate"] == cert)
                & (kem_data["Network Condition"] == modes[mode_key])
            ]["Runtime (ms)"].values[0]
            ax.text(
                j + (i - len(modes) / 2 + 0.5) * width,
                v,
                f"{v:.1f}",
                ha="center",
                va="bottom",
                fontsize=6,
                rotation=90,
                color="black",  # Ensure text is visible
            )

# Remove the unused sixth subplot
fig.delaxes(axs[5])

plt.tight_layout()
plt.show()
