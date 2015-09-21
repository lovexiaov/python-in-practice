#!/usr/bin/env python3
# Copyright © 2012-13 Qtrac Ltd. All rights reserved.
# This program or module is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version. It is provided for
# educational purposes and is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

import collections
import numpy
import os
import re


CLEAR_ALPHA = 0x00FFFFFF # & to ARGB color int to get rid of alpha channel
MAX_ARGB = 0xFFFFFFFF
MAX_COMPONENT = 0xFF
SOLID = 0xFF000000 # + to RGB color int to get a solid ARGB color int


class Error(Exception): pass


def sanitized_name(name):
    """returns a name suitable for XBM and XPM images"""
    name = re.sub(r"\W+", "", os.path.basename(os.path.splitext(name)[0]))
    if not name or name[0].isdigit():
        name = "z" + name
    return name


def create_array(width, height, background=None):
    """returns anumpy.array of the correct size and with the given
    background color"""
    if background is None:
        return numpy.zeros(width * height, dtype=numpy.uint32)
    iterable = (background for _ in range(width * height))
    return numpy.fromiter(iterable, numpy.uint32)


def argb_for_color(color):
    """returns an ARGB quadruple for a color specified as an int or
    a color name or an #HHH, #HHHH, #HHHHHH or #HHHHHHHH RGB
    str---in the latter case the alpha channel is set to 0xFF
    (solid) if not specified"""
    if isinstance(color, numpy.uint32):
        color = int(color)
    if isinstance(color, str):
        color = color_for_name(color)
    elif not isinstance(color, int) or not (0 <= color <= MAX_ARGB):
        raise Error("invalid color {}".format(color))
    a = (color >> 24) & MAX_COMPONENT
    r = (color >> 16) & MAX_COMPONENT
    g = (color >> 8) & MAX_COMPONENT
    b = (color & MAX_COMPONENT)
    return a, r, g, b


def rgb_for_color(color):
    """returns an RGB triple for a color specified as an int or
    a color name or an #HHH, #HHHH, #HHHHHH or #HHHHHHHH RGB
    str---in the latter case the alpha channel is set to 0xFF
    (solid) if not specified"""
    return argb_for_color(color)[1:]


def color_for_argb(a, r, g, b):
    """returns an int representing the given ARGB value"""
    if (0 <= a <= MAX_COMPONENT and 0 <= r <= MAX_COMPONENT and
        0 <= g <= MAX_COMPONENT and 0 <= b <= MAX_COMPONENT):
        color = 0
        color |= (((a & MAX_COMPONENT) << 24) |
                    ((r & MAX_COMPONENT) << 16) |
                    ((g & MAX_COMPONENT) << 8) | (b & MAX_COMPONENT))
        return color
    raise Error("invalid argb {}, {}, {}, {}".format(a, r, g, b))


def color_for_rgb(r, g, b):
    """returns an int representing the given RGB value; the alpha
    channel is set to 0xFF (solid)"""
    return color_for_argb(MAX_COMPONENT, r, g, b)


def color_for_name(name):
    """returns an ARGB int for a color specified as an int or
    a color name or an #HHH, #HHHH, #HHHHHH or #HHHHHHHH RGB
    str---in the latter case the alpha channel is set to 0xFF
    (solid) if not specified"""
    if name is None:
        return ColorForName["transparent"]  
    if name.startswith("#"):
        name = name[1:]
        if len(name) == 3: # add solid alpha
            name = "F" + name # now has 4 hex digits
        if len(name) == 6: # add solid alpha
            name = "FF" + name # now has the full 8 hex digits
        if len(name) == 4: # originally #FFF or #FFFF
            components = []
            for h in name:
                components.extend([h, h])
            name = "".join(components) # now has the full 8 hex digits
        return int(name, 16)
    return ColorForName[name.lower()]
    # ColorForName is a default dict so will always return a color,
    # e.g., black


# Taken from rgb.txt and converted to ARGB (with the addition of
# transparent). Default is solid black.
ColorForName = collections.defaultdict(lambda: 0xFF000000, {
    "transparent": 0x00000000, "aliceblue": 0xFFF0F8FF,
    "antiquewhite": 0xFFFAEBD7, "antiquewhite1": 0xFFFFEFDB,
    "antiquewhite2": 0xFFEEDFCC, "antiquewhite3": 0xFFCDC0B0,
    "antiquewhite4": 0xFF8B8378, "aquamarine": 0xFF7FFFD4,
    "aquamarine1": 0xFF7FFFD4, "aquamarine2": 0xFF76EEC6,
    "aquamarine3": 0xFF66CDAA, "aquamarine4": 0xFF458B74,
    "azure": 0xFFF0FFFF, "azure1": 0xFFF0FFFF, "azure2": 0xFFE0EEEE,
    "azure3": 0xFFC1CDCD, "azure4": 0xFF838B8B, "beige": 0xFFF5F5DC,
    "bisque": 0xFFFFE4C4, "bisque1": 0xFFFFE4C4, "bisque2": 0xFFEED5B7,
    "bisque3": 0xFFCDB79E, "bisque4": 0xFF8B7D6B, "black": 0xFF000000,
    "blanchedalmond": 0xFFFFEBCD, "blue": 0xFF0000FF, "blue1": 0xFF0000FF,
    "blue2": 0xFF0000EE, "blue3": 0xFF0000CD, "blue4": 0xFF00008B,
    "blueviolet": 0xFF8A2BE2, "brown": 0xFFA52A2A, "brown1": 0xFFFF4040,
    "brown2": 0xFFEE3B3B, "brown3": 0xFFCD3333, "brown4": 0xFF8B2323,
    "burlywood": 0xFFDEB887, "burlywood1": 0xFFFFD39B,
    "burlywood2": 0xFFEEC591, "burlywood3": 0xFFCDAA7D,
    "burlywood4": 0xFF8B7355, "cadetblue": 0xFF5F9EA0,
    "cadetblue1": 0xFF98F5FF, "cadetblue2": 0xFF8EE5EE,
    "cadetblue3": 0xFF7AC5CD, "cadetblue4": 0xFF53868B,
    "chartreuse": 0xFF7FFF00, "chartreuse1": 0xFF7FFF00,
    "chartreuse2": 0xFF76EE00, "chartreuse3": 0xFF66CD00,
    "chartreuse4": 0xFF458B00, "chocolate": 0xFFD2691E,
    "chocolate1": 0xFFFF7F24, "chocolate2": 0xFFEE7621,
    "chocolate3": 0xFFCD661D, "chocolate4": 0xFF8B4513, "coral": 0xFFFF7F50,
    "coral1": 0xFFFF7256, "coral2": 0xFFEE6A50, "coral3": 0xFFCD5B45,
    "coral4": 0xFF8B3E2F, "cornflowerblue": 0xFF6495ED,
    "cornsilk": 0xFFFFF8DC, "cornsilk1": 0xFFFFF8DC,
    "cornsilk2": 0xFFEEE8CD, "cornsilk3": 0xFFCDC8B1,
    "cornsilk4": 0xFF8B8878, "cyan": 0xFF00FFFF, "cyan1": 0xFF00FFFF,
    "cyan2": 0xFF00EEEE, "cyan3": 0xFF00CDCD, "cyan4": 0xFF008B8B,
    "darkblue": 0xFF00008B, "darkcyan": 0xFF008B8B,
    "darkgoldenrod": 0xFFB8860B, "darkgoldenrod1": 0xFFFFB90F,
    "darkgoldenrod2": 0xFFEEAD0E, "darkgoldenrod3": 0xFFCD950C,
    "darkgoldenrod4": 0xFF8B6508, "darkgray": 0xFFA9A9A9,
    "darkgreen": 0xFF006400, "darkgrey": 0xFFA9A9A9,
    "darkkhaki": 0xFFBDB76B, "darkmagenta": 0xFF8B008B,
    "darkolivegreen": 0xFF556B2F, "darkolivegreen1": 0xFFCAFF70,
    "darkolivegreen2": 0xFFBCEE68, "darkolivegreen3": 0xFFA2CD5A,
    "darkolivegreen4": 0xFF6E8B3D, "darkorange": 0xFFFF8C00,
    "darkorange1": 0xFFFF7F00, "darkorange2": 0xFFEE7600,
    "darkorange3": 0xFFCD6600, "darkorange4": 0xFF8B4500,
    "darkorchid": 0xFF9932CC, "darkorchid1": 0xFFBF3EFF,
    "darkorchid2": 0xFFB23AEE, "darkorchid3": 0xFF9A32CD,
    "darkorchid4": 0xFF68228B, "darkred": 0xFF8B0000,
    "darksalmon": 0xFFE9967A, "darkseagreen": 0xFF8FBC8F,
    "darkseagreen1": 0xFFC1FFC1, "darkseagreen2": 0xFFB4EEB4,
    "darkseagreen3": 0xFF9BCD9B, "darkseagreen4": 0xFF698B69,
    "darkslateblue": 0xFF483D8B, "darkslategray": 0xFF2F4F4F,
    "darkslategray1": 0xFF97FFFF, "darkslategray2": 0xFF8DEEEE,
    "darkslategray3": 0xFF79CDCD, "darkslategray4": 0xFF528B8B,
    "darkslategrey": 0xFF2F4F4F, "darkturquoise": 0xFF00CED1,
    "darkviolet": 0xFF9400D3, "debianred": 0xFFD70751,
    "deeppink": 0xFFFF1493, "deeppink1": 0xFFFF1493,
    "deeppink2": 0xFFEE1289, "deeppink3": 0xFFCD1076,
    "deeppink4": 0xFF8B0A50, "deepskyblue": 0xFF00BFFF,
    "deepskyblue1": 0xFF00BFFF, "deepskyblue2": 0xFF00B2EE,
    "deepskyblue3": 0xFF009ACD, "deepskyblue4": 0xFF00688B,
    "dimgray": 0xFF696969, "dimgrey": 0xFF696969, "dodgerblue": 0xFF1E90FF,
    "dodgerblue1": 0xFF1E90FF, "dodgerblue2": 0xFF1C86EE,
    "dodgerblue3": 0xFF1874CD, "dodgerblue4": 0xFF104E8B,
    "firebrick": 0xFFB22222, "firebrick1": 0xFFFF3030,
    "firebrick2": 0xFFEE2C2C, "firebrick3": 0xFFCD2626,
    "firebrick4": 0xFF8B1A1A, "floralwhite": 0xFFFFFAF0,
    "forestgreen": 0xFF228B22, "gainsboro": 0xFFDCDCDC,
    "ghostwhite": 0xFFF8F8FF, "gold": 0xFFFFD700, "gold1": 0xFFFFD700,
    "gold2": 0xFFEEC900, "gold3": 0xFFCDAD00, "gold4": 0xFF8B7500,
    "goldenrod": 0xFFDAA520, "goldenrod1": 0xFFFFC125,
    "goldenrod2": 0xFFEEB422, "goldenrod3": 0xFFCD9B1D,
    "goldenrod4": 0xFF8B6914, "gray0": 0xFF000000, "gray": 0xFFBEBEBE,
    "gray100": 0xFFFFFFFF, "gray10": 0xFF1A1A1A, "gray1": 0xFF030303,
    "gray11": 0xFF1C1C1C, "gray12": 0xFF1F1F1F, "gray13": 0xFF212121,
    "gray14": 0xFF242424, "gray15": 0xFF262626, "gray16": 0xFF292929,
    "gray17": 0xFF2B2B2B, "gray18": 0xFF2E2E2E, "gray19": 0xFF303030,
    "gray20": 0xFF333333, "gray2": 0xFF050505, "gray21": 0xFF363636,
    "gray22": 0xFF383838, "gray23": 0xFF3B3B3B, "gray24": 0xFF3D3D3D,
    "gray25": 0xFF404040, "gray26": 0xFF424242, "gray27": 0xFF454545,
    "gray28": 0xFF474747, "gray29": 0xFF4A4A4A, "gray30": 0xFF4D4D4D,
    "gray3": 0xFF080808, "gray31": 0xFF4F4F4F, "gray32": 0xFF525252,
    "gray33": 0xFF545454, "gray34": 0xFF575757, "gray35": 0xFF595959,
    "gray36": 0xFF5C5C5C, "gray37": 0xFF5E5E5E, "gray38": 0xFF616161,
    "gray39": 0xFF636363, "gray40": 0xFF666666, "gray4": 0xFF0A0A0A,
    "gray41": 0xFF696969, "gray42": 0xFF6B6B6B, "gray43": 0xFF6E6E6E,
    "gray44": 0xFF707070, "gray45": 0xFF737373, "gray46": 0xFF757575,
    "gray47": 0xFF787878, "gray48": 0xFF7A7A7A, "gray49": 0xFF7D7D7D,
    "gray50": 0xFF7F7F7F, "gray5": 0xFF0D0D0D, "gray51": 0xFF828282,
    "gray52": 0xFF858585, "gray53": 0xFF878787, "gray54": 0xFF8A8A8A,
    "gray55": 0xFF8C8C8C, "gray56": 0xFF8F8F8F, "gray57": 0xFF919191,
    "gray58": 0xFF949494, "gray59": 0xFF969696, "gray60": 0xFF999999,
    "gray6": 0xFF0F0F0F, "gray61": 0xFF9C9C9C, "gray62": 0xFF9E9E9E,
    "gray63": 0xFFA1A1A1, "gray64": 0xFFA3A3A3, "gray65": 0xFFA6A6A6,
    "gray66": 0xFFA8A8A8, "gray67": 0xFFABABAB, "gray68": 0xFFADADAD,
    "gray69": 0xFFB0B0B0, "gray70": 0xFFB3B3B3, "gray7": 0xFF121212,
    "gray71": 0xFFB5B5B5, "gray72": 0xFFB8B8B8, "gray73": 0xFFBABABA,
    "gray74": 0xFFBDBDBD, "gray75": 0xFFBFBFBF, "gray76": 0xFFC2C2C2,
    "gray77": 0xFFC4C4C4, "gray78": 0xFFC7C7C7, "gray79": 0xFFC9C9C9,
    "gray80": 0xFFCCCCCC, "gray8": 0xFF141414, "gray81": 0xFFCFCFCF,
    "gray82": 0xFFD1D1D1, "gray83": 0xFFD4D4D4, "gray84": 0xFFD6D6D6,
    "gray85": 0xFFD9D9D9, "gray86": 0xFFDBDBDB, "gray87": 0xFFDEDEDE,
    "gray88": 0xFFE0E0E0, "gray89": 0xFFE3E3E3, "gray90": 0xFFE5E5E5,
    "gray9": 0xFF171717, "gray91": 0xFFE8E8E8, "gray92": 0xFFEBEBEB,
    "gray93": 0xFFEDEDED, "gray94": 0xFFF0F0F0, "gray95": 0xFFF2F2F2,
    "gray96": 0xFFF5F5F5, "gray97": 0xFFF7F7F7, "gray98": 0xFFFAFAFA,
    "gray99": 0xFFFCFCFC, "green": 0xFF00FF00, "green1": 0xFF00FF00,
    "green2": 0xFF00EE00, "green3": 0xFF00CD00, "green4": 0xFF008B00,
    "greenyellow": 0xFFADFF2F, "grey0": 0xFF000000, "grey": 0xFFBEBEBE,
    "grey100": 0xFFFFFFFF, "grey10": 0xFF1A1A1A, "grey1": 0xFF030303,
    "grey11": 0xFF1C1C1C, "grey12": 0xFF1F1F1F, "grey13": 0xFF212121,
    "grey14": 0xFF242424, "grey15": 0xFF262626, "grey16": 0xFF292929,
    "grey17": 0xFF2B2B2B, "grey18": 0xFF2E2E2E, "grey19": 0xFF303030,
    "grey20": 0xFF333333, "grey2": 0xFF050505, "grey21": 0xFF363636,
    "grey22": 0xFF383838, "grey23": 0xFF3B3B3B, "grey24": 0xFF3D3D3D,
    "grey25": 0xFF404040, "grey26": 0xFF424242, "grey27": 0xFF454545,
    "grey28": 0xFF474747, "grey29": 0xFF4A4A4A, "grey30": 0xFF4D4D4D,
    "grey3": 0xFF080808, "grey31": 0xFF4F4F4F, "grey32": 0xFF525252,
    "grey33": 0xFF545454, "grey34": 0xFF575757, "grey35": 0xFF595959,
    "grey36": 0xFF5C5C5C, "grey37": 0xFF5E5E5E, "grey38": 0xFF616161,
    "grey39": 0xFF636363, "grey40": 0xFF666666, "grey4": 0xFF0A0A0A,
    "grey41": 0xFF696969, "grey42": 0xFF6B6B6B, "grey43": 0xFF6E6E6E,
    "grey44": 0xFF707070, "grey45": 0xFF737373, "grey46": 0xFF757575,
    "grey47": 0xFF787878, "grey48": 0xFF7A7A7A, "grey49": 0xFF7D7D7D,
    "grey50": 0xFF7F7F7F, "grey5": 0xFF0D0D0D, "grey51": 0xFF828282,
    "grey52": 0xFF858585, "grey53": 0xFF878787, "grey54": 0xFF8A8A8A,
    "grey55": 0xFF8C8C8C, "grey56": 0xFF8F8F8F, "grey57": 0xFF919191,
    "grey58": 0xFF949494, "grey59": 0xFF969696, "grey60": 0xFF999999,
    "grey6": 0xFF0F0F0F, "grey61": 0xFF9C9C9C, "grey62": 0xFF9E9E9E,
    "grey63": 0xFFA1A1A1, "grey64": 0xFFA3A3A3, "grey65": 0xFFA6A6A6,
    "grey66": 0xFFA8A8A8, "grey67": 0xFFABABAB, "grey68": 0xFFADADAD,
    "grey69": 0xFFB0B0B0, "grey70": 0xFFB3B3B3, "grey7": 0xFF121212,
    "grey71": 0xFFB5B5B5, "grey72": 0xFFB8B8B8, "grey73": 0xFFBABABA,
    "grey74": 0xFFBDBDBD, "grey75": 0xFFBFBFBF, "grey76": 0xFFC2C2C2,
    "grey77": 0xFFC4C4C4, "grey78": 0xFFC7C7C7, "grey79": 0xFFC9C9C9,
    "grey80": 0xFFCCCCCC, "grey8": 0xFF141414, "grey81": 0xFFCFCFCF,
    "grey82": 0xFFD1D1D1, "grey83": 0xFFD4D4D4, "grey84": 0xFFD6D6D6,
    "grey85": 0xFFD9D9D9, "grey86": 0xFFDBDBDB, "grey87": 0xFFDEDEDE,
    "grey88": 0xFFE0E0E0, "grey89": 0xFFE3E3E3, "grey90": 0xFFE5E5E5,
    "grey9": 0xFF171717, "grey91": 0xFFE8E8E8, "grey92": 0xFFEBEBEB,
    "grey93": 0xFFEDEDED, "grey94": 0xFFF0F0F0, "grey95": 0xFFF2F2F2,
    "grey96": 0xFFF5F5F5, "grey97": 0xFFF7F7F7, "grey98": 0xFFFAFAFA,
    "grey99": 0xFFFCFCFC, "honeydew": 0xFFF0FFF0, "honeydew1": 0xFFF0FFF0,
    "honeydew2": 0xFFE0EEE0, "honeydew3": 0xFFC1CDC1,
    "honeydew4": 0xFF838B83, "hotpink": 0xFFFF69B4, "hotpink1": 0xFFFF6EB4,
    "hotpink2": 0xFFEE6AA7, "hotpink3": 0xFFCD6090, "hotpink4": 0xFF8B3A62,
    "indianred": 0xFFCD5C5C, "indianred1": 0xFFFF6A6A,
    "indianred2": 0xFFEE6363, "indianred3": 0xFFCD5555,
    "indianred4": 0xFF8B3A3A, "ivory": 0xFFFFFFF0, "ivory1": 0xFFFFFFF0,
    "ivory2": 0xFFEEEEE0, "ivory3": 0xFFCDCDC1, "ivory4": 0xFF8B8B83,
    "khaki": 0xFFF0E68C, "khaki1": 0xFFFFF68F, "khaki2": 0xFFEEE685,
    "khaki3": 0xFFCDC673, "khaki4": 0xFF8B864E, "lavender": 0xFFE6E6FA,
    "lavenderblush": 0xFFFFF0F5, "lavenderblush1": 0xFFFFF0F5,
    "lavenderblush2": 0xFFEEE0E5, "lavenderblush3": 0xFFCDC1C5,
    "lavenderblush4": 0xFF8B8386, "lawngreen": 0xFF7CFC00,
    "lemonchiffon": 0xFFFFFACD, "lemonchiffon1": 0xFFFFFACD,
    "lemonchiffon2": 0xFFEEE9BF, "lemonchiffon3": 0xFFCDC9A5,
    "lemonchiffon4": 0xFF8B8970, "lightblue": 0xFFADD8E6,
    "lightblue1": 0xFFBFEFFF, "lightblue2": 0xFFB2DFEE,
    "lightblue3": 0xFF9AC0CD, "lightblue4": 0xFF68838B,
    "lightcoral": 0xFFF08080, "lightcyan": 0xFFE0FFFF,
    "lightcyan1": 0xFFE0FFFF, "lightcyan2": 0xFFD1EEEE,
    "lightcyan3": 0xFFB4CDCD, "lightcyan4": 0xFF7A8B8B,
    "lightgoldenrod": 0xFFEEDD82, "lightgoldenrod1": 0xFFFFEC8B,
    "lightgoldenrod2": 0xFFEEDC82, "lightgoldenrod3": 0xFFCDBE70,
    "lightgoldenrod4": 0xFF8B814C, "lightgoldenrodyellow": 0xFFFAFAD2,
    "lightgray": 0xFFD3D3D3, "lightgreen": 0xFF90EE90,
    "lightgrey": 0xFFD3D3D3, "lightpink": 0xFFFFB6C1,
    "lightpink1": 0xFFFFAEB9, "lightpink2": 0xFFEEA2AD,
    "lightpink3": 0xFFCD8C95, "lightpink4": 0xFF8B5F65,
    "lightsalmon": 0xFFFFA07A, "lightsalmon1": 0xFFFFA07A,
    "lightsalmon2": 0xFFEE9572, "lightsalmon3": 0xFFCD8162,
    "lightsalmon4": 0xFF8B5742, "lightseagreen": 0xFF20B2AA,
    "lightskyblue": 0xFF87CEFA, "lightskyblue1": 0xFFB0E2FF,
    "lightskyblue2": 0xFFA4D3EE, "lightskyblue3": 0xFF8DB6CD,
    "lightskyblue4": 0xFF607B8B, "lightslateblue": 0xFF8470FF,
    "lightslategray": 0xFF778899, "lightslategrey": 0xFF778899,
    "lightsteelblue": 0xFFB0C4DE, "lightsteelblue1": 0xFFCAE1FF,
    "lightsteelblue2": 0xFFBCD2EE, "lightsteelblue3": 0xFFA2B5CD,
    "lightsteelblue4": 0xFF6E7B8B, "lightyellow": 0xFFFFFFE0,
    "lightyellow1": 0xFFFFFFE0, "lightyellow2": 0xFFEEEED1,
    "lightyellow3": 0xFFCDCDB4, "lightyellow4": 0xFF8B8B7A,
    "limegreen": 0xFF32CD32, "linen": 0xFFFAF0E6, "magenta": 0xFFFF00FF,
    "magenta1": 0xFFFF00FF, "magenta2": 0xFFEE00EE, "magenta3": 0xFFCD00CD,
    "magenta4": 0xFF8B008B, "maroon": 0xFFB03060, "maroon1": 0xFFFF34B3,
    "maroon2": 0xFFEE30A7, "maroon3": 0xFFCD2990, "maroon4": 0xFF8B1C62,
    "mediumaquamarine": 0xFF66CDAA, "mediumblue": 0xFF0000CD,
    "mediumorchid": 0xFFBA55D3, "mediumorchid1": 0xFFE066FF,
    "mediumorchid2": 0xFFD15FEE, "mediumorchid3": 0xFFB452CD,
    "mediumorchid4": 0xFF7A378B, "mediumpurple": 0xFF9370DB,
    "mediumpurple1": 0xFFAB82FF, "mediumpurple2": 0xFF9F79EE,
    "mediumpurple3": 0xFF8968CD, "mediumpurple4": 0xFF5D478B,
    "mediumseagreen": 0xFF3CB371, "mediumslateblue": 0xFF7B68EE,
    "mediumspringgreen": 0xFF00FA9A, "mediumturquoise": 0xFF48D1CC,
    "mediumvioletred": 0xFFC71585, "midnightblue": 0xFF191970,
    "mintcream": 0xFFF5FFFA, "mistyrose": 0xFFFFE4E1,
    "mistyrose1": 0xFFFFE4E1, "mistyrose2": 0xFFEED5D2,
    "mistyrose3": 0xFFCDB7B5, "mistyrose4": 0xFF8B7D7B,
    "moccasin": 0xFFFFE4B5, "navajowhite": 0xFFFFDEAD,
    "navajowhite1": 0xFFFFDEAD, "navajowhite2": 0xFFEECFA1,
    "navajowhite3": 0xFFCDB38B, "navajowhite4": 0xFF8B795E,
    "navy": 0xFF000080, "navyblue": 0xFF000080, "oldlace": 0xFFFDF5E6,
    "olivedrab": 0xFF6B8E23, "olivedrab1": 0xFFC0FF3E,
    "olivedrab2": 0xFFB3EE3A, "olivedrab3": 0xFF9ACD32,
    "olivedrab4": 0xFF698B22, "orange": 0xFFFFA500, "orange1": 0xFFFFA500,
    "orange2": 0xFFEE9A00, "orange3": 0xFFCD8500, "orange4": 0xFF8B5A00,
    "orangered": 0xFFFF4500, "orangered1": 0xFFFF4500,
    "orangered2": 0xFFEE4000, "orangered3": 0xFFCD3700,
    "orangered4": 0xFF8B2500, "orchid": 0xFFDA70D6, "orchid1": 0xFFFF83FA,
    "orchid2": 0xFFEE7AE9, "orchid3": 0xFFCD69C9, "orchid4": 0xFF8B4789,
    "palegoldenrod": 0xFFEEE8AA, "palegreen": 0xFF98FB98,
    "palegreen1": 0xFF9AFF9A, "palegreen2": 0xFF90EE90,
    "palegreen3": 0xFF7CCD7C, "palegreen4": 0xFF548B54,
    "paleturquoise": 0xFFAFEEEE, "paleturquoise1": 0xFFBBFFFF,
    "paleturquoise2": 0xFFAEEEEE, "paleturquoise3": 0xFF96CDCD,
    "paleturquoise4": 0xFF668B8B, "palevioletred": 0xFFDB7093,
    "palevioletred1": 0xFFFF82AB, "palevioletred2": 0xFFEE799F,
    "palevioletred3": 0xFFCD6889, "palevioletred4": 0xFF8B475D,
    "papayawhip": 0xFFFFEFD5, "peachpuff": 0xFFFFDAB9,
    "peachpuff1": 0xFFFFDAB9, "peachpuff2": 0xFFEECBAD,
    "peachpuff3": 0xFFCDAF95, "peachpuff4": 0xFF8B7765,
    "peru": 0xFFCD853F, "pink": 0xFFFFC0CB, "pink1": 0xFFFFB5C5,
    "pink2": 0xFFEEA9B8, "pink3": 0xFFCD919E, "pink4": 0xFF8B636C,
    "plum": 0xFFDDA0DD, "plum1": 0xFFFFBBFF, "plum2": 0xFFEEAEEE,
    "plum3": 0xFFCD96CD, "plum4": 0xFF8B668B, "powderblue": 0xFFB0E0E6,
    "purple": 0xFFA020F0, "purple1": 0xFF9B30FF, "purple2": 0xFF912CEE,
    "purple3": 0xFF7D26CD, "purple4": 0xFF551A8B, "red": 0xFFFF0000,
    "red1": 0xFFFF0000, "red2": 0xFFEE0000, "red3": 0xFFCD0000,
    "red4": 0xFF8B0000, "rosybrown": 0xFFBC8F8F, "rosybrown1": 0xFFFFC1C1,
    "rosybrown2": 0xFFEEB4B4, "rosybrown3": 0xFFCD9B9B,
    "rosybrown4": 0xFF8B6969, "royalblue": 0xFF4169E1,
    "royalblue1": 0xFF4876FF, "royalblue2": 0xFF436EEE,
    "royalblue3": 0xFF3A5FCD, "royalblue4": 0xFF27408B,
    "saddlebrown": 0xFF8B4513, "salmon": 0xFFFA8072, "salmon1": 0xFFFF8C69,
    "salmon2": 0xFFEE8262, "salmon3": 0xFFCD7054, "salmon4": 0xFF8B4C39,
    "sandybrown": 0xFFF4A460, "seagreen": 0xFF2E8B57,
    "seagreen1": 0xFF54FF9F, "seagreen2": 0xFF4EEE94,
    "seagreen3": 0xFF43CD80, "seagreen4": 0xFF2E8B57,
    "seashell": 0xFFFFF5EE, "seashell1": 0xFFFFF5EE,
    "seashell2": 0xFFEEE5DE, "seashell3": 0xFFCDC5BF,
    "seashell4": 0xFF8B8682, "sienna": 0xFFA0522D, "sienna1": 0xFFFF8247,
    "sienna2": 0xFFEE7942, "sienna3": 0xFFCD6839, "sienna4": 0xFF8B4726,
    "skyblue": 0xFF87CEEB, "skyblue1": 0xFF87CEFF, "skyblue2": 0xFF7EC0EE,
    "skyblue3": 0xFF6CA6CD, "skyblue4": 0xFF4A708B, "slateblue": 0xFF6A5ACD,
    "slateblue1": 0xFF836FFF, "slateblue2": 0xFF7A67EE,
    "slateblue3": 0xFF6959CD, "slateblue4": 0xFF473C8B,
    "slategray": 0xFF708090, "slategray1": 0xFFC6E2FF,
    "slategray2": 0xFFB9D3EE, "slategray3": 0xFF9FB6CD,
    "slategray4": 0xFF6C7B8B, "slategrey": 0xFF708090, "snow": 0xFFFFFAFA,
    "snow1": 0xFFFFFAFA, "snow2": 0xFFEEE9E9, "snow3": 0xFFCDC9C9,
    "snow4": 0xFF8B8989, "springgreen": 0xFF00FF7F,
    "springgreen1": 0xFF00FF7F, "springgreen2": 0xFF00EE76,
    "springgreen3": 0xFF00CD66, "springgreen4": 0xFF008B45,
    "steelblue": 0xFF4682B4, "steelblue1": 0xFF63B8FF,
    "steelblue2": 0xFF5CACEE, "steelblue3": 0xFF4F94CD,
    "steelblue4": 0xFF36648B, "tan": 0xFFD2B48C, "tan1": 0xFFFFA54F,
    "tan2": 0xFFEE9A49, "tan3": 0xFFCD853F, "tan4": 0xFF8B5A2B,
    "thistle": 0xFFD8BFD8, "thistle1": 0xFFFFE1FF, "thistle2": 0xFFEED2EE,
    "thistle3": 0xFFCDB5CD, "thistle4": 0xFF8B7B8B, "tomato": 0xFFFF6347,
    "tomato1": 0xFFFF6347, "tomato2": 0xFFEE5C42, "tomato3": 0xFFCD4F39,
    "tomato4": 0xFF8B3626, "turquoise": 0xFF40E0D0,
    "turquoise1": 0xFF00F5FF, "turquoise2": 0xFF00E5EE,
    "turquoise3": 0xFF00C5CD, "turquoise4": 0xFF00868B,
    "violet": 0xFFEE82EE, "violetred": 0xFFD02090, "violetred1": 0xFFFF3E96,
    "violetred2": 0xFFEE3A8C, "violetred3": 0xFFCD3278,
    "violetred4": 0xFF8B2252, "wheat": 0xFFF5DEB3, "wheat1": 0xFFFFE7BA,
    "wheat2": 0xFFEED8AE, "wheat3": 0xFFCDBA96, "wheat4": 0xFF8B7E66,
    "white": 0xFFFFFFFF, "whitesmoke": 0xFFF5F5F5, "yellow": 0xFFFFFF00,
    "yellow1": 0xFFFFFF00, "yellow2": 0xFFEEEE00, "yellow3": 0xFFCDCD00,
    "yellow4": 0xFF8B8B00, "yellowgreen": 0xFF9ACD32})
