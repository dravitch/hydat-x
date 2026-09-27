{
  description = "HYDAT-X — Independent Flood Prediction Benchmark (reproducible Nix devShell)";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";

  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
    in
    {
      devShells = forAllSystems (system:
        let
          pkgs = import nixpkgs { inherit system; };
        in
        {
          default = pkgs.mkShell {
            name = "hydat-x-dev";
            nativeBuildInputs = with pkgs; [ git ];
            buildInputs = with pkgs; [
              # Outillage système (exigences mission HYDAT-X)
              git
              curl
              wget
              unzip
              jq
              sqlite
              duckdb
              python312
              uv
              coreutils
              gawk
              findutils
              gzip
              xz
              zstd
              # Lecture de la documentation ECCC (PDF) — audit des flags/sémantique
              poppler_utils
              # Bibliothèques natives requises par les wheels (numpy/pandas/…)
              stdenv.cc.cc.lib
              zlib
            ];

            shellHook = ''
              export PATH="$HOME/.local/bin:$PATH"
              # Wheels PyPI (numpy 2.x, pandas, pyarrow) exigent libstdc++.so.6
              export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath [ pkgs.stdenv.cc.cc.lib pkgs.zlib ]}"
              if [ -d ".venv" ] && [ -x ".venv/bin/python" ]; then
                export VIRTUAL_ENV="$(pwd)/.venv"
                export PATH="$VIRTUAL_ENV/bin:$PATH"
              fi
              echo "HYDAT-X devShell ('nix develop') prêt — python: $(command -v python || echo nix-python) ; soup: $(command -v soup || echo non-installé)"
            '';
          };
        });
    };
}