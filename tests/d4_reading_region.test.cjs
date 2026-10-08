const test=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs');
const source=fs.readFileSync('src/js/core.js','utf8').split('\n').find(l=>l.startsWith('function gestureReadingRegion('));
function region({existing=null,v4=true,client=200,scroll=400,overflow='auto'}={}){
 const detail={clientHeight:client,scrollHeight:scroll,closest:()=>v4?{}:null};
 const ctx={getComputedStyle:()=>({overflowY:overflow})};vm.createContext(ctx);vm.runInContext(source,ctx);
 const found=ctx.gestureReadingRegion({closest:s=>s==='.job-detail'?detail:existing});return {found,detail};
}
test('D4 reading retains established gesture scroll regions',()=>{const existing={};assert.equal(region({existing}).found,existing);});
test('D4 overflowing visible task detail uses established scroll mode',()=>{const x=region();assert.equal(x.found,x.detail);});
test('D4 nonoverflow and V3 task detail retain original gesture behavior',()=>{for(const data of [{v4:false},{client:0},{scroll:200},{overflow:'visible'},{overflow:'hidden'}])assert.equal(region(data).found,null);});
