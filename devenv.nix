# This pulls in the Nix package repository (nixpkgs), which provides all the packages used later in the buildInputs section. It is essential for accessing Python, libraries, and other utilities.
let
  pkgs = import <nixpkgs> {}; 
in pkgs.mkShell {
# Here the Python versions and dependencies will be managed.
  buildInputs = [
    pkgs.python311Full  # Python 3.11 for this project
    pkgs.python311Packages.pip
    pkgs.pre-commit     # To enable pre-commit hooks (see below)
    pkgs.poetry         # Poetry for dependency management
    pkgs.stdenv.cc.cc.lib   # Include libstdc++
  ];

# Add environment variables and enable pre-commit hooks with the Devenv pre-commit module (imported above).
  shellHook = ''
    export LD_LIBRARY_PATH=/nix/store/40yjzm7r5ki59kkk9423dnwbm86x7pyd-gcc-13.2.0-lib/lib:$LD_LIBRARY_PATH # Exposing the path of libstdc++ to the environment.
    echo "Welcome to the Biosignal Project Dev Environment!"
    echo "Python version: $(python3 --version)"
    echo "Run 'uvicorn app.main:app --reload' to start the server."
    pre-commit install # Enable pre-commit hooks with the Devenv pre-commit module (imported above). Hooks are defined in .pre-commit-config.yaml.
    poetry install --no-root  # Install dependencies defined in pyproject.toml (root of the project).
  '';
}
