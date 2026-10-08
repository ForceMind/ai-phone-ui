"""Read-only investigation of PR21's same-task child-route review.

Exercise actual route/keyboard/pulley entry points. Record observed task ownership
instead of assuming the catalog CLD-04 route belongs to the native cloud task.
The existing D4 200% styles persist across production DOM reconstruction.
"""
import json,os,subprocess,traceback
from playwright.sync_api import sync_playwright
import storage_origin_test as native
import confirmation_reading_test as reading
import d4_accessibility_test as d4
RESULTS=[]

def observe(page):
    return page.evaluate('''()=>{const job=document.querySelector('.job-detail');return {route:Suite.current().id,task:currentTask,stack:stack.map(x=>({kind:x.kind,route:x.routeId})),jobNodes:document.querySelectorAll('.job-detail').length,offset:job?.scrollTop??null,font:job?getComputedStyle(job.querySelector('#jobPercent')).fontSize:null,savedCloudOffset:sessions.cloud?.jobScroll??null};}''')

def shot(page,name):page.locator('#phone').screenshot(path=str(native.OUT/(name+'.png')),animations='disabled')

def original_cloud(page,before,name):
    now=observe(page);shot(page,name)
    native.ensure(now['task']=='cloud' and now['route']=='CLD-03','Did not return to the original native cloud reader: '+str(now))
    native.ensure(now['font']==before['font'],'Persistent 200% font rules changed')
    native.ensure(abs(now['offset']-before['offset'])<=1,'Original cloud read position changed: '+str({'before':before,'after':now}))
    native.assert_original(page)
    return now

def probe(page,name):
    d4.open_route(page,'CLD-03');d4.resize(page,name,'CLD-03')
    before=observe(page);native.ensure(before['offset']>0,'Must genuinely scroll the 200% native job reader')
    business=page.evaluate('JSON.stringify({notes:S.notes,photo:S.photo,job:S.job,outbox:Suite.state().localOutbox})')
    shot(page,name+'-before-child')
    # Exact catalog route from the review. Record, do not assume, task identity.
    reading.go(page,'CLD-04');d4.settle(page);child=observe(page);shot(page,name+'-catalog-child')
    native.ensure(child['route']=='CLD-04','Catalog child did not open')
    page.locator('#screen').focus();page.keyboard.press('Escape');d4.settle(page)
    dismissed=observe(page);shot(page,name+'-catalog-child-dismissed')
    native.ensure(dismissed['route']=='CLD-03','Child Back did not return to its catalog parent')
    # Returning to the original native task must retain its own reader.
    page.keyboard.press('h');page.locator('[data-task="cloud"]').click();d4.settle(page)
    from_cover=original_cloud(page,before,name+'-native-cover-resumed')
    # A direct catalog round trip is checked independently of the activity cover.
    reading.go(page,'CLD-04');reading.go(page,'CLD-03');d4.settle(page)
    from_catalog=original_cloud(page,before,name+'-catalog-root-resumed')
    # The real same-cloud child: native Pulley result, not another catalog task.
    page.locator('#screen').focus();page.keyboard.press('m')
    page.locator('#pulley [data-menu="1"]').click();d4.settle(page)
    native.ensure(page.evaluate('currentTask==="cloud" && stack.at(-1)?.kind==="result"'),'Native result did not remain in cloud task')
    native_child=observe(page);shot(page,name+'-native-result-child')
    page.keyboard.press('Escape');d4.settle(page)
    native_back=original_cloud(page,before,name+'-native-result-returned')
    native.ensure(page.evaluate('JSON.stringify({notes:S.notes,photo:S.photo,job:S.job,outbox:Suite.state().localOutbox})')==business,'Navigation changed original data, execution state or outbox')
    return dict(before=before,catalog_child=child,catalog_dismissed=dismissed,cover_resumed=from_cover,catalog_resumed=from_catalog,native_child=native_child,native_returned=native_back)

def main():
    native.OUT=native.OUT/'d4-same-task';native.OUT.mkdir(parents=True,exist_ok=True);version=None
    try:
        with native.preview_server() as origin,sync_playwright() as pw:
            opts={'headless':True}
            if os.environ.get('CHROMIUM_PATH'):opts['executable_path']=os.environ['CHROMIUM_PATH']
            browser=pw.chromium.launch(**opts);version=browser.version
            for theme in ['light','dark']:
                for mode in ['glass','opaque','contrast']:
                    name=theme+'-'+mode
                    try:
                        with native.case(browser,origin) as page:d4.configure(page,theme,mode);details=probe(page,name)
                        RESULTS.append(dict(name=name,status='pass',details=details))
                    except Exception as e:traceback.print_exc();RESULTS.append(dict(name=name,status='fail',error=str(e)))
            browser.close()
    except Exception as e:traceback.print_exc();RESULTS.append(dict(name='harness',status='fail',error=str(e)))
    for name,items in [('no-page-errors',native.ERRORS),('no-outbound',native.OUTBOUND)]:RESULTS.append(dict(name=name,status='fail' if items else 'pass',details=items))
    report=dict(source_head=subprocess.check_output(['git','rev-parse','HEAD'],text=True,cwd=native.ROOT).strip(),browser=version,checks=RESULTS,passed=sum(x['status']=='pass' for x in RESULTS),failed=sum(x['status']=='fail' for x in RESULTS),not_tested=['physical devices','OS font scaling','screen readers','unrelated routes'])
    (native.OUT/'d4-same-task-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False));return bool(report['failed'])
if __name__=='__main__':raise SystemExit(main())
