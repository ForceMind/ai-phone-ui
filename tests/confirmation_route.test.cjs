const test=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs');
const source=fs.readFileSync('src/js/suite.js','utf8').split('\n').find(l=>l.startsWith('function stackRoute('));const ctx={};vm.createContext(ctx);vm.runInContext(source,ctx);
test('confirmation retains nearest child-page presentation route',()=>assert.equal(ctx.stackRoute([{kind:'suite',routeId:'DAY-05'},{kind:'confirm'}]),'DAY-05'));
test('nested confirmation binds its own underlying page',()=>assert.equal(ctx.stackRoute([{kind:'suite',routeId:'DAY-05'},{kind:'suite',routeId:'AI-08'},{kind:'confirm'}]),'AI-08'));
test('normal suite route remains unchanged',()=>assert.equal(ctx.stackRoute([{kind:'suite',routeId:'SET-01'}]),'SET-01'));
test('native and absent stacks retain existing root fallback',()=>{assert.equal(ctx.stackRoute([]),undefined);assert.equal(ctx.stackRoute(undefined),undefined);assert.equal(ctx.stackRoute([{kind:'suite',routeId:'DAY-05'},{kind:'talk'}]),undefined);});
