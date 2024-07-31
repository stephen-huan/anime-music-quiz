{
  description = "Computer plays AMQ";

  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";

  outputs = { nixpkgs, ... }:
    let
      inherit (nixpkgs) lib;
      systems = lib.systems.flakeExposed;
      eachDefaultSystem = f: builtins.foldl' lib.attrsets.recursiveUpdate { }
        (map f systems);
    in
    eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pkgs' = import ./pkgs { inherit pkgs; };
        python3' = pkgs'.python3Packages.python.override {
          packageOverrides = final: prev: pkgs'.python3Packages;
          self = python3';
        };
        python' = python3'.withPackages (ps: with ps; [
          audio2numpy
          numpy
          pydub
          scipy
          selenium
          sounddevice
        ]);
        formatters = [ pkgs.black pkgs.isort pkgs.nixpkgs-fmt ];
        linters = [ pkgs.pyright pkgs.ruff pkgs.statix ];
      in
      {
        formatter.${system} = pkgs.writeShellApplication {
          name = "formatter";
          runtimeInputs = formatters;
          text = ''
            isort "$@"
            black "$@"
            nixpkgs-fmt "$@"
          '';
        };

        checks.${system}.lint = pkgs.stdenvNoCC.mkDerivation {
          name = "lint";
          src = ./.;
          doCheck = true;
          nativeCheckInputs = formatters ++ linters ++ lib.singleton python';
          checkPhase = ''
            isort --check --diff .
            black --check --diff .
            nixpkgs-fmt --check .
            ruff check .
            pyright .
            statix check
          '';
          installPhase = "touch $out";
        };

        devShells.${system}.default = pkgs.mkShell {
          packages = [
            python'
          ]
          ++ formatters
          ++ linters;
        };
      }
    );
}
