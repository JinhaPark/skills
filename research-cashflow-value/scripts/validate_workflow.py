"""Validate workflow records and artifacts, not financial truth or actual execution."""
import argparse
import hashlib
import json
from pathlib import Path

STAGES = ('plan', 'industry', 'peers', 'selection', 'model', 'outline', 'writing', 'review', 'publish')
REQUIRED_HANDOFF = ('task_id', 'status', 'artifact_paths', 'input_versions', 'summary', 'claims', 'key_metrics', 'uncertainties', 'next_inputs')


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local_file(root, name):
    if not isinstance(name, str) or not name or Path(name).is_absolute():
        raise ValueError('Expected a nonempty relative artifact path')
    path = (root / name).resolve()
    if not path.is_relative_to(root) or path.name == 'manifest.json':
        raise ValueError('Artifact must stay inside run directory and not be manifest')
    if not path.is_file() or not path.stat().st_size:
        raise ValueError(f'Missing or empty artifact: {name}')
    return path


def validate_run(run_dir, through='review'):
    root = Path(run_dir).resolve()
    data = json.loads((root / 'manifest.json').read_text())
    errors = []
    if data.get('schema_version') != 1 or not data.get('run_id'):
        errors.append('Missing schema version 1 or run_id')
    decision = data.get('decision')
    if decision not in ('selected', 'no_selection'):
        errors.append('Decision must be selected or no_selection before a final gate')
    versions = data.get('versions', {})
    for key in ('data', 'model'):
        value = versions.get(key)
        if type(value) is not int or value < (1 if key == 'data' or decision == 'selected' else 0):
            errors.append(f'Invalid canonical {key} version')
    tasks = data.get('tasks', {})
    end = STAGES.index(through)
    for index, name in enumerate(STAGES[:end + 1]):
        task = tasks.get(name)
        if not isinstance(task, dict):
            errors.append(f'{name}: missing task record')
            continue
        expected = [] if index == 0 else [STAGES[index - 1]]
        if task.get('deps') != expected:
            errors.append(f'{name}: incorrect dependencies')
        if name == 'model' and decision == 'no_selection' and task.get('status') == 'not_applicable':
            if not task.get('reason') or task.get('input_versions', {}).get('data') != versions.get('data'):
                errors.append('model: no-selection skip requires reason and current data version')
            continue
        if task.get('status') != 'completed':
            errors.append(f'{name}: stage is not completed')
            continue
        required = ('data',) if index >= 3 else ()
        if index >= 5 and decision == 'selected':
            required = ('data', 'model')
        inputs = task.get('input_versions', {})
        for key in required:
            if type(inputs.get(key)) is not int or inputs[key] != versions.get(key):
                errors.append(f'{name}: stale or absent {key} input version')
        for key, value in inputs.items():
            if key not in versions or type(value) is not int or value != versions[key]:
                errors.append(f'{name}: input version mismatch for {key}')
        artifacts = task.get('artifacts')
        if not isinstance(artifacts, list) or not artifacts:
            errors.append(f'{name}: no artifact records')
            continue
        paths = []
        for artifact in artifacts:
            try:
                path = local_file(root, artifact.get('path'))
                if sha256(path) != artifact.get('sha256'):
                    raise ValueError(f'Hash mismatch: {artifact.get("path")}')
                paths.append(artifact['path'])
            except (ValueError, AttributeError, TypeError) as exc:
                errors.append(f'{name}: {exc}')
        try:
            handoff_path = local_file(root, task.get('handoff'))
            if task.get('handoff_sha256') != sha256(handoff_path):
                raise ValueError('Missing or mismatched handoff SHA-256')
            handoff = json.loads(handoff_path.read_text())
            if any(key not in handoff for key in REQUIRED_HANDOFF):
                raise ValueError('Incomplete handoff fields')
            if handoff['task_id'] != name or handoff['status'] != 'completed':
                raise ValueError('Wrong handoff task/status')
            if handoff['input_versions'] != inputs:
                raise ValueError('Handoff input versions differ from task')
            if not isinstance(handoff['summary'], str) or not handoff['summary'].strip():
                raise ValueError('Empty handoff summary')
            if any(not isinstance(handoff[key], list) for key in ('claims', 'key_metrics', 'uncertainties', 'next_inputs', 'artifact_paths')):
                raise ValueError('Handoff arrays must be lists')
            if set(handoff['artifact_paths']) != set(paths):
                raise ValueError('Handoff artifact references differ from task')
        except (ValueError, KeyError, TypeError) as exc:
            errors.append(f'{name}: {exc}')
    for filename, key in (('data.json', 'data'), ('model.json', 'model')):
        if key == 'model' and decision != 'selected':
            continue
        try:
            artifact = local_file(root, filename)
            canonical = json.loads(artifact.read_text())
            if type(canonical.get('version')) is not int or canonical['version'] != versions.get(key):
                raise ValueError(f'{filename} version differs from manifest')
            found = any(a.get('path') == filename for task in tasks.values() if isinstance(task, dict) for a in task.get('artifacts', []) if isinstance(a, dict))
            if not found:
                raise ValueError(f'{filename} not registered as a task artifact')
        except (ValueError, TypeError) as exc:
            errors.append(str(exc))
    review = data.get('review', {})
    if review.get('passed') is not True or type(review.get('unresolved_critical')) is not int or review.get('unresolved_critical') != 0:
        errors.append('Review not passed or critical findings unresolved')
    if through == 'publish':
        try:
            local_file(root, 'report.md')
            registered = any(a.get('path') == 'report.md' for a in tasks.get('publish', {}).get('artifacts', []) if isinstance(a, dict))
            if not registered:
                errors.append('publish: report.md must be a hashed artifact')
        except ValueError as exc:
            errors.append(str(exc))
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_dir')
    parser.add_argument('--through', choices=('review', 'publish'), default='review')
    args = parser.parse_args()
    try:
        errors = validate_run(args.run_dir, args.through)
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        errors = [f'Invalid manifest/artifacts: {exc}']
    print(json.dumps({'passed': not errors, 'errors': errors}, ensure_ascii=False, indent=2))
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
