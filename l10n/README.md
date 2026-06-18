# zh-CN release layer

This fork keeps Chinese localization as a final patch layer instead of editing upstream Cromite patches directly.

## Files

- `build/patches/9999-Chinese-localization.patch`: zh-CN overrides. Keep this as the last patch.
- `l10n/scripts/ensure_zh_patch_last.py`: rewrites `build/cromite_patches_list.txt` so the zh-CN patch remains last.
- `l10n/scripts/check_new_untranslated.py`: checks upstream patch diffs for newly added strings that are not covered by the zh-CN patch.
- `.github/workflows/sync-upstream-zh.yml`: syncs upstream and blocks if new untranslated strings are detected.
- `.github/workflows/zh-arm64-artifact.yml`: builds an arm64 APK artifact on a self-hosted runner.

## Workflow

1. Sync upstream with `Sync upstream with zh-CN guard`.
2. If it fails, check the log for new `IDS_...` values or hardcoded English strings.
3. Add translations to `build/patches/9999-Chinese-localization.patch`.
4. Run `Build zh-CN arm64 artifact`.
5. Download the APK from the workflow run artifacts.

The first arm64 workflow uploads an artifact only. Signing and GitHub Release publishing can be added after the self-hosted runner and keystore secrets are confirmed.
