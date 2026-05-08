# Windows Codex Handoff: Horosa v1.3.4 Qimen Tianpan Fix

This folder is the Windows-side handoff package for the Horosa/星阙 `v1.3.4` Dunjia/Qimen fix.

The macOS/web side has already been fixed and verified. The Windows side should sync the same algorithm and tests, but must adapt the release work to Windows.

## Hard Boundary

- Do not run Apple signing on Windows.
- Do not run Apple notarization on Windows.
- Do not use Developer ID, `notarytool`, `stapler`, `.pkg`, `.app`, or macOS Gatekeeper checks.
- Do not copy the macOS packaging workflow into the Windows repository.
- Use only the Windows repository's own installer/build/release flow.

## What Was Fixed

Bug: Qimen/Dunjia Tianpan heavenly stems appeared fixed and did not move correctly when the selected time changed.

Root cause: the Tianpan calculation was anchored on the Zhifu star palace. The legacy Horosa Qimen result anchors Tianpan flying with:

- source palace = Earth-pan palace of the hour Xun-head Liuyi stem
- target palace = Earth-pan palace of the current hour heavenly stem

Then it flies the Qiyi sequence around the eight outer palaces by Yang clockwise / Yin reverse order.

## macOS/Web Source Files

Use these files as the working reference:

- `/Users/horacedong/Desktop/Horosa-Primary Direction Trial/Horosa-Web/astrostudyui/src/components/dunjia/DunJiaCalc.js`
- `/Users/horacedong/Desktop/Horosa-Primary Direction Trial/Horosa-Web/astrostudyui/src/components/dunjia/__tests__/DunJiaCalc.test.js`
- `/Users/horacedong/Desktop/Horosa-Primary Direction Trial/Horosa-Web/astrostudyui/src/components/sanshi/__tests__/SanShiUnitedMain.test.js`

Legacy app reference:

- `/Users/horacedong/Desktop/玄哲/玄學奧術/玄學軟件大全/星阙网站/Horosa-APP-main/星阙/前端/App/lib/models/qi_men.dart`
- `/Users/horacedong/Desktop/玄哲/玄學奧術/玄學軟件大全/星阙网站/Horosa-APP-main/星阙/前端/App/lib/services/qi_men.dart`

The legacy app calls `/trigram/qimen`; compare against its response shape: `tianpan`, `dipan`, `men`, `xing`, `shen`, `zhifushi`, `paiju`.

## Files In This Package

- `ALGORITHM_SPEC.md`: exact algorithm and constants.
- `VALIDATION_CASES.md`: golden sample, hour-by-hour sample, and batch test plan.
- `WINDOWS_CODEX_PROMPT.md`: complete prompt to paste into Windows Codex.

## Acceptance Criteria

- Dunjia/Qimen standalone chart Tianpan stems change correctly when time changes.
- Sanshi United uses the same fixed Dunjia calculation.
- AI export / AI analysis snapshots use the same fixed result when serializing Qimen or Sanshi.
- Golden sample `1998-02-20 20:48` matches `阳遁九局上元` and Tianpan `1庚 2丙 3丁 4戊 6己 7壬 8辛 9乙`.
- Batch validation across dozens of cases passes.
- Windows release, if published, contains only Windows assets and no Apple signing/notarization steps.
