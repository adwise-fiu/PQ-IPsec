#!/bin/bash

certificate=$1
proposal=$2
constraint=$3

output_file="~/measurements/${certificate}_${proposal}_${constraint}.txt"

sleep_duration=0.1  # Adjust the sleep duration as needed (in seconds)

for i in {1..10}; do
  start=$(date +%s.%N)
  sudo swanctl --initiate --ike home
  end=$(date +%s.%N)
  runtime=$(echo "$end - $start" | bc -l)
  echo "$runtime" >> "$output_file"
  sleep $sleep_duration
  sudo swanctl --terminate --ike home
done
