{
  description = "Development environment for Python and Go";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
      in
      {
        devShell = pkgs.mkShell {
          buildInputs = [
            pkgs.python3
            pkgs.python3Packages.pip
            pkgs.python3Packages.virtualenv
            pkgs.go
            pkgs.python312Packages.numpy
            pkgs.stdenv.cc.cc.lib
            pkgs.playwright
            pkgs.playwright-driver.browsers
          ];

          shellHook = ''
            echo "Welcome to the Python and Go development environment!"
            # Create a virtual environment if it doesn't exist
            if [ ! -d ".venv" ]; then
              python -m venv .venv
            fi
            # Activate the virtual environment
            source .venv/bin/activate
            # Install Python dependencies
            pip install -r requirements.txt

            # Set environment variables for lib 
            export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib"
            export PLAYWRIGHT_BROWSERS_PATH=${pkgs.playwright-driver.browsers}
            export PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=true
          '';
        };
      });
}
