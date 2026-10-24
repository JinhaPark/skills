---
name: travel-photo-to-illustration
description: Clean travel photos, convert them to watercolor or colored-pencil illustrations, optimize responsive WebP assets, and integrate them into existing guides. Use for travel-photo illustration (여행 사진 수채화·워터칼러·색연필화 변환), removal of window glare, utility poles, wires, and foreground crowds (차창 반사광·전봇대·전선·하단 단체관광객·군중 제거), upper-frame restoration (사진 상단 보완), mobile optimization (모바일 최적화), or guide image batches. Preserve portrait subjects, architectural details, and natural water reflections. Delegate visual edits to the built-in imagegen skill; use the bundled script only for resizing and encoding.
---

# Travel Photo to Illustration

Prioritize the user's instructions and explain results in polite Korean (존댓말). Reuse existing illustrations and completed work. Complete the task within the actual authorization granted; do not invent additional approval requirements.

## 1. Inspect inputs and current state

- Check applicable `AGENTS.md` instructions, the latest default and working branches, PRs, and audit records. For guide work, read [guide-integration.md](references/guide-integration.md). Do not require repository operations for ordinary image editing.
- Open each original and record its filename, dimensions after EXIF orientation, location and subject, role as an edit target or style reference, and elements to remove or preserve. Do not establish a location or capture date from file order, filename, or upload time.
- Distinguish the user's travel photos from internet screenshots. Verify external photos' source pages, authors, and usage terms; satisfy required credits, licenses, and modification notices. Style transfer does not replace permission to use an image. Do not publish screenshots with unverified rights; obtain reusable alternatives.
- Check building identification against the original features and the user's corrections. Preserve the correction concerning Minor and Gur-e Amir images previously misassigned to Bibi-Khanym (미노르·구르에미르·비비하눔). Do not redo illustrations completed in other PRs.

## Cache and batch processing

First read [cache-and-parallel.md](references/cache-and-parallel.md). Apply its persistent mapping from originals to edit revisions to published variants, and its two-stage cache. Look up existing results before processing. When multiple independent images remain unprocessed, assign them to asynchronous subagents in parallel. The parent agent alone writes shared files and validates and integrates the results. Keep successive edits to the same image sequential and preserve earlier revisions. The repository orchestration agent alone manages image registration, replacement, retirement, and deletion, following the reference's CRUD lifecycle. Do not upload originals; record their hashes during processing.

## 2. Plan cleanup and style

Read [editing-rules.md](references/editing-rules.md). Make a short removal list and preservation list for each photo. Preserve the original-to-result mapping across batches.

- Remove vehicle/window glare, utility poles, wires, and incidental crowds along the lower edge (차창 반사광·전봇대·전선·하단 단체관광객·군중 제거). Preserve the main subject in portraits, statues and their hands, and genuine water reflections.
- Match one or two existing illustrations with restrained transparent watercolor and fine colored-pencil lines (절제된 투명 수채화·섬세한 색연필 선). Default to watercolor for landscapes and colored pencil for architectural or artifact details, while prioritizing the established style.
- Keep tables, numbers, maps, and exhibition panels as `documentary-photo` assets to preserve their meaning.
- Preserve the original composition, aspect ratio, perspective, and major architecture by default. An explicit user request or subsequent explicit approval of a specific result may authorize a framing exception, including portrait-to-landscape reframing (세로 사진의 가로 구도 변경), cropping, or outpainting. Record the exact user instruction or approval, the original and final dimensions, the affected framing, and generated additions; do not infer blanket approval for other images. Keep architecture and factual details faithful even when reframing is authorized.

## 3. Perform visual edits

- Read the currently available **imagegen skill** and use the built-in image tool. Inspect local originals and reference images in a viewer first. Follow the current tool's supported file-path or conversation-image reference mechanism; do not guess arguments.
- Combine cleanup and style conversion in one request when practical. Add only the actual removal and preservation requirements to the prompts in [editing-rules.md](references/editing-rules.md).
- Compare each result against its original. Check for residual crowds, damage to the main subject, clipped towers, distorted proportions, changed windows or patterns, fabricated text, and warped reflections. Re-edit only what needs correction. Do not overwrite approved assets or originals.
- If the tool fails, follow the imagegen skill's fallback rules. Do not substitute an arbitrary API, CLI, or Pillow filter for visual editing.

## 4. Prepare mobile assets

Obtain the final generated file's local path. Do not leave project assets only in the default generation location. The Python/Pillow script below performs EXIF orientation, resizing, WebP encoding, and metadata removal **without visual editing**. Resolve the script path relative to this skill directory.

iPhone HEIC/HEIF originals are supported when `pillow-heif` is installed. If the codec is unavailable, use an available conversion tool to create a PNG/JPEG working copy while preserving orientation, color, and dimensions, and record its mapping to the original. Do not merely change the extension or overwrite the original.

```bash
python scripts/optimize-images.py \
  --input /absolute/path/final-illustration.png \
  --source /absolute/path/original.jpeg \
  --id city-subject-watercolor --style watercolor \
  --out-dir /absolute/path/project/public/illustrations
```

- `--style`: `watercolor`, `colored-pencil`, or `documentary-photo`. Default candidate widths are 480/800/1200 px, with a **250,000-byte** limit per file. Neither output dimension may exceed the corresponding dimension of the original, generated image, or specified previous edit. Add the largest feasible width for small originals; never upscale.
- For edits to an existing illustration, add `--edit-input /path/previous-edit.png`. Explicitly use `--framing outpaint` for requested frame extensions and `--framing crop` for crops. The default `preserve` mode rejects aspect-ratio deviations of 0.3% or more. For a user-authorized framing exception, select the truthful framing mode, record the specific approval and original/final dimensions, and use a narrowly scoped validation exception rather than bypassing all checks. Do not resize originals or misuse framing options to bypass checks.
- Store the JSON output's `audit` separately in audit documentation; copy only necessary fields into the manifest. A generic `framingEdit: outpaint/crop` value does not automatically satisfy a project's narrower exceptions.
- Do not overwrite existing files by default. Use `--overwrite` only for authorized replacements. If the size budget is exceeded even at the quality floor, resolve the cause instead of disabling checks.

## 5. Integrate and complete

- For guide work, follow [guide-integration.md](references/guide-integration.md) to update the manifest, Korean captions (한글 캡션), alt text, single placement, and required attribution. Do not commit original JPEG/HEIC files, generated PNG files, or private local paths to public repositories.
- Verify actual decoding, dimensions, aspect ratio, file size, metadata, and duplicates. Check mobile captions, overflow, `srcset`, and offline behavior. Distinguish desktop emulation from tests on an actual iPhone; never mark an unperformed test as passed.
- Preserve actual prompts, tools, sources, generated additions, file hashes, and validation evidence in audit records. Briefly report original-to-asset mappings, storage locations, key edits, verification, and limitations.
- Follow the user's authorization and repository instructions for saving, committing, pushing, PR creation, merging, and deployment. This skill grants no additional publishing authority. Do not unnecessarily reconfirm actions already authorized.

## Canonical derivative filenames

- For new Caucasus guide derivatives, use `caucasus-YYYYMMDD-place-subject-style-WIDTH.webp` (lowercase ASCII kebab-case) and `shared/public/illustrations/` unless the repository explicitly defines a different shared asset root. Use actual pixel width, the user-confirmed date, the correct destination, and `watercolor`, `pencil`, or `photo` (documentary) for the style token. Existing established filenames must not be renamed without a reference audit.
- Group responsive widths under one stable logical illustration ID. Preserve uploaded filename as an intake alias and verified Git blob SHA/byte count, then verify SHA-256, decoding and dimensions before publishing or declaring a visual-cache hit. Rename or relocate an already uploaded derivative using its existing Git blob object when supported, without recompressing and without uploading an original.
- Consult the destination repository's naming document, such as `shared/images/ASSET-NAMING.md`, and let its coordinating agent decide placements and record canonical lineage.

## Publish through a separate skill

- This skill owns image cleanup, illustration, optimization, hash calculation, provenance, and visual revision caching. It produces validated assets and a publication handoff; it does not implement GitHub transport, authentication, branch updates, or PR creation.
- For repository publication, the coordinating agent invokes [publish-github-assets](../publish-github-assets/SKILL.md) with the approved derivative file, SHA-256, target repository path, base ref, and authorization scope. Do not send original photos or their encoded copies.
- The publishing skill verifies transport availability and checks the remote result. If transport fails, keep the local approved artifact and its lineage; do not register a nonexistent published variant or claim a PR was created.

## Scoped revisions and deferred merge

- Apply the repository README's scoped-work and deferred-merge policy. For small guide changes, batch related edits, check the affected diff/assets/behavior, and leave the PR open. Run the complete repository suite and required build/integration checks on the integrated result only when the user requests merging.
- Reuse approved illustrations and valid check records after matching hashes and relevant dependencies. Caption, alt-text or placement changes do not require new artwork. Re-encode only when encoding inputs change; regenerate only when the requested visual edit changes.
- Avoid unrelated whole-guide audits, repeated status polling and extra image variants. Preserve per-image validation for new or changed assets; defer broader regression checks to the merge stage. Parallel image workers can reduce elapsed time but do not guarantee lower credit use.
