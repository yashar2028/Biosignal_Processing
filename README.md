## Project Overview
...

## Prerequisites
- Python 3.11
- 'devenv' for environment management

## Project Setup

#### 1. Clone the repository:
   ```bash
   git clone git@github.com:yashar2028/Biosignal_Processing.git
   cd Biosignal_Processing
   ```
   
#### 2. This project uses Nix for managing your project environment. Follow this command to install: (skip if Nix is already installed)
   ```bash
   sh <(curl -L https://nixos.org/nix/install)
   ```
   Install devenv from Nix packages (if not installed):
   ```bash
   nix-env -iA nixpkgs.devenv
   ```

#### 3. Make the bash script executable and run the script:
   ```bash
   chmod +x setup.sh
   ./scripts/setup.sh
   ```

#### 4. Run the database and then start the server:
   ```bash
   ./scripts/start_db.sh
   poetry run uvicorn main:app --reload
   ```
