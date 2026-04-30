# autoload all files in operations directory
from importlib import import_module
from pathlib import Path
modules = Path(__file__).parent.glob("*.py")
[import_module(f'.{f.stem}', 'path.operations') for f in modules if f.stem != '__init__']
