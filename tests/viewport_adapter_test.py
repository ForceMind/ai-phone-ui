"""D1 393x852 layout against unchanged 360x672 logical gesture thresholds."""
import json,os,subprocess,traceback
from playwright.sync_api import sync_playwright
import storage_origin_test as native
import confirmation_reading_test as reading
import design_preview_test as design
from keyboard_focus_test import gesture
RESULTS=[]
def configure(page):
    page.locator('#designVersion').select_option('v4')
    page.locator('#designViewport').select_option('portrait')
    page.wait_for_function('document.getElementById("screen").clientWidth===393 && document.getElementById("screen").clientHeight===852')
    page.locator('#screen').evaluate("el=>{window.__viewportGestures=[];el.addEventListener('pointerup',e=>window.__viewportGestures.push({mode:gesture?.mode,startOverlay:gesture?.startOverlay,dx:gesture?.dx,dy:gesture?.dy,overlay,clientX:e.clientX,clientY:e.clientY}),true)}")
def point(page,x,y):
    r=page.locator('#screen').bounding_box();return r['x']+x*r['width']/360,r['y']+y*r['height']/672
def peek(page):
    reading.go(page,'IMG-02')
    before=page.evaluate('JSON.stringify({photo:S.photo,notes:S.notes,drafts:S.drafts})')
    gesture(page,(5,340),(100,340),(5,340))
    native.ensure(page.evaluate('appOpen'),'Peek reversal minimized the task')
    native.ensure(page.evaluate('JSON.stringify({photo:S.photo,notes:S.notes,drafts:S.drafts})')==before,'Peek changed content')
    gesture(page,(5,340),(210,340))
    native.ensure(not page.evaluate('appOpen'),'Logical minimize threshold no longer works')
    page.locator('[data-task="photo"]').click()
    native.ensure(page.evaluate('appOpen && currentTask==="photo"'),'Task did not resume')
    native.ensure(page.evaluate('JSON.stringify({photo:S.photo,notes:S.notes,drafts:S.drafts})')==before,'Resume changed content')
def spaces(page):
    reading.go(page,'SYS-01')
    gesture(page,(240,80),(100,80))
    native.ensure(page.evaluate('homeIndex')==2,'Horizontal system swipe lost its logical threshold')
    translate=page.locator('#systemTrack').evaluate('el=>new DOMMatrix(getComputedStyle(el).transform).m41')
    native.ensure(abs(translate+786)<1,'System pages do not align to actual 393px width')
    gesture(page,(100,80),(240,80));native.ensure(page.evaluate('homeIndex')==1,'Reverse system navigation failed')
def overlays(page):
    reading.go(page,'IMG-02')
    gesture(page,(180,668),(180,480));native.ensure(page.evaluate('overlay')=='caps','Bottom edge missed after taller viewport')
    gesture(page,(180,200),(180,430))
    native.ensure(page.evaluate('overlay')=='caps' and page.evaluate('window.__viewportGestures.at(-1).mode')=='scroll','Scrollable capability content lost gesture ownership')
    gesture(page,(180,55),(180,280));native.ensure(page.evaluate('overlay')=='','Bottom header close failed: '+json.dumps(page.evaluate('window.__viewportGestures')))
    gesture(page,(180,4),(180,210));native.ensure(page.evaluate('overlay')=='top','Top edge missed after taller viewport')
    gesture(page,(180,300),(180,120));native.ensure(page.evaluate('overlay')=='','Top layer failed to close')
def interrupt(page,target=None):
    reading.open_review(page);before=page.evaluate('JSON.stringify(stack.at(-1).payload)')
    page.mouse.move(*point(page,240,420));page.mouse.down();page.mouse.move(*point(page,80,420),steps=12)
    page.set_viewport_size(target or {'width':1100,'height':820})
    page.wait_for_function('gesture===null')
    page.mouse.up()
    native.ensure(page.evaluate('Suite.state().localOutbox.length')==0,'Resize accepted a pending gesture')
    native.ensure(page.evaluate('JSON.stringify(stack.at(-1).payload)')==before,'Resize changed fixed review')
    page.keyboard.press('Escape');reading.cancelled(page)
def interrupt_translation(page):
    page.set_viewport_size({'width':1700,'height':1500})
    page.wait_for_function('(()=>{const r=document.getElementById("deviceArea").getBoundingClientRect();return fit.layoutKey===[r.left,r.top,r.width,r.height].join(":")})()')
    before=page.evaluate('scale')
    interrupt(page,{'width':1800,'height':1500})
    native.ensure(abs(page.evaluate('scale')-before)<1e-9,'This case must isolate translation without scale changes')

def snapshots(page,theme):
    design.samples(page,theme)
def main():
    native.OUT=native.OUT/'viewport'
    version=None
    try:
        with native.preview_server() as origin,sync_playwright() as pw:
            options={'headless':True}
            if os.environ.get('CHROMIUM_PATH'):options['executable_path']=os.environ['CHROMIUM_PATH']
            browser=pw.chromium.launch(**options);version=browser.version
            cases=[('peek-and-resume',peek),('three-spaces',spaces),('top-bottom-overlays',overlays),('confirmation-gestures',reading.gesture_reading),('confirmation-resume-once',reading.resume_accept),('resize-cancels-pending-acceptance',interrupt),('translation-cancels-pending-acceptance',interrupt_translation),('photo-ring-reprojection',design.photo_geometry),('light-portrait',lambda p:snapshots(p,'light')),('dark-portrait',lambda p:snapshots(p,'dark'))]
            for name,fn in cases:
                visual=native.fixture('portrait',source='') if name.endswith('-portrait') else None
                try:
                    with native.case(browser,origin,original=visual) as page:
                        configure(page);fn(page)
                    RESULTS.append({'name':name,'status':'pass'})
                except Exception as exc:
                    traceback.print_exc();RESULTS.append({'name':name,'status':'fail','error':str(exc)})
            browser.close()
    except Exception as exc:
        traceback.print_exc();RESULTS.append({'name':'harness','status':'fail','error':str(exc)})
    for name,items in [('no-page-errors',native.ERRORS),('no-outbound',native.OUTBOUND)]:RESULTS.append({'name':name,'status':'fail' if items else 'pass','details':items})
    report={'source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=native.ROOT,text=True).strip(),'browser':version,'checks':RESULTS,'reading_trace':reading.TRACE,'passed':sum(r['status']=='pass' for r in RESULTS),'failed':sum(r['status']=='fail' for r in RESULTS),'not_tested':['physical devices','screen readers','mobile soft keyboard','OS font scaling']}
    native.OUT.mkdir(exist_ok=True);(native.OUT/'viewport-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2));return bool(report['failed'])
if __name__=='__main__':raise SystemExit(main())
