# GIMP ID Photo Plugin - GIMP 3 Migration

## Overview

This repository contains the GIMP ID Photo plugin that has been migrated from Python 2/PyGTK to Python 3/PyGObject for GIMP 3 compatibility.

## Migration Status

✅ **COMPLETED:**
- Python 3 compatibility (shebang, syntax, imports)
- PyGObject/GTK3 migration (from pygtk/gtk to gi.repository.Gtk)
- Plugin architecture update for GIMP 3
- GUI components and signal handling
- Configuration and file operations
- Testing framework with mock classes

🔄 **PENDING (when GIMP 3 API is finalized):**
- GIMP API function calls (marked with "GIMP 3 compatibility" comments)
- PDB (Procedural Database) function updates
- Image/layer manipulation operations
- Plugin registration system
- Context management (undo/redo)

## Key Changes Made

### 1. Python 3 Compatibility
- Updated shebang to `#!/usr/bin/env python3`
- Fixed print statements: `print "text"` → `print("text")`
- Updated file handling: `open(file, 'wb')` with proper context management
- Fixed string/bytes handling for Python 3

### 2. PyGObject Migration
- **Before:** `import pygtk; pygtk.require('2.0'); import gtk`
- **After:** `import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk`

### 3. Widget Updates
- `gtk.VBox()` → `Gtk.VBox()`
- `gtk.Button()` → `Gtk.Button()`
- `gtk.RadioButton()` → `Gtk.RadioButton.new_with_label_from_widget()`
- `gtk.MessageDialog()` → `Gtk.MessageDialog()`
- All widget properties and methods updated to GTK3 API

### 4. GIMP Plugin System
- Created compatibility layer for GIMP 3 plugin architecture
- Updated from `gimpplugin.plugin` to new plugin class structure
- Added error handling for missing GIMP 3 API functions

## Testing

Run the test script to verify the migration:

```bash
python3 test_plugin.py
```

Test individual components:

```bash
# Test basic import
python3 -c "import id_photo_for_gimp; print('✓ Import successful')"

# Test standalone execution
python3 id_photo_for_gimp.py
```

## Installation for GIMP 3

1. Ensure GIMP 3 is installed with Python 3 support
2. Copy `id_photo_for_gimp.py` to your GIMP 3 plugins directory:
   - Linux: `~/.config/GIMP/3.0/plug-ins/`
   - Windows: `%APPDATA%/GIMP/3.0/plug-ins/`
   - macOS: `~/Library/Application Support/GIMP/3.0/plug-ins/`

3. Make the file executable (Linux/macOS):
   ```bash
   chmod +x id_photo_for_gimp.py
   ```

## Dependencies

- Python 3.6+
- PyGObject (gi)
- GTK 3.0+
- GIMP 3.0+ (when available)

For development/testing without GIMP:
- The plugin includes mock classes for testing

## API Update Guide

When GIMP 3 API is finalized, update the following areas (marked in code):

### Image Operations
```python
# OLD (GIMP 2)
image.resize(w, h, x, y)
gimp.set_background(r, g, b)
pdb.gimp_levels_stretch(drawable)

# NEW (GIMP 3) - To be updated
# Gimp.Image.resize(image, w, h, x, y)
# Gimp.context_set_background(color)
# Gimp.drawable_levels_stretch(drawable)
```

### Plugin Registration
```python
# OLD (GIMP 2)
gimp.install_procedure(name, description, help, ...)

# NEW (GIMP 3) - To be updated  
# Gimp.procedure_new(name, description, help, ...)
```

## Original Features

The plugin provides tools for creating ID photos with:
- Multiple document format presets (passport, visa, certificates)
- Automatic cropping based on guides
- Photo effects (grayscale, frames, oval mask)
- Batch printing on various paper sizes
- Custom format creation and editing

## Contributing

1. Test the plugin with GIMP 3 when available
2. Update GIMP API calls as the API stabilizes
3. Report issues with the migration
4. Submit improvements and fixes

## License

GNU General Public License v3.0 - see original license in the code.

## Author

Original plugin by Александр Карабанов (zend.karabanov@gmail.com)
GIMP 3 migration completed in 2024.