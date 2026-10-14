// Runtime endpoint order: Cloudflare Worker, then the legacy n8n service.
window.QRAMEN_API='https://qramen-engine.alexisledeunf.workers.dev/webhook/qramen';
window.QRAMEN_API_FALLBACK='https://n8n.ledeunf.fr/webhook/qramen';
window.qramenFetch=async function(path,options={}){
  let last;
  const {timeoutMs=8000,signal:ignoredSignal,...requestOptions}=options;
  const readOnly=['GET','HEAD'].includes((requestOptions.method||'GET').toUpperCase());
  for(const base of readOnly?[window.QRAMEN_API,window.QRAMEN_API_FALLBACK]:[window.QRAMEN_API]){
    try{const response=await fetch(base+path,{...requestOptions,signal:AbortSignal.timeout(timeoutMs)});if(!response.ok)throw new Error('API '+response.status);return response;}catch(error){last=error}
  }
  throw last||new Error('API indisponible');
};
