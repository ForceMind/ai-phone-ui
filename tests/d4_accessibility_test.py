"""Bounded D4 real rendered-background contrast and text-only 200% resize.
No OS/font-accessibility certification. Never changes deviceScaleFactor or zoom.
"""
import io,json,math,os,re,subprocess,traceback
from PIL import Image
from playwright.sync_api import sync_playwright
import storage_origin_test as native
import confirmation_reading_test as reading
RESULTS=[]

def check(name,fn):
    try: details=fn();RESULTS.append(dict(name=name,status='pass',details=details))
    except Exception as e: traceback.print_exc();RESULTS.append(dict(name=name,status='fail',error=str(e)))

def configure(page,theme,mode):
    page.locator('#designVersion').select_option('v4')
    page.locator('#designViewport').select_option('portrait')
    page.locator('#designTheme').select_option(theme)
    if mode=='opaque':page.locator('#designOpaque').check()
    if mode=='contrast':
        reading.go(page,'SET-11');page.locator('[data-action="ui:toggle:contrast"]').filter(visible=True).last.click()
    page.wait_for_timeout(100)

def settle(page):page.wait_for_timeout(350)

def luminance(rgb):
    c=[x/255 for x in rgb]
    c=[x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in c]
    return sum(x*w for x,w in zip(c,[.2126,.7152,.0722]))

def ratio(fg,bg):
    a,b=sorted([luminance(fg),luminance(bg)])
    return (b+.05)/(a+.05)

# Target selectors deliberately identify representative text; not an all-page audit.
SAMPLES={
 'DAY-05':['.dialog-inner h2','.dialog-inner p','.dialog-head .accept','.dialog-head [data-action="back"]'],
 'SET-01':['.suite-header h2','.s-row b','.s-row small'],
 'CLD-03':['.app-header h2','.job-desc','.job-phases span','.job-foot'],
 'SYS-04':['#topMenu h2','#topMenu .sub','#topMenu .settings-row','#topMenu .menu-footer']}

def open_route(page,route):
    if route=='DAY-05':reading.open_review(page)
    else:reading.go(page,route)
    settle(page)

def contrast(page,name,route):
    samples=[]
    for selector in SAMPLES[route]:
        locator=page.locator(selector).filter(visible=True)
        native.ensure(locator.count()>0,'Missing contrast sample '+selector)
        # One representative row/body per semantic class, not hidden/clipped rows.
        el=locator.last if route=='DAY-05' else locator.first
        data=el.evaluate('''e=>{const c=getComputedStyle(e),r=document.createRange();r.selectNodeContents(e);let opacity=1,unsupported=[];
          for(let a=e;a;a=a.parentElement){const s=getComputedStyle(a);opacity*=Number(s.opacity);if(s.filter!=='none'||s.mixBlendMode!=='normal')unsupported.push(a.className+':filter/blend');}
          return {text:e.textContent.slice(0,100),color:c.color,font:parseFloat(c.fontSize),weight:Number(c.fontWeight),opacity,unsupported,
          rects:[...r.getClientRects()].map(r=>({x:r.x,y:r.y,right:r.right,bottom:r.bottom})),box:JSON.stringify(e.getBoundingClientRect()),scroll:[e.scrollTop,e.scrollLeft]};}''')
        native.ensure(not data['unsupported'],'Unverified filter/blend '+str(data))
        # All descendant styles are saved; only glyph fill/shadow are suppressed.
        el.evaluate('''e=>{for(const n of [e,...e.querySelectorAll('*')]){n.dataset.d4Style=n.getAttribute('style')??'__absent__';n.style.setProperty('-webkit-text-fill-color','transparent','important');n.style.setProperty('text-shadow','none','important');}}''')
        png=page.screenshot(animations='disabled')
        after=el.evaluate('e=>({box:JSON.stringify(e.getBoundingClientRect()),scroll:[e.scrollTop,e.scrollLeft]})')
        el.evaluate('''e=>{for(const n of [e,...e.querySelectorAll('*')]){const s=n.dataset.d4Style;if(s==='__absent__')n.removeAttribute('style');else n.setAttribute('style',s);delete n.dataset.d4Style;}}''')
        native.ensure(after['box']==data['box'] and after['scroll']==data['scroll'],'Text masking changed geometry/scroll')
        img=Image.open(io.BytesIO(png)).convert('RGB')
        values=[float(x) for x in re.findall(r'[\d.]+',data['color'])];rgb=values[:3];alpha=(values[3] if len(values)>3 else 1)*data['opacity']
        screen=page.locator('#screen').bounding_box();ratios=[];colors=set()
        for r in data['rects']:
            # Conservative rectangle interiors: background variations between glyphs count too.
            for y in range(max(0,math.ceil(r['y']+1),math.ceil(screen['y'])),min(img.height,math.floor(r['bottom']-1),math.floor(screen['y']+screen['height'])),2):
                for x in range(max(0,math.ceil(r['x']+1),math.ceil(screen['x'])),min(img.width,math.floor(r['right']-1),math.floor(screen['x']+screen['width'])),2):
                    bg=img.getpixel((x,y));colors.add(bg)
        native.ensure(colors,'No visible pixels sampled '+selector)
        for bg in colors:ratios.append(ratio([a*alpha+b*(1-alpha) for a,b in zip(rgb,bg)],bg))
        threshold=3 if data['font']>=24 or (data['font']>=18.6667 and data['weight']>=700) else 4.5
        samples.append(dict(selector=selector,minimum_ratio=round(min(ratios),4),threshold=threshold,background_colors=len(colors),**data))
    (native.OUT/(name+'-contrast.json')).write_text(json.dumps(samples,ensure_ascii=False,indent=2))
    page.locator('#phone').screenshot(path=str(native.OUT/(name+'-100.png')),animations='disabled')
    native.ensure(all(x['minimum_ratio']>=x['threshold'] for x in samples),'Actual composite contrast failures: '+json.dumps([x for x in samples if x['minimum_ratio']<x['threshold']],ensure_ascii=False))
    return samples

def resize(page,name,route):
    # Snapshot first: no cascading/compound doubling. Absolute computed line-heights
    # double with glyphs; normal remains normal. No width/height/transform changes.
    fonts=page.locator('#screen').evaluate('''root=>{const all=[root,...root.querySelectorAll('*')].map(e=>({e,font:parseFloat(getComputedStyle(e).fontSize),line:getComputedStyle(e).lineHeight}));for(const x of all){x.e.style.setProperty('font-size',x.font*2+'px','important');if(x.line!=='normal')x.e.style.setProperty('line-height',parseFloat(x.line)*2+'px','important');}return all.map(x=>({before:x.font,after:parseFloat(getComputedStyle(x.e).fontSize)}));}''')
    native.ensure(all(abs(x['after']-2*x['before'])<.01 for x in fonts),'Computed text size was not exactly 200%')
    settle(page)
    page.locator('#phone').screenshot(path=str(native.OUT/(name+'-200-start.png')),animations='disabled')
    if route=='DAY-05':
        start=reading.observe(page,name+':200-start');reading.wheel_end(page);end=reading.observe(page,name+':200-end')
        page.locator('#phone').screenshot(path=str(native.OUT/(name+'-200-end.png')),animations='disabled')
        reading.bounded(start);reading.bounded(end);reading.tail_visible(end)
        for action in ['back','accept']:
            native.ensure(reading.control(page,action).evaluate('e=>{const r=e.getBoundingClientRect();return e.contains(document.elementFromPoint(r.x+r.width/2,r.y+r.height/2));}'),'200% action obscured: '+action)
        reading.control(page,'back').click();reading.cancelled(page)
        return {'fonts_checked':len(fonts),'reading':end}
    selector='.suite-scroll' if route=='SET-01' else '.job-detail'
    box=page.locator(selector).filter(visible=True).last
    targets=box.locator('b,small,span,p,.job-foot,.job-desc')
    measurements=[]
    for i in range(targets.count()):
        el=targets.nth(i)
        if not el.inner_text().strip():continue
        el.scroll_into_view_if_needed();settle(page)
        measurements.append(el.evaluate('''e=>{const r=e.getBoundingClientRect(),s=document.getElementById('screen').getBoundingClientRect();const range=document.createRange();range.selectNodeContents(e);return {text:e.textContent.slice(0,60),horizontalFit:[...range.getClientRects()].every(x=>x.left>=s.left&&x.right<=s.right),verticalFit:r.top>=s.top&&r.bottom<=s.bottom,scrollWidth:e.scrollWidth,clientWidth:e.clientWidth};}'''))
    page.locator('#phone').screenshot(path=str(native.OUT/(name+'-200-end.png')),animations='disabled')
    (native.OUT/(name+'-resize.json')).write_text(json.dumps(measurements,ensure_ascii=False,indent=2))
    native.ensure(measurements,'No resize targets')
    native.ensure(all(x['horizontalFit'] and x['verticalFit'] for x in measurements),'200% unreachable or clipped text: '+json.dumps([x for x in measurements if not x['horizontalFit'] or not x['verticalFit']],ensure_ascii=False))
    native.assert_original(page)
    return {'fonts_checked':len(fonts),'reading':measurements}

def main():
    native.OUT=native.OUT/'d4-accessibility';native.OUT.mkdir(parents=True,exist_ok=True);version=None
    try:
        with native.preview_server() as origin,sync_playwright() as pw:
            opts={'headless':True}
            if os.environ.get('CHROMIUM_PATH'):opts['executable_path']=os.environ['CHROMIUM_PATH']
            browser=pw.chromium.launch(**opts);version=browser.version
            for theme in ['light','dark']:
                for mode in ['glass','opaque','contrast']:
                    for route in SAMPLES:
                        name=theme+'-'+mode+'-'+route
                        with native.case(browser,origin) as page:
                            configure(page,theme,mode);open_route(page,route)
                            check(name+'-contrast',lambda:contrast(page,name,route))
                            if route!='SYS-04':check(name+'-resize',lambda:resize(page,name,route))
            browser.close()
    except Exception as e:traceback.print_exc();RESULTS.append(dict(name='harness',status='fail',error=str(e)))
    for name,items in [('no-page-errors',native.ERRORS),('no-outbound',native.OUTBOUND)]:RESULTS.append(dict(name=name,status='fail' if items else 'pass',details=items))
    report=dict(source_head=subprocess.check_output(['git','rev-parse','HEAD'],text=True,cwd=native.ROOT).strip(),browser=version,checks=RESULTS,passed=sum(x['status']=='pass' for x in RESULTS),failed=sum(x['status']=='fail' for x in RESULTS),not_tested=['physical devices','OS text scaling','screen readers','all 86 routes','native browser zoom','OS contrast/transparency media preferences'])
    (native.OUT/'d4-accessibility-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False));return bool(report['failed'])
if __name__=='__main__':raise SystemExit(main())
