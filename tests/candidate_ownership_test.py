"""Bounded import ownership regressions: real HTTP, file choosers and task covers.

Synthetic files only. This is desktop Chromium evidence, not physical-device QA.
"""
from datetime import datetime, timezone
import base64
import json
import os
import subprocess
import traceback
from playwright.sync_api import sync_playwright
import storage_origin_test as native

RESULTS, TRACE = [], []


def observe(page, stage):
    state = page.evaluate('''() => ({task: currentTask, route: Suite.current().id,
        reviews: stack.filter(p => p.kind === 'confirm').map(p => ({mode:p.mode,
          suiteMode:p.suiteMode, title:p.title, name:p.payload?.name, consumed:!!p.consumed})),
        photo:S.photo.name, notes:S.notes, nickname:Suite.state().nickname})''')
    TRACE.append({'stage': stage, **state})
    return state


def go(page, route):
    # The workbench is the existing page-entry UI; no hidden route mutation.
    page.locator('#catalogNav [data-screen-id="' + route + '"]').click()
    page.wait_for_function('id => Suite.current().id === id', arg=route)


def select(page, action, filename, raw, mime):
    opener = page.locator('#task [data-action="' + action + '"]').filter(visible=True).last
    with page.expect_file_chooser() as chooser:
        opener.click()
    chooser.value.set_files({'name': filename, 'mimeType': mime, 'buffer': raw})


def backup(page, label, route):
    go(page, route)
    select(page, 'ui:restore', label + '.json', json.dumps(native.fixture(label)).encode(), 'application/json')
    page.wait_for_function('stack.at(-1)?.suiteMode === "restore"')
    task = page.evaluate('currentTask')
    observe(page, label + ':reviewed')
    native.assert_original(page)
    return task


def leave(page):
    page.keyboard.press('h')
    native.ensure(not page.evaluate('appOpen'), 'Task was not minimized')


def resume(page, task):
    if page.evaluate('appOpen'):
        leave(page)
    page.locator('[data-task="' + task + '"]').click()
    page.wait_for_function('task => appOpen && currentTask === task', arg=task)


def backup_older(page, newer):
    owner = backup(page, 'candidate-A', 'SET-10')
    leave(page)
    backup(page, 'candidate-B', 'CLD-17')
    if newer == 'cancelled':
        native.click_dialog(page, 'back')
    elif newer == 'invalid':
        native.click_dialog(page, 'back')
        select(page, 'ui:restore', 'invalid.json', b'{broken', 'application/json')
        page.wait_for_function('document.getElementById("toast").textContent.includes("无法恢复")')
    resume(page, owner)
    native.ensure(page.evaluate('stack.at(-1)?.payload?.name') == 'candidate-A.json', 'Did not resume older A review')
    native.assert_original(page)
    observe(page, 'A:before-accept-after-B-' + newer)
    native.commit_and_reload(page)
    observe(page, 'A:after-production-reload')
    native.assert_restored(page, native.fixture('candidate-A'))


def backup_cancel_older(page):
    older = backup(page, 'candidate-A', 'SET-10')
    leave(page)
    newer = backup(page, 'candidate-B', 'CLD-17')
    resume(page, older)
    native.click_dialog(page, 'back')
    native.assert_original(page)
    resume(page, newer)
    native.ensure(page.evaluate('stack.at(-1)?.payload?.name') == 'candidate-B.json', 'Newer B review lost')
    native.commit_and_reload(page)
    native.assert_restored(page, native.fixture('candidate-B'))


def photo_cancel_newer(page):
    go(page, 'IMG-10')
    select(page, 'ui:import', 'candidate-A.png', base64.b64decode(native.PNG.split(',')[1]), 'image/png')
    page.wait_for_function('stack.at(-1)?.mode === "import"')
    native.assert_original(page)
    leave(page)
    go(page, 'IMG-01')
    second = native.synthetic_png(3, 2)
    select(page, 'ui:import', 'candidate-B.png', base64.b64decode(second.split(',')[1]), 'image/png')
    page.wait_for_function('stack.filter(p => p.mode === "import").length === 2')
    native.assert_original(page)
    observe(page, 'photo:B:above-A')
    native.click_dialog(page, 'back')
    native.ensure(page.evaluate('Suite.current().id') == 'IMG-01', 'Cancel did not return to newer opener')
    resume(page, 'photo')
    native.ensure(page.evaluate('stack.filter(p => p.mode === "import").length') == 1, 'Older photo review lost')
    native.assert_original(page)
    native.click_dialog(page, 'accept')
    page.wait_for_function('S.photo.name !== "original.png"')
    observe(page, 'photo:A:after-accept')
    native.ensure(page.evaluate('S.photo.name') == 'candidate-A.png', 'Older A review imported another file')
    native.ensure(page.evaluate('({w:baseCanvas.width,h:baseCanvas.height})') == {'w': 1, 'h': 1}, 'Accepted wrong candidate pixels')
    native.ensure(page.evaluate('S.photo.versions.length') == 1, 'Import did not produce its own original')
    native.ensure(page.evaluate('S.drafts.photo') == 'original photo draft', 'Import lost continuing draft')
    native.reload_page(page)
    native.ensure(page.evaluate('S.photo.name') == 'candidate-A.png', 'Accepted candidate lost after reload')


def run(browser, origin, name, fn):
    print('RUN', name, flush=True)
    try:
        with native.case(browser, origin) as page:
            page.on('filechooser', lambda chooser: None)
            page.bring_to_front()
            page.wait_for_function('document.hasFocus()')
            try:
                fn(page)
            except Exception:
                observe(page, name + ':failure')
                page.screenshot(path=str(native.OUT / ('candidate-' + name + '.png')))
                raise
        RESULTS.append({'name': name, 'status': 'pass'})
    except Exception as exc:
        traceback.print_exc()
        RESULTS.append({'name': name, 'status': 'fail', 'error': str(exc)[:2500]})


def main():
    version = origin = None
    try:
        with native.preview_server() as origin, sync_playwright() as pw:
            options = {'headless': True}
            if os.environ.get('CHROMIUM_PATH'):
                options['executable_path'] = os.environ['CHROMIUM_PATH']
            browser = pw.chromium.launch(**options)
            version = browser.version
            for newer in ('pending', 'cancelled', 'invalid'):
                run(browser, origin, 'backup-accept-A-after-B-' + newer, lambda p, n=newer: backup_older(p, n))
            run(browser, origin, 'backup-cancel-A-accept-B', backup_cancel_older)
            run(browser, origin, 'photo-cancel-B-resume-accept-A', photo_cancel_newer)
            browser.close()
    except Exception as exc:
        traceback.print_exc()
        RESULTS.append({'name': 'harness-startup-or-teardown', 'status': 'fail', 'error': str(exc)[:4000]})
    for name, values in [('no-page-errors', native.ERRORS), ('no-external-requests', native.OUTBOUND)]:
        RESULTS.append({'name': name, 'status': 'fail' if values else 'pass', 'details': values})
    report = {'timestamp': datetime.now(timezone.utc).isoformat(),
        'source_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=native.ROOT, text=True).strip(),
        'browser': version, 'origin': origin, 'total': len(RESULTS),
        'passed': sum(r['status'] == 'pass' for r in RESULTS),
        'failed': sum(r['status'] == 'fail' for r in RESULTS), 'checks': RESULTS, 'trace': TRACE,
        'not_tested': ['physical Android/iOS', 'screen readers', 'mobile soft keyboards', 'OS storage pressure']}
    native.OUT.mkdir(parents=True, exist_ok=True)
    (native.OUT / 'candidate-ownership-results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('source_head', 'browser', 'total', 'passed', 'failed')}, indent=2))
    return 1 if report['failed'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
