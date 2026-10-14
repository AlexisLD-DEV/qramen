// Runtime endpoint order: Cloudflare Worker, then the legacy n8n service.
window.QRAMEN_API='https://qramen-engine.alexisledeunf.workers.dev/webhook/qramen';
window.QRAMEN_API_FALLBACK='https://n8n.ledeunf.fr/webhook/qramen';
window.qramenFetch=async function(path,options={}){
  let last;
  const {timeoutMs=8000,signal:ignoredSignal,...requestOptions}=options;
  for(const base of [window.QRAMEN_API,window.QRAMEN_API_FALLBACK]){
    try{const response=await fetch(base+path,{...requestOptions,signal:AbortSignal.timeout(timeoutMs)});if(!response.ok)throw new Error('API '+response.status);return response;}catch(error){last=error}
  }
  throw last||new Error('API indisponible');
};
