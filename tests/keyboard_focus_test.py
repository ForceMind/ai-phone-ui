"""UI-014: native HTTP-origin keyboard/cancel regressions for existing reviews.

Only synthetic files are selected. Browser focus is observed, never mocked.
Desktop Chromium results do not claim screen-reader or physical-phone coverage.
"""
from datetime import datetime, timezone
import base64
import json
import os
import subprocess
import traceback
from playwright.sync_api import sync_playwright
import storage_origin_test as native

ROOT, OUT = native.ROOT, native.OUT
RESULTS, TRACE = [], []
SURFACES = ('backup-settings', 'backup-cloud', 'photo-gallery', 'photo-camera', 'photo-export')


def observe(page, stage):
    value = page.evaluate('''() => ({route: Suite.current().id, task: currentTask,
        page: stack.at(-1)?.kind || 'root', mode: stack.at(-1)?.mode || null,
        focus: {tag: document.activeElement?.tagName, id: document.activeElement?.id,
          action: document.activeElement?.dataset.action || null,
          menu: document.activeElement?.dataset.menu || null,
          inReview: !!document.activeElement?.closest('#stackRoot .stack-page[data-kind="confirm"]')},
        reviewCount: stack.filter(p => p.kind === 'confirm').length})''')
    TRACE.append({'stage': stage, **value})
    return value


def focused(page, locator, label):
    state = observe(page, label)
    native.ensure(locator.evaluate('(el) => document.activeElement === el'),
                  label + ': ' + json.dumps(state, ensure_ascii=False))


def dialog(page, action):
    return page.locator('#stackRoot .stack-page').last.locator('[data-action="' + action + '"]')


def origin(surface):
    return {'backup-settings': 'SET-10', 'backup-cloud': 'CLD-17',
            'photo-gallery': 'IMG-10', 'photo-camera': 'IMG-01', 'photo-export': 'IMG-02'}[surface]


def opener(page, surface):
    if surface == 'photo-export':
        return page.locator('#pulley [data-menu="2"]')
    action = 'ui:restore' if surface.startswith('backup') else 'ui:import'
    return page.locator('#task [data-action="' + action + '"]').filter(visible=True).last


def open_review(page, surface, navigate=True):
    if navigate:
        native.go(page, origin(surface))
    if surface == 'photo-export':
        # Existing M shortcut opens the existing Pulley; native Enter activates it.
        page.locator('#screen').click(position={'x': 175, 'y': 100})
        page.keyboard.press('m')
        opener(page, surface).focus()
        page.keyboard.press('Enter')
    else:
        opener(page, surface).focus()
        with page.expect_file_chooser() as chooser:
            page.keyboard.press('Enter')
        if surface.startswith('backup'):
            file = {'name': 'synthetic-backup.json', 'mimeType': 'application/json',
                    'buffer': json.dumps(native.fixture('candidate')).encode()}
        else:
            file = {'name': 'synthetic-photo.png', 'mimeType': 'image/png',
                    'buffer': base64.b64decode(native.PNG.split(',')[1])}
        chooser.value.set_files(file)
    page.wait_for_function('stack.at(-1)?.kind === "confirm"')
    observe(page, surface + ':opened')
    native.assert_original(page)


def assert_return(page, surface):
    state = observe(page, surface + ':returned')
    native.ensure(state['page'] != 'confirm', 'Cancel must dismiss the review')
    native.ensure(state['route'] == origin(surface), 'Cancel lost its origin: ' + str(state))
    focused(page, opener(page, surface), surface + ':focus-return')
    native.assert_original(page)


def entry(page, surface):
    open_review(page, surface)
    focused(page, dialog(page, 'back'), surface + ':safe-initial-focus')


def tab_order(page, surface):
    open_review(page, surface)
    # Isolate the cycle independently of the initial-focus assertion.
    dialog(page, 'back').focus()
    for key, action in [('Tab', 'accept'), ('Tab', 'back'),
                        ('Shift+Tab', 'accept'), ('Shift+Tab', 'back')]:
        page.keyboard.press(key)
        focused(page, dialog(page, action), surface + ':' + key + ':' + action)
    native.assert_original(page)


def cancel_return(page, surface, method):
    downloads = []
    page.on('download', lambda download: downloads.append(download.suggested_filename))
    open_review(page, surface)
    if method == 'escape':
        page.keyboard.press('Escape')
    elif method == 'keyboard':
        dialog(page, 'back').focus()
        page.keyboard.press('Enter')
    else:
        dialog(page, 'back').click()
    assert_return(page, surface)
    native.ensure(not downloads, 'Cancel unexpectedly downloaded a file')
    # The same file/command remains reachable; a fresh review still needs consent.
    open_review(page, surface, navigate=False)
    focused(page, dialog(page, 'back'), surface + ':reopened-safe-focus')
    native.assert_original(page)
    native.ensure(not downloads, 'Reopening unexpectedly downloaded a file')


def gesture(page, start, end, reverse=None, cancel=False):
    r = page.locator('#screen').bounding_box()
    def point(p):
        return r['x'] + p[0] * r['width'] / 360, r['y'] + p[1] * r['height'] / 672
    page.mouse.move(*point(start)); page.mouse.down()
    page.mouse.move(*point(end), steps=12)
    if reverse:
        page.mouse.move(*point(reverse), steps=12)
    if cancel:
        page.evaluate("document.getElementById('screen').dispatchEvent(new PointerEvent('pointercancel',{pointerId:1,bubbles:true}))")
    page.mouse.up()
    page.wait_for_timeout(450)  # existing 400 ms post-gesture click suppression


def interrupted_gestures(page, surface):
    open_review(page, surface)
    identity = page.evaluate('JSON.stringify(stack.at(-1))')
    for reverse, cancel in [((230, 420), False), (None, True)]:
        gesture(page, (240, 420), (70, 420), reverse, cancel)
        native.ensure(page.evaluate('JSON.stringify(stack.at(-1))') == identity,
                      'Reversed/cancelled acceptance changed its review snapshot')
        native.assert_original(page)
    gesture(page, (75, 420), (250, 420))
    assert_return(page, surface)


def minimize_reopen(page, surface):
    open_review(page, surface)
    task = page.evaluate('currentTask')
    page.keyboard.press('h')
    native.ensure(not page.evaluate('appOpen'), 'H must preserve existing minimize behavior')
    native.assert_original(page)
    page.locator('[data-task="' + task + '"]').click()
    page.wait_for_function('appOpen && stack.at(-1)?.kind === "confirm"')
    focused(page, dialog(page, 'back'), surface + ':resumed-review-focus')
    native.assert_original(page)
    page.keyboard.press('Escape')
    assert_return(page, surface)


def run_case(browser, server, name, fn):
    print('RUN', name, flush=True)
    try:
        with native.case(browser, server) as page:
            try:
                fn(page)
            except Exception:
                observe(page, name + ':failure')
                page.screenshot(path=str(OUT / (name.replace(':', '-') + '.png')))
                raise
        RESULTS.append({'name': name, 'status': 'pass'})
    except Exception as exc:
        traceback.print_exc()
        RESULTS.append({'name': name, 'status': 'fail', 'error': str(exc)[:2500]})


def main():
    browser_version = server = None
    try:
        with native.preview_server() as server, sync_playwright() as pw:
            options = {'headless': True}
            if os.environ.get('CHROMIUM_PATH'):
                options['executable_path'] = os.environ['CHROMIUM_PATH']
            browser = pw.chromium.launch(**options)
            browser_version = browser.version
            for surface in SURFACES:
                for name, fn in [('entry', entry), ('tab-cycle', tab_order),
                                 ('escape-return-reopen', lambda p, s: cancel_return(p, s, 'escape')),
                                 ('keyboard-cancel-return-reopen', lambda p, s: cancel_return(p, s, 'keyboard')),
                                 ('mouse-cancel-return-reopen', lambda p, s: cancel_return(p, s, 'mouse')),
                                 ('minimize-resume-cancel', minimize_reopen)]:
                    run_case(browser, server, surface + ':' + name, lambda p, s=surface, f=fn: f(p, s))
            for surface in ('backup-settings', 'photo-export'):
                run_case(browser, server, surface + ':gesture-reversal-pointercancel-right-cancel',
                         lambda p, s=surface: interrupted_gestures(p, s))
            browser.close()
    except Exception as exc:
        traceback.print_exc()
        RESULTS.append({'name': 'harness:startup-or-teardown', 'status': 'fail', 'error': str(exc)[:4000]})
    for name, values in [('no-page-errors', native.ERRORS), ('no-external-requests', native.OUTBOUND)]:
        RESULTS.append({'name': name, 'status': 'fail' if values else 'pass', 'details': values})
    report = {'timestamp': datetime.now(timezone.utc).isoformat(),
              'source_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'browser': browser_version, 'origin': server,
              'harness': 'HTTP; native localStorage, file chooser, keyboard Tab/Shift+Tab/Enter/Escape and mouse gestures',
              'not_tested': ['screen readers', 'physical Android/iOS', 'mobile soft keyboards', 'real-device gestures'],
              'total': len(RESULTS), 'passed': sum(r['status'] == 'pass' for r in RESULTS),
              'failed': sum(r['status'] == 'fail' for r in RESULTS), 'checks': RESULTS, 'focus_trace': TRACE}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'keyboard-focus-results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('source_head', 'browser', 'total', 'passed', 'failed')}, indent=2))
    return 1 if report['failed'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
