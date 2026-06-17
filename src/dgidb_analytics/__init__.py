"""Short project description"""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("dgidb_analytics")
except PackageNotFoundError:
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError
