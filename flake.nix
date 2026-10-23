{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs?ref=nixos-unstable";
    nixlib.url = "github:nix-util/nixlib";

    opencode-sandbox.url = "github:OpencodeSandbox/opencode-sandbox?ref=feat/opencodev2";
    opencode-sandbox.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = {nixlib, ...} @ inputs: let
    systems = ["x86_64-linux"];
    util = nixlib.util {inherit systems inputs;};
  in {
    formatter = util.forEachSystem ({pkgs, ...}: pkgs.alejandra);

    nixosModules = util.forEachModule {
      sandbox-config = {self, ...}: {
        opencode-sandbox = {
          git.remote.url = "https://github.com/Trantorian1/learn-ai-coding-starter.git";
          git.shutdown.pushOnExit = false;
          git.withLocalChanges = true;

          forwardPorts = [8888];
          env.extend = [self.packages.devenv];
        };

        programs.nix-ld.enable = true;

        system.stateVersion = "26.11";
      };
    };

    packages = util.forEachSystem ({
      self,
      opencode-sandbox,
      pkgs,
      libpkgs,
      libmodules,
      ...
    }: rec {
      sandbox = libmodules.build {
        name = "opencode-sandbox.sandbox.package";

        modules = [
          opencode-sandbox.nixosModules.sandbox
          opencode-sandbox.nixosModules.microvm
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
    });

    devShells = util.forEachSystem ({
      self,
      pkgs,
      ...
    }: {
      default = pkgs.mkShell {
        packages = [self.packages.devenv];
      };
    });
  };
}
