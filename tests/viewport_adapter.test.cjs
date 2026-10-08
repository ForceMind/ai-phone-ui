'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs');
const core=fs.readFileSync('src/js/core.js','utf8');
function fixture(width=360,height=672){
 const screen={clientWidth:width,clientHeight:height,querySelectorAll:()=>elements,getBoundingClientRect:()=>({left:40,top:70,width:width*.7,height:height*.9})},elements=[];
 const ctx={W:360,H:672,$:()=>screen,viewportTransforms:new WeakMap()};vm.createContext(ctx);
 for(const n of ['viewportSize','viewX','viewY','viewportTransform','viewportStyles','refreshViewportTransforms','coords'])vm.runInContext(core.split('\n').find(l=>l.startsWith('function '+n+'(')),ctx);
 return{ctx,screen,elements};
}
test('viewport baseline is an identity transform',()=>{const {ctx}=fixture();assert.equal(ctx.viewX(360),360);assert.equal(ctx.viewY(672),672);assert.equal(ctx.viewportTransform('translateX(-720px)'), 'translateX(-720px)');});
test('portrait scales each render axis independently without changing logical thresholds',()=>{const {ctx}=fixture(393,852);assert.equal(ctx.viewX(360),393);assert.equal(ctx.viewY(672),852);assert.equal(ctx.viewportTransform('translateY(-672px)'), 'translateY(-852px)');assert.equal(ctx.viewportTransform('translate3d(360px,0,0)'), 'translate3d(393px,0,0)');assert.equal(ctx.W,360);assert.equal(ctx.H,672);});
test('actual non-uniform screen rect normalizes both pointer axes',()=>{const {ctx,screen}=fixture(393,852),r=screen.getBoundingClientRect();const p=ctx.coords({clientX:r.left+r.width*.25,clientY:r.top+r.height*.75});assert.ok(Math.abs(p.x-90)<1e-10);assert.ok(Math.abs(p.y-504)<1e-10);});
test('zero-area screen cannot yield NaN pointer coordinates',()=>{const {ctx,screen}=fixture();screen.getBoundingClientRect=()=>({width:0,height:0});assert.equal(ctx.coords({clientX:0,clientY:0}),null);});
test('reprojection uses retained logical transforms, not already scaled output',()=>{const {ctx,screen,elements}=fixture(),el={style:{}};elements.push(el);const source={transform:'translateX(-360px)',opacity:'1'};Object.assign(el.style,ctx.viewportStyles(el,source));screen.clientWidth=393;for(let i=0;i<30;i++)ctx.refreshViewportTransforms();assert.equal(el.style.transform,'translateX(-393px)');screen.clientWidth=360;ctx.refreshViewportTransforms();assert.equal(el.style.transform,'translateX(-360px)');assert.equal(source.transform,'translateX(-360px)');});
test('non-position CSS and zero transforms remain unchanged',()=>{const {ctx}=fixture(393,852);assert.equal(ctx.viewportTransform('rotate(20deg) scale(.5)'), 'rotate(20deg) scale(.5)');assert.equal(ctx.viewportTransform('translate3d(0,0,0)'), 'translate3d(0,0,0)');});
