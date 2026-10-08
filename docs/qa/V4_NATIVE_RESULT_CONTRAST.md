# V4 native result-body contrast

## Confirmed RED

Baseline main: `0509dae7d0b628fd95a978c8fbcc3f63f11ac571`. Test-only commit: `ea337dcda1ae66a0ba08b8519ce7b0221778575e`.
[Run 37792922596](https://github.com/ForceMind/ai-phone-ui/actions/runs/37792922596): old local-ui passed; existing D4 50/50 and child-route 8/8 passed. New result suite 4 passed, 4 failed. Chromium 143.0.7499.4.

Preserved D4 artifact 11557192198, ZIP SHA256 `68e079ebbc426bd3aec8d3957c73be187e0f772642ecc37199b21aa2f9e38883` contains full JSON, visible and masked-background PNGs. Light/highcontrast empty and completed result each measured **1.3805520821569766:1** against 4.5:1; dark empty/completed each measured **11.427409389821817:1**. The inherited foreground was rgb(201,224,223), font 14px / weight 400 / opacity 1. Actual backgrounds were white and rgb(32,35,39).

## Bounded test and minimal repair

`tests/native_result_contrast_test.py` opens native CLD-03 and its actual Pulley result action. The completed case runs the real offline local job and compares rendered text with S.job.result, preserving its input snapshot. The empty case checks the actual incomplete state. Selector: `#stackRoot > .stack-page[data-kind="result"] > .stack-scroll`.

It uses the existing D4 compositor helper: leaf text runs, actual rendered backgrounds with glyph fill hidden while retaining element backgrounds/currentColor/layout; structure, rect and scroll self-checks; visible clipping/occlusion and unsupported-style guards; full-pixel background sampling, sRGB luminance and unrounded thresholds. This is not a token-only ratio. Business state and original notes are checked unchanged; page errors and outbound requests remain failures. Six appearance/state samples plus two safety checks form eight checks.

Repair: `[data-design-surface][data-design-sample=true] .stack-page[data-kind=result]>.stack-scroll{color:var(--v4-text)}`. Only the native V4 result body's semantic foreground changes. No JS, geometry, text sizing, session ownership, confirmation, storage or service changes. V3 is unaffected. This separate confirmed contrast defect does not change PR22's unconfirmed review finding or the successful cross-task reading-position evidence.

## Completion gate and limits

[PR23](https://github.com/ForceMind/ai-phone-ui/pull/23) records exact candidate/main runs and final evidence. Require build, 26 static and 134 unit checks, all existing native suites, D4 50, child-route 8 and native-result 8; inspect all six final visible result images and verify artifact source_head/dist bytes. Normal merge only after the exact candidate passes, then independently verify main before replacing the same delivered HTML.

This is a representative native-result body gate, not whole-site accessibility certification. It does not add 200%/native zoom/OS-size assertions to this suite; the prior D4 actual 200% matrix remains independent. Physical devices, OS text sizes, screen readers and unrelated pages/states remain unverified here. Pages deployment and real services remain separate.
