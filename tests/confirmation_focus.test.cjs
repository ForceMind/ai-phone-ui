'use strict';
// Unit-only focus lifecycle fixture. Native focus/keyboard results live in the
// independent HTTP-origin suite; these objects do not emulate browser layout.
const test=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs'),path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../src/js/core.js'),'utf8');
const code=source.slice(source.indexOf('// Focus belongs to a particular review'),source.indexOf('function saveNow()'));
function fixture(){
  let focusCount=0,backs=0,hidden=false,inert=false,help=false;
  const ctx={appOpen:true,overlay:'',locked:false,sleeping:false,currentTask:'photo',stack:[{kind:'confirm'}],
    document:{activeElement:null},$:()=>({classList:{contains:()=>help}}),backPage(){backs++;}};
  const button=action=>({dataset:{action},focus(){if(!hidden){ctx.document.activeElement=this;focusCount++;}}});
  const back=button('back'),accept=button('accept');
  const dialog={closest:()=>inert,contains:el=>el===back||el===accept,
    querySelector:selector=>selector.includes('back')?back:accept};
  ctx.topPage=()=>dialog;
  vm.createContext(ctx);vm.runInContext(code,ctx);
  return {ctx,back,accept,dialog,sync:()=>ctx.syncConfirmationFocus(),count:()=>focusCount,backs:()=>backs,
    hidden:value=>hidden=value,inert:value=>inert=value,help:value=>help=value,
    key(key,extra={}){let prevented=false;const handled=ctx.confirmationKey({key,...extra,preventDefault(){prevented=true;}});return {handled,prevented};}};
}
test('confirmation focus: enter safely, preserve Accept during repeated sync',()=>{
 const f=fixture();f.sync();assert.equal(f.ctx.document.activeElement,f.back);f.accept.focus();f.sync();assert.equal(f.ctx.document.activeElement,f.accept);assert.equal(f.count(),2);
});
test('confirmation focus: hidden task retries when it becomes visible',()=>{
 const f=fixture();f.hidden(true);f.sync();assert.equal(f.count(),0);f.hidden(false);f.sync();assert.equal(f.ctx.document.activeElement,f.back);
});
for(const [name,disable,enable] of [
 ['minimized',f=>f.ctx.appOpen=false,f=>f.ctx.appOpen=true],
 ['overlay',f=>f.ctx.overlay='top',f=>f.ctx.overlay=''],
 ['locked',f=>f.ctx.locked=true,f=>f.ctx.locked=false],
 ['sleeping',f=>f.ctx.sleeping=true,f=>f.ctx.sleeping=false],
 ['inert workbench',f=>f.inert(true),f=>f.inert(false)],
 ['help',f=>f.help(true),f=>f.help(false)]
])test('confirmation focus: '+name+' releases ownership, resume focuses Cancel',()=>{
 const f=fixture();f.sync();f.accept.focus();disable(f);f.sync();assert.deepEqual(f.key('Tab'),{handled:false,prevented:false});assert.deepEqual(f.key('Escape'),{handled:false,prevented:false});assert.equal(f.backs(),0);enable(f);f.sync();assert.equal(f.ctx.document.activeElement,f.back);
});
test('confirmation focus: Tab boundaries and outside focus stay within review',()=>{
 const f=fixture();f.sync();assert.deepEqual(f.key('Tab'),{handled:true,prevented:false});
 assert.deepEqual(f.key('Tab',{shiftKey:true}),{handled:true,prevented:true});assert.equal(f.ctx.document.activeElement,f.accept);
 assert.deepEqual(f.key('Tab'),{handled:true,prevented:true});assert.equal(f.ctx.document.activeElement,f.back);
 f.ctx.document.activeElement=null;f.key('Tab',{shiftKey:true});assert.equal(f.ctx.document.activeElement,f.accept);
});
test('confirmation focus: Escape cancels once; Enter and modified keys retain native behavior',()=>{
 const f=fixture();f.sync();assert.deepEqual(f.key('Enter'),{handled:false,prevented:false});assert.deepEqual(f.key('Tab',{ctrlKey:true}),{handled:false,prevented:false});assert.deepEqual(f.key('Escape'),{handled:true,prevented:true});assert.equal(f.backs(),1);
});
test('confirmation focus: return descriptor is serializable and survives session copies',()=>{
 const f=fixture();const el={id:'',dataset:{action:'pulley-action',menu:'2'},closest:()=>({})};
 const descriptor=f.ctx.confirmationReturn(el),page={kind:'confirm',returnFocus:descriptor};
 assert.deepEqual(JSON.parse(JSON.stringify({...page})),{kind:'confirm',returnFocus:{task:'photo',id:'',action:'pulley-action',menu:'2',pulley:true}});
});
test('confirmation focus: ordinary task pages retain their existing keyboard behavior',()=>{
 const f=fixture();f.ctx.stack=[{kind:'suite'}];f.sync();assert.equal(f.count(),0);assert.deepEqual(f.key('Tab'),{handled:false,prevented:false});
});
