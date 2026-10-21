# SPDX-License-Identifier: GPL-3.0-or-later
"""Build/validate the runtime-only extension ZIP using Blender's extension CLI."""
import argparse
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import tomllib
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'quick_lighting_environment'
RUNTIME_FILES = (
    '__init__.py', 'backdrops.py', 'colors.py', 'constants.py', 'defaults.py', 'environment.py',
    'light_controls.py', 'operators.py', 'panels.py', 'position.py', 'properties.py',
    'state.py', 'temperatures.py', 'stage_colors.py', '_backdrop.blend', '_backdrops.blend', 'blender_manifest.toml',
)
RUNTIME_FILES += tuple(str(path.relative_to(PACKAGE)) for path in sorted((PACKAGE / 'icons/stage_colors').glob('*.png')))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--blender', type=Path)
    parser.add_argument('--source-only', action='store_true', help='Package without launching Blender or runtime validation')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'dist')
    args = parser.parse_args()
    if not args.source_only and args.blender is None:
        parser.error('Supply --blender or --source-only')
    manifest = tomllib.loads((PACKAGE / 'blender_manifest.toml').read_text())
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output = args.output_dir.resolve() / f"{manifest['id']}-{manifest['version']}.zip"
    with tempfile.TemporaryDirectory(prefix='qle-build-') as directory:
        directory = Path(directory)
        staging = directory / 'package'
        staging.mkdir()
        for name in RUNTIME_FILES:
            (staging / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(PACKAGE / name, staging / name)
        shutil.copy2(ROOT / 'LICENSE', staging / 'LICENSE.txt')
        if args.source_only:
            with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
                for file in sorted(staging.rglob('*')):
                    if file.is_file():
                        archive.write(file, str(file.relative_to(staging)))
        else:
            environment = os.environ.copy()
            for key, name in [('BLENDER_USER_CONFIG', 'config'), ('BLENDER_USER_SCRIPTS', 'scripts'),
                              ('BLENDER_USER_EXTENSIONS', 'extensions')]:
                environment[key] = str(directory / name)
                Path(environment[key]).mkdir()
            environment['PYTHONDONTWRITEBYTECODE'] = '1'
            base = [str(args.blender.resolve()), '--background', '--factory-startup',
                    '--offline-mode', '--disable-autoexec', '--command', 'extension']
            for command in [
                ['validate', str(staging)],
                ['build', '--source-dir', str(staging), '--output-filepath', str(output)],
                ['validate', str(output)],
            ]:
                subprocess.run(base + command, env=environment, check=True)
    expected = set(RUNTIME_FILES) | {'LICENSE.txt'}
    with zipfile.ZipFile(output) as archive:
        assert set(archive.namelist()) == expected, archive.namelist()
        assert len(archive.namelist()) == len(expected), 'Duplicate ZIP entries'
        assert archive.testzip() is None, 'ZIP CRC failure'
        built_manifest = tomllib.loads(archive.read('blender_manifest.toml').decode())
        assert built_manifest['version'] == manifest['version']
        assert built_manifest['blender_version_min'] == '4.5.0'
        for name in RUNTIME_FILES:
            if name != 'blender_manifest.toml':
                assert archive.read(name) == (PACKAGE / name).read_bytes(), name
        assert archive.read('LICENSE.txt') == (ROOT / 'LICENSE').read_bytes()
    print('QLE_EXTENSION_BUILD_OK', 'source-only' if args.source_only else 'Blender-validated', output, 'files', len(expected), 'sha256', hashlib.sha256(output.read_bytes()).hexdigest())


if __name__ == '__main__':
    main()
