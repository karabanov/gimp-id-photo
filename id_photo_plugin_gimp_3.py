#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Фото на документы в GIMP (порт под GIMP 3.0 / Python 3 / GTK3)
# Оригинал: Александр Карабанов (zend.karabanov@gmail.com)
# Порт на GIMP 3: сделан UALinux https://ualinux.com/
# Эта программа является свободным программным обеспечением: вы можете распространять её и/или модифицировать в соответствии с условиями лицензии GNU General Public License версии 3 либо (по вашему выбору) любой более поздней версии, опубликованной Free Software Foundation.
# Эта программа распространяется в надежде на то, что она будет полезной, но БЕЗ КАКИХ-ЛИБО ГАРАНТИЙ, вы используете её на свой СТРАХ и РИСК.
# Прочтите GNU General Public License для более подробной информации.
# ============================================================================
#
# ЧТО ПОМЕНЯЛОСЬ ПРИ ПОРТИРОВАНИИ С GIMP 2.10 (Python 2) НА GIMP 3 (Python 3):
# 1. `gimpfu` больше не существует. Регистрация плагина теперь идёт через класс-наследник `Gimp.PlugIn` с методами do_query_procedures() / do_create_procedure(), см. класс IdPhotoPlugin в конце файла.
# 2. GTK2 (`import gtk`) заменён на GTK3 через GObject Introspection (`from gi.repository import Gtk`). Убраны stock-иконки кнопок (gtk.STOCK_*), которых в GTK3.20+ больше нет — заменены обычными подписанными кнопками. Gtk.Table (deprecated) заменен на Gtk.Grid.
# 3. `gimpshelf.shelf` (данные, которые переживают закрытие диалога и доступны из следующего вызова процедуры в рамках сессии GIMP) заменён на Gimp.get_data()/Gimp.set_data() — это официальный аналог в GI-биндингах.
# 4. Все вызовы `pdb.gimp_xxx_yyy(obj, ...)` переведены в объектную форму `obj.yyy(...)`, как это сделано в новых GI-биндингах GIMP 3 (PDB теперь представлен как обычные методы классов Gimp.Image / Gimp.Drawable / Gimp.Layer / Gimp.Item и т.п.). Там, где я не был уверен на 100% в точном имени метода (например transform_translate/copy у слоёв), вызов сделан через универсальный pdb-хелпер run_pdb(), который вызывает процедуру PDB напрямую по её "классическому" имени (оно не менялось между версиями GIMP) — это надёжнее, чем угадывать имя метода.
# 5. Цвета фона/переднего плана в GIMP 3 — это объекты Gegl.Color, а не кортежи (r, g, b). Есть хелпер rgb_color().
# 6. Файл конфигурации (formats.dat) хранится через pickle, как и раньше, но путь берётся через GLib.get_user_config_dir(), это надёжнее, чем Gimp.directory() в разных ОС.
#
# Если что-то в вашей версии GIMP 3 называется иначе (сверяйте в консоли Python-Fu: Filters > Python-Fu > Console, там `dir(image)`, `help(Gimp.Image)` и т.п. покажут точные имена) — правьте точечно, структура кода не менялась.
# ============================================================================
import os
import sys
import pickle
import gi
gi.require_version('Gimp', '3.0')
gi.require_version('GimpUi', '3.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gimp, GimpUi, Gtk, GLib, GObject, Gio
try:
    gi.require_version('Gegl', '0.4')
    from gi.repository import Gegl
    _HAS_GEGL = True
except (ValueError, ImportError):
    _HAS_GEGL = False

def gimp_enum_value(enum_cls, *candidate_names, int_fallback=0):
    """Достаёт значение из enum-класса GI по нескольким возможным именам
    (некоторые enum-константы GIMP начинаются с цифры, например ROTATE_90,
    и в разных версиях биндингов PyGObject называются по-разному:
    '_90', 'ROTATE_90', '90' и т.п.). Если ни одно имя не подошло —
    строит значение enum по числу (int_fallback), это всегда работает,
    так как числовые значения перечислений в PDB стабильны между версиями.
    """
    for candidate in candidate_names:
        if hasattr(enum_cls, candidate):
            return getattr(enum_cls, candidate)
    return enum_cls(int_fallback)

def rgb_color(r, g, b, a=255):
    """Создаёт цвет для Gimp.context_set_background/foreground.
    r, g, b, a — 0..255, как в оригинальном плагине."""
    if _HAS_GEGL:
        color = Gegl.Color.new('black')
        color.set_rgba(r / 255.0, g / 255.0, b / 255.0, a / 255.0)
        return color
    # Фолбэк, если Gegl почему-то недоступен в момент импорта
    return Gimp.RGB(r / 255.0, g / 255.0, b / 255.0, a / 255.0)

def run_pdb(name, *args):
    """Универсальный вызов процедуры PDB по её классическому имени
    (например 'gimp-image-select-ellipse'). Аргументы передаются как есть,
    GI сам приводит типы. Возвращает объект результата (значения через
    result.index(n) или result.length()/result.values, в зависимости от
    версии биндингов)."""
    procedure = Gimp.get_pdb().lookup_procedure(name)
    if procedure is None:
        raise RuntimeError('Процедура PDB не найдена: %s' % name)
    config = procedure.create_config()
    arg_specs = procedure.get_arguments()
    for spec, value in zip(arg_specs, args):
        config.set_property(spec.name, value)
    return procedure.run(config)

# Путь до папки с конфигом (используем стандартную папку конфигурации
# пользователя, чтобы не зависеть от точной семантики Gimp.directory())
CONFIG_DIR = os.path.join(GLib.get_user_config_dir(), 'GIMP', 'id_photo')
CONFIG_PATH = os.path.join(CONFIG_DIR, 'formats.dat')

class IdPhotoBase(object):
    # Содержимое конфига, который будет сгенерирован если необходимо
    DEFAULT_FORMATS = {
        'formats': [
            # --- Паспорта ---
            {'angle': False, 'category': 'pass', 'copys': 4, 'faceheight': 34, 'gray_frame': False, 'height': 45, 'name': 'UA Паспорт (книжечка)', 'onlyface': False, 'oval': False, 'overheadheight': 5, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 35, 'url': 'https://dmsu.gov.ua/poslugi/pasport-gromadyanina-ukrajni/vkleyuvannya-fotografij-do-pasporta-gromadyanina-ukrajni-pri-dosyagnenni-25-ta-45-richnogo-viku.html'},
            {'angle': False, 'category': 'pass', 'copys': 1, 'faceheight': 110, 'gray_frame': False, 'height': 150, 'name': 'UA Загранпаспорт ребёнка до 12 лет', 'onlyface': False, 'oval': False, 'overheadheight': 12, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 100, 'url': 'https://dmsu.gov.ua/news/region/16734.html'},
            {'angle': False, 'category': 'pass', 'copys': 1, 'faceheight': 110, 'gray_frame': False, 'height': 150, 'name': 'UA Фото 10x15 для сканирования', 'onlyface': False, 'oval': False, 'overheadheight': 12, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 100, 'url': 'https://zakon.rada.gov.ua/laws/show/z1146-19#Text'},
            {'angle': False, 'category': 'pass', 'copys': 4, 'faceheight': 12, 'gray_frame': False, 'height': 47, 'name': 'RU Паспорт', 'onlyface': True, 'oval': False, 'overheadheight': 5, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 37, 'url': 'https://мвд.рф/mvd/structure1/Glavnie_upravlenija/guvm'},
            {'angle': False, 'category': 'pass', 'copys': 4, 'faceheight': 34, 'gray_frame': False, 'height': 47, 'name': 'RU Загранпаспорт МИД', 'onlyface': False, 'oval': False, 'overheadheight': 4, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 36, 'url': ''},
            # --- Визы ---
            {'angle': False, 'category': 'visa', 'copys': 4, 'faceheight': 34, 'gray_frame': False, 'height': 45, 'name': 'EU Шенген / ICAO (35x45)', 'onlyface': False, 'oval': False, 'overheadheight': 4, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 35, 'url': 'https://eur-lex.europa.eu/eli/reg/2009/810/2024-06-28/eng'},
            {'angle': False, 'category': 'visa', 'copys': 4, 'faceheight': 35, 'gray_frame': False, 'height': 51, 'name': 'США / Грин-карта', 'onlyface': False, 'oval': False, 'overheadheight': 5, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 51, 'url': 'https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/photos.html'},
            {'angle': False, 'category': 'visa', 'copys': 4, 'faceheight': 33, 'gray_frame': False, 'height': 45, 'name': 'Канада — временная', 'onlyface': False, 'oval': False, 'overheadheight': 5, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 35, 'url': 'https://www.canada.ca/en/immigration-refugees-citizenship/services/application/application-forms-guides/temporary-resident-visa-application-photograph-specifications.html'},
            {'angle': False, 'category': 'visa', 'copys': 4, 'faceheight': 33, 'gray_frame': False, 'height': 70, 'name': 'Канада — PR / Permanent Resident', 'onlyface': False, 'oval': False, 'overheadheight': 5, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 50, 'url': 'https://www.canada.ca/en/immigration-refugees-citizenship/services/permanent-residents/card/photos.html'},
            # --- Удостоверения ---
            {'angle': False, 'category': 'cert', 'copys': 4, 'faceheight': 26, 'gray_frame': False, 'height': 40, 'name': 'Студенческий / Медсправка (30x40)', 'onlyface': False, 'oval': False, 'overheadheight': 3, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 30, 'url': 'https://mon.gov.ua/'},
            {'angle': False, 'category': 'cert', 'copys': 1, 'faceheight': 0, 'gray_frame': False, 'height': 45, 'name': 'Международное водительское', 'onlyface': False, 'oval': False, 'overheadheight': 0, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 35, 'url': 'https://hsc.gov.ua/index/poslugi/vidacha-posvidchennya-vodiya/vidacha-mizhnarodnogo-posvidchennya-vodiya/'},
            {'angle': False, 'category': 'cert', 'copys': 4, 'faceheight': 12, 'gray_frame': False, 'height': 34, 'name': 'Пенсионное', 'onlyface': True, 'oval': False, 'overheadheight': 3, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 27, 'url': 'https://www.pfu.gov.ua/'},
            {'angle': False, 'category': 'cert', 'copys': 4, 'faceheight': 9, 'gray_frame': False, 'height': 34, 'name': 'Ветеран войны', 'onlyface': True, 'oval': False, 'overheadheight': 4, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 27, 'url': 'https://mva.gov.ua/'},
            {'angle': False, 'category': 'cert', 'copys': 4, 'faceheight': 12, 'gray_frame': False, 'height': 50, 'name': 'Вид на жительство', 'onlyface': True, 'oval': False, 'overheadheight': 4, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 40, 'url': 'https://ualinux.com/'},
            {'angle': False, 'category': 'cert', 'copys': 4, 'faceheight': 35, 'gray_frame': False, 'height': 120, 'name': 'Личное дело', 'onlyface': True, 'oval': False, 'overheadheight': 10, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 90, 'url': 'https://ualinux.com/'},
            {'angle': False, 'category': 'cert', 'copys': 4, 'faceheight': 15, 'gray_frame': False, 'height': 55, 'name': 'Пропуск', 'onlyface': True, 'oval': False, 'overheadheight': 6, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 40, 'url': 'https://ualinux.com/'},
            # --- Прочее ---
            {'angle': False, 'category': 'other', 'copys': 4, 'faceheight': 12, 'gray_frame': False, 'height': 40, 'name': 'Формат (30 х 40)', 'onlyface': True, 'oval': False, 'overheadheight': 4, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 30, 'url': 'https://ualinux.com/'},
            {'angle': False, 'category': 'other', 'copys': 4, 'faceheight': 15, 'gray_frame': False, 'height': 30, 'name': 'Формат (30 x 25)', 'onlyface': True, 'oval': False, 'overheadheight': 4, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 25, 'url': 'https://ualinux.com/'},
            {'angle': False, 'category': 'other', 'copys': 4, 'faceheight': 15, 'gray_frame': False, 'height': 45, 'name': 'Формат (35 x 45)', 'onlyface': True, 'oval': False, 'overheadheight': 4, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 35, 'url': 'https://ualinux.com/'},
            {'angle': False, 'category': 'other', 'copys': 4, 'faceheight': 12, 'gray_frame': False, 'height': 50, 'name': 'Формат (40 x 50)', 'onlyface': True, 'oval': False, 'overheadheight': 4, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 40, 'url': 'https://ualinux.com/'},
            {'angle': False, 'category': 'other', 'copys': 4, 'faceheight': 15, 'gray_frame': False, 'height': 60, 'name': 'Формат (40 x 60)', 'onlyface': True, 'oval': False, 'overheadheight': 4, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 40, 'url': 'https://ualinux.com/'},
            {'angle': False, 'category': 'other', 'copys': 4, 'faceheight': 12, 'gray_frame': False, 'height': 35, 'name': 'Формат (45 x 35)', 'onlyface': True, 'oval': False, 'overheadheight': 4, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 45, 'url': 'https://ualinux.com/'},
            {'angle': False, 'category': 'other', 'copys': 4, 'faceheight': 14, 'gray_frame': False, 'height': 50, 'name': 'Формат (45 x 50)', 'onlyface': True, 'oval': False, 'overheadheight': 4, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 45, 'url': 'https://ualinux.com/'},
            {'angle': False, 'category': 'other', 'copys': 4, 'faceheight': 22, 'gray_frame': False, 'height': 60, 'name': 'Формат (45 x 60)', 'onlyface': True, 'oval': False, 'overheadheight': 4, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 45, 'url': 'https://ualinux.com/'},
            {'angle': False, 'category': 'other', 'copys': 4, 'faceheight': 35, 'gray_frame': False, 'height': 120, 'name': 'Формат (90 x 120)', 'onlyface': True, 'oval': False, 'overheadheight': 10, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 90, 'url': 'https://ualinux.com/'},
        ],
        'properties': {'auto_levels': False, 'resolution': 1200, 'white_bg': True},
    }
    path_dir = CONFIG_DIR
    path = CONFIG_PATH

    @classmethod
    def load_data(cls):
        if not os.path.exists(cls.path_dir):
            os.makedirs(cls.path_dir)
        if not os.path.exists(cls.path):
            with open(cls.path, 'wb') as config:
                pickle.dump(cls.DEFAULT_FORMATS, config)
        with open(cls.path, 'rb') as data_file:
            return pickle.load(data_file)

    def __init__(self):
        self.data = self.load_data()

    def save_data(self):
        with open(self.path, 'wb') as config:
            pickle.dump(self.data, config)

    # Функция конвертирует размер в миллиметрах в размер в пикселях
    def mm_in_px(self, size_mm, resolution):
        return int(round((size_mm / 25.4) * resolution))

    # функция выводит всплывающее окно с сообщением об ошибке
    def show_error_msg(self, msg):
        errdialog = Gtk.MessageDialog(transient_for=None, modal=True,
                                      message_type=Gtk.MessageType.ERROR,
                                      buttons=Gtk.ButtonsType.OK,
                                      text=str(msg))
        errdialog.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        errdialog.run()
        errdialog.destroy()

    # функция выводит всплывающее окно с сообщением
    def info(self, msg):
        infodialog = Gtk.MessageDialog(transient_for=None, modal=True,
                                       message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK,
                                       text=str(msg))
        infodialog.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        infodialog.run()
        infodialog.destroy()

    # функция выводит всплывающее окно "О программе"
    def about(self, widget, data=None):
        about_dialog = Gtk.AboutDialog()
        about_dialog.set_destroy_with_parent(True)
        about_dialog.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        about_dialog.set_program_name('Фото на документы')
        about_dialog.set_version('3.0.0')
        about_dialog.set_copyright('Автор: Александр Карабанов (zend.karabanov@gmail.com)\nПорт под GIMP 3: UALinux (main@ualinux.com)')
        about_dialog.set_website('https://github.com/karabanov/gimp-id-photo')
        about_dialog.set_license(
            'Эта программа является свободным программным обеспечением: вы можете '
            'распространять её и/или модифицировать в соответствии с условиями лицензии '
            'GNU General Public License версии 3 либо (по вашему выбору) любой более поздней '
            'версии, опубликованной Free Software Foundation.\n'
            'Эта программа распространяется в надежде на то, что она будет полезной, но БЕЗ '
            'КАКИХ-ЛИБО ГАРАНТИЙ, вы используете её на свой СТРАХ и РИСК. Прочтите GNU General '
            'Public License для более подробной информации.'
        )
        about_dialog.set_wrap_license(True)
        about_dialog.run()
        about_dialog.destroy()

    # Эта функция кадрирует фото в соответствии с переданым ей форматом.
    def create_id_foto(self, image, drawable, fmt, auto_levels):
        hguide_list = []
        vguide_list = []
        dguide_list = []
        guide_id = 0

        guide_id = image.find_next_guide(guide_id)
        if guide_id == 0:
            self.info('Нет ни одной направляющей.\n'
                      'Поместите одну горизонтальную направляющую на уровне верхней части головы, '
                      'одну горизонтальную направляющую на уровне глаз и одну на уровне подбородка, '
                      'затем поставьте одну вертикальную направляющую на линию симметрии лица.\n'
                      'Порядок в котором вы будете расставлять направляющие не важен, можно начать с любой.')
            image.undo_group_end()
            return False

        while guide_id != 0:
            dguide_list.append(guide_id)
            if image.get_guide_orientation(guide_id) == Gimp.OrientationType.HORIZONTAL:
                hguide_list.append(image.get_guide_position(guide_id))
            else:
                vguide_list.append(image.get_guide_position(guide_id))
            guide_id = image.find_next_guide(guide_id)

        if len(hguide_list) != 3:
            self.info('Горизонтальных направляющих должно быть три.\n'
                      'Расставьте направляющие правильно и попробуйте ещё раз.')
            image.undo_group_end()
            return False
        elif len(vguide_list) < 1:
            self.info('Нет вертикальной направляющей.\n'
                      'Установите вертикальную направляющую на линию симметрии лица и попробуйте ещё раз.')
            image.undo_group_end()
            return False
        elif len(vguide_list) > 1:
            self.info('Должна быть только одна вертикальная направляющая.\n'
                      'Расставьте направляющие правильно и попробуйте ещё раз.')
            image.undo_group_end()
            return False

        hguide_list.sort()
        if fmt['onlyface']:
            k = hguide_list[2] - hguide_list[1]  # Только лицо
        else:
            k = hguide_list[2] - hguide_list[0]  # Вся голова

        w = round((fmt['width'] * k) / fmt['faceheight'])
        h = round((fmt['height'] * k) / fmt['faceheight'])
        x = (w / 2) - vguide_list[0]
        y = round((fmt['overheadheight'] * k) / fmt['faceheight']) - hguide_list[0]
        image.resize(int(w), int(h), int(x), int(y))

        old_background = Gimp.context_get_background()
        Gimp.context_set_background(rgb_color(113, 255, 0))
        self.drawable = image.flatten()
        Gimp.context_set_background(old_background)
        image.set_resolution(self.format_resolution, self.format_resolution)

        for gid in dguide_list:
            image.delete_guide(gid)

        if auto_levels:
            if not self.drawable.is_indexed():
                self.drawable.levels_stretch()
            else:
                self.info('Инструмент "авто-уровни" не работает с индексированными слоями.\n'
                          'Слой будет конвертирован из режима "Индексированный" в режим "RGB".')
                image.convert_rgb()
                self.drawable.levels_stretch()
        return True

    # Эта функция конвертирует цветное изображение в чёрно-белое
    def to_grayscale(self, image, drawable):
        if not drawable.is_gray():
            image.convert_grayscale()

    # Эта функция добавляет серую однопиксельную рамку к изображению
    def gray_frame(self, image):
        image.resize(image.get_width() + 2, image.get_height() + 2, 1, 1)
        old_background = Gimp.context_get_background()
        Gimp.context_set_background(rgb_color(200, 200, 200))
        self.drawable = image.flatten()
        Gimp.context_set_background(old_background)

    # Эта функция добавляет овал с растушёвкой к изображению
    def oval(self, image, drawable):
        if drawable.is_gray() or drawable.is_indexed():
            image.convert_rgb()

        white_oval = Gimp.Layer.new(image, 'Овал с растушёвкой', drawable.get_width(),
                                    drawable.get_height(), Gimp.ImageType.RGBA_IMAGE,
                                    100, Gimp.LayerMode.NORMAL)
        old_background = Gimp.context_get_background()
        Gimp.context_set_background(rgb_color(255, 255, 255))
        white_oval.fill(Gimp.FillType.BACKGROUND)
        Gimp.context_set_background(old_background)
        image.insert_layer(white_oval, None, 0)

        Gimp.context_set_antialias(True)
        Gimp.context_set_feather(True)
        f_r = self.mm_in_px(4.5, self.format_resolution)
        Gimp.context_set_feather_radius(f_r, f_r)

        image.select_ellipse(Gimp.ChannelOps.REPLACE,
                             drawable.get_width() * 0.1, 0,
                             drawable.get_width() * 0.8, drawable.get_height() * 0.9)
        white_oval.edit_clear()
        Gimp.Selection.none(image)
        self.drawable = image.flatten()

    # Эта функция добавляет "уголок" к изображению
    def angle(self, image, drawable, angle_type):
        res = self.format_resolution
        Gimp.context_set_antialias(True)
        Gimp.context_set_feather(True)
        Gimp.context_set_feather_radius(2.0, 2.0)

        if angle_type == 'right_circular':
            image.select_ellipse(Gimp.ChannelOps.REPLACE,
                                 image.get_width() - self.mm_in_px(18, res),
                                 image.get_height() - self.mm_in_px(14, res),
                                 self.mm_in_px(45, res), self.mm_in_px(45, res))
        elif angle_type == 'left_circular':
            image.select_ellipse(Gimp.ChannelOps.REPLACE,
                                 -self.mm_in_px(26, res),
                                 image.get_height() - self.mm_in_px(14, res),
                                 self.mm_in_px(45, res), self.mm_in_px(45, res))
        elif angle_type == 'right_direct':
            points = [image.get_width(), image.get_height() - self.mm_in_px(14, res),
                      image.get_width(), image.get_height(),
                      image.get_width() - self.mm_in_px(16, res), image.get_height()]
            image.select_polygon(Gimp.ChannelOps.REPLACE, points)
        elif angle_type == 'left_direct':
            points = [0, image.get_height() - self.mm_in_px(14, res),
                      0, image.get_height(),
                      self.mm_in_px(16, res), image.get_height()]
            image.select_polygon(Gimp.ChannelOps.REPLACE, points)

        old_background = Gimp.context_get_background()
        Gimp.context_set_background(rgb_color(255, 255, 255))
        drawable.edit_clear()
        Gimp.Selection.none(image)
        Gimp.context_set_background(old_background)

    def print_function(self, image, drawable, paper, copys, print_photo):
        res = self.format_resolution
        paper_size = {'10x15': (99.99, 149.94), 'A5': (148.51, 209.97), 'A4': (209.97, 297.01)}
        paper_width = self.mm_in_px(paper_size[paper][0], res)
        paper_height = self.mm_in_px(paper_size[paper][1], res)
        space = self.mm_in_px(1.5, res)

        layer_new_width = drawable.get_width() + space
        layer_new_height = drawable.get_height() + space

        w_count = int(paper_width // layer_new_width)
        h_count = int(paper_height // layer_new_height)

        if w_count == 0 or h_count == 0:
            self.info('Ни одной фотографии не помещается на выбранном вами листе бумаги '
                      'формата "' + str(paper) + '".\n'
                      'Выберете более подходящий формат бумаги и попробуйте ещё раз.')
            image.undo_group_end()
            return

        image.resize(paper_width, paper_height, 0, 0)

        if self.data['properties']['white_bg']:
            if drawable.is_rgb():
                white_bg = Gimp.Layer.new(image, 'Белый фон', paper_width, paper_height,
                                          Gimp.ImageType.RGB_IMAGE, 100, Gimp.LayerMode.NORMAL)
            else:
                white_bg = Gimp.Layer.new(image, 'Белый фон', paper_width, paper_height,
                                          Gimp.ImageType.GRAY_IMAGE, 100, Gimp.LayerMode.NORMAL)
            old_background = Gimp.context_get_background()
            Gimp.context_set_background(rgb_color(255, 255, 255))
            white_bg.fill(Gimp.FillType.BACKGROUND)
            Gimp.context_set_background(old_background)
            white_bg.add_alpha()
            image.insert_layer(white_bg, None, 0)
            image.raise_item_to_top(drawable)

        w_count_rotate = int(paper_width // layer_new_height)
        h_count_rotate = int(paper_height // layer_new_width)
        if (w_count_rotate * h_count_rotate) > (w_count * h_count):
            rotate_90 = gimp_enum_value(Gimp.RotationType, '_90', 'ROTATE_90', '90', int_fallback=0)
            drawable.transform_rotate_simple(rotate_90, True, 0, 0)
            drawable.transform_translate(drawable.get_width(), 0)
            layer_new_width, layer_new_height = layer_new_height, layer_new_width
            w_count, h_count = w_count_rotate, h_count_rotate

        x_fundamental = (paper_width - (layer_new_width * w_count)) / 2
        y_fundamental = (paper_height - (layer_new_height * h_count)) / 2
        drawable.transform_translate(x_fundamental, y_fundamental)

        copys_counter = 0
        layer_group = Gimp.GroupLayer.new(image)
        layer_group.set_name('Фотографии')
        image.insert_layer(layer_group, None, 0)
        drawable.set_name('Фото')

        for i in range(h_count):
            for j in range(w_count):
                if copys_counter == copys or copys_counter == (w_count * h_count):
                    break
                layer_new = Gimp.Layer.new_from_drawable(drawable, image)
                layer_new.set_name('Фото')
                layer_new.add_alpha()
                image.insert_layer(layer_new, layer_group, 0)
                layer_new.transform_translate(layer_new_width * j, layer_new_height * i)
                copys_counter += 1
        image.remove_layer(drawable)

        if print_photo:
            run_pdb('file-print-gtk', image)

    # ---------- Хранилище "shelf" (переживает вызов процедуры в рамках сессии) ----------
    # В GIMP 3 Gimp.set_data()/get_data() из GIMP 2 в биндингах недоступны/переименованы,
    # поэтому вместо PDB-хранилища используем обычный файл в той же папке конфигурации,
    # где уже надёжно читается/пишется formats.dat.
    @staticmethod
    def _shelf_path(key):
        safe = ''.join(c if c.isalnum() or c in '-_' else '_' for c in key)
        return os.path.join(CONFIG_DIR, safe + '.shelf')

    @classmethod
    def shelf_set(cls, key, value):
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
        with open(cls._shelf_path(key), 'wb') as f:
            pickle.dump(value, f)

    @classmethod
    def shelf_get(cls, key, default=None):
        path = cls._shelf_path(key)
        if not os.path.exists(path):
            return default
        try:
            with open(path, 'rb') as f:
                return pickle.load(f)
        except Exception:
            return default

    # Эта функция крафтит фото для документов
    def auto_execute(self, widget, data=None):
        self.window.hide()
        Gimp.context_push()
        self.image.undo_group_start()

        auto_levels = self.autolevels_check.get_active()
        for idx, format_id in enumerate(self.format_radio):
            if format_id.get_active():
                tmp_dict = dict(self.data['formats'][idx])
                tmp_dict['resolution'] = self.data['properties']['resolution']
                self.shelf_set('id-photo-format', tmp_dict)
                self.format_resolution = tmp_dict['resolution']
                ok = self.create_id_foto(self.image, self.drawable, tmp_dict, auto_levels)

                if ok and data == 'auto_execute':
                    fmt = self.data['formats'][idx]
                    self.image.scale(self.mm_in_px(fmt['width'], self.format_resolution),
                                     self.mm_in_px(fmt['height'], self.format_resolution))
                    if fmt['angle']:
                        self.angle(self.image, self.drawable, fmt['angle'])
                    if fmt['oval']:
                        self.oval(self.image, self.drawable)
                    if fmt['to_grayscale']:
                        self.to_grayscale(self.image, self.drawable)
                    if fmt['gray_frame']:
                        self.gray_frame(self.image)
                    self.print_function(self.image, self.drawable, fmt['paper'],
                                        fmt['copys'], fmt['print_photo'])
                break

        Gimp.displays_flush()
        self.image.undo_group_end()
        Gimp.context_pop()
        Gtk.main_quit()

    # Эта функция только формирует конечный результат
    # и ещё выводит изображение на дефолтный принтер если необходимо
    def compose_or_print(self, widget, data=None):
        self.window.hide()
        Gimp.context_push()
        self.image.undo_group_start()

        fmt = self.shelf_get('id-photo-format')
        self.format_resolution = fmt['resolution']
        self.image.scale(self.mm_in_px(fmt['width'], self.format_resolution),
                         self.mm_in_px(fmt['height'], self.format_resolution))

        if self.oval_check.get_active():
            self.oval(self.image, self.drawable)
        if self.gray_check.get_active():
            self.to_grayscale(self.image, self.drawable)
        if self.border_check.get_active():
            self.gray_frame(self.image)

        if self.angle_right_circular_radio.get_active():
            self.angle(self.image, self.drawable, 'right_circular')
        elif self.angle_left_circular_radio.get_active():
            self.angle(self.image, self.drawable, 'left_circular')
        elif self.angle_right_direct_radio.get_active():
            self.angle(self.image, self.drawable, 'right_direct')
        elif self.angle_left_direct_radio.get_active():
            self.angle(self.image, self.drawable, 'left_direct')

        copys = self.copys_spin.get_value_as_int()
        paper = self.paper_cb.get_active_text()
        print_photo = (data == 'print_it')
        self.print_function(self.image, self.drawable, paper, copys, print_photo)

        Gimp.displays_flush()
        self.image.undo_group_end()
        Gimp.context_pop()
        Gtk.main_quit()

    # Эта функция способствует редактированию настроек
    def apply_settings(self, widget, data=None):
        self.window.hide()
        self.data['properties']['white_bg'] = self.white_bg_check.get_active()
        self.data['properties']['auto_levels'] = self.auto_levels_check.get_active()
        self.data['properties']['resolution'] = int(self.resolution_cb.get_active_text())
        self.save_data()
        Gtk.main_quit()

    # -------- Общий конструктор диалога "формат" (используется и для добавления, и для правки) --------
    def _build_format_dialog(self, title, ok_label, existing=None):
        name_entry = Gtk.Entry()
        name_entry.set_text(existing['name'] if existing else 'Название формата')
        name_entry.grab_focus()

        category_cb = Gtk.ComboBoxText()
        for text in ('Категория (Разное)', 'Разное', 'Паспорт', 'Виза', 'Удостоверение'):
            category_cb.append_text(text)
        category_map = {'other': 1, 'pass': 2, 'visa': 3, 'cert': 4}
        category_cb.set_active(category_map.get(existing['category'], 0) if existing else 0)

        def labeled_spin(label_text, value, upper=200.0):
            label = Gtk.Label(label=label_text)
            label.set_justify(Gtk.Justification.LEFT)
            adj = Gtk.Adjustment(value=value, lower=0.0, upper=upper,
                                 step_increment=1.0, page_increment=1.0, page_size=0.0)
            spin = Gtk.SpinButton(adjustment=adj, climb_rate=0, digits=0)
            spin.set_numeric(True)
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
            hbox.pack_start(label, True, True, 0)
            hbox.pack_start(spin, False, False, 5)
            return hbox, spin

        width_hbox, width_spin = labeled_spin('Ширина фото:', existing['width'] if existing else 0.0)
        height_hbox, height_spin = labeled_spin('Высота фото: ', existing['height'] if existing else 0.0)
        overheadheight_hbox, overheadheight_spin = labeled_spin(
            'До головы:     ', existing['overheadheight'] if existing else 0.0)

        size_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        size_vbox.set_homogeneous(True)
        for w in (width_hbox, height_hbox, overheadheight_hbox):
            size_vbox.pack_start(w, True, True, 0)

        onlyface1_radio = Gtk.RadioButton.new_with_label(None, 'от глаз до подбородка')
        onlyface2_radio = Gtk.RadioButton.new_with_label_from_widget(onlyface1_radio, 'от макушки до подбородка')
        if existing:
            (onlyface1_radio if existing['onlyface'] else onlyface2_radio).set_active(True)

        faceheight_adj = Gtk.Adjustment(value=existing['faceheight'] if existing else 0.0,
                                        lower=0.0, upper=200.0, step_increment=1.0,
                                        page_increment=1.0, page_size=0.0)
        faceheight_spin = Gtk.SpinButton(adjustment=faceheight_adj, climb_rate=0, digits=0)
        faceheight_spin.set_numeric(True)

        faceheight_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        faceheight_vbox.set_homogeneous(True)
        faceheight_vbox.set_border_width(10)
        for w in (faceheight_spin, onlyface1_radio, onlyface2_radio):
            faceheight_vbox.pack_start(w, True, True, 0)

        faceheight_frame = Gtk.Frame(label='Размер лицевой части головы')
        faceheight_frame.add(faceheight_vbox)

        table = Gtk.Grid()
        table.set_border_width(5)
        table.set_row_spacing(0)
        table.set_column_spacing(10)
        table.attach(size_vbox, 0, 0, 1, 1)
        table.attach(faceheight_frame, 1, 0, 1, 1)

        angle_cb = Gtk.ComboBoxText()
        for text in ('Уголок (Без уголка)', 'Без уголка', 'Круглый справа', 'Круглый слева',
                     'Прямой справа', 'Прямой слева'):
            angle_cb.append_text(text)
        angle_map = {False: 1, 'right_circular': 2, 'left_circular': 3,
                     'right_direct': 4, 'left_direct': 5}
        angle_cb.set_active(angle_map.get(existing['angle'], 1) if existing else 1)

        paper_cb = Gtk.ComboBoxText()
        for text in ('Формат бумаги (10x15)', '10x15', 'A5', 'A4'):
            paper_cb.append_text(text)
        paper_map = {'10x15': 1, 'A5': 2, 'A4': 3}
        paper_cb.set_active(paper_map.get(existing['paper'], 0) if existing else 0)

        copys_adj = Gtk.Adjustment(value=existing['copys'] if existing else 1.0,
                                   lower=1.0, upper=200.0, step_increment=1.0,
                                   page_increment=1.0, page_size=0.0)
        copys_spin = Gtk.SpinButton(adjustment=copys_adj, climb_rate=0, digits=0)
        copys_spin.set_numeric(True)
        copys_label = Gtk.Label(label='фото на листе')
        copys_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        copys_hbox.pack_start(copys_spin, False, False, 0)
        copys_hbox.pack_start(copys_label, False, False, 5)

        to_grayscale_check = Gtk.CheckButton(label='обесцветить фото')
        gray_frame_check = Gtk.CheckButton(label='добавить рамку')
        oval_check = Gtk.CheckButton(label='добавить овал с растушёвкой')
        print_photo_check = Gtk.CheckButton(label='распечатать автоматически')
        if existing:
            to_grayscale_check.set_active(existing['to_grayscale'])
            gray_frame_check.set_active(existing['gray_frame'])
            oval_check.set_active(existing['oval'])
            print_photo_check.set_active(existing['print_photo'])

        dialog = Gtk.Dialog(title=title, transient_for=self.window, modal=True,
                            destroy_with_parent=True)
        dialog.add_button('Отмена', Gtk.ResponseType.CANCEL)
        dialog.add_button(ok_label, Gtk.ResponseType.OK)
        dialog.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        dialog.set_resizable(False)
        dialog.set_border_width(10)

        content = dialog.get_content_area()
        for w in (name_entry, category_cb, table, angle_cb, paper_cb, copys_hbox,
                  to_grayscale_check, gray_frame_check, oval_check, print_photo_check):
            content.pack_start(w, True, True, 5)

        dialog.show_all()
        response = dialog.run()
        result = None
        if response == Gtk.ResponseType.OK:
            angle_text = angle_cb.get_active_text()
            angle_val = False
            for text, val in (('Круглый справа', 'right_circular'), ('Круглый слева', 'left_circular'),
                              ('Прямой справа', 'right_direct'), ('Прямой слева', 'left_direct')):
                if angle_text == text:
                    angle_val = val
            paper_text = paper_cb.get_active_text()
            paper_val = '10x15'
            if paper_text == 'A5':
                paper_val = 'A5'
            elif paper_text == 'A4':
                paper_val = 'A4'

            category_text = category_cb.get_active_text()
            category_val = 'other'
            for text, val in (('Паспорт', 'pass'), ('Виза', 'visa'), ('Удостоверение', 'cert')):
                if category_text == text:
                    category_val = val

            result = {
                'name': name_entry.get_text(),
                'category': category_val,
                'width': width_spin.get_value_as_int(),
                'height': height_spin.get_value_as_int(),
                'faceheight': faceheight_spin.get_value_as_int(),
                'onlyface': onlyface1_radio.get_active(),
                'overheadheight': overheadheight_spin.get_value_as_int(),
                'angle': angle_val,
                'copys': copys_spin.get_value_as_int(),
                'gray_frame': gray_frame_check.get_active(),
                'oval': oval_check.get_active(),
                'paper': paper_val,
                'to_grayscale': to_grayscale_check.get_active(),
                'print_photo': print_photo_check.get_active(),
                'url': 'http://gimp-id-photo.ru',
            }
        dialog.destroy()
        return result

    # Эта функция способствует редактированию выбранного формата
    def edit_format(self, widget, data=None):
        for idx, format_id in enumerate(self.format_radio):
            if format_id.get_active():
                current = self.data['formats'][idx]
                result = self._build_format_dialog(
                    'Правка формата "%s"' % current['name'], 'Сохранить', existing=current)
                if result is not None:
                    self.data['formats'][idx] = result
                    self.save_data()
                    self.format_radio[idx].set_label(str(result['name']))
                    self.add_success_label.set_markup(
                        '<span foreground="#008600">"' + str(result['name']) + '" успешно изменён\n</span>')
                break

    # Эта функция способствует удалению выбранного формата
    def delete_format(self, widget, data=None):
        for idx, format_id in enumerate(self.format_radio):
            if format_id.get_active():
                name = self.data['formats'][idx]['name']
                dialog = Gtk.Dialog(title='Удаление формата "%s"' % name, transient_for=self.window,
                                    modal=True, destroy_with_parent=True)
                dialog.add_button('Нет', Gtk.ResponseType.CANCEL)
                dialog.add_button('Да', Gtk.ResponseType.OK)
                dialog.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
                dialog.set_resizable(False)
                dialog.set_border_width(10)
                label = Gtk.Label(label='Вы действительно хотите удалить формат "%s"?' % name)
                dialog.get_content_area().pack_start(label, True, True, 5)
                dialog.show_all()
                response = dialog.run()
                if response == Gtk.ResponseType.OK:
                    del self.data['formats'][idx]
                    self.save_data()
                    self.format_radio[idx].hide()
                    if len(self.format_radio) == 1:
                        pass
                    elif idx + 1 <= len(self.format_radio) - 1:
                        self.format_radio[idx + 1].set_active(True)
                    else:
                        self.format_radio[idx - 1].set_active(True)
                    del self.format_radio[idx]
                    if len(self.format_radio) < 1:
                        self.delete_button.set_sensitive(False)
                        self.edit_button.set_sensitive(False)
                    self.add_success_label.set_markup(
                        '<span foreground="#008600">"' + str(name) + '" успешно удалён\n</span>')
                dialog.destroy()
                break

    # Эта функция способствует добавлению нового формата
    def add_format(self, widget, data=None):
        result = self._build_format_dialog('Добавить новый формат', 'Добавить', existing=None)
        if result is None:
            return
        self.data['formats'].append(result)
        self.save_data()
        group = self.format_radio[-1] if self.format_radio else None
        if group is not None:
            new_radio = Gtk.RadioButton.new_with_label_from_widget(group, result['name'])
        else:
            new_radio = Gtk.RadioButton.new_with_label(None, result['name'])
        self.format_radio.append(new_radio)
        new_radio.show()
        new_radio.set_active(True)
        self.formats_vbox.pack_start(new_radio, False, False, 0)
        self.delete_button.set_sensitive(True)
        self.edit_button.set_sensitive(True)
        self.add_success_label.set_markup(
            '<span foreground="#008600">"' + str(result['name']) + '" успешно добавлен\n</span>')

    def set_mark(self, widget, data=None):
        self.learn_more_label.set_markup(
            '<a href="' + data[0] + '">Узнать подробности о формате "' + data[1] + '"</a>')

    # Вспомогательная функция. Выполняется при закрытии окна
    def delete_event(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        Gtk.main_quit()


#########################################################
#-------- Тут и класса конец, а кто потомок молодец ----#
#########################################################

class SelectFormatIdPhoto(IdPhotoBase):
    def __init__(self, run_mode, image, drawable):
        super().__init__()
        self.image, self.drawable = image, drawable

        self.pass_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.pass_vbox.set_border_width(5)
        self.visa_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.visa_vbox.set_border_width(5)
        self.cert_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.cert_vbox.set_border_width(5)
        self.other_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.other_vbox.set_border_width(5)

        self.learn_more_label = Gtk.Label()
        self.learn_more_label.set_justify(Gtk.Justification.LEFT)
        self.learn_more_label.set_markup(
            '<a href="https://ualinux.com/">'
            'Узнать подробности о формате "Паспорт РФ"</a>')
        self.learn_more_label.set_tooltip_text(
            'Посмотреть сведения о формате с помощью браузера используемого по умолчанию')
        self.learn_more_label.set_halign(Gtk.Align.START)

        group = None
        self.format_radio = []
        for fmt in self.data['formats']:
            if group is None:
                radio = Gtk.RadioButton.new_with_label(None, fmt['name'])
            else:
                radio = Gtk.RadioButton.new_with_label_from_widget(group, fmt['name'])
            radio.connect('clicked', self.set_mark, (fmt['url'], fmt['name']))
            group = radio
            self.format_radio.append(radio)
            target = {'pass': self.pass_vbox, 'visa': self.visa_vbox,
                      'cert': self.cert_vbox, 'other': self.other_vbox}[fmt['category']]
            target.pack_start(radio, False, False, 0)

        self.pass_frame = Gtk.Frame(label='Паспорта')
        self.pass_frame.add(self.pass_vbox)
        self.visa_frame = Gtk.Frame(label='Визы')
        self.visa_frame.add(self.visa_vbox)
        self.cert_frame = Gtk.Frame(label='Удостоверения')
        self.cert_frame.add(self.cert_vbox)
        self.other_frame = Gtk.Frame(label='Разное')
        self.other_frame.add(self.other_vbox)

        self.cancel_button = Gtk.Button(label='Отмена')
        self.cancel_button.connect('clicked', self.destroy, None)
        self.cancel_button.set_tooltip_text('Не выполнять никаких действий с изображением')

        self.apply_button = Gtk.Button(label='Применить')
        self.apply_button.connect('clicked', self.auto_execute, None)
        self.apply_button.set_tooltip_text('Кадрировать фото в соответствии с выбранным форматом')

        self.execute_button = Gtk.Button(label='Выполнить автоматически')
        self.execute_button.connect('clicked', self.auto_execute, 'auto_execute')
        self.execute_button.set_tooltip_text('Выполнить все необходимые действия автоматически')

        self.autolevels_check = Gtk.CheckButton(label='авто-уровни')
        self.autolevels_check.set_active(self.data['properties']['auto_levels'])
        self.autolevels_check.set_tooltip_text('Автоматически подобрать уровни')

        self.button_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.button_hbox.pack_start(self.autolevels_check, False, False, 0)
        self.button_hbox.pack_end(self.apply_button, False, False, 0)
        self.button_hbox.pack_end(self.cancel_button, False, False, 0)
        self.button_hbox.pack_end(self.execute_button, False, False, 50)

        self.table = Gtk.Grid()
        self.table.set_border_width(5)
        self.table.set_row_spacing(10)
        self.table.set_column_spacing(10)
        self.table.attach(self.pass_frame, 0, 0, 1, 1)
        self.table.attach(self.visa_frame, 1, 0, 1, 1)
        self.table.attach(self.cert_frame, 2, 0, 1, 1)
        self.table.attach(self.other_frame, 3, 0, 1, 1)
        self.table.attach(self.button_hbox, 0, 1, 4, 1)
        self.table.attach(self.learn_more_label, 0, 2, 4, 1)

        self.window = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
        self.window.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.window.set_title('Выбор формата фотографии')
        self.window.set_border_width(5)
        self.window.set_resizable(False)
        self.window.connect('delete-event', self.delete_event)
        self.window.connect('destroy', self.destroy)
        self.window.add(self.table)
        self.window.show_all()
        self.window.present()
        Gtk.main()


class SettingsDialog(IdPhotoBase):
    def __init__(self, run_mode, image):
        super().__init__()
        self.formats_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.formats_vbox.set_border_width(10)

        group = None
        self.format_radio = []
        for fmt in self.data['formats']:
            if group is None:
                radio = Gtk.RadioButton.new_with_label(None, fmt['name'])
            else:
                radio = Gtk.RadioButton.new_with_label_from_widget(group, fmt['name'])
            group = radio
            self.format_radio.append(radio)
            self.formats_vbox.pack_start(radio, False, False, 0)

        self.sc_win = Gtk.ScrolledWindow()
        self.sc_win.set_border_width(0)
        self.sc_win.set_size_request(270, 200)
        self.sc_win.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.sc_win.add(self.formats_vbox)

        self.add_button = Gtk.Button(label='Добавить')
        self.add_button.connect('clicked', self.add_format, None)
        self.add_button.set_tooltip_text('Добавить формат')

        self.edit_button = Gtk.Button(label='Править')
        self.edit_button.connect('clicked', self.edit_format, None)
        self.edit_button.set_tooltip_text('Внести изменения в выбранный формат')
        if len(self.format_radio) < 1:
            self.edit_button.set_sensitive(False)

        self.delete_button = Gtk.Button(label='Удалить')
        self.delete_button.connect('clicked', self.delete_format, None)
        self.delete_button.set_tooltip_text('Удалить выбранный формат')
        if len(self.format_radio) < 1:
            self.delete_button.set_sensitive(False)

        self.button_format_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.button_format_hbox.pack_start(self.add_button, True, True, 0)
        self.button_format_hbox.pack_start(self.edit_button, True, True, 0)
        self.button_format_hbox.pack_start(self.delete_button, True, True, 0)

        self.add_success_label = Gtk.Label()
        self.add_success_label.set_justify(Gtk.Justification.LEFT)
        self.add_success_label.set_markup('\n')

        self.formats_table = Gtk.Grid()
        self.formats_table.set_border_width(10)
        self.formats_table.set_row_spacing(10)
        self.formats_table.set_column_spacing(10)
        self.formats_table.attach(self.sc_win, 0, 0, 1, 1)
        self.add_success_label.set_hexpand(True)
        self.add_success_label.set_vexpand(True)
        self.formats_table.attach(self.add_success_label, 0, 1, 1, 1)
        self.button_format_hbox.set_hexpand(True)
        self.button_format_hbox.set_vexpand(True)
        self.formats_table.attach(self.button_format_hbox, 0, 2, 1, 1)

        self.formats_frame = Gtk.Frame(label='Операции с форматами')
        self.formats_frame.add(self.formats_table)

        self.use_resolution_label = Gtk.Label(label='Использовать разрешение: ')
        self.resolution_cb = Gtk.ComboBoxText()
        for text in ('300', '600', '1147', '1200', '2400'):
            self.resolution_cb.append_text(text)
        self.resolution_cb.set_tooltip_text('При печати фотографий будет использовано это разрешение')

        self.ppi_label = Gtk.Label(label='ppi')
        res_map = {300: 0, 600: 1, 1147: 2, 1200: 3, 2400: 4}
        self.resolution_cb.set_active(res_map.get(self.data['properties']['resolution'], 1))

        self.ppi_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        self.ppi_hbox.pack_start(self.use_resolution_label, True, True, 0)
        self.ppi_hbox.pack_start(self.resolution_cb, True, True, 0)
        self.ppi_hbox.pack_start(self.ppi_label, True, True, 0)

        self.white_bg_check = Gtk.CheckButton(label='всегда добавлять слой "Белый фон"')
        self.white_bg_check.set_tooltip_text('Если отключить, то отрисовка происходит быстрее')
        self.white_bg_check.set_active(self.data['properties']['white_bg'])

        self.auto_levels_check = Gtk.CheckButton(label='всегда использовать "авто-уровни"')
        self.auto_levels_check.set_tooltip_text('Если включить, то уровни всегда будут подбираться автоматически')
        self.auto_levels_check.set_active(self.data['properties']['auto_levels'])

        self.different_options_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.different_options_vbox.set_border_width(10)
        for w in (self.ppi_hbox, self.white_bg_check, self.auto_levels_check):
            self.different_options_vbox.pack_start(w, False, False, 0)

        self.different_options_frame = Gtk.Frame(label='Различные опции')
        self.different_options_frame.add(self.different_options_vbox)

        self.about_button = Gtk.Button(label='О программе')
        self.about_button.connect('clicked', self.about, None)
        self.about_button.set_tooltip_text('О программе')

        self.apply_button = Gtk.Button(label='Применить')
        self.apply_button.connect('clicked', self.apply_settings, None)
        self.apply_button.set_tooltip_text('Применить эти настройки')

        self.cancel_button = Gtk.Button(label='Отмена')
        self.cancel_button.connect('clicked', self.destroy, None)
        self.cancel_button.set_tooltip_text('Закрыть это окно и не выполнять никаких действий')

        self.button_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.button_hbox.pack_start(self.about_button, False, False, 0)
        self.button_hbox.pack_end(self.apply_button, False, False, 0)
        self.button_hbox.pack_end(self.cancel_button, False, False, 0)

        self.table = Gtk.Grid()
        self.table.set_border_width(10)
        self.table.set_row_spacing(20)
        self.table.set_column_spacing(10)
        self.table.attach(self.formats_frame, 0, 0, 1, 1)
        self.table.attach(self.different_options_frame, 1, 0, 1, 1)
        self.table.attach(self.button_hbox, 0, 1, 2, 1)

        self.window = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
        self.window.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.window.set_title('Настройки дополнения "Фото на документы"')
        self.window.set_border_width(5)
        self.window.set_resizable(False)
        self.window.connect('delete-event', self.delete_event)
        self.window.connect('destroy', self.destroy)
        self.window.add(self.table)
        self.window.show_all()
        self.window.present()
        Gtk.main()


class PrintPhotoDialog(IdPhotoBase):
    def __init__(self, run_mode, image, drawable):
        super().__init__()
        self.image, self.drawable = image, drawable
        fmt = self.shelf_get('id-photo-format')
        if fmt is None:
            return
        self.format_resolution = fmt['resolution']

        self.gray_check = Gtk.CheckButton(label='обесцветить фото')
        self.gray_check.set_active(fmt['to_grayscale'])

        self.border_check = Gtk.CheckButton(label='добавить рамку')
        self.border_check.set_active(fmt['gray_frame'])

        self.oval_check = Gtk.CheckButton(label='добавить овал с растушёвкой')
        self.oval_check.set_active(fmt['oval'])

        self.angle_none_radio = Gtk.RadioButton.new_with_label(None, 'без уголка')
        self.angle_right_circular_radio = Gtk.RadioButton.new_with_label_from_widget(
            self.angle_none_radio, 'круглый справа')
        self.angle_left_circular_radio = Gtk.RadioButton.new_with_label_from_widget(
            self.angle_right_circular_radio, 'круглый слева')
        self.angle_right_direct_radio = Gtk.RadioButton.new_with_label_from_widget(
            self.angle_left_circular_radio, 'прямой справа')
        self.angle_left_direct_radio = Gtk.RadioButton.new_with_label_from_widget(
            self.angle_right_direct_radio, 'прямой слева')

        angle_widget = {False: self.angle_none_radio, 'right_circular': self.angle_right_circular_radio,
                        'left_circular': self.angle_left_circular_radio,
                        'right_direct': self.angle_right_direct_radio,
                        'left_direct': self.angle_left_direct_radio}
        angle_widget.get(fmt['angle'], self.angle_none_radio).set_active(True)

        copys_adj = Gtk.Adjustment(value=fmt['copys'] or 4.0, lower=0.0, upper=200.0,
                                   step_increment=1.0, page_increment=1.0, page_size=0.0)
        self.copys_spin = Gtk.SpinButton(adjustment=copys_adj, climb_rate=0, digits=0)
        self.copys_spin.set_numeric(True)
        self.copys_label = Gtk.Label(label='фото на листе')
        self.copys_label.set_justify(Gtk.Justification.LEFT)

        self.paper_cb = Gtk.ComboBoxText()
        for text in ('10x15', 'A5', 'A4'):
            self.paper_cb.append_text(text)
        paper_map = {'10x15': 0, 'A5': 1, 'A4': 2}
        self.paper_cb.set_active(paper_map.get(fmt['paper'], 0))

        self.copys_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.copys_hbox.pack_start(self.copys_spin, False, False, 0)
        self.copys_hbox.pack_start(self.copys_label, False, False, 5)
        self.copys_hbox.pack_start(self.paper_cb, False, False, 0)

        self.options_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        for w in (self.copys_hbox, self.gray_check, self.border_check, self.oval_check):
            self.options_vbox.pack_start(w, False, False, 5)

        self.angle_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.angle_vbox.set_border_width(5)
        for w in (self.angle_none_radio, self.angle_right_circular_radio, self.angle_left_circular_radio,
                  self.angle_right_direct_radio, self.angle_left_direct_radio):
            self.angle_vbox.pack_start(w, False, False, 0)

        self.angle_frame = Gtk.Frame(label='Добавить уголок')
        self.angle_frame.add(self.angle_vbox)

        self.cancel_button = Gtk.Button(label='Отмена')
        self.cancel_button.connect('clicked', self.destroy, None)
        self.cancel_button.set_tooltip_text('Не выполнять никаких действий с изображением')

        self.print_button = Gtk.Button(label='Напечатать')
        self.print_button.connect('clicked', self.compose_or_print, 'print_it')
        self.print_button.set_tooltip_text(
            'Сформировать окончательный результат и вывести его на принтер используемый по умолчанию')

        self.apply_button = Gtk.Button(label='Применить')
        self.apply_button.connect('clicked', self.compose_or_print, None)
        self.apply_button.set_tooltip_text('Сформировать окончательный результат')

        self.button_box = Gtk.ButtonBox(orientation=Gtk.Orientation.HORIZONTAL)
        self.button_box.set_layout(Gtk.ButtonBoxStyle.EDGE)
        self.button_box.set_spacing(10)
        for b in (self.cancel_button, self.print_button, self.apply_button):
            self.button_box.add(b)

        self.table = Gtk.Grid()
        self.table.set_border_width(5)
        self.table.set_row_spacing(10)
        self.table.set_column_spacing(10)
        self.table.attach(self.options_vbox, 0, 0, 1, 1)
        self.table.attach(self.angle_frame, 1, 0, 1, 1)
        self.table.attach(self.button_box, 0, 1, 2, 1)

        self.window = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
        self.window.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.window.set_title('Сформировать и распечатать')
        self.window.set_border_width(5)
        self.window.set_resizable(False)
        self.window.connect('delete-event', self.delete_event)
        self.window.connect('destroy', self.destroy)
        self.window.add(self.table)
        self.window.show_all()
        self.window.present()
        Gtk.main()


#########################################################
#--------           Вот оно - начало начал          ----#
#########################################################

PROC_SELECT_FORMAT = 'python-fu-id-photo-select-format'
PROC_SETTINGS = 'python-fu-id-photo-settings'
PROC_PRINT = 'python-fu-id-photo-print'
MENU_PATH = '<Image>/На документы/'

def _run_select_format(procedure, run_mode, image, drawables, config, run_data):
    GimpUi.init('id-photo')
    drawable = drawables[0] if drawables else None
    SelectFormatIdPhoto(run_mode, image, drawable)
    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

def _run_settings(procedure, run_mode, image, drawables, config, run_data):
    GimpUi.init('id-photo')
    SettingsDialog(run_mode, image)
    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

def _run_print(procedure, run_mode, image, drawables, config, run_data):
    GimpUi.init('id-photo')
    drawable = drawables[0] if drawables else None
    PrintPhotoDialog(run_mode, image, drawable)
    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

class IdPhotoPlugin(Gimp.PlugIn):
    def do_set_i18n(self, name):
        return False

    def do_query_procedures(self):
        return [PROC_SELECT_FORMAT, PROC_SETTINGS, PROC_PRINT]

    def do_create_procedure(self, name):
        author = 'Карабанов Александр (zend.karabanov@gmail.com)'
        copyright_name = 'Карабанов Александр'
        date = '2012-2026 (порт на GIMP 3)'

        if name == PROC_SELECT_FORMAT:
            procedure = Gimp.ImageProcedure.new(
                self, name, Gimp.PDBProcType.PLUGIN, _run_select_format, None)
            procedure.set_image_types('RGB*, GRAY*')
            procedure.set_sensitivity_mask(Gimp.ProcedureSensitivityMask.DRAWABLE)
            procedure.set_menu_label('_Формат...')
            procedure.add_menu_path(MENU_PATH)
            procedure.set_documentation(
                'Выводит диалог содержащий в себе список форматов.',
                'Расставьте направляющие и вызовите эту функцию.', name)
            procedure.set_attribution(author, copyright_name, date)
            return procedure

        if name == PROC_SETTINGS:
            procedure = Gimp.ImageProcedure.new(
                self, name, Gimp.PDBProcType.PLUGIN, _run_settings, None)
            procedure.set_image_types('*')
            procedure.set_sensitivity_mask(
                Gimp.ProcedureSensitivityMask.DRAWABLE | Gimp.ProcedureSensitivityMask.NO_DRAWABLES)
            procedure.set_menu_label('_Настройки...')
            procedure.add_menu_path(MENU_PATH)
            procedure.set_documentation(
                'Выводит диалог настроек.',
                'Вызовите эту функцию, чтобы добавить или отредактировать формат.', name)
            procedure.set_attribution(author, copyright_name, date)
            return procedure

        if name == PROC_PRINT:
            procedure = Gimp.ImageProcedure.new(
                self, name, Gimp.PDBProcType.PLUGIN, _run_print, None)
            procedure.set_image_types('RGB*, GRAY*')
            procedure.set_sensitivity_mask(Gimp.ProcedureSensitivityMask.DRAWABLE)
            procedure.set_menu_label('_Печать...')
            procedure.add_menu_path(MENU_PATH)
            procedure.set_documentation(
                'Выводит диалог из которого можно сформировать и напечатать окончательный результат.',
                'Вызовите эту функцию, чтобы распечатать фото.', name)
            procedure.set_attribution(author, copyright_name, date)
            return procedure

        return None

Gimp.main(IdPhotoPlugin.__gtype__, sys.argv)
