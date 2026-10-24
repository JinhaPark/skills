#!/usr/bin/env python3
"""Local content-addressed checkpoints. External persistence remains a provider action."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import tempfile
from datetime import datetime, timezone

HEX = re.compile(r"^[0-9a-f]{64}$")
COMMIT = re.compile(r"^[0-9a-f]{40}$")
REUSABLE_STAGES = {"source-evidence", "industry", "peers", "model", "outline", "writing"}


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(value).hexdigest()


def utc(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include timezone")
    return parsed.astimezone(timezone.utc)


def safe_root(path, create=False):
    path = Path(os.path.abspath(path))
    for component in [*reversed(path.parents), path]:
        if component.is_symlink():
            raise ValueError("symlink paths are not allowed")
    if create:
        path.mkdir(parents=True, exist_ok=True)
    if not path.is_dir():
        raise ValueError("root must be a directory")
    return path


def safe_file(root, relative):
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise ValueError("invalid relative path")
    rel = PurePosixPath(relative)
    if rel.is_absolute() or any(p in {"", ".", ".."} for p in relative.split("/")):
        raise ValueError("path traversal is not allowed")
    path = root.joinpath(*rel.parts)
    for component in [path, *path.parents]:
        if component == root:
            break
        if component.is_symlink():
            raise ValueError("symlink artifacts are not allowed")
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError("artifact must be a nonempty regular file")
    return path


def descriptor_key(descriptor):
    required = {"stage", "skill_commit", "input_hashes", "sources", "settings", "volatility"}
    if set(descriptor) != required:
        raise ValueError("descriptor fields must match documented schema")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", descriptor["stage"]):
        raise ValueError("invalid stage")
    if not COMMIT.fullmatch(descriptor["skill_commit"]):
        raise ValueError("skill_commit must be a full commit SHA")
    if descriptor["volatility"] not in {"static", "market"}:
        raise ValueError("invalid volatility")
    if not isinstance(descriptor["settings"], dict) or not isinstance(descriptor["input_hashes"], dict):
        raise ValueError("settings and input_hashes must be objects")
    if any(not isinstance(k, str) or not k or not HEX.fullmatch(v) for k, v in descriptor["input_hashes"].items()):
        raise ValueError("input hashes must be named SHA-256 digests")
    if not isinstance(descriptor["sources"], list):
        raise ValueError("sources must be an array")
    ids = []
    for source in descriptor["sources"]:
        if set(source) != {"source_id", "as_of", "sha256"} or not isinstance(source["source_id"], str) or not source["source_id"]:
            raise ValueError("invalid source entry")
        ids.append(source["source_id"])
        utc(source["as_of"])
        if not HEX.fullmatch(source["sha256"]):
            raise ValueError("invalid source digest")
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate source_id")
    normalized = {**descriptor, "sources": sorted(descriptor["sources"], key=lambda s: s["source_id"])}
    return digest(encoded(normalized))


def load_json(path):
    return json.loads(path.read_text())


def snapshot(run_root, cache_root, descriptor, run_id, status, artifacts, created_at, valid_until):
    run_root, cache_root = safe_root(run_root), safe_root(cache_root, create=True)
    key = descriptor_key(descriptor)
    if not isinstance(run_id, str) or not run_id or status not in {"completed", "failed", "blocked"}:
        raise ValueError("run_id and valid status are required")
    if utc(valid_until) <= utc(created_at):
        raise ValueError("valid_until must follow created_at")
    if any(utc(source["as_of"]) > utc(created_at) for source in descriptor["sources"]):
        raise ValueError("source observation cannot postdate snapshot creation")
    if not artifacts or len(artifacts) != len(set(artifacts)):
        raise ValueError("provide distinct artifact paths")
    payload = {p: safe_file(run_root, p).read_bytes() for p in artifacts}
    manifest = {"schema_version": 1, "key": key, "descriptor": descriptor, "run_id": run_id, "status": status, "created_at": created_at, "valid_until": valid_until,
                "artifacts": [{"path": p, "sha256": digest(payload[p]), "bytes": len(payload[p])} for p in sorted(payload)]}
    snapshot_id = digest(encoded(manifest))
    snapshots = safe_root(cache_root / "snapshots", create=True)
    destination = snapshots / snapshot_id
    if destination.exists():
        verify(cache_root, snapshot_id)
        return {"snapshot_id": snapshot_id, "key": key, "path": str(destination), "durable": False}
    temporary = Path(tempfile.mkdtemp(prefix=".pending-", dir=snapshots))
    try:
        for p, data in payload.items():
            target = temporary / "files" / p
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        (temporary / "manifest.json").write_bytes(encoded(manifest))
        os.rename(temporary, destination)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    return {"snapshot_id": snapshot_id, "key": key, "path": str(destination), "durable": False}


def verify(cache_root, snapshot_id):
    if not HEX.fullmatch(snapshot_id):
        raise ValueError("invalid snapshot_id")
    cache_root = safe_root(cache_root)
    root = safe_root(cache_root / "snapshots" / snapshot_id)
    manifest = load_json(safe_file(root, "manifest.json"))
    required = {"schema_version", "key", "descriptor", "run_id", "status", "created_at", "valid_until", "artifacts"}
    if not isinstance(manifest, dict) or set(manifest) != required or not isinstance(manifest["run_id"], str) or not manifest["run_id"]:
        raise ValueError("invalid snapshot fields or run_id")
    if digest(encoded(manifest)) != snapshot_id or descriptor_key(manifest["descriptor"]) != manifest["key"]:
        raise ValueError("snapshot metadata hash mismatch")
    if manifest["schema_version"] != 1 or manifest["status"] not in {"completed", "failed", "blocked"}:
        raise ValueError("invalid snapshot metadata")
    if utc(manifest["valid_until"]) <= utc(manifest["created_at"]):
        raise ValueError("invalid snapshot validity")
    if any(utc(source["as_of"]) > utc(manifest["created_at"]) for source in manifest["descriptor"]["sources"]):
        raise ValueError("source observation cannot postdate snapshot creation")
    files = safe_root(root / "files")
    seen = set()
    if not isinstance(manifest["artifacts"], list):
        raise ValueError("invalid artifacts array")
    for artifact in manifest["artifacts"]:
        if not isinstance(artifact, dict) or set(artifact) != {"path", "sha256", "bytes"}:
            raise ValueError("invalid artifact record")
        path = artifact["path"]
        if path in seen:
            raise ValueError("duplicate artifact path")
        seen.add(path)
        content = safe_file(files, path).read_bytes()
        if digest(content) != artifact["sha256"] or len(content) != artifact["bytes"]:
            raise ValueError("artifact hash mismatch")
    if not seen:
        raise ValueError("empty snapshot")
    expected = {"manifest.json", *("files/" + p for p in seen)}
    actual = set()
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ValueError("symlink inside snapshot")
        if path.is_file():
            actual.add(path.relative_to(root).as_posix())
        elif not path.is_dir():
            raise ValueError("unexpected snapshot object")
    if actual != expected:
        raise ValueError("unregistered snapshot file")
    return manifest


def register_receipt(cache_root, snapshot_id, provider, storage_reference, saved_at, evidence_file):
    """Record observed provider result; this function does not call or verify the provider."""
    cache_root = safe_root(cache_root)
    manifest = verify(cache_root, snapshot_id)
    if not provider.strip() or not storage_reference.strip():
        raise ValueError("provider and observed storage reference required")
    if utc(saved_at) < utc(manifest["created_at"]):
        raise ValueError("receipt predates snapshot")
    evidence_path = Path(os.path.abspath(evidence_file))
    evidence = safe_file(safe_root(evidence_path.parent), evidence_path.name).read_bytes()
    receipt = {"snapshot_id": snapshot_id, "provider": provider, "storage_reference": storage_reference, "saved_at": saved_at, "evidence_sha256": digest(evidence)}
    receipt_id = digest(encoded(receipt))
    receipts_root = safe_root(cache_root / "receipts", create=True)
    folder = receipts_root / receipt_id
    expected = {"receipt.json": encoded(receipt), "provider-result.txt": evidence}
    if folder.exists():
        safe_root(folder)
        if any(p.name not in expected for p in folder.iterdir()):
            raise ValueError("unexpected receipt contents")
        for name, data in expected.items():
            if (folder / name).exists() and safe_file(folder, name).read_bytes() != data:
                raise ValueError("receipt collision or tampering")
        if all((folder / name).is_file() for name in expected):
            return {"receipt_id": receipt_id, **receipt}
    temporary = Path(tempfile.mkdtemp(prefix=".pending-", dir=receipts_root))
    try:
        for name, data in expected.items():
            (temporary / name).write_bytes(data)
        if folder.exists():
            # Preserve a matching interrupted pair, then atomically install the full pair.
            preserved = receipts_root / (".partial-" + receipt_id + "-" + temporary.name.removeprefix(".pending-"))
            os.rename(folder, preserved)
        os.rename(temporary, folder)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    return {"receipt_id": receipt_id, **receipt}


def receipts(cache_root):
    folder = Path(cache_root) / "receipts"
    if not folder.exists():
        return [], []
    folder = safe_root(folder)
    matches, quarantined = [], []
    for item in sorted(folder.iterdir()):
        try:
            if not HEX.fullmatch(item.name):
                raise ValueError("incomplete, preserved or unexpected receipt entry")
            item = safe_root(item)
            receipt = load_json(safe_file(item, "receipt.json"))
            if digest(encoded(receipt)) != item.name or digest(safe_file(item, "provider-result.txt").read_bytes()) != receipt["evidence_sha256"]:
                raise ValueError("receipt hash mismatch")
            if not HEX.fullmatch(receipt["snapshot_id"]) or not receipt["provider"].strip() or not receipt["storage_reference"].strip():
                raise ValueError("invalid receipt metadata")
            utc(receipt["saved_at"])
            matches.append({"receipt_id": item.name, **receipt})
        except (ValueError, KeyError, TypeError, AttributeError, OSError) as error:
            quarantined.append({"kind": "receipt", "entry": item.name, "reason": str(error)})
    return matches, quarantined


def verified_snapshots(cache_root):
    folder = Path(cache_root) / "snapshots"
    valid, quarantined = [], []
    if folder.exists():
        for path in sorted(safe_root(folder).iterdir()):
            try:
                valid.append((path.name, verify(cache_root, path.name)))
            except (ValueError, KeyError, TypeError, AttributeError, OSError) as error:
                quarantined.append({"kind": "snapshot", "entry": path.name, "reason": str(error)})
    return valid, quarantined


def lookup(cache_root, descriptor, run_id, now):
    cache_root = safe_root(cache_root)
    key, current_time = descriptor_key(descriptor), utc(now)
    eligible, rejected = [], []
    snapshots, quarantined = verified_snapshots(cache_root)
    proofs, receipt_errors = receipts(cache_root)
    quarantined.extend(receipt_errors)
    for snapshot_id, manifest in snapshots:
        if manifest["key"] != key:
            continue
        reason = None
        if manifest["status"] != "completed":
            reason = "incomplete_status"
        elif not utc(manifest["created_at"]) <= current_time < utc(manifest["valid_until"]):
            reason = "expired_or_future"
        elif manifest["run_id"] != run_id and (descriptor["volatility"] == "market" or descriptor["stage"] not in REUSABLE_STAGES):
            reason = "new_run_requires_refresh"
        proof = [r for r in proofs if r["snapshot_id"] == snapshot_id and utc(manifest["created_at"]) <= utc(r["saved_at"]) <= current_time]
        if not proof and reason is None:
            reason = "durable_receipt_missing"
        result = {"snapshot_id": snapshot_id, "source_run_id": manifest["run_id"]}
        if reason:
            rejected.append({**result, "reason": reason})
        else:
            eligible.append({**result, "created_at": manifest["created_at"], "artifacts": manifest["artifacts"], "receipts": proof})
    eligible.sort(key=lambda x: utc(x["created_at"]), reverse=True)
    return {"key": key, "eligible": eligible, "rejected": rejected, "quarantined": quarantined}


def index(cache_root):
    cache_root = safe_root(cache_root)
    entries = []
    snapshots, quarantined = verified_snapshots(cache_root)
    proofs, receipt_errors = receipts(cache_root)
    quarantined.extend(receipt_errors)
    for snapshot_id, manifest in snapshots:
        entries.append({"snapshot_id": snapshot_id, "key": manifest["key"], "run_id": manifest["run_id"], "status": manifest["status"], "stage": manifest["descriptor"]["stage"], "receipts": [r for r in proofs if r["snapshot_id"] == snapshot_id]})
    return {"schema_version": 1, "snapshots": entries, "quarantined": quarantined}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    save = sub.add_parser("snapshot")
    for arg in ("run-root", "cache-root", "descriptor", "run-id", "status", "created-at", "valid-until"):
        save.add_argument("--" + arg, required=True)
    save.add_argument("--artifact", action="append", required=True)
    check = sub.add_parser("verify")
    check.add_argument("--cache-root", required=True)
    check.add_argument("--snapshot-id", required=True)
    find = sub.add_parser("lookup")
    for arg in ("cache-root", "descriptor", "run-id", "now"):
        find.add_argument("--" + arg, required=True)
    receipt = sub.add_parser("receipt")
    for arg in ("cache-root", "snapshot-id", "provider", "storage-reference", "saved-at", "evidence-file"):
        receipt.add_argument("--" + arg, required=True)
    listing = sub.add_parser("index")
    listing.add_argument("--cache-root", required=True)
    args = vars(parser.parse_args())
    action = args.pop("action")
    if "descriptor" in args:
        args["descriptor"] = load_json(Path(args["descriptor"]))
    if "artifact" in args:
        args["artifacts"] = args.pop("artifact")
    function = {"snapshot": snapshot, "verify": verify, "lookup": lookup, "receipt": register_receipt, "index": index}[action]
    try:
        print(json.dumps(function(**args), ensure_ascii=False, indent=2))
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(1, f"cache error: {error}\n")


if __name__ == "__main__":
    main()
