{ pkgs ? import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/2362848adf8def2866fabbffc50462e929d7fffb.tar.gz") {}
}:
pkgs.mkShell {
    name="AIDA website";
    buildInputs = [
        pkgs.just
        pkgs.nushell
    ];
    shellHook = ''
        echo "Initialized development environment.."
    '';
}
