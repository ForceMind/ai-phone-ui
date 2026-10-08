"""D2 shared surfaces: migrated route pixels and real local closures, no service claims."""
import json,os,subprocess,traceback
from pathlib import Path
from playwright.sync_api import sync_playwright
import storage_origin_test as native
import confirmation_reading_test as reading
import keyboard_focus_test as keyboard
import candidate_ownership_test as candidates
import viewport_adapter_test as viewport

RESULTS=[]
ROUTES=[r['id'] for r in json.loads((native.ROOT/'src/data/screens.json').read_text()) if r.get('v4Migration',{}).get('phase')=='D2']
def configure(page):
    viewport.configure(page)
def snapshots(page,theme):
    page.locator('#designTheme').select_option(theme)
    for route in ROUTES:
        reading.go(page,route)
        page.wait_for_function('id=>document.documentElement.dataset.designRoute===id && document.documentElement.dataset.designSample==="true"',arg=route)
        surface=page.locator('.suite-scroll').filter(visible=True)
        if surface.count():
            box=surface.last.evaluate('e=>({w:e.clientWidth,sw:e.scrollWidth})')
            native.ensure(box['sw']<=box['w']+1,route+' has horizontal content overflow')
        page.locator('#phone').screenshot(path=str(native.OUT/(theme+'-'+route+'.png')),animations='disabled')
        before=page.evaluate('JSON.stringify({notes:S.notes,photo:S.photo,drafts:S.drafts})')
        page.locator('#designVersion').select_option('baseline')
        page.locator('#designVersion').select_option('v4')
        native.ensure(page.evaluate('JSON.stringify({notes:S.notes,photo:S.photo,drafts:S.drafts})')==before,route+' rollback changed content')
        page.locator('#screen').focus();page.keyboard.press('Escape')
        native.ensure(page.evaluate('Suite.current().id')!=None,route+' exit lost route')
def note_flow(page):
    reading.go(page,'DOC-02')
    editor=page.locator('#noteEditor')
    editor.fill('D2 原文保留\n第二条需要整理\nD2 原文保留')
    editor.blur()
    original=page.evaluate('S.notes')
    page.locator('#screen').focus();page.keyboard.press('h')
    page.locator('[data-task="notes"]').click()
    native.ensure(editor.input_value()==original,'Notes lost on task resume')
    reading.go(page,'CLD-04')
    page.locator('[data-action="ui:job-toggle"]').filter(visible=True).last.click()
    page.wait_for_function('S.job.status==="done"',timeout=20000)
    native.ensure(page.evaluate('S.job.source')==original,'Job lost source snapshot')
    reading.go(page,'DOC-04')
    expected=page.evaluate('S.job.result')
    native.ensure(bool(expected),'No local result produced')
    page.locator('[data-action="ui:export-document"]').filter(visible=True).last.click()
    page.wait_for_function('stack.at(-1)?.kind==="confirm"')
    page.keyboard.press('Escape')
    native.ensure(page.evaluate('S.notes')==original,'Cancel changed source')
    page.locator('[data-action="ui:export-document"]').filter(visible=True).last.click()
    with page.expect_download() as download: keyboard.dialog(page,'accept').click()
    native.ensure(Path(download.value.path()).read_text()==expected,'Downloaded result differs from fixed text')
    page.locator('#phone').screenshot(path=str(native.OUT/'notes-result.png'),animations='disabled')
def main():
    native.OUT=native.OUT/'core-flows';native.OUT.mkdir(parents=True,exist_ok=True)
    browser_version=None
    try:
        with native.preview_server() as origin,sync_playwright() as pw:
            options={'headless':True}
            if os.environ.get('CHROMIUM_PATH'):options['executable_path']=os.environ['CHROMIUM_PATH']
            browser=pw.chromium.launch(**options);browser_version=browser.version
            cases=[('light-migrated-routes',lambda p:snapshots(p,'light')),('dark-migrated-routes',lambda p:snapshots(p,'dark')),('notes-source-result-export',note_flow),('photo-fixed-export',lambda p:keyboard.keyboard_accept(p,'photo-export')),('photo-candidate-cancel-resume',candidates.photo_cancel_newer),('backup-cancel-resume',keyboard.other_task_resume),('execution-confirmation-cancel',reading.gesture_reading),('execution-confirmation-once',reading.resume_accept)]
            for name,fn in cases:
                try:
                    with native.case(browser,origin) as page:configure(page);fn(page)
                    RESULTS.append({'name':name,'status':'pass'})
                except Exception as exc:traceback.print_exc();RESULTS.append({'name':name,'status':'fail','error':str(exc)})
            browser.close()
    except Exception as exc:traceback.print_exc();RESULTS.append({'name':'harness','status':'fail','error':str(exc)})
    for name,items in [('no-page-errors',native.ERRORS),('no-outbound',native.OUTBOUND)]:RESULTS.append({'name':name,'status':'fail' if items else 'pass','details':items})
    report={'source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=native.ROOT,text=True).strip(),'browser':browser_version,'migrated_routes':ROUTES,'checks':RESULTS,'passed':sum(x['status']=='pass' for x in RESULTS),'failed':sum(x['status']=='fail' for x in RESULTS),'not_tested':['real execution services','physical devices','screen readers','mobile keyboard']}
    (native.OUT/'core-flows-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False));return bool(report['failed'])
if __name__=='__main__':raise SystemExit(main())
