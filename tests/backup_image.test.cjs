'use strict';
// Unit-only async control-flow fixture. Native image decoding is separately
// verified by storage_origin_test.py; these mocks do not prove browser support.
const test=require('node:test'),assert=require('node:assert/strict');
const vm=require('node:vm'),fs=require('node:fs'),path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../src/js/suite.js'),'utf8');
const handler=source.slice(source.indexOf('async function validateBackupPhoto('),source.indexOf('\nconst assist='));
function deferred(){let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b;});return {promise,resolve,reject};}
function fixture(options={}){
  let change,decodes=0,images=0;const started=deferred(),toasts=[],reviews=[];
  class Image{
    constructor(){images++;this.naturalWidth=options.width??4000;this.naturalHeight=options.height??4000;}
    set src(value){this.source=value;queueMicrotask(()=>options.loadError?this.onerror():this.onload());}
    decode(){decodes++;started.resolve();return options.decode?options.decode(this.source):Promise.resolve();}
  }
  const input={addEventListener(type,fn){change=fn;}};
  const ctx={Image,document:{createElement:()=>input,body:{appendChild(){}}},stack:[{routeId:'SET-10'}],
    restoreSerial:0,pendingRestore:null,validate:x=>x,PhoneModel:{validate:x=>x},
    toast:text=>toasts.push(text),confirm(){reviews.push(ctx.pendingRestore);ctx.stack.push({suiteMode:'restore'});}};
  vm.createContext(ctx);vm.runInContext(handler,ctx);
  const choose=(source='data:image/png;base64,c3ludGhldGlj',raw)=>change({target:{value:'backup.json',files:[{
    size:100,name:'backup.json',text:async()=>raw??JSON.stringify({format:'ai-phone-ui-backup',version:1,core:{photo:{source}},suite:{}})
  }]}});
  return {ctx,choose,started:started.promise,toasts,reviews,decodes:()=>decodes,images:()=>images};
}
test('backup image: empty sample source remains valid without decoder',async()=>{
  const f=fixture();await f.choose('');assert.equal(f.images(),0);assert.equal(f.reviews.length,1);
});
test('backup image: exact 16MP is decoded and original data URL preserved',async()=>{
  const f=fixture();await f.choose('unchanged source');assert.equal(f.decodes(),1);assert.equal(f.reviews[0].core.photo.source,'unchanged source');
});
test('backup image: oversized dimensions reject before full decode or confirmation',async()=>{
  const f=fixture({width:4001});await f.choose();assert.equal(f.decodes(),0);assert.equal(f.reviews.length,0);assert.match(f.toasts[0],/1600 万像素/);assert.equal(f.ctx.pendingRestore,null);
});
test('backup image: load failure rejects without confirmation',async()=>{
  const f=fixture({loadError:true});await f.choose();assert.equal(f.reviews.length,0);assert.match(f.toasts[0],/无法解码/);
});
test('backup image: decode failure rejects even after successful load',async()=>{
  const f=fixture({decode:()=>Promise.reject(Error('decode'))});await f.choose();assert.equal(f.reviews.length,0);assert.match(f.toasts[0],/无法解码/);
});
test('backup image: newer invalid selection supersedes an in-flight decode',async()=>{
  const gate=deferred(),f=fixture({decode:()=>gate.promise});const old=f.choose();await f.started;
  await f.choose('', '{broken');gate.resolve();await old;assert.equal(f.reviews.length,0);assert.equal(f.ctx.pendingRestore,null);
});
test('backup image: leaving origin page while decoding cannot reopen confirmation',async()=>{
  const gate=deferred(),f=fixture({decode:()=>gate.promise});const pending=f.choose();await f.started;
  f.ctx.stack.pop();gate.resolve();await pending;assert.equal(f.reviews.length,0);assert.equal(f.ctx.pendingRestore,null);
});
test('backup image: stale failure cannot clear a newer reviewed snapshot',async()=>{
  const gate=deferred(),f=fixture({decode:()=>gate.promise});const old=f.choose();await f.started;
  await f.choose('');const current=f.ctx.pendingRestore;gate.reject(Error('late decode'));await old;
  assert.equal(f.ctx.pendingRestore,current);assert.equal(f.reviews.length,1);assert.equal(f.toasts.length,0);
});
