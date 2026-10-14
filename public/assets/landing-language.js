(()=>{
  const button=document.querySelector('#language-toggle');
  if(!button)return;
  let language=localStorage.getItem('qramen-language')||'fr';
  const qroque=document.body.classList.contains('theme-qroque');
  const translations={
    fr:{eyebrow:qroque?'CROQUE-MONSIEUR · ROUEN':'LE QRAMEN · BAR À RAMEN · ROUEN',kicker:qroque?'LE BONHEUR ENTRE DEUX TRANCHES':'一杯のよろこび',baseline:qroque?'Du croustillant, du fondant.<br><strong>Du fait maison.</strong>':'Scannez. Commandez.<br><strong>Slurpez.</strong>',menu:'Voir le menu',find:'NOUS TROUVER',table:'À TABLE',everyday:'Tous les jours',hours:'12h–14h30 · 19h–22h30',demo:'Écrans normalement réservés au personnel · démo',switchToQroque:'Vous préférez un croque ?',switchToQramen:'Un ramen vous tente ?',themeLight:'Activer le mode clair',themeDark:'Activer le mode sombre'},
    en:{eyebrow:qroque?'CROQUE-MONSIEUR · ROUEN':'RAMEN BAR · ROUEN',kicker:qroque?'HAPPINESS BETWEEN TWO SLICES':'一杯のよろこび · A BOWL OF JOY',baseline:qroque?'Crispy, melty.<br><strong>Made in house.</strong>':'Scan. Order.<br><strong>Slurp.</strong>',menu:'View the menu',find:'FIND US',table:'AT YOUR TABLE',everyday:'Every day',hours:'12–2:30 pm · 7–10:30 pm',demo:'Staff screens · demo',switchToQroque:'Fancy a croque?',switchToQramen:'How about ramen?',themeLight:'Switch to light mode',themeDark:'Switch to dark mode'}
  };
  function render(){
    const t=translations[language];document.documentElement.lang=language;
    document.querySelector('#eyebrow').textContent=t.eyebrow;
    document.querySelector('#landing-kicker').innerHTML=t.kicker+' <span>·</span> ROUEN';
    document.querySelector('#landing-baseline').innerHTML=t.baseline;
    document.querySelector('#menu-link').childNodes[0].textContent=t.menu+' ';
    document.querySelectorAll('#landing-bottom .label')[0].textContent=t.find;
    document.querySelectorAll('#landing-bottom .label')[1].textContent=t.table;
    const bottom=document.querySelectorAll('#landing-bottom>div');
    bottom[0].querySelector('p').innerHTML=(qroque?'QRoque Monsieur':'Le QRamen')+'<br>14 rue du Gros-Horloge<br>76000 Rouen';
    bottom[1].querySelector('p').innerHTML=t.everyday+'<br>'+t.hours;
    const demoLinks=document.querySelectorAll('.demo-actions a');
    demoLinks.forEach((link,i)=>link.childNodes[0].textContent=(language==='en'?['Demo: Table 5','Demo: Kitchen','Demo: Dining room','Demo: QR'][i]:['Demo : Table 5','Demo : Cuisine','Demo : Salle','Demo : QR'][i])+' ');
    document.querySelector('.demo-note').textContent=t.demo;
    document.querySelectorAll('.restaurant-switch-button[data-switch]').forEach(s=>{const name=s.dataset.targetConcept;s.querySelector('span').textContent=name==='QRoque'?t.switchToQroque:t.switchToQramen;s.setAttribute('aria-label',name==='QRoque'?t.switchToQroque:t.switchToQramen)});
    const theme=document.querySelector('.theme-toggle');if(theme)theme.setAttribute('aria-label',document.body.classList.contains('dark-mode')?t.themeLight:t.themeDark);
    button.textContent=language==='fr'?'EN':'FR';
    button.setAttribute('aria-label',language==='fr'?'EN — Switch to English':'FR — Passer en français');
  }
  button.addEventListener('click',()=>{language=language==='fr'?'en':'fr';localStorage.setItem('qramen-language',language);render()});
  render();
})();
