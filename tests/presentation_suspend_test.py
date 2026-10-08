"""Read-only presentation interruption regressions on synthetic local data.

Keep the real scroll anchoring behavior enabled. Observe mounted content through
system overlays and lock/resume; never patch layout, handlers, or reading offsets.
"""
import json
import os
import subprocess
import traceback

from playwright.sync_api import sync_playwright

import confirmation_reading_test as reading
import storage_origin_test as native

RESULTS, TRACE = [], []
CONFIGS = [('v3-360', 'baseline', 'baseline'),
           ('v4-360', 'v4', 'baseline'),
           ('v4-393', 'v4', 'portrait')]


def configure(page, version, viewport):
    page.locator('#designVersion').select_option(version)
    if version == 'v4':
        page.locator('#designViewport').select_option(viewport)
    expected = [393, 852] if viewport == 'portrait' else [360, 672]
    page.wait_for_function('size => {const e = document.getElementById("screen"); '
                           'return e.clientWidth === size[0] && e.clientHeight === size[1]}',
                           arg=expected)


def settled(page):
    # Longer than the longest existing 290 ms navigation transition. Retain
    # native browser layout and scroll anchoring rather than modifying styles.
    page.wait_for_timeout(350)


def reading_state(page, stage):
    state = reading.observe(page, stage)
    state['presentation'] = page.evaluate('document.documentElement.dataset.designSample')
    state['visible_route'] = page.evaluate('Suite.current().id')
    state['payload'] = page.evaluate('JSON.stringify(stack.at(-1).payload)')
    TRACE.append({'stage': stage, **state})
    return state


def assert_review_unchanged(page, before, after):
    native.ensure(after['payload'] == before['payload'], 'Interruption changed fixed review payload')
    native.ensure(after['outbox'] == 0, 'Interruption accepted the pending review')
    native.ensure(after['visible_route'] == 'DAY-05', 'Interruption lost the source page')
    native.ensure(after['focus'] == 'back', 'Resumed review did not focus safe cancel')
    reading.bounded(after)
    native.ensure(abs(after['scrollTop'] - before['scrollTop']) <= 1,
                  'Interruption lost reading position: before=' + str(before['scrollTop']) +
                  ', after=' + str(after['scrollTop']) +
                  ', presentation=' + str(after['presentation']))
    reading.tail_visible(after)
    page.keyboard.press('Escape')
    reading.cancelled(page)


def top_overlay(page, name):
    reading.open_review(page)
    reading.wheel_end(page)
    before = reading_state(page, name + ':before')
    reading.tail_visible(before)
    reading.screenshot(page, name + '-before')
    page.keyboard.press('t')
    page.wait_for_function('overlay === "top"')
    settled(page)
    reading_state(page, name + ':covered')
    reading.screenshot(page, name + '-covered')
    page.keyboard.press('Escape')
    page.wait_for_function('overlay === ""')
    settled(page)
    after = reading_state(page, name + ':after')
    reading.screenshot(page, name + '-after')
    assert_review_unchanged(page, before, after)


def lock_resume(page, name):
    reading.open_review(page)
    task = page.evaluate('currentTask')
    reading.wheel_end(page)
    before = reading_state(page, name + ':before')
    reading.tail_visible(before)
    reading.screenshot(page, name + '-before')
    page.locator('.hw[data-action="power"]').click()
    page.wait_for_function('locked && sleeping')
    settled(page)
    reading_state(page, name + ':asleep')
    page.locator('.hw[data-action="power"]').click()
    page.wait_for_function('locked && !sleeping')
    page.keyboard.press('Enter')
    page.wait_for_function('!locked && !sleeping && !appOpen')
    settled(page)
    page.locator('[data-task="' + task + '"]').click()
    page.wait_for_function('appOpen && stack.at(-1)?.suiteMode === "message"')
    settled(page)
    after = reading_state(page, name + ':after')
    reading.screenshot(page, name + '-after')
    assert_review_unchanged(page, before, after)


def photo_overlay(page, name):
    reading.go(page, 'IMG-02')
    settled(page)
    stage = page.locator('#photoStage').bounding_box()
    side = min(stage['width'], stage['height'])  # The native fixture is square.
    page.mouse.click(stage['x'] + stage['width'] / 2 + side * .2,
                     stage['y'] + stage['height'] / 2 + side * .1)
    selection = page.evaluate('JSON.stringify(S.photo.selection)')
    native.ensure(selection != 'null', 'Photo setup did not select image content')
    before = page.evaluate('JSON.stringify({photo:S.photo,notes:S.notes,drafts:S.drafts})')
    page.keyboard.press('t')
    page.wait_for_function('overlay === "top"')
    settled(page)
    page.keyboard.press('Escape')
    page.wait_for_function('overlay === ""')
    settled(page)
    stage = page.locator('#photoStage').bounding_box()
    ring = page.locator('#selection').bounding_box()
    point = json.loads(selection)
    side = min(stage['width'], stage['height'])
    expected_x = stage['x'] + (stage['width'] - side) / 2 + point['x'] * side
    expected_y = stage['y'] + (stage['height'] - side) / 2 + point['y'] * side
    TRACE.append({'stage': name, 'photo_stage': stage, 'ring': ring,
                  'selection': point, 'expected_center': [expected_x, expected_y]})
    reading.screenshot(page, name + '-after')
    native.ensure(abs(ring['x'] + ring['width'] / 2 - expected_x) <= 1 and
                  abs(ring['y'] + ring['height'] / 2 - expected_y) <= 1,
                  'Overlay dismissal lost selected-image ring geometry')
    native.ensure(page.evaluate('JSON.stringify({photo:S.photo,notes:S.notes,drafts:S.drafts})') == before,
                  'Overlay changed photo selection, versions, notes, or drafts')


def main():
    native.OUT = native.OUT / 'presentation-suspend'
    browser_version = None
    try:
        with native.preview_server() as origin, sync_playwright() as pw:
            options = {'headless': True}
            if os.environ.get('CHROMIUM_PATH'):
                options['executable_path'] = os.environ['CHROMIUM_PATH']
            browser = pw.chromium.launch(**options)
            browser_version = browser.version
            for config, version, viewport in CONFIGS:
                for kind, run in [('top-overlay-reading', top_overlay),
                                  ('lock-resume-reading', lock_resume),
                                  ('photo-overlay-geometry', photo_overlay)]:
                    name = config + '-' + kind
                    print('RUN', name, flush=True)
                    try:
                        with native.case(browser, origin) as page:
                            configure(page, version, viewport)
                            run(page, name)
                        RESULTS.append({'name': name, 'status': 'pass'})
                    except Exception as exc:
                        traceback.print_exc()
                        RESULTS.append({'name': name, 'status': 'fail', 'error': str(exc)})
            browser.close()
    except Exception as exc:
        traceback.print_exc()
        RESULTS.append({'name': 'harness', 'status': 'fail', 'error': str(exc)})
    for name, items in [('no-page-errors', native.ERRORS), ('no-outbound', native.OUTBOUND)]:
        RESULTS.append({'name': name, 'status': 'fail' if items else 'pass', 'details': items})
    report = {'source_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'],
                cwd=native.ROOT, text=True).strip(), 'browser': browser_version,
              'checks': RESULTS, 'trace': TRACE,
              'passed': sum(r['status'] == 'pass' for r in RESULTS),
              'failed': sum(r['status'] == 'fail' for r in RESULTS),
              'not_tested': ['physical devices', 'screen readers', 'mobile soft keyboard',
                             'OS font scaling', 'real OS lock/unlock']}
    native.OUT.mkdir(parents=True, exist_ok=True)
    (native.OUT / 'presentation-suspend-results.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return bool(report['failed'])


if __name__ == '__main__':
    raise SystemExit(main())
