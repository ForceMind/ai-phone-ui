"""Browser UI regression. DOM injection is explicit, not a hosted/file origin test.
Success-path persistence uses an in-memory localStorage fixture. Denied storage is
checked separately. No policy changes or external services are used.
"""
from pathlib import Path
from datetime import datetime, timezone
import os, json, traceback
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
HTML=(ROOT/'dist/index.html').read_text()
CATALOG=json.loads((ROOT/'src/data/screens.json').read_text())
OUT=ROOT/'docs/qa'
OUT.mkdir(parents=True,exist_ok=True)
RESULTS=[]
ERRORS=[]
REQUESTS=[]

def check(name,fn):
    print('RUN',name,flush=True)
    try:
        fn()
        RESULTS.append({'name':name,'status':'pass'})
    except Exception as exc:
        RESULTS.append({'name':name,'status':'fail','error':str(exc)[:1200]})
        print('FAIL',name,str(exc)[:180],flush=True)

def ensure(value,message='Assertion failed'):
    if not value: raise AssertionError(message)

def start(browser,width=1440,height=1000,touch=False,storage=True):
    ctx=browser.new_context(viewport={'width':width,'height':height},has_touch=touch,accept_downloads=True)
    page=ctx.new_page()
    page.set_default_timeout(4000)
    page.on('pageerror',lambda e:ERRORS.append(str(e)))
    page.on('request',lambda r: REQUESTS.append(r.url) if r.url.startswith(('http:','https:','ws:','wss:')) else None)
    if storage:
        page.evaluate("""Object.defineProperty(window,'localStorage',{value:{getItem(k){return Object.prototype.hasOwnProperty.call(this,k)?this[k]:null},setItem(k,v){this[k]=String(v)},removeItem(k){delete this[k]}}})""")
    page.set_content(HTML,wait_until='load')
    page.wait_for_function('typeof Suite!=="undefined" && ready')
    return ctx,page

def go(page,id):
    page.evaluate('(id)=>Suite.go(id)',id)
    page.wait_for_timeout(60)

def visible(page,selector):
    return page.locator(selector).filter(visible=True).last

def action(page,name):
    page.wait_for_timeout(430) # past the post-gesture synthetic click suppression window
    visible(page,'[data-action="ui:'+name+'"]').click(timeout=3000)
    page.wait_for_timeout(90)

def field(page,name,value):
    visible(page,'[data-field="'+name+'"]').fill(value,timeout=3000)

def point(page,x,y):
    r=page.locator('#screen').bounding_box()
    return r['x']+x*r['width']/360,r['y']+y*r['height']/672

def drag(page,start,end,reverse=None,touch=False,cancel=False):
    x,y=point(page,*start); ex,ey=point(page,*end)
    if touch:
        client=page.context.new_cdp_session(page)
        client.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':y}]})
        for i in range(1,9):
            client.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x+(ex-x)*i/8,'y':y+(ey-y)*i/8}]})
        if reverse:
            rx,ry=point(page,*reverse)
            for i in range(1,9):client.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':ex+(rx-ex)*i/8,'y':ey+(ry-ey)*i/8}]})
        client.send('Input.dispatchTouchEvent',{'type':'touchCancel' if cancel else 'touchEnd','touchPoints':[]})
        client.detach()
    else:
        page.mouse.move(x,y);page.mouse.down();page.mouse.move(ex,ey,steps=10)
        if reverse: page.mouse.move(*point(page,*reverse),steps=10)
        if cancel:page.evaluate("document.getElementById('screen').dispatchEvent(new PointerEvent('pointercancel',{pointerId:1,bubbles:true}))")
        page.mouse.up()
    page.wait_for_timeout(330)

with sync_playwright() as pw:
    executable=os.environ.get('CHROMIUM_PATH')
    if not executable and Path('/usr/bin/chromium').exists():executable='/usr/bin/chromium'
    opts={'headless':True,'args':['--no-sandbox']}
    if executable:opts['executable_path']=executable
    browser=pw.chromium.launch(**opts)
    ctx,page=start(browser)
    for r in CATALOG:
        def route_check(r=r):
            go(page,r['id'])
            ensure(page.evaluate('Suite.current().id')==r['id'],'Route mismatch '+r['id'])
            ensure(page.locator('#specTitle').inner_text()==r['name'],'Inspector mismatch')
            if r['mode']=='prototype' and r['id'] not in ['IMG-01']:
                ensure('未连接' in page.locator('#specMode').inner_text(),'Missing prototype disclosure')
        check('route:'+r['id'],route_check)
    check('no-default-network',lambda:ensure(not REQUESTS,str(REQUESTS)))
    ctx.close()
    ctx,page=start(browser)
    def photo_edit():
        go(page,'IMG-02');before=page.evaluate('S.photo.versions.length')
        drag(page,(180,102),(180,188))
        ensure(page.evaluate('S.photo.versions.length')==before+1,'Pulley did not create version')
        ensure(page.evaluate('S.photo.versions[0].ops.length')==0,'Original overwritten')
    check('mouse:pulley-applies-warm-copy',photo_edit)
    def pulley_cancel():
        before=page.evaluate('S.photo.versions.length');drag(page,(180,100),(180,195),(180,106));ensure(page.evaluate('S.photo.versions.length')==before)
    check('mouse:pulley-reversal-cancels',pulley_cancel)
    def peek():
        page.evaluate("pushPage({kind:'talk'},false)")
        page.locator('#talkInput').fill('半滑时不丢失')
        before=page.evaluate('JSON.stringify(stack)')
        drag(page,(4,360),(168,360),(12,360))
        ensure(page.evaluate('appOpen'))
        ensure(page.evaluate('JSON.stringify(stack)')==before)
        ensure(page.locator('#talkInput').input_value()=='半滑时不丢失')
    check('mouse:peek-reversal-keeps-stack-and-draft',peek)
    def minimize_resume():
        drag(page,(4,350),(232,350));ensure(not page.evaluate('appOpen'))
        ensure(page.evaluate('Suite.current().id')=='SYS-01')
        page.evaluate("openTask('photo',{noAnimation:true})")
        ensure(page.locator('#talkInput').input_value()=='半滑时不丢失')
    check('mouse:edge-minimize-resume-draft',minimize_resume)
    def versions_back():
        go(page,'IMG-03');ensure(page.evaluate('stack.length')>0)
        drag(page,(75,400),(246,400));ensure(page.evaluate('stack.length')==0);ensure(page.evaluate('appOpen'))
    check('mouse:content-back-not-minimize',versions_back)
    def deep_pulley():
        go(page,'IMG-02');drag(page,(180,95),(180,373));ensure(page.evaluate('pulleyPinned'))
        page.evaluate('resetPulley()')
    check('mouse:deep-pull-pins-menu',deep_pulley)
    def cover_job():
        go(page,'SYS-01');page.evaluate('S.job.status="idle"')
        cover=page.locator('[data-task="cloud"]').bounding_box();r=page.locator('#screen').bounding_box()
        x=(cover['x']-r['x']+cover['width']*.28)*360/r['width'];y=(cover['y']-r['y']+cover['height']*.5)*672/r['height']
        drag(page,(x,y),(x+74,y));ensure(page.evaluate('S.job.status')=='running');ensure(not page.evaluate('appOpen'))
        drag(page,(x,y),(x+74,y));ensure(page.evaluate('S.job.status')=='paused')
    check('mouse:active-cover-controls-same-job',cover_job)
    def top_edge():
        go(page,'IMG-02');drag(page,(180,4),(180,250));ensure(page.evaluate('overlay')=='top')
        drag(page,(180,450),(180,280));ensure(page.evaluate('overlay')=='')
    check('mouse:top-edge-global-controls',top_edge)
    def bottom_edge():
        go(page,'IMG-02');drag(page,(180,669),(180,390));ensure(page.evaluate('overlay')=='caps');page.evaluate('closeOverlay(true)')
    check('mouse:bottom-edge-capability-layer',bottom_edge)
    def child_pulley():
        go(page,'IMG-06');field(page,'generationPrompt','保留人物，背景改成雨夜')
        drag(page,(180,110),(180,194));ensure(page.evaluate('Suite.current().id')=='IMG-07');ensure(page.evaluate('Suite.state().generatedDraft').startswith('保留人物'))
    check('mouse:child-page-pulley-and-draft',child_pulley)
    def nested_job_parent():
        go(page,'CLD-04');drag(page,(60,420),(240,420));ensure(page.evaluate('Suite.current().id')=='CLD-03');ensure('同一个本机整理任务' in page.locator('#stackRoot').inner_text());ensure('这个路由应由' not in page.locator('#stackRoot').inner_text())
    check('flow:nested-job-parent-has-real-state',nested_job_parent)
    def conversational_note():
        go(page,'AI-01');field(page,'prompt','记下：UI 测试中的新想法');action(page,'prompt');ensure('UI 测试中的新想法' in page.evaluate('S.notes'))
        ensure(page.evaluate('Suite.state().remoteState')=='disconnected')
    check('flow:conversation-writes-local-note',conversational_note)
    def form_restore():
        go(page,'DAY-02');field(page,'eventTitle','待完成的评审');go(page,'IMG-02');go(page,'DAY-02');ensure(visible(page,'[data-field="eventTitle"]').input_value()=='待完成的评审')
    check('flow:unsent-form-draft-survives-route-switch',form_restore)
    def event_save():
        action(page,'save-event');ensure(page.evaluate('Suite.state().calendar.at(-1).title')=='待完成的评审')
    check('flow:local-calendar-save',event_save)
    def schedule():
        go(page,'CLD-12');field(page,'scheduleName','每周资料整理');action(page,'save-schedule');ensure(page.evaluate('Suite.state().schedules.at(-1).enabled') is False)
    check('flow:schedule-is-draft-not-running-automation',schedule)
    def confirm_cancel():
        go(page,'DAY-05');field(page,'message','不会发出去的草稿');action(page,'confirm-message');n=page.evaluate('Suite.state().localOutbox.length');drag(page,(80,400),(249,400));ensure(page.evaluate('Suite.state().localOutbox.length')==n)
    check('flow:message-confirm-right-swipe-cancel',confirm_cancel)
    def confirm_once():
        action(page,'confirm-message');n=page.evaluate('Suite.state().localOutbox.length');page.evaluate("Suite.state().messageDraft='后改的文字'")
        drag(page,(270,400),(76,400));ensure(page.evaluate('Suite.state().localOutbox.length')==n+1)
        ensure(page.evaluate('Suite.state().localOutbox.at(-1).text')=='不会发出去的草稿')
        ensure(page.evaluate('Suite.state().localOutbox.at(-1).status')=='local-preview-only')
    check('flow:message-left-accept-freezes-snapshot',confirm_once)
    def memory_delete():
        n=page.evaluate('Suite.state().memories.length');go(page,'ERR-08');action(page,'confirm-delete');drag(page,(260,400),(66,400));ensure(page.evaluate('Suite.state().memories.length')==n-1);go(page,'ERR-08');action(page,'undo-delete');ensure(page.evaluate('Suite.state().memories.length')==n)
    check('flow:selective-delete-and-undo',memory_delete)
    def search():
        go(page,'DAY-14');field(page,'search','IMG-02');ensure('照片' in page.locator('#suiteSearchResults').inner_text())
    check('flow:local-search-updates-results',search)
    def checklist():
        go(page,'DOC-03');action(page,'refresh-checklist');ensure(page.evaluate('Suite.state().checklist.length')>0)
        ck=visible(page,'[data-check-id]');ck.check();ensure(page.evaluate('Suite.state().checklist.some(x=>x.done)'))
    check('flow:checklist-persists-toggle',checklist)
    def export_png():
        go(page,'IMG-04');
        with page.expect_download(timeout=5000) as pending:action(page,'crop-export')
        dl=pending.value;data=Path(dl.path()).read_bytes();ensure(data[:8]==b'\x89PNG\r\n\x1a\n');ensure(len(data)>300)
    check('download:actual-crop-png',export_png)
    def export_backup():
        go(page,'SET-10')
        with page.expect_download(timeout=5000) as pending:action(page,'backup')
        data=json.loads(Path(pending.value.path()).read_text());ensure(data['format']=='ai-phone-ui-backup');ensure(data['suite']['remoteState']=='disconnected');ensure('core' in data)
    check('download:actual-json-backup',export_backup)
    def malformed_backup():
        go(page,'SET-10');before=page.evaluate('S.notes')
        page.locator('#suiteBackupInput').set_input_files({'name':'bad.json','mimeType':'application/json','buffer':b'{broken'})
        page.wait_for_timeout(200);ensure('无法恢复' in page.locator('#toast').inner_text());ensure(page.evaluate('S.notes')==before)
    check('backup:malformed-file-preserves-current-data',malformed_backup)
    def valid_backup_review():
        raw=page.evaluate("JSON.stringify({format:'ai-phone-ui-backup',version:1,core:S,suite:Suite.state()})")
        page.locator('#suiteBackupInput').set_input_files({'name':'backup.json','mimeType':'application/json','buffer':raw.encode()})
        page.wait_for_timeout(200);ensure(page.evaluate('stack.at(-1).suiteMode')=='restore')
        before=page.evaluate('S.notes');drag(page,(70,400),(245,400));ensure(page.evaluate('S.notes')==before)
    check('backup:valid-file-requires-confirmation-and-can-cancel',valid_backup_review)
    def restore_quota_failure():
        go(page,'SET-10')
        before=page.evaluate('({notes:S.notes,nickname:Suite.state().nickname})')
        raw=page.evaluate("(() => {const b=JSON.parse(JSON.stringify({format:'ai-phone-ui-backup',version:1,core:S,suite:Suite.state()}));b.core.notes='quota-test replacement';b.suite.nickname='quota-test nickname';return JSON.stringify(b);})()")
        page.locator('#suiteBackupInput').set_input_files({'name':'quota-test.json','mimeType':'application/json','buffer':raw.encode()})
        page.wait_for_function("stack.at(-1)?.suiteMode==='restore'")
        page.evaluate("window.__savedSetItem=localStorage.setItem;localStorage.setItem=function(k,v){if(k==='ai-phone-ui-state-v1')throw new DOMException('Full','QuotaExceededError');return window.__savedSetItem.call(this,k,v);}")
        try:
            page.evaluate('acceptDialog();acceptDialog();')
            ensure(page.evaluate('S.notes')==before['notes'])
            ensure(page.evaluate('Suite.state().nickname')==before['nickname'])
            ensure(page.evaluate("stack.at(-1)?.suiteMode")=='restore')
            ensure(not page.evaluate('!!stack.at(-1).consumed'))
            ensure(page.evaluate("localStorage.getItem('ai-phone-ui-state-v1')") is None)
            ensure('恢复未完成' in page.locator('#toast').inner_text())
            page.evaluate('backPage()')
            ensure(page.evaluate('S.notes')==before['notes'])
        finally:
            page.evaluate('localStorage.setItem=window.__savedSetItem;delete window.__savedSetItem')
    check('backup:quota-failure-preserves-data-and-retryable-confirmation',restore_quota_failure)
    def no_nav():
        ensure(not page.locator('.nav-bar,.assistant-dock,.nav-region').count());ensure(not page.locator('#suiteAssist').is_visible())
    check('design:no-default-bottom-nav-or-assistant-dock',no_nav)
    def theme():
        go(page,'SET-02');page.evaluate("action('theme-dusk')");ensure(page.evaluate('S.theme')=='dusk');ensure(page.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--accent').trim()")=='#ffcfb1')
    check('design:ambience-propagates',theme)
    def states():
        go(page,'AI-01')
        for state in ['empty','loading','error','offline']:
            page.evaluate('(s)=>Suite.showState(s)',state);ensure(page.locator('#suiteStateOverlay').is_visible());ensure(page.locator('#suiteStateOverlay').locator('button').count()>0)
        page.evaluate("Suite.showState('default')");ensure(page.locator('#suiteStateOverlay').count()==0)
    check('design:four-state-inspector-recovery-controls',states)
    def keyboard():
        go(page,'AI-01');field(page,'prompt','文字 h 不切回');visible(page,'[data-field="prompt"]').press('h');ensure(page.evaluate('appOpen'));page.locator('#screen').click(position={'x':220,'y':40});page.keyboard.press('h');ensure(not page.evaluate('appOpen'))
    check('keyboard:typing-does-not-trigger-shortcuts',keyboard)
    def storage_roundtrip():
        snapshot=page.evaluate('JSON.stringify(Suite.state())');checked=page.evaluate('(s)=>PhoneModel.validate(JSON.parse(s))',snapshot);ensure(checked['remoteState']=='disconnected');ensure(len(checked['calendar'])>0)
    check('state:validated-backup-roundtrip-in-memory',storage_roundtrip)
    ctx.close()
    ctx,page=start(browser,width=390,height=844,touch=True)
    def mobile_catalog():
        page.locator('[data-action="ui:catalog"]').click();ensure(page.locator('#catalogModal').is_visible());page.locator('#mobileCatalogSearch').fill('SET-11');page.locator('#mobileCatalogNav [data-screen-id="SET-11"]').click();ensure(page.evaluate('Suite.current().id')=='SET-11');ensure(not page.locator('#catalogModal').is_visible())
    check('mobile:catalog-accessible',mobile_catalog)
    def mobile_fit():
        r=page.locator('#phone').bounding_box();ensure(r['x']>=0 and r['x']+r['width']<=391);ensure(r['y']>=0 and r['y']+r['height']<=845)
    check('mobile:device-fits-390x844',mobile_fit)
    def touch_peek():
        go(page,'IMG-02');drag(page,(4,330),(175,330),(8,330),touch=True);ensure(page.evaluate('appOpen'))
    check('touch:peek-reversal',touch_peek)
    def touch_minimize():
        drag(page,(4,340),(220,340),touch=True);ensure(not page.evaluate('appOpen'))
    check('touch:edge-minimize',touch_minimize)
    def touch_pulley():
        go(page,'IMG-02');n=page.evaluate('S.photo.versions.length');drag(page,(180,100),(180,185),touch=True);ensure(page.evaluate('S.photo.versions.length')==n+1)
    check('touch:pulley-select-and-release',touch_pulley)
    def touch_cancel():
        go(page,'IMG-02');drag(page,(4,340),(200,340),touch=True,cancel=True);ensure(page.evaluate('appOpen'))
    check('touch:pointercancel-never-commits',touch_cancel)
    def scroll_vs_pulley():
        go(page,'SET-01');p=page.locator('#surfaceContent .suite-scroll');p.evaluate('(e)=>e.scrollTop=100');drag(page,(160,390),(160,480),touch=True);ensure(not page.evaluate('pulleyPinned'));ensure(page.evaluate('Suite.current().id')=='SET-01')
    check('touch:scrolled-content-not-pulley',scroll_vs_pulley)
    ctx.close()
    ctx,page=start(browser,storage=False)
    def denied_storage():
        go(page,'DOC-02');page.locator('#noteEditor').fill('临时使用仍可编辑');page.wait_for_timeout(330);ensure(page.locator('#storageError').is_visible());ensure(page.evaluate('S.notes')=='临时使用仍可编辑')
    check('storage:denied-fallback-editable-and-warning',denied_storage)
    ctx.close()
    check('no-page-errors',lambda:ensure(not ERRORS,str(ERRORS)))
    check('no-outbound-http-requests',lambda:ensure(not REQUESTS,str(REQUESTS)))
    browser.close()
report={'timestamp':datetime.now(timezone.utc).isoformat(),'harness':'Chromium set_content; in-memory localStorage fixture; separate denied-storage run; CDP touch simulation','not_tested':['real device','file-origin persistence','HTTPS deployed origin','real microphone/camera','backend/Android/model','live GitHub Actions'], 'total':len(RESULTS),'passed':sum(x['status']=='pass' for x in RESULTS),'failed':sum(x['status']=='fail' for x in RESULTS),'page_errors':ERRORS,'network_requests':REQUESTS,'checks':RESULTS}
(OUT/'browser-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:report[k] for k in ['total','passed','failed','page_errors']},ensure_ascii=False,indent=2))
raise SystemExit(1 if report['failed'] else 0)
