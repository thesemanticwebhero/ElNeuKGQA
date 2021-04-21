from .base_entitity_linking_system import BaseEntityLinkingSystem, EntityLinkingDict
from .dbpedia_spotlight_system import DBpediaSpotlight
from .open_tapioca_system import OpenTapioca
from .tagme_system import TagMe, TagMeWAT
from .aida_system import Aida
from .ensemble_entity_linking_system import (
    FullSystems
)
from .precision_priority_system import PrecisionPrioritySystem
from .voting_system import VotingSystem


__all__ = [
    'BaseEntityLinkingSystem',
    'DBpediaSpotlight',
    'OpenTapioca',
    'TagMe',
    'TagMeWAT',
    'Aida',
    'FullSystems',
    'PrecisionPrioritySystem',
    'VotingSystem',
    'EntityLinkingDict'
]