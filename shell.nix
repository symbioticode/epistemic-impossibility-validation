# shell.nix — Environnement reproductible pour EIP (NixOS 25.05)
{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  packages = with pkgs.python312Packages; [
    python
    pip
    pytorch        # Framework PyTorch CPU pré-compilé
    transformers
    matplotlib
    seaborn
    scipy
    pandas
    numpy
    pytest
  ];

  shellHook = ''
    echo "✅ Environnement EIP activé"
    echo "   Python    : $(python --version)"
    echo "   PyTorch   : $(python -c 'import torch; print(torch.__version__)' 2>/dev/null || echo 'non chargé')"
    echo "   Transformers: $(python -c 'import transformers; print(transformers.__version__)' 2>/dev/null || echo 'non chargé')"
  '';
}
