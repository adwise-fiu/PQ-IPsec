import os
import time
import shutil
from vmware_fusion_py import VMware
from strongswan_manager import StrongSwan
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

certificates = [
    # "ecdsa",
    # "ed25519",
    # "rsa",
    # "falcon512",
    # "falcon1024",
    "dilithium2",
    # "dilithium3",
    # "dilithium5",
]
base_proposal = "aes256-sha256"
kem_proposals = [
    "x25519",
    "ke1_kyber1-x25519",
    "ke1_kyber3-x25519",
    "ke1_kyber5-x25519",
    "ke1_kyber3-ke2_bike3-ke3_hqc3-x25519",
]
mode = "200ping0pl"
log_names = []
iterations = str(500)

carol_conf_path = os.getenv("CAROL_CONF_PATH")
moon_conf_path = os.getenv("MOON_CONF_PATH")
certificates_path = os.getenv("CERTIFICATES_PATH")

if not carol_conf_path or not moon_conf_path or not certificates_path:
    print("Please provideCAROL_CONF_PATH, MOON_CONF_PATH and CERTIFICATES_PATH!")
    exit(1)

# Initialize vmware class
vmrun_path = shutil.which("vmrun")
if not vmrun_path:
    print(
        f"Could not find vmrun. Install vmrun from {"".format('', "https://www.vmware.com/products/desktop-hypervisor.html", "VMware")}"
    )
    exit()

carol = VMware(
    vmrun_path=vmrun_path,
    vm_path=os.getenv("CAROL_VM_PATH") or "",
)

carol.set_guest_user(os.getenv("CAROL_USER"))
carol.set_guest_password(os.getenv("CAROL_PASSWORD"))

moon = VMware(
    vmrun_path=vmrun_path,
    vm_path=os.getenv("MOON_VM_PATH") or "",
)

moon.set_guest_user(os.getenv("MOON_USER"))
moon.set_guest_password(os.getenv("MOON_PASSWORD"))

# Start the VMs
carol.start()
moon.start()

# Initialize StrongSwan class
strongswan = StrongSwan(carol_conf_path, moon_conf_path)

for certificate in certificates:
    print(f"Updating certificates to {certificate}")
    certificate_path = certificates_path + "/" + certificate + "/"

    print(
        carol.copy_file_from_host_to_guest(
            host_path=certificate_path + "carolCert.pem",
            guest_path="/etc/swanctl/x509/carolCert.pem",
        )
    )
    print(
        carol.copy_file_from_host_to_guest(
            host_path=certificate_path + "carolKey.pem",
            guest_path="/etc/swanctl/pkcs8/carolKey.pem",
        )
    )
    print(
        carol.copy_file_from_host_to_guest(
            host_path=certificate_path + "caCert.pem",
            guest_path="/etc/swanctl/x509ca/caCert.pem",
        )
    )
    print(
        moon.copy_file_from_host_to_guest(
            host_path=certificate_path + "moonCert.pem",
            guest_path="/etc/swanctl/x509/moonCert.pem",
        )
    )
    print(
        moon.copy_file_from_host_to_guest(
            host_path=certificate_path + "moonKey.pem",
            guest_path="/etc/swanctl/pkcs8/moonKey.pem",
        )
    )
    print(
        moon.copy_file_from_host_to_guest(
            host_path=certificate_path + "caCert.pem",
            guest_path="/etc/swanctl/x509ca/caCert.pem",
        )
    )
    print(f"Updated certificates to {certificate}")

    for proposal in kem_proposals:
        print(f"Updating proposals to {base_proposal}-{proposal}")
        proposals = f"{base_proposal}-{proposal}"
        strongswan.update_proposals(proposals)
        carol.copy_file_from_host_to_guest(
            host_path=carol_conf_path, guest_path="/etc/swanctl/swanctl.conf"
        )
        moon.copy_file_from_host_to_guest(
            host_path=moon_conf_path, guest_path="/etc/swanctl/swanctl.conf"
        )
        print(f"Updated proposals")
        carol.run_program_in_guest(
            os.getenv("CAROL_RELOAD_SCRIPT"),
            program_arguments=[os.getenv("CAROL_PASSWORD")],
        )
        moon.run_program_in_guest(
            os.getenv("MOON_RELOAD_SCRIPT"),
            program_arguments=[
                os.getenv("MOON_PASSWORD")
            ],  # Fixed: now uses MOON_PASSWORD
        )
        carol.run_program_in_guest(
            os.getenv("CAROL_BENCHMARK_SCRIPT"),
            program_arguments=[
                certificate,
                proposal,
                mode,
                iterations,
                os.getenv("CAROL_PASSWORD"),
            ],
        )
        log_names.append(f"{certificate}_{proposal}_{mode}")
        print(
            f"Completed benchmark for {certificate}-{proposal}-{mode} with {iterations} connections."
        )

print(log_names)
print("Complete")
