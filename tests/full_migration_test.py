"""D3 route-by-route presentation and recovery matrix; no external services."""
import json,os,subprocess,traceback
from playwright.sync_api import sync_playwright
import storage_origin_test as native
import confirmation_reading_test as reading
import viewport_adapter_test as viewport
from keyboard_focus_test import gesture,dialog
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
    if route['id']=='SET-11':
        contrast=page.locator('[data-action="ui:toggle:contrast"]').filter(visible=True).last
        original=page.evaluate('Suite.state().settings.contrast')
        if not original:contrast.click()
        page.locator('#screen').focus();page.keyboard.press('t')
        page.wait_for_function('overlay==="top"')
        native.ensure(page.locator('#topMenu').evaluate('e=>getComputedStyle(e).backdropFilter')=='none','Product high contrast retained glass blur')
        page.keyboard.press('Escape');page.wait_for_function('overlay===""')
        if not original:page.locator('[data-action="ui:toggle:contrast"]').filter(visible=True).last.click()
    page.locator('#phone').screenshot(path=str(native.OUT/(theme+'-'+route['id']+'.png')),animations='disabled')
    before=page.evaluate('JSON.stringify({notes:S.notes,photo:S.photo,drafts:S.drafts})')
    # Use the design-state selector and each real recovery button, including lock/sleep.
    targets={'empty':'DOC-02','error':'AI-04','offline':'IMG-02'}
    for state in ['empty','loading','error','offline']:
        page.locator('#viewState').select_option(state)
        layer=page.locator('#suiteStateOverlay');layer.wait_for(state='visible')
        recovery=layer.locator('button').first
        native.ensure(recovery.evaluate('e=>{const r=e.getBoundingClientRect();return r.width>0&&r.height>0&&e.contains(document.elementFromPoint(r.x+r.width/2,r.y+r.height/2));}'),'State recovery control is obscured: '+state)
        if capture_state or route['id'] in ['SYS-05','SYS-06']:
            page.locator('#phone').screenshot(path=str(native.OUT/(theme+'-'+route['id']+'-'+state+'.png')),animations='disabled')
        recovery.click()
        page.wait_for_function('!document.getElementById("suiteStateOverlay")')
        if state in targets:page.wait_for_function('id=>Suite.current().id===id',arg=targets[state])
        reading.go(page,route['id'])
    review_before=page.evaluate('JSON.stringify(stack.map(x=>({kind:x.kind,payload:x.payload,route:x.routeId})))')
    page.locator('#designVersion').select_option('baseline');page.locator('#designVersion').select_option('v4')
    native.ensure(page.evaluate('JSON.stringify(stack.map(x=>({kind:x.kind,payload:x.payload,route:x.routeId})))')==review_before,'V3 rollback changed fixed confirmation')
    native.ensure(page.evaluate('JSON.stringify({notes:S.notes,photo:S.photo,drafts:S.drafts})')==before,'State recovery/rollback altered content or confirmation')
    # Native keyboard equivalents exercise actual Back/Cancel and wake/unlock handlers.
    page.locator('#screen').focus()
    prior=page.evaluate('({sleeping,locked,overlay,appOpen,depth:stack.length,outbox:Suite.state().localOutbox.length})')
    if prior['sleeping']:
        page.keyboard.press('Enter');page.wait_for_function('!sleeping')
    if page.evaluate('locked'):
        page.keyboard.press('Enter');page.wait_for_function('!locked')
    if prior['overlay']:
        page.keyboard.press('Escape');page.wait_for_function('overlay===""')
    elif prior['appOpen'] and not prior['locked'] and not prior['sleeping']:
        page.keyboard.press('Escape')
        page.wait_for_function('depth=>!appOpen||stack.length<depth',arg=prior['depth'])
    native.ensure(page.evaluate('Suite.state().localOutbox.length')==prior['outbox'],'Back/Cancel accepted a preview action')
    page.keyboard.press('h')
    page.wait_for_function('Suite.current().id==="SYS-01" && !locked && !sleeping && !appOpen')

def guarded_state(page,theme):
    reading.open_review(page);reading.wheel_end(page)
    fixed=page.evaluate('JSON.stringify(stack.at(-1).payload)');offset=page.locator('.dialog-inner').last.evaluate('e=>e.scrollTop')
    page.mouse.move(*viewport.point(page,260,330));page.mouse.down();page.mouse.move(*viewport.point(page,90,330),steps=12)
    page.locator('#viewState').select_option('loading')
    native.ensure(page.evaluate('gesture===null'),'Opening state layer left in-flight confirmation gesture alive')
    page.mouse.up()
    native.ensure(page.locator('#task').evaluate('e=>e.inert'),'State layer left underlying task interactive')
    gesture(page,(270,330),(70,330))
    native.ensure(page.evaluate('JSON.stringify(stack.at(-1).payload)')==fixed,'State layer swipe consumed underlying confirmation')
    native.ensure(page.evaluate('Suite.state().localOutbox.length')==0,'State layer swipe accepted underlying action')
    page.keyboard.press('Tab');page.keyboard.press('Tab')
    native.ensure(page.evaluate('!!document.activeElement.closest("#suiteStateOverlay")'),'State Tab escaped to hidden controls')
    page.keyboard.press('Enter');page.wait_for_function('!document.getElementById("suiteStateOverlay")')
    native.ensure(page.evaluate('JSON.stringify(stack.at(-1).payload)')==fixed,'State primary button accepted underlying action')
    page.locator('#viewState').select_option('loading');page.keyboard.press('Escape')
    page.wait_for_function('!document.getElementById("suiteStateOverlay")')
    native.ensure(page.evaluate('JSON.stringify(stack.at(-1).payload)')==fixed,'State Escape cancelled original confirmation')
    native.ensure(page.locator('.dialog-inner').last.evaluate('e=>e.scrollTop')==offset,'State interruption changed reading offset')
    page.locator('#phone').screenshot(path=str(native.OUT/(theme+'-state-safe-return.png')),animations='disabled')
    dialog(page,'accept').click();native.ensure(page.evaluate('Suite.state().localOutbox.length')==1,'Explicit restored acceptance failed')
def system_footer(page,theme):
    for preset in ['baseline','portrait']:
        page.locator('#designViewport').select_option(preset);reading.go(page,'SYS-04')
        value=page.locator('#topMenu').evaluate('e=>{const f=e.querySelector(".menu-footer"),b=e.querySelector(".settings-row:last-child"),r=e.getBoundingClientRect(),fr=f.getBoundingClientRect(),br=b.getBoundingClientRect();return {overlap:fr.bottom>br.top+1,fit:br.bottom<=r.bottom+1,sub:getComputedStyle(e.querySelector(".sub")).color,label:getComputedStyle(e.querySelector(".ambience span")).color,secondary:getComputedStyle(e).getPropertyValue("--v4-secondary").trim()}}')
        native.ensure(not value['overlap'] and value['fit'],'System footer overlap/overflow '+str(value))
        native.ensure(value['label']=='rgb(255, 255, 255)','Media label lost high-contrast foreground')
        page.locator('#phone').screenshot(path=str(native.OUT/(theme+'-system-footer-'+preset+'.png')),animations='disabled')
        page.locator('#screen').focus();page.keyboard.press('Escape');page.wait_for_function('overlay===""')
    page.locator('#designViewport').select_option('portrait')
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
                    # Real recovery targets create legitimate empty task slots once.
                    # Initialize them before snapshots so retention assertions compare like states.
                    for target in ['DOC-02','AI-04','IMG-02','SYS-01']:reading.go(page,target)
                    for route in CATALOG:
                        group=route['id'].split('-')[0]
                        try:verify_route(page,route,theme,group not in groups);RESULTS.append({'name':theme+'-'+route['id'],'status':'pass','group':group})
                        except Exception as e:
                            traceback.print_exc();page.locator('#phone').screenshot(path=str(native.OUT/(theme+'-'+route['id']+'-FAIL.png')),animations='disabled');RESULTS.append({'name':theme+'-'+route['id'],'status':'fail','error':str(e),'group':group})
                        groups.add(group)
                    for name,fn in [('guarded-state',guarded_state),('system-footer',system_footer)]:
                        try:fn(page,theme);RESULTS.append({'name':theme+'-'+name,'status':'pass'})
                        except Exception as e:traceback.print_exc();RESULTS.append({'name':theme+'-'+name,'status':'fail','error':str(e)})
            browser.close()
    except Exception as e:traceback.print_exc();RESULTS.append({'name':'harness','status':'fail','error':str(e)})
    for name,items in [('no-page-errors',native.ERRORS),('no-outbound',native.OUTBOUND)]:RESULTS.append({'name':name,'status':'fail' if items else 'pass','details':items})
    report={'source_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True,cwd=native.ROOT).strip(),'browser':version,'viewport':'393x852','checks':RESULTS,'passed':sum(x['status']=='pass' for x in RESULTS),'failed':sum(x['status']=='fail' for x in RESULTS),'not_tested':['physical devices','screen readers','mobile keyboard','external services']}
    (native.OUT/'full-migration-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False));return bool(report['failed'])
if __name__=='__main__':raise SystemExit(main())
