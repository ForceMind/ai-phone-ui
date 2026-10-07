/* Shared, deterministic local state. No network side effects. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.PhoneModel=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const SCHEMA=1;
  const clock=v=>typeof v==='string'&&/^(?:[01]\d|2[0-3]):[0-5]\d$/.test(v);
  const text=(v,n=3000)=>typeof v==='string'?v.slice(0,n):'';
  const finite=(v,a,b,fallback)=>Number.isFinite(v)?Math.min(b,Math.max(a,v)):fallback;
  function initial(){return {schema:SCHEMA,nickname:'我的手机',consent:{camera:false,microphone:false,notifications:false},settings:{largeText:false,assist:false,contrast:false,sound:false,volume:45,quiet:false},messages:[],drafts:{},forms:{},checklist:[],schedules:[],calendar:[],alarms:[{id:'alarm-demo',time:'07:30',label:'早起，留一点时间',enabled:false,repeat:'工作日'}],memories:[{id:'pref-style',text:'照片处理时保留原图，不覆盖人物。',source:'明确设置 · 示例偏好',enabled:true},{id:'pref-focus',text:'交互尽量使用单手手势。',source:'项目交互约束',enabled:true}],audit:[],generatedDraft:'',cropRatio:'1:1',comparison:50,musicPlaying:false,callState:'idle',dial:'',messageDraft:'',localOutbox:[],readQuery:'',remoteState:'disconnected'};}
  function validate(raw){
    if(!raw||typeof raw!=='object'||raw.schema!==SCHEMA)throw new Error('备份版本无效或不受支持');
    const d=initial();d.nickname=text(raw.nickname,32)||d.nickname;
    for(const key of Object.keys(d.consent))d.consent[key]=raw.consent?.[key]===true;
    for(const key of ['largeText','assist','contrast','sound','quiet'])d.settings[key]=raw.settings?.[key]===true;
    d.settings.volume=finite(raw.settings?.volume,0,100,45);
    const clean=(key,fn,max=100)=>{if(raw[key]!==undefined&&!Array.isArray(raw[key]))throw Error(key+' 必须是列表');return (raw[key]||[]).slice(0,max).filter(x=>x&&typeof x==='object').map(fn);};
    d.messages=clean('messages',m=>({role:m.role==='user'?'user':'assistant',text:text(m.text,5000)}),80);
    d.checklist=clean('checklist',m=>({id:text(m.id,80),text:text(m.text,3000),done:!!m.done}),200);
    d.schedules=clean('schedules',m=>({id:text(m.id,80),name:text(m.name,150),time:clock(m.time)?m.time:'09:00',frequency:['每天','每周一','每周五'].includes(m.frequency)?m.frequency:'每周五',timezone:['Asia/Shanghai','America/Los_Angeles','UTC'].includes(m.timezone)?m.timezone:'Asia/Shanghai',enabled:false,source:'当前笔记'}),40);
    d.calendar=clean('calendar',m=>({id:text(m.id,80),title:text(m.title,150),date:text(m.date,10),time:text(m.time,5),note:text(m.note,1000)}),100);
    d.alarms=raw.alarms?clean('alarms',m=>({id:text(m.id,80),label:text(m.label,80),time:clock(m.time)?m.time:'07:30',enabled:!!m.enabled,repeat:text(m.repeat,40)}),30):d.alarms;
    d.memories=raw.memories?clean('memories',m=>({id:text(m.id,80),text:text(m.text,1000),source:text(m.source,150),enabled:!!m.enabled}),80):d.memories;
    d.audit=clean('audit',m=>({id:text(m.id,80),title:text(m.title,150),at:finite(m.at,0,1e15,0),detail:text(m.detail,500)}),120);
    d.localOutbox=clean('localOutbox',m=>({id:text(m.id,80),text:text(m.text,3000),recipient:text(m.recipient,80),status:'local-preview-only'}),50);
    if(raw.drafts&&typeof raw.drafts==='object')for(const [key,value] of Object.entries(raw.drafts)){if(/^[A-Z]{2,3}-\d{2}$/.test(key))d.drafts[key]=text(value,10000);}
    if(raw.forms&&typeof raw.forms==='object')for(const [page,fields] of Object.entries(raw.forms)){if(/^[A-Z]{2,3}-\d{2}$/.test(page)&&fields&&typeof fields==='object'){d.forms[page]={};for(const [k,v] of Object.entries(fields)){if(/^[A-Za-z][A-Za-z0-9]{0,40}$/.test(k))d.forms[page][k]=text(v,10000);}}}
    d.generatedDraft=text(raw.generatedDraft,3000);d.cropRatio=['1:1','4:3','3:4','16:9','9:16'].includes(raw.cropRatio)?raw.cropRatio:'1:1';d.comparison=finite(raw.comparison,0,100,50);d.messageDraft=text(raw.messageDraft);return d;
  }
  function extractChecklist(source){return String(source).split(/\n+/).map(x=>x.trim()).filter(Boolean).slice(0,200).map((t,i)=>({id:'line-'+i,text:t,done:false}));}
  function centerCrop(width,height,ratio){const parts=String(ratio).split(':').map(Number);if(parts.length!==2||parts.some(n=>!Number.isFinite(n)||n<=0)||!Number.isFinite(width)||!Number.isFinite(height)||width<=0||height<=0)throw new Error('裁切尺寸无效');const r=parts[0]/parts[1];const w=Math.min(width,height*r),h=w/r;return {x:(width-w)/2,y:(height-h)/2,width:w,height:h};}
  function search(catalog,note,query){const q=String(query).trim().toLocaleLowerCase();if(!q)return [];const screens=catalog.filter(x=>(x.id+' '+x.name+' '+x.purpose).toLowerCase().includes(q)).map(x=>({type:'screen',id:x.id,title:x.name,detail:x.purpose}));if(String(note).toLowerCase().includes(q))screens.unshift({type:'note',id:'DOC-02',title:'我的想法',detail:String(note).slice(0,100)});return screens.slice(0,60);}
  function approvalSnapshot(kind,payload){const freeze=o=>{if(o&&typeof o==='object'){Object.values(o).forEach(freeze);Object.freeze(o);}return o;};return freeze({kind,id:'approval-'+Date.now()+'-'+Math.random().toString(36).slice(2),payload:JSON.parse(JSON.stringify(payload)),consumed:false});}
  return {SCHEMA,initial,validate,extractChecklist,centerCrop,search,approvalSnapshot};
});
