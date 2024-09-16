# Check if the password argument is provided
if [ -z "$1" ]; then
    echo "Please provide the sudo password as an argument."
    exit 1
fi

# File to store the output
output_file=~/reload_settings_output.txt

# Run the commands with the provided password and save the output
echo "$1" | sudo -S swanctl --reload-settings >> $output_file 2>&1
echo "$1" | sudo -S swanctl --load-all >> $output_file 2>&1

echo "Output saved to $output_file"
