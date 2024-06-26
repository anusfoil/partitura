#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module defines a function "show" that creates a rendering of one
or more parts or partgroups and opens it using the desktop default
application.
"""

import platform
import warnings
import os
import subprocess
import shutil
from tempfile import NamedTemporaryFile, TemporaryFile
from typing import Optional

from partitura import save_musicxml
from partitura.io.musescore import render_musescore
from partitura.score import ScoreLike

from partitura.utils.misc import PathLike, deprecated_alias


__all__ = ["render"]

# def ly_install_msg():
#     """Issue a platform specific installation suggestion for lilypond

#     """
#     if platform.system() == 'Linux':
#         s = ('Is lilypond installed? On debian based '
#              'installations you can install it using the '
#              'command "sudo apt install lilypond"')
#     elif platform.system() == 'Darwin':
#         s = ('Is lilypond installed? Lilypond can be '
#              'installed using brew ( https://brew.sh/ ) '
#              'using the command "brew cask install lilypond"')
#     elif platform.system() == 'Windows':
#         s = ('Is lilypond installed? It can be downloaded from '
#              'http://lilypond.org/')
#     return s


@deprecated_alias(out_fn="out", part="score_data")
def render(
    score_data: ScoreLike,
    fmt: str = "png",
    dpi: int = 90,
    out: Optional[PathLike] = None,
) -> None:
    """Create a rendering of one or more parts or partgroups.

    The function can save the rendered image to a file (when
    `out_fn` is specified), or shown in the default image viewer
    application.

    Rendering is first attempted through musecore, and if that
    fails through lilypond. If that also fails the function returns
    without raising an exception.

    Parameters
    ----------
    score_data : ScoreLike
        The score content to be displayed
    fmt : {'png', 'pdf'}, optional
        The image format of the rendered material
    out_fn : str or None, optional
        The path of the image output file. If None, the rendering will
        be displayed in a viewer.
    """

    img_fn = render_musescore(score_data, fmt, out, dpi)

    if img_fn is None or not os.path.exists(img_fn):
        img_fn = render_lilypond(score_data, fmt)
        if img_fn is None or not os.path.exists(img_fn):
            return

    if not out:
        # NOTE: the temporary image file will not be deleted.
        if platform.system() == "Linux":
            subprocess.call(["xdg-open", img_fn])
        elif platform.system() == "Darwin":
            subprocess.call(["open", img_fn])
        elif platform.system() == "Windows":
            os.startfile(img_fn)


@deprecated_alias(part="score_data")
def render_lilypond(
    score_data,
    fmt="png",
    out=None,
) -> Optional[PathLike]:
    """
    Render a score-like object using Lilypond

    Parameters
    ----------
    score_data : ScoreLike
        Score-like object to be rendered
    fmt : {'png', 'pdf'}
        Output image format
    out : str or None, optional
        The path of the image output file, if not specified, the
        rendering will be saved to a temporary filename. Defaults to
        None.

    Returns
    -------
    out : PathLike
        Path of the generated output image (or None if no image was generated).
    """
    if fmt not in ("png", "pdf"):
        warnings.warn("warning: unsupported output format")
        return None

    prvw_sfx = ".preview.{}".format(fmt)

    with TemporaryFile() as xml_fh, NamedTemporaryFile(
        suffix=prvw_sfx, delete=False
    ) as img_fh:

        # save part to musicxml in file handle xml_fh
        save_musicxml(score_data, xml_fh)
        # rewind read pointer of file handle before we pass it to musicxml2ly
        xml_fh.seek(0)

        img_stem = img_fh.name[: -len(prvw_sfx)]

        # convert musicxml to lilypond format (use stdout pipe)
        cmd1 = ["musicxml2ly", "-o-", "-"]
        try:
            ps1 = subprocess.run(
                cmd1, stdin=xml_fh, stdout=subprocess.PIPE, check=False
            )
            if ps1.returncode != 0:
                warnings.warn(
                    "Command {} failed with code {}".format(cmd1, ps1.returncode),
                    stacklevel=2,
                )
                return None
        except FileNotFoundError as f:
            warnings.warn(
                'Executing "{}" returned  {}.'.format(" ".join(cmd1), f),
                ImportWarning,
                stacklevel=2,
            )
            return None

        # convert lilypond format (read from pipe of ps1) to image, and save to
        # temporary filename
        cmd2 = [
            "lilypond",
            "--{}".format(fmt),
            "-dno-print-pages",
            "-dpreview",
            "-o{}".format(img_stem),
            "-",
        ]
        try:
            ps2 = subprocess.run(cmd2, input=ps1.stdout, check=False)
            if ps2.returncode != 0:
                warnings.warn(
                    "Command {} failed with code {}".format(cmd2, ps2.returncode),
                    stacklevel=2,
                )
                return None
        except FileNotFoundError as f:
            warnings.warn(
                'Executing "{}" returned {}.'.format(" ".join(cmd2), f),
                ImportWarning,
                stacklevel=2,
            )
            return

        if out is not None:
            shutil.copy(img_fh.name, out)
        else:
            out = img_fh.name

        return out
