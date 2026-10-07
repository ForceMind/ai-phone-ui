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
SURFACES = ('backup-settings', 'backup-cloud', 'photo-gallery', 'photo-camera-import', 'photo-export')


def observe(page, stage):
    value = page.evaluate('''() => ({route: Suite.current().id, task: currentTask,
        page: stack.at(-1)?.kind || 'root', documentFocused: document.hasFocus(), inputEvents: window.__ui014Inputs || [], mode: stack.at(-1)?.mode || null,
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
            'photo-gallery': 'IMG-10', 'photo-camera-import': 'IMG-01', 'photo-export': 'IMG-02'}[surface]


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
        page.locator('#screen').focus()
        page.keyboard.press('m')
        opener(page, surface).focus()
        page.keyboard.press('Enter')
    else:
        opener(page, surface).focus()
        with page.expect_file_chooser() as chooser:
            page.keyboard.press('Enter', delay=40)
        if surface.startswith('backup'):
            file = {'name': 'synthetic-backup.json', 'mimeType': 'application/json',
                    'buffer': json.dumps(native.fixture('candidate')).encode()}
        else:
            file = {'name': 'synthetic-photo.png', 'mimeType': 'image/png',
                    'buffer': base64.b64decode(native.PNG.split(',')[1])}
        chooser.value.set_files(file)
    page.wait_for_function('stack.at(-1)?.kind === "confirm"')
    if surface.startswith('backup'):
        native.ensure(dialog(page, 'accept').inner_text().strip() == '确认恢复', 'Backup acceptance must be labeled as restore, not export')
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
    if surface in ('backup-settings', 'photo-export'):
        page.screenshot(path=str(OUT / ('keyboard-focus-' + surface + '.png')), animations='disabled')


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
    page.keyboard.press('Escape')
    native.reload_page(page)
    native.assert_original(page)


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



def overlay_guards(page):
    open_review(page, 'backup-settings')
    dialog(page, 'accept').focus()
    page.evaluate('syncAccess()')
    focused(page, dialog(page, 'accept'), 'same-review-does-not-steal-accept-focus')
    page.keyboard.press('t')
    native.ensure(page.evaluate('overlay') == 'top', 'Existing T overlay did not open')
    page.keyboard.press('Escape')
    focused(page, dialog(page, 'back'), 'overlay-close-resumes-review-focus')
    page.locator('[data-action="ui:catalog"]').click()
    focused(page, page.locator('#mobileCatalogSearch'), 'catalog-focus-not-stolen')
    page.keyboard.press('Tab')
    native.ensure(page.evaluate('!!document.activeElement.closest("#catalogModal")'),
                  'Confirmation trapped Tab through inert workbench')
    page.keyboard.press('Escape')
    native.ensure(page.evaluate('stack.at(-1)?.suiteMode') == 'restore', 'Catalog Escape cancelled review')
    page.keyboard.press('Tab')
    focused(page, dialog(page, 'back'), 'return-from-catalog-remains-reachable')
    native.assert_original(page)


def other_task_resume(page):
    open_review(page, 'backup-settings')
    task = page.evaluate('currentTask')
    page.keyboard.press('h')
    page.locator('[data-task="notes"]').click()
    native.ensure(page.evaluate('currentTask') == 'notes', 'Did not enter another task')
    page.keyboard.press('h')
    page.locator('[data-task="' + task + '"]').click()
    focused(page, dialog(page, 'back'), 'copied-session-retains-safe-focus')
    page.keyboard.press('Escape')
    assert_return(page, 'backup-settings')


def keyboard_accept(page, surface):
    open_review(page, surface)
    focused(page, dialog(page, 'back'), surface + ':before-accept')
    page.keyboard.press('Tab')
    focused(page, dialog(page, 'accept'), surface + ':accept-reachable')
    if surface.startswith('backup'):
        route = native.initial_route(page)
        with page.expect_navigation(wait_until='load'):
            page.keyboard.press('Enter')
        native.ready(page, route)
        native.assert_restored(page, native.fixture('candidate'))
    elif surface == 'photo-export':
        version = page.evaluate('stack.at(-1).versionId')
        source = page.evaluate('S.photo.source')
        # A newer selected version must not replace the reviewed export snapshot.
        page.evaluate('S.photo.current = 0')
        downloads = []
        page.on('download', lambda d: downloads.append(d.suggested_filename))
        with page.expect_download() as result:
            page.keyboard.press('Enter')
        native.ensure(result.value.suggested_filename == 'SWIPE-' + version + '.png', 'Export changed fixed version')
        page.keyboard.press('Enter')
        page.wait_for_timeout(100)
        native.ensure(downloads == ['SWIPE-' + version + '.png'], 'Accepted more than once')
        native.ensure(page.evaluate('S.photo.source') == source, 'Export changed original pixels')
        native.ensure(page.evaluate('S.drafts.photo') == 'original photo draft', 'Export lost draft')
    else:
        page.keyboard.press('Enter')
        page.wait_for_function('S.photo.name === "synthetic-photo.png"')
        native.ensure(page.evaluate('currentTask') == 'photo', 'Accepted import changed destination')
        native.ensure(page.evaluate('S.photo.versions.length') == 1, 'Import did not create its single original')
        native.ensure(page.evaluate('S.drafts.photo') == 'original photo draft', 'Import lost continuing draft')


def keyboard_quota(page):
    open_review(page, 'backup-settings')
    native.fill_quota(page)
    before = native.stored(page)
    page.keyboard.press('Tab')
    page.keyboard.press('Enter')
    page.wait_for_function('document.getElementById("toast").textContent.includes("恢复未完成")')
    native.ensure(not page.evaluate('stack.at(-1).consumed'), 'Quota failure consumed review')
    focused(page, dialog(page, 'accept'), 'quota-failure-keeps-accept-focused')
    native.ensure(native.stored(page) == before, 'Quota failure changed durable state')
    native.assert_original(page)
    page.keyboard.press('Escape')
    assert_return(page, 'backup-settings')


def abandoned_picker(page):
    native.go(page, 'IMG-10')
    opener(page, 'photo-gallery').focus()
    with page.expect_file_chooser() as chooser:
        page.keyboard.press('Enter', delay=40)
    native.go(page, 'DOC-02')
    chooser.value.set_files({'name': 'stale.png', 'mimeType': 'image/png',
                            'buffer': base64.b64decode(native.PNG.split(',')[1])})
    native.ensure(page.evaluate('currentTask') == 'notes', 'Old picker resurrected photo task')
    native.ensure(not page.evaluate('stack.some(p => p.kind === "confirm")'), 'Old picker reopened review')
    native.assert_original(page)


def run_case(browser, server, name, fn):
    print('RUN', name, flush=True)
    try:
        with native.case(browser, server) as page:
            # Keep interception enabled for the whole document. A per-use listener
            # can race its asynchronous protocol setup against an immediate key.
            page.on('filechooser', lambda chooser: None)
            page.evaluate("""() => {
              window.__ui014Inputs = [];
              for (const type of ['keydown', 'keyup', 'click']) window.addEventListener(type, e => {
                const item = {type, key: e.key, target: e.target.id || e.target.dataset.action || e.target.tagName,
                  trusted: e.isTrusted, activation: navigator.userActivation.isActive,
                  blockedUntil: clickBlock, now: performance.now()};
                window.__ui014Inputs.push(item);
                if (window.__ui014Inputs.length > 20) window.__ui014Inputs.shift();
                queueMicrotask(() => item.prevented = e.defaultPrevented);
              }, true);
            }""")
            page.bring_to_front()
            page.wait_for_function('document.hasFocus()')
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
            for name, fn in [('overlay-and-inert-guards', overlay_guards), ('other-task-resume', other_task_resume),
                             ('keyboard-quota-failure', keyboard_quota), ('abandoned-picker', abandoned_picker)]:
                run_case(browser, server, name, fn)
            for surface in ('backup-settings', 'photo-export', 'photo-gallery'):
                run_case(browser, server, surface + ':keyboard-accept', lambda p, s=surface: keyboard_accept(p, s))
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
