const test=require('node:test');const assert=require('node:assert/strict');const fs=require('node:fs');const vm=require('node:vm');
function harness(search=''){
 const elements={};for(const id of ['designVersion','designTheme','designOpaque','designScope'])elements[id]={value:id==='designVersion'?'baseline':'light',checked:false,disabled:false,handlers:{},addEventListener(t,f){this.handlers[t]=f;}};
 const panel={className:'',setAttribute(){},querySelector(s){return elements[s.slice(1)];}};
 const root={dataset:{}},events={},pending=[];let mounts=0,current='SYS-01';
 const context={URLSearchParams,queueMicrotask:f=>pending.push(f),location:{search},document:{documentElement:root,createElement(){mounts++;return panel;},querySelector(){return {after(){}};}},Suite:{current(){return{id:current};}},window:{addEventListener(t,f){events[t]=f;}}};
 vm.runInNewContext(fs.readFileSync('src/js/design-preview.js','utf8'),context);
 const change=(id,value)=>{const e=elements[id];if(typeof value==='boolean')e.checked=value;else e.value=value;e.handlers.change({target:e});};
 return{root,elements,events,change,mounts,pending,setCurrent:id=>{current=id;},flush:()=>{while(pending.length)pending.shift()();}};
}
test('V4 presentation is opt-in; baseline remains default',()=>{const h=harness();assert.equal(h.root.dataset.design,'baseline');assert.equal(h.elements.designTheme.disabled,true);});
test('V4 theme and opaque controls do not require any business-state or storage API',()=>{const h=harness('?design=v4');h.change('designTheme','dark');h.change('designOpaque',true);assert.equal(h.root.dataset.designTheme,'dark');assert.equal(h.root.dataset.designOpaque,'true');assert.equal(h.root.dataset.designSample,'true');assert.equal(h.mounts,1);});
test('route changes leave non-sample pages clearly outside V4',()=>{const h=harness('?design=v4');h.events['design:route']({detail:{id:'DOC-02'}});assert.equal(h.root.dataset.designSample,'false');assert.match(h.elements.designScope.textContent,/保留 V3/);h.events['design:route']({detail:{id:'DAY-05'}});assert.equal(h.root.dataset.designSample,'true');});
test('rollback removes sample styling without navigation or state reset',()=>{const h=harness('?design=v4');for(let i=0;i<30;i++)h.change('designTheme',i%2?'light':'dark');h.change('designVersion','baseline');assert.equal(h.root.dataset.designSample,'false');assert.equal(h.root.dataset.design,'baseline');assert.equal(h.mounts,1);});

test('D1 single-file payload stays within the declared 300000-byte budget',()=>{assert.ok(fs.statSync('dist/index.html').size<=300000);});

test('visibility sync coalesces and follows the final visible surface',()=>{const h=harness('?design=v4');h.setCurrent('DOC-02');h.events['ui:visibility']();h.events['ui:visibility']();assert.equal(h.pending.length,1);h.flush();assert.equal(h.root.dataset.designSample,'false');h.setCurrent('SYS-01');h.events['ui:visibility']();h.flush();assert.equal(h.root.dataset.designSample,'true');});
