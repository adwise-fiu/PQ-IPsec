#!/bin/bash

# Kill charon process
sudo pkill -9 charon

# Define valid signatures
valid_signatures=("rsa" "ecdsa" "ed25519" "dilithium2" "dilithium3" "dilithium5" "falcon512" "falcon1024")

# Create base certificates directory
base_dir="certificates"
mkdir -p $base_dir

# Generate certificates for each signature type
for signature in "${valid_signatures[@]}"; do
    echo "Generating certificates for $signature"
    cert_dir="$base_dir/$signature"
    mkdir -p $cert_dir
    cd $cert_dir

    # Generate CA key and certificate
    pki --gen --type $signature --outform pem > caKey.pem
    pki --self --type priv --in caKey.pem --ca --lifetime 3652 \
        --dn "C=CH, O=Cyber, CN=Cyber Root CA"                 \
        --outform pem > caCert.pem

    # Generate moon key and certificate
    pki --gen --type $signature --outform pem > moonKey.pem
    pki --issue --cacert caCert.pem --cakey caKey.pem  \
        --type priv --in moonKey.pem --lifetime 1461   \
        --dn "C=CH, O=Cyber, CN=moon.strongswan.org"   \
        --san moon.strongswan.org --outform pem > moonCert.pem

    # Generate carol key and certificate
    pki --gen --type $signature --outform pem > carolKey.pem
    pki --issue --cacert caCert.pem --cakey caKey.pem   \
        --type priv --in carolKey.pem --lifetime 1461   \
        --dn "C=CH, O=Cyber, CN=carol@strongswan.org"   \
        --san carol@strongswan.org --outform pem > carolCert.pem

    cd - > /dev/null
done

# Copy certs for the specified signature to SwanCtl directories
copy_certs_to_swanctl() {
    local sig=$1
    sudo cp $base_dir/$sig/caCert.pem /etc/swanctl/x509ca/
    sudo cp $base_dir/$sig/moonCert.pem /etc/swanctl/x509/
    sudo cp $base_dir/$sig/moonKey.pem /etc/swanctl/pkcs8/
}

# Check if a signature argument was provided
if [ $# -eq 1 ]; then
    signature=$1
    if [[ " ${valid_signatures[@]} " =~ " $signature " ]]; then
        copy_certs_to_swanctl $signature
    else
        echo "Error: Invalid signature. Valid options are: ${valid_signatures[*]}"
        exit 1
    fi
else
    echo "No signature specified. Certificates generated in $base_dir directory."
    echo "To copy certificates for a specific signature to SwanCtl directories, run the script with a signature argument."
fi

# Start charon process in the background
sudo /charon &
