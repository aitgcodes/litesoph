#!/bin/bash

# Check if the type argument is provided
if [ -z "$1" ]; then
	echo "Error: No type provided. Usage: ./bootstrap.sh {type}"
	exit 1
fi

# Assign the first argument to a variable
TYPE=$(echo "$1" | tr '[:upper:]' '[:lower:]')

# Check if the provided type is valid
if [[ "$TYPE" != "ubuntu"]]; then
	echo "Error: Invalid type. Type can only be 'ubuntu'."
	exit 1
fi

# Perform actions based on the type
if [ "$TYPE" == "ubuntu" ]; then
	echo ""
fi