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
for(const dims of [[1600,900],[900,1600]])test('photo ring preserves coordinates across portrait viewport for '+dims.join('x'),()=>{const f=fixture(660,.61);f.stage.clientWidth=393;f.stage.getBoundingClientRect=()=>({left:40,top:90,width:393*.61,height:660*.8});f.ctx.baseCanvas.width=dims[0];f.ctx.baseCanvas.height=dims[1];f.ctx.selectPhoto({clientX:40+393*.61/2,clientY:90+660*.8/2});assert.ok(Math.abs(f.ctx.S.photo.selection.x-.5)<1e-9);assert.ok(Math.abs(f.ctx.S.photo.selection.y-.5)<1e-9);});
test('hidden photo surface cannot write a non-finite selection',()=>{const f=fixture(480);f.stage.getBoundingClientRect=()=>({left:40,top:90,width:0,height:0});f.click(100,100);assert.equal(f.ctx.S.photo.selection,null);});
