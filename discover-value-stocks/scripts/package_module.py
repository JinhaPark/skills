"""Materialize one independent skill, preserving its declared resource closure.

This only prepares files. It never commits, pushes, installs, or changes access.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path


def module_files(root, name, commit):
    root = Path(root).resolve()
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name):
        raise ValueError('Invalid skill name')
    if not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise ValueError('An exact source commit is required')
    entry = root / ('SKILL.md' if name == 'discover-value-stocks' else f'subskills/{name}/SKILL.md')
    if not entry.is_file():
        raise ValueError('Unknown skill')
    resources = {p.relative_to(root).as_posix(): p for folder in ('references', 'scripts', 'assets')
                 for p in (root / folder).glob('*') if p.is_file() and p.suffix in ('.md', '.py', '.json')}
    selected = {'SKILL.md': entry}
    queue = [entry]
    while queue:
        current = queue.pop()
        content = current.read_text()
        for relative, resource in resources.items():
            # All bundled resource names are unique. Match complete filenames,
            # including bare helper names in the existing stage instructions.
            pattern = r'(?<![\w-])' + re.escape(resource.name) + r'(?![\w-])'
            if relative not in selected and re.search(pattern, content):
                selected[relative] = resource
                queue.append(resource)
    result = {}
    provenance = []
    for relative, source in sorted(selected.items()):
        content = source.read_text()
        if relative == 'SKILL.md' and name != 'discover-value-stocks':
            content = content.replace('../../references/', 'references/').replace('../../scripts/', 'scripts/').replace('../../assets/', 'assets/')
        if source.suffix == '.md':
            # Cross-skill links remain explicit identities, never embedded SKILLs.
            def cross_link(match):
                target = match.group(1)
                if '://' in target or target.startswith('#'):
                    return match.group(0)
                resolved = (source.parent / target).resolve()
                if resolved.name != 'SKILL.md' or resolved == entry:
                    return match.group(0)
                if not resolved.is_relative_to(root) or not resolved.is_file():
                    raise ValueError(f'Unknown cross-skill link: {target}')
                canonical = resolved.relative_to(root).as_posix()
                return f'](https://github.com/JinhaPark/skills/blob/{commit}/discover-value-stocks/{canonical})'
            # Resolve using original source-relative links before packaging.
            original = source.read_text()
            for match in re.finditer(r'\]\(([^)]+)\)', original):
                replacement = cross_link(match)
                if replacement != match.group(0):
                    content = content.replace(match.group(0), replacement)
        result[relative] = content
        provenance.append({'source_path': source.relative_to(root).as_posix(),
                           'packaged_path': relative,
                           'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                           'packaged_sha256': hashlib.sha256(content.encode()).hexdigest()})
    result['assets/source-provenance.json'] = json.dumps({'schema_version': 1,
        'repository': 'JinhaPark/skills', 'commit': commit, 'skill': name,
        'files': provenance}, indent=2) + '\n'
    return result


def materialize(root, name, commit, destination):
    destination = Path(destination).resolve()
    if destination.name != name:
        raise ValueError('Destination folder must match skill name')
    files = module_files(root, name, commit)
    if destination.exists():
        existing = {p.relative_to(destination).as_posix() for p in destination.rglob('*') if p.is_file()}
        unexpected = existing - set(files) - {'agents/openai.yaml'}
        if unexpected:
            raise ValueError(f'Refusing to overwrite unrelated files: {sorted(unexpected)}')
    for relative, content in files.items():
        path = destination / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    return sorted(files)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('skill')
    parser.add_argument('--source', default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument('--commit', required=True)
    parser.add_argument('--destination', required=True)
    args = parser.parse_args()
    files = materialize(args.source, args.skill, args.commit, args.destination)
    print(json.dumps({'skill': args.skill, 'files': files, 'installed': False}, indent=2))


if __name__ == '__main__':
    main()
