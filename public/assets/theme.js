(()=>{
  const body=document.body,button=document.querySelector('.theme-toggle');
  const key=body.dataset.themeScope==='staff'?'qramen-theme-staff':'qramen-theme';
  const saved=localStorage.getItem(key);
  const fallback=body.dataset.themeScope==='staff'?'light':(body.classList.contains('theme-qroque')?'light':(body.dataset.defaultTheme||'light'));
  const lightColor=()=>body.classList.contains('theme-qroque')||location.hostname.startsWith('qroque.')?'#F3EDE1':'#F7F2E9';
  function apply(theme){
    const dark=theme==='dark';body.classList.toggle('dark-mode',dark);
    document.querySelector('meta[name="theme-color"]')?.setAttribute('content',dark?'#171a1e':lightColor());
    if(button){button.textContent=dark?'☀':'☾';button.setAttribute('aria-label',dark?'Activer le mode clair':'Activer le mode sombre');button.setAttribute('aria-pressed',String(dark));}
  }
  apply(saved==='dark'||saved==='light'?saved:fallback);
  button?.addEventListener('click',()=>{const theme=body.classList.contains('dark-mode')?'light':'dark';localStorage.setItem(key,theme);apply(theme)});
})();
