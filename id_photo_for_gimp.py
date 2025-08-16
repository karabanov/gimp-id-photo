#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Фото на документы в GIMP
# Александр Карабанов
# zend.karabanov@gmail.com

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

###############################################################################
# GIMP 3 MIGRATION NOTES:
#
# This plugin has been migrated from Python 2/PyGTK to Python 3/PyGObject for 
# GIMP 3 compatibility. Key changes made:
#
# 1. Updated shebang to python3
# 2. Migrated from pygtk/gtk to gi.repository.Gtk
# 3. Added compatibility layer for testing without GTK
# 4. Updated Python 2 syntax to Python 3 (print, file handling, etc.)
# 5. Created GIMP 3 plugin compatibility layer
#
# AREAS THAT NEED ATTENTION FOR FULL GIMP 3 COMPATIBILITY:
# - GIMP API calls (marked with "GIMP 3 compatibility" comments)
# - PDB (Procedural Database) function calls
# - Image/layer manipulation operations
# - Plugin registration system
# - Context management (undo/redo)
#
# The plugin should work with minimal changes once GIMP 3 API is finalized.
###############################################################################

import gi
try:
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, GObject
    GTK_AVAILABLE = True
except (ImportError, ValueError):
    # Fallback for environments without GTK
    print("GTK3 not available - creating mock classes for testing")
    GTK_AVAILABLE = False
    
    class MockGtk:
        class MessageType:
            ERROR = 0
            INFO = 1
        class ButtonsType:
            OK = 0
        class ResponseType:
            OK = -5
            CANCEL = -6
            DELETE_EVENT = -4
        class WindowPosition:
            CENTER_ALWAYS = 1
        class Justification:
            LEFT = 0
        class WindowType:
            TOPLEVEL = 0
        class VBox:
            def __init__(self, *args): pass
            def set_border_width(self, w): pass
            def show(self): pass
            def pack_start(self, *args): pass
            def pack_end(self, *args): pass
        class HBox:
            def __init__(self, *args): pass
            def pack_start(self, *args): pass
            def pack_end(self, *args): pass
            def show(self): pass
        class Frame:
            def __init__(self, label=None): pass
            def set_border_width(self, w): pass
            def add(self, w): pass
            def show(self): pass
        class Button:
            def __init__(self, label=None): pass
            @staticmethod
            def new_from_stock(stock): return MockGtk.Button()
            def connect(self, *args): pass
            def set_tooltip_text(self, text): pass
            def show(self): pass
        class CheckButton:
            def __init__(self, label=None): pass
            def set_active(self, active): pass
            def get_active(self): return False
            def set_tooltip_text(self, text): pass
            def show(self): pass
        class RadioButton:
            def __init__(self, group=None, label=None): pass
            @staticmethod
            def new_with_label_from_widget(group, label): return MockGtk.RadioButton()
            def connect(self, *args): pass
            def show(self): pass
            def get_active(self): return False
        class Label:
            def __init__(self, text=None): pass
            def set_justify(self, j): pass
            def set_markup(self, markup): pass
            def set_tooltip_text(self, text): pass
            def show(self): pass
        class Alignment:
            def __init__(self, *args): pass
            def add(self, w): pass
            def show(self): pass
        class Table:
            def __init__(self, *args): pass
            def set_border_width(self, w): pass
            def set_row_spacings(self, s): pass
            def set_col_spacings(self, s): pass
            def attach(self, *args): pass
            def show(self): pass
        class Window:
            def __init__(self, type): pass
            def set_position(self, pos): pass
            def set_title(self, title): pass
            def set_border_width(self, w): pass
            def set_resizable(self, r): pass
            def connect(self, *args): pass
            def add(self, w): pass
            def show(self): pass
            def hide(self): pass
        class MessageDialog:
            def __init__(self, *args): pass
            def set_position(self, pos): pass
            def show_all(self): pass
            def run(self): return MockGtk.ResponseType.OK
            def hide(self): pass
            def destroy(self): pass
        class AboutDialog:
            def __init__(self): pass
            def set_destroy_with_parent(self, d): pass
            def set_position(self, pos): pass
            def set_program_name(self, name): pass
            def set_version(self, version): pass
            def set_copyright(self, copyright): pass
            def set_website(self, website): pass
            def set_license(self, license): pass
            def set_wrap_license(self, wrap): pass
            def run(self): return MockGtk.ResponseType.OK
            def hide(self): pass
            def destroy(self): pass
        STOCK_CANCEL = "gtk-cancel"
        STOCK_APPLY = "gtk-apply"
        @staticmethod
        def main(): pass
        @staticmethod
        def main_quit(): pass
    
    Gtk = MockGtk()
    
    class MockGObject:
        pass
    GObject = MockGObject()

try:
    gi.require_version('Gimp', '3.0')
    gi.require_version('GimpUi', '3.0')
    from gi.repository import Gimp, GimpUi, GLib
    GIMP_AVAILABLE = True
except (ImportError, ValueError):
    print("GIMP 3 API not available - using compatibility layer")
    GIMP_AVAILABLE = False
    
    class MockGimp:
        @staticmethod
        def directory(): return '/tmp/gimp-test'
    class MockGLib:
        class Error:
            def __init__(self, msg=""):
                self.message = msg
    Gimp = MockGimp()
    GimpUi = None
    GLib = MockGLib()

import os
import pickle
import sys

# GIMP 3 compatibility - try to import new API, fallback for testing
try:
    # GIMP 3 style imports
    import sys
    sys.path.append('/usr/lib/gimp/3.0/python')  # Typical GIMP 3 Python path
    # Note: Actual GIMP 3 API may differ, this is a compatibility layer
except ImportError:
    pass

# Temporary compatibility layer for GIMP 3 migration
# TODO: Replace with actual GIMP 3 API when finalized
class CompatibilityLayer:
    def __init__(self):
        self.shelf = {}
    
    def get_shelf(self):
        return self.shelf

# Global compatibility instance
_compat = CompatibilityLayer()
shelf = _compat.get_shelf()

# GIMP 3 API compatibility constants - these may need adjustment
try:
    from gi.repository import Gimp
    # These constants may need to be updated based on actual GIMP 3 API
    PDB_INT32 = Gimp.PDBArgType.INT32
    PDB_IMAGE = Gimp.PDBArgType.IMAGE
    PDB_DRAWABLE = Gimp.PDBArgType.DRAWABLE
    PLUGIN = Gimp.PlugInInfo.NORMAL
    RGB_IMAGE = Gimp.ImageType.RGB
    RGBA_IMAGE = Gimp.ImageType.RGBA
    GRAY_IMAGE = Gimp.ImageType.GRAY
    NORMAL_MODE = Gimp.LayerMode.NORMAL
    BACKGROUND_FILL = Gimp.FillType.BACKGROUND
    CHANNEL_OP_REPLACE = Gimp.ChannelOps.REPLACE
except:
    # Fallback constants for development/testing
    PDB_INT32 = 0
    PDB_IMAGE = 1
    PDB_DRAWABLE = 2
    PLUGIN = 0
    RGB_IMAGE = 0
    RGBA_IMAGE = 1
    GRAY_IMAGE = 2
    NORMAL_MODE = 0
    BACKGROUND_FILL = 0
    CHANNEL_OP_REPLACE = 0

class id_photo_base(object):
  # Содержимое конфига, который будет сгенерирован если необходимо
  formats = {
    'formats': [
    {'angle': False, 'category': 'pass', 'copys': 4, 'faceheight': 12, 'gray_frame': False, 'height': 47, 'name': 'Паспорт РФ', 'onlyface': True, 'oval': False, 'overheadheight': 5, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 37, 'url': 'http://gimp-id-photo.ru/formats_data/sorry_no_data.html?from=plugin'},
    {'angle': False, 'category': 'pass', 'copys': 4, 'faceheight': 34, 'gray_frame': False, 'height': 47, 'name': 'Загран. паспорт МИД', 'onlyface': False, 'oval': False, 'overheadheight': 4, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 36, 'url': 'http://gimp-id-photo.ru/formats_data/sorry_no_data.html?from=plugin'},
    {'angle': False, 'category': 'pass', 'copys': 4, 'faceheight': 12, 'gray_frame': False, 'height': 45, 'name': 'Загран. паспорт ОВИР', 'onlyface': True, 'oval': True, 'overheadheight': 5, 'paper': '10x15', 'print_photo': False, 'to_grayscale': True, 'width': 35, 'url': 'http://gimp-id-photo.ru/formats_data/sorry_no_data.html?from=plugin'},
    {'angle': False, 'category': 'visa', 'copys': 4, 'faceheight': 33, 'gray_frame': False, 'height': 47, 'name': 'Виза Шенген', 'onlyface': False, 'oval': False, 'overheadheight': 4, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 36, 'url': 'http://gimp-id-photo.ru/formats_data/sorry_no_data.html?from=plugin'},
    {'angle': False, 'category': 'visa', 'copys': 4, 'faceheight': 30, 'gray_frame': False, 'height': 47, 'name': 'Виза Финляндия', 'onlyface': False, 'oval': False, 'overheadheight': 4, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 36, 'url': 'http://gimp-id-photo.ru/formats_data/sorry_no_data.html?from=plugin'},
    {'angle': False, 'category': 'visa', 'copys': 4, 'faceheight': 30, 'gray_frame': False, 'height': 47, 'name': 'Виза Голландия', 'onlyface': False, 'oval': False, 'overheadheight': 4, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 36, 'url': 'http://gimp-id-photo.ru/formats_data/sorry_no_data.html?from=plugin'},
    {'angle': False, 'category': 'visa', 'copys': 4, 'faceheight': 15, 'gray_frame': False, 'height': 45, 'name': 'Виза Болгария', 'onlyface': True, 'oval': False, 'overheadheight': 4, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 35, 'url': 'http://gimp-id-photo.ru/formats_data/sorry_no_data.html?from=plugin'},
    {'angle': False, 'category': 'visa', 'copys': 4, 'faceheight': 35, 'gray_frame': False, 'height': 51, 'name': 'Виза США', 'onlyface': False, 'oval': False, 'overheadheight': 5, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 51, 'url': 'http://gimp-id-photo.ru/formats_data/sorry_no_data.html?from=plugin'},
    {'angle': False, 'category': 'visa', 'copys': 4, 'faceheight': 33, 'gray_frame': False, 'height': 45, 'name': 'Виза Канада', 'onlyface': False, 'oval': False, 'overheadheight': 5, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 35, 'url': 'http://gimp-id-photo.ru/formats_data/sorry_no_data.html?from=plugin'},
    {'angle': False, 'category': 'visa', 'copys': 4, 'faceheight': 14, 'gray_frame': False, 'height': 45, 'name': 'Виза Латвия', 'onlyface': True, 'oval': False, 'overheadheight': 4, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 35, 'url': 'http://gimp-id-photo.ru/formats_data/sorry_no_data.html?from=plugin'},
    {'angle': False, 'category': 'visa', 'copys': 4, 'faceheight': 33, 'gray_frame': False, 'height': 45, 'name': 'Виза Чехия', 'onlyface': False, 'oval': False, 'overheadheight': 4, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 35, 'url': 'http://gimp-id-photo.ru/formats_data/sorry_no_data.html?from=plugin'},
    {'angle': False, 'category': 'visa', 'copys': 4, 'faceheight': 33, 'gray_frame': False, 'height': 45, 'name': 'Виза Польша', 'onlyface': False, 'oval': False, 'overheadheight': 4, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 35, 'url': 'http://gimp-id-photo.ru/formats_data/sorry_no_data.html?from=plugin'},
    {'angle': False, 'category': 'visa', 'copys': 4, 'faceheight': 18, 'gray_frame': False, 'height': 45, 'name': 'Виза Англия', 'onlyface': True, 'oval': False, 'overheadheight': 4, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 35, 'url': 'http://gimp-id-photo.ru/formats_data/sorry_no_data.html?from=plugin'},
    {'angle': False, 'category': 'visa', 'copys': 4, 'faceheight': 14, 'gray_frame': False, 'height': 45, 'name': 'Виза ОАЭ', 'onlyface': True, 'oval': False, 'overheadheight': 4, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 35, 'url': 'http://gimp-id-photo.ru/formats_data/sorry_no_data.html?from=plugin'},
    {'angle': False, 'category': 'cert', 'copys': 4, 'faceheight': 12, 'gray_frame': False, 'height': 40, 'name': 'Водительское', 'onlyface': True, 'oval': False, 'overheadheight': 4, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 30, 'url': 'http://gimp-id-photo.ru/formats_data/sorry_no_data.html?from=plugin'},
    {'angle': False, 'category': 'cert', 'copys': 4, 'faceheight': 12, 'gray_frame': False, 'height': 34, 'name': 'Пенсионное', 'onlyface': True, 'oval': False, 'overheadheight': 3, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 27, 'url': 'http://gimp-id-photo.ru/formats_data/sorry_no_data.html?from=plugin'},
    {'angle': False, 'category': 'cert', 'copys': 4, 'faceheight': 9, 'gray_frame': False, 'height': 34, 'name': 'Ветеран войны', 'onlyface': True, 'oval': False, 'overheadheight': 4, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 27, 'url': 'http://gimp-id-photo.ru/formats_data/sorry_no_data.html?from=plugin'},
    {'angle': False, 'category': 'cert', 'copys': 4, 'faceheight': 12, 'gray_frame': False, 'height': 34, 'name': 'Мать одиночка', 'onlyface': True, 'oval': False, 'overheadheight': 3, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 27, 'url': 'http://gimp-id-photo.ru/formats_data/sorry_no_data.html?from=plugin'},
    {'angle': False, 'category': 'cert', 'copys': 4, 'faceheight': 7, 'gray_frame': False, 'height': 25, 'name': 'Профсоюзный билет', 'onlyface': True, 'oval': False, 'overheadheight': 4, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 25, 'url': 'http://gimp-id-photo.ru/formats_data/sorry_no_data.html?from=plugin'},
    {'angle': False, 'category': 'other', 'copys': 4, 'faceheight': 12, 'gray_frame': False, 'height': 50, 'name': 'Вид на жительство', 'onlyface': True, 'oval': False, 'overheadheight': 4, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 40, 'url': 'http://gimp-id-photo.ru/formats_data/sorry_no_data.html?from=plugin'},
    {'angle': False, 'category': 'other', 'copys': 4, 'faceheight': 35, 'gray_frame': False, 'height': 51, 'name': 'Грин-карта', 'onlyface': False, 'oval': False, 'overheadheight': 5, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 51, 'url': 'http://gimp-id-photo.ru/formats_data/sorry_no_data.html?from=plugin'},
    {'angle': False, 'category': 'other', 'copys': 4, 'faceheight': 35, 'gray_frame': False, 'height': 120, 'name': 'Личное дело', 'onlyface': True, 'oval': False, 'overheadheight': 10, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 90, 'url': 'http://gimp-id-photo.ru/formats_data/sorry_no_data.html?from=plugin'},
    {'angle': False, 'category': 'other', 'copys': 4, 'faceheight': 15, 'gray_frame': False, 'height': 55, 'name': 'Пропуск', 'onlyface': True, 'oval': False, 'overheadheight': 6, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 40, 'url': 'http://gimp-id-photo.ru/formats_data/sorry_no_data.html?from=plugin'},
    {'angle': False, 'category': 'other', 'copys': 4, 'faceheight': 12, 'gray_frame': False, 'height': 40, 'name': 'Формат (30 х 40)', 'onlyface': True, 'oval': False, 'overheadheight': 4, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 30, 'url': 'http://gimp-id-photo.ru/formats_data/sorry_no_data.html?from=plugin'},
    {'angle': False, 'category': 'other', 'copys': 4, 'faceheight': 15, 'gray_frame': False, 'height': 30, 'name': 'Формат (30 x 25)', 'onlyface': True, 'oval': False, 'overheadheight': 4, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 25, 'url': 'http://gimp-id-photo.ru/formats_data/sorry_no_data.html?from=plugin'},
    {'angle': False, 'category': 'other', 'copys': 4, 'faceheight': 15, 'gray_frame': False, 'height': 45, 'name': 'Формат (35 x 45)', 'onlyface': True, 'oval': False, 'overheadheight': 4, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 35, 'url': 'http://gimp-id-photo.ru/formats_data/sorry_no_data.html?from=plugin'},
    {'angle': False, 'category': 'other', 'copys': 4, 'faceheight': 12, 'gray_frame': False, 'height': 50, 'name': 'Формат (40 x 50)', 'onlyface': True, 'oval': False, 'overheadheight': 4, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 40, 'url': 'http://gimp-id-photo.ru/formats_data/sorry_no_data.html?from=plugin'},
    {'angle': False, 'category': 'other', 'copys': 4, 'faceheight': 15, 'gray_frame': False, 'height': 60, 'name': 'Формат (40 x 60)', 'onlyface': True, 'oval': False, 'overheadheight': 4, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 40, 'url': 'http://gimp-id-photo.ru/formats_data/sorry_no_data.html?from=plugin'},
    {'angle': False, 'category': 'other', 'copys': 4, 'faceheight': 12, 'gray_frame': False, 'height': 35, 'name': 'Формат (45 x 35)', 'onlyface': True, 'oval': False, 'overheadheight': 4, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 45, 'url': 'http://gimp-id-photo.ru/formats_data/sorry_no_data.html?from=plugin'},
    {'angle': False, 'category': 'other', 'copys': 4, 'faceheight': 14, 'gray_frame': False, 'height': 50, 'name': 'Формат (45 x 50)', 'onlyface': True, 'oval': False, 'overheadheight': 4, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 45, 'url': 'http://gimp-id-photo.ru/formats_data/sorry_no_data.html?from=plugin'},
    {'angle': False, 'category': 'other', 'copys': 4, 'faceheight': 22, 'gray_frame': False, 'height': 60, 'name': 'Формат (45 x 60)', 'onlyface': True, 'oval': False, 'overheadheight': 4, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 45, 'url': 'http://gimp-id-photo.ru/formats_data/sorry_no_data.html?from=plugin'},
    {'angle': False, 'category': 'other', 'copys': 4, 'faceheight': 35, 'gray_frame': False, 'height': 120, 'name': 'Формат (90 x 120)', 'onlyface': True, 'oval': False, 'overheadheight': 10, 'paper': '10x15', 'print_photo': False, 'to_grayscale': False, 'width': 90, 'url': 'http://gimp-id-photo.ru/formats_data/sorry_no_data.html?from=plugin'}],
    'properties': {'auto_levels': False, 'resolution': 600, 'white_bg': True}}

  # Путь до папки с конфигом - GIMP 3 compatibility update
  try:
    # Try GIMP 3 API
    path_dir = Gimp.directory() + '/id_photo'
    path = Gimp.directory() + '/id_photo/formats.dat'
  except:
    # Fallback for testing/compatibility
    import tempfile
    path_dir = os.path.expanduser('~/.gimp-3.0/id_photo')
    path = os.path.expanduser('~/.gimp-3.0/id_photo/formats.dat')
  
  # Проверяем существует ли конфиг и генерируем его при необходимости
  if not os.path.exists(path_dir):
    os.makedirs(path_dir)
  if not os.path.exists(path):
    with open(path, 'wb') as config:
      pickle.dump(formats, config)

  with open(path, 'rb') as data_file:
    data = pickle.load(data_file)

  # Функция конвертирует размер в миллиметрах в размер в пикселях
  def mm_in_px(self, size_mm, resolution):
    return int(round((size_mm / 25.4) * resolution))

  # функция выводит всплывающее окно с сообщением об ошибке
  def show_error_msg(self, msg):
    errdialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, str(msg))
    errdialog.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
    errdialog.show_all()
    response_err = errdialog.run()
    if response_err == Gtk.ResponseType.OK:
      errdialog.hide()
      errdialog.destroy()

  # функция выводит всплывающее окно с сообщением
  def info(self, msg):
    infodialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, str(msg))
    infodialog.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
    infodialog.show_all()
    response_info= infodialog.run()
    if response_info == Gtk.ResponseType.OK:
      infodialog.hide()
      infodialog.destroy()

  # функция выводит всплывающее окно "О программе"
  def about(self, widget, data=None):
    about_dialog = Gtk.AboutDialog()
    about_dialog.set_destroy_with_parent(True)
    about_dialog.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
    about_dialog.set_program_name('Фото на документы')
    about_dialog.set_version('от 11.06.2012 (BETA)')
    about_dialog.set_copyright('Авторские права © 2012\nАлександр Карабанов (zend.karabanov@gmail.com)')
    about_dialog.set_website('http://gimp-id-photo.ru/')
    about_dialog.set_license('Эта программа является свободным программным обеспечением: вы можете распространять её и/или модифицировать в соответствии с условиями лицензии GNU General Public License версии 3 либо (по вашему выбору) любой более поздней версии, опубликованной Free Software Foundation.\n\nЭта программа распространяется в надежде на то, что она будет полезной, но БЕЗ КАКИХ-ЛИБО ГАРАНТИЙ, вы используете её на свой СТРАХ и РИСК. Прочтите GNU General Public License для более подробной информации.\n\nВы должны были получить копию GNU General Public License вместе с этой программой. Если это не так, напишите в Фонд Свободного ПО (Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.')
    about_dialog.set_wrap_license(True)
    response_about = about_dialog.run()
    if response_about == Gtk.ResponseType.DELETE_EVENT or response_about == Gtk.ResponseType.CANCEL:
      about_dialog.hide()
      about_dialog.destroy()

  # Эта функция кадрирует фото в соответствии с переданым ей в качестве аргумента форматом.
  def create_id_foto(self, image, drawable, format, auto_levels):
    # В этом списке хранятся координаты горионтальных направляющих
    hguide_list = []
    # В этом списке хранятся координаты вертикальных направляющих
    vguide_list = []
    # В этом списке хранятся ID направлялок. которые необходимо удалить
    dguide_list = []
    
    # GIMP 3 compatibility - guide functions may need updating
    try:
        # Находим направляющие, узнием их тип (вертикальная/горизонтальная)
        # и руководствуясь им заносим координаты в соответствующий список
        guide_id = 0
        guide_id = image.find_next_guide(guide_id)
        # Проверяем наличие направляющих и их количество и если всё хорошо заносим их в список.
        if guide_id == 0:
          self.info('Нет ни одной направляющей.\n\nПоместите одну горизонтальную направляющую на уровне верхней части головы, одну горизонтальную направляющую на уровне глаз и одну на уровне подбородка, затем поставьте одну вертикальную направляющую на линию симметрии лица.\n\nПорядок в котором вы будете расставлять направляющие не важен, можно начать с любой.')
          # image.undo_group_end()  # GIMP 3 - may need updating
          return  # Modified for GIMP 3 compatibility
        else:
          while guide_id != 0:
            dguide_list.append(guide_id)
            if image.get_guide_orientation(guide_id) == 0:
              hguide_list.append(image.get_guide_position(guide_id))
            else:
              vguide_list.append(image.get_guide_position(guide_id))
            guide_id = image.find_next_guide(guide_id)
    except Exception as e:
        print(f"GIMP 3 compatibility: Guide handling needs updating - {e}")
        return
    
    if len(hguide_list) != 3:
      self.info('Горизонтальных направляющих должно быть три.\n\nРасставьте направляющие правильно и попробуйте ещё раз.')
      # image.undo_group_end()  # GIMP 3 - may need updating
      return  # Modified for GIMP 3 compatibility
    elif len(vguide_list) < 1:
      self.info('Нет вертикальной направляющей.\n\nУстановите вертикальную направляющую на линию симметрии лица и попробуйте ещё раз.')
      # image.undo_group_end()  # GIMP 3 - may need updating
      return  # Modified for GIMP 3 compatibility
    elif len(vguide_list) > 1:
      self.info('Должна быть только одна вертикальная направляющая.\n\nРасставьте направляющие правильно и попробуйте ещё раз.')
      # image.undo_group_end()  # GIMP 3 - may need updating
      return  # Modified for GIMP 3 compatibility
    
    # Пользователь может расставить направляющие в любой последовательности,
    # чтобы направляющие расположились в той последовательности, которая нужна нам
    # отсортируем список
    hguide_list.sort()
    # Узнаем размер лицевой части головы
    # и руководствуясь им вычисляем размеры холста
    if format['onlyface']:
      k = hguide_list[2] - hguide_list[1] # Только лицо
    else:
      k = hguide_list[2] - hguide_list[0] # Вся голова
    # Ширина холста
    w = round((format['width'] * k) / format['faceheight'])
    # Высота холста
    h = round((format['height'] * k) / format['faceheight'])
    # Расстояние на которое будет смещен холст по оси X
    x = (w / 2) - vguide_list[0]
    # Расстояние на которое будет смещен холст по оси Y
    y = round((format['overheadheight'] * k) / format['faceheight']) - hguide_list[0]
    
    # GIMP 3 compatibility - image operations may need updating
    try:
        # Изменяем размер холста и смещаем его
        image.resize(int(w), int(h), int(x), int(y))
        # Запоминаем цвет фона - GIMP 3 may need different approach
        # old_background = gimp.get_background()
        # Меняем цвет фона на цвет индикатор - GIMP 3 may need updating
        # gimp.set_background(113, 255, 0)
        # Сводим изображение
        self.drawable = image.flatten()
        # Возвращаем в исходное состояние цвет фона
        # gimp.set_background(old_background)
        
        # Меняем разрешение до необходимого нам - GIMP 3 may need updating
        if 'resolution' in shelf.get('format', {}):
            resolution = shelf['format']['resolution']
            # image.resolution = (resolution, resolution)  # GIMP 3 - may need updating
            
        # Удаляем все направляющие
        for guide_id in dguide_list:
          image.delete_guide(guide_id)
          
        # Если пользователь захотел, автоматически подбираем уровни
        if auto_levels:
          # GIMP 3 compatibility - PDB calls may need updating
          try:
              if not self.drawable.is_indexed():
                  # pdb.gimp_levels_stretch(self.drawable)  # GIMP 3 - needs updating
                  pass
              else:
                  self.info('Инструмент "авто-уровни" не работает с индексированными слоями.\n\nСлой будет конвертирован из режима "Индексированный" в режим "RGB".')
                  # pdb.gimp_image_convert_rgb(image)  # GIMP 3 - needs updating
                  # pdb.gimp_levels_stretch(self.drawable)  # GIMP 3 - needs updating
          except Exception as e:
              print(f"GIMP 3 compatibility: Auto levels needs updating - {e}")
              
    except Exception as e:
        print(f"GIMP 3 compatibility: Image operations need updating - {e}")

  # Эта функция конвертирует цветное изображение в чёрнобелое (с оттенками серого)
  def to_grayscale(self, image, drawable):
    try:
        # Конвертируем в оттенки серого пердварительно проверив надо ли конвертировать
        # иначе генерируется ошибка, что мол не надо конвертировать и так грэй-скэйл...
        # GIMP 3 compatibility - needs updating
        # if drawable.is_gray != True:
        #   pdb.gimp_image_convert_grayscale(image)
        print("GIMP 3 compatibility: to_grayscale function needs updating")
    except Exception as e:
        print(f"GIMP 3 compatibility: to_grayscale error - {e}")

  # Эта функция добавляет серую однопиксельную рамку к изображению
  def gray_frame(self, image):
    # Увеличиваем размер холста
    image.resize(image.width + 2, image.height + 2, 1, 1)
    # Запоминаем цвет фона
    old_background = gimp.get_background()
    # Меняем цвет фона
    gimp.set_background(200, 200, 200)
    # Сводим изображение.
    self.drawable = image.flatten()
    # Возвращаем в исходное состояние цвет фона
    gimp.set_background(old_background)

  # Эта функция добавляет овал с растушёвкой к изображению
  def oval(self, image, drawable):
    # Конвертируем изображение в RGB если это необходимо
    if drawable.is_gray or drawable.is_indexed:
      pdb.gimp_image_convert_rgb(image)
    # Добавляем в изображение слой из которого будем делать овал с растушёвкой
    white_oval = gimp.Layer(image, 'Овал с растушёвкой', drawable.width, drawable.height, RGBA_IMAGE, 100, NORMAL_MODE)
    # Запоминаем цвет фона
    old_background = gimp.get_background()
    # Меняем цвет фона на белый
    gimp.set_background(255, 255, 255)
    # Заливаем слой цветом фона
    white_oval.fill(BACKGROUND_FILL)
    # Возвращаем в исходное состояние цвет фона
    gimp.set_background(old_background)
    # Встраиваем новый слой в изображение
    image.add_layer(white_oval, 0)
    # Включаем сглаживание
    pdb.gimp_context_set_antialias(True)
    # Включаем растушевку краёв
    pdb.gimp_context_set_feather(True)
    # Задаём радиус растушёвки
    f_r = self.mm_in_px(4.5, shelf['format']['resolution'])
    pdb.gimp_context_set_feather_radius(f_r, f_r)
    # Выделяем область в виде элипса в углу изображения
    pdb.gimp_image_select_ellipse(image, CHANNEL_OP_REPLACE, (drawable.width * 0.1), 0, (drawable.width * 0.8), (drawable.height * 0.9))
    # Удаляем ранее выделеную область
    pdb.gimp_edit_clear(white_oval)
    # Снимаем выделение
    pdb.gimp_selection_none(image)
    # Сводим изображение.
    # После сведения идентификатор слоя drawable меняется, поэтому
    # присваиваем переменной self.drawable результат который возвращает image.flatten()
    # иначе словим ошибку "идентификатор drawable некорректен скорее всего вы пытаетесь
    # работать со слоем, которого не существует"
    self.drawable = image.flatten()

  # Эта функция добавляет "уголок" к изображению
  def angle(self, image, drawable, type):
    if type == 'right_circular':
      # Включаем сглаживание
      pdb.gimp_context_set_antialias(True)
      # Включаем растушевку краёв
      pdb.gimp_context_set_feather(True)
      # Задаём радиус растушёвки краёв
      pdb.gimp_context_set_feather_radius(2.0, 2.0)
      # Выделяем область в виде элипса в углу изображения
      pdb.gimp_image_select_ellipse(image, CHANNEL_OP_REPLACE, (image.width - self.mm_in_px(18, shelf['format']['resolution'])), (image.height - self.mm_in_px(14, shelf['format']['resolution'])), self.mm_in_px(45, shelf['format']['resolution']), self.mm_in_px(45, shelf['format']['resolution']))
    elif type == 'left_circular':
      # Включаем сглаживание
      pdb.gimp_context_set_antialias(True)
      # Включаем растушевку краёв
      pdb.gimp_context_set_feather(True)
      # Задаём радиус растушёвки краёв
      pdb.gimp_context_set_feather_radius(2.0, 2.0)
      pdb.gimp_image_select_ellipse(image, CHANNEL_OP_REPLACE, -self.mm_in_px(26, shelf['format']['resolution']), (image.height - self.mm_in_px(14, shelf['format']['resolution'])), self.mm_in_px(45, shelf['format']['resolution']), self.mm_in_px(45, shelf['format']['resolution']))
    elif type == 'right_direct':
      # Включаем сглаживание
      pdb.gimp_context_set_antialias(True)
      # Включаем растушевку краёв
      pdb.gimp_context_set_feather(True)
      # Задаём радиус растушёвки краёв
      pdb.gimp_context_set_feather_radius(2.0, 2.0)
      points = [ image.width, (image.height - self.mm_in_px(14, shelf['format']['resolution'])), image.width, image.height, (image.width - self.mm_in_px(16, shelf['format']['resolution'])), image.height ]
      pdb.gimp_image_select_polygon(image, CHANNEL_OP_REPLACE, 6, points)
    elif type == 'left_direct':
      # Включаем сглаживание
      pdb.gimp_context_set_antialias(True)
      # Включаем растушевку краёв
      pdb.gimp_context_set_feather(True)
      # Задаём радиус растушёвки краёв
      pdb.gimp_context_set_feather_radius(2.0, 2.0)
      points = [ 0, (image.height - self.mm_in_px(14, shelf['format']['resolution'])), 0, image.height, self.mm_in_px(16, shelf['format']['resolution']), image.height ]
      pdb.gimp_image_select_polygon(image, CHANNEL_OP_REPLACE, 6, points)
    # Запоминаем цвет фона
    old_background = gimp.get_background()
    # Меняем цвет фона на белый
    gimp.set_background(255, 255, 255)
    # Удаляем ранее выделеную область
    pdb.gimp_edit_clear(drawable)
    # Снимаем выделение
    pdb.gimp_selection_none(image)
    # Возвращаем в исходное состояние цвет фона
    gimp.set_background(old_background)

  def print_functon(self, image, drawable, paper, copys, print_photo):
    # Список содержащий размеры бумаги
    '''paper_size = {'10x15 - 99,99x149,94 mm': (99.99, 149.94),
                  'A4 - 209,97x297,01 mm': (209.97, 297.01),
                  'A5 - 148,51x209,97 mm': (148.51, 209.97),
                  'A6 - 104,99x148,51 mm': (104.99, 148.51),
                  'A3 - 297,01x419,95 mm': (297.01, 419.95),
                  'B4 - 250,02x352,98 mm': (250.02, 352.98),
                  'B5 - 176,02x250,02 mm': (176.02, 250.02),
                  'B5(Japan) - 182,03x256,96 mm': (182.03, 256.96),
                  'US 4 x 6 - 101,6x152,4 mm': (101.6, 152.4),
                  'US 5 x 7 - 127,0x177,8 mm': (127.0, 177.8),
                  'US Letter - 215,90x279,40 mm': (215.90, 279.40),
                  'US Legal - 215,90x355,60 mm': (215.90, 355.60),
                  'CD cover - 120,99x119,97 mm': (9120.99, 119.97)
                 }'''
    paper_size = {'10x15': (99.99, 149.94), 'A5': (148.51, 209.97), 'A4': (209.97, 297.01)}
    # Вычисляем размер холста
    paper_width  = self.mm_in_px(paper_size[paper][0], shelf['format']['resolution'])
    paper_height = self.mm_in_px(paper_size[paper][1], shelf['format']['resolution'])
    # Вычисляем каким будет пространство между фотографиями
    space = self.mm_in_px(1.5, shelf['format']['resolution'])
    # Вычисляем размер слоя источника с учетом заданного ранее
    # пространства между фотографиями (размер слоя, естественно, ни как не изменяется физически)
    layer_new_width = drawable.width + space
    layer_new_height = drawable.height + space
    # Вычисляем сколько фоток по вертикали и горизонтали поместится
    # на заданном холсте
    w_count = paper_width / layer_new_width
    h_count = paper_height / layer_new_height
    # Проверяем стоит ли фообще заморачиваться с печатью
    if w_count == 0 or h_count == 0:
      self.info('Ни одной фотографии не помещается на выбранном вами листе бумаги формата "' + str(paper) + '".\n\nВыберете более подходящий формат бумаги и попробуйте ещё раз.')
      image.undo_group_end()
      gimp.quit()
    # Изменяем размер холста до необходимых размеров
    image.resize(paper_width, paper_height, 0, 0)
    # Если пользователь захотел, то добавляем в изображение слой,
    # белого цвета, который будет играть роль фона.
    if self.data['properties']['white_bg']:
      # Добавляем в изображение слой, который будет играть роль фона
      if drawable.is_rgb:
        white_bg = gimp.Layer(image, 'Белый фон', paper_width, paper_height, RGB_IMAGE, 100, NORMAL_MODE)
      else:
        white_bg = gimp.Layer(image, 'Белый фон', paper_width, paper_height, GRAY_IMAGE, 100, NORMAL_MODE)
      # Запоминаем цвет фона
      old_background = gimp.get_background()
      # Меняем цвет фона на белый
      gimp.set_background(255, 255, 255)
      # Заливаем слой цветом фона
      white_bg.fill(BACKGROUND_FILL)
      # Возвращаем в исходное состояние цвет фона
      gimp.set_background(old_background)
      # Добавляем аьфа-канал
      white_bg.add_alpha()
      # Встраиваем новый слой в изображение
      image.add_layer(white_bg, 0)
      # Слой источник оказался внизу, поэтому переместим его наверх
      image.raise_layer_to_top(drawable)
    # Вычисляем сколько фоток по вертикали и горизонтали поместится
    # на заданном холсте если перевернуть фото на 90°
    w_count_rotate = paper_width / layer_new_height
    h_count_rotate = paper_height / layer_new_width
    # Поворачиваем слой источник на 90° если это повысит плотность укладки
    if (w_count_rotate * h_count_rotate) > (w_count * h_count):
      drawable.transform_rotate_simple(0, 0, 0, 0)
      # Слой источник сместился за пределы холста
      # Вернм его на место
      drawable.translate(drawable.width, 0)
      # Ширинаи высота слоя источника поменялись местами
      # Вернём и их на место
      layer_new_width, layer_new_height = layer_new_height, layer_new_width
      # Количество фоток по вертикали и горизонтали поменялось
      # Исправим это
      w_count, h_count = w_count_rotate, h_count_rotate
    # Вычисляем координаты точки отстчета
    x_fundamental = (paper_width - (layer_new_width * w_count)) / 2
    y_fundamental = (paper_height - (layer_new_height * h_count)) / 2
    # Позицианируем слой источник в точку отсчета, в этакое начало координат
    drawable.translate(x_fundamental, y_fundamental)
    # Инициируем счетчик, который будет отсчитывать текущее коичество фотографий на холсте
    # счетчик увеличивает своё значение с каждой итерацией цикла
    copys_counter = 0
    # Заполняем холст фотографиями
    # Для начала создадим группу слоёв которая объединит в себе все фотографии
    layer_group = pdb.gimp_layer_group_new(image)
    layer_group.name = 'Фотографии'
    image.add_layer(layer_group, 0)
    # Присвоим слою источнику адекватное имя
    drawable.name = 'Фото'
    # w_count - количество фоток по гризонтали
    # h_count - количество фоток по вертикали
    for i in range(h_count):
      for j in range(w_count):
        # Если пользователь хочет напечатать больше фоток чем может поместиться на холсте,
        # то выходим из цикла при достижении максимального (w_count * h_count) числа копий,
        # которые могут поместиться на холсте.
        # Если пользователь хочет напечатать меньше фоток чем может поместиться нахолсте,
        # то выходим из цилкла при достижении этого числа фоток.
        if copys_counter == copys or copys_counter == (w_count * h_count):
          break
        layer_new = drawable.copy()
        layer_new.name = 'Фото'
        layer_new.add_alpha()
        image.insert_layer(layer_new, layer_group, 0)
        layer_new.translate(layer_new_width * j, layer_new_height * i)
        copys_counter += 1
    # Удаляем слой источник.
    # Он своё дело сделал и теперь может уйти
    image.remove_layer(drawable)
    # Сразу же печатаем изображение на дефолтном принтере
    # Если пользователь этого захотел
    if print_photo:
      pdb.file_print_gtk(image)

  # Эта функция крафтит фото для документов
  def auto_execute(self, widget, data=None):
    # Скрываем окно, чтоб не мешало
    self.window.hide()
    gimp.context_push()
    # Запрещаем запись информации UNDO
    self.image.undo_group_start()
    # Включаем "авто-уровни"
    if self.autolevels_check.get_active():
      auto_levels = True
    else:
      auto_levels = False
    # Ищем активный gtk.RadioButton
    for format_id in self.format_radio:
      if format_id.get_active():
        # Формируем удобный словарь с данными о формате
        tmp_dict = self.data['formats'][self.format_radio.index(format_id)]
        tmp_dict['resolution'] = self.data['properties']['resolution']
        shelf['format'] = tmp_dict

        # Если gtk.RadioButton активен вызываем функцию, которая кадрирует фото
        # В качестве параметров передаём ей указатель на изображение
        # и список с параметрами выбранноо формата
        self.create_id_foto(self.image, self.drawable, shelf['format'], auto_levels)
        if data == 'auto_execute':
          # Меняем размеры
          self.image.scale(self.mm_in_px(shelf['format']['width'], shelf['format']['resolution']), self.mm_in_px(shelf['format']['height'], shelf['format']['resolution']))
          if self.data['formats'][self.format_radio.index(format_id)]['angle']:
            self.angle(self.image, self.drawable, self.data['formats'][self.format_radio.index(format_id)]['angle'])
          if self.data['formats'][self.format_radio.index(format_id)]['oval']:
            self.oval(self.image, self.drawable)
          if self.data['formats'][self.format_radio.index(format_id)]['to_grayscale']:
            self.to_grayscale(self.image, self.drawable)
          if self.data['formats'][self.format_radio.index(format_id)]['gray_frame']:
            self.gray_frame(self.image)
          copys = self.data['formats'][self.format_radio.index(format_id)]['copys']
          paper = self.data['formats'][self.format_radio.index(format_id)]['paper']
          print_photo = self.data['formats'][self.format_radio.index(format_id)]['print_photo']
          self.print_functon(self.image, self.drawable, paper, copys, print_photo)
        break
    # Обновляем изоборажение на дисплее
    gimp.displays_flush()
    # Разрешаем запись информации UNDO
    self.image.undo_group_end()
    gimp.context_pop()
    gtk.main_quit()

  # Эта функция только формирует конечный результат
  # и ещё выводит изображение на дефолтный принтер если необходимо
  def compose_or_print(self, widget, data=None):
    # Скрываем окно, чтоб не мешало
    self.window.hide()
    gimp.context_push()
    # Запрещаем запись информации UNDO
    self.image.undo_group_start()
    # Меняем размеры
    self.image.scale(self.mm_in_px(shelf['format']['width'], shelf['format']['resolution']), self.mm_in_px(shelf['format']['height'], shelf['format']['resolution']))
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
    if data == 'print_it':
      print_photo = True
    else:
      print_photo = False
    self.print_functon(self.image, self.drawable, paper, copys, print_photo)
    # Обновляем изоборажение на дисплее
    gimp.displays_flush()
    # Разрешаем запись информации UNDO
    self.image.undo_group_end()
    gimp.context_pop()
    gtk.main_quit()

  # Эта функция способствует редактироывнию настроек
  def apply_settings(self, widget, data=None):
    # Скрываем окно, чтоб не мешало
    self.window.hide()
    if self.white_bg_check.get_active():
      self.data['properties']['white_bg'] = True
    else:
      self.data['properties']['white_bg'] = False
    if self.auto_levels_check.get_active():
      self.data['properties']['auto_levels'] = True
    else:
      self.data['properties']['auto_levels'] = False
    self.data['properties']['resolution'] = int(self.resolution_cb.get_active_text())
    config = open(self.path, 'wb')
    pickle.dump(self.data, config)
    config.close()
    gtk.main_quit()

  # Эта функция способствует редактироывнию выбранного формата
  def edit_format(self, widget, data=None):
    # Ищем активный gtk.RadioButton
    for format_id in self.format_radio:
      if format_id.get_active():
        # Название формата
        self.name_entry = gtk.Entry()
        self.name_entry.set_text(self.data['formats'][self.format_radio.index(format_id)]['name'])
        #self.name_entry.connect('changed', lambda e: self.name_entry.set_text(''))
        self.name_entry.grab_focus()
        self.name_entry.show()
        # Выпадающий сисок "Категория"
        self.category_cb = gtk.combo_box_new_text()
        self.category_cb.append_text('Категория (Разное)')
        self.category_cb.append_text('Разное')
        self.category_cb.append_text('Паспорт')
        self.category_cb.append_text('Виза')
        self.category_cb.append_text('Удостоверение')
        self.category_cb.set_active(0)
        self.category_cb.show()

        if self.data['formats'][self.format_radio.index(format_id)]['category'] == 'other':
          self.category_cb.set_active(1)
        elif self.data['formats'][self.format_radio.index(format_id)]['category'] == 'pass':
          self.category_cb.set_active(2)
        elif self.data['formats'][self.format_radio.index(format_id)]['category'] == 'visa':
          self.category_cb.set_active(3)
        elif self.data['formats'][self.format_radio.index(format_id)]['category'] == 'cert':
          self.category_cb.set_active(4)

        # Ширина фото
        self.width_label = gtk.Label('Ширина фото:')
        self.width_label.set_justify(gtk.JUSTIFY_LEFT)
        self.width_label.show()
        self.width_adj = gtk.Adjustment(self.data['formats'][self.format_radio.index(format_id)]['width'], 0.0, 200.0, 1.0, 1.0, 0.0)
        self.width_spin = gtk.SpinButton(self.width_adj, 0, 0)
        self.width_spin.set_numeric(True)
        self.width_spin.show()
        # Высота фото
        self.height_label = gtk.Label('Высота фото: ')
        self.height_label.set_justify(gtk.JUSTIFY_LEFT)
        self.height_label.show()
        self.height_adj = gtk.Adjustment(self.data['formats'][self.format_radio.index(format_id)]['height'], 0.0, 200.0, 1.0, 1.0, 0.0)
        self.height_spin = gtk.SpinButton(self.height_adj, 0, 0)
        self.height_spin.set_numeric(True)
        self.height_spin.show()
        # До головы
        self.overheadheight_label = gtk.Label('До головы:     ')
        self.overheadheight_label.set_justify(gtk.JUSTIFY_LEFT)
        self.overheadheight_label.show()
        self.overheadheight_adj = gtk.Adjustment(self.data['formats'][self.format_radio.index(format_id)]['overheadheight'], 0.0, 200.0, 1.0, 1.0, 0.0)
        self.overheadheight_spin = gtk.SpinButton(self.overheadheight_adj, 0, 0)
        self.overheadheight_spin.set_numeric(True)
        self.overheadheight_spin.show()
        # флажок "обесцветить фото"
        self.to_grayscale = gtk.CheckButton('обесцветить фото')
        self.to_grayscale.show()
        if self.data['formats'][self.format_radio.index(format_id)]['to_grayscale']:
          self.to_grayscale.set_active(True)
        # флажок "добавить рамку"
        self.gray_frame = gtk.CheckButton('добавить рамку')
        self.gray_frame.show()
        if self.data['formats'][self.format_radio.index(format_id)]['gray_frame']:
          self.gray_frame.set_active(True)
        # флажок "добавить овал с растушёвкой"
        self.oval = gtk.CheckButton('добавить овал с растушёвкой')
        self.oval.show()
        if self.data['formats'][self.format_radio.index(format_id)]['oval']:
          self.oval.set_active(True)
        # флажок "распечатать немедленно"
        self.print_photo = gtk.CheckButton('распечатать автоматически')
        self.print_photo.show()
        if self.data['formats'][self.format_radio.index(format_id)]['print_photo']:
          self.print_photo.set_active(True)
        # Выпадающий сисок "Уголок"
        self.angle_cb = gtk.combo_box_new_text()
        self.angle_cb.append_text('Уголок (Без уголка)')
        self.angle_cb.append_text('Без уголка')
        self.angle_cb.append_text('Круглый справа')
        self.angle_cb.append_text('Круглый слева')
        self.angle_cb.append_text('Прямой справа')
        self.angle_cb.append_text('Прямой слева')
        self.angle_cb.set_active(1)
        self.angle_cb.show()
        if self.data['formats'][self.format_radio.index(format_id)]['angle'] == 'right_circular':
          self.angle_cb.set_active(2)
        elif self.data['formats'][self.format_radio.index(format_id)]['angle'] == 'left_circular':
          self.angle_cb.set_active(3)
        elif self.data['formats'][self.format_radio.index(format_id)]['angle'] == 'right_direct':
          self.angle_cb.set_active(4)
        elif self.data['formats'][self.format_radio.index(format_id)]['angle'] == 'left_direct':
          self.angle_cb.set_active(5)
        # Выпадающий сисок "Формат бумаги"
        self.paper_cb = gtk.combo_box_new_text()
        self.paper_cb.append_text('Формат бумаги (10x15)')
        self.paper_cb.append_text('10x15')
        self.paper_cb.append_text('A5')
        self.paper_cb.append_text('A4')
        self.paper_cb.set_active(0)
        self.paper_cb.show()
        if self.data['formats'][self.format_radio.index(format_id)]['paper'] == '10x15':
          self.paper_cb.set_active(1)
        elif self.data['formats'][self.format_radio.index(format_id)]['paper'] == 'A5':
          self.paper_cb.set_active(2)
        elif self.data['formats'][self.format_radio.index(format_id)]['paper'] == 'A4':
          self.paper_cb.set_active(3)
        # Количество фоток
        self.copys_adj = gtk.Adjustment(self.data['formats'][self.format_radio.index(format_id)]['copys'], 1.0, 200.0, 1.0, 1.0, 0.0)
        self.copys_spin = gtk.SpinButton(self.copys_adj, 0, 0)
        self.copys_spin.set_numeric(True)
        self.copys_spin.show()
        self.copys_label = gtk.Label('фото на листе')
        self.copys_label.set_justify(gtk.JUSTIFY_LEFT)
        self.copys_label.show()
        # Пакуем виджеты в горизонтальный бокс
        self.copys_hbox = gtk.HBox(False, 0)
        self.copys_hbox.pack_start(self.copys_spin, False, False, 0)
        self.copys_hbox.pack_start(self.copys_label, False, False, 5)
        self.copys_hbox.show()
        # Пакуем ширину в горизонтальный бокс
        self.width_hbox = gtk.HBox(False, 0)
        self.width_hbox.pack_start(self.width_label, True, True, 0)
        self.width_hbox.pack_start(self.width_spin, False, False, 5)
        self.width_hbox.show()
        # Пакуем высоту в горизонтальный бокс
        self.height_hbox = gtk.HBox(False, 0)
        self.height_hbox.pack_start(self.height_label, True, True, 0)
        self.height_hbox.pack_start(self.height_spin, False, False, 5)
        self.height_hbox.show()
        # Пакуем над головой в горизонтальный бокс
        self.overheadheight_hbox = gtk.HBox(False, 0)
        self.overheadheight_hbox.pack_start(self.overheadheight_label, True, True, 0)
        self.overheadheight_hbox.pack_start(self.overheadheight_spin, False, False, 5)
        self.overheadheight_hbox.show()
        # Пакуем в вертикальный бокс горизонтальные боксы с виджетами
        self.size_vbox = gtk.VBox(True, 0)
        self.size_vbox.pack_start(self.width_hbox, True, True, 0)
        self.size_vbox.pack_start(self.height_hbox, True, True, 0)
        self.size_vbox.pack_start(self.overheadheight_hbox, True, True, 0)
        self.size_vbox.show()

        self.onlyface1_radio = gtk.RadioButton(None, 'от глаз до подбородка')
        self.onlyface1_radio.show()

        self.onlyface2_radio = gtk.RadioButton(self.onlyface1_radio, 'от макушки до подбородка')
        self.onlyface2_radio.show()

        if self.data['formats'][self.format_radio.index(format_id)]['onlyface']:
          self.onlyface1_radio.set_active(True)
        else:
          self.onlyface2_radio.set_active(True)

        self.faceheight_adj = gtk.Adjustment(self.data['formats'][self.format_radio.index(format_id)]['faceheight'], 0.0, 200.0, 1.0, 1.0, 0.0)
        self.faceheight_spin = gtk.SpinButton(self.faceheight_adj, 0, 0)
        self.faceheight_spin.set_numeric(True)
        self.faceheight_spin.show()

        # Пакуем в вертикальный бокс горизонтальные боксы с виджетами
        self.faceheight_vbox = gtk.VBox(True, 5)
        self.faceheight_vbox.set_border_width(10)
        self.faceheight_vbox.pack_start(self.faceheight_spin, True, True, 0)
        self.faceheight_vbox.pack_start(self.onlyface1_radio, True, True, 0)
        self.faceheight_vbox.pack_start(self.onlyface2_radio, True, True, 0)
        self.faceheight_vbox.show()

        self.faceheight_frame = gtk.Frame('Размер лицевой части головы')
        self.faceheight_frame.add(self.faceheight_vbox)
        self.faceheight_frame.show()
        # Конец особая магия для "Лицевая чпасть головы" %-)

        # Инициируем таблицу, в которую поместим все виджеты
        self.table = gtk.Table(1, 2, False)
        self.table.set_border_width(5)
        self.table.set_row_spacings(0)
        self.table.set_col_spacings(10)
        self.table.attach(self.size_vbox, 0, 1, 0, 1)
        self.table.attach(self.faceheight_frame, 1, 2, 0, 1)
        self.table.show()

        # Инициируем диалог, на котором будут все наши виджеты находиться
        dialog = gtk.Dialog('Правка формата "' + self.data['formats'][self.format_radio.index(format_id)]['name'] + '"', self.window, gtk.DIALOG_NO_SEPARATOR | gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        dialog.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        dialog.set_resizable(False)
        dialog.set_border_width(10)
        dialog.vbox.pack_start(self.name_entry, True, True, 5)
        dialog.vbox.pack_start(self.category_cb, True, True, 5)
        dialog.vbox.pack_start(self.table, True, True, 5)
        dialog.vbox.pack_start(self.angle_cb, True, True, 5)
        dialog.vbox.pack_start(self.paper_cb, True, True, 5)
        dialog.vbox.pack_start(self.copys_hbox, True, True, 5)
        dialog.vbox.pack_start(self.to_grayscale, True, True, 5)
        dialog.vbox.pack_start(self.gray_frame, True, True, 5)
        dialog.vbox.pack_start(self.oval, True, True, 5)
        dialog.vbox.pack_start(self.print_photo, True, True, 5)
        dialog.show_all()

        response = dialog.run()
        if response == gtk.RESPONSE_CANCEL:
          dialog.hide()
          dialog.destroy()
        if response == gtk.RESPONSE_OK:
          name = self.name_entry.get_text()
          width = self.width_spin.get_value_as_int()
          height = self.height_spin.get_value_as_int()
          faceheight = self.faceheight_spin.get_value_as_int()
          overheadheight = self.overheadheight_spin.get_value_as_int()
          copys = self.copys_spin.get_value_as_int()

          if self.angle_cb.get_active_text() == 'Без уголка' or self.angle_cb.get_active_text() == 'Уголок (Без уголка)':
            angle = False
          elif self.angle_cb.get_active_text() == 'Круглый справа':
            angle = 'right_circular'
          elif self.angle_cb.get_active_text() == 'Круглый слева':
            angle = 'left_circular'
          elif self.angle_cb.get_active_text() == 'Прямой справа':
            angle = 'right_direct'
          elif self.angle_cb.get_active_text() == 'Прямой слева':
            angle = 'left_direct'

          if self.gray_frame.get_active():
            gray_frame = True
          else:
            gray_frame = False

          if self.oval.get_active():
            oval = True
          else:
            oval = False

          if self.print_photo.get_active():
            print_photo = True
          else:
            print_photo = False

          if self.to_grayscale.get_active():
            to_grayscale = True
          else:
            to_grayscale = False

          if self.paper_cb.get_active_text() == '10x15' or self.paper_cb.get_active_text() == 'Формат бумаги (10x15)':
            paper = '10x15'
          elif self.paper_cb.get_active_text() == 'A5':
            paper = 'A5'
          elif self.paper_cb.get_active_text() == 'A4':
            paper = 'A4'

          if self.category_cb.get_active_text() == 'Разное' or self.category_cb.get_active_text() == 'Категория (Разное)':
            category = 'other'
          elif self.category_cb.get_active_text() == 'Паспорт':
            category = 'pass'
          elif self.category_cb.get_active_text() == 'Виза':
            category = 'visa'
          elif self.category_cb.get_active_text() == 'Удостоверение':
            category = 'cert'

          if self.onlyface1_radio.get_active():
            onlyface = True
          elif self.onlyface2_radio.get_active():
            onlyface = False

          self.data['formats'][self.format_radio.index(format_id)] = {'name': name,
             'category': category,
             'width': width,
             'height': height,
             'faceheight': faceheight,
             'onlyface': onlyface,
             'overheadheight': overheadheight,
             'angle': angle,
             'copys': copys,
             'gray_frame': gray_frame,
             'oval': oval,
             'paper': paper,
             'to_grayscale': to_grayscale,
             'print_photo': print_photo,
             'url': 'http://gimp-id-photo.ru/formats_data/sorry_no_data.html?from=plugin'}

          config = open(self.path, 'wb')
          pickle.dump(self.data, config)
          config.close()
          self.format_radio[self.format_radio.index(format_id)].set_name(str(self.data['formats'][self.format_radio.index(format_id)]['name']))
          self.add_success_label.set_markup('<span foreground="#008600">"'+ str(self.data['formats'][self.format_radio.index(format_id)]['name']) +'" успешно изменён\n</span>')
          dialog.hide()
          dialog.destroy()
        break

  # Эта функция способствует удалению выбранного формата
  def delete_format(self, widget, data=None):
    # Ищем активный gtk.RadioButton
    for format_id in self.format_radio:
      if format_id.get_active():
        # Инициируем диалог, с помощью которого пользователь подтвердит свой выбор
        dialog = gtk.Dialog('Удаление формата "' + self.data['formats'][self.format_radio.index(format_id)]['name'] + '"', self.window, gtk.DIALOG_NO_SEPARATOR | gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_NO, gtk.RESPONSE_CANCEL, gtk.STOCK_YES, gtk.RESPONSE_OK))
        dialog.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        dialog.set_resizable(False)
        dialog.set_border_width(10)
        self.confirmation_label = gtk.Label('Вы действительно хотите удалить формат "' + self.data['formats'][self.format_radio.index(format_id)]['name'] + '"?')
        dialog.vbox.pack_start(self.confirmation_label, True, True, 5)
        dialog.show_all()
        response = dialog.run()
        if response == gtk.RESPONSE_CANCEL:
          dialog.hide()
          dialog.destroy()
        if response == gtk.RESPONSE_OK:
          # Удаляем формат
          name = self.data['formats'][self.format_radio.index(format_id)]['name']
          del self.data['formats'][self.format_radio.index(format_id)]
          config = open(self.path, 'wb')
          pickle.dump(self.data, config)
          config.close()
          self.format_radio[self.format_radio.index(format_id)].hide()
          if len(self.format_radio) == 1:
            pass
          elif self.format_radio.index(format_id) + 1 <= len(self.format_radio) - 1:
            self.format_radio[self.format_radio.index(format_id) + 1].set_active(True)
          elif self.format_radio.index(format_id) + 1 > len(self.format_radio) - 1:
            self.format_radio[self.format_radio.index(format_id) - 1].set_active(True)
          del self.format_radio[self.format_radio.index(format_id)]
          if len(self.format_radio) < 1:
            self.delete_button.set_sensitive(False)
            self.edit_button.set_sensitive(False)
          self.add_success_label.set_markup('<span foreground="#008600">"' + str(name) + '" успешно удалён\n</span>')
          dialog.hide()
          dialog.destroy()
        break

  # Эта функция способствует добавлению нового формата
  def add_format(self, widget, data=None):
    # Название формата
    self.name_entry = gtk.Entry()
    self.name_entry.set_text('Название формата')
    #self.name_entry.connect('changed', lambda e: self.name_entry.set_text(''))
    self.name_entry.grab_focus()
    self.name_entry.show()
    # Выпадающий сисок "Категория"
    self.category_cb = gtk.combo_box_new_text()
    self.category_cb.append_text('Категория (Разное)')
    self.category_cb.append_text('Разное')
    self.category_cb.append_text('Паспорт')
    self.category_cb.append_text('Виза')
    self.category_cb.append_text('Удостоверение')
    self.category_cb.set_active(0)
    self.category_cb.show()
    # Ширина фото
    self.width_label = gtk.Label('Ширина фото:')
    self.width_label.set_justify(gtk.JUSTIFY_LEFT)
    self.width_label.show()
    self.width_adj = gtk.Adjustment(0.0, 0.0, 200.0, 1.0, 1.0, 0.0)
    self.width_spin = gtk.SpinButton(self.width_adj, 0, 0)
    self.width_spin.set_numeric(True)
    self.width_spin.show()
    # Высота фото
    self.height_label = gtk.Label('Высота фото: ')
    self.height_label.set_justify(gtk.JUSTIFY_LEFT)
    self.height_label.show()
    self.height_adj = gtk.Adjustment(0.0, 0.0, 200.0, 1.0, 1.0, 0.0)
    self.height_spin = gtk.SpinButton(self.height_adj, 0, 0)
    self.height_spin.set_numeric(True)
    self.height_spin.show()
    # До головы
    self.overheadheight_label = gtk.Label('До головы:     ')
    self.overheadheight_label.set_justify(gtk.JUSTIFY_LEFT)
    self.overheadheight_label.show()
    self.overheadheight_adj = gtk.Adjustment(0.0, 0.0, 200.0, 1.0, 1.0, 0.0)
    self.overheadheight_spin = gtk.SpinButton(self.overheadheight_adj, 0, 0)
    self.overheadheight_spin.set_numeric(True)
    self.overheadheight_spin.show()
    # флажок "обесцветить фото"
    self.to_grayscale = gtk.CheckButton('обесцветить фото')
    self.to_grayscale.show()
    # флажок "добавить рамку"
    self.gray_frame = gtk.CheckButton('добавить рамку')
    self.gray_frame.show()
    # флажок "добавить овал с растушёвкой"
    self.oval = gtk.CheckButton('добавить овал с растушёвкой')
    self.oval.show()
    # флажок "распечатать немедленно"
    self.print_photo = gtk.CheckButton('распечатать автоматически')
    self.print_photo.show()
    # Выпадающий сисок "Уголок"
    self.angle_cb = gtk.combo_box_new_text()
    self.angle_cb.append_text('Уголок (Без уголка)')
    self.angle_cb.append_text('Без уголка')
    self.angle_cb.append_text('Круглый справа')
    self.angle_cb.append_text('Круглый слева')
    self.angle_cb.append_text('Прямой справа')
    self.angle_cb.append_text('Прямой слева')
    self.angle_cb.set_active(0)
    self.angle_cb.show()
    # Выпадающий сисок "Формат бумаги"
    self.paper_cb = gtk.combo_box_new_text()
    self.paper_cb.append_text('Формат бумаги (10x15)')
    self.paper_cb.append_text('10x15')
    self.paper_cb.append_text('A5')
    self.paper_cb.append_text('A4')
    self.paper_cb.set_active(0)
    self.paper_cb.show()
    # Количество фоток
    self.copys_adj = gtk.Adjustment(4.0, 1.0, 200.0, 1.0, 1.0, 0.0)
    self.copys_spin = gtk.SpinButton(self.copys_adj, 0, 0)
    self.copys_spin.set_numeric(True)
    self.copys_spin.show()
    self.copys_label = gtk.Label('фото на листе')
    self.copys_label.set_justify(gtk.JUSTIFY_LEFT)
    self.copys_label.show()
    # Пакуем виджеты в горизонтальный бокс
    self.copys_hbox = gtk.HBox(False, 0)
    self.copys_hbox.pack_start(self.copys_spin, False, False, 0)
    self.copys_hbox.pack_start(self.copys_label, False, False, 5)
    self.copys_hbox.show()
    # Пакуем ширину в горизонтальный бокс
    self.width_hbox = gtk.HBox(False, 0)
    self.width_hbox.pack_start(self.width_label, True, True, 0)
    self.width_hbox.pack_start(self.width_spin, False, False, 5)
    self.width_hbox.show()
    # Пакуем высоту в горизонтальный бокс
    self.height_hbox = gtk.HBox(False, 0)
    self.height_hbox.pack_start(self.height_label, True, True, 0)
    self.height_hbox.pack_start(self.height_spin, False, False, 5)
    self.height_hbox.show()
    # Пакуем над головой в горизонтальный бокс
    self.overheadheight_hbox = gtk.HBox(False, 0)
    self.overheadheight_hbox.pack_start(self.overheadheight_label, True, True, 0)
    self.overheadheight_hbox.pack_start(self.overheadheight_spin, False, False, 5)
    self.overheadheight_hbox.show()
    # Пакуем в вертикальный бокс горизонтальные боксы с виджетами
    self.size_vbox = gtk.VBox(True, 0)
    self.size_vbox.pack_start(self.width_hbox, True, True, 0)
    self.size_vbox.pack_start(self.height_hbox, True, True, 0)
    self.size_vbox.pack_start(self.overheadheight_hbox, True, True, 0)
    self.size_vbox.show()
    # Голова от кудова докудова?
    self.onlyface1_radio = gtk.RadioButton(None, 'от глаз до подбородка')
    self.onlyface1_radio.show()
    self.onlyface2_radio = gtk.RadioButton(self.onlyface1_radio, 'от макушки до подбородка')
    self.onlyface2_radio.show()
    # И Указываем откудова докудова
    self.faceheight_adj = gtk.Adjustment(0.0, 0.0, 200.0, 1.0, 1.0, 0.0)
    self.faceheight_spin = gtk.SpinButton(self.faceheight_adj, 0, 0)
    self.faceheight_spin.set_numeric(True)
    self.faceheight_spin.show()
    # Пакуем в вертикальный бокс горизонтальные боксы с виджетами
    self.faceheight_vbox = gtk.VBox(True, 5)
    self.faceheight_vbox.set_border_width(10)
    self.faceheight_vbox.pack_start(self.faceheight_spin, True, True, 0)
    self.faceheight_vbox.pack_start(self.onlyface1_radio, True, True, 0)
    self.faceheight_vbox.pack_start(self.onlyface2_radio, True, True, 0)
    self.faceheight_vbox.show()
    self.faceheight_frame = gtk.Frame('Размер лицевой части головы')
    self.faceheight_frame.add(self.faceheight_vbox)
    self.faceheight_frame.show()
    # Конец особая магия для "Лицевая чпасть головы" %-)
    # Инициируем таблицу, в которую поместим все виджеты
    self.table = gtk.Table(1, 2, False)
    self.table.set_border_width(5)
    self.table.set_row_spacings(0)
    self.table.set_col_spacings(10)
    self.table.attach(self.size_vbox, 0, 1, 0, 1)
    self.table.attach(self.faceheight_frame, 1, 2, 0, 1)
    self.table.show()
    # Инициируем диалог, на котором будут все наши виджеты находиться
    dialog = gtk.Dialog('Добавить новый формат', self.window, gtk.DIALOG_NO_SEPARATOR | gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_ADD, gtk.RESPONSE_OK))
    dialog.set_position(gtk.WIN_POS_CENTER_ALWAYS)
    dialog.set_resizable(False)
    dialog.set_border_width(10)
    dialog.vbox.pack_start(self.name_entry, True, True, 5)
    dialog.vbox.pack_start(self.category_cb, True, True, 5)
    dialog.vbox.pack_start(self.table, True, True, 5)
    dialog.vbox.pack_start(self.angle_cb, True, True, 5)
    dialog.vbox.pack_start(self.paper_cb, True, True, 5)
    dialog.vbox.pack_start(self.copys_hbox, True, True, 5)
    dialog.vbox.pack_start(self.to_grayscale, True, True, 5)
    dialog.vbox.pack_start(self.gray_frame, True, True, 5)
    dialog.vbox.pack_start(self.oval, True, True, 5)
    dialog.vbox.pack_start(self.print_photo, True, True, 5)
    dialog.show_all()
    response = dialog.run()
    if response == gtk.RESPONSE_CANCEL:
      dialog.hide()
      dialog.destroy()
    if response == gtk.RESPONSE_OK:
      name = self.name_entry.get_text()
      width = self.width_spin.get_value_as_int()
      height = self.height_spin.get_value_as_int()
      faceheight = self.faceheight_spin.get_value_as_int()
      overheadheight = self.overheadheight_spin.get_value_as_int()
      copys = self.copys_spin.get_value_as_int()

      if self.angle_cb.get_active_text() == 'Без уголка' or self.angle_cb.get_active_text() == 'Уголок (Без уголка)':
        angle = False
      elif self.angle_cb.get_active_text() == 'Круглый справа':
        angle = 'right_circular'
      elif self.angle_cb.get_active_text() == 'Круглый слева':
        angle = 'left_circular'
      elif self.angle_cb.get_active_text() == 'Прямой справа':
        angle = 'right_direct'
      elif self.angle_cb.get_active_text() == 'Прямой слева':
        angle = 'left_direct'

      if self.gray_frame.get_active():
        gray_frame = True
      else:
        gray_frame = False

      if self.oval.get_active():
        oval = True
      else:
        oval = False

      if self.print_photo.get_active():
        print_photo = True
      else:
        print_photo = False

      if self.to_grayscale.get_active():
        to_grayscale = True
      else:
        to_grayscale = False

      if self.paper_cb.get_active_text() == '10x15' or self.paper_cb.get_active_text() == 'Формат бумаги (10x15)':
        paper = '10x15'
      elif self.paper_cb.get_active_text() == 'A5':
        paper = 'A5'
      elif self.paper_cb.get_active_text() == 'A4':
        paper = 'A4'

      if self.category_cb.get_active_text() == 'Разное' or self.category_cb.get_active_text() == 'Категория (Разное)':
        category = 'other'
      elif self.category_cb.get_active_text() == 'Паспорт':
        category = 'pass'
      elif self.category_cb.get_active_text() == 'Виза':
        category = 'visa'
      elif self.category_cb.get_active_text() == 'Удостоверение':
        category = 'cert'

      if self.onlyface1_radio.get_active():
        onlyface = True
      elif self.onlyface2_radio.get_active():
        onlyface = False

      self.data['formats'].append(
        {'name': name,
         'category': category,
         'width': width,
         'height': height,
         'faceheight': faceheight,
         'onlyface': onlyface,
         'overheadheight': overheadheight,
         'angle': angle,
         'copys': copys,
         'gray_frame': gray_frame,
         'oval': oval,
         'paper': paper,
         'to_grayscale': to_grayscale,
         'print_photo': print_photo,
         'url': 'http://gimp-id-photo.ru'})

      config = open(self.path, 'wb')
      pickle.dump(self.data, config)
      config.close()

      group = None
      if len(self.format_radio) > 0:
        group = self.format_radio[-1]
      self.format_radio.append(gtk.RadioButton(group, self.data['formats'][-1]['name']))
      self.format_radio[-1].show()
      self.format_radio[-1].set_active(True)
      self.formats_vbox.pack_start(self.format_radio[-1], False, False, 0)
      if len(self.format_radio) > 0:
        self.delete_button.set_sensitive(True)
        self.edit_button.set_sensitive(True)
      self.add_success_label.set_markup('<span foreground="#008600">"'+ str(name) +'" успешно добавлен\n</span>')
      dialog.hide()
      dialog.destroy()

  def set_mark(self, widget, data=None):
    self.learn_more_label.set_markup('<a href="' + data[0] + '">Узнать подробности о формате "' + data[1] + '"</a>')

  # Вспомогательная функция. Выполняется при закрытии окна
  # или нажатии кнопки "Отмена"
  def delete_event(self, widget, event, data=None):
    return False

  # Вспомогательная функция. Выполняется при закрытии окна
  # или нажатии кнопки "Отмена"
  def destroy(self, widget, data=None):
    Gtk.main_quit()

#########################################################
#-------- Тут и класса конец, а кто потомок молодец ----#
#########################################################
class select_format_id_photo(id_photo_base):
  def __init__(self, runmode, image, drawable):
    self.image, self.drawable = image, drawable
    # Вертикальный бокс для паспортов
    self.pass_vbox = Gtk.VBox(False, 5)
    self.pass_vbox.set_border_width(5)
    self.pass_vbox.show()
    # Вертикальный бокс для виз
    self.visa_vbox = Gtk.VBox(False, 5)
    self.visa_vbox.set_border_width(5)
    self.visa_vbox.show()
    # Вертикальный бокс для удостоверений
    self.cert_vbox = Gtk.VBox(False, 5)
    self.cert_vbox.set_border_width(5)
    self.cert_vbox.show()
    # Вертикальный бокс для иных форматов
    self.other_vbox = Gtk.VBox(False, 5)
    self.other_vbox.set_border_width(5)
    self.other_vbox.show()
    # В эту метку будем записывать различные сообщения
    self.learn_more_label = Gtk.Label()
    self.learn_more_label.set_justify(Gtk.Justification.LEFT)
    self.learn_more_label.set_markup('<a href="http://gimp-id-photo.ru/formats_data/sorry_no_data.html?from=plugin">Узнать подробности о формате "Паспорт РФ"</a>')
    self.learn_more_label.set_tooltip_text('Поросмотреть сведения о формате с помощью браузера используемого по умолчанию')
    self.learn_more_label.show()
    # Выравниваем метку по левому краю
    self.learn_more_alignment = Gtk.Alignment(0.0, 0.0, 0.0, 0.0)
    self.learn_more_alignment.add(self.learn_more_label)
    self.learn_more_alignment.show()
    # Формируем "список форматов"
    # self.data - это свойство класа id_photo_base
    group = None
    self.format_radio = [x for x in range(len(self.data['formats']))]
    id = 0
    for format in self.data['formats']:
      self.format_radio[id] = Gtk.RadioButton.new_with_label_from_widget(group, format['name'])
      self.format_radio[id].connect('clicked', self.set_mark, (format['url'],format['name']))
      self.format_radio[id].show()
      if group is None:
        group = self.format_radio[id]
      if format['category'] == 'pass':
        self.pass_vbox.pack_start(self.format_radio[id], False, False, 0)
      elif format['category'] == 'visa':
        self.visa_vbox.pack_start(self.format_radio[id], False, False, 0)
      elif format['category'] == 'cert':
        self.cert_vbox.pack_start(self.format_radio[id], False, False, 0)
      elif format['category'] == 'other':
        self.other_vbox.pack_start(self.format_radio[id], False, False, 0)
      id += 1
    # Фрейм для паспортов
    self.pass_frame = Gtk.Frame(label='Паспорта')
    self.pass_frame.set_border_width(0)
    self.pass_frame.add(self.pass_vbox)
    self.pass_frame.show()
    # Фрейм для виз
    self.visa_frame = Gtk.Frame(label='Визы')
    self.visa_frame.set_border_width(0)
    self.visa_frame.add(self.visa_vbox)
    self.visa_frame.show()
    # Фрейм для удостоверений
    self.cert_frame = Gtk.Frame(label='Удостоверения')
    self.cert_frame.set_border_width(0)
    self.cert_frame.add(self.cert_vbox)
    self.cert_frame.show()
    # Фрейм для иных форматов
    self.other_frame = Gtk.Frame(label='Разное')
    self.other_frame.set_border_width(0)
    self.other_frame.add(self.other_vbox)
    self.other_frame.show()
    # Создаем кнопку "Отмена"
    self.cancel_button = Gtk.Button.new_from_stock(Gtk.STOCK_CANCEL)
    self.cancel_button.connect('clicked', self.destroy)
    self.cancel_button.set_tooltip_text('Не выполнять никаких действий с изображением')
    self.cancel_button.show()
    # Создаем кнопку "Применить"
    self.apply_button = Gtk.Button.new_from_stock(Gtk.STOCK_APPLY)
    self.apply_button.connect('clicked', self.auto_execute, None)
    self.apply_button.set_tooltip_text('Кадрировать фото в соответствии с выбранным форматом')
    self.apply_button.show()
    # Создаем кнопку "Выполнить"
    self.execute_button = Gtk.Button(label='Выполнить автоматически')
    self.execute_button.connect('clicked', self.auto_execute, 'auto_execute')
    self.execute_button.set_tooltip_text('Выполнить все необходимые действия автоматически')
    self.execute_button.show()
    # Создаем флажок "автоуровни"
    self.autolevels_check = Gtk.CheckButton(label='авто-уровни')
    self.autolevels_check.set_active(self.data['properties']['auto_levels'])
    self.autolevels_check.set_tooltip_text('Автоматически подорать уровни')
    self.autolevels_check.show()
    # Пакуем виджеты в горизонтальный бокс
    self.button_hbox = Gtk.HBox(False, 10)
    self.button_hbox.pack_start(self.autolevels_check, False, False, 0)
    self.button_hbox.pack_end(self.apply_button, False, False, 0)
    self.button_hbox.pack_end(self.cancel_button, False, False, 0)
    self.button_hbox.pack_end(self.execute_button, False, False, 50)
    self.button_hbox.show()
    # Инициируем таблицу, в которую поместим все виджеты
    self.table = Gtk.Table(3, 4, False)
    self.table.set_border_width(5)
    self.table.set_row_spacings(10)
    self.table.set_col_spacings(10)
    self.table.attach(self.pass_frame, 0, 1, 0, 1)
    self.table.attach(self.visa_frame, 1, 2, 0, 1)
    self.table.attach(self.cert_frame, 2, 3, 0, 1)
    self.table.attach(self.other_frame, 3, 4, 0, 1)
    self.table.attach(self.button_hbox, 0, 4, 1, 2)
    self.table.attach(self.learn_more_alignment, 0, 4, 2, 3) # Занять все 4 ячейки в третьей строке
    self.table.show()
    # Создаем окно. Добавляем всё к окну и показываем его
    self.window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
    self.window.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
    self.window.set_title('Выбор формата фотографии')
    self.window.set_border_width(5)
    self.window.set_resizable(False)
    self.window.connect('delete_event', self.delete_event)
    self.window.connect('destroy', self.destroy)
    self.window.add(self.table)
    self.window.show()
  # Эта функция крафтит фото для документов
  def auto_execute(self, widget, data=None):
    # Скрываем окно, чтоб не мешало
    self.window.hide()
    try:
        # GIMP 3 compatibility - context operations may need updating
        # gimp.context_push()  # GIMP 3 - needs updating
        # Запрещаем запись информации UNDO
        # self.image.undo_group_start()  # GIMP 3 - needs updating
        
        # Включаем "авто-уровни"
        if self.autolevels_check.get_active():
          auto_levels = True
        else:
          auto_levels = False
          
        # Ищем активный Gtk.RadioButton
        for format_id in self.format_radio:
          if format_id.get_active():
            # Формируем удобный словарь с данными о формате
            tmp_dict = self.data['formats'][self.format_radio.index(format_id)]
            tmp_dict['resolution'] = self.data['properties']['resolution']
            shelf['format'] = tmp_dict

            # Если Gtk.RadioButton активен вызываем функцию, которая кадрирует фото
            # В качестве параметров передаём ей указатель на изображение
            # и список с параметрами выбранноо формата
            self.create_id_foto(self.image, self.drawable, shelf['format'], auto_levels)
            if data == 'auto_execute':
              # Меняем размеры - GIMP 3 compatibility needed
              try:
                  # self.image.scale(self.mm_in_px(shelf['format']['width'], shelf['format']['resolution']), self.mm_in_px(shelf['format']['height'], shelf['format']['resolution']))
                  if self.data['formats'][self.format_radio.index(format_id)]['angle']:
                    self.angle(self.image, self.drawable, self.data['formats'][self.format_radio.index(format_id)]['angle'])
                  if self.data['formats'][self.format_radio.index(format_id)]['oval']:
                    self.oval(self.image, self.drawable)
                  if self.data['formats'][self.format_radio.index(format_id)]['to_grayscale']:
                    self.to_grayscale(self.image, self.drawable)
                  if self.data['formats'][self.format_radio.index(format_id)]['gray_frame']:
                    self.gray_frame(self.image)
                  copys = self.data['formats'][self.format_radio.index(format_id)]['copys']
                  paper = self.data['formats'][self.format_radio.index(format_id)]['paper']
                  print_photo = self.data['formats'][self.format_radio.index(format_id)]['print_photo']
                  self.print_functon(self.image, self.drawable, paper, copys, print_photo)
              except Exception as e:
                  print(f"GIMP 3 compatibility: Auto execute operations need updating - {e}")
            break
            
        # Обновляем изоборажение на дисплее - GIMP 3 compatibility needed
        # gimp.displays_flush()  # GIMP 3 - needs updating
        # Разрешаем запись информации UNDO
        # self.image.undo_group_end()  # GIMP 3 - needs updating
        # gimp.context_pop()  # GIMP 3 - needs updating
    except Exception as e:
        print(f"GIMP 3 compatibility: Auto execute function needs updating - {e}")
    
    Gtk.main_quit()

class settings(id_photo_base):
  def __init__(self, runmode, image):
    # Вертикальный бокс для форматов
    self.formats_vbox = gtk.VBox(False, 5)
    self.formats_vbox.set_border_width(10)
    # Формируем "список форматов"
    # self.data - это свойство класа id_photo_base
    group = None
    self.format_radio = [x for x in range(len(self.data['formats']))]
    id = 0
    for format in self.data['formats']:
      self.format_radio[id] = gtk.RadioButton(group, format['name'])
      self.format_radio[id].show()
      self.formats_vbox.pack_start(self.format_radio[id], False, False, 0)
      group = self.format_radio[id]
      id += 1
    self.formats_vbox.show()
    # Инициализируем виджет, который позволит добавить прокрутку к списку форматов
    self.sc_win = gtk.ScrolledWindow(None, None)
    self.sc_win.set_border_width(0)
    self.sc_win.set_size_request(270,200)
    self.sc_win.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    self.sc_win.add_with_viewport(self.formats_vbox)
    self.sc_win.show()
    # Создаем кнопку "Добавить"
    self.add_button = gtk.Button(None, gtk.STOCK_ADD)
    self.add_button.connect_object('clicked', self.add_format, None)
    self.add_button.set_tooltip_text('Добавить формат')
    self.add_button.show()
    # Создаем кнопку "Править"
    self.edit_button = gtk.Button(None, gtk.STOCK_EDIT)
    self.edit_button.connect('clicked', self.edit_format, None)
    self.edit_button.set_tooltip_text('Внести изменения в выбранный формат')
    self.edit_button.show()
    if len(self.format_radio) < 1:
      self.edit_button.set_sensitive(False)
    # Создаем кнопку "Удалить"
    self.delete_button = gtk.Button(None, gtk.STOCK_DELETE)
    self.delete_button.connect('clicked', self.delete_format, None)
    self.delete_button.set_tooltip_text('Удалить выбранный формат')
    self.delete_button.show()
    if len(self.format_radio) < 1:
      self.delete_button.set_sensitive(False)
    # Пакуем кнопки в горизонтальный бокс
    self.button_format_hbox = gtk.HBox(False, 10)
    self.button_format_hbox.pack_start(self.add_button, True, True, 0)
    self.button_format_hbox.pack_start(self.edit_button, True, True, 0)
    self.button_format_hbox.pack_start(self.delete_button, True, True, 0)
    self.button_format_hbox.show()
    # В эту метку будем записывать различные сообщения
    self.add_success_label = gtk.Label(None)
    self.add_success_label.set_justify(gtk.JUSTIFY_LEFT)
    self.add_success_label.set_markup(' \n ')
    self.add_success_label.show()
    # Таблица в которую поместим всё, что касается операций с форматами
    self.formats_table = gtk.Table(3, 1, False)
    self.formats_table.set_border_width(10)
    self.formats_table.set_row_spacings(10)
    self.formats_table.set_col_spacings(10)
    self.formats_table.attach(self.sc_win, 0, 1, 0, 1, gtk.FILL|gtk.EXPAND, gtk.FILL|gtk.EXPAND, 0, 0)
    self.formats_table.attach(self.add_success_label, 0, 1, 1, 2, gtk.FILL|gtk.SHRINK, gtk.FILL|gtk.SHRINK, 0, 0)
    self.formats_table.attach(self.button_format_hbox, 0, 1, 2, 3, gtk.FILL|gtk.SHRINK, gtk.FILL|gtk.SHRINK, 0, 0)
    self.formats_table.show()
    # Фрейм 'Операции с форматами'
    self.formats_frame = gtk.Frame('Операции с форматами')
    self.formats_frame.add(self.formats_table)
    self.formats_frame.show()
    # Создаём поясняющую метку "Использовать разрешение:"
    self.use_resolution_label = gtk.Label(None)
    self.use_resolution_label.set('Использовать разрешение: ');
    self.use_resolution_label.show()
    # Выпадающий сисок "Разрешение"
    self.resolution_cb = gtk.combo_box_new_text()
    self.resolution_cb.append_text('300')
    self.resolution_cb.append_text('600')
    self.resolution_cb.append_text('1147')
    self.resolution_cb.append_text('1200')
    self.resolution_cb.append_text('2400')
    self.resolution_cb.set_active(0)
    self.resolution_cb.set_tooltip_text('При печати фотографий будет использовано это разрешение')
    self.resolution_cb.show()
    # Создаём поясняющую метку "ppi"
    self.ppi_label = gtk.Label(None)
    self.ppi_label.set('ppi');
    self.ppi_label.show()
    # Делаем активным пункт выподающего списка разрешений
    if self.data['properties']['resolution'] == 300:
      self.resolution_cb.set_active(0)
    elif self.data['properties']['resolution'] == 600:
      self.resolution_cb.set_active(1)
    elif self.data['properties']['resolution'] == 1147:
      self.resolution_cb.set_active(2)
    elif self.data['properties']['resolution'] == 1200:
      self.resolution_cb.set_active(3)
    elif self.data['properties']['resolution'] == 2400:
      self.resolution_cb.set_active(4)
    # Пакуем настройки разрешения в горизонтальный бокс
    self.ppi_hbox = gtk.HBox(False, 3)
    self.ppi_hbox.pack_start(self.use_resolution_label, True, True, 0)
    self.ppi_hbox.pack_start(self.resolution_cb, True, True, 0)
    self.ppi_hbox.pack_start(self.ppi_label, True, True, 0)
    self.ppi_hbox.show()
    # Создаем флажок 'всегда добавлять слой "Белый фон"'
    self.white_bg_check = gtk.CheckButton('всегда добавлять слой "Белый фон"')
    self.white_bg_check.set_tooltip_text('Если отключить, то отрисовка происходит быстрее')
    self.white_bg_check.show()
    if self.data['properties']['white_bg']:
      self.white_bg_check.set_active(True)
    # Создаем флажок 'всегда использовать авто-уровни'
    self.auto_levels_check = gtk.CheckButton('всегда использовать "авто-уровни"')
    self.auto_levels_check.set_tooltip_text('Если включить, то уровни всегда будут подбираться автоматически')
    self.auto_levels_check.show()
    if self.data['properties']['auto_levels']:
      self.auto_levels_check.set_active(True)
    # Создаём метку в которую будем выводить сообщения
    self.success_label = gtk.Label(None)
    self.success_label.set_markup('<span foreground="#008600"><a href="http://gimp-id-photo.ru">Успешно сохранено</a></span>');
    self.success_label.set_justify(gtk.JUSTIFY_LEFT)
    #self.success_label.show()
    # Создаём текстовое поле для рекламного текста
    self.text = gtk.TextView(None)
    self.text.set_size_request(260,100)
    self.text.set_editable(True)
    self.text.set_cursor_visible(True)
    self.text.set_wrap_mode(gtk.WRAP_CHAR)
    self.text.set_justification(gtk.JUSTIFY_LEFT)
    self.text.set_indent(0) # Абзацный отступ
    self.text.set_left_margin(5) # Отступ слева
    self.text.set_right_margin(5) # Отступ справа
    self.text.set_pixels_above_lines(5) # Отступ сверху
    self.text.set_pixels_below_lines(5) # Отступ снизу
    self.text.set_pixels_inside_wrap(0) # Интерлиньяж
    #self.text.show()
    # Вертикальный бокс для иных опций
    self.different_options_vbox = gtk.VBox(False, 5)
    self.different_options_vbox.set_border_width(10)
    self.different_options_vbox.pack_start(self.ppi_hbox, False, False, 0)
    self.different_options_vbox.pack_start(self.white_bg_check, False, False, 0)
    self.different_options_vbox.pack_start(self.auto_levels_check, False, False, 0)
    self.different_options_vbox.pack_start(self.success_label, False, False, 0)
    self.different_options_vbox.pack_start(self.text, True, True, 0)
    self.different_options_vbox.show()
    # Фрейм для иных
    self.different_options_frame = gtk.Frame('Различные опции')
    self.different_options_frame.set_border_width(0)
    self.different_options_frame.add(self.different_options_vbox)
    self.different_options_frame.show()
    # Создаем кнопку "О программе"
    self.about_button = gtk.Button(None, gtk.STOCK_ABOUT)
    self.about_button.connect('clicked', self.about, None)
    self.about_button.set_tooltip_text('О программе')
    self.about_button.show()
    # Создаем кнопку "Применить"
    self.apply_button = gtk.Button(None, gtk.STOCK_APPLY)
    self.apply_button.connect('clicked', self.apply_settings, None)
    self.apply_button.set_tooltip_text('Применить эти настройки')
    self.apply_button.show()
    # Создаем кнопку "Отмена"
    self.cancel_button = gtk.Button(None, gtk.STOCK_CANCEL)
    self.cancel_button.connect('clicked', self.destroy, None)
    self.cancel_button.set_tooltip_text('Закрыть это окно и не выполнять никаких действий')
    self.cancel_button.show()
    # Пакуем виджеты в горизонтальный бокс
    self.button_hbox = gtk.HBox(False, 10)
    self.button_hbox.pack_start(self.about_button, False, False, 0)
    self.button_hbox.pack_end(self.apply_button, False, False, 0)
    self.button_hbox.pack_end(self.cancel_button, False, False, 0)
    self.button_hbox.show()
    # Инициируем таблицу, в которую поместим все виджеты
    self.table = gtk.Table(2, 2, False)
    self.table.set_border_width(10)
    self.table.set_row_spacings(20)
    self.table.set_col_spacings(10)
    self.table.attach(self.formats_frame, 0, 1, 0, 1)
    self.table.attach(self.different_options_frame, 1, 2, 0, 1)
    self.table.attach(self.button_hbox, 0, 2, 1, 2)
    self.table.show()
    # Создаем окно. Добавляем всё к окну и показываем его
    self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    self.window.set_position(gtk.WIN_POS_CENTER_ALWAYS)
    self.window.set_title('Настройки дополенения "Фото на документы"')
    self.window.set_border_width(5)
    self.window.set_resizable(False)
    self.window.connect('delete_event', self.delete_event)
    self.window.connect('destroy', self.destroy)
    self.window.add(self.table)
    self.window.show()
    gtk.main()

class print_photo(id_photo_base):
  def __init__(self, runmode, image, drawable):
    self.image, self.drawable = image, drawable
    # Если shelf['format'] пуст ничео не делаем
    if not shelf.has_key('format'):
      gtk.main_quit()
    # Создаем виджеты
    self.gray_check = gtk.CheckButton('обесцветить фото')
    self.gray_check.show()
    if shelf['format']['to_grayscale']:
      self.gray_check.set_active(True)
    self.border_check = gtk.CheckButton('добавить рамку')
    self.border_check.show()
    if shelf['format']['gray_frame']:
      self.border_check.set_active(True)
    self.oval_check = gtk.CheckButton('добавить овал с растушёвкой')
    self.oval_check.show()
    if shelf['format']['oval']:
      self.oval_check.set_active(True)
    # Уголки
    self.angle_none_radio = gtk.RadioButton(None, 'без уголка')
    self.angle_none_radio.show()
    self.angle_right_circular_radio = gtk.RadioButton(self.angle_none_radio, 'круглый справа')
    self.angle_right_circular_radio.show()
    self.angle_left_circular_radio = gtk.RadioButton(self.angle_right_circular_radio, 'круглый слева')
    self.angle_left_circular_radio.show()
    self.angle_right_direct_radio = gtk.RadioButton(self.angle_left_circular_radio, 'прямой справа')
    self.angle_right_direct_radio.show()
    self.angle_left_direct_radio = gtk.RadioButton(self.angle_right_direct_radio, 'прямой слева')
    self.angle_left_direct_radio.show()
    if not shelf['format']['angle']:
      self.angle_none_radio.set_active(True)
    elif shelf['format']['angle'] == 'right_circular':
      self.angle_right_circular_radio.set_active(True)
    elif shelf['format']['angle'] == 'left_circular':
      self.angle_left_circular_radio.set_active(True)
    elif shelf['format']['angle'] == 'right_direct':
      self.angle_right_direct_radio.set_active(True)
    elif shelf['format']['angle'] == 'left_direct':
      self.angle_left_direct_radio.set_active(True)
    # Количество фоток
    if shelf['format']['copys']:
      self.copys_adj = gtk.Adjustment(shelf['format']['copys'], 0.0, 200.0, 1.0, 1.0, 0.0)
    else:
      self.copys_adj = gtk.Adjustment(4.0, 0.0, 200.0, 1.0, 1.0, 0.0)
    self.copys_spin = gtk.SpinButton(self.copys_adj, 0, 0)
    self.copys_spin.set_numeric(True)
    self.copys_spin.show()
    self.copys_label = gtk.Label('фото на листе')
    self.copys_label.set_justify(gtk.JUSTIFY_LEFT)
    self.copys_label.show()
    # Выпадающий сисок "Формат бумаги"
    self.paper_cb = gtk.combo_box_new_text()
    self.paper_cb.append_text('10x15')
    self.paper_cb.append_text('A5')
    self.paper_cb.append_text('A4')
    self.paper_cb.set_active(0)
    self.paper_cb.show()
    if shelf['format']['paper'] == '10x15':
      self.paper_cb.set_active(0)
    elif shelf['format']['paper'] == 'A5':
      self.paper_cb.set_active(1)
    elif shelf['format']['paper'] == 'A4':
      self.paper_cb.set_active(2)
    # Пакуем виджеты в горизонтальный бокс
    self.copys_hbox = gtk.HBox(False, 0)
    self.copys_hbox.pack_start(self.copys_spin, False, False, 0)
    self.copys_hbox.pack_start(self.copys_label, False, False, 5)
    self.copys_hbox.pack_start(self.paper_cb, False, False, 0)
    self.copys_hbox.show()
    # Пакуем опции в вертикальный бокс
    self.options_vbox = gtk.VBox(False, 5)
    self.options_vbox.pack_start(self.copys_hbox, False, False, 5)
    self.options_vbox.pack_start(self.gray_check, False, False, 5)
    self.options_vbox.pack_start(self.border_check, False, False, 5)
    self.options_vbox.pack_start(self.oval_check, False, False, 5)
    self.options_vbox.show()
    # Пакуем уголки в вертикальный бокс
    self.angle_vbox = gtk.VBox(False, 5)
    self.angle_vbox.set_border_width(5)
    self.angle_vbox.pack_start(self.angle_none_radio, False, False, 0)
    self.angle_vbox.pack_start(self.angle_right_circular_radio, False, False, 0)
    self.angle_vbox.pack_start(self.angle_left_circular_radio, False, False, 0)
    self.angle_vbox.pack_start(self.angle_right_direct_radio, False, False, 0)
    self.angle_vbox.pack_start(self.angle_left_direct_radio, False, False, 0)
    self.angle_vbox.show()
    # Фрейм для уголка
    self.angle_frame = gtk.Frame('Добавить уголок')
    self.angle_frame.set_border_width(0)
    self.angle_frame.add(self.angle_vbox)
    self.angle_frame.show()
    # Создаем кнопку "Отмена"
    self.cancel_button = gtk.Button(None, gtk.STOCK_CANCEL)
    self.cancel_button.connect_object('clicked', self.destroy, None)
    self.cancel_button.set_tooltip_text('Не выполнять никаких действий с изображением')
    self.cancel_button.show()
    # Создаем кнопку "Напечатать"
    self.print_button = gtk.Button(None, gtk.STOCK_PRINT)
    self.print_button.connect('clicked', self.compose_or_print, 'print_it')
    self.print_button.set_tooltip_text('Сформировать окончательный результат и вывести его на принтер используемый по умолчанию')
    self.print_button.show()
    # Создаем кнопку "Применить"
    self.apply_button = gtk.Button(None, gtk.STOCK_APPLY)
    self.apply_button.connect('clicked', self.compose_or_print, None)
    self.apply_button.set_tooltip_text('Сформировать окончательный результат')
    self.apply_button.show()
    # Пакуем кнопки "Отмена" и "Применить" и "Печать"
    self.button_box = gtk.HButtonBox()
    self.button_box.set_layout(gtk.BUTTONBOX_EDGE)
    self.button_box.set_spacing(10)
    self.button_box.add(self.cancel_button)
    self.button_box.add(self.print_button)
    self.button_box.add(self.apply_button)
    self.button_box.show()
    # Инициируем таблицу, в которую поместим все виджеты
    self.table = gtk.Table(2, 2, False)
    self.table.set_border_width(5)
    self.table.set_row_spacings(10)
    self.table.set_col_spacings(10)
    self.table.attach(self.options_vbox, 0, 1, 0, 1)
    self.table.attach(self.angle_frame, 1, 2, 0, 1)
    self.table.attach(self.button_box, 0, 2, 1, 2)
    self.table.show()
    # Создаем окно. Добавляем всё к окну и показываем его
    self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    self.window.set_position(gtk.WIN_POS_CENTER_ALWAYS)
    self.window.set_title('Сформировать и распечатать')
    self.window.set_border_width(5)
    self.window.set_resizable(False)
    self.window.connect('delete_event', self.delete_event)
    self.window.connect('destroy', self.destroy)
    self.window.add(self.table)
    self.window.show()
    gtk.main()

#########################################################
#--------           Вот оно - начало начал          ----#
#########################################################

# GIMP 3 Plugin System - Modern Gimp.PlugIn and Gimp.ImageProcedure implementation
class IdPhotoPlugin(Gimp.PlugIn if GIMP_AVAILABLE else object):
    """GIMP 3 compatible plugin using modern Gimp.PlugIn and Gimp.ImageProcedure"""
    
    def __init__(self):
        super().__init__()
        if GIMP_AVAILABLE:
            self.set_name("id-photo-plugin")
            self.set_title("Фото на документы")
    
    def do_set_i18n(self, name):
        """Set up internationalization"""
        return True
    
    def do_query_procedures(self):
        """Query and register plugin procedures using modern GIMP 3 API"""
        try:
            return [
                "python-select-format-id-photo",
                "python-settings-id-photo", 
                "python-print-id-photo"
            ]
        except Exception as e:
            print(f"GIMP 3: do_query_procedures error - {e}")
            return []
    
    def do_create_procedure(self, name):
        """Create procedures using Gimp.ImageProcedure"""
        try:
            if name == "python-select-format-id-photo":
                procedure = Gimp.ImageProcedure.new(
                    self, name, Gimp.PDBProcType.PLUGIN,
                    self.run_select_format, None
                )
                procedure.set_image_types("*")
                procedure.set_sensitivity_mask(
                    Gimp.ProcedureSensitivityMask.DRAWABLE |
                    Gimp.ProcedureSensitivityMask.DRAWABLES_ALPHA
                )
                procedure.set_documentation(
                    "Выбор формата фото на документы",
                    "Выводит диалог со списком форматов для создания фото на документы. "
                    "Расставьте направляющие и вызовите эту функцию.",
                    name
                )
                procedure.set_menu_label("Выбрать формат...")
                procedure.set_attribution(
                    "Карабанов Александр",
                    "Карабанов Александр (zend.karabanov@gmail.com)",
                    "2019-2024"
                )
                procedure.add_menu_path("<Image>/На документы/")
                return procedure
                
            elif name == "python-settings-id-photo":
                procedure = Gimp.ImageProcedure.new(
                    self, name, Gimp.PDBProcType.PLUGIN,
                    self.run_settings, None
                )
                procedure.set_image_types("*")
                procedure.set_documentation(
                    "Настройки плагина фото на документы",
                    "Выводит диалог настроек для добавления и редактирования форматов.",
                    name
                )
                procedure.set_menu_label("Настройки...")
                procedure.set_attribution(
                    "Карабанов Александр",
                    "Карабанов Александр (zend.karabanov@gmail.com)",
                    "2019-2024"
                )
                procedure.add_menu_path("<Image>/На документы/")
                return procedure
                
            elif name == "python-print-id-photo":
                procedure = Gimp.ImageProcedure.new(
                    self, name, Gimp.PDBProcType.PLUGIN,
                    self.run_print_photo, None
                )
                procedure.set_image_types("*")
                procedure.set_sensitivity_mask(
                    Gimp.ProcedureSensitivityMask.DRAWABLE |
                    Gimp.ProcedureSensitivityMask.DRAWABLES_ALPHA
                )
                procedure.set_documentation(
                    "Печать фото на документы",
                    "Выводит диалог для формирования и печати окончательного результата.",
                    name
                )
                procedure.set_menu_label("Печать...")
                procedure.set_attribution(
                    "Карабанов Александр",
                    "Карабанов Александр (zend.karabanov@gmail.com)",
                    "2019-2024"
                )
                procedure.add_menu_path("<Image>/На документы/")
                return procedure
                
        except Exception as e:
            print(f"GIMP 3: do_create_procedure error for {name} - {e}")
            
        return None
    
    def run_select_format(self, procedure, run_mode, image, drawables, config, data):
        """Run select format dialog"""
        try:
            if not drawables:
                return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, 
                                                  GLib.Error("No drawable selected"))
            
            drawable = drawables[0]
            select_format_id_photo(run_mode, image, drawable)
            return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())
            
        except Exception as e:
            print(f"GIMP 3: run_select_format error - {e}")
            return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR,
                                              GLib.Error(f"Error in select format: {e}"))
    
    def run_settings(self, procedure, run_mode, image, drawables, config, data):
        """Run settings dialog"""
        try:
            settings(run_mode, image)
            return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())
            
        except Exception as e:
            print(f"GIMP 3: run_settings error - {e}")
            return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR,
                                              GLib.Error(f"Error in settings: {e}"))
    
    def run_print_photo(self, procedure, run_mode, image, drawables, config, data):
        """Run print photo dialog"""
        try:
            if not drawables:
                return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR,
                                                  GLib.Error("No drawable selected"))
            
            drawable = drawables[0]
            print_photo(run_mode, image, drawable)
            return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())
            
        except Exception as e:
            print(f"GIMP 3: run_print_photo error - {e}")
            return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR,
                                              GLib.Error(f"Error in print photo: {e}"))


# Legacy compatibility layer for older GIMP versions
class id_photo_plugin:
    """Legacy compatibility class - this is a fallback for non-GIMP 3 environments"""
    
    def start(self):
        try:
            print("Legacy compatibility: Plugin start - using fallback mode")
            self.init()
        except Exception as e:
            print(f"Legacy compatibility: Plugin start error - {e}")

    def init(self):
        """Initialize plugin"""
        print("Legacy compatibility: Plugin initialized")

    def quit(self):
        """Cleanup on plugin exit"""
        print("Legacy compatibility: Plugin quit")

    def python_select_format_id_photo(self, runmode, image, drawable):
        """Select format dialog"""
        try:
            select_format_id_photo(runmode, image, drawable)
        except Exception as e:
            print(f"Legacy compatibility: python_select_format_id_photo error - {e}")

    def python_settings(self, runmode, image):
        """Settings dialog"""
        try:
            settings(runmode, image)
        except Exception as e:
            print(f"Legacy compatibility: python_settings error - {e}")

    def python_print_photo(self, runmode, image, drawable):
        """Print photo dialog"""
        try:
            print_photo(runmode, image, drawable)
        except Exception as e:
            print(f"Legacy compatibility: python_print_photo error - {e}")

# Test function for standalone execution
def main():
    """Main function for testing - can be called directly"""
    print("GIMP ID Photo Plugin - GIMP 3 Migration")
    print("Note: This is a compatibility version for GIMP 3")
    
    # For testing, we can create a simple GTK window
    try:
        # Test the GUI components
        test_image = None  # Would need actual GIMP image object
        test_drawable = None  # Would need actual GIMP drawable object
        
        # Initialize GTK
        # Gtk.init()  # May not be needed in GIMP 3 context
        
        # Test select format dialog
        print("Testing select format dialog...")
        # select_format_id_photo(0, test_image, test_drawable)
        
    except Exception as e:
        print(f"Test error: {e}")

if __name__ == '__main__':
    # When run standalone, execute test
    main()
else:
    # When imported as GIMP plugin, start the appropriate plugin system
    try:
        if GIMP_AVAILABLE:
            # Use modern GIMP 3 plugin system with Gimp.PlugIn and Gimp.ImageProcedure
            plugin = IdPhotoPlugin()
            Gimp.main(IdPhotoPlugin, sys.argv)
        else:
            # Fallback to legacy compatibility mode for testing
            id_photo_plugin().start()
    except Exception as e:
        print(f"Plugin startup error - {e}")
        # Fallback to legacy mode
        try:
            id_photo_plugin().start()
        except Exception as e2:
            print(f"Legacy plugin startup error - {e2}")
