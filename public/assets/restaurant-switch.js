(()=>{
  const buttons=[...document.querySelectorAll('.restaurant-switch[data-switch]')];
  if(!buttons.length)return;
  const query=new URLSearchParams(location.search);
  const restaurantSelect=document.querySelector('#restaurant, #salle-concept');
  let concept=query.get('concept')||(location.hostname.includes('qroque')?'QRoque':'QRamen');
  if(!['QRamen','QRoque'].includes(concept))concept='QRamen';
  if(restaurantSelect)concept=restaurantSelect.value;
  const targetFor=()=>concept==='QRamen'?'QRoque':'QRamen';
  function render(){
    const target=targetFor(),isCroque=target==='QRoque';
    const label=isCroque?'Vous préférez un croque ?':'Un ramen vous tente ?';
    const mascot=isCroque?'compact-qroque.svg':'compact-qramen.svg';
    for(const button of buttons){
      button.replaceChildren();
      const img=document.createElement('img');img.src='assets/mascottes/'+mascot;img.alt='';img.setAttribute('aria-hidden','true');
      const text=document.createElement('span');text.textContent=label;
      button.append(img,text);button.setAttribute('aria-label',label);button.dataset.targetConcept=target;
    }
  }
  restaurantSelect?.addEventListener('change',()=>{concept=restaurantSelect.value;render()});
  for(const button of buttons)button.addEventListener('click',()=>{
    const next=targetFor(),url=new URL(location.href);
    url.protocol='https:';url.port='';url.hostname=next==='QRoque'?'qroque.alexisld.fr':'qramen.alexisld.fr';
    url.searchParams.set('concept',next);
    if(button.dataset.cart)url.searchParams.set('panier',button.dataset.cart);
    location.assign(url.href);
  });
  render();
})();
