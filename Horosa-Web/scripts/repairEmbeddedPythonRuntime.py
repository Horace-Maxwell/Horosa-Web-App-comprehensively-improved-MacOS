#!/usr/bin/env python3
import argparse
import os
import pathlib
import shutil
import subprocess
import sys
from typing import List, Optional, Tuple


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, text=True)


def run_checked(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, text=True, check=True)


def infer_python_version(root: pathlib.Path) -> str:
    for entry in sorted((root / "lib").glob("python*")):
        if entry.is_dir() and entry.name.startswith("python"):
            return entry.name.removeprefix("python")
    raise SystemExit(f"unable to infer embedded python version under {root}")


def macho_deps(path: pathlib.Path) -> Optional[List[str]]:
    result = run("otool", "-L", str(path))
    if result.returncode != 0:
        return None
    deps: List[str] = []
    for line in result.stdout.splitlines()[1:]:
        line = line.strip()
        if not line:
            continue
        deps.append(line.split(" (compatibility version", 1)[0].strip())
    return deps


def install_name(path: pathlib.Path) -> Optional[str]:
    result = run("otool", "-D", str(path))
    if result.returncode != 0:
        return None
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if len(lines) < 2:
        return None
    return lines[1]


def iter_macho_candidates(root: pathlib.Path) -> List[pathlib.Path]:
    candidates = set()
    for path in (root / "bin").glob("*"):
        if path.is_file() and not path.is_symlink():
            candidates.add(path)
    for path in (root / "lib").rglob("*.dylib"):
        if path.is_file() and not path.is_symlink():
            candidates.add(path)
    for path in (root / "lib").rglob("*.so"):
        if path.is_file() and not path.is_symlink():
            candidates.add(path)
    main_lib = root / "Python"
    if main_lib.is_file() and not main_lib.is_symlink():
        candidates.add(main_lib)
    app_python = root / "Resources" / "Python.app" / "Contents" / "MacOS" / "Python"
    if app_python.is_file() and not app_python.is_symlink():
        candidates.add(app_python)
    return sorted(candidates)


def iter_macho_files(root: pathlib.Path) -> List[pathlib.Path]:
    candidates: List[pathlib.Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        if "_CodeSignature" in path.parts:
            continue
        kind = run("file", str(path))
        if kind.returncode == 0 and "Mach-O" in kind.stdout:
            candidates.append(path)
    return sorted(candidates)


def python_app_bundle(root: pathlib.Path) -> pathlib.Path:
    return root / "Resources" / "Python.app"


def python_app_executable(root: pathlib.Path) -> pathlib.Path:
    return python_app_bundle(root) / "Contents" / "MacOS" / "Python"


def validate_layout(root: pathlib.Path) -> List[str]:
    missing = []
    if not (root / "Python").is_file():
        missing.append("Python")
    if not (root / "lib").is_dir():
        missing.append("lib")
    if not python_app_bundle(root).is_dir():
        missing.append("Resources/Python.app")
    if not python_app_executable(root).is_file():
        missing.append("Resources/Python.app/Contents/MacOS/Python")
    return missing


def clear_code_signatures(root: pathlib.Path) -> None:
    paths = sorted(root.rglob("_CodeSignature"), key=lambda path: len(path.parts), reverse=True)
    for path in paths:
        if path.is_dir():
            shutil.rmtree(path)


def sign_targets(root: pathlib.Path) -> None:
    files = iter_macho_files(root)
    files.sort(key=lambda path: (len(path.parts), str(path)), reverse=True)
    for path in files:
        run_checked("codesign", "--force", "--sign", "-", str(path))
    bundle = python_app_bundle(root)
    if bundle.is_dir():
        run_checked("codesign", "--force", "--sign", "-", str(bundle))


def verify_signatures(root: pathlib.Path) -> List[str]:
    problems: List[str] = []
    for path in iter_macho_files(root):
        result = run("codesign", "--verify", "-vvvv", str(path))
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip() or "codesign verify failed"
            problems.append(f"{path}: {detail}")
    bundle = python_app_bundle(root)
    if bundle.is_dir():
        result = run("codesign", "--verify", "-vvvv", str(bundle))
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip() or "codesign verify failed"
            problems.append(f"{bundle}: {detail}")
    return problems


def discover_changes(root: pathlib.Path) -> Tuple[List[Tuple[pathlib.Path, Optional[str], List[Tuple[str, str]]]], List[Tuple[str, str]]]:
    version = infer_python_version(root)
    framework_prefix = f"/Library/Frameworks/Python.framework/Versions/{version}"
    mapping = {f"{framework_prefix}/Python": root / "Python"}
    for dylib in sorted((root / "lib").glob("*.dylib")):
        mapping[f"{framework_prefix}/lib/{dylib.name}"] = dylib

    instructions: List[Tuple[pathlib.Path, Optional[str], List[Tuple[str, str]]]] = []
    unresolved: List[Tuple[str, str]] = []

    for path in iter_macho_candidates(root):
        deps = macho_deps(path)
        if deps is None:
            continue

        id_target: Optional[str] = None
        if path == root / "Python" or path.parent == root / "lib" and path.suffix == ".dylib":
            rel = path.relative_to(root).as_posix()
            id_target = f"@rpath/{rel}"

        changes: List[Tuple[str, str]] = []
        for dep in deps:
            if not dep.startswith(framework_prefix + "/"):
                continue
            target = mapping.get(dep)
            if target is None or not target.exists():
                unresolved.append((str(path), dep))
                continue
            rel = os.path.relpath(target, start=path.parent).replace(os.sep, "/")
            changes.append((dep, f"@loader_path/{rel}"))

        current_id = install_name(path) if id_target else None
        if current_id == id_target:
            id_target = None

        if id_target or changes:
            instructions.append((path, id_target, changes))

    return instructions, unresolved


def apply_changes(instructions: List[Tuple[pathlib.Path, Optional[str], List[Tuple[str, str]]]]) -> int:
    touched = 0
    for path, id_target, changes in instructions:
        cmd = ["install_name_tool"]
        if id_target:
            cmd.extend(["-id", id_target])
        for dep, replacement in changes:
            cmd.extend(["-change", dep, replacement])
        cmd.append(str(path))
        subprocess.run(cmd, check=True)
        touched += 1
    return touched


def main() -> int:
    parser = argparse.ArgumentParser(description="Repair embedded macOS Python runtime dylib links.")
    parser.add_argument("--check", action="store_true", help="Only check for bad absolute framework refs.")
    parser.add_argument("--repair", action="store_true", help="Rewrite bad refs in-place.")
    parser.add_argument("root", help="Path to embedded python root, e.g. runtime/mac/python")
    args = parser.parse_args()

    mode_repair = args.repair or not args.check
    root = pathlib.Path(args.root).resolve()
    if not root.is_dir():
        raise SystemExit(f"python runtime root not found: {root}")

    missing = validate_layout(root)
    if missing:
        for item in missing:
            print(f"embedded python runtime missing required path: {root / item}", file=sys.stderr)
        return 1

    instructions, unresolved = discover_changes(root)
    remaining = sum(len(changes) + (1 if id_target else 0) for _, id_target, changes in instructions)

    if unresolved:
        for path, dep in unresolved:
            print(f"unresolved embedded python dependency: {path} -> {dep}", file=sys.stderr)
        return 1

    if mode_repair and instructions:
        touched = apply_changes(instructions)
        print(f"embedded python runtime relinked: touched={touched}")
        instructions, unresolved = discover_changes(root)
        if unresolved:
            for path, dep in unresolved:
                print(f"unresolved embedded python dependency after repair: {path} -> {dep}", file=sys.stderr)
            return 1
        remaining = sum(len(changes) + (1 if id_target else 0) for _, id_target, changes in instructions)

    if mode_repair:
        clear_code_signatures(root)
        sign_targets(root)

    if remaining:
        print(f"embedded python runtime still has {remaining} absolute load commands", file=sys.stderr)
        return 1

    signature_problems = verify_signatures(root)
    if signature_problems:
        for issue in signature_problems:
            print(f"embedded python signature invalid: {issue}", file=sys.stderr)
        return 1

    print("embedded python runtime links OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
