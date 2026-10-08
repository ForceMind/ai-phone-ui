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
 'SYS-04':['#topMenu h2','#topMenu .sub','#topMenu .settings-row','#topMenu .settings-row small','#topMenu .menu-footer']}

def open_route(page,route):
    if route=='DAY-05':reading.open_review(page)
    else:reading.go(page,route)
    settle(page)

def contrast(page,name,route):
    samples=[]
    for sample_index,selector in enumerate(SAMPLES[route]):
        locator=page.locator(selector).filter(visible=True)
        native.ensure(locator.count()>0,'Missing contrast sample '+selector)
        # One representative row/body per semantic class, not hidden/clipped rows.
        el=locator.last if route=='DAY-05' else locator.first
        data=el.evaluate('''e=>{const c=getComputedStyle(e);const rects=[];for(const n of e.childNodes){if(n.nodeType===Node.TEXT_NODE&&n.textContent.trim()){const r=document.createRange();r.selectNodeContents(n);rects.push(...r.getClientRects());}}let opacity=1,unsupported=[];if(c.webkitTextFillColor!==c.color||parseFloat(c.webkitTextStrokeWidth)!==0||c.backgroundClip==='text')unsupported.push('nonstandard-glyph-paint');
          for(let a=e;a;a=a.parentElement){const s=getComputedStyle(a);opacity*=Number(s.opacity);if(s.filter!=='none'||s.mixBlendMode!=='normal'||Number(s.opacity)!==1)unsupported.push(a.className+':filter/blend/group-opacity');}
          const screen=document.getElementById('screen').getBoundingClientRect();let clip={left:screen.left,right:screen.right,top:screen.top,bottom:screen.bottom};for(let a=e;a&&a.id!=='screen';a=a.parentElement){const cs=getComputedStyle(a),ar=a.getBoundingClientRect();if(cs.overflowY!=='visible'){clip.top=Math.max(clip.top,ar.top);clip.bottom=Math.min(clip.bottom,ar.bottom);}if(cs.overflowX!=='visible'){clip.left=Math.max(clip.left,ar.left);clip.right=Math.min(clip.right,ar.right);}}let blocked=[];for(const r of rects){const left=Math.max(r.left,clip.left),right=Math.min(r.right,clip.right),top=Math.max(r.top,clip.top),bottom=Math.min(r.bottom,clip.bottom);for(let y=top+1;y<bottom-1;y+=8)for(let x=left+1;x<right-1;x+=8){const hit=document.elementFromPoint(x,y);if(hit!==e&&!e.contains(hit))blocked.push({x,y,tag:hit?.tagName});}}return {blocked,clip,text:e.textContent.slice(0,100),color:c.color,font:parseFloat(c.fontSize),weight:Number(c.fontWeight),opacity,unsupported,
          rects:rects.map(r=>({x:r.x,y:r.y,right:r.right,bottom:r.bottom})),box:JSON.stringify(e.getBoundingClientRect()),scroll:[e.scrollTop,e.scrollLeft]};}''')
        native.ensure(not data['unsupported'],'Unverified glyph/filter/blend/group-opacity '+str(data))
        native.ensure(not data['blocked'],'Occluded contrast sample '+str(data))
        native.ensure(re.fullmatch(r'rgba?\([\d.,% ]+\)',data['color']) is not None,'Unsupported computed color '+data['color'])
        # All descendant styles are saved; only glyph fill/shadow are suppressed.
        el.evaluate('''e=>{for(const n of [e,...e.querySelectorAll('*')]){n.dataset.d4Style=n.getAttribute('style')??'__absent__';n.style.setProperty('-webkit-text-fill-color','transparent','important');n.style.setProperty('text-shadow','none','important');}}''')
        png=page.screenshot(path=str(native.OUT/(name+'-background-'+str(sample_index)+'.png')),animations='disabled')
        after=el.evaluate('e=>({box:JSON.stringify(e.getBoundingClientRect()),scroll:[e.scrollTop,e.scrollLeft]})')
        el.evaluate('''e=>{for(const n of [e,...e.querySelectorAll('*')]){const s=n.dataset.d4Style;if(s==='__absent__')n.removeAttribute('style');else n.setAttribute('style',s);delete n.dataset.d4Style;}}''')
        native.ensure(after['box']==data['box'] and after['scroll']==data['scroll'],'Text masking changed geometry/scroll')
        img=Image.open(io.BytesIO(png)).convert('RGB')
        native.ensure(img.size==(page.viewport_size['width'],page.viewport_size['height']),'Pixel/CSS coordinate scale mismatch')
        values=[float(x) for x in re.findall(r'[\d.]+',data['color'])];native.ensure(len(values) in [3,4] and '%' not in data['color'],'Unsupported color channels');rgb=values[:3];alpha=(values[3] if len(values)>3 else 1)*data['opacity']
        screen=page.locator('#screen').bounding_box();ratios=[];colors=set()
        for r in data['rects']:
            # Conservative rectangle interiors: background variations between glyphs count too.
            for y in range(max(0,math.ceil(r['y']+1),math.ceil(data['clip']['top'])),min(img.height,math.floor(r['bottom']-1),math.floor(data['clip']['bottom']))):
                for x in range(max(0,math.ceil(r['x']+1),math.ceil(data['clip']['left'])),min(img.width,math.floor(r['right']-1),math.floor(data['clip']['right']))):
                    bg=img.getpixel((x,y));colors.add(bg)
        native.ensure(colors,'No visible pixels sampled '+selector)
        for bg in colors:ratios.append(ratio([a*alpha+b*(1-alpha) for a,b in zip(rgb,bg)],bg))
        scale=page.locator('#screen').evaluate('e=>e.getBoundingClientRect().width/e.offsetWidth')
        rendered_font=data['font']*scale
        threshold=3 if rendered_font>=24 or (rendered_font>=18.6667 and data['weight']>=700) else 4.5
        samples.append(dict(selector=selector,minimum_ratio=min(ratios),threshold=threshold,background_colors=len(colors),rendered_font=rendered_font,**data))
    (native.OUT/(name+'-contrast.json')).write_text(json.dumps(samples,ensure_ascii=False,indent=2))
    page.locator('#phone').screenshot(path=str(native.OUT/(name+'-100.png')),animations='disabled')
    native.ensure(all(x['minimum_ratio']>=x['threshold'] for x in samples),'Actual composite contrast failures: '+json.dumps([x for x in samples if x['minimum_ratio']<x['threshold']],ensure_ascii=False))
    return samples

def resize(page,name,route):
    snapshot=page.evaluate('JSON.stringify({core:S,suite:Suite.state(),payload:stack.at(-1)?.payload})')
    # Snapshot first: no cascading/compound doubling. Absolute computed line-heights
    # double with glyphs; normal remains normal. No width/height/transform changes.
    fonts=page.locator('#screen').evaluate('''root=>{const all=[root,...root.querySelectorAll('*')].map(e=>({e,font:parseFloat(getComputedStyle(e).fontSize),line:getComputedStyle(e).lineHeight}));for(const x of all){x.e.style.setProperty('font-size',x.font*2+'px','important');if(x.line!=='normal')x.e.style.setProperty('line-height',parseFloat(x.line)*2+'px','important');}return all.map(x=>({before:x.font,after:parseFloat(getComputedStyle(x.e).fontSize)}));}''')
    native.ensure(all(abs(x['after']-2*x['before'])<.01 for x in fonts),'Computed text size was not exactly 200%')
    settle(page)
    native.ensure(page.evaluate('JSON.stringify({core:S,suite:Suite.state(),payload:stack.at(-1)?.payload})')==snapshot,'Text-only resize changed business state or fixed payload')
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
    targets=box.locator('b,small,.job-phases span,.job-foot,.job-desc')
    native.ensure(targets.count()>0,'No resize targets')
    seen=set();expected=set();measurements=[]
    # Only actual wheel input can establish reachability. scrollIntoView would
    # programmatically scroll overflow:hidden ancestors and create false passes.
    point=box.bounding_box();screen=page.locator('#screen').bounding_box()
    page.mouse.move(point['x']+point['width']/2,min(point['y']+80,screen['y']+screen['height']-80))
    page.mouse.wheel(0,-100000);settle(page)
    for step in range(28):
        current=[]
        for i in range(targets.count()):
            el=targets.nth(i)
            if not el.inner_text().strip():continue
            m=el.evaluate('''e=>{const range=document.createRange();range.selectNodeContents(e);const s=document.getElementById('screen').getBoundingClientRect();let clip={left:s.left,right:s.right,top:s.top,bottom:s.bottom};for(let p=e;p&&p.id!=='screen';p=p.parentElement){const cs=getComputedStyle(p),r=p.getBoundingClientRect();if(cs.overflowY!=='visible'){clip.top=Math.max(clip.top,r.top);clip.bottom=Math.min(clip.bottom,r.bottom);}if(cs.overflowX!=='visible'){clip.left=Math.max(clip.left,r.left);clip.right=Math.min(clip.right,r.right);}}
              const rects=[...range.getClientRects()].filter(r=>r.width>0&&r.height>0);const lines=rects.map((r,index)=>{const fit=r.left>=clip.left-1&&r.right<=clip.right+1&&r.top>=clip.top-1&&r.bottom<=clip.bottom+1;let unobscured=fit;if(fit)for(const x of [r.left+1,(r.left+r.right)/2,r.right-1]){const hit=document.elementFromPoint(x,(r.top+r.bottom)/2);if(hit!==e&&!e.contains(hit))unobscured=false;}return {index,fit,unobscured};});return {text:e.textContent.slice(0,60),lines,scrollWidth:e.scrollWidth,clientWidth:e.clientWidth};}''')
            for line in m['lines']:
                key=str(i)+':'+str(line['index']);expected.add(key)
                if line['fit'] and line['unobscured']:seen.add(key)
            current.append(dict(index=i,**m))
        measurements.append(dict(step=step,targets=current))
        if seen==expected and expected:break
        page.mouse.wheel(0,120);page.wait_for_timeout(60)
    page.locator('#phone').screenshot(path=str(native.OUT/(name+'-200-end.png')),animations='disabled')
    (native.OUT/(name+'-resize.json')).write_text(json.dumps(measurements,ensure_ascii=False,indent=2))
    # Header text must not overlap the independently scrolling reading body.
    header=page.locator('.suite-header' if route=='SET-01' else '#task .app-header').filter(visible=True).last
    header_lines=header.evaluate('''e=>{const s=document.getElementById('screen').getBoundingClientRect(),walker=document.createTreeWalker(e,NodeFilter.SHOW_TEXT);let n,lines=[];while(n=walker.nextNode()){if(!n.textContent.trim())continue;const r=document.createRange();r.selectNodeContents(n);for(const box of r.getClientRects())lines.push({text:n.textContent,left:box.left,right:box.right,fit:box.left>=s.left&&box.right<=s.right});}return lines;}''')
    native.ensure(all(x['fit'] for x in header_lines),'200% header text horizontally clipped: '+str(header_lines))
    geometry={'header':header.bounding_box(),'body':box.bounding_box(),'screen_scroll':page.locator('#screen').evaluate('e=>[e.scrollTop,e.scrollLeft]')}
    native.ensure(geometry['screen_scroll']==[0,0],'Hidden screen was scrolled by the harness')
    native.ensure(geometry['header']['y']+geometry['header']['height']<=geometry['body']['y']+1,'200% header overlaps reading body: '+str(geometry))
    native.ensure(seen==expected and bool(expected),'200% text unreachable by wheel: '+json.dumps({'seen':sorted(seen),'expected':sorted(expected),'last':measurements[-1]},ensure_ascii=False))
    native.assert_original(page)
    return {'fonts_checked':len(fonts),'reading':measurements,'geometry':geometry}

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
