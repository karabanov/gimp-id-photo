#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Фото на документы в GIMP
# Александр Карабанов
# zend.karabanov@gmail.com
# Cursor

# Эта программа является свободным программным обеспечением:
# вы можете распространять её и/или модифицировать
# в соответствии с условиями лицензии GNU General Public License версии 3
# либо (по вашему выбору) любой более поздней версии, опубликованной
# Free Software Foundation.

# Эта программа распространяется в надежде на то, что она будет полезной,
# но БЕЗ КАКИХ-ЛИБО ГАРАНТИЙ, вы используете её на свой СТРАХ и РИСК.
# Прочтите GNU General Public License для более подробной информации.

# Вы должны были получить копию GNU General Public License
# вместе с этой программой. Если нет, см. <http://www.gnu.org/licenses/>.

import os
import pickle
import sys

import gi

gi.require_version("Gegl", "0.4")
gi.require_version("Gimp", "3.0")
gi.require_version("GimpUi", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gegl, Gimp, GimpUi, Gtk

CATEGORY_LABELS = ("Разное", "Паспорт", "Виза", "Удостоверение")
CATEGORY_KEYS = ("other", "pass", "visa", "cert")
ANGLE_LABELS = (
    "Без уголка",
    "Круглый справа",
    "Круглый слева",
    "Прямой справа",
    "Прямой слева",
)
ANGLE_KEYS = (False, "right_circular", "left_circular", "right_direct", "left_direct")
PAPER_LABELS = ("10x15", "A5", "A4")

_PLUGINDIR = os.path.dirname(os.path.abspath(__file__))
if _PLUGINDIR not in sys.path:
    sys.path.insert(0, _PLUGINDIR)

DEFAULT_PROPERTIES = {'auto_levels': False, 'resolution': 600, 'white_bg': True}

DEFAULT_FORMATS = [{'angle': False,
  'category': 'pass',
  'copys': 4,
  'faceheight': 12,
  'gray_frame': False,
  'height': 47,
  'name': 'Паспорт РФ',
  'onlyface': True,
  'oval': False,
  'overheadheight': 5,
  'paper': '10x15',
  'print_photo': False,
  'to_grayscale': False,
  'width': 37},
 {'angle': False,
  'category': 'pass',
  'copys': 4,
  'faceheight': 34,
  'gray_frame': False,
  'height': 47,
  'name': 'Загран. паспорт МИД',
  'onlyface': False,
  'oval': False,
  'overheadheight': 4,
  'paper': '10x15',
  'print_photo': False,
  'to_grayscale': False,
  'width': 36},
 {'angle': False,
  'category': 'pass',
  'copys': 4,
  'faceheight': 12,
  'gray_frame': False,
  'height': 45,
  'name': 'Загран. паспорт ОВИР',
  'onlyface': True,
  'oval': True,
  'overheadheight': 5,
  'paper': '10x15',
  'print_photo': False,
  'to_grayscale': True,
  'width': 35},
 {'angle': False,
  'category': 'visa',
  'copys': 4,
  'faceheight': 33,
  'gray_frame': False,
  'height': 47,
  'name': 'Виза Шенген',
  'onlyface': False,
  'oval': False,
  'overheadheight': 4,
  'paper': '10x15',
  'print_photo': False,
  'to_grayscale': False,
  'width': 36},
 {'angle': False,
  'category': 'visa',
  'copys': 4,
  'faceheight': 30,
  'gray_frame': False,
  'height': 47,
  'name': 'Виза Финляндия',
  'onlyface': False,
  'oval': False,
  'overheadheight': 4,
  'paper': '10x15',
  'print_photo': False,
  'to_grayscale': False,
  'width': 36},
 {'angle': False,
  'category': 'visa',
  'copys': 4,
  'faceheight': 30,
  'gray_frame': False,
  'height': 47,
  'name': 'Виза Голландия',
  'onlyface': False,
  'oval': False,
  'overheadheight': 4,
  'paper': '10x15',
  'print_photo': False,
  'to_grayscale': False,
  'width': 36},
 {'angle': False,
  'category': 'visa',
  'copys': 4,
  'faceheight': 15,
  'gray_frame': False,
  'height': 45,
  'name': 'Виза Болгария',
  'onlyface': True,
  'oval': False,
  'overheadheight': 4,
  'paper': '10x15',
  'print_photo': False,
  'to_grayscale': False,
  'width': 35},
 {'angle': False,
  'category': 'visa',
  'copys': 4,
  'faceheight': 35,
  'gray_frame': False,
  'height': 51,
  'name': 'Виза США',
  'onlyface': False,
  'oval': False,
  'overheadheight': 5,
  'paper': '10x15',
  'print_photo': False,
  'to_grayscale': False,
  'width': 51},
 {'angle': False,
  'category': 'visa',
  'copys': 4,
  'faceheight': 33,
  'gray_frame': False,
  'height': 45,
  'name': 'Виза Канада',
  'onlyface': False,
  'oval': False,
  'overheadheight': 5,
  'paper': '10x15',
  'print_photo': False,
  'to_grayscale': False,
  'width': 35},
 {'angle': False,
  'category': 'visa',
  'copys': 4,
  'faceheight': 14,
  'gray_frame': False,
  'height': 45,
  'name': 'Виза Латвия',
  'onlyface': True,
  'oval': False,
  'overheadheight': 4,
  'paper': '10x15',
  'print_photo': False,
  'to_grayscale': False,
  'width': 35},
 {'angle': False,
  'category': 'visa',
  'copys': 4,
  'faceheight': 33,
  'gray_frame': False,
  'height': 45,
  'name': 'Виза Чехия',
  'onlyface': False,
  'oval': False,
  'overheadheight': 4,
  'paper': '10x15',
  'print_photo': False,
  'to_grayscale': False,
  'width': 35},
 {'angle': False,
  'category': 'visa',
  'copys': 4,
  'faceheight': 33,
  'gray_frame': False,
  'height': 45,
  'name': 'Виза Польша',
  'onlyface': False,
  'oval': False,
  'overheadheight': 4,
  'paper': '10x15',
  'print_photo': False,
  'to_grayscale': False,
  'width': 35},
 {'angle': False,
  'category': 'visa',
  'copys': 4,
  'faceheight': 18,
  'gray_frame': False,
  'height': 45,
  'name': 'Виза Англия',
  'onlyface': True,
  'oval': False,
  'overheadheight': 4,
  'paper': '10x15',
  'print_photo': False,
  'to_grayscale': False,
  'width': 35},
 {'angle': False,
  'category': 'visa',
  'copys': 4,
  'faceheight': 14,
  'gray_frame': False,
  'height': 45,
  'name': 'Виза ОАЭ',
  'onlyface': True,
  'oval': False,
  'overheadheight': 4,
  'paper': '10x15',
  'print_photo': False,
  'to_grayscale': False,
  'width': 35},
 {'angle': False,
  'category': 'cert',
  'copys': 4,
  'faceheight': 12,
  'gray_frame': False,
  'height': 40,
  'name': 'Водительское',
  'onlyface': True,
  'oval': False,
  'overheadheight': 4,
  'paper': '10x15',
  'print_photo': False,
  'to_grayscale': False,
  'width': 30},
 {'angle': False,
  'category': 'cert',
  'copys': 4,
  'faceheight': 12,
  'gray_frame': False,
  'height': 34,
  'name': 'Пенсионное',
  'onlyface': True,
  'oval': False,
  'overheadheight': 3,
  'paper': '10x15',
  'print_photo': False,
  'to_grayscale': False,
  'width': 27},
 {'angle': False,
  'category': 'cert',
  'copys': 4,
  'faceheight': 9,
  'gray_frame': False,
  'height': 34,
  'name': 'Ветеран войны',
  'onlyface': True,
  'oval': False,
  'overheadheight': 4,
  'paper': '10x15',
  'print_photo': False,
  'to_grayscale': False,
  'width': 27},
 {'angle': False,
  'category': 'cert',
  'copys': 4,
  'faceheight': 12,
  'gray_frame': False,
  'height': 34,
  'name': 'Мать одиночка',
  'onlyface': True,
  'oval': False,
  'overheadheight': 3,
  'paper': '10x15',
  'print_photo': False,
  'to_grayscale': False,
  'width': 27},
 {'angle': False,
  'category': 'cert',
  'copys': 4,
  'faceheight': 7,
  'gray_frame': False,
  'height': 25,
  'name': 'Профсоюзный билет',
  'onlyface': True,
  'oval': False,
  'overheadheight': 4,
  'paper': '10x15',
  'print_photo': False,
  'to_grayscale': False,
  'width': 25},
 {'angle': False,
  'category': 'other',
  'copys': 4,
  'faceheight': 12,
  'gray_frame': False,
  'height': 50,
  'name': 'Вид на жительство',
  'onlyface': True,
  'oval': False,
  'overheadheight': 4,
  'paper': '10x15',
  'print_photo': False,
  'to_grayscale': False,
  'width': 40},
 {'angle': False,
  'category': 'other',
  'copys': 4,
  'faceheight': 35,
  'gray_frame': False,
  'height': 51,
  'name': 'Грин-карта',
  'onlyface': False,
  'oval': False,
  'overheadheight': 5,
  'paper': '10x15',
  'print_photo': False,
  'to_grayscale': False,
  'width': 51},
 {'angle': False,
  'category': 'other',
  'copys': 4,
  'faceheight': 35,
  'gray_frame': False,
  'height': 120,
  'name': 'Личное дело',
  'onlyface': True,
  'oval': False,
  'overheadheight': 10,
  'paper': '10x15',
  'print_photo': False,
  'to_grayscale': False,
  'width': 90},
 {'angle': False,
  'category': 'other',
  'copys': 4,
  'faceheight': 15,
  'gray_frame': False,
  'height': 55,
  'name': 'Пропуск',
  'onlyface': True,
  'oval': False,
  'overheadheight': 6,
  'paper': '10x15',
  'print_photo': False,
  'to_grayscale': False,
  'width': 40},
 {'angle': False,
  'category': 'other',
  'copys': 4,
  'faceheight': 12,
  'gray_frame': False,
  'height': 40,
  'name': 'Формат (30 х 40)',
  'onlyface': True,
  'oval': False,
  'overheadheight': 4,
  'paper': '10x15',
  'print_photo': False,
  'to_grayscale': False,
  'width': 30},
 {'angle': False,
  'category': 'other',
  'copys': 4,
  'faceheight': 15,
  'gray_frame': False,
  'height': 30,
  'name': 'Формат (30 x 25)',
  'onlyface': True,
  'oval': False,
  'overheadheight': 4,
  'paper': '10x15',
  'print_photo': False,
  'to_grayscale': False,
  'width': 25},
 {'angle': False,
  'category': 'other',
  'copys': 4,
  'faceheight': 15,
  'gray_frame': False,
  'height': 45,
  'name': 'Формат (35 x 45)',
  'onlyface': True,
  'oval': False,
  'overheadheight': 4,
  'paper': '10x15',
  'print_photo': False,
  'to_grayscale': False,
  'width': 35},
 {'angle': False,
  'category': 'other',
  'copys': 4,
  'faceheight': 12,
  'gray_frame': False,
  'height': 50,
  'name': 'Формат (40 x 50)',
  'onlyface': True,
  'oval': False,
  'overheadheight': 4,
  'paper': '10x15',
  'print_photo': False,
  'to_grayscale': False,
  'width': 40},
 {'angle': False,
  'category': 'other',
  'copys': 4,
  'faceheight': 15,
  'gray_frame': False,
  'height': 60,
  'name': 'Формат (40 x 60)',
  'onlyface': True,
  'oval': False,
  'overheadheight': 4,
  'paper': '10x15',
  'print_photo': False,
  'to_grayscale': False,
  'width': 40},
 {'angle': False,
  'category': 'other',
  'copys': 4,
  'faceheight': 12,
  'gray_frame': False,
  'height': 35,
  'name': 'Формат (45 x 35)',
  'onlyface': True,
  'oval': False,
  'overheadheight': 4,
  'paper': '10x15',
  'print_photo': False,
  'to_grayscale': False,
  'width': 45},
 {'angle': False,
  'category': 'other',
  'copys': 4,
  'faceheight': 14,
  'gray_frame': False,
  'height': 50,
  'name': 'Формат (45 x 50)',
  'onlyface': True,
  'oval': False,
  'overheadheight': 4,
  'paper': '10x15',
  'print_photo': False,
  'to_grayscale': False,
  'width': 45},
 {'angle': False,
  'category': 'other',
  'copys': 4,
  'faceheight': 22,
  'gray_frame': False,
  'height': 60,
  'name': 'Формат (45 x 60)',
  'onlyface': True,
  'oval': False,
  'overheadheight': 4,
  'paper': '10x15',
  'print_photo': False,
  'to_grayscale': False,
  'width': 45},
 {'angle': False,
  'category': 'other',
  'copys': 4,
  'faceheight': 35,
  'gray_frame': False,
  'height': 120,
  'name': 'Формат (90 x 120)',
  'onlyface': True,
  'oval': False,
  'overheadheight': 10,
  'paper': '10x15',
  'print_photo': False,
  'to_grayscale': False,
  'width': 90}]


def get_gimp_dir():
    d = Gimp.directory()
    return d if isinstance(d, str) else d.get_path()


def normalize_properties(props):
    merged = dict(DEFAULT_PROPERTIES)
    if props:
        merged.update(props)
    return merged


def normalize_format_row(row):
    out = dict(row)
    out.pop("url", None)
    defaults = {
        "category": "other",
        "angle": False,
        "gray_frame": False,
        "oval": False,
        "to_grayscale": False,
        "print_photo": False,
        "paper": "10x15",
        "copys": 4,
    }
    for k, v in defaults.items():
        out.setdefault(k, v)
    return out


def gegl_rgb8(r, g, b):
    c = Gegl.Color.new("")
    c.set_rgba(r / 255.0, g / 255.0, b / 255.0, 1.0)
    return c


def mm_in_px(size_mm, res):
    return int(round((size_mm / 25.4) * res))


def collect_guides(image):
    h_guides, v_guides, all_ids = [], [], []
    gid = image.find_next_guide(0)
    while gid != 0:
        all_ids.append(gid)
        orient = image.get_guide_orientation(gid)
        pos = image.get_guide_position(gid)
        if orient == Gimp.OrientationType.HORIZONTAL:
            h_guides.append(pos)
        elif orient == Gimp.OrientationType.VERTICAL:
            v_guides.append(pos)
        gid = image.find_next_guide(gid)
    h_guides.sort()
    v_guides.sort()
    return h_guides, v_guides, all_ids


def validate_guides(h_guides, v_guides, info_cb):
    if not h_guides and not v_guides:
        info_cb(
            "Нет ни одной направляющей.\n\n"
            "Поместите одну горизонтальную направляющую на уровне верхней части головы, "
            "одну горизонтальную на уровне глаз и одну на уровне подбородка, затем поставьте "
            "одну вертикальную направляющую на линию симметрии лица.\n\n"
            "Порядок расстановки направляющих не важен."
        )
        return False
    if len(h_guides) != 3:
        info_cb(
            "Горизонтальных направляющих должно быть три.\n\n"
            "Расставьте направляющие правильно и попробуйте ещё раз."
        )
        return False
    if len(v_guides) < 1:
        info_cb(
            "Нет вертикальной направляющей.\n\n"
            "Установите вертикальную направляющую на линию симметрии лица и попробуйте ещё раз."
        )
        return False
    if len(v_guides) > 1:
        info_cb(
            "Должна быть только одна вертикальная направляющая.\n\n"
            "Расставьте направляющие правильно и попробуйте ещё раз."
        )
        return False
    return True


def delete_guides(image, guide_ids):
    for gid in guide_ids:
        try:
            image.delete_guide(gid)
        except Exception:
            pass


def create_id_foto(image, layer, fmt, resolution, auto_levels, info_cb):
    h_guides, v_guides, guide_ids = collect_guides(image)
    if not validate_guides(h_guides, v_guides, info_cb):
        return None

    onlyface = fmt.get("onlyface", True)
    k = (h_guides[2] - h_guides[1]) if onlyface else (h_guides[2] - h_guides[0])
    w = int(round((fmt["width"] * k) / fmt["faceheight"]))
    h = int(round((fmt["height"] * k) / fmt["faceheight"]))
    x = int((w / 2) - v_guides[0])
    y = int(round((fmt["overheadheight"] * k) / fmt["faceheight"]) - h_guides[0])

    image.resize(w, h, x, y)

    Gimp.context_push()
    try:
        old_bg = Gimp.context_get_background()
        Gimp.context_set_background(gegl_rgb8(113, 255, 0))
        layer = image.flatten()
        Gimp.context_set_background(old_bg)
    finally:
        Gimp.context_pop()

    image.set_resolution(float(resolution), float(resolution))

    delete_guides(image, guide_ids)

    if auto_levels:
        if layer.is_indexed():
            image.convert_rgb()
            layer = image.flatten()
            info_cb(
                'Инструмент "авто-уровни" не работает с индексированными слоями.\n\n'
                'Слой был переведён в RGB.'
            )
        layer.levels_stretch()

    return layer


def to_grayscale(image, drawable):
    if not drawable.is_gray():
        image.convert_grayscale()
        return image.flatten()
    return drawable


def gray_frame(image):
    image.resize(image.get_width() + 2, image.get_height() + 2, 1, 1)
    Gimp.context_push()
    try:
        old_bg = Gimp.context_get_background()
        Gimp.context_set_background(gegl_rgb8(200, 200, 200))
        layer = image.flatten()
        Gimp.context_set_background(old_bg)
        return layer
    finally:
        Gimp.context_pop()


def oval_portrait(image, drawable, resolution):
    if drawable.is_gray() or drawable.is_indexed():
        image.convert_rgb()
        drawable = image.get_layers()[0] if image.get_layers() else drawable

    w, h = drawable.get_width(), drawable.get_height()
    white = Gimp.Layer.new(
        image,
        "Овал с растушёвкой",
        w,
        h,
        Gimp.ImageType.RGBA_IMAGE,
        100.0,
        Gimp.LayerMode.NORMAL,
    )
    Gimp.context_push()
    try:
        old_bg = Gimp.context_get_background()
        Gimp.context_set_background(gegl_rgb8(255, 255, 255))
        white.fill(Gimp.FillType.BACKGROUND)
        Gimp.context_set_background(old_bg)
        Gimp.context_set_antialias(True)
        Gimp.context_set_feather(True)
        fr = float(mm_in_px(4.5, resolution))
        Gimp.context_set_feather_radius(fr, fr)
        image.insert_layer(white, None, 0)
        image.select_ellipse(
            Gimp.ChannelOps.REPLACE,
            w * 0.1,
            0.0,
            w * 0.8,
            h * 0.9,
        )
        white.edit_clear()
        Gimp.Selection.none(image)
        Gimp.context_set_feather(False)
        Gimp.context_set_antialias(True)
    finally:
        Gimp.context_pop()
    return image.flatten()


def angle_corner(image, drawable, angle_type, resolution):
    if not angle_type:
        return drawable
    Gimp.context_push()
    try:
        Gimp.context_set_antialias(True)
        Gimp.context_set_feather(True)
        Gimp.context_set_feather_radius(2.0, 2.0)
        iw, ih = image.get_width(), image.get_height()
        if angle_type == "right_circular":
            image.select_ellipse(
                Gimp.ChannelOps.REPLACE,
                float(iw - mm_in_px(18, resolution)),
                float(ih - mm_in_px(14, resolution)),
                float(mm_in_px(45, resolution)),
                float(mm_in_px(45, resolution)),
            )
        elif angle_type == "left_circular":
            image.select_ellipse(
                Gimp.ChannelOps.REPLACE,
                float(-mm_in_px(26, resolution)),
                float(ih - mm_in_px(14, resolution)),
                float(mm_in_px(45, resolution)),
                float(mm_in_px(45, resolution)),
            )
        elif angle_type == "right_direct":
            y0 = float(ih - mm_in_px(14, resolution))
            segs = [
                float(iw),
                y0,
                float(iw),
                float(ih),
                float(iw - mm_in_px(16, resolution)),
                float(ih),
            ]
            image.select_polygon(Gimp.ChannelOps.REPLACE, segs)
        elif angle_type == "left_direct":
            y0 = float(ih - mm_in_px(14, resolution))
            segs = [0.0, y0, 0.0, float(ih), float(mm_in_px(16, resolution)), float(ih)]
            image.select_polygon(Gimp.ChannelOps.REPLACE, segs)
        else:
            return drawable

        old_bg = Gimp.context_get_background()
        Gimp.context_set_background(gegl_rgb8(255, 255, 255))
        drawable.edit_clear()
        Gimp.context_set_background(old_bg)
        Gimp.Selection.none(image)
    finally:
        Gimp.context_set_feather(False)
        Gimp.context_pop()
    return drawable


PAPER_SIZE_MM = {"10x15": (99.99, 149.94), "A5": (148.51, 209.97), "A4": (209.97, 297.01)}


def print_photo(image, drawable, paper, copys, do_print, white_bg, resolution, info_cb):
    """Arrange the processed photo on paper and optionally invoke printing."""
    if paper not in PAPER_SIZE_MM:
        paper = "10x15"
    pw_mm, ph_mm = PAPER_SIZE_MM[paper]
    paper_w = mm_in_px(pw_mm, resolution)
    paper_h = mm_in_px(ph_mm, resolution)
    space = mm_in_px(1.5, resolution)
    lw = drawable.get_width() + space
    lh = drawable.get_height() + space
    w_count = paper_w // lw if lw else 0
    h_count = paper_h // lh if lh else 0
    w_rot = paper_w // lh if lh else 0
    h_rot = paper_h // lw if lw else 0

    if w_count == 0 or h_count == 0:
        info_cb(
            f'Ни одной фотографии не помещается на листе "{paper}".\n\n'
            "Выберите более подходящий формат бумаги."
        )
        return False

    image.resize(paper_w, paper_h, 0, 0)

    if white_bg:
        if drawable.is_rgb():
            ltype = Gimp.ImageType.RGB_IMAGE
        else:
            ltype = Gimp.ImageType.GRAY_IMAGE
        white_bg_layer = Gimp.Layer.new(
            image, "Белый фон", paper_w, paper_h, ltype, 100.0, Gimp.LayerMode.NORMAL
        )
        Gimp.context_push()
        try:
            old_bg = Gimp.context_get_background()
            Gimp.context_set_background(gegl_rgb8(255, 255, 255))
            white_bg_layer.fill(Gimp.FillType.BACKGROUND)
            Gimp.context_set_background(old_bg)
        finally:
            Gimp.context_pop()
        white_bg_layer.add_alpha()
        image.insert_layer(white_bg_layer, None, 0)
        image.lower_item_to_bottom(white_bg_layer)
        image.raise_item_to_top(drawable)

    if (w_rot * h_rot) > (w_count * h_count):
        drawable.transform_rotate_simple(
            Gimp.RotationType.DEGREES90, False, 0.0, 0.0
        )
        drawable.transform_translate(float(drawable.get_width()), 0.0)
        lw, lh = lh, lw
        w_count, h_count = w_rot, h_rot

    x0 = (paper_w - (lw * w_count)) // 2
    y0 = (paper_h - (lh * h_count)) // 2
    drawable.transform_translate(float(x0), float(y0))

    layer_group = Gimp.GroupLayer.new(image, "Фотографии")
    image.insert_layer(layer_group, None, 0)
    drawable.set_name("Фото")

    n = 0
    for i in range(h_count):
        for j in range(w_count):
            if n >= copys or n >= w_count * h_count:
                break
            dup = drawable.copy()
            dup.set_name("Фото")
            dup.add_alpha()
            image.insert_layer(dup, layer_group, 0)
            dup.transform_translate(float(j * lw), float(i * lh))
            n += 1
        if n >= copys or n >= w_count * h_count:
            break

    image.remove_layer(drawable)

    if do_print:
        _try_invoke_print(image)
    return True


def _try_invoke_print(image):
    pdb = Gimp.get_pdb()
    layers = image.get_layers()
    top = layers[0] if layers else None

    def _try_set(cfg, name, value):
        try:
            cfg.set_property(name, value)
            return True
        except Exception:
            return False

    for proc_name in (
        "file-print",
        "file-print-gtk",
        "gimp-file-print",
        "plug-in-file-print-gtk",
    ):
        proc = pdb.lookup_procedure(proc_name)
        if not proc:
            continue
        cfg = proc.create_config()
        _try_set(cfg, "run-mode", Gimp.RunMode.INTERACTIVE)
        _try_set(cfg, "image", image)
        if top is not None:
            _try_set(cfg, "drawable", top)
        try:
            proc.run(cfg)
            return
        except Exception:
            continue
    Gimp.message(
        "Печать: используйте меню изображения «Файл» → «Печать…» (или Ctrl+P), "
        "если автоматический вызов печати недоступен в этой версии GIMP."
    )


class id_photo_base:
    def init_config(self):
        dir_path = os.path.join(get_gimp_dir(), "id_photo")
        self.path = os.path.join(dir_path, "formats.dat")
        os.makedirs(dir_path, exist_ok=True)

        if not os.path.exists(self.path):
            self.data = {
                "formats": [normalize_format_row(dict(x)) for x in DEFAULT_FORMATS],
                "properties": normalize_properties(DEFAULT_PROPERTIES),
                "last_format": None,
            }
            self._save_config()
        else:
            with open(self.path, "rb") as f:
                self.data = pickle.load(f)
            self._migrate_config()

    def _migrate_config(self):
        if not isinstance(self.data, dict):
            self.data = {}
        if "formats" not in self.data or not isinstance(self.data["formats"], list):
            self.data["formats"] = [normalize_format_row(dict(x)) for x in DEFAULT_FORMATS]
        else:
            self.data["formats"] = [normalize_format_row(dict(x)) for x in self.data["formats"]]
            # Раньше в formats.dat мог остаться короткий список (2 формата) — дополняем штатные пресеты.
            added = self._merge_missing_default_formats()
            if added:
                self._save_config()
        self.data["properties"] = normalize_properties(self.data.get("properties"))
        if "last_format" not in self.data:
            self.data["last_format"] = None
        elif self.data["last_format"]:
            lf = normalize_format_row(dict(self.data["last_format"]))
            lf.setdefault("resolution", self.data["properties"].get("resolution", 600))
            self.data["last_format"] = lf

    def _merge_missing_default_formats(self):
        """Добавить из DEFAULT_FORMATS записи, которых ещё нет (сравнение по полю name)."""
        names = {f.get("name") for f in self.data["formats"]}
        added = False
        for row in DEFAULT_FORMATS:
            n = row.get("name")
            if n and n not in names:
                self.data["formats"].append(normalize_format_row(dict(row)))
                names.add(n)
                added = True
        return added

    def _save_config(self):
        with open(self.path, "wb") as f:
            pickle.dump(self.data, f)

    def store_last_format(self, fmt, resolution):
        row = normalize_format_row(dict(fmt))
        row["resolution"] = int(resolution)
        self.data["last_format"] = row
        self._save_config()

    def info(self, msg, parent=None):
        d = Gtk.MessageDialog(
            transient_for=parent,
            flags=0,
            type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Внимание",
        )
        d.format_secondary_text(msg)
        d.run()
        d.destroy()


class SelectFormatDialog(Gtk.Window, id_photo_base):
    def __init__(self, image, layer):
        Gtk.Window.__init__(self, title="Выбор формата фотографии")
        self.image, self.layer = image, layer
        self.init_config()
        self._fmt_by_widget = {}
        self._radio_first = None

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        root.set_border_width(10)

        nb = Gtk.Notebook()
        tab_labels = [
            ("pass", "Паспорта"),
            ("visa", "Визы"),
            ("cert", "Удостоверения"),
            ("other", "Разное"),
        ]
        for cat, title in tab_labels:
            scroll = Gtk.ScrolledWindow()
            scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            scroll.set_min_content_height(160)
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            scroll.add(box)
            for fmt in self.data["formats"]:
                if fmt.get("category", "other") != cat:
                    continue
                rb = Gtk.RadioButton.new_with_label_from_widget(self._radio_first, fmt["name"])
                if self._radio_first is None:
                    self._radio_first = rb
                rb.set_active(False)
                box.pack_start(rb, False, False, 0)
                self._fmt_by_widget[rb] = fmt
            nb.append_page(scroll, Gtk.Label(label=title))

        if self._radio_first:
            self._radio_first.set_active(True)

        self.autolevels = Gtk.CheckButton(label="авто-уровни")
        self.autolevels.set_active(bool(self.data["properties"].get("auto_levels")))

        btn_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        cancel = Gtk.Button.new_with_label("Отмена")
        cancel.connect("clicked", lambda *_: self.destroy())
        apply_btn = Gtk.Button.new_with_label("Применить")
        apply_btn.connect("clicked", self._on_apply, False)
        exec_btn = Gtk.Button.new_with_label("Выполнить автоматически")
        exec_btn.connect("clicked", self._on_apply, True)
        btn_row.pack_start(self.autolevels, False, False, 0)
        btn_row.pack_end(exec_btn, False, False, 0)
        btn_row.pack_end(apply_btn, False, False, 0)
        btn_row.pack_end(cancel, False, False, 0)

        root.pack_start(nb, True, True, 0)
        root.pack_start(btn_row, False, False, 0)
        self.add(root)
        self.connect("destroy", lambda *_: Gtk.main_quit())
        self.show_all()

    def _active_format(self):
        for rb, fmt in self._fmt_by_widget.items():
            if rb.get_active():
                return fmt
        return None

    def _on_apply(self, _btn, full_auto):
        fmt = self._active_format()
        if not fmt:
            self.info("Выберите формат.", parent=self)
            return

        res = int(self.data["properties"]["resolution"])
        fmt_run = normalize_format_row(dict(fmt))
        fmt_run["resolution"] = res
        auto_levels = self.autolevels.get_active()

        self.image.undo_group_start()
        try:
            layer = create_id_foto(
                self.image,
                self.layer,
                fmt_run,
                res,
                auto_levels,
                lambda m: self.info(m, parent=self),
            )
            if layer is None:
                return
            self.layer = layer

            if full_auto:
                tw = mm_in_px(fmt_run["width"], res)
                th = mm_in_px(fmt_run["height"], res)
                self.image.scale(tw, th)
                self.image.set_resolution(float(res), float(res))
                self.layer = self.image.get_layers()[0] if self.image.get_layers() else self.layer

                ang = fmt_run.get("angle")
                if ang:
                    self.layer = angle_corner(self.image, self.layer, ang, res)
                if fmt_run.get("oval"):
                    self.layer = oval_portrait(self.image, self.layer, res)
                if fmt_run.get("to_grayscale"):
                    self.layer = to_grayscale(self.image, self.layer)
                if fmt_run.get("gray_frame"):
                    self.layer = gray_frame(self.image)

                white_bg = bool(self.data["properties"].get("white_bg", True))
                if not print_photo(
                    self.image,
                    self.layer,
                    fmt_run.get("paper", "10x15"),
                    int(fmt_run.get("copys", 4)),
                    bool(fmt_run.get("print_photo")),
                    white_bg,
                    res,
                    lambda m: self.info(m, parent=self),
                ):
                    return

            self.store_last_format(fmt, res)
            Gimp.displays_flush()
        finally:
            self.image.undo_group_end()

        self.destroy()
        Gtk.main_quit()


class PrintPhotoDialog(Gtk.Window, id_photo_base):
    def __init__(self, image, layer):
        Gtk.Window.__init__(self, title="Сформировать и распечатать")
        self.image, self.layer = image, layer
        self.init_config()
        lf = self.data.get("last_format")
        if not lf:
            Gimp.message(
                "Сначала выберите формат: «На документы» → «Формат…», "
                "затем снова откройте «Печать…»."
            )
            self._abort = True
            return

        self._abort = False
        self.lf = normalize_format_row(dict(lf))
        self.lf["resolution"] = int(self.lf.get("resolution", self.data["properties"]["resolution"]))

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        root.set_border_width(10)

        self.gray_check = Gtk.CheckButton(label="обесцветить фото")
        self.gray_check.set_active(bool(self.lf.get("to_grayscale")))
        self.border_check = Gtk.CheckButton(label="добавить рамку")
        self.border_check.set_active(bool(self.lf.get("gray_frame")))
        self.oval_check = Gtk.CheckButton(label="добавить овал с растушёвкой")
        self.oval_check.set_active(bool(self.lf.get("oval")))

        self.angle_none = Gtk.RadioButton.new_with_label_from_widget(None, "без уголка")
        self.angle_rc = Gtk.RadioButton.new_with_label_from_widget(self.angle_none, "круглый справа")
        self.angle_lc = Gtk.RadioButton.new_with_label_from_widget(self.angle_none, "круглый слева")
        self.angle_rd = Gtk.RadioButton.new_with_label_from_widget(self.angle_none, "прямой справа")
        self.angle_ld = Gtk.RadioButton.new_with_label_from_widget(self.angle_none, "прямой слева")
        ag = self.lf.get("angle")
        if ag == "right_circular":
            self.angle_rc.set_active(True)
        elif ag == "left_circular":
            self.angle_lc.set_active(True)
        elif ag == "right_direct":
            self.angle_rd.set_active(True)
        elif ag == "left_direct":
            self.angle_ld.set_active(True)
        else:
            self.angle_none.set_active(True)

        adj = Gtk.Adjustment(value=float(self.lf.get("copys", 4)), lower=1, upper=200, step_increment=1)
        self.copys = Gtk.SpinButton.new(adj, 1, 0)
        self.paper = Gtk.ComboBoxText()
        for p in ("10x15", "A5", "A4"):
            self.paper.append_text(p)
        ap = self.lf.get("paper", "10x15")
        self.paper.set_active({"10x15": 0, "A5": 1, "A4": 2}.get(ap, 0))

        row1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        row1.pack_start(self.copys, False, False, 0)
        row1.pack_start(Gtk.Label(label="фото на листе"), False, False, 0)
        row1.pack_start(self.paper, False, False, 0)

        opts = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        opts.pack_start(row1, False, False, 0)
        opts.pack_start(self.gray_check, False, False, 0)
        opts.pack_start(self.border_check, False, False, 0)
        opts.pack_start(self.oval_check, False, False, 0)

        ang_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        for w in (self.angle_none, self.angle_rc, self.angle_lc, self.angle_rd, self.angle_ld):
            ang_box.pack_start(w, False, False, 0)
        frame = Gtk.Frame(label="Добавить уголок")
        frame.add(ang_box)

        grid = Gtk.Grid(column_spacing=10, row_spacing=8)
        grid.attach(opts, 0, 0, 1, 1)
        grid.attach(frame, 1, 0, 1, 1)

        btn_row = Gtk.ButtonBox.new(Gtk.Orientation.HORIZONTAL)
        btn_row.set_layout(Gtk.ButtonBoxStyle.END)
        btn_row.set_spacing(8)
        cancel = Gtk.Button.new_with_label("Отмена")
        cancel.connect("clicked", lambda *_: self.destroy())
        apply_btn = Gtk.Button.new_with_label("Применить")
        apply_btn.connect("clicked", self._compose, False)
        print_btn = Gtk.Button.new_with_label("Печать…")
        print_btn.connect("clicked", self._compose, True)
        btn_row.add(cancel)
        btn_row.add(apply_btn)
        btn_row.add(print_btn)

        root.pack_start(grid, True, True, 0)
        root.pack_start(btn_row, False, False, 0)
        self.add(root)
        self.connect("destroy", lambda *_: Gtk.main_quit())
        self.show_all()

    def _selected_angle(self):
        if self.angle_rc.get_active():
            return "right_circular"
        if self.angle_lc.get_active():
            return "left_circular"
        if self.angle_rd.get_active():
            return "right_direct"
        if self.angle_ld.get_active():
            return "left_direct"
        return False

    def _compose(self, _btn, do_print):
        res = int(self.lf["resolution"])
        self.image.undo_group_start()
        try:
            tw = mm_in_px(self.lf["width"], res)
            th = mm_in_px(self.lf["height"], res)
            self.image.scale(tw, th)
            self.image.set_resolution(float(res), float(res))
            layer = self.image.get_layers()[0] if self.image.get_layers() else self.layer

            if self.oval_check.get_active():
                layer = oval_portrait(self.image, layer, res)
            if self.gray_check.get_active():
                layer = to_grayscale(self.image, layer)
            if self.border_check.get_active():
                layer = gray_frame(self.image)
            ang = self._selected_angle()
            if ang:
                layer = angle_corner(self.image, layer, ang, res)

            paper = self.paper.get_active_text() or "10x15"
            copys = int(self.copys.get_value())
            white_bg = bool(self.data["properties"].get("white_bg", True))
            if not print_photo(
                self.image,
                layer,
                paper,
                copys,
                do_print,
                white_bg,
                res,
                lambda m: self.info(m, parent=self),
            ):
                return
            Gimp.displays_flush()
        finally:
            self.image.undo_group_end()
        self.destroy()
        Gtk.main_quit()


class SettingsDialog(Gtk.Window, id_photo_base):
    def __init__(self, image):
        Gtk.Window.__init__(self, title='Настройки дополнения «Фото на документы»')
        self.image = image
        self.init_config()
        self._radios = []

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        outer.set_border_width(10)

        paned = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
        left = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        scroll = Gtk.ScrolledWindow()
        scroll.set_min_content_width(260)
        scroll.set_min_content_height(220)
        self.list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        scroll.add(self.list_box)
        self._rebuild_format_radios()
        left.pack_start(scroll, True, True, 0)

        btn_fmt = Gtk.ButtonBox.new(Gtk.Orientation.HORIZONTAL)
        btn_fmt.set_layout(Gtk.ButtonBoxStyle.SPREAD)
        add_b = Gtk.Button.new_with_label("Добавить")
        add_b.connect("clicked", self._add_format)
        edit_b = Gtk.Button.new_with_label("Править")
        edit_b.connect("clicked", self._edit_format)
        del_b = Gtk.Button.new_with_label("Удалить")
        del_b.connect("clicked", self._delete_format)
        btn_fmt.add(add_b)
        btn_fmt.add(edit_b)
        btn_fmt.add(del_b)
        self._edit_btn, self._del_btn = edit_b, del_b
        self._sync_edit_buttons()
        left.pack_start(btn_fmt, False, False, 0)

        self.msg = Gtk.Label()
        self.msg.set_halign(Gtk.Align.START)

        right = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        res_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        res_row.pack_start(Gtk.Label(label="Разрешение (ppi):"), False, False, 0)
        self.res_combo = Gtk.ComboBoxText()
        for r in ("300", "600", "1147", "1200", "2400"):
            self.res_combo.append_text(r)
        cur = str(int(self.data["properties"].get("resolution", 600)))
        idx = {"300": 0, "600": 1, "1147": 2, "1200": 3, "2400": 4}.get(cur, 1)
        self.res_combo.set_active(idx)
        res_row.pack_start(self.res_combo, False, False, 0)
        self.white_bg = Gtk.CheckButton(label='Всегда добавлять слой «Белый фон»')
        self.white_bg.set_active(bool(self.data["properties"].get("white_bg", True)))
        self.def_autolevels = Gtk.CheckButton(label='По умолчанию включать «авто-уровни»')
        self.def_autolevels.set_active(bool(self.data["properties"].get("auto_levels")))
        right.pack_start(res_row, False, False, 0)
        right.pack_start(self.white_bg, False, False, 0)
        right.pack_start(self.def_autolevels, False, False, 0)

        paned.pack1(left, True, False)
        paned.pack2(right, True, False)
        paned.set_position(320)

        btn_row = Gtk.ButtonBox.new(Gtk.Orientation.HORIZONTAL)
        btn_row.set_layout(Gtk.ButtonBoxStyle.END)
        btn_row.set_spacing(8)
        about_b = Gtk.Button.new_with_label("О программе")
        about_b.connect("clicked", self._about)
        cancel = Gtk.Button.new_with_label("Отмена")
        cancel.connect("clicked", lambda *_: self.destroy())
        ok = Gtk.Button.new_with_label("Применить")
        ok.connect("clicked", self._apply_settings)
        btn_row.add(about_b)
        btn_row.add(cancel)
        btn_row.add(ok)

        outer.pack_start(paned, True, True, 0)
        outer.pack_start(self.msg, False, False, 0)
        outer.pack_start(btn_row, False, False, 0)
        self.add(outer)
        self.connect("destroy", lambda *_: Gtk.main_quit())
        self.show_all()

    def _sync_edit_buttons(self):
        sens = len(self.data["formats"]) > 0
        self._edit_btn.set_sensitive(sens)
        self._del_btn.set_sensitive(sens)

    def _rebuild_format_radios(self):
        for c in self.list_box.get_children():
            self.list_box.remove(c)
        self._radios.clear()
        group = None
        for i, fmt in enumerate(self.data["formats"]):
            rb = Gtk.RadioButton.new_with_label_from_widget(group, fmt["name"])
            group = rb
            rb.set_active(i == 0)
            self.list_box.pack_start(rb, False, False, 0)
            self._radios.append(rb)
        self.list_box.show_all()

    def _selected_index(self):
        for i, rb in enumerate(self._radios):
            if rb.get_active():
                return i
        return 0

    def _apply_settings(self, *_):
        self.data["properties"]["white_bg"] = self.white_bg.get_active()
        self.data["properties"]["auto_levels"] = self.def_autolevels.get_active()
        self.data["properties"]["resolution"] = int(self.res_combo.get_active_text())
        self._save_config()
        self.destroy()
        Gtk.main_quit()

    def _about(self, *_):
        d = Gtk.AboutDialog()
        d.set_program_name("Фото на документы")
        d.set_version("GIMP 3 / 2026")
        d.set_comments(
            "Порт плагина для GIMP 3 (python-gi). Исходный плагин: Александр Карабанов."
        )
        d.set_website("http://gimp-id-photo.ru/")
        d.set_license_type(Gtk.License.GPL_3_0)
        d.run()
        d.destroy()

    def _delete_format(self, *_):
        i = self._selected_index()
        fmt = self.data["formats"][i]
        c = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f'Удалить формат «{fmt["name"]}»?',
        )
        r = c.run()
        c.destroy()
        if r != Gtk.ResponseType.YES:
            return
        del self.data["formats"][i]
        self._save_config()
        self._rebuild_format_radios()
        self._sync_edit_buttons()
        self.msg.set_text("Формат удалён.")

    def _edit_format(self, *_):
        i = self._selected_index()
        fmt = normalize_format_row(dict(self.data["formats"][i]))
        dlg = Gtk.Dialog(title=f'Правка формата «{fmt["name"]}»', transient_for=self, flags=0)
        dlg.add_buttons("Отмена", Gtk.ResponseType.CANCEL, "Сохранить", Gtk.ResponseType.OK)
        box = dlg.get_content_area()
        grid = Gtk.Grid(column_spacing=8, row_spacing=6)
        r = 0

        name_e = Gtk.Entry()
        name_e.set_text(fmt["name"])
        grid.attach(Gtk.Label(label="Название:", halign=Gtk.Align.START), 0, r, 1, 1)
        grid.attach(name_e, 1, r, 1, 1)
        r += 1

        cat_c = Gtk.ComboBoxText()
        for lab in CATEGORY_LABELS:
            cat_c.append_text(lab)
        try:
            cat_c.set_active(CATEGORY_KEYS.index(fmt.get("category", "other")))
        except ValueError:
            cat_c.set_active(0)
        grid.attach(Gtk.Label(label="Категория:", halign=Gtk.Align.START), 0, r, 1, 1)
        grid.attach(cat_c, 1, r, 1, 1)
        r += 1

        def spin_row(label, val, low, high):
            nonlocal r
            adj = Gtk.Adjustment(value=float(val), lower=low, upper=high, step_increment=1)
            sp = Gtk.SpinButton.new(adj, 1, 0)
            grid.attach(Gtk.Label(label=label, halign=Gtk.Align.START), 0, r, 1, 1)
            grid.attach(sp, 1, r, 1, 1)
            r += 1
            return sp

        w_sp = spin_row("Ширина (мм):", fmt["width"], 1, 300)
        h_sp = spin_row("Высота (мм):", fmt["height"], 1, 300)
        oh_sp = spin_row("До головы (мм):", fmt["overheadheight"], 0, 200)
        fh_sp = spin_row("Лицо: размер (мм):", fmt["faceheight"], 1, 200)

        only1 = Gtk.RadioButton.new_with_label_from_widget(None, "от глаз до подбородка")
        only2 = Gtk.RadioButton.new_with_label_from_widget(only1, "от макушки до подбородка")
        if fmt.get("onlyface", True):
            only1.set_active(True)
        else:
            only2.set_active(True)
        grid.attach(only1, 1, r, 1, 1)
        r += 1
        grid.attach(only2, 1, r, 1, 1)
        r += 1

        angle_c = Gtk.ComboBoxText()
        for lab in ANGLE_LABELS:
            angle_c.append_text(lab)
        ag = fmt.get("angle", False)
        try:
            angle_c.set_active(ANGLE_KEYS.index(ag))
        except ValueError:
            angle_c.set_active(0)
        grid.attach(Gtk.Label(label="Уголок:", halign=Gtk.Align.START), 0, r, 1, 1)
        grid.attach(angle_c, 1, r, 1, 1)
        r += 1

        paper_c = Gtk.ComboBoxText()
        for lab in PAPER_LABELS:
            paper_c.append_text(lab)
        try:
            paper_c.set_active(PAPER_LABELS.index(fmt.get("paper", "10x15")))
        except ValueError:
            paper_c.set_active(0)
        grid.attach(Gtk.Label(label="Бумага:", halign=Gtk.Align.START), 0, r, 1, 1)
        grid.attach(paper_c, 1, r, 1, 1)
        r += 1

        copys_sp = spin_row("Копий на листе:", fmt.get("copys", 4), 1, 200)

        cb_g = Gtk.CheckButton(label="обесцветить")
        cb_g.set_active(bool(fmt.get("to_grayscale")))
        cb_frame = Gtk.CheckButton(label="серая рамка")
        cb_frame.set_active(bool(fmt.get("gray_frame")))
        cb_oval = Gtk.CheckButton(label="овал")
        cb_oval.set_active(bool(fmt.get("oval")))
        cb_print = Gtk.CheckButton(label="печатать автоматически")
        cb_print.set_active(bool(fmt.get("print_photo")))
        for w in (cb_g, cb_frame, cb_oval, cb_print):
            grid.attach(w, 1, r, 1, 1)
            r += 1

        box.add(grid)
        dlg.show_all()
        resp = dlg.run()
        if resp == Gtk.ResponseType.OK:
            ic = cat_c.get_active()
            category = CATEGORY_KEYS[ic] if 0 <= ic < len(CATEGORY_KEYS) else "other"
            ia = angle_c.get_active()
            angle_val = ANGLE_KEYS[ia] if 0 <= ia < len(ANGLE_KEYS) else False
            ip = paper_c.get_active()
            paper = PAPER_LABELS[ip] if 0 <= ip < len(PAPER_LABELS) else "10x15"

            self.data["formats"][i] = {
                "name": name_e.get_text(),
                "category": category,
                "width": int(w_sp.get_value()),
                "height": int(h_sp.get_value()),
                "faceheight": int(fh_sp.get_value()),
                "onlyface": only1.get_active(),
                "overheadheight": int(oh_sp.get_value()),
                "angle": angle_val,
                "copys": int(copys_sp.get_value()),
                "gray_frame": cb_frame.get_active(),
                "oval": cb_oval.get_active(),
                "paper": paper,
                "to_grayscale": cb_g.get_active(),
                "print_photo": cb_print.get_active(),
            }
            self.data["formats"][i] = normalize_format_row(self.data["formats"][i])
            self._save_config()
            self._rebuild_format_radios()
            self.msg.set_markup(f'<span foreground="#008600">Сохранено.</span>')
        dlg.destroy()

    def _add_format(self, *_):
        dlg = Gtk.Dialog(title="Новый формат", transient_for=self, flags=0)
        dlg.add_buttons("Отмена", Gtk.ResponseType.CANCEL, "Добавить", Gtk.ResponseType.OK)
        box = dlg.get_content_area()
        grid = Gtk.Grid(column_spacing=8, row_spacing=6)
        r = 0

        name_e = Gtk.Entry()
        name_e.set_text("Новый формат")
        grid.attach(Gtk.Label(label="Название:", halign=Gtk.Align.START), 0, r, 1, 1)
        grid.attach(name_e, 1, r, 1, 1)
        r += 1

        cat_c = Gtk.ComboBoxText()
        for lab in CATEGORY_LABELS:
            cat_c.append_text(lab)
        cat_c.set_active(0)
        grid.attach(Gtk.Label(label="Категория:", halign=Gtk.Align.START), 0, r, 1, 1)
        grid.attach(cat_c, 1, r, 1, 1)
        r += 1

        def spin_row(label, val, low, high):
            nonlocal r
            adj = Gtk.Adjustment(value=float(val), lower=low, upper=high, step_increment=1)
            sp = Gtk.SpinButton.new(adj, 1, 0)
            grid.attach(Gtk.Label(label=label, halign=Gtk.Align.START), 0, r, 1, 1)
            grid.attach(sp, 1, r, 1, 1)
            r += 1
            return sp

        w_sp = spin_row("Ширина (мм):", 35, 1, 300)
        h_sp = spin_row("Высота (мм):", 45, 1, 300)
        oh_sp = spin_row("До головы (мм):", 4, 0, 200)
        fh_sp = spin_row("Лицо: размер (мм):", 12, 1, 200)
        only1 = Gtk.RadioButton.new_with_label_from_widget(None, "от глаз до подбородка")
        only2 = Gtk.RadioButton.new_with_label_from_widget(only1, "от макушки до подбородка")
        only1.set_active(True)
        grid.attach(only1, 1, r, 1, 1)
        r += 1
        grid.attach(only2, 1, r, 1, 1)
        r += 1

        angle_c = Gtk.ComboBoxText()
        for lab in ANGLE_LABELS:
            angle_c.append_text(lab)
        angle_c.set_active(0)
        grid.attach(Gtk.Label(label="Уголок:", halign=Gtk.Align.START), 0, r, 1, 1)
        grid.attach(angle_c, 1, r, 1, 1)
        r += 1

        paper_c = Gtk.ComboBoxText()
        for lab in PAPER_LABELS:
            paper_c.append_text(lab)
        paper_c.set_active(0)
        grid.attach(Gtk.Label(label="Бумага:", halign=Gtk.Align.START), 0, r, 1, 1)
        grid.attach(paper_c, 1, r, 1, 1)
        r += 1

        copys_sp = spin_row("Копий на листе:", 4, 1, 200)
        cb_g = Gtk.CheckButton(label="обесцветить")
        cb_frame = Gtk.CheckButton(label="серая рамка")
        cb_oval = Gtk.CheckButton(label="овал")
        cb_print = Gtk.CheckButton(label="печатать автоматически")
        for w in (cb_g, cb_frame, cb_oval, cb_print):
            grid.attach(w, 1, r, 1, 1)
            r += 1

        box.add(grid)
        dlg.show_all()
        resp = dlg.run()
        if resp == Gtk.ResponseType.OK:
            ic = cat_c.get_active()
            category = CATEGORY_KEYS[ic] if 0 <= ic < len(CATEGORY_KEYS) else "other"
            ia = angle_c.get_active()
            angle_val = ANGLE_KEYS[ia] if 0 <= ia < len(ANGLE_KEYS) else False
            ip = paper_c.get_active()
            paper = PAPER_LABELS[ip] if 0 <= ip < len(PAPER_LABELS) else "10x15"

            newf = normalize_format_row(
                {
                    "name": name_e.get_text(),
                    "category": category,
                    "width": int(w_sp.get_value()),
                    "height": int(h_sp.get_value()),
                    "faceheight": int(fh_sp.get_value()),
                    "onlyface": only1.get_active(),
                    "overheadheight": int(oh_sp.get_value()),
                    "angle": angle_val,
                    "copys": int(copys_sp.get_value()),
                    "gray_frame": cb_frame.get_active(),
                    "oval": cb_oval.get_active(),
                    "paper": paper,
                    "to_grayscale": cb_g.get_active(),
                    "print_photo": cb_print.get_active(),
                }
            )
            self.data["formats"].append(newf)
            self._save_config()
            self._rebuild_format_radios()
            self._sync_edit_buttons()
            self.msg.set_markup(f'<span foreground="#008600">Формат добавлен.</span>')
        dlg.destroy()


# GIMP 3: имя процедуры — канонический идентификатор (без «_», только [a-z0-9-]).
PROC_FORMAT = "python-select-format-id-photo"
PROC_SETTINGS = "python-settings"
PROC_PRINT = "python-print-photo"


class IdPhotoPlugin(Gimp.PlugIn):
    def do_query_procedures(self):
        return [PROC_FORMAT, PROC_SETTINGS, PROC_PRINT]

    def do_set_i18n(self, name):
        return False

    def do_create_procedure(self, name):
        Gegl.init(None)

        if name == PROC_FORMAT:
            p = Gimp.ImageProcedure.new(self, name, Gimp.PDBProcType.PLUGIN, self.run_format, None)
            p.set_image_types("RGB*,GRAY*")
            p.set_sensitivity_mask(
                Gimp.ProcedureSensitivityMask.DRAWABLE
                | Gimp.ProcedureSensitivityMask.DRAWABLES
            )
            p.set_menu_label("Формат…")
            p.add_menu_path("<Image>/На документы")
            p.set_documentation(
                "Выбор формата и обработка по направляющим",
                "Расставьте направляющие и выберите формат.",
                name,
            )
            p.set_attribution("id-photo", "id-photo", "2026")
            return p

        if name == PROC_SETTINGS:
            p = Gimp.ImageProcedure.new(self, name, Gimp.PDBProcType.PLUGIN, self.run_settings, None)
            p.set_image_types("*")
            p.set_sensitivity_mask(
                Gimp.ProcedureSensitivityMask.DRAWABLE
                | Gimp.ProcedureSensitivityMask.DRAWABLES
                | Gimp.ProcedureSensitivityMask.NO_DRAWABLES
            )
            p.set_menu_label("Настройки…")
            p.add_menu_path("<Image>/На документы")
            p.set_documentation("Настройки плагина", "Форматы и параметры печати.", name)
            p.set_attribution("id-photo", "id-photo", "2026")
            return p

        if name == PROC_PRINT:
            p = Gimp.ImageProcedure.new(self, name, Gimp.PDBProcType.PLUGIN, self.run_print, None)
            p.set_image_types("RGB*,GRAY*")
            p.set_sensitivity_mask(
                Gimp.ProcedureSensitivityMask.DRAWABLE
                | Gimp.ProcedureSensitivityMask.DRAWABLES
            )
            p.set_menu_label("Печать…")
            p.add_menu_path("<Image>/На документы")
            p.set_documentation("Раскладка на лист", "Сетка копий и печать.", name)
            p.set_attribution("id-photo", "id-photo", "2026")
            return p

        return None

    def run_format(self, procedure, run_mode, image, drawables, config, run_data):
        if run_mode != Gimp.RunMode.INTERACTIVE:
            Gimp.message("Плагин работает только в интерактивном режиме.")
            return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, None)
        if not drawables:
            Gimp.message("Нет выбранного слоя.")
            return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, None)
        layer = drawables[0]
        if not isinstance(layer, Gimp.Layer):
            Gimp.message("Выберите слой с изображением.")
            return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, None)
        GimpUi.init("id_photo")
        SelectFormatDialog(image, layer)
        Gtk.main()
        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, None)

    def run_settings(self, procedure, run_mode, image, drawables, config, run_data):
        if run_mode != Gimp.RunMode.INTERACTIVE:
            Gimp.message("Плагин работает только в интерактивном режиме.")
            return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, None)
        GimpUi.init("id_photo")
        SettingsDialog(image)
        Gtk.main()
        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, None)

    def run_print(self, procedure, run_mode, image, drawables, config, run_data):
        if run_mode != Gimp.RunMode.INTERACTIVE:
            Gimp.message("Плагин работает только в интерактивном режиме.")
            return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, None)
        if not drawables:
            Gimp.message("Нет выбранного слоя.")
            return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, None)
        layer = drawables[0]
        if not isinstance(layer, Gimp.Layer):
            Gimp.message("Выберите слой с изображением.")
            return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, None)
        GimpUi.init("id_photo")
        dlg = PrintPhotoDialog(image, layer)
        if getattr(dlg, "_abort", False):
            return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, None)
        Gtk.main()
        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, None)


if __name__ == "__main__":
    Gimp.main(IdPhotoPlugin.__gtype__, sys.argv)
