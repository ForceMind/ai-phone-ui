"""Isolated presentation persistence: reload, denial, backup restore and rollback."""
import json,os,subprocess,traceback
from pathlib import Path
from playwright.sync_api import sync_playwright
import storage_origin_test as native
import confirmation_reading_test as reading
KEY='ai-phone-ui-presentation-v1'
RESULTS=[]
def configure(page):
    page.locator('#designVersion').select_option('v4')
    page.locator('#designTheme').select_option('dark')
    page.locator('#designViewport').select_option('portrait')
    page.locator('#designOpaque').check()
def remembered(page):
    native.ensure(page.locator('#designVersion').input_value()=='v4','Design was not restored')
    native.ensure(page.locator('#designTheme').input_value()=='dark','Theme was not restored')
    native.ensure(page.locator('#designViewport').input_value()=='portrait','Viewport was not restored')
    native.ensure(page.locator('#designOpaque').is_checked(),'Opacity preference was not restored')
def reload_preferences(page):
    configure(page);native.reload_page(page);remembered(page);native.assert_original(page)
    reading.go(page,'SET-02')
    native.ensure(page.locator('[data-design-preference="dark"]').filter(visible=True).last.get_attribute('aria-pressed')=='true','Product preference selection lost')
    page.locator('#phone').screenshot(path=str(native.OUT/'preferences-reloaded.png'),animations='disabled')
def denied(page):
    page.add_init_script('''(()=>{const set=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){if(k==='ai-phone-ui-presentation-v1')throw new DOMException('blocked','SecurityError');return set.call(this,k,v);};})();''')
    native.reload_page(page);page.set_viewport_size({'width':390,'height':844});configure(page)
    page.locator('#designScope').wait_for(state='visible')
    native.ensure(page.locator('#designScope').is_visible(),'Narrow-screen save failure feedback is hidden')
    page.wait_for_function('document.getElementById("phone").getBoundingClientRect().bottom <= document.querySelector(".design-preview-tools").getBoundingClientRect().top')
    page.screenshot(path=str(native.OUT/'narrow-storage-denial.png'),full_page=True,animations='disabled')
    native.ensure(page.evaluate('document.documentElement.dataset.designTheme')=='dark','Denied storage stopped current presentation')
    native.ensure('保存不可用' in page.locator('#designScope').inner_text(),'Denied save was presented as durable')
    native.ensure(page.evaluate('(k)=>localStorage.getItem(k)',KEY) is None,'Denied preference was persisted')
    native.assert_original(page);native.reload_page(page)
    native.ensure(page.locator('#designVersion').input_value()=='baseline','Denied preference survived reload unexpectedly')
    native.assert_original(page)
def backup_restore(page):
    configure(page);before=page.evaluate('(k)=>localStorage.getItem(k)',KEY)
    reading.go(page,'SET-10');native.review(page,native.fixture('candidate'));native.commit_and_reload(page)
    native.assert_restored(page,native.fixture('candidate'));remembered(page)
    native.ensure(page.evaluate('(k)=>localStorage.getItem(k)',KEY)==before,'Business restore replaced presentation preference')
    with page.expect_download() as downloaded:
        page.locator('[data-action="ui:backup"]').filter(visible=True).last.click()
    backup=json.loads(Path(downloaded.value.path()).read_text())
    native.ensure(KEY not in json.dumps(backup),'Business backup leaked separate presentation key')
def rollback(page):
    configure(page);page.locator('#designVersion').select_option('baseline');native.assert_original(page)
    native.reload_page(page)
    native.ensure(page.locator('#designVersion').input_value()=='baseline','V3 rollback was not remembered')
    native.assert_original(page);page.locator('#designVersion').select_option('v4');remembered(page)
def system_theme(page):
    page.locator('#designVersion').select_option('v4');page.locator('#designTheme').select_option('system')
    before=page.evaluate('(k)=>localStorage.getItem(k)',KEY)
    for mode in ['dark','light']:
        page.emulate_media(color_scheme=mode)
        page.wait_for_function('v=>document.documentElement.dataset.designTheme===v',arg=mode)
    native.ensure(page.evaluate('(k)=>localStorage.getItem(k)',KEY)==before,'OS theme events rewrote preferences')
    native.assert_original(page)
def invalid(page):
    page.evaluate('(k)=>localStorage.setItem(k,JSON.stringify({schema:1,design:"v4",theme:"url(javascript:1)",opaque:true,viewport:"9999"}))',KEY)
    native.reload_page(page);native.ensure(page.locator('#designVersion').input_value()=='baseline','Invalid preference activated');native.assert_original(page)
def main():
    native.OUT=native.OUT/'presentation-preferences';native.OUT.mkdir(parents=True,exist_ok=True);version=None
    try:
        with native.preview_server() as origin,sync_playwright() as pw:
            opts={'headless':True}
            if os.environ.get('CHROMIUM_PATH'):opts['executable_path']=os.environ['CHROMIUM_PATH']
            browser=pw.chromium.launch(**opts);version=browser.version
            for name,fn in [('reload-and-product-controls',reload_preferences),('storage-denial-fallback',denied),('business-restore-isolated',backup_restore),('v3-rollback',rollback),('system-theme',system_theme),('invalid-record',invalid)]:
                try:
                    with native.case(browser,origin) as page:fn(page)
                    RESULTS.append({'name':name,'status':'pass'})
                except Exception as e:traceback.print_exc();RESULTS.append({'name':name,'status':'fail','error':str(e)})
            browser.close()
    except Exception as e:traceback.print_exc();RESULTS.append({'name':'harness','status':'fail','error':str(e)})
    for name,items in [('no-page-errors',native.ERRORS),('no-outbound',native.OUTBOUND)]:RESULTS.append({'name':name,'status':'fail' if items else 'pass','details':items})
    report={'source_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True,cwd=native.ROOT).strip(),'browser':version,'checks':RESULTS,'passed':sum(x['status']=='pass' for x in RESULTS),'failed':sum(x['status']=='fail' for x in RESULTS),'not_tested':['cross-device sync','physical OS appearance changes']}
    (native.OUT/'presentation-preferences-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False));return bool(report['failed'])
if __name__=='__main__':raise SystemExit(main())
