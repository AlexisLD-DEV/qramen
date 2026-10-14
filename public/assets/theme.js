(()=>{
  const key='qramen-theme',body=document.body,button=document.querySelector('.theme-toggle');
  const saved=localStorage.getItem(key);
  const fallback=body.classList.contains('theme-qroque')?'light':(body.dataset.defaultTheme||'light');
  function apply(theme){
    const dark=theme==='dark';body.classList.toggle('dark-mode',dark);
    document.querySelector('meta[name="theme-color"]')?.setAttribute('content',dark?'#171a1e':(body.classList.contains('theme-qroque')?'#F3EDE1':'#F7F2E9'));
    if(button){button.textContent=dark?'☀':'☾';button.setAttribute('aria-label',dark?'Activer le mode clair':'Activer le mode sombre');button.setAttribute('aria-pressed',String(dark));}
  }
  apply(saved==='dark'||saved==='light'?saved:fallback);
  button?.addEventListener('click',()=>{const theme=body.classList.contains('dark-mode')?'light':'dark';localStorage.setItem(key,theme);apply(theme)});
  const current=new URLSearchParams(location.search).get('concept')||(location.hostname.includes('qroque')?'QRoque':'QRamen');
  document.querySelectorAll('.restaurant-switch a[data-concept]').forEach(a=>{
    const target=a.dataset.concept,otherHost=target==='QRoque'?'qroque.alexisld.fr':'qramen.alexisld.fr';
    const u=new URL(location.pathname,location.protocol+'//'+otherHost);
    for(const [k,v] of new URLSearchParams(location.search))if(k!=='concept')u.searchParams.append(k,v);
    a.href=u.href;if(target===current)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');
  });
})();
