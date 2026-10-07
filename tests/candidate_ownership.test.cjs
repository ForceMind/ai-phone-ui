'use strict';
// Production handlers in a VM. Native selection/navigation is tested separately.
const test=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs');
const core=fs.readFileSync(require.resolve('../src/js/core.js'),'utf8');
const suite=fs.readFileSync(require.resolve('../src/js/suite.js'),'utf8');
function fixture(){
  const imports=[],writes=[];let reloads=0;
  const ctx={stack:[],photoPickerOrigin:null,appOpen:true,currentTask:'photo',saveTimer:1,
    S:{drafts:{},notes:'old notes'},D:{nickname:'old phone'},NAMES:{photo:'photo'},
    $:()=>null,confirmationReturn:()=>({task:'photo'}),pushPage:p=>ctx.stack.push(p),
    openTask:t=>{ctx.currentTask=t;ctx.appOpen=true;},importImage:f=>imports.push(f),
    renderStack(){},restoreConfirmationFocus(){},stopVoice(){},save(){},report(){},
    toast(){},clearTimeout(){},location:{reload(){reloads++;}},
    PhoneStorage:{replace(a,b){if(ctx.fail)throw Error('quota');writes.push([a,b]);}},
    uiStorageWarned:false,original:{}};
  vm.createContext(ctx);
  for(const name of ['fileChosen','acceptDialog','backPage'])vm.runInContext(core.split('\n').find(l=>l.startsWith('function '+name+'(')),ctx);
  ctx.original.acceptDialog=ctx.acceptDialog;
  vm.runInContext(suite.slice(suite.indexOf('acceptDialog=function(){'),suite.indexOf('\nfunction fields(){')),ctx);
  return {ctx,imports,writes,reloads:()=>reloads,choose:f=>ctx.fileChosen(f),accept:()=>ctx.acceptDialog(),cancel:()=>ctx.backPage()};
}
function backup(label){return {core:{notes:label,job:{status:'running'},focus:{running:true}},suite:{nickname:label}};}
function review(value){return {kind:'confirm',mode:'suite',suiteMode:'restore',candidate:{value}};}
test('candidate ownership: selection binds its File without importing',()=>{
 const f=fixture(),file={name:'A.png'};f.choose(file);
 assert.equal(f.ctx.stack[0].candidate.value,file);assert.equal(f.imports.length,0);
});
test('candidate ownership: older photo consumes only its file through a shallow session copy',()=>{
 const f=fixture(),a={name:'A.png'},b={name:'B.png'};f.choose(a);const older={...f.ctx.stack[0]};f.choose(b);const newer=f.ctx.stack.at(-1);
 f.ctx.stack=[older];f.accept();assert.deepEqual(f.imports,[a]);assert.equal(newer.candidate.value,b);
 assert.equal(older.candidate.value,null);
});
test('candidate ownership: cancelled photo revokes saved aliases but not another review',()=>{
 const f=fixture(),a={name:'A.png'},b={name:'B.png'};f.choose(a);const alias={...f.ctx.stack[0]};f.choose(b);const newer=f.ctx.stack.at(-1);
 f.ctx.stack=[alias];f.cancel();assert.equal(alias.candidate.value,null);assert.equal(newer.candidate.value,b);
 f.ctx.stack=[{...alias}];f.accept();assert.equal(f.imports.length,0);
 f.ctx.stack=[newer];f.accept();assert.deepEqual(f.imports,[b]);
});
test('candidate ownership: successful photo acceptance cannot replay a stale alias',()=>{
 const f=fixture();f.choose({name:'A.png'});const alias={...f.ctx.stack[0]};f.accept();f.ctx.stack=[alias];f.accept();assert.equal(f.imports.length,1);
});
test('candidate ownership: a missing photo candidate never consumes another global file',()=>{
 const f=fixture();f.ctx.pendingFile={name:'unreviewed.png'};f.ctx.stack=[{kind:'confirm',mode:'import'}];f.accept();assert.equal(f.imports.length,0);
});
test('candidate ownership: failed restore keeps its own shared candidate for retry after switching',()=>{
 const f=fixture(),a=backup('A'),b=backup('B'),older=review(a),newer=review(b);f.ctx.stack=[older];f.ctx.fail=true;f.accept();
 assert.equal(older.candidate.value,a);assert.equal(f.ctx.S.notes,'old notes');assert.equal(f.writes.length,0);
 f.ctx.stack=[newer];f.ctx.stack=[{...older}];f.ctx.fail=false;f.accept();
 assert.equal(f.ctx.S.notes,'A');assert.equal(f.ctx.D.nickname,'A');assert.equal(newer.candidate.value,b);assert.equal(older.candidate.value,null);
 assert.equal(a.core.job.status,'running');assert.equal(f.ctx.S.job.status,'paused');assert.equal(f.reloads(),1);
});
test('candidate ownership: successful restore revokes stale shallow aliases',()=>{
 const f=fixture(),older=review(backup('A')),alias={...older};f.ctx.stack=[older];f.accept();f.ctx.stack=[alias];f.accept();
 assert.equal(f.writes.length,1);assert.equal(f.reloads(),1);
});
test('candidate ownership: cancelled restore releases only its own snapshot',()=>{
 const f=fixture(),older=review(backup('A')),alias={...older},newer=review(backup('B'));f.ctx.stack=[older];f.cancel();
 assert.equal(alias.candidate.value,null);f.ctx.stack=[alias];f.accept();assert.equal(f.writes.length,0);
 f.ctx.stack=[newer];f.accept();assert.equal(f.ctx.S.notes,'B');assert.equal(f.ctx.D.nickname,'B');assert.equal(f.writes.length,1);
});
