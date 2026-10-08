"""D1 opt-in presentation: native state invariance and exact-head review images."""
import json
import os
import subprocess
import traceback
from playwright.sync_api import sync_playwright
import storage_origin_test as native
import confirmation_reading_test as reading

RESULTS=[]
SAMPLES=['SYS-01','SYS-02','SYS-03','IMG-02','CLD-03','DAY-05','SET-01']
def check(name,fn):
    try:
        fn();RESULTS.append({'name':name,'status':'pass'})
    except Exception as exc:
        traceback.print_exc();RESULTS.append({'name':name,'status':'fail','error':str(exc)})
def state(page):
    return page.evaluate('JSON.stringify({core:JSON.parse(localStorage.getItem("ai-phone-ui-state-v1")||"null"),stack:stack.map(s=>({kind:s.kind,payload:s.payload})),route:Suite.current().id})')
def image(page,name):
    page.locator('#phone').screenshot(path=str(native.OUT/('v4-'+name+'.png')))
    page.screenshot(path=str(native.OUT/('v4-'+name+'-full.png')),full_page=True)
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
    page.wait_for_timeout(100)
    a=page.locator('#phone').bounding_box();b=page.locator('.design-preview-tools').bounding_box()
    native.ensure(a['y']+a['height']<=b['y'],'Review controls overlap mobile phone')
    image(page,'mobile-dark-high-contrast')

def main():
    version=None
    try:
        with native.preview_server() as origin,sync_playwright() as pw:
            options={'headless':True}
            if os.environ.get('CHROMIUM_PATH'):options['executable_path']=os.environ['CHROMIUM_PATH']
            browser=pw.chromium.launch(**options);version=browser.version
            for name,fn in [('state-invariance',invariant),('light-samples',lambda p:samples(p,'light')),('dark-samples',lambda p:samples(p,'dark')),('contrast-and-mobile-controls',contrast)]:
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
    report={'source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=native.ROOT,text=True).strip(),'browser':version,'checks':RESULTS,'passed':sum(r['status']=='pass' for r in RESULTS),'failed':sum(r['status']=='fail' for r in RESULTS),'not_tested':['physical devices','screen readers','mobile keyboard','OS font scaling','60fps qualification']}
    native.OUT.mkdir(exist_ok=True);(native.OUT/'v4-design-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps(report,ensure_ascii=False,indent=2));return bool(report['failed'])
if __name__=='__main__':raise SystemExit(main())
