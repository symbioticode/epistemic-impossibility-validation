"""
channels.py — Point d'entrée unique pour les classes de canaux EIP.
Délègue vers channels_standalone.py (implémentation sans HuggingFace Hub).
Ce fichier remplace la version conflictuelle issue du merge Git.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from channels_standalone import TextChannel, LatentChannel, CLAIMChannel, CLAIM

__all__ = ["TextChannel", "LatentChannel", "CLAIMChannel", "CLAIM"]
