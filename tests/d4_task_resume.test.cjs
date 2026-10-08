const test=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs');
const source=fs.readFileSync('src/js/core.js','utf8').split('\n').find(l=>l.startsWith('function captureSession('));
function capture(offset){const ctx={photoPickerOrigin:null,appOpen:true,currentTask:'cloud',stack:[],sessions:{},S:{drafts:{}},$:id=>id==='stackRoot'?{lastElementChild:null}:id==='surfaceContent'?{querySelector:()=>offset===null?null:{scrollTop:offset}}:null};vm.createContext(ctx);vm.runInContext(source,ctx);ctx.captureSession();return ctx.sessions.cloud;}
test('D4 cloud root reading offset uses the existing task session',()=>assert.equal(capture(237).jobScroll,237));
test('D4 tasks without a root job region record a zero default',()=>assert.equal(capture(null).jobScroll,0));
