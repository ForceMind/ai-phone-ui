/* D1 review controls live outside the phone. Presentation only: no storage/state writes. */
(function(){
'use strict';
const samples=['SYS-01','SYS-02','SYS-03','IMG-02','CLD-03','DAY-05','SET-01'];
const root=document.documentElement;
const enabled=new URLSearchParams(location.search).get('design')==='v4';
let theme='light',opaque=false,viewport='baseline',routeId=Suite.current().id;
const panel=document.createElement('section');panel.className='design-preview-tools';panel.setAttribute('aria-label','V4 样板外观检查');
panel.innerHTML='<label>设计版本 <select id="designVersion"><option value="baseline">现有 V3</option><option value="v4">V4 样板</option></select></label><label>外观 <select id="designTheme"><option value="light">浅色</option><option value="dark">深色</option></select></label><label>画板 <select id="designViewport"><option value="baseline">360×672</option><option value="portrait">393×852</option></select></label><label><input type="checkbox" id="designOpaque"> 减少透明度</label><span id="designScope" role="status"></span>';
document.querySelector('.web-head').after(panel);
const version=panel.querySelector('#designVersion');version.value=enabled?'v4':'baseline';
function apply(){
 const active=version.value==='v4',id=routeId,previousViewport=root.dataset.designViewport;
 root.dataset.design=active?'v4':'baseline';root.dataset.designTheme=theme;
 root.dataset.designSample=active&&samples.includes(id)?'true':'false';
 root.dataset.designOpaque=opaque?'true':'false';root.dataset.designRoute=id;root.dataset.designViewport=active?viewport:'baseline';
 if(previousViewport!==root.dataset.designViewport&&typeof fit==='function')fit();
 if(typeof renderPhotoSelection==='function')renderPhotoSelection();
 panel.querySelector('#designViewport').disabled=!active;panel.querySelector('#designTheme').disabled=!active;panel.querySelector('#designOpaque').disabled=!active;
 panel.querySelector('#designScope').textContent=active?(samples.includes(id)?'D1 样板 · 下拉菜单随当前任务验收':'此页保留 V3 · 全量迁移尚未开始'):'现有 V3 回归基线';
}
version.addEventListener('change',apply);
panel.querySelector('#designTheme').addEventListener('change',e=>{theme=e.target.value;apply();});
panel.querySelector('#designOpaque').addEventListener('change',e=>{opaque=e.target.checked;apply();});
panel.querySelector('#designViewport').addEventListener('change',e=>{viewport=e.target.value;apply();});
window.addEventListener('design:route',e=>{routeId=e.detail.id;apply();});
apply();
})();
