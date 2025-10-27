# brother_ql - Python 3.9+ Fixed Version

This is a fixed version of the original [brother_ql](https://github.com/pklaus/brother_ql) package that works with Python 3.9 through 3.13+.

## What Was Fixed

The original `brother_ql` v0.9.4 had a dependency on `python-future`, a Python 2/3 compatibility package from 2013 that:
- Is no longer needed for Python 3.9+
- Causes installation failures on Python 3.13+
- Contains obsolete compatibility shims

**Changes made:**
1. ✅ Removed `python-future` dependency from setup.py
2. ✅ Removed `from __future__ import` statements
3. ✅ Removed Python < 3.5 conditional dependencies (`typing`, `enum34`)
4. ✅ Updated version to 0.9.5
5. ✅ Added Python 3.9-3.13 to classifiers

**Preserved:**
- ✅ All original functionality
- ✅ All printer model support
- ✅ All backends (network, USB, serial)
- ✅ CLI tools
- ✅ Complete API compatibility

## Installation

This package is designed to be installed from the parent project:

```bash
cd ..
pip install -r requirements-fixed.txt
```

Or install directly:

```bash
pip install -e ./brother_ql_fixed
```

## Python Version Support

- ✅ Python 3.9
- ✅ Python 3.10
- ✅ Python 3.11
- ✅ Python 3.12
- ✅ Python 3.13
- ✅ Python 3.14+ (Verified working!)

## API Usage

The API is identical to the original:

```python
from brother_ql.raster import BrotherQLRaster
from brother_ql.conversion import convert
from brother_ql.backends.helpers import send

# Create raster instance
qlr = BrotherQLRaster('QL-820NWB')

# Convert image
from PIL import Image
image = Image.open('label.png')

instructions = convert(
    qlr=qlr,
    images=[image],
    label='62',
    rotate='auto',
    threshold=70.0,
    cut=True
)

# Send to printer
send(
    instructions=instructions,
    printer_identifier='tcp://192.168.1.100',
    backend_identifier='network',
    blocking=True
)
```

## CLI Usage

All CLI tools work exactly as before:

```bash
# Discover printers
brother_ql discover

# Print image
brother_ql -p tcp://192.168.1.100 -m QL-820NWB print -l 62 image.png

# Get info
brother_ql info
```

## License

This package retains the original GPL license from the brother_ql project.

## Credits

- **Original Author**: Philipp Klaus
- **Original Repository**: https://github.com/pklaus/brother_ql
- **Fixes**: Removed Python 2 compatibility for modern Python 3.9+ support

## Why Bundle This?

Rather than requiring users to:
1. Clone a repository
2. Apply patches
3. Hope upstream accepts PR
4. Deal with multiple forks

We bundle a pre-fixed version that:
- Works out of the box
- Requires no extra steps
- Maintains full compatibility
- Is tested with the Brother Label API

## Testing

To verify the installation:

```bash
python -c "from brother_ql.raster import BrotherQLRaster; print('✓ Works!')"
```

## Updates

This is based on brother_ql v0.9.4 (the last released version). If upstream releases a new version that removes the `python-future` dependency, you can switch back to the official package.

Check for updates:
- Original repo: https://github.com/pklaus/brother_ql
- Maintained fork: https://github.com/matmair/brother_ql-inventree

## Contributing

For issues with the Brother Label API, open an issue in the parent project.

For issues with the underlying brother_ql functionality, consider contributing to the original project or maintained forks.
