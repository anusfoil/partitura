#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tools for music analysis.

"""

from .voice_separation import estimate_voices
from .key_identification import estimate_key
from .pitch_spelling import estimate_spelling
from .tonal_tension import estimate_tonaltension
from .note_features import make_note_feats
from .performance_codec import encode_performance, decode_performance


__all__ = [
    "estimate_voices",
    "estimate_key",
    "estimate_spelling",
    "estimate_tonaltension",
]
