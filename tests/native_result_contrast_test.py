"""Bounded D4 native result-body contrast, actual compositor backgrounds.

Three appearances, empty and locally completed result. No service connection,
text-size/geometry mutation, token-only ratio, or broader page audit.
"""
import json,os,subprocess,traceback
from playwright.sync_api import sync_playwright
import storage_origin_test as native
import confirmation_reading_test as reading
import d4_accessibility_test as d4
RESULTS=[]
SELECTOR='#stackRoot > .stack-page[data-kind="result"] > .stack-scroll'

def result_body(page,name,completed):
    reading.go(page,'CLD-03')
    if completed:
        page.locator('#screen').focus();page.keyboard.press('m')
        page.locator('#pulley [data-menu="0"]').click()
        page.wait_for_function('S.job.status==="done"',timeout=10000)
        native.ensure(page.evaluate('S.job.source===S.notes'),'Local result changed its original input snapshot')
    page.locator('#screen').focus();page.keyboard.press('m')
    page.locator('#pulley [data-menu="1"]').click()
    page.wait_for_function('currentTask==="cloud" && stack.at(-1)?.kind==="result"')
    d4.settle(page)
    body=page.locator(SELECTOR).filter(visible=True)
    native.ensure(body.count()==1,'Must measure the actual native result body')
    text=body.text_content()
    if completed:native.ensure(text==page.evaluate('S.job.result') and bool(text),'Rendered result differs from the completed local result')
    else:native.ensure(text.startswith('整理尚未完成'),'Empty native result state was not shown')
    before=page.evaluate('JSON.stringify({notes:S.notes,photo:S.photo,job:S.job,outbox:Suite.state().localOutbox})')
    page.locator('#phone').screenshot(path=str(native.OUT/(name+'-visible.png')),animations='disabled')
    d4.SAMPLES['native-result']=[SELECTOR]
    measured=d4.contrast(page,name,'native-result')
    native.ensure(page.evaluate('JSON.stringify({notes:S.notes,photo:S.photo,job:S.job,outbox:Suite.state().localOutbox})')==before,'Contrast capture changed original result or business state')
    page.keyboard.press('Escape');page.wait_for_function('stack.length===0 && currentTask==="cloud"')
    native.assert_original(page)
    return {'state':'completed' if completed else 'empty','samples':measured,'original_notes_preserved':True}

def main():
    native.OUT=native.OUT/'native-result-contrast';native.OUT.mkdir(parents=True,exist_ok=True);version=None
    try:
        with native.preview_server() as origin,sync_playwright() as pw:
            opts={'headless':True}
            if os.environ.get('CHROMIUM_PATH'):opts['executable_path']=os.environ['CHROMIUM_PATH']
            browser=pw.chromium.launch(**opts);version=browser.version
            for name,theme,mode in [('light','light','glass'),('dark','dark','glass'),('highcontrast','light','contrast')]:
                for completed in [False,True]:
                    case=name+('-completed' if completed else '-empty')
                    try:
                        with native.case(browser,origin) as page:d4.configure(page,theme,mode);details=result_body(page,case,completed)
                        RESULTS.append(dict(name=case,status='pass',details=details))
                    except Exception as e:traceback.print_exc();RESULTS.append(dict(name=case,status='fail',error=str(e)))
            browser.close()
    except Exception as e:traceback.print_exc();RESULTS.append(dict(name='harness',status='fail',error=str(e)))
    for name,items in [('no-page-errors',native.ERRORS),('no-outbound',native.OUTBOUND)]:RESULTS.append(dict(name=name,status='fail' if items else 'pass',details=items))
    report=dict(source_head=subprocess.check_output(['git','rev-parse','HEAD'],text=True,cwd=native.ROOT).strip(),browser=version,selector=SELECTOR,checks=RESULTS,passed=sum(x['status']=='pass' for x in RESULTS),failed=sum(x['status']=='fail' for x in RESULTS),not_tested=['physical devices','OS text size','screen readers','unrelated pages or result states'])
    (native.OUT/'native-result-contrast-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False));return bool(report['failed'])
if __name__=='__main__':raise SystemExit(main())
