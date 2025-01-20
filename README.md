## Project Overview
This is an independant application that requires only a Bitalino sensor set to capture, display and analyze the EEG signal acquired from a subject. This application is also developed as the project for Innovation and Complexity Management and Media Management courses. Analysis code and hardware connection code can be found in the analysis notebook as well. Note that the analysis code is not as same as the one used in the application (for example pandas library is not included in the application).
## Prerequisites
- Python 3.11
- 'devenv' for environment management

Below is the set up and running for users. Make sure that you include the .env file. The environment variables are added in repository settings at codespace secrets but the security restrictions regardingthe email API Key which is used for OTP verification still remains and codespace does not read the key. The recommendation is to run the app as dev set up or using docker in a local environment where .envshould be included. Database dump is also included in the compose file so static data is served on the graph.
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

#### 3. Run the setup script to enter developement environment:
   ```bash
   ./scripts/setup.sh
   ```

#### 4. Run the database and then start the server:
   ```bash
   ./scripts/start_db.sh
   poetry run uvicorn main:app --reload
   ```
## Run the app (Users)
   ```bash
   docker-compose up --build
   ```
## Contributers
Backend Developement: [Yashar Najafi](https://github.com/yashar2028)

Signal Processing and Hardware Connection: [Sina Najafi](https://github.com/SinaNajafi1)

Sensor Hardware and Hardware Connection: [Sepehr Hajimokhtar](https://github.com/sepehrmokhtar)

Frontend Developement: [Parnian Taji](https://github.com/ParnianTaji)
##
<img src="https://github.com/user-attachments/assets/4d358e72-d39e-4db6-999c-21cf98acf878" alt="syps 300dpi-01" width="100">
