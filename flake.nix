{
  description = "unspsc-cards build toolchain (Poetry for Python deps, Nix for system tools)";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          packages = [
            pkgs.python311
            pkgs.poetry
            pkgs.just
            pkgs.pagefind
          ];
          # Keep Poetry's virtualenv inside the project so CI can cache it.
          POETRY_VIRTUALENVS_IN_PROJECT = "true";
          # numpy/pandas manylinux wheels link against libstdc++ (and zlib) at runtime,
          # which a pure Nix shell doesn't expose by default.
          shellHook = ''
            export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath [ pkgs.stdenv.cc.cc.lib pkgs.zlib ]}''${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
          '';
        };
      }
    );
}
