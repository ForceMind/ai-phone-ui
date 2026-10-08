"""D1 opt-in presentation: native state invariance and exact-head review images."""
import json
import os
import subprocess
import traceback
from playwright.sync_api import sync_playwright
import storage_origin_test as native
import confirmation_reading_test as reading

RESULTS=[]
FRAME_SAMPLE={}
GEOMETRY_OBSERVATION={}
SAMPLES=['SYS-01','SYS-02','SYS-03','IMG-02','CLD-03','DAY-05','SET-01']
def check(name,fn):
    try:
        fn();RESULTS.append({'name':name,'status':'pass'})
    except Exception as exc:
        traceback.print_exc();RESULTS.append({'name':name,'status':'fail','error':str(exc)})
def state(page):
    return page.evaluate('JSON.stringify({core:JSON.parse(localStorage.getItem("ai-phone-ui-state-v1")||"null"),stack:stack.map(s=>({kind:s.kind,payload:s.payload})),route:Suite.current().id})')
def image(page,name):
    page.locator('#phone').screenshot(path=str(native.OUT/('v4-'+name+'.png')),animations='disabled')
    page.screenshot(path=str(native.OUT/('v4-'+name+'-full.png')),full_page=True,animations='disabled')
def invariant(page):
    reading.open_review(page)
    before=state(page)
    count=page.locator('*').count()
    for i in range(30):
        page.locator('#designTheme').select_option('light' if i%2 else 'dark')
        page.locator('#designOpaque').set_checked(bool(i%2))
    native.ensure(state(page)==before,'Presentation changed business state or fixed confirmation')
    native.ensure(page.locator('*').count()==count,'Repeated controls grow DOM')
    page.locator('#designVersion').select_option('baseline')
    native.ensure(state(page)==before,'Baseline rollback changed business state')
    page.locator('#designVersion').select_option('v4')
    reading.wheel_end(page)
    reading.bounded(reading.observe(page,'v4-long-end'))
    reading.tail_visible(reading.observe(page,'v4-long-tail'))
    reading.control(page,'back').click();reading.cancelled(page)
def samples(page,theme):
    page.locator('#designTheme').select_option(theme)
    for route in SAMPLES:
        reading.go(page,route)
        page.wait_for_function('document.documentElement.dataset.designSample === "true"')
        image(page,theme+'-'+route)
    reading.open_review(page)
    image(page,theme+'-confirmation-start');reading.wheel_end(page)
    image(page,theme+'-confirmation-end')
    reading.bounded(reading.observe(page,theme+'-confirmation'))
    reading.control(page,'back').click()
    reading.go(page,'IMG-02')
    page.locator('#screen').click(position={'x':180,'y':30})
    page.keyboard.press('m')
    page.wait_for_function('!document.getElementById("taskSurface").getAnimations().some(a=>a.playState==="running")')
    rows=page.locator('#pulley .pulley-row').all()
    surface_top=page.locator('#taskSurface').bounding_box()['y']
    for row in rows:
        box=row.bounding_box();native.ensure(box['y']+box['height']<=surface_top,'Pinned menu command is covered by task surface')
    image(page,theme+'-pulley')
    page.keyboard.press('Escape')
def contrast(page):
    page.locator('#designTheme').select_option('dark')
    page.emulate_media(contrast='more')
    reading.go(page,'SET-01')
    palette=page.locator('#screen').evaluate("el=>{const s=getComputedStyle(el);return {accent:s.getPropertyValue('--v4-accent').trim(),background:s.getPropertyValue('--v4-bg').trim(),control:s.getPropertyValue('--v4-control-text').trim()}}")
    native.ensure(palette=={'accent':'#004641','background':'#fff','control':'#fff'},'Incomplete high-contrast palette: '+str(palette))
    image(page,'dark-high-contrast')
    page.set_viewport_size({'width':390,'height':844})
    page.wait_for_function('document.getElementById("deviceSlot").getBoundingClientRect().width < 390')
    a=page.locator('#phone').bounding_box();b=page.locator('.design-preview-tools').bounding_box()
    native.ensure(a['y']+a['height']<=b['y'],'Review controls overlap mobile phone')
    image(page,'mobile-dark-high-contrast')

def photo_geometry(page):
    global GEOMETRY_OBSERVATION
    reading.go(page,'IMG-02')
    page.wait_for_function('!document.getElementById("task").getAnimations().some(a=>a.playState==="running")')
    stage=page.locator('#photoStage').bounding_box()
    page.locator('#photoStage').evaluate("el=>el.addEventListener('click',e=>window.__photoClick={x:e.clientX,y:e.clientY},{once:true})")
    page.mouse.click(stage['x']+stage['width']/2,stage['y']+stage['height']/2)
    selection=page.evaluate('JSON.stringify(S.photo.selection)')
    point=json.loads(selection)
    click=page.evaluate('window.__photoClick')
    # The square 1px fixture is contain-fitted: infer geometry independently of production helpers.
    side=min(stage['width'],stage['height']);left=stage['x']+(stage['width']-side)/2;top=stage['y']+(stage['height']-side)/2
    expected={'x':(click['x']-left)/side,'y':(click['y']-top)/side}
    GEOMETRY_OBSERVATION={'stage':stage,'actual_click':click,'expected_image_point':expected,'actual_selection':point}
    native.ensure(abs(click['x']-(stage['x']+stage['width']/2))<=1 and abs(click['y']-(stage['y']+stage['height']/2))<=1,'Browser click did not land within one device CSS pixel of requested center')
    native.ensure(abs(point['x']-expected['x'])<.00001 and abs(point['y']-expected['y'])<.00001,'Selection does not match actual browser click: '+json.dumps(GEOMETRY_OBSERVATION))
    for design in ['baseline','v4']:
        page.locator('#designVersion').select_option(design)
        stage=page.locator('#photoStage').bounding_box();ring=page.locator('#selection').bounding_box()
        native.ensure(abs((ring['x']+ring['width']/2)-(stage['x']+stage['width']/2))<1,'Ring x drift after design switch')
        native.ensure(abs((ring['y']+ring['height']/2)-(stage['y']+stage['height']/2))<1,'Ring y drift after design switch')
        native.ensure(page.evaluate('JSON.stringify(S.photo.selection)')==selection,'Theme rollback changed selected image region')
    colors=page.locator('#toast').evaluate('el=>({color:getComputedStyle(el).color,background:getComputedStyle(el).backgroundColor})')
    native.ensure(colors=={'color':'rgb(255, 255, 255)','background':'rgb(32, 33, 38)'},'Photo status feedback must use the light inverse palette: '+str(colors))
    ring_style=page.locator('#selection').evaluate('el=>({border:getComputedStyle(el).borderTopColor,shadow:getComputedStyle(el).boxShadow})')
    native.ensure(ring_style['border']=='rgb(255, 255, 255)' and 'rgb(17, 17, 17)' in ring_style['shadow'],'Selection needs both light and dark edge contrast')
    image(page,'photo-selection-aligned')
    stage=page.locator('#photoStage').bounding_box()
    page.mouse.click(stage['x']+stage['width']/2,stage['y']+5)
    native.ensure(page.evaluate('JSON.stringify(S.photo.selection)')==selection,'Letterbox became image content')

def photo_drag_region(page):
    reading.go(page,'IMG-02')
    page.wait_for_function('!document.getElementById("task").getAnimations().some(a=>a.playState==="running")')
    stage=page.locator('#photoStage').bounding_box();screen=page.locator('#screen').bounding_box()
    y=(stage['y']+12-screen['y'])*672/screen['height']
    native.ensure(y<148,'This regression must start above the old hard-coded image band')
    reading.gesture(page,(90,y),(270,y))
    native.ensure(page.evaluate('S.photo.current')==0 and page.evaluate('stack.length')==0,'Upper photo region did not select the previous version')
    reading.gesture(page,(270,y),(90,y))
    native.ensure(page.evaluate('S.photo.current')==1 and page.evaluate('stack.length')==0,'Upper photo region opened a page instead of selecting the next version')

def presentation_visibility(page):
    reading.go(page,'ONB-01')
    page.wait_for_function('document.documentElement.dataset.designSample==="false"')
    page.keyboard.press('h')
    page.wait_for_function('!appOpen && document.documentElement.dataset.designSample==="true" && document.documentElement.dataset.designRoute==="SYS-01"')
    page.keyboard.press('t')
    page.wait_for_function('overlay==="top" && document.documentElement.dataset.designSample==="false"')
    page.keyboard.press('Escape')
    page.wait_for_function('overlay==="" && document.documentElement.dataset.designRoute==="SYS-01"')
    page.keyboard.press('a')
    page.wait_for_function('overlay==="caps" && document.documentElement.dataset.designRoute==="SYS-03"')
    page.keyboard.press('Escape')
    page.wait_for_function('overlay==="" && document.documentElement.dataset.designRoute==="SYS-01"')
    native.assert_original(page)

def frame_sample(page):
    global FRAME_SAMPLE
    reading.go(page,'SYS-01')
    FRAME_SAMPLE=page.evaluate("""() => new Promise(resolve=>{
      const intervals=[];const begin=performance.now();let last=begin;
      function frame(now){intervals.push(now-last);last=now;
        if(now-begin<5000){requestAnimationFrame(frame);return;}
        intervals.sort((a,b)=>a-b);
        resolve({duration_ms:now-begin,frames:intervals.length,p50_ms:intervals[Math.floor(intervals.length*.5)],p95_ms:intervals[Math.floor(intervals.length*.95)],over_50ms:intervals.filter(v=>v>50).length,context:'CI Chromium foreground baseline; not a physical-device 60fps certificate'});
      }requestAnimationFrame(frame);
    })""")
    native.ensure(FRAME_SAMPLE['frames']>0,'No visible frame sample')

def main():
    version=None
    try:
        with native.preview_server() as origin,sync_playwright() as pw:
            options={'headless':True}
            if os.environ.get('CHROMIUM_PATH'):options['executable_path']=os.environ['CHROMIUM_PATH']
            browser=pw.chromium.launch(**options);version=browser.version
            for name,fn in [('state-invariance',invariant),('light-samples',lambda p:samples(p,'light')),('dark-samples',lambda p:samples(p,'dark')),('contrast-and-mobile-controls',contrast),('record-frame-baseline',frame_sample),('photo-selection-geometry',photo_geometry),('v4-cross-task-reading-resume',reading.resume_accept),('photo-stage-swipe-region',photo_drag_region),('presentation-follows-visible-surface',presentation_visibility)]:
                visual=native.fixture('visual',source='') if name.endswith('-samples') else None
                if visual:
                    visual['core']['photo']['name']='山径 · 黄昏'
                    visual['core']['notes']='把今天的想法留在这里。\n照片、笔记和进行中的事，都能从刚才的地方继续。'
                    visual['core']['events']=[{'title':'照片已准备好','body':'内置生成风景，本机编辑演示。','task':'photo','at':1791414000000},{'title':'接着写下想法','body':'示例笔记留在本机，可以继续编辑。','task':'notes','at':1791413940000}]
                with native.case(browser,origin,original=visual) as page:
                    page.locator('#designVersion').select_option('v4')
                    check(name,lambda:fn(page))
            browser.close()
    except Exception as exc:
        traceback.print_exc();RESULTS.append({'name':'harness','status':'fail','error':str(exc)})
    for name,items in [('no-page-errors',native.ERRORS),('no-outbound',native.OUTBOUND)]:
        RESULTS.append({'name':name,'status':'fail' if items else 'pass','details':items})
    report={'source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=native.ROOT,text=True).strip(),'browser':version,'frame_sample':FRAME_SAMPLE,'geometry_observation':GEOMETRY_OBSERVATION,'checks':RESULTS,'reading_trace':reading.TRACE,'passed':sum(r['status']=='pass' for r in RESULTS),'failed':sum(r['status']=='fail' for r in RESULTS),'not_tested':['physical devices','screen readers','mobile keyboard','OS font scaling','60fps qualification']}
    native.OUT.mkdir(exist_ok=True);(native.OUT/'v4-design-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps(report,ensure_ascii=False,indent=2));return bool(report['failed'])
if __name__=='__main__':raise SystemExit(main())
