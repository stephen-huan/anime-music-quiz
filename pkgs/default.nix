{ pkgs }:

{
  python3Packages = pkgs.python3Packages.overrideScope (final: prev: {
    audio2numpy = final.callPackage ./audio2numpy { };
  });
}
