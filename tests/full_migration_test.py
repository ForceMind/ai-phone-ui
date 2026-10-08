"""D3 route-by-route presentation and recovery matrix; no external services."""
import json,os,subprocess,traceback
from playwright.sync_api import sync_playwright
import storage_origin_test as native
import confirmation_reading_test as reading
import viewport_adapter_test as viewport
RESULTS=[]
CATALOG=json.loads((native.ROOT/'src/data/screens.json').read_text())
def verify_route(page,route,theme,capture_state):
    reading.go(page,route['id'])
    page.wait_for_function('id=>document.documentElement.dataset.designRoute===id && document.documentElement.dataset.designSample==="true"',arg=route['id'])
    native.ensure(page.evaluate('Suite.current().id')==route['id'],'Route identity changed')
    visible=page.locator('.suite-scroll').filter(visible=True)
    if visible.count():
        geometry=visible.last.evaluate('e=>{const r=e.getBoundingClientRect(),s=document.getElementById("screen").getBoundingClientRect(),h=e.parentElement.querySelector(".suite-header")?.getBoundingClientRect();return {overflow:e.scrollWidth>e.clientWidth+1,height:e.clientHeight,within:r.bottom<=s.bottom+1,overlap:h&&h.bottom>r.top+1}}')
        native.ensure(not geometry['overflow'] and geometry['height']>90 and geometry['within'] and not geometry['overlap'],route['id']+' bad reading region '+str(geometry))
    if route['id'] in ['SET-02','SET-11']:
        before_prefs=page.evaluate('JSON.stringify({core:S,suite:Suite.state()})')
        button=page.locator('[data-design-preference="opaque"]').filter(visible=True).last
        initial=page.locator('#designOpaque').is_checked();button.click()
        native.ensure(page.locator('#designOpaque').is_checked()!=initial,'Product opacity preference did not apply')
        button.click()
        native.ensure(page.evaluate('JSON.stringify({core:S,suite:Suite.state()})')==before_prefs,'Presentation preference changed business data')
    page.locator('#phone').screenshot(path=str(native.OUT/(theme+'-'+route['id']+'.png')),animations='disabled')
    before=page.evaluate('JSON.stringify({notes:S.notes,photo:S.photo,drafts:S.drafts,stack:stack.map(x=>({kind:x.kind,payload:x.payload,route:x.routeId}))})')
    # Every route retains all four explicit design-state previews and a non-mutating dismissal.
    for state in ['empty','loading','error','offline']:
        page.evaluate('x=>Suite.showState(x)',state)
        native.ensure(page.locator('#suiteStateOverlay').count()==1,'Missing '+state)
        if capture_state and route['id'] not in ['SYS-05','SYS-06']:
            page.locator('#phone').screenshot(path=str(native.OUT/(theme+'-'+route['id']+'-'+state+'.png')),animations='disabled')
        page.evaluate('Suite.showState("default")')
        native.ensure(page.locator('#suiteStateOverlay').count()==0,'State layer did not dismiss')
    page.locator('#designVersion').select_option('baseline');page.locator('#designVersion').select_option('v4')
    native.ensure(page.evaluate('JSON.stringify({notes:S.notes,photo:S.photo,drafts:S.drafts,stack:stack.map(x=>({kind:x.kind,payload:x.payload,route:x.routeId}))})')==before,'State preview/rollback altered content or confirmation')
    page.evaluate('Suite.go("SYS-01")')
    page.wait_for_function('Suite.current().id==="SYS-01" && !locked && !sleeping && !appOpen')
def main():
    native.OUT=native.OUT/'full-migration';native.OUT.mkdir(parents=True,exist_ok=True);version=None
    try:
        with native.preview_server() as origin,sync_playwright() as pw:
            opts={'headless':True}
            if os.environ.get('CHROMIUM_PATH'):opts['executable_path']=os.environ['CHROMIUM_PATH']
            browser=pw.chromium.launch(**opts);version=browser.version
            for theme in ['light','dark']:
                groups=set()
                with native.case(browser,origin,original=native.fixture('migration',source='')) as page:
                    viewport.configure(page);page.locator('#designTheme').select_option(theme)
                    for route in CATALOG:
                        group=route['id'].split('-')[0]
                        try:verify_route(page,route,theme,group not in groups);RESULTS.append({'name':theme+'-'+route['id'],'status':'pass','group':group})
                        except Exception as e:
                            traceback.print_exc();page.locator('#phone').screenshot(path=str(native.OUT/(theme+'-'+route['id']+'-FAIL.png')),animations='disabled');RESULTS.append({'name':theme+'-'+route['id'],'status':'fail','error':str(e),'group':group})
                        groups.add(group)
            browser.close()
    except Exception as e:traceback.print_exc();RESULTS.append({'name':'harness','status':'fail','error':str(e)})
    for name,items in [('no-page-errors',native.ERRORS),('no-outbound',native.OUTBOUND)]:RESULTS.append({'name':name,'status':'fail' if items else 'pass','details':items})
    report={'source_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True,cwd=native.ROOT).strip(),'browser':version,'checks':RESULTS,'passed':sum(x['status']=='pass' for x in RESULTS),'failed':sum(x['status']=='fail' for x in RESULTS),'not_tested':['physical devices','screen readers','mobile keyboard','external services']}
    (native.OUT/'full-migration-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False));return bool(report['failed'])
if __name__=='__main__':raise SystemExit(main())
