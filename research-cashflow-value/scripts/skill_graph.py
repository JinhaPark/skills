"""Inspect the modular workflow graph and plan dispatch; never execute or accept tasks."""
import argparse
import hashlib
import json
import re
from pathlib import Path

MANIFEST_TASKS = ('plan', 'industry', 'peers', 'selection', 'model', 'outline', 'writing', 'review', 'publish')
STATUSES = {'pending', 'running', 'accepted', 'not_applicable', 'blocked', 'failed', 'cancelled'}
REQUIREMENTS = {'accepted', 'terminal', 'accepted-or-no-selection'}
CONDITIONS = {'always', 'selected', 'report-path', 'terminal-outcome'}
SHA256 = re.compile(r'^[0-9a-f]{64}$')


def validate_graph(graph, package_root=None):
    """Return structural errors, optionally checking every referenced skill file."""
    errors = []
    if graph.get('schema_version') != 1:
        errors.append('Expected graph schema_version 1')
    registry, nodes = graph.get('registry'), graph.get('nodes')
    if not isinstance(registry, dict) or not registry or not isinstance(nodes, dict) or not nodes:
        return errors + ['Registry and nodes must be nonempty objects']
    root = Path(package_root).resolve() if package_root else None
    for skill, definition in registry.items():
        if not isinstance(definition, dict):
            errors.append(f'{skill}: invalid registry entry')
            continue
        path = definition.get('path')
        if not isinstance(path, str) or Path(path).is_absolute() or '..' in Path(path).parts or not path.endswith('/SKILL.md'):
            errors.append(f'{skill}: skill path must be package-relative SKILL.md')
            continue
        if root:
            target = (root / path).resolve()
            if not target.is_relative_to(root) or not target.is_file():
                errors.append(f'{skill}: missing skill file or path outside package')
            elif not re.search(r'^name:\s*' + re.escape(skill) + r'\s*$', target.read_text(), re.M):
                errors.append(f'{skill}: frontmatter name differs from registry')
    manifests = []
    for name, node in nodes.items():
        if not isinstance(node, dict):
            errors.append(f'{name}: node must be an object')
            continue
        if node.get('skill') not in registry:
            errors.append(f'{name}: unknown skill')
        if not isinstance(node.get('phase'), str) or not node['phase']:
            errors.append(f'{name}: missing phase')
        if node.get('when') not in CONDITIONS:
            errors.append(f'{name}: unknown condition')
        for field in ('inputs', 'outputs', 'gates', 'deps'):
            if not isinstance(node.get(field), list):
                errors.append(f'{name}: {field} must be a list')
        for dependency in node.get('deps', []) if isinstance(node.get('deps'), list) else []:
            if not isinstance(dependency, dict) or dependency.get('node') not in nodes or dependency.get('requires') not in REQUIREMENTS:
                errors.append(f'{name}: invalid dependency')
        for gate in node.get('gates', []) if isinstance(node.get('gates'), list) else []:
            if gate not in graph.get('gate_commands', {}):
                errors.append(f'{name}: unknown gate')
        fanout = node.get('fanout')
        if fanout and (not isinstance(fanout, dict) or fanout.get('source') not in {'fixed','approved-peer-pool','approved-section-dag'} or fanout.get('join') != 'all-required-accepted'):
            errors.append(f'{name}: invalid bounded fanout contract')
        if node.get('manifest_task'):
            manifests.append(node['manifest_task'])
    if sorted(manifests) != sorted(MANIFEST_TASKS):
        errors.append('The nine manifest tasks must each map exactly once')
    visited, active = set(), set()
    def visit(name):
        if name in active:
            errors.append(f'Cycle includes {name}')
            return
        if name in visited:
            return
        active.add(name)
        node = nodes[name]
        if isinstance(node, dict) and isinstance(node.get('deps'), list):
            for dep in node['deps']:
                if isinstance(dep, dict) and dep.get('node') in nodes:
                    visit(dep['node'])
        active.remove(name)
        visited.add(name)
    for name in nodes:
        visit(name)
    dispatch = graph.get('dispatch', {})
    if dispatch.get('max_parallel') != 'available-agent-slots' or dispatch.get('fanout_limit') != 'remaining-agent-slots' or dispatch.get('workers_launch_siblings') is not False:
        errors.append('Dispatch must be bounded and coordinator-owned')
    hook = graph.get('checkpoint_hook', {})
    if hook.get('skill') not in registry or hook.get('blocks_next_node') is not False:
        errors.append('Invalid checkpoint hook')
    return errors


def _evidence(record):
    values = record.get('evidence')
    return isinstance(values, list) and bool(values) and all(isinstance(x, str) and bool(x.strip()) for x in values)


def _fresh(state, node_id, record):
    expected = state.get('input_hashes', {}).get(node_id)
    return isinstance(expected, str) and SHA256.fullmatch(expected) and record.get('input_hash') == expected


def _accepted(state, node_id):
    record = state.get('nodes', {}).get(node_id, {})
    return record.get('status') == 'accepted' and _evidence(record) and _fresh(state, node_id, record)


def _not_applicable(state, node_id):
    record = state.get('nodes', {}).get(node_id, {})
    return node_id == 'model' and state.get('decision') == 'no_selection' and record.get('status') == 'not_applicable' and bool(record.get('reason')) and _evidence(record) and _fresh(state, node_id, record)


def _terminal(state, node_id):
    record = state.get('nodes', {}).get(node_id, {})
    return bool(_accepted(state, node_id) or _not_applicable(state, node_id) or
                (record.get('status') in {'blocked', 'failed', 'cancelled'} and bool(record.get('reason')) and _evidence(record)))


def _condition(state, condition):
    if condition == 'terminal-outcome':
        return state['outcome'] != 'running'
    # Old accepted predecessors never restart work after an observed outcome.
    if state['outcome'] != 'running':
        return False
    return (condition == 'always' or
            condition == 'selected' and state['decision'] == 'selected' or
            condition == 'report-path' and state['decision'] in {'selected', 'no_selection'})


def ready_nodes(graph, state, available_slots):
    """Return bounded eligible aggregate nodes. No state changes or tool calls occur.

    Evidence pointers are assertions to inspect, not proof. Existing workflow and
    lifecycle validators plus actual artifact/receipt inspection remain mandatory.
    """
    errors = validate_graph(graph)
    if errors:
        raise ValueError('; '.join(errors))
    if type(available_slots) is not int or available_slots < 0:
        raise ValueError('available_slots must be a nonnegative integer')
    if state.get('decision') not in {'undecided', 'selected', 'no_selection', 'blocked'}:
        raise ValueError('Unknown decision')
    if state.get('outcome') not in {'running', 'blocked', 'failed', 'delivered', 'no_selection_delivered'}:
        raise ValueError('Unknown outcome')
    records = state.get('nodes', {})
    if not isinstance(records, dict) or not isinstance(state.get('input_hashes', {}), dict) or not isinstance(state.get('gates', {}), dict):
        raise ValueError('Invalid state objects')
    for name, record in records.items():
        if name not in graph['nodes'] or not isinstance(record, dict) or record.get('status') not in STATUSES:
            raise ValueError('Unknown node or status')
    ready = []
    for name, node in graph['nodes'].items():
        if records.get(name, {}).get('status', 'pending') != 'pending' or not _condition(state, node['when']):
            continue
        # Closing an invocation never races active research or delivery workers.
        if node['when'] == 'terminal-outcome' and any(r.get('status') == 'running' for key, r in records.items() if key not in {'dashboard', 'reflection-closeout', 'evolution', 'cache-final'}):
            continue
        passed = True
        for dependency in node['deps']:
            predecessor, requirement = dependency['node'], dependency['requires']
            if requirement == 'terminal':
                valid = _terminal(state, predecessor)
            elif requirement == 'accepted-or-no-selection':
                valid = _accepted(state, predecessor) or _not_applicable(state, predecessor)
            else:
                valid = _accepted(state, predecessor)
            passed = passed and bool(valid)
        for gate in node['gates']:
            receipt = state.get('gates', {}).get(gate, {})
            if not isinstance(receipt, dict):
                passed = False
                continue
            passed = passed and receipt.get('passed') is True and receipt.get('command') == graph['gate_commands'][gate] and _evidence(receipt) and bool(_fresh(state, name, receipt))
        if passed:
            ready.append(name)
    return ready[:available_slots]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('graph', type=Path)
    parser.add_argument('--package-root', type=Path)
    parser.add_argument('--state', type=Path)
    parser.add_argument('--available-slots', type=int, default=1)
    args = parser.parse_args()
    try:
        graph = json.loads(args.graph.read_text())
        errors = validate_graph(graph, args.package_root)
        result = {'passed': not errors, 'errors': errors, 'graph_sha256': hashlib.sha256(args.graph.read_bytes()).hexdigest()}
        if args.state and not errors:
            result['ready_nodes'] = ready_nodes(graph, json.loads(args.state.read_text()), args.available_slots)
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        result = {'passed': False, 'errors': [str(exc)]}
    print(json.dumps(result, indent=2))
    return not result['passed']


if __name__ == '__main__':
    raise SystemExit(main())
