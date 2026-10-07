"""Small dependency-free Markdown subset renderer for the project's own documents.
No arbitrary raw HTML is accepted. This is a review export, not a general Markdown parser.
"""
from pathlib import Path
import html, re, json
ROOT=Path(__file__).resolve().parents[1]
files=[ROOT/x for x in ['README.md','AGENTS.md','CHANGELOG.md']]+sorted((ROOT/'docs').rglob('*.md'))
paths={p.resolve():'doc-'+str(i) for i,p in enumerate(files)}
def inline(s,current):
    x=html.escape(s)
    def link(m):
        label,url=m.groups();dest=(current.parent/url.split('#')[0]).resolve()
        if dest in paths:return '<a href="#'+paths[dest]+'">'+label+'</a>'
        if url.startswith(('https://','http://')):return '<a href="'+url+'" target="_blank" rel="noopener noreferrer">'+label+'</a>'
        return '<span>'+label+'</span>'
    x=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',link,x)
    x=re.sub(r'`([^`]+)`',r'<code>\1</code>',x)
    x=re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',x)
    return x

def render(text,current):
    lines=text.splitlines();out=[];i=0;code=[];fenced=False
    while i<len(lines):
        s=lines[i];i+=1
        if s.startswith('```'):
            if fenced:out.append('<pre><code>'+html.escape('\n'.join(code))+'</code></pre>');code=[]
            fenced=not fenced;continue
        if fenced:code.append(s);continue
        if not s.strip():continue
        if s.startswith('|'):
            table=[s]
            while i<len(lines) and lines[i].startswith('|'):table.append(lines[i]);i+=1
            rows=[]
            for j,row in enumerate(table):
                cells=row.strip().strip('|').split('|')
                if all(re.fullmatch(r'[\s:=-]+',c) for c in cells):continue
                tag='th' if j==0 else 'td';rows.append('<tr>'+''.join('<'+tag+'>'+inline(c.strip(),current)+'</'+tag+'>' for c in cells)+'</tr>')
            out.append('<div class="table-scroll"><table>'+''.join(rows)+'</table></div>');continue
        match=re.match(r'^(#{1,6})\s+(.*)',s)
        if match:
            n=min(6,len(match[1])+1);out.append(f'<h{n}>'+inline(match[2],current)+f'</h{n}>');continue
        if s.startswith('> '):out.append('<blockquote>'+inline(s[2:],current)+'</blockquote>');continue
        if re.match(r'^\s*(?:- |\d+\. )',s):out.append('<p class="list-item">'+inline(s,current)+'</p>');continue
        out.append('<p>'+inline(s,current)+'</p>')
    if code:out.append('<pre>'+html.escape('\n'.join(code))+'</pre>')
    return '\n'.join(out)
nav=[];docs=[]
for p in files:
    title=p.read_text().splitlines()[0].lstrip('# ').strip();id=paths[p.resolve()];nav.append('<a href="#'+id+'">'+html.escape(title)+'</a>');docs.append('<article id="'+id+'"><div class="filename">'+html.escape(str(p.relative_to(ROOT)))+'</div>'+render(p.read_text(),p)+'</article>')
css='''*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#f7f8f6;color:#253330;font-family:system-ui,"Microsoft YaHei",sans-serif;line-height:1.85;font-size:15px}header{padding:32px 34px;border-bottom:1px solid #d6dfdb;background:#fff;position:relative}header h1{font-size:26px;margin:0 0 8px;font-weight:500}header p{margin:0;color:#687b75;font-size:13px}aside{position:fixed;top:162px;bottom:0;left:0;width:265px;padding:22px;overflow:auto;background:#eef3ef;border-right:1px solid #dae3dd}aside a{display:block;padding:8px 4px;text-decoration:none;font-size:12px;color:#48665b;border-bottom:1px solid #dce5dd}main{max-width:1120px;margin-left:265px;padding:0 42px 60px}article{padding:38px 0;border-bottom:1px solid #c8d4cc;scroll-margin-top:18px}.filename{font:11px monospace;color:#80968a;letter-spacing:.3px;margin-bottom:15px}h2{font-size:28px;line-height:1.5;font-weight:500;color:#214c3b;margin:8px 0 25px}h3{font-size:21px;font-weight:500;margin-top:30px}h4{font-size:17px;font-weight:600;margin-top:24px}p{margin:9px 0}a{color:#237a68;text-underline-offset:3px}pre{background:#eaf0ea;border:1px solid #dbe4dc;padding:18px;white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px;line-height:1.8}code{font-family:ui-monospace,monospace;font-size:.9em;background:#e6eee8;padding:2px 4px;border-radius:3px}pre code{padding:0;background:none}.table-scroll{overflow:auto;margin:20px 0}table{border-collapse:collapse;width:100%;font-size:13px}td,th{padding:11px 12px;text-align:left;vertical-align:top;border:1px solid #d4dfd6;min-width:80px}th{background:#eaf2ea;font-weight:600}blockquote{border-left:3px solid #bb9272;background:#faf4ea;margin:18px 0;padding:14px 18px;font-size:14px}.list-item{padding-left:14px;color:#3b5148}button{background:#e0ebe0;color:#285a47;border:1px solid #aec6b5;padding:7px 12px;cursor:pointer}#menu{display:none}@media(max-width:880px){header{padding:24px}aside{display:none;position:relative;top:auto;width:100%;max-height:50vh}aside.show{display:block}main{margin-left:0;padding:0 22px 40px}#menu{display:block;margin-top:16px}h2{font-size:23px}body{font-size:14px}}@media print{aside,#menu{display:none}main{margin:0;max-width:none}article{break-before:page}header{border:0}}'''
output='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SWIPE / AI · 项目计划与设计文档</title><style>'+css+'</style></head><body><header><h1>SWIPE / AI · 项目计划与设计文档</h1><p>v0.1.0 · 86页UI工作台 · 基于认可的V3 · 公开源码快照与原始历史包；模型与云端服务未连接</p><button id="menu" onclick="document.querySelector(\'aside\').classList.toggle(\'show\')">文档目录</button></header><aside>'+''.join(nav)+'</aside><main>'+''.join(docs)+'</main></body></html>'
(ROOT/'dist/project-guide.html').write_text(output)
print('Exported',len(files),'documents to dist/project-guide.html')
