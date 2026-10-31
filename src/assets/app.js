/* Moto S. Cristóvão — scripts partilhados */
(function(){
const D = window.DATA, C = window.CFG || {};
const $ = (s,el=document)=>el.querySelector(s), $$ = (s,el=document)=>[...el.querySelectorAll(s)];
const ROOT = document.body.dataset.root || "";
const CARTA = {AM:"AM / B", A1:"A1 / B*", A2:"A2", A:"A"};
const SEG1 = {"Scooters":"Scooter","Maxi-scooters":"Maxi-scooter","Naked":"Naked","Trail / Aventura":"Trail / Aventura","Custom e clássicas":"Custom / Clássica","Desportivas":"Desportiva","Moto 4 / UTV":"Moto 4 / UTV"};
const eur = n => n ? "PVP "+Number(n).toLocaleString("pt-PT",{minimumFractionDigits:0})+" €" : "Preço sob consulta";
const cor = b => (D.marcas[b]||{}).cor || "#2b2f34";
const h = v => String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const safeUrl = u => /^(https:\/\/|assets\/|\.\.\/assets\/)/.test(u||"") ? h(u) : "";
const store = {get(k){try{return JSON.parse(localStorage.getItem(k))}catch(e){return null}},set(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}};

/* ---------- Ilustrações genéricas por segmento (substituídas pelas fotos reais quando houver img) ---------- */
function wheel(x,y,r){return `<g><circle cx="${x}" cy="${y}" r="${r}" fill="#1f2226"/><circle cx="${x}" cy="${y}" r="${r*.66}" fill="#c9ccd0"/><circle cx="${x}" cy="${y}" r="${r*.56}" fill="#eef0f2"/><circle cx="${x}" cy="${y}" r="${r*.34}" fill="none" stroke="#9aa0a6" stroke-width="3"/><circle cx="${x}" cy="${y}" r="${r*.12}" fill="#5b6066"/></g>`}
const SH = {
  "Naked": c=>`${wheel(62,120,34)}${wheel(204,120,34)}
    <path d="M62 120 L128 104" stroke="#3a3f45" stroke-width="9" stroke-linecap="round"/>
    <path d="M204 120 L182 52" stroke="#9aa0a6" stroke-width="7" stroke-linecap="round"/>
    <rect x="108" y="84" width="52" height="38" rx="6" fill="#5b6066"/><rect x="114" y="90" width="18" height="26" rx="3" fill="#7b8087"/>
    <path d="M128 112 Q150 132 186 128 L192 136 Q148 142 122 120Z" fill="#8b9096"/>
    <path d="M96 78 L176 66 L168 86 L110 92Z" fill="#3a3f45"/>
    <path d="M104 64 Q126 42 166 50 L178 68 L108 80Z" fill="${c}"/>
    <path d="M58 70 L108 66 L110 78 L66 82Z" fill="#26292d"/>
    <path d="M30 58 L66 68 L64 80 L42 76Z" fill="${c}"/>
    <path d="M28 96 Q46 86 64 88" stroke="#26292d" stroke-width="5" fill="none"/>
    <circle cx="188" cy="58" r="11" fill="#26292d"/><circle cx="191" cy="58" r="6" fill="#f4f1d0"/>
    <path d="M170 40 L192 46" stroke="#26292d" stroke-width="5" stroke-linecap="round"/>
    <path d="M186 94 Q206 84 226 96" stroke="#26292d" stroke-width="6" fill="none"/>`,
  "Scooters": c=>`${wheel(66,124,26)}${wheel(198,124,26)}
    <path d="M28 94 Q34 62 92 60 L128 62 L136 102 L70 114 Q34 114 28 94Z" fill="${c}"/>
    <path d="M48 62 Q76 44 128 54 L126 64 L52 68Z" fill="#26292d"/>
    <rect x="112" y="100" width="62" height="10" fill="#3a3f45"/>
    <path d="M164 34 L182 34 Q192 78 202 112 L180 114 Q170 78 164 34Z" fill="${c}"/>
    <path d="M172 112 Q198 92 222 112" stroke="${c}" stroke-width="8" fill="none"/>
    <path d="M160 26 L190 30" stroke="#26292d" stroke-width="5" stroke-linecap="round"/>
    <circle cx="186" cy="44" r="6" fill="#f4f1d0"/>
    <path d="M52 112 Q66 98 86 108" stroke="#26292d" stroke-width="6" fill="none"/>
    <rect x="24" y="80" width="10" height="7" fill="#e5463e"/>`,
  "Maxi-scooters": c=>`${wheel(62,124,28)}${wheel(204,124,28)}
    <path d="M20 92 Q24 58 86 52 L134 56 L142 104 L72 116 Q24 116 20 92Z" fill="${c}"/>
    <path d="M40 54 Q60 36 96 42 L104 34 Q126 40 134 52 L130 60 L44 62Z" fill="#26292d"/>
    <rect x="112" y="100" width="66" height="10" fill="#3a3f45"/>
    <path d="M160 26 L190 28 Q204 74 212 114 L184 116 Q170 74 160 26Z" fill="${c}"/>
    <path d="M160 26 L176 2 L190 6 L184 30Z" fill="#b8d4e8" opacity=".85"/>
    <path d="M176 114 Q204 92 230 114" stroke="${c}" stroke-width="8" fill="none"/>
    <path d="M190 52 L214 60 L206 70 L188 64Z" fill="#f4f1d0"/>
    <path d="M44 114 Q62 96 88 108" stroke="#26292d" stroke-width="7" fill="none"/>`,
  "Trail / Aventura": c=>`${wheel(60,118,34)}${wheel(206,118,38)}
    <path d="M60 118 L126 100" stroke="#3a3f45" stroke-width="9" stroke-linecap="round"/>
    <path d="M206 118 L180 36" stroke="#9aa0a6" stroke-width="8" stroke-linecap="round"/>
    <rect x="104" y="80" width="54" height="38" rx="6" fill="#5b6066"/>
    <path d="M104 118 L160 118 L156 128 L110 128Z" fill="#3a3f45"/>
    <path d="M98 56 Q130 36 176 44 L186 70 L150 86 L104 82Z" fill="${c}"/>
    <path d="M52 56 L104 54 L106 66 L60 70Z" fill="#26292d"/>
    <path d="M22 44 L60 56 L58 68 L30 62Z" fill="${c}"/>
    <rect x="18" y="62" width="34" height="22" fill="#3a3f45"/>
    <path d="M172 40 L188 14 L200 18 L190 46Z" fill="#b8d4e8" opacity=".85"/>
    <path d="M182 48 L206 54 L200 70 L184 64Z" fill="#26292d"/><circle cx="198" cy="60" r="5" fill="#f4f1d0"/>
    <path d="M196 74 L232 86 L228 92 L196 82Z" fill="${c}"/>
    <path d="M118 104 Q90 108 70 92 L56 90" stroke="#8b9096" stroke-width="6" fill="none"/>`,
  "Custom e clássicas": c=>`${wheel(56,122,32)}${wheel(214,122,30)}
    <path d="M56 122 L120 112" stroke="#3a3f45" stroke-width="9" stroke-linecap="round"/>
    <path d="M214 122 L186 52" stroke="#c0c4c8" stroke-width="7" stroke-linecap="round"/>
    <path d="M108 92 L130 76 L150 76 L158 118 L114 120Z" fill="#6b7077"/>
    <circle cx="128" cy="100" r="11" fill="#9aa0a6"/><circle cx="146" cy="96" r="9" fill="#9aa0a6"/>
    <path d="M118 120 Q170 128 236 118 L238 126 Q170 136 116 128Z" fill="#c0c4c8"/>
    <path d="M120 66 Q146 48 178 60 L176 74 L124 80Z" fill="${c}"/>
    <path d="M68 82 Q90 70 122 74 L120 86 L72 92Z" fill="#26292d"/>
    <path d="M22 100 Q30 72 66 76 L70 92 Q44 90 34 104Z" fill="${c}"/>
    <path d="M168 38 Q182 30 194 44" stroke="#c0c4c8" stroke-width="5" fill="none"/>
    <circle cx="194" cy="62" r="11" fill="#c0c4c8"/><circle cx="197" cy="62" r="7" fill="#f4f1d0"/>
    <path d="M190 108 Q212 96 234 108" stroke="${c}" stroke-width="7" fill="none"/>`,
  "Desportivas": c=>`${wheel(62,120,32)}${wheel(204,120,32)}
    <path d="M62 120 L126 106" stroke="#3a3f45" stroke-width="9" stroke-linecap="round"/>
    <path d="M204 120 L184 60" stroke="#9aa0a6" stroke-width="7" stroke-linecap="round"/>
    <path d="M96 62 Q150 40 196 54 L214 84 L176 116 L110 116 L98 92Z" fill="${c}"/>
    <path d="M196 54 L214 84 L200 86 L186 62Z" fill="#26292d"/>
    <path d="M178 50 L198 36 L206 46 L190 56Z" fill="#b8d4e8" opacity=".85"/>
    <path d="M196 66 L212 74 L206 82 L194 76Z" fill="#f4f1d0"/>
    <path d="M60 66 L102 62 L104 72 L66 76Z" fill="#26292d"/>
    <path d="M26 52 L66 64 L64 76 L36 70Z" fill="${c}"/>
    <path d="M122 96 L170 96" stroke="#ffffff" stroke-width="4" opacity=".7"/>
    <path d="M98 112 Q74 106 58 86" stroke="#8b9096" stroke-width="7" fill="none"/>`,
  "Moto 4 / UTV": c=>`${wheel(62,118,32)}${wheel(196,118,32)}
    <path d="M24 92 Q36 66 92 70 L170 70 Q226 66 236 92 L232 98 Q214 82 196 84 Q176 84 168 100 L92 100 Q86 84 62 84 Q42 84 28 98Z" fill="${c}"/>
    <path d="M88 70 L104 52 L150 52 L160 70Z" fill="#26292d"/>
    <rect x="96" y="96" width="70" height="22" rx="4" fill="#5b6066"/>
    <path d="M30 62 L82 62" stroke="#3a3f45" stroke-width="5"/><path d="M186 62 L232 62" stroke="#3a3f45" stroke-width="5"/>
    <path d="M30 62 L34 72 M82 62 L80 70 M186 62 L188 70 M232 62 L228 72" stroke="#3a3f45" stroke-width="4"/>
    <path d="M160 52 L176 34 L196 32" stroke="#26292d" stroke-width="5" fill="none" stroke-linecap="round"/>
    <rect x="218" y="80" width="12" height="8" fill="#f4f1d0"/>`
};
function illus(x){const f=SH[x.seg]||SH["Naked"];return `<svg viewBox="0 0 260 160" role="img" aria-label="Ilustração ${x.b||""} ${x.m}"><ellipse cx="132" cy="154" rx="108" ry="5" fill="#000" opacity=".08"/>${f(x.b?cor(x.b):"#6b7077")}</svg>`}
function photo(x,size="s",i=0){
  const f=(x.fotos||[])[i]; if(!f) return illus(x);
  const src=safeUrl(ROOT+f[size]); if(!src) return illus(x);
  return `<img src="${src}" alt="${h(((x.b||"")+" "+x.m).trim())}" loading="lazy" data-fb="${h(encodeURIComponent(illus(x)))}">`;
}
window.MSC = {photo, illus, eur, cor, CARTA, SEG1};
document.addEventListener("error",e=>{const t=e.target;if(t.tagName==="IMG"&&t.dataset.fb)t.outerHTML=decodeURIComponent(t.dataset.fb)},true);

/* ---------- Links de convite/recuperação do painel → /admin ---------- */
if(/(invite|recovery|confirmation|email_change)_token=/.test(location.hash)) location.replace(ROOT+"admin/"+location.hash);

/* ---------- Galeria (página de mota/usada) ---------- */
const gal=$("#gal");
if(gal){
  const x=(gal.dataset.kind==="usada"?D.usados:D.motas).find(v=>v.id===gal.dataset.id);
  if(x){
    const fs=x.fotos||[];let cur=0;
    gal.innerHTML=`<button class="main" type="button" aria-label="Ampliar foto">${photo(x,"l",0)}</button>`+
      (fs.length>1?`<div class="thumbs">${fs.map((f,k)=>`<button type="button" data-k="${k}" aria-label="Foto ${k+1}" class="${k?"":"on"}">${photo(x,"s",k)}</button>`).join("")}</div>`:"");
    const show=k=>{cur=k;$(".main",gal).innerHTML=photo(x,"l",k);$$(".thumbs button",gal).forEach((b,j)=>b.classList.toggle("on",j===k))};
    $$(".thumbs button",gal).forEach(b=>b.onclick=()=>show(+b.dataset.k));
    if(fs.length){
      const lb=document.createElement("div");lb.className="lb";lb.setAttribute("role","dialog");lb.setAttribute("aria-label","Galeria de fotos");
      lb.innerHTML=`<button class="x" aria-label="Fechar">×</button>${fs.length>1?'<button class="nav p" aria-label="Anterior">‹</button><button class="nav n" aria-label="Seguinte">›</button>':""}<img alt=""><span class="cnt"></span>`;
      document.body.appendChild(lb);
      const img=$("img",lb),cnt=$(".cnt",lb);
      const open=k=>{cur=(k+fs.length)%fs.length;img.src=ROOT+fs[cur].l;img.alt=h(((x.b||"")+" "+x.m).trim())+" — foto "+(cur+1);cnt.textContent=(cur+1)+" / "+fs.length;lb.classList.add("on");document.body.style.overflow="hidden"};
      const close=()=>{lb.classList.remove("on");document.body.style.overflow=""};
      $(".main",gal).onclick=()=>open(cur);
      $(".x",lb).onclick=close;lb.onclick=e=>{if(e.target===lb)close()};
      if(fs.length>1){$(".p",lb).onclick=()=>open(cur-1);$(".n",lb).onclick=()=>open(cur+1)}
      document.addEventListener("keydown",e=>{if(!lb.classList.contains("on"))return;if(e.key==="Escape")close();if(e.key==="ArrowLeft")open(cur-1);if(e.key==="ArrowRight")open(cur+1)});
      let sx=0;lb.addEventListener("touchstart",e=>sx=e.touches[0].clientX,{passive:true});lb.addEventListener("touchend",e=>{const d=e.changedTouches[0].clientX-sx;if(Math.abs(d)>50)open(cur+(d<0?1:-1))});
    }
  }
}

/* ---------- Cartões ---------- */
function card(x, compare){
  const specs=[SEG1[x.seg], x.cc?x.cc+" cc":"Vários modelos", x.carta?"Carta "+CARTA[x.carta]:"Carta: consultar"];
  return `<article class="card">
    <div class="ph">${photo(x)}<span class="lbl" style="background:${cor(x.b)}">${x.b}</span><span class="stock ${x.disp==="stand"?"in":""}">${x.disp==="stand"?"Em stand":"Por encomenda"}</span></div>
    <div class="bd"><h3><a href="${ROOT}motas/${x.id}.html">${x.m}</a></h3>
      <ul>${specs.map(s=>`<li>${s}</li>`).join("")}</ul>
      <div class="pr"><b>${eur(x.preco)}</b><span class="more">Ver mais →</span></div>
    </div></article>`;
}

/* ---------- Header / menu / cookies / WhatsApp ---------- */
$(".burger")?.addEventListener("click",()=>{const n=$("nav.main");n.classList.toggle("open");$(".burger").setAttribute("aria-expanded",n.classList.contains("open"))});
const page=document.body.dataset.page; $$(`nav.main a[data-p="${page}"]`).forEach(a=>a.classList.add("on"));
if(!store.get("cookies")){
  document.body.insertAdjacentHTML("beforeend",`<div class="cookie" id="cookie" role="dialog" aria-label="Cookies">Este site utiliza apenas cookies essenciais e o mapa do Google. <a href="${ROOT}privacidade.html">Saber mais</a> <button class="btn btn-sm" id="cookieOk">Aceitar</button></div>`);
  $("#cookieOk").onclick=()=>{store.set("cookies",1);$("#cookie").remove()};
}
const waMsg="Olá! Vim pelo site da Moto S. Cristóvão e gostava de obter informações.";
const waHref=C.whatsapp?`https://wa.me/${C.whatsapp}?text=${encodeURIComponent(waMsg)}`:`${ROOT}contactos.html`;
if(C.whatsapp) document.body.insertAdjacentHTML("beforeend",`<a class="wa" href="${waHref}" ${C.whatsapp?'target="_blank" rel="noopener"':""} aria-label="Falar connosco por WhatsApp"><svg viewBox="0 0 32 32" fill="#fff"><path d="M16 3C9 3 3.3 8.6 3.3 15.6c0 2.2.6 4.4 1.7 6.3L3.2 29l7.3-1.9c1.8 1 3.9 1.5 6 1.5h0c7 0 12.7-5.7 12.7-12.6C28.7 8.6 23 3 16 3zm0 23.1c-1.9 0-3.8-.5-5.4-1.5l-.4-.2-4.3 1.1 1.2-4.2-.3-.4c-1.1-1.7-1.6-3.6-1.6-5.6C5.2 9.8 10 5.1 16 5.1s10.7 4.7 10.7 10.5S21.9 26.1 16 26.1zm5.9-7.9c-.3-.2-1.9-.9-2.2-1s-.5-.2-.7.2-.8 1-1 1.2-.4.2-.7 0c-.3-.2-1.4-.5-2.6-1.6-1-.9-1.6-1.9-1.8-2.2s0-.5.1-.6l.5-.6c.2-.2.2-.3.3-.5s0-.4 0-.6-.7-1.7-1-2.3c-.3-.6-.5-.5-.7-.5h-.6c-.2 0-.6.1-.9.4s-1.2 1.1-1.2 2.7 1.2 3.1 1.3 3.3c.2.2 2.3 3.5 5.6 4.9.8.3 1.4.5 1.9.7.8.3 1.5.2 2.1.1.6-.1 1.9-.8 2.2-1.5.3-.7.3-1.4.2-1.5-.1-.2-.3-.3-.6-.4z"/></svg></a>`);
if(C.email) $$("[data-mailto]").forEach(a=>{a.href=`mailto:${C.email}?subject=${encodeURIComponent(a.dataset.mailto)}`;a.hidden=false});
if(C.email) $$("[data-email]").forEach(e=>e.innerHTML=`<a href="mailto:${C.email}">${C.email}</a>`);
if(C.facebook) $$("[data-fb]").forEach(e=>{e.href=C.facebook;e.hidden=false});
if(C.instagram) $$("[data-ig]").forEach(e=>{e.href=C.instagram;e.hidden=false});

/* ---------- Slider ---------- */
const sl=$(".slider");
if(sl){
  const ss=$$(".slide",sl), dots=$(".dots",sl); let i=0,t;
  dots.innerHTML=ss.map((_,k)=>`<button aria-label="Destaque ${k+1}"></button>`).join("");
  const go=k=>{ss[i].classList.remove("on");dots.children[i].classList.remove("on");i=(k+ss.length)%ss.length;ss[i].classList.add("on");dots.children[i].classList.add("on")};
  [...dots.children].forEach((b,k)=>b.onclick=()=>{go(k);reset()});
  const reset=()=>{clearInterval(t);if(!matchMedia("(prefers-reduced-motion: reduce)").matches)t=setInterval(()=>go(i+1),6500)};
  $$("[data-art]",sl).forEach(el=>{const m=D.motas.find(x=>x.id===el.dataset.art);if(m)el.innerHTML=photo(m,"l")});
  go(0);reset();
}

/* ---------- Destaques na home ---------- */
const hl=$("#destaques");
if(hl) hl.innerHTML=hl.dataset.ids.split(",").map(id=>D.motas.find(x=>x.id===id)).filter(Boolean).map(x=>card(x)).join("");

/* ---------- Catálogo ---------- */
const cat=$("#catalogo");
if(cat){
  const q=new URLSearchParams(location.search);
  let fb=q.get("marca")||"all";
  const fCarta=$("#fCarta"),fDisp=$("#fDisp"),fSeg=$("#fSeg");
  if(q.get("seg")) fSeg.value=q.get("seg");
  const render=()=>{
    const c=fCarta.value,d=fDisp.value,s=fSeg.value;
    const list=D.motas.filter(x=>(fb==="all"||x.b===fb)&&(!c||x.carta===c)&&(!d||x.disp===d)&&(!s||x.seg===s));
    $("#count").textContent=`${list.length} modelo${list.length!==1?"s":""}${fb!=="all"?" "+fb:""}`;
    $$("#tabs button").forEach(b=>b.classList.toggle("on",b.dataset.b===fb));
    cat.innerHTML=list.length?D.segmentos.map(sg=>{const it=list.filter(x=>x.seg===sg);return it.length?`<div class="cat"><h2>${sg}<span>${it.length} modelo${it.length>1?"s":""}</span></h2><div class="grid">${it.map(x=>card(x)).join("")}</div></div>`:""}).join("")
      :`<div class="empty">Sem modelos com estes filtros.<br><a href="${ROOT}contactos.html?assunto=Proposta%20para%20mota%20nova" style="color:var(--red);font-weight:700">Peça-nos uma proposta</a> — encomendamos o modelo que procura.</div>`;
    const u=new URL(location);fb==="all"?u.searchParams.delete("marca"):u.searchParams.set("marca",fb);s?u.searchParams.set("seg",s):u.searchParams.delete("seg");history.replaceState(null,"",u);
  };
  $("#tabs").onclick=e=>{if(e.target.dataset.b){fb=e.target.dataset.b;render()}};
  [fCarta,fDisp,fSeg].forEach(s=>s.onchange=render);
  render();
}


/* ---------- Usadas ---------- */
const ug=$("#usados");
if(ug){
  const draw=list=>{ug.innerHTML=list.map(x=>{const d={...x,b:"",seg:"Naked"};return `<article class="card"><div class="ph">${photo(d)}<span class="lbl" style="background:var(--ant)">Usada</span>${(x.fotos||[]).length>1?`<span class="stock">${x.fotos.length} fotos</span>`:""}</div>
    <div class="bd"><h3><a href="${ROOT}usadas/${x.id}.html">${h(x.m)}</a></h3><ul><li>${h(x.tipo||"—")}</li><li>Ano: ${h(x.ano||"sob consulta")}</li><li>Km: ${x.km&&!isNaN(x.km)?Number(x.km).toLocaleString("pt-PT"):"sob consulta"}</li></ul>
    <div class="pr"><b>${x.preco&&!isNaN(x.preco)?Number(x.preco).toLocaleString("pt-PT")+" €":"Preço sob consulta"}</b><span class="more">Ver mais →</span></div></div></article>`}).join("")};
  draw(D.usados.slice(0,+(ug.dataset.max||99)));
}


})();
