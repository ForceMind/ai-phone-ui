'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs');
const core=fs.readFileSync('src/js/core.js','utf8');
function fixture(height,scale=.75){
 const stage={clientWidth:360,clientHeight:height,getBoundingClientRect:()=>({left:40,top:90,width:360*scale,height:height*scale})},ring={hidden:true,style:{}};
 const ctx={W:360,scale,baseCanvas:{width:1050,height:1220},S:{photo:{selection:null}},$:(id)=>id==='photoStage'?stage:id==='selection'?ring:null,renderPhoto(){},save(){},toast(){}};
 vm.createContext(ctx);
 for(const name of ['photoViewport','renderPhotoSelection','selectPhoto']){const line=core.split('\n').find(l=>l.startsWith('function '+name+'('));if(line)vm.runInContext(line,ctx);}
 return {ctx,stage,ring,click:(x,y)=>ctx.selectPhoto({clientX:40+x*scale,clientY:90+y*scale})};
}
for(const height of [424,480])test('photo selection tracks actual '+height+'px content viewport',()=>{const f=fixture(height);f.click(180,height/2);assert.ok(Math.abs(f.ctx.S.photo.selection.x-.5)<1e-9);assert.ok(Math.abs(f.ctx.S.photo.selection.y-.5)<1e-9);});
test('V4 letterbox does not become selectable image content',()=>{const f=fixture(480);f.click(180,15);assert.equal(f.ctx.S.photo.selection,null);});
test('ring reprojects to changed viewport without changing selected image coordinates',()=>{const f=fixture(480);f.ctx.S.photo.selection={x:.5,y:.5,r:.23};assert.equal(typeof f.ctx.renderPhotoSelection,'function');const before=JSON.stringify(f.ctx.S);f.ctx.renderPhotoSelection();assert.match(f.ring.style.cssText,/top:157\.2px/);f.stage.clientHeight=424;f.ctx.renderPhotoSelection();assert.match(f.ring.style.cssText,/top:129\.2px/);assert.equal(JSON.stringify(f.ctx.S),before);});
