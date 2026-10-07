"""Capture the real rendered default first screen for every catalog route.
Uses the same explicit DOM + in-memory storage fixture as browser tests. No external
assets, real user data or authenticated services are accessed.
"""
from pathlib import Path
import json, base64, html, os
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
SCREENS=ROOT/'docs/qa/screens'
SCREENS.mkdir(parents=True,exist_ok=True)
catalog=json.loads((ROOT/'src/data/screens.json').read_text())
source=(ROOT/'dist/index.html').read_text()
with sync_playwright() as pw:
    exe=os.environ.get('CHROMIUM_PATH') or ('/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else None)
    opts={'headless':True,'args':['--no-sandbox']}
    if exe:opts['executable_path']=exe
    b=pw.chromium.launch(**opts)
    p=b.new_page(viewport={'width':1440,'height':1000},device_scale_factor=1)
    p.evaluate("Object.defineProperty(window,'localStorage',{value:{getItem(k){return this[k]??null},setItem(k,v){this[k]=String(v)},removeItem(k){delete this[k]}}})")
    p.set_content(source,wait_until='load')
    p.wait_for_function('typeof Suite!=="undefined" && ready')
    p.evaluate("S.reduce=true;theme()")
    p.screenshot(path=str(ROOT/'docs/qa/workbench.png'))
    for r in catalog:
        p.evaluate('(id)=>Suite.go(id)',r['id'])
        p.wait_for_timeout(55)
        p.evaluate("document.getElementById('toast').classList.remove('show')")
        p.locator('#screen').screenshot(path=str(SCREENS/(r['id']+'.jpg')),type='jpeg',quality=82,animations='disabled')
    b.close()

cards=[]
for r in catalog:
    uri='data:image/jpeg;base64,'+base64.b64encode((SCREENS/(r['id']+'.jpg')).read_bytes()).decode()
    cards.append('<article data-key="'+html.escape(r['id']+' '+r['name']+' '+r['group'])+'"><div class="meta"><span>'+html.escape(r['id'])+'</span><small>'+html.escape(r['group'])+'</small></div><button class="shot" onclick="zoom(this)"><img loading="lazy" src="'+uri+'" alt="'+html.escape(r['name'])+'"></button><h2>'+html.escape(r['name'])+'</h2><p>'+html.escape(r['purpose'])+'</p><small class="mode">'+('本机交互' if r['mode']=='local' else '服务未连接 · UI预览')+'</small></article>')
style='''*{box-sizing:border-box}body{margin:0;background:#102026;color:#e1eff0;font-family:system-ui,"Microsoft YaHei",sans-serif}header{padding:48px 5vw 22px;border-bottom:1px solid #31434a}h1{font-size:36px;font-weight:300;margin:0 0 18px;letter-spacing:2px}header p{max-width:840px;line-height:1.9;color:#b3c8cd;font-size:14px}input{width:min(460px,100%);background:#17313a;border:1px solid #45656d;color:white;padding:14px 18px;font-size:15px;margin-top:14px}nav{font-size:12px;color:#98bfc6;margin-top:16px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(216px,1fr));gap:28px;padding:32px 5vw}article{max-width:370px;margin:auto;width:100%;min-width:0}.meta{display:flex;justify-content:space-between;font-size:12px;letter-spacing:1px;color:#acd7dc;padding:10px 0}.meta small{font-size:11px}button.shot{padding:0;border:1px solid #456069;background:#0c1a20;width:100%;cursor:zoom-in;overflow:hidden;border-radius:13px;display:block}img{display:block;width:100%;height:auto}h2{font-size:17px;font-weight:400;margin:13px 0 7px}article p{font-size:12px;line-height:1.8;color:#94adb6;min-height:43px;margin:0 0 8px}.mode{font-size:10px;border:1px solid #52727a;padding:4px 8px;color:#9ebfc7}dialog{padding:14px;background:#102026;border:1px solid #597880;color:white;max-width:min(90vw,500px)}dialog::backdrop{background:#010b14d9;backdrop-filter:blur(6px)}dialog img{max-height:83vh;width:auto;max-width:100%;margin:auto}dialog button{position:absolute;right:16px;top:16px;color:white;background:#102026;border:1px solid #84a8b7;font-size:23px;padding:3px 10px;cursor:pointer}footer{padding:25px 5vw;font-size:12px;color:#9db9c1}article[hidden]{display:none}@media(max-width:520px){main{grid-template-columns:1fr 1fr;gap:16px;padding:20px 4vw}h1{font-size:28px}h2{font-size:14px}.meta{font-size:10px}.meta small{font-size:9px}article p{font-size:11px}.mode{font-size:9px;padding:3px 4px}}'''
body='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SWIPE / AI · 全界面总览</title><style>'''+style+'''</style></head><body><header><h1>SWIPE / AI — 全界面总览</h1><p>86 个已登记页面的默认首屏截图，全部来自同一可操作原型。这里便于对照与评审；实际手势、滚动、表单和任务状态请在 <b>ai_phone_ui_workbench.html</b> 或源码中的 <b>dist/index.html</b> 体验。31 个服务界面仍是未连接预览，不能当成后端已实现。</p><input id="q" type="search" placeholder="搜索页面、编号或分组" aria-label="筛选界面"><nav id="n">显示 86 / 86 个界面 · 点击图片放大</nav></header><main>'''+''.join(cards)+'''</main><footer>v0.1.0 · 默认首屏，不包含全部滚动内容。截图采用本地演示资料，无真实账户数据。</footer><dialog id="d"><button onclick="d.close()" aria-label="关闭">×</button><img id="big" alt="放大的界面"></dialog><script>const d=document.getElementById('d');function zoom(b){document.getElementById('big').src=b.querySelector('img').src;document.getElementById('big').alt=b.querySelector('img').alt;d.showModal()}document.getElementById('q').addEventListener('input',e=>{let n=0;document.querySelectorAll('article').forEach(a=>{a.hidden=!a.dataset.key.toLowerCase().includes(e.target.value.trim().toLowerCase());if(!a.hidden)n++});document.getElementById('n').textContent='显示 '+n+' / 86 个界面 · 点击图片放大'});d.addEventListener('click',e=>{if(e.target===d)d.close()})</script></body></html>'''
(ROOT/'docs/design/UI_ATLAS.html').write_text(body)
print('Captured',len(catalog),'screen first viewports and embedded atlas',len(body.encode()),'bytes')
