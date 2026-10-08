const test=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs');
const source=fs.readFileSync('src/js/core.js','utf8').split('\n').find(l=>l.startsWith('function chooseMode('));
function mode(inside,y,edge=''){const ctx={sleeping:false,locked:false,appOpen:true,stack:[],currentTask:'photo',setHome(){}};vm.createContext(ctx);vm.runInContext(source,ctx);return ctx.chooseMode({dx:150,dy:0,y,edge,scroll:null,startOverlay:'',target:{closest:s=>inside&&s==='#photoStage'?{}:null}});}
test('photo swipe follows the enlarged stage above the old y band',()=>assert.equal(mode(true,100),'photo-version'));
test('non-photo content inside the old y band does not inherit image gestures',()=>assert.equal(mode(false,200),'ignore'));
test('photo content retains the system edge priority',()=>assert.equal(mode(true,200,'left'),'edge-home'));
