# This pulls in the Nix package repository (nixpkgs), which provides all the packages used later in the buildInputs section. It is essential for accessing Python, libraries, and other utilities.
let
  pkgs = import <nixpkgs> {}; 
in pkgs.mkShell {
# Here the Python versions and dependencies will be managed.
  buildInputs = [
    pkgs.python311Full  # Python 3.11 for this project
    pkgs.python311Packages.pip
    pkgs.python311Packages.fastapi    # FastAPI framework
    pkgs.python311Packages.uvicorn    # Uvicorn server to run app
    pkgs.python311Packages.numpy      # NumPy
    pkgs.python311Packages.pandas     # Pandas
    pkgs.python311Packages.matplotlib # For signal visualization
    pkgs.python311Packages.aiohttp    # For async tasks
    pkgs.pre-commit                   # To enable pre-commit hooks (see below)
    pkgs.python311Packages.black      # Code formatter
    pkgs.python311Packages.flake8     # Linter (use python311Packages)
    pkgs.python311Packages.isort      # Import sorter
    pkgs.python311Packages.pytest     # Testing framework
  ];

# Add environment variables # Enable pre-commit hooks with the Devenv pre-commit module (imported above)
  shellHook = ''
    echo "Welcome to the Biosignal Project Dev Environment!"
    echo "Python version: $(python3 --version)"
    echo "Run 'uvicorn app.main:app --reload' to start the server."
    pre-commit install # Enable pre-commit hooks with the Devenv pre-commit module (imported above). Hooks are defined in .pre-commit-config.yaml
  '';
}
