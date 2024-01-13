# shell.nix

{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    # Frontend dependencies
    pkgs.nodejs
    pkgs.yarn

    # Backend dependencies
    pkgs.python38Packages.virtualenv
  ];

  shellHook = ''
    # Enter frontend directory
    cd $PWD/frontend
    # Install frontend dependencies
    npm install

    # Enter backen directory
    cd $PWD/server
    # Create and activate Python virtual environment
    python -m venv venv
    . venv/Scripts/activate
    # Install backend dependencies
    pip install -r requirements.txt
  '';
}