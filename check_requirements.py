import sys

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    from importlib_metadata import version, PackageNotFoundError

try:
    from packaging.version import Version
except ImportError:
    print("The 'packaging' library is missing.")
    sys.exit(1)

requirements = {
    "fastapi": "0.110.0",
    "uvicorn": "0.28.0",
    "python-multipart": "0.0.9",
    "pypdf": "4.0.0",
    "pandas": "2.2.0",
    "openpyxl": "3.1.2",
    "packaging": "24.0",
}

errors = False

for package, minimum in requirements.items():
    try:
        installed = version(package)
        if Version(installed) < Version(minimum):
            print(f"[OUTDATED] {package}: {installed} (requires {minimum}+)")
            errors = True
    except PackageNotFoundError:
        print(f"[MISSING] {package}")
        errors = True

if errors:
    sys.exit(1)

print("All requirements are installed.")
sys.exit(0)