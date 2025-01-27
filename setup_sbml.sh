#!/bin/bash

# Exit on any error
set -e

# Update and install required packages
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    cmake \
    libsbml5-dev \
    swig \
    python3-dev \
    default-jdk \
    ruby-dev \
    mono-mcs

# Function to uninstall the library
deinstall_libsbmlsim() {
    echo "Uninstalling LibSBMLSim..."
    sudo make uninstall
    echo "LibSBMLSim uninstalled successfully!"
    exit 0
}

# Check for the --deinstall flag
if [ "$1" == "--deinstall" ]; then
    if [ -d "libsbmlsim/build" ]; then
        cd libsbmlsim/build
        deinstall_libsbmlsim
    else
        echo "Build directory not found. Please ensure LibSBMLSim is installed."
        exit 1
    fi
fi

# Clone the libsbmlsim repository
git clone https://github.com/libsbmlsim/libsbmlsim.git
cd libsbmlsim

# Create a build directory
mkdir -p build
cd build

# Configure the build with cmake
cmake .. -DWITH_PYTHON=ON

# Build the project
make -j$(nproc --ignore=1)

# Install the library
sudo make install

# Confirm the installation
echo "LibSBMLSim installed successfully!"
simulateSBML --version