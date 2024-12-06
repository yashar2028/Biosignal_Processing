#!/bin/bash

# Added to ensure this is root of the project
PROJECT_DIR=$(cd "$(dirname "$0")/.." && pwd)

echo "Initializing development environment for the project."

# Check if Nix is installed which is necessary
if ! command -v nix-shell &> /dev/null
then
    echo "Nix is not installed. Please install Nix first."
    exit 1
fi

# Run nix-shell to run devenv.nix (same as nix develop) to set up the environment (setting up the dependencies, versions, pre-hook-commits and etc.
echo "Running nix develop."
nix-shell "$PROJECT_DIR/devenv.nix" || { echo "Failed to enter nix-shell."; exit 1; }

echo "Development environment setup completed!"

