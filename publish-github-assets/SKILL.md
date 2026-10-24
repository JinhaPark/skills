---
name: publish-github-assets
description: Publish approved binary or text assets to GitHub branches and pull requests using verified app or authenticated Git transports; check hashes and never upload private originals.
---

# Publish GitHub Assets

This skill owns GitHub **transport and publication**, not image generation, image transformations, revision caching, caption selection, or placement ownership. It can be used by `travel-photo-to-illustration` or any workflow that produces an approved derivative asset.

## Inputs and contract

- Repository and target relative path; approved artifact path or accessible bytes; source classification (`approved-derivative` or `ordinary-project-file`); expected SHA-256 and byte count; base branch or SHA; desired branch and commit/PR messages; explicit publishing authorization.
- Optional companion manifest, lineage or reference changes supplied by the coordinating agent. Never guess a target path or edit shared manifests independently.
- Output: publication status (`published`, `blocked`, or `failed`), transport method, branch/commit/PR refs when real, artifact Git blob SHA and independently verified checks, or a precise blocker. Do not turn a failed or unverified upload into a success report.

## Transport capability check

1. Verify that the artifact can be read and decoded locally; calculate SHA-256, size, and for images, dimensions. Reject mismatches and refuse to publish original user photos, original bytes encoded as Base64, or confidential input assets.
2. Prefer the connected GitHub app. `create_blob` accepts `encoding: base64`, but the **entire encoded byte string must be transferable from the file-reading runtime into the tool call**. An image's local path or an incomplete Base64 fragment is not its content. Test the actual bridge before publishing.
3. If the tool bridge exists, upload the verified bytes with `create_blob`, then create a tree against the current base, a commit, and an updated **dedicated working branch**. Inspect the current base and branch head to avoid overwriting concurrent commits. Create a PR only after verifying uploaded content and that referenced assets exist.
4. If direct app transport cannot access the bytes, use an authenticated Git worktree **only if** that execution environment has actual local file access, network connectivity and push permission. The assistant must carry out Git commands; never imply the user is required to operate a terminal. Return `blocked` if neither route is available.
5. Do not attempt to work around application access controls using secret extraction, credentials embedded in messages, public paste services or undeclared uploads. Do not print Base64 image payloads in chat or commit original photographs.

## Commit, verification and recovery

- Use the Git object blob SHA (Git's SHA-1 object identifier, not SHA-256) for tree entries; store SHA-256 separately for asset integrity. Verify remote bytes with a supported readback if available. If the GitHub connector cannot read back binary bytes, report the verification limitation and do not claim byte-for-byte verification.
- Stage binary file plus coordinating-agent-provided manifest and lineage changes in one coherent branch update when possible. If a failure interrupts intermediate blob creation, do not modify `main` or invent a successful commit.
- Respect branch protection, target branch freshness, and related open PRs. Reuse an unfinished PR for the same change. Preserve earlier published revisions until validated replacement.
- Run checks scoped to touched assets and file references; defer broad tests and merge until the user requests them. Provide PR URL and commit SHA only when returned by GitHub. Never auto-merge unless explicitly requested.
