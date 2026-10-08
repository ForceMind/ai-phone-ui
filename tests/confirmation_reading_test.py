"""Bounded DAY-05 reading checks over real HTTP-origin Chromium.

Synthetic drafts only; actions can create only the existing local preview record.
No page state, scroll position, key handler or layout is patched by this suite.
"""
from datetime import datetime, timezone
import json
import os
import subprocess
import traceback
from playwright.sync_api import sync_playwright
import storage_origin_test as native
from keyboard_focus_test import gesture

RESULTS, TRACE = [], []
LONG = '\n'.join(f'段落 {i:02d}：这是用来检查阅读的虚构草稿。逐段保留固定文字，不发送给任何人。' for i in range(1, 25)) + '\n草稿末尾 END-OF-DRAFT'
UNBROKEN = 'BEGIN-' + 'Abc0123456789' * 160 + '-END-OF-DRAFT'
DISCLAIMER = '向左接受仅写入本机预览记录，不会实际发送。'


def go(page, route):
    page.locator('#catalogNav [data-screen-id="' + route + '"]').click()
    page.wait_for_function('id => Suite.current().id === id', arg=route)


def review(page):
    return page.locator('#stackRoot .stack-page').last


def control(page, action):
    return review(page).locator('[data-action="' + action + '"]')


def observe(page, stage):
    state = review(page).evaluate('''el => {
      const box = el.querySelector('.dialog-inner'), p = box.querySelector('p');
      const rect = e => { const r = e.getBoundingClientRect(); return {x:r.x,y:r.y,right:r.right,bottom:r.bottom,width:r.width,height:r.height}; };
      const range = document.createRange(); range.selectNodeContents(p);
      const lines = [...range.getClientRects()].map(r => ({x:r.x,right:r.right}));
      range.setStart(p.firstChild, p.textContent.lastIndexOf('向左接受'));
      return {scrollTop:box.scrollTop,scrollHeight:box.scrollHeight,clientHeight:box.clientHeight,
        scrollWidth:box.scrollWidth,clientWidth:box.clientWidth,box:rect(box),screen:rect(document.getElementById('screen')),
        head:rect(el.querySelector('.dialog-head')),hint:rect(el.querySelector('.dialog-hint')),
        tail:rect(range),horizontalFit:lines.every(r=>r.x>=rect(box).x-1&&r.right<=rect(box).right+1),
        fontSize:parseFloat(getComputedStyle(p).fontSize),focus:document.activeElement?.dataset.action,
        payloadLength:stack.at(-1).payload.text.length,outbox:Suite.state().localOutbox.length};
    }''')
    TRACE.append({'stage': stage, **state})
    return state


def screenshot(page, name):
    page.locator('#screen').screenshot(path=str(native.OUT / ('reading-' + name + '.png')), animations='disabled')


def open_review(page, text=LONG, large=False):
    if large:
        go(page, 'SET-11')
        page.locator('#task [data-action="ui:toggle:largeText"]').filter(visible=True).last.click()
        native.ensure(page.locator('body').evaluate('el => el.classList.contains("large-text")'), 'Large-text preference did not activate')
    go(page, 'DAY-05')
    page.locator('#task textarea[data-field="message"]').filter(visible=True).last.fill(text)
    page.locator('#task [data-action="ui:confirm-message"]').filter(visible=True).last.click()
    page.wait_for_function('stack.at(-1)?.suiteMode === "message"')
    page.wait_for_function('!topPage().getAnimations().some(a => a.playState === "running")')
    native.ensure(page.evaluate('stack.at(-1).payload.text') == text, 'Review changed exact draft')
    native.ensure(control(page, 'accept').inner_text().strip() == '确认本机预览', 'Message acceptance label must describe its local-only preview effect')
    native.ensure(review(page).locator('p').inner_text().endswith(DISCLAIMER), 'Local-only disclaimer missing')
    native.ensure(control(page, 'back').evaluate('el => document.activeElement === el'), 'Initial focus must stay on cancel')
    native.ensure(page.evaluate('Suite.state().localOutbox.length') == 0, 'Opening review executed a preview')


def bounded(state):
    native.ensure(state['box']['y'] >= state['head']['bottom'] and state['box']['bottom'] <= state['hint']['y'],
                  'Review body extends under controls or past the reading viewport: ' + json.dumps(state))
    native.ensure(state['horizontalFit'] and state['scrollWidth'] <= state['clientWidth'] + 1,
                  'Draft text is horizontally clipped instead of wrapping')


def tail_visible(state):
    native.ensure(state['tail']['y'] >= state['box']['y'] - 1 and state['tail']['bottom'] <= state['box']['bottom'] + 1,
                  'Final local-only disclaimer cannot be read after scrolling')


def wheel_end(page):
    screen = page.locator('#screen').bounding_box()
    page.mouse.move(screen['x'] + screen['width'] / 2, screen['y'] + screen['height'] * .6)
    page.mouse.wheel(0, 100000)
    page.wait_for_timeout(200)


def cancelled(page, text=LONG):
    native.ensure(page.evaluate('stack.at(-1)?.kind') != 'confirm', 'Cancel left review open')
    native.ensure(page.evaluate('Suite.current().id') == 'DAY-05', 'Cancel lost DAY-05')
    native.ensure(page.locator('#task textarea[data-field="message"]').filter(visible=True).last.input_value() == text,
                  'Cancel changed exact draft')
    native.ensure(page.evaluate('Suite.state().localOutbox.length') == 0, 'Cancel wrote a preview record')
    native.assert_original(page)


def reading(page, text, large, name):
    open_review(page, text, large)
    screenshot(page, name + '-start')
    start = observe(page, name + ':start')
    wheel_end(page)
    end = observe(page, name + ':end')
    screenshot(page, name + '-end')
    bounded(start)
    bounded(end)
    tail_visible(end)
    if large:
        native.ensure(start['fontSize'] >= 16, 'Existing large-text setting does not enlarge confirmation body')
    control(page, 'back').click()
    cancelled(page, text)


def keyboard_reading(page):
    open_review(page)
    page.keyboard.press('PageDown')
    native.ensure(observe(page, 'keyboard:page-down')['scrollTop'] > 0, 'PageDown cannot read review from safe cancel focus')
    page.keyboard.press('End')
    tail_visible(observe(page, 'keyboard:end'))
    page.keyboard.press('Home')
    native.ensure(observe(page, 'keyboard:home')['scrollTop'] == 0, 'Home cannot return to beginning')
    for key, action in [('Tab', 'accept'), ('Tab', 'back'), ('Shift+Tab', 'accept'), ('Shift+Tab', 'back')]:
        page.keyboard.press(key)
        native.ensure(control(page, action).evaluate('el => document.activeElement === el'), 'Reading broke button cycle')
    page.keyboard.press('Escape')
    cancelled(page)


def gesture_reading(page):
    open_review(page)
    snapshot = page.evaluate('JSON.stringify(stack.at(-1).payload)')
    gesture(page, (180, 520), (180, 250))
    native.ensure(observe(page, 'gesture:vertical')['scrollTop'] > 0, 'Vertical drag does not scroll review')
    for reverse, cancel in [((230, 420), False), (None, True)]:
        gesture(page, (240, 420), (70, 420), reverse, cancel)
        native.ensure(page.evaluate('JSON.stringify(stack.at(-1).payload)') == snapshot, 'Interrupted swipe replaced fixed review')
        native.ensure(page.evaluate('Suite.state().localOutbox.length') == 0, 'Interrupted swipe accepted review')
    gesture(page, (75, 420), (250, 420))
    cancelled(page)


def resume_accept(page):
    open_review(page)
    task = page.evaluate('currentTask')
    wheel_end(page)
    before = observe(page, 'resume:before')
    native.ensure(before['scrollTop'] > 0, 'Review cannot be scrolled before resume')
    page.keyboard.press('h')
    page.locator('[data-task="notes"]').click()
    page.keyboard.press('h')
    page.locator('[data-task="' + task + '"]').click()
    page.wait_for_function('stack.at(-1)?.suiteMode === "message"')
    native.ensure(page.evaluate('Suite.current().id') == 'DAY-05', 'Resumed confirmation lost its source page route')
    after = observe(page, 'resume:after')
    native.ensure(abs(after['scrollTop'] - before['scrollTop']) <= 1, 'Resuming review lost reading position')
    native.ensure(after['focus'] == 'back', 'Resuming review did not focus cancel')
    tail_visible(after)
    native.ensure(page.evaluate('stack.at(-1).payload.text') == LONG, 'Resuming changed fixed draft')
    screenshot(page, 'resumed-end')
    page.keyboard.press('Tab')
    page.keyboard.press('Enter')
    page.wait_for_function('Suite.state().localOutbox.length === 1')
    page.keyboard.press('Enter')
    outbox = page.evaluate('Suite.state().localOutbox')
    native.ensure(len(outbox) == 1 and outbox[0]['text'] == LONG and outbox[0]['status'] == 'local-preview-only',
                  'Explicit acceptance must write this fixed preview exactly once')
    native.ensure(page.evaluate('Suite.state().messageDraft') == '', 'Accepted local preview did not clear composer')
    native.assert_original(page)


def run(browser, origin, name, fn):
    print('RUN', name, flush=True)
    try:
        with native.case(browser, origin) as page:
            page.bring_to_front()
            page.wait_for_function('document.hasFocus()')
            try:
                fn(page)
            except Exception:
                if page.evaluate('stack.at(-1)?.suiteMode === "message"'):
                    observe(page, name + ':failure')
                screenshot(page, name + '-failure')
                raise
        RESULTS.append({'name': name, 'status': 'pass'})
    except Exception as exc:
        traceback.print_exc()
        RESULTS.append({'name': name, 'status': 'fail', 'error': str(exc)[:3500]})


def main():
    version = origin = None
    try:
        with native.preview_server() as origin, sync_playwright() as pw:
            options = {'headless': True}
            if os.environ.get('CHROMIUM_PATH'):
                options['executable_path'] = os.environ['CHROMIUM_PATH']
            browser = pw.chromium.launch(**options)
            version = browser.version
            for name, text, large in [('ordinary', LONG, False), ('large', LONG, True), ('unbroken', UNBROKEN, False)]:
                run(browser, origin, name, lambda p, t=text, l=large, n=name: reading(p, t, l, n))
            for name, fn in [('keyboard', keyboard_reading), ('gestures', gesture_reading), ('resume-accept', resume_accept)]:
                run(browser, origin, name, fn)
            browser.close()
    except Exception as exc:
        traceback.print_exc()
        RESULTS.append({'name': 'harness-startup-or-teardown', 'status': 'fail', 'error': str(exc)[:4000]})
    for name, values in [('no-page-errors', native.ERRORS), ('no-external-requests', native.OUTBOUND)]:
        RESULTS.append({'name': name, 'status': 'fail' if values else 'pass', 'details': values})
    report = {'timestamp': datetime.now(timezone.utc).isoformat(),
        'source_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=native.ROOT, text=True).strip(),
        'browser': version, 'origin': origin, 'total': len(RESULTS),
        'passed': sum(r['status'] == 'pass' for r in RESULTS), 'failed': sum(r['status'] == 'fail' for r in RESULTS),
        'checks': RESULTS, 'trace': TRACE,
        'not_tested': ['physical Android/iOS', 'screen readers', 'mobile soft keyboards', 'OS text scaling']}
    native.OUT.mkdir(parents=True, exist_ok=True)
    (native.OUT / 'confirmation-reading-results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('source_head', 'browser', 'total', 'passed', 'failed')}, indent=2))
    return 1 if report['failed'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
