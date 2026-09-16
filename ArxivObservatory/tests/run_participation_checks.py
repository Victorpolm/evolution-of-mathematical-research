"""Run the focused participation fixtures without installing pytest."""
import importlib.util
import inspect
from pathlib import Path
import sys
import unittest


def main():
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root))
    suite = unittest.TestSuite()
    for filename in (
        "test_openalex_names.py", "test_retention_audit.py",
        "test_papers_contributors.py", "test_export_metadata.py",
    ):
        spec = importlib.util.spec_from_file_location(filename[:-3], root / "tests" / filename)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
        for name, obj in vars(module).items():
            if name.startswith("test_") and inspect.isfunction(obj):
                suite.addTest(unittest.FunctionTestCase(obj))
    result = unittest.TextTestRunner().run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
