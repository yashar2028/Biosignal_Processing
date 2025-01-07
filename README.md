## Project Overview
This is an independant application that requires only a Bitalino sensor set to capture, display and analyze the EEG signal acquired from a subject. This application is also developed as the project for Innovation and Complexity Management and Media Management courses.

## Prerequisites
- Python 3.11
- 'devenv' for environment management

## Project Setup (Devs)

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

#### 3. Make the bash scripts executable and run the setup script to enter developement environment:
   ```bash
   chmod +x start_db.sh
   chmod +x setup.sh
   ./scripts/setup.sh
   ```

#### 4. Run the database and then start the server:
   ```bash
   ./scripts/start_db.sh
   poetry run uvicorn main:app --reload
   ```
## Run the app (Users)
