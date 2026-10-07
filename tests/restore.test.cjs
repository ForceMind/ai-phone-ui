'use strict';
// Production handler in an isolated VM; synthetic storage, no browser/device claim.
const test=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs'),path=require('node:path');
const Storage=require('../src/js/storage.cjs');
const source=fs.readFileSync(path.join(__dirname,'../src/js/suite.js'),'utf8');
const handler=source.slice(source.indexOf('acceptDialog=function(){'),source.indexOf('\nfunction fields(){'));
const back=source.split('\n').find(x=>x.startsWith('backPage=function(){'));
function fixture(){
 const oldCore={notes:'old notes',job:{status:'idle'},focus:{running:false}},oldSuite={nickname:'old nickname'};
 const values=new Map([[Storage.CORE_KEY,JSON.stringify(oldCore)],[Storage.SUITE_KEY,JSON.stringify(oldSuite)]]),writes=[];
 const raw={fail:false,getItem:k=>values.has(k)?values.get(k):null,setItem(k,v){if(raw.fail)throw Error('QuotaExceededError');writes.push(k);values.set(k,v);},removeItem:k=>values.delete(k)};
 const api=Storage.create(raw),warning={hidden:true};let reloads=0,clears=0;
 const dialog={mode:'suite',suiteMode:'restore',consumed:false},pending={core:{notes:'new notes',job:{status:'running'},focus:{running:true}},suite:{nickname:'new nickname'}};
 dialog.candidate={value:pending};
 const ctx={S:oldCore,D:oldSuite,stack:[dialog],PhoneStorage:api,saveTimer:1,clearTimeout(){clears++;},location:{reload(){reloads++;}},$:()=>warning,uiStorageWarned:false,toast(t){ctx.lastToast=t;},renderStack(){},original:{acceptDialog(){},backPage(){ctx.stack.pop();}},rootForTask:new Map(),currentTask:'photo',activeRoute:'CLD-17',emit(){}};
 vm.createContext(ctx);vm.runInContext(handler+'\n'+back,ctx);
 return {ctx,raw,values,writes,api,dialog,pending,oldCore,oldSuite,warning,reloads:()=>reloads,clears:()=>clears,accept:()=>vm.runInContext('acceptDialog()',ctx),cancel:()=>vm.runInContext('backPage()',ctx)};
}
test('restore: quota failure retains memory, both stored values, and confirmation',()=>{const f=fixture();f.raw.fail=true;f.accept();assert.equal(f.ctx.S,f.oldCore);assert.equal(f.ctx.D,f.oldSuite);assert.equal(f.api.getItem(Storage.CORE_KEY),JSON.stringify(f.oldCore));assert.equal(f.api.getItem(Storage.SUITE_KEY),JSON.stringify(f.oldSuite));assert.equal(f.dialog.candidate.value,f.pending);assert.equal(f.ctx.stack[0],f.dialog);assert.equal(f.dialog.consumed,false);assert.equal(f.reloads(),0);assert.equal(f.clears(),0);assert.equal(f.warning.hidden,false);assert.match(f.ctx.lastToast,/恢复未完成/);});
test('restore: retry after storage failure commits once and pauses running work',()=>{const f=fixture();f.raw.fail=true;f.accept();f.raw.fail=false;f.accept();assert.equal(f.writes.length,1);assert.equal(f.writes[0],Storage.SNAPSHOT_KEY);assert.equal(f.reloads(),1);assert.equal(f.clears(),1);assert.equal(f.dialog.candidate.value,null);assert.equal(f.ctx.S.notes,'new notes');assert.equal(f.ctx.S.job.status,'paused');assert.equal(f.ctx.S.focus.running,false);assert.equal(JSON.parse(f.api.getItem(Storage.SUITE_KEY)).nickname,'new nickname');});
test('restore: repeated confirmation after success does not write or reload twice',()=>{const f=fixture();f.accept();f.accept();assert.equal(f.writes.length,1);assert.equal(f.reloads(),1);});
test('restore: cancel after failure keeps old data and does not reload',()=>{const f=fixture();f.raw.fail=true;f.accept();f.cancel();f.accept();assert.equal(f.ctx.stack.length,0);assert.equal(f.ctx.S,f.oldCore);assert.equal(f.ctx.D,f.oldSuite);assert.equal(f.writes.length,0);assert.equal(f.reloads(),0);});
test('restore: serialization failure leaves confirmation retryable',()=>{const f=fixture();f.pending.core.self=f.pending.core;f.accept();assert.equal(f.ctx.S,f.oldCore);assert.equal(f.writes.length,0);assert.equal(f.dialog.consumed,false);assert.equal(f.reloads(),0);});
test('restore: success does not mutate the reviewed input snapshot',()=>{const f=fixture();f.accept();assert.equal(f.pending.core.job.status,'running');assert.equal(f.pending.core.focus.running,true);assert.notEqual(f.ctx.S,f.pending.core);});
test('restore: reload interruption leaves a complete durable pair',()=>{const f=fixture();f.ctx.location.reload=()=>{throw Error('interrupted reload');};assert.throws(f.accept,/interrupted reload/);const restarted=Storage.create(f.raw);assert.equal(JSON.parse(restarted.getItem(Storage.CORE_KEY)).notes,'new notes');assert.equal(JSON.parse(restarted.getItem(Storage.SUITE_KEY)).nickname,'new nickname');});
