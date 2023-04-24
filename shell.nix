{ pkgs ? import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/fd901ef4bf93499374c5af385b2943f5801c0833.tar.gz") {}
}:
pkgs.mkShell {
    name="AIDA website";
    buildInputs = [
        pkgs.just
        pkgs.ed
    ];
    shellHook = ''
        echo "Initialized development environment.."
    '';
}
