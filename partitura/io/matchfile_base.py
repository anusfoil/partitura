#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains base classes for Match lines and utilities for
parsing and formatting match lines.
"""
from __future__ import annotations

from typing import Callable, Tuple, Any, Optional, Union, Dict, List, Iterable
import re

import numpy as np

from partitura.utils.music import (
    pitch_spelling_to_midi_pitch,
    ensure_pitch_spelling_format,
    ALTER_SIGNS,
)

from partitura.io.matchfile_utils import (
    Version,
    interpret_version,
    interpret_version,
    format_version,
    interpret_as_string,
    format_string,
    interpret_as_float,
    format_float,
    format_float_unconstrained,
    interpret_as_int,
    format_int,
    FractionalSymbolicDuration,
    format_fractional,
    interpret_as_fractional,
    interpret_as_list,
    format_list,
)


class MatchError(Exception):
    """
    Base exception for parsing match files.
    """

    pass


class MatchLine(object):
    """
    Base class for representing match lines.

    This class should be subclassed for the different match lines.

    Parameters
    ----------
    version : Version
        Indicate the version of the match line.

    Attributes
    ----------
    version: Version
        The version of the match line.
    field_names: Tuple[str]
        The names of the different fields with information in the match line.
    field_types : Tuple[type]
        The data type of the different fields.
    out_pattern : str
        The output pattern for the match line (i.e., how the match line looks like
        in a match file).
    pattern : re.Pattern
        Regular expression to parse information from a string.
    format_fun: Dict[str, Callable]
        A dictionary of methods for formatting the values of each field name.
    """

    # Version of the match line
    version: Version

    # Field names that appear in the match line
    # A match line will generally have these
    # field names as attributes.
    # Following the original Prolog-based specification
    # the names of the attributes start with upper-case letters
    field_names: Tuple[str]

    # type of the information in the fields
    field_types: Tuple[Union[type, Tuple[type]]]

    # Output pattern
    out_pattern: str

    # A dictionary of callables for each field name
    # the callables should get the value of the input
    # and return a string formatted for the matchfile.
    format_fun: Union[
        Dict[str, Callable[Any, str]],
        Tuple[Dict[str, Callable[Any, str]]],
    ]

    # Regular expression to parse
    # information from a string.
    pattern: Union[re.Pattern, Tuple[re.Pattern]]

    def __init__(self, version: Version) -> None:
        # Subclasses need to initialize the other
        # default field names
        self.version = version

    def __str__(self) -> str:
        """
        Prints the printing the match line
        """
        r = [self.__class__.__name__]
        for fn in self.field_names:
            r.append(" {0}: {1}".format(fn, self.__dict__[fn]))
        return "\n".join(r) + "\n"

    @property
    def matchline(self) -> str:
        """
        Generate matchline as a string.

        This method can be adapted as needed by subclasses.
        """
        matchline = self.out_pattern.format(
            **dict(
                [
                    (field, self.format_fun[field](getattr(self, field)))
                    for field in self.field_names
                ]
            )
        )

        return matchline

    @classmethod
    def from_matchline(
        cls,
        matchline: str,
        version: Version,
    ) -> MatchLine:
        """
        Create a new MatchLine object from a string

        Parameters
        ----------
        matchline : str
            String with a matchline
        version : Version
            Version of the matchline

        Returns
        -------
        a MatchLine instance
        """
        raise NotImplementedError  # pragma: no cover

    def check_types(self, verbose: bool = False) -> bool:
        """
        Check whether the values of the fields are of the correct type.

        Parameters
        ----------
        verbose : bool
            Prints whether each of the attributes in field_names has the correct dtype.
            values are

        Returns
        -------
        types_are_correct : bool
            True if the values of all fields in the match line have the
            correct type.
        """
        types_are_correct_list = [
            isinstance(getattr(self, field), field_type)
            for field, field_type in zip(self.field_names, self.field_types)
        ]
        if verbose:
            print(list(zip(self.field_names, types_are_correct_list)))

        types_are_correct = all(types_are_correct_list)
        return types_are_correct


## The following classes define match lines that appear in all matchfile versions
## These classes need to be subclassed in the corresponding module for each version.


class BaseInfoLine(MatchLine):
    """
    Base class specifying global information lines.

    These lines have the general structure "info(<Attribute>,<Value>)."
    Which attributes are valid depending on the version of the match line.

    Parameters
    ----------
    version : Version
        The version of the info line.
    kwargs : keyword arguments
        Keyword arguments specifying the type of line and its value.
    """

    # Base field names (can be updated in subclasses).
    # "attribute" will have type str, but the type of value needs to be specified
    # during initialization.
    field_names = ("Attribute", "Value")

    out_pattern = "info({Attribute},{Value})."

    pattern = re.compile(r"info\((?P<Attribute>[^,]+),(?P<Value>.+)\)\.")

    def __init__(
        self,
        version: Version,
        attribute: str,
        value: Any,
        value_type: type,
        format_fun: Callable[Any, str],
    ) -> None:
        super().__init__(version)

        self.field_types = (str, value_type)
        self.format_fun = dict(Attribute=format_string, Value=format_fun)
        self.Attribute = attribute
        self.Value = value


# deprecate bar for measure
class BaseSnoteLine(MatchLine):
    """
    Base class to represent score notes.

    Parameters
    ----------
    version: Version
    anchor: str
    note_name: str
    modifier: str
    octave: Optional[int]
    measure: int
    beat: int
    offset: FractionalSymbolicDuration
    duration: FractionalSymbolicDuration
    onset_in_beats: float
    offset_in_beats: float
    score_attributes_list: List[str]

    Attributes
    ----------
    DurationInBeats : float
    DurationSymbolic : float
    MidiPitch : float

    Notes
    -----
    * The snote line has not changed much since the first version of
      the Match file format. New versions are just more explicit in the
      the formatting of the attributes (field names), e.g., NoteName
      should always be uppercase starting from version 1.0.0, etc.
    """

    # All derived classes should include
    # at least these field names
    field_names = (
        "Anchor",
        "NoteName",
        "Modifier",
        "Octave",
        "Measure",
        "Beat",
        "Offset",
        "Duration",
        "OnsetInBeats",
        "OffsetInBeats",
        "ScoreAttributesList",
    )

    field_types = (
        str,
        str,
        (int, type(None)),
        (int, type(None)),
        int,
        int,
        FractionalSymbolicDuration,
        FractionalSymbolicDuration,
        float,
        float,
        list,
    )

    out_pattern = (
        "snote({Anchor},[{NoteName},{Modifier}],{Octave},"
        "{Measure}:{Beat},{Offset},{Duration},{OnsetInBeats},"
        "{OffsetInBeats},{ScoreAttributesList})"
    )

    pattern = re.compile(
        r"snote\("
        r"(?P<Anchor>[^,]+),"
        r"\[(?P<NoteName>[^,]+),(?P<Modifier>[^,]+)\],"
        r"(?P<Octave>[^,]+),"
        r"(?P<Measure>[^,]+):(?P<Beat>[^,]+),"
        r"(?P<Offset>[^,]+),"
        r"(?P<Duration>[^,]+),"
        r"(?P<OnsetInBeats>[^,]+),"
        r"(?P<OffsetInBeats>[^,]+),"
        r"\[(?P<ScoreAttributesList>.*)\]\)"
    )

    format_fun = dict(
        Anchor=format_string,
        NoteName=lambda x: str(x).upper(),
        Modifier=lambda x: "n" if x == 0 else ALTER_SIGNS[x],
        Octave=format_int,
        Measure=format_int,
        Beat=format_int,
        Offset=format_fractional,
        Duration=format_fractional,
        OnsetInBeats=format_float_unconstrained,
        OffsetInBeats=format_float_unconstrained,
        ScoreAttributesList=format_list,
    )

    def __init__(
        self,
        version: Version,
        anchor: str,
        note_name: str,
        modifier: str,
        octave: Optional[int],
        measure: int,
        beat: int,
        offset: FractionalSymbolicDuration,
        duration: FractionalSymbolicDuration,
        onset_in_beats: float,
        offset_in_beats: float,
        score_attributes_list: List[str],
    ) -> None:
        super().__init__(version)

        # All of these attributes should have the
        # correct dtype (otherwise we need to be constantly
        # checking the types).
        self.Anchor = anchor
        self.NoteName = note_name
        self.Modifier = modifier
        self.Octave = octave
        self.Measure = measure
        self.Beat = beat
        self.Offset = offset
        self.Duration = duration
        self.OnsetInBeats = onset_in_beats
        self.OffsetInBeats = offset_in_beats
        self.ScoreAttributesList = score_attributes_list

    @property
    def DurationInBeats(self) -> float:
        return self.OffsetInBeats - self.OnsetInBeats

    @property
    def DurationSymbolic(self) -> str:
        # Duration should always be a FractionalSymbolicDuration
        return str(self.Duration)

    @property
    def MidiPitch(self) -> Optional[int]:
        if isinstance(self.Octave, int):
            return pitch_spelling_to_midi_pitch(
                step=self.NoteName, octave=self.Octave, alter=self.Modifier
            )
        else:
            return None

    @classmethod
    def prepare_kwargs_from_matchline(
        cls,
        matchline: str,
        pos: int = 0,
    ) -> Dict:

        match_pattern = cls.pattern.search(matchline, pos)

        if match_pattern is not None:

            (
                anchor_str,
                note_name_str,
                modifier_str,
                octave_str,
                measure_str,
                beat_str,
                offset_str,
                duration_str,
                onset_in_beats_str,
                offset_in_beats_str,
                score_attributes_list_str,
            ) = match_pattern.groups()

            anchor = interpret_as_string(anchor_str)
            note_name, modifier, octave = ensure_pitch_spelling_format(
                step=note_name_str,
                alter=modifier_str,
                octave=octave_str,
            )

            return dict(
                anchor=interpret_as_string(anchor),
                note_name=note_name,
                modifier=modifier,
                octave=octave,
                measure=interpret_as_int(measure_str),
                beat=interpret_as_int(beat_str),
                offset=interpret_as_fractional(offset_str),
                duration=interpret_as_fractional(duration_str),
                onset_in_beats=interpret_as_float(onset_in_beats_str),
                offset_in_beats=interpret_as_float(offset_in_beats_str),
                score_attributes_list=interpret_as_list(score_attributes_list_str),
            )

        else:
            raise MatchError("Input match line does not fit the expected pattern.")


class BaseNoteLine(MatchLine):

    # All derived classes should include at least
    # these field names
    field_names = (
        "Id",
        "Onset",
        "Offset",
        "Velocity",
    )

    field_types = (
        str,
        int,
        float,
        float,
        int,
    )

    def __init__(
        self,
        version: Version,
        id: str,
        midi_pitch: int,
        onset: float,
        offset: float,
        velocity: int,
    ) -> None:
        super().__init__(version)
        self.Id = id
        # The MIDI pitch is not a part of all
        # note versions. For versions < 1.0.0
        # it needs to be inferred from pitch spelling.
        self.MidiPitch = midi_pitch
        self.Onset = onset
        self.Offset = offset
        self.Velocity = velocity

    @property
    def Duration(self):
        return self.Offset - self.Onset


class BaseSnoteNoteLine(MatchLine):

    out_pattern = "{SnoteLine}-{NoteLine}"

    def __init__(
        self,
        version: Version,
        snote: BaseSnoteLine,
        note: BaseNoteLine,
    ) -> None:

        super().__init__(version)

        self.snote = snote
        self.note = note

        self.field_names = self.snote.field_names + self.note.field_names

        self.field_types = self.snote.field_types + self.note.field_types

        self.pattern = (self.snote.pattern, self.note.pattern)
        # self.pattern = re.compile(f"{self.snote.pattern.pattern}-{self.note.pattern.pattern}")

        self.format_fun = (self.snote.format_fun, self.note.format_fun)

    @property
    def matchline(self) -> str:
        return self.out_pattern.format(
            SnoteLine=self.snote.matchline,
            NoteLine=self.note.matchline,
        )

    def __str__(self) -> str:

        """
        Prints the printing the match line
        """
        r = [self.__class__.__name__]
        r += [" Snote"] + [
            "   {0}: {1}".format(fn, getattr(self.snote, fn, None))
            for fn in self.snote.field_names
        ]

        r += [" Note"] + [
            "   {0}: {1}".format(fn, getattr(self.note, fn, None))
            for fn in self.note.field_names
        ]

        return "\n".join(r) + "\n"

    def check_types(self, verbose: bool = False) -> bool:
        """
        Check whether the values of the fields are of the correct type.

        Parameters
        ----------
        verbose : bool
            Prints whether each of the attributes in field_names has the correct dtype.
            values are

        Returns
        -------
        types_are_correct : bool
            True if the values of all fields in the match line have the
            correct type.
        """
        snote_types_are_correct = self.snote.check_types(verbose)
        note_types_are_correct = self.note.check_types(verbose)

        types_are_correct = snote_types_are_correct and note_types_are_correct

        return types_are_correct

    @classmethod
    def prepare_kwargs_from_matchline(
        cls,
        matchline: str,
        snote_class: BaseSnoteLine,
        note_class: BaseNoteLine,
        version: Version,
    ) -> Dict:
        snote = snote_class.from_matchline(matchline, version=version)
        note = note_class.from_matchline(matchline, version=version)

        kwargs = dict(
            version=version,
            snote=snote,
            note=note,
        )

        return kwargs


class BaseDeletionLine(MatchLine):

    out_pattern = "{SnoteLine}-deletion."

    def __init__(self, version: Version, snote: BaseSnoteLine) -> None:

        super().__init__(version)

        self.snote = snote

        self.field_names = self.snote.field_names

        self.field_types = self.snote.field_types

        self.pattern = re.compile(rf"{self.snote.pattern.pattern}-deletion\.")

        self.format_fun = self.snote.format_fun

        for fn in self.field_names:
            setattr(self, fn, getattr(self.snote, fn))

    @property
    def matchline(self) -> str:
        return self.out_pattern.format(
            SnoteLine=self.snote.matchline,
        )

    @classmethod
    def prepare_kwargs_from_matchline(
        cls,
        matchline: str,
        snote_class: BaseSnoteLine,
        version: Version,
    ) -> Dict:

        snote = snote_class.from_matchline(matchline, version=version)

        kwargs = dict(
            version=version,
            snote=snote,
        )

        return kwargs


class BaseInsertionLine(MatchLine):

    out_pattern = "insertion-{NoteLine}"

    def __init__(self, version: Version, note: BaseNoteLine) -> None:

        super().__init__(version)

        self.note = note

        self.field_names = self.note.field_names

        self.field_types = self.note.field_types

        self.pattern = re.compile(f"insertion-{self.note.pattern.pattern}")

        self.format_fun = self.note.format_fun

        for fn in self.field_names:
            setattr(self, fn, getattr(self.note, fn))

    @property
    def matchline(self) -> str:
        return self.out_pattern.format(
            NoteLine=self.note.matchline,
        )

    @classmethod
    def prepare_kwargs_from_matchline(
        cls,
        matchline: str,
        note_class: BaseNoteLine,
        version: Version,
    ) -> Dict:

        note = note_class.from_matchline(matchline, version=version)

        kwargs = dict(
            version=version,
            note=note,
        )

        return kwargs


## MatchFile

# classes that contain score notes
snote_classes = (BaseSnoteLine, BaseSnoteNoteLine, BaseDeletionLine)

# classes that contain performed notes.
note_classes = (BaseNoteLine, BaseSnoteNoteLine, BaseInsertionLine)


class MatchFile(object):
    """
    Class for representing MatchFiles
    """

    version: Version
    lines: np.ndarray

    def __init__(self, lines: Iterable[MatchLine]) -> None:

        # check that all lines have the same version
        same_version = all([line.version == lines[0].version for line in lines])

        if not same_version:
            raise ValueError("All lines should have the same version")

        self.lines = np.array(lines)

    @property
    def note_pairs(self):
        """
        Return all(snote, note) tuples

        """
        return [
            (x.snote, x.note) for x in self.lines if isinstance(x, BaseSnoteNoteLine)
        ]

    @property
    def notes(self):
        """
        Return all performed notes (as MatchNote objects)
        """
        return [x.note for x in self.lines if isinstance(x, note_classes)]

    def iter_notes(self):
        """
        Iterate over all performed notes (as MatchNote objects)
        """
        for x in self.lines:
            if isinstance(x, note_classes):
                # if hasattr(x, "note"):
                yield x.note

    @property
    def snotes(self):
        """
        Return all score notes (as MatchSnote objects)
        """
        return [x.snote for x in self.lines if isinstance(x, snote_classes)]
        # return [x.snote for x in self.lines if hasattr(x, "snote")]

    def iter_snotes(self):
        """
        Iterate over all performed notes (as MatchNote objects)
        """
        for x in self.lines:
            if hasattr(x, "snote"):
                yield x.snote

    @property
    def sustain_pedal(self):
        return [line for line in self.lines if isinstance(line, MatchSustainPedal)]

    @property
    def insertions(self):
        return [x.note for x in self.lines if isinstance(x, MatchInsertionNote)]

    @property
    def deletions(self):
        return [x.snote for x in self.lines if isinstance(x, MatchSnoteDeletion)]

    @property
    def _info(self):
        """
        Return all InfoLine objects

        """
        return [i for i in self.lines if isinstance(i, BaseInfoLine)]

    def info(self, attribute=None):
        """
        Return the value of the MatchInfo object corresponding to
        attribute, or None if there is no such object

        : param attribute: the name of the attribute to return the value for

        """
        if attribute:
            try:
                idx = [i.Attribute for i in self._info].index(attribute)
                return self._info[idx].Value
            except ValueError:
                return None
        else:
            return self._info

    @property
    def first_onset(self):
        return min([n.OnsetInBeats for n in self.snotes])

    @property
    def first_bar(self):
        return min([n.Bar for n in self.snotes])

    @property
    def time_signatures(self):
        """
        A list of tuples(t, b, (n, d)), indicating a time signature of
        n over v, starting at t in bar b

        """
        tspat = re.compile("([0-9]+)/([0-9]*)")
        m = [(int(x[0]), int(x[1])) for x in tspat.findall(self.info("timeSignature"))]
        _timeSigs = []
        if len(m) > 0:

            _timeSigs.append((self.first_onset, self.first_bar, m[0]))
        for line in self.time_sig_lines:

            _timeSigs.append(
                (
                    float(line.TimeInBeats),
                    int(line.Bar),
                    [(int(x[0]), int(x[1])) for x in tspat.findall(line.Value)][0],
                )
            )
        _timeSigs = list(set(_timeSigs))
        _timeSigs.sort(key=lambda x: [x[0], x[1]])

        # ensure that all consecutive time signatures are different
        timeSigs = [_timeSigs[0]]

        for ts in _timeSigs:
            ts_on, bar, (ts_num, ts_den) = ts
            ts_on_prev, ts_bar_prev, (ts_num_prev, ts_den_prev) = timeSigs[-1]
            if ts_num != ts_num_prev or ts_den != ts_den_prev:
                timeSigs.append(ts)

        return timeSigs

    def _time_sig_lines(self):
        return [
            i
            for i in self.lines
            if isinstance(i, MatchMeta)
            and hasattr(i, "Attribute")
            and i.Attribute == "timeSignature"
        ]

    @property
    def time_sig_lines(self):
        ml = self._time_sig_lines()
        if len(ml) == 0:
            ts = self.info("timeSignature")
            ml = [
                parse_matchline(
                    "meta(timeSignature,{0},{1},{2}).".format(
                        ts, self.first_bar, self.first_onset
                    )
                )
            ]
        return ml

    @property
    def key_signatures(self):
        """
        A list of tuples (t, b, (f,m)) or (t, b, (f1, m1, f2, m2))
        """
        kspat = re.compile(
            (
                "(?P<step1>[A-G])(?P<alter1>[#b]*) "
                "(?P<mode1>[a-zA-z]+)(?P<slash>/*)"
                "(?P<step2>[A-G]*)(?P<alter2>[#b]*)"
                "(?P<space2> *)(?P<mode2>[a-zA-z]*)"
            )
        )

        _keysigs = []
        for ksl in self.key_sig_lines:
            if isinstance(ksl, MatchInfo):
                # remove brackets and only take
                # the first key signature
                ks = ksl.Value.replace("[", "").replace("]", "").split(",")[0]
                t = self.first_onset
                b = self.first_bar
            elif isinstance(ksl, MatchMeta):
                ks = ksl.Value
                t = ksl.TimeInBeats
                b = ksl.Bar

            ks_info = kspat.search(ks)

            keysig = (
                self._format_key_signature(
                    step=ks_info.group("step1"),
                    alter_sign=ks_info.group("alter1"),
                    mode=ks_info.group("mode1"),
                ),
            )

            if ks_info.group("step2") != "":
                keysig += (
                    self._format_key_signature(
                        step=ks_info.group("step2"),
                        alter_sign=ks_info.group("alter2"),
                        mode=ks_info.group("mode2"),
                    ),
                )

            _keysigs.append((t, b, keysig))

        keysigs = []
        if len(_keysigs) > 0:
            keysigs.append(_keysigs[0])

            for k in _keysigs:
                if k[2] != keysigs[-1][2]:
                    keysigs.append(k)

        return keysigs

    def _format_key_signature(self, step, alter_sign, mode):

        if mode.lower() in ("maj", "", "major"):
            mode = ""
        elif mode.lower() in ("min", "m", "minor"):
            mode = "m"
        else:
            raise ValueError(
                'Invalid mode. Expected "major" or "minor" but got {0}'.format(mode)
            )

        return step + alter_sign + mode

    @property
    def key_sig_lines(self):

        ks_info = [line for line in self.info() if line.Attribute == "keySignature"]
        ml = ks_info + [
            i
            for i in self.lines
            if isinstance(i, MatchMeta)
            and hasattr(i, "Attribute")
            and i.Attribute == "keySignature"
        ]

        return ml

    def write(self, filename):
        with open(filename, "w") as f:
            for line in self.lines:
                f.write(line.matchline + "\n")

    @classmethod
    def from_lines(cls, lines, name=""):
        matchfile = cls(None)
        matchfile.lines = np.array(lines)
        matchfile.name = name
        return matchfile
