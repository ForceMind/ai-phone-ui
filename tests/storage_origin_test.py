"""UI-011 against HTTP + native Chromium localStorage, never a storage mock.

Starts the existing loopback preview server on an OS-assigned port. Each case has
an isolated browser context and synthetic data. The quota probe changes only one
fixture key, is bounded at 16 Mi code units, and requires QuotaExceededError.
No device, HTTPS, cross-tab conflict, or OS storage-pressure claim is made.
"""
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
import base64
import hashlib
import random
import struct
import zlib
import json
import os
import re
import subprocess
import sys
import time
import traceback
from urllib.parse import parse_qs, urlsplit

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'test-results'
CORE = 'ai-phone-ui-core-v1'
SUITE = 'ai-phone-ui-suite-v1'
SNAPSHOT = 'ai-phone-ui-state-v1'
FILLER = 'ui011-test-only-quota-filler'
PNG = ('data:image/png;base64,'
       'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a/aQAAAAASUVORK5CYII=')
RESULTS, ERRORS, OUTBOUND, QUOTAS, IMAGES = [], [], [], [], []


def ensure(value, message='Assertion failed'):
    if not value:
        raise AssertionError(message)


def check(name, fn):
    print('RUN', name, flush=True)
    try:
        fn()
        RESULTS.append({'name': name, 'status': 'pass'})
    except Exception as exc:
        RESULTS.append({'name': name, 'status': 'fail', 'error': str(exc)[:2000]})
        traceback.print_exc()


def synthetic_png(width, height, noisy=False):
    """Real, bounded PNG bytes, generated without third-party image dependencies."""
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data))
    rng = random.Random(11011)
    rows = (b'\0' + (rng.randbytes(width * 3) if noisy else bytes((48, 120, 176)) * width)
            for _ in range(height))
    compressor = zlib.compressobj()
    compressed = b''.join(compressor.compress(row) for row in rows) + compressor.flush()
    data = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', compressed) + chunk(b'IEND', b''))
    IMAGES.append({'width': width, 'height': height, 'pixels': width * height,
                   'encoded_bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(), 'noisy': noisy})
    return 'data:image/png;base64,' + base64.b64encode(data).decode()


def fixture(label, source=PNG):
    return {
        'format': 'ai-phone-ui-backup', 'version': 1,
        'core': {
            'schema': 3, 'notes': label + ' notes', 'theme': 'sea',
            'photo': {'source': source, 'name': label + '.png', 'current': 1,
                      'selection': None, 'versions': [
                          {'id': 'original', 'label': 'Original', 'ops': []},
                          {'id': 'warm', 'label': 'Warm copy', 'ops': [{'type': 'warm', 'region': None}]}]},
            'drafts': {'photo': label + ' photo draft'},
            'job': {'status': 'idle', 'progress': 0, 'source': '', 'cursor': 0,
                    'lines': [], 'items': [], 'result': ''},
            'focus': {'seconds': 600, 'running': False}, 'events': []},
        'suite': {'schema': 1, 'nickname': label + ' phone',
                  'forms': {'DAY-02': {'eventTitle': label + ' event draft'}},
                  'drafts': {'DAY-02': label + ' event draft'},
                  'calendar': [{'id': label, 'title': label + ' calendar', 'date': '2026-10-07', 'time': '09:00', 'note': ''}]}}


def values(backup, snapshot=False):
    pair = {CORE: json.dumps(backup['core']), SUITE: json.dumps(backup['suite'])}
    if snapshot:
        return {SNAPSHOT: json.dumps({'format': 'ai-phone-ui-local-state', 'version': 1,
                                    'core': pair[CORE], 'suite': pair[SUITE]})}
    return pair


@contextmanager
def preview_server():
    OUT.mkdir(parents=True, exist_ok=True)
    log_path = OUT / 'storage-origin-server.log'
    with log_path.open('w') as log:
        process = subprocess.Popen([sys.executable, 'scripts/serve.py', '--port', '0'],
                                   cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        try:
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                text = log_path.read_text()
                match = re.search(r'Preview: (http://127\.0\.0\.1:\d+)', text)
                if match:
                    yield match.group(1)
                    return
                if process.poll() is not None:
                    raise RuntimeError('Preview server failed: ' + text[-2000:])
                time.sleep(0.05)
            raise RuntimeError('Preview server did not become ready within 10 seconds')
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


def ready(page, initial_route):
    # Core image initialization sets `ready` before Workbench's scheduled deep-link
    # restoration. Wait for that visible route too, or the old URL route can
    # overwrite the test's next navigation on a fast runner after reload.
    page.wait_for_function('''route => typeof Suite !== "undefined" && ready &&
        typeof Workbench !== "undefined" && Suite.current().id === route &&
        location.hash === "#screen=" + route''', arg=initial_route)
    ensure(page.evaluate('localStorage instanceof Storage'), 'Native Storage is required')


def initial_route(page):
    route = parse_qs(urlsplit(page.url).fragment).get('screen', [''])[0]
    ensure(re.fullmatch(r'[A-Z]{2,3}-\d{2}', route), 'Explicit startup route is required')
    return route


def reload_page(page):
    route = initial_route(page)
    page.reload(wait_until='load')
    ready(page, route)


@contextmanager
def case(browser, origin, snapshot=False, original=None):
    seeded = values(original or fixture('original'), snapshot)
    context = browser.new_context(viewport={'width': 1440, 'height': 1000},
        storage_state={'cookies': [], 'origins': [{'origin': origin, 'localStorage': [
            {'name': key, 'value': value} for key, value in seeded.items()]}]})
    page = context.new_page()
    page.set_default_timeout(5000)
    page.on('pageerror', lambda err: ERRORS.append(str(err)))
    context.route('**/*', lambda route: route.continue_() if
        route.request.url.startswith(origin + '/') else
        (OUTBOUND.append(route.request.url), route.abort())[-1])
    try:
        response = page.goto(origin + '/index.html#screen=SET-10', wait_until='load')
        ensure(response.status == 200, 'Preview must be served successfully over HTTP')
        ready(page, 'SET-10')
        yield page
    finally:
        context.close()


def go(page, route):
    page.evaluate('(id) => Suite.go(id)', route)


def stored(page):
    return page.evaluate('keys => Object.fromEntries(keys.map(k => [k, localStorage.getItem(k)]))',
                         [CORE, SUITE, SNAPSHOT])


def live(page):
    return page.evaluate('({core: S, suite: Suite.state()})')


def assert_original(page, backup=None):
    backup = backup or fixture('original')
    state = live(page)
    for key in ('notes', 'photo'):
        ensure(state['core'][key] == backup['core'][key], 'Original core ' + key + ' was changed')
    ensure(state['core']['drafts']['photo'] == backup['core']['drafts']['photo'], 'Original photo draft was lost')
    ensure(state['suite']['nickname'] == backup['suite']['nickname'], 'Original suite was replaced')
    ensure(state['suite']['forms']['DAY-02'] == backup['suite']['forms']['DAY-02'], 'Original form draft was lost')
    ensure(state['suite']['drafts']['DAY-02'] == backup['suite']['drafts']['DAY-02'], 'Original suite draft was lost')


def import_file(page, raw, name='restore.json'):
    page.locator('#suiteBackupInput').set_input_files({
        'name': name, 'mimeType': 'application/json', 'buffer': raw})


def review(page, backup):
    import_file(page, json.dumps(backup).encode())
    page.wait_for_function('stack.at(-1)?.suiteMode === "restore"')
    expect(page.locator('.dialog-inner').last).to_contain_text('恢复本机资料')
    ensure(page.locator('#suiteBackupInput').input_value() == '', 'File input must allow selecting the same file again')


def click_dialog(page, action):
    page.locator('#stackRoot .stack-page').last.locator('[data-action="' + action + '"]').click()


def commit_and_reload(page):
    # This observes the application's real reload. No call to location.reload is stubbed.
    route = initial_route(page)
    with page.expect_navigation(wait_until='load'):
        click_dialog(page, 'accept')
    ready(page, route)
    ensure(page.evaluate('performance.getEntriesByType("navigation")[0].type') == 'reload',
           'The production confirmation must reload the document')


def assert_restored(page, backup):
    state = live(page)
    ensure(state['core']['notes'] == backup['core']['notes'], 'Core did not survive reload')
    ensure(state['suite']['nickname'] == backup['suite']['nickname'], 'Suite did not survive reload')
    ensure(state['core']['photo']['source'] == backup['core']['photo']['source'], 'Photo original changed on reload')
    ensure(state['core']['photo']['versions'] == backup['core']['photo']['versions'], 'Photo versions changed')
    ensure(state['core']['drafts']['photo'] == backup['core']['drafts']['photo'], 'Core draft lost')
    ensure(state['suite']['forms']['DAY-02']['eventTitle'] == backup['suite']['forms']['DAY-02']['eventTitle'], 'Suite draft lost')
    raw = stored(page)
    ensure(raw[CORE] is None and raw[SUITE] is None, 'Legacy keys were not cleaned after commit')
    snapshot = json.loads(raw[SNAPSHOT])
    ensure(json.loads(snapshot['core'])['notes'] == backup['core']['notes'], 'Durable core mismatch')
    ensure(json.loads(snapshot['suite'])['nickname'] == backup['suite']['nickname'], 'Durable suite mismatch')


def migration(browser, origin, snapshot=False):
    with case(browser, origin, snapshot) as page:
        go(page, 'SET-10')
        before = stored(page)
        new = fixture('restored')
        new['core']['job']['status'] = 'running'
        new['core']['focus']['running'] = True
        new['suite']['remoteState'] = 'connected'
        new['suite']['schedules'] = [{'id': 'schedule', 'name': 'Do not run', 'time': '09:00', 'enabled': True}]
        review(page, new)
        ensure(stored(page) == before, 'Selecting a backup wrote data before confirmation')
        assert_original(page)
        commit_and_reload(page)
        assert_restored(page, new)
        ensure(page.evaluate('S.job.status') == 'paused', 'Restored job auto-started')
        ensure(not page.evaluate('S.focus.running'), 'Restored focus auto-started')
        ensure(page.evaluate('Suite.state().remoteState') == 'disconnected', 'Forged connection survived')
        ensure(not page.evaluate('Suite.state().schedules[0].enabled'), 'Restored schedule enabled itself')
        reload_page(page)
        assert_restored(page, new)
        # Exercise normal production saves after migration, preserving the other half.
        go(page, 'DOC-02')
        page.locator('#noteEditor').fill('edited after real reload')
        page.wait_for_function('JSON.parse(JSON.parse(localStorage.getItem("ai-phone-ui-state-v1")).core).notes === "edited after real reload"')
        go(page, 'DAY-02')
        page.locator('[data-field="eventTitle"]').filter(visible=True).last.fill('new suite draft')
        reload_page(page)
        ensure(page.evaluate('S.notes') == 'edited after real reload', 'Suite save overwrote core')
        ensure(page.evaluate('Suite.state().forms["DAY-02"].eventTitle') == 'new suite draft', 'Core save overwrote suite')
        ensure(page.evaluate('S.photo.source') == PNG, 'Normal saves lost original photo')


def legacy_reload(browser, origin):
    with case(browser, origin) as page:
        assert_original(page)
        ensure(stored(page)[SNAPSHOT] is None, 'Startup must not migrate before a successful restore')
        reload_page(page)
        assert_original(page)
        ensure(stored(page)[SNAPSHOT] is None, 'Reload must retain legacy mode')


def cancel(browser, origin):
    with case(browser, origin) as page:
        go(page, 'CLD-17')
        before = stored(page)
        review(page, fixture('cancelled'))
        click_dialog(page, 'back')
        ensure(not page.evaluate('stack.some(p => p.suiteMode === "restore")'), 'Cancelled dialog remains')
        ensure(stored(page) == before, 'Cancel changed durable data')
        assert_original(page)
        reload_page(page)
        assert_original(page)


def reject(browser, origin, raw, expected):
    with case(browser, origin) as page:
        go(page, 'SET-10')
        before = stored(page)
        import_file(page, raw)
        expect(page.locator('#toast')).to_contain_text(expected)
        ensure(not page.evaluate('stack.some(p => p.suiteMode === "restore")'), 'Invalid file opened confirmation')
        ensure(stored(page) == before, 'Rejected file changed native storage')
        assert_original(page)
        reload_page(page)
        assert_original(page)


def fill_quota(page):
    result = page.evaluate('''key => {
        const limit = 16 * 1024 * 1024;
        let low = 0, high = limit, attempts = 0, quotaErrors = 0;
        const write = n => {
            attempts++;
            try { localStorage.setItem(key, 'q'.repeat(n)); return true; }
            catch (error) {
                if (error.name !== 'QuotaExceededError') throw error;
                quotaErrors++; return false;
            }
        };
        if (write(limit)) throw Error('Native quota not reached within the 16 Mi code-unit bound');
        while (low + 1 < high) {
            const mid = Math.floor((low + high) / 2);
            if (write(mid)) low = mid; else high = mid;
        }
        if (!quotaErrors || !low || attempts > 26) throw Error('Invalid bounded quota probe');
        return {filledCodeUnits: localStorage.getItem(key).length, attempts, quotaErrors, boundCodeUnits: limit};
    }''', FILLER)
    QUOTAS.append(result)


def quota(browser, origin, snapshot=False, retry=True, image_source=None):
    original = fixture('original', image_source or PNG)
    with case(browser, origin, snapshot, original) as page:
        go(page, 'SET-10')
        new = fixture('quota restored', image_source or PNG)
        new['core']['notes'] = 'restored under quota ' + ('x' * 29000)
        review(page, new)
        before = stored(page)
        before_live = live(page)
        if image_source:
            ensure(len(image_source) > 1024 * 1024, 'Image must occupy over 1 Mi native storage code units')
            ensure(page.evaluate('([baseCanvas.width, baseCanvas.height])') == [512, 512], 'Occupancy image did not decode')
        document_token = page.evaluate('window.__ui011Document = Math.random().toString(36)')
        fill_quota(page)
        for _ in range(2):
            click_dialog(page, 'accept')
            expect(page.locator('#toast')).to_contain_text('恢复未完成')
            ensure(page.evaluate('window.__ui011Document') == document_token, 'Failure reloaded the page')
            ensure(page.evaluate('stack.at(-1)?.suiteMode === "restore" && !stack.at(-1).consumed'), 'Confirmation lost retry state')
            ensure(stored(page) == before, 'Quota failure changed original durable bytes')
            ensure(live(page) == before_live, 'Quota failure changed in-memory data')
            expect(page.locator('#storageError')).to_be_visible()
            assert_original(page, original)
        if retry:
            page.evaluate('key => localStorage.removeItem(key)', FILLER)
            commit_and_reload(page)
            assert_restored(page, new)
            reload_page(page)
            assert_restored(page, new)
        else:
            click_dialog(page, 'back')
            ensure(not page.evaluate('stack.some(p => p.suiteMode === "restore")'), 'Cancel left a pending dialog')
            ensure(stored(page) == before, 'Cancel after failure changed durable data')
            page.evaluate('key => localStorage.removeItem(key)', FILLER)
            reload_page(page)
            assert_original(page, original)
            # Same file can be selected after cancellation; approval is required again.
            review(page, new)
            assert_original(page, original)
            click_dialog(page, 'back')


def image_boundary(browser, origin, source):
    with case(browser, origin) as page:
        page.set_default_timeout(15000)
        new = fixture('16MP boundary', source)
        before = stored(page)
        review(page, new)
        ensure(stored(page) == before, 'Boundary image wrote before approval')
        assert_original(page)
        commit_and_reload(page)
        assert_restored(page, new)
        ensure(page.evaluate('([baseCanvas.width, baseCanvas.height])') == [4000, 4000],
               'Exact 16MP boundary was replaced or resized')
        reload_page(page)
        assert_restored(page, new)


def reject_image(browser, origin, source):
    with case(browser, origin) as page:
        page.set_default_timeout(15000)
        before = stored(page)
        before_live = live(page)
        import_file(page, json.dumps(fixture('invalid image', source)).encode())
        page.wait_for_function('stack.at(-1)?.suiteMode === "restore" || document.querySelector("#toast").textContent.includes("无法恢复")')
        ensure(not page.evaluate('stack.some(p => p.suiteMode === "restore")'),
               'Undecodable/over-16MP image reached replacement approval instead of rejection')
        expect(page.locator('#toast')).to_contain_text('无法恢复')
        ensure(stored(page) == before, 'Rejected image changed durable bytes')
        ensure(live(page) == before_live, 'Rejected image changed live originals or drafts')
        reload_page(page)
        assert_original(page)


def main():
    browser_version = None
    origin = None
    try:
        with preview_server() as origin, sync_playwright() as pw:
            options = {'headless': True}
            executable = os.environ.get('CHROMIUM_PATH')
            if executable:
                options['executable_path'] = executable
            browser = pw.chromium.launch(**options)
            browser_version = browser.version
            check('native:legacy-reload-without-premature-migration', lambda: legacy_reload(browser, origin))
            check('native:legacy-to-snapshot-confirm-reload-and-normal-saves', lambda: migration(browser, origin))
            check('native:snapshot-replacement-confirm-reload-and-normal-saves', lambda: migration(browser, origin, True))
            check('native:cancel-valid-import-retains-both-sections-after-reload', lambda: cancel(browser, origin))
            check('native:malformed-json-rejected-before-writing', lambda: reject(browser, origin, b'{broken', '无法恢复'))
            wrong = fixture('invalid'); wrong['version'] = 99
            check('native:unsupported-backup-version-rejected', lambda: reject(browser, origin, json.dumps(wrong).encode(), '无法恢复'))
            bad = fixture('invalid'); bad['core']['photo']['source'] = 'https://example.invalid/photo.png'
            check('native:external-photo-backup-rejected', lambda: reject(browser, origin, json.dumps(bad).encode(), '无法恢复'))
            oversized = json.dumps(fixture('oversized')).encode() + b' ' * (12 * 1024 * 1024)
            check('native:over-12MiB-backup-rejected-before-writing', lambda: reject(browser, origin, oversized, '备份超过 12 MB'))
            for snapshot in (False, True):
                for retry in (False, True):
                    mode = ('snapshot' if snapshot else 'legacy') + ('-retry' if retry else '-cancel')
                    check('native:bounded-quota-' + mode, lambda s=snapshot, r=retry: quota(browser, origin, s, r))
            boundary = synthetic_png(4000, 4000)
            oversized_image = synthetic_png(4001, 4000)
            occupancy = synthetic_png(512, 512, noisy=True)
            check('native:image-exact-16MP-confirm-and-reload', lambda: image_boundary(browser, origin, boundary))
            check('native:image-over-16MP-rejected-before-replacement', lambda: reject_image(browser, origin, oversized_image))
            encoded_invalid = 'data:image/png;base64,' + base64.b64encode(b'valid base64 but not a decodable PNG').decode()
            check('native:image-valid-base64-undecodable-rejected', lambda: reject_image(browser, origin, encoded_invalid))
            check('native:image-occupied-legacy-quota-cancel-and-reload', lambda: quota(browser, origin, retry=False, image_source=occupancy))
            check('native:image-occupied-snapshot-quota-retry-and-reload', lambda: quota(browser, origin, snapshot=True, image_source=occupancy))
            check('native:no-page-errors' , lambda: ensure(not ERRORS, str(ERRORS)))
            check('native:no-external-requests', lambda: ensure(not OUTBOUND, str(OUTBOUND)))
            browser.close()
    except Exception as exc:
        RESULTS.append({'name': 'harness:startup-or-teardown', 'status': 'fail', 'error': str(exc)[:4000]})
        traceback.print_exc()
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'timestamp': datetime.now(timezone.utc).isoformat(), 'source_head': head,
              'browser': browser_version, 'origin': origin,
              'harness': 'HTTP scripts/serve.py; native localStorage; real file input, confirmation clicks and document reload',
              'not_tested': ['physical Android/iOS', 'HTTPS deployment', 'OS disk pressure',
                             'physical-device large-image memory pressure', 'concurrent-tab conflict resolution', 'camera/microphone permissions'],
              'total': len(RESULTS), 'passed': sum(x['status'] == 'pass' for x in RESULTS),
              'failed': sum(x['status'] == 'fail' for x in RESULTS), 'page_errors': ERRORS,
              'external_requests': OUTBOUND, 'quota_probes': QUOTAS, 'synthetic_images': IMAGES, 'checks': RESULTS}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'storage-origin-results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({key: report[key] for key in ('source_head', 'browser', 'total', 'passed', 'failed')}, indent=2))
    return 1 if report['failed'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
