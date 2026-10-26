{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs?ref=nixos-unstable";
    nixlib.url = "github:nix-util/nixlib";

    opencode-sandbox.url = "github:OpencodeSandbox/opencode-sandbox?ref=feat/opencodev2";
    opencode-sandbox.inputs.nixpkgs.follows = "nixpkgs";
    opencode-sandbox.inputs.nixlib.follows = "nixlib";
  };

  outputs = {nixlib, ...} @ inputs:
    nixlib.flake inputs ({self, ...}: {
      systems = ["x86_64-linux"];

      nixosModules = {
        sandbox-config = {...}: {
          opencode-sandbox = {
            git.remote.url = "https://github.com/Trantorian1/learn-ai-coding-starter.git";
            git.shutdown.pushOnExit = false;
            git.withLocalChanges = true;

            # env.extend = [self'.packages.devenv];
            opencode.config.mountHomeConfig = true;
            forwardPorts = [8888];
          };

          programs.nix-ld.enable = true;

          system.stateVersion = "26.11";
        };
      };

      perSystem = {
        self',
        opencode-sandbox',
        pkgs,
        libpkgs,
        libmodules,
        ...
      }: {
        formatter = pkgs.alejandra;

        packages = rec {
          sandbox = libmodules.build {
            name = "opencode-sandbox.sandbox.package";

            modules = [
              opencode-sandbox'.nixosModules.microvm
              opencode-sandbox'.nixosModules.sandbox
              self.nixosModules.sandbox-config
            ];
          };

          devenv = libpkgs.mkEnv {
            packages = with pkgs; [
              go
              bootdev-cli
              uv
              python313
            ];
          };

          default = sandbox;
        };

        devShells = {
          default = pkgs.mkShell {
            packages = [self'.packages.devenv];
          };
        };
      };
    });
}
