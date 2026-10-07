/* Local persistence only. A restored core/suite pair has one atomic commit point. */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.PhoneStorage=api.create(()=>root.localStorage);
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const CORE_KEY='ai-phone-ui-core-v1',SUITE_KEY='ai-phone-ui-suite-v1';
  const SNAPSHOT_KEY='ai-phone-ui-state-v1';
  function field(key){
    if(key===CORE_KEY)return 'core';
    if(key===SUITE_KEY)return 'suite';
    throw Error('未知的本机资料区域');
  }
  function decode(raw){
    const value=JSON.parse(raw);
    if(!value||value.format!=='ai-phone-ui-local-state'||value.version!==1||typeof value.core!=='string'||typeof value.suite!=='string')throw Error('本机资料快照无效');
    return value;
  }
  function create(resolveStorage){
    const getStorage=typeof resolveStorage==='function'?resolveStorage:()=>resolveStorage;
    return {
      getItem(key){
        const name=field(key),storage=getStorage(),raw=storage.getItem(SNAPSHOT_KEY);
        return raw===null?storage.getItem(key):decode(raw)[name];
      },
      setItem(key,value){
        const name=field(key);if(typeof value!=='string')throw Error('资料必须先序列化');
        const storage=getStorage(),raw=storage.getItem(SNAPSHOT_KEY);
        if(raw===null){storage.setItem(key,value);return;}
        const next=decode(raw);next[name]=value;
        storage.setItem(SNAPSHOT_KEY,JSON.stringify(next));
      },
      replace(core,suite){
        if(typeof core!=='string'||typeof suite!=='string')throw Error('恢复资料必须先序列化');
        // Build the complete value before touching storage. Web Storage setItem
        // either replaces this one key or throws without changing its old value.
        const next=JSON.stringify({format:'ai-phone-ui-local-state',version:1,core,suite});
        const storage=getStorage();storage.setItem(SNAPSHOT_KEY,next);
        // The committed snapshot is authoritative even if cleanup is interrupted.
        // Never delete legacy data until the replacement has been committed.
        for(const key of [CORE_KEY,SUITE_KEY]){try{storage.removeItem(key);}catch{}}
      }
    };
  }
  return {create,CORE_KEY,SUITE_KEY,SNAPSHOT_KEY};
});
