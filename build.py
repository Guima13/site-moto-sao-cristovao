#!/usr/bin/env python3
"""Gera o site estático em dist/ a partir de src/.
Uso:  python3 build.py            -> versão final (dist/)
      PREVIEW=1 python3 build.py  -> versão de pré-visualização com aviso e noindex (dist-preview/)
"""
import json, os, shutil, html, re, hashlib
from pathlib import Path

ROOTDIR = Path(__file__).parent
SRC = ROOTDIR / "src"
CONTENT = ROOTDIR / "content"
PREVIEW = os.environ.get("PREVIEW") == "1"
OUT = ROOTDIR / os.environ.get("OUT_DIR", "dist-preview" if PREVIEW else "dist")
SITE = "https://www.motosaocristovao.pt/"
E = html.escape

# ---------- Conteúdos (editáveis no painel /admin) ----------
M = json.loads((SRC / "data/marcas.json").read_text(encoding="utf-8"))
INFO = json.loads((CONTENT / "site.json").read_text(encoding="utf-8"))
TEL = INFO["telefone"]; TEL_LINK = "+351" + re.sub(r"\D", "", TEL); EMAIL = INFO["email"]
DISP = {"Em stand": "stand", "Por encomenda": "enc", "Vendida": "vend"}
def load(folder):
    out = []
    for f in sorted((CONTENT / folder).glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8")); d["id"] = f.stem; out.append(d)
    return out
BORDER = {b: i for i, b in enumerate(M["marcas"])}
SORDER = {s: i for i, s in enumerate(M["segmentos"])}
MOTAS = [m for m in load("motas") if m.get("publicado", True) and m.get("marca") in M["marcas"]]
MOTAS.sort(key=lambda m: (SORDER.get(m.get("segmento"), 99), BORDER[m["marca"]], -(m.get("cilindrada") or 0), m["modelo"]))
USADAS = [u for u in load("usadas") if u.get("publicado", True) and not u.get("vendida")]
USADAS.sort(key=lambda u: (-(u.get("ano") or 0), u["modelo"]))

# ---------- Fotos: otimização automática (WebP, 1600 px e 640 px) ----------
try:
    from PIL import Image, ImageOps
except ImportError:
    Image = None
IMG_OUT = OUT / "assets/img"
if OUT.exists(): shutil.rmtree(OUT)
(OUT / "motas").mkdir(parents=True); (OUT / "usadas").mkdir(parents=True)
shutil.copytree(SRC / "assets", OUT / "assets", ignore=shutil.ignore_patterns("uploads"))
if (SRC / "admin").exists(): shutil.copytree(SRC / "admin", OUT / "admin")
_cache = {}
def foto(path):
    """Recebe '/assets/fotos/x.jpg' e devolve {'l': grande, 's': pequena} já otimizadas."""
    if not path: return None
    rel = path.lstrip("/")
    if rel in _cache: return _cache[rel]
    src = SRC / rel
    if not src.exists():
        print("  ! foto em falta:", rel); _cache[rel] = None; return None
    IMG_OUT.mkdir(parents=True, exist_ok=True)
    h = hashlib.md5(src.read_bytes()).hexdigest()[:8]
    stem = re.sub(r"[^a-z0-9-]+", "-", src.stem.lower()).strip("-")[:60] or "foto"
    res = {}
    for key, w in (("l", 1600), ("s", 640)):
        name = f"{stem}-{h}-{w}.webp"
        dst = IMG_OUT / name
        if Image:
            if not dst.exists():
                im = ImageOps.exif_transpose(Image.open(src))
                im = im.convert("RGBA") if im.mode in ("RGBA", "LA", "P") else im.convert("RGB")
                if im.width > w: im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
                im.save(dst, "WEBP", quality=80, method=4)
            res[key] = "assets/img/" + name
        else:
            res[key] = rel
    _cache[rel] = res; return res

def prep_mota(m):
    fotos = [f for f in (foto(p) for p in m.get("fotos", [])) if f]
    return {"id": m["id"], "b": m["marca"], "m": m["modelo"], "seg": m.get("segmento", ""), "cc": m.get("cilindrada"),
            "carta": None if m.get("carta") in (None, "", "Consultar") else m["carta"], "kw": m.get("potencia_kw"), "cv": m.get("potencia_cv"),
            "peso": m.get("peso"), "dep": m.get("deposito"), "banco": m.get("altura_banco"),
            "disp": DISP.get(m.get("disponibilidade"), "enc"), "preco": m.get("preco"), "extra": m.get("transporte_legalizacao"),
            "desc": m.get("descricao", ""), "fonte": m.get("link_oficial") or "", "destaque": bool(m.get("destaque")), "fotos": fotos}
def prep_usada(u):
    fotos = [f for f in (foto(p) for p in u.get("fotos", [])) if f]
    return {"id": u["id"], "m": u["modelo"], "tipo": u.get("tipo", ""), "ano": u.get("ano"), "km": u.get("quilometros"),
            "preco": u.get("preco"), "desc": u.get("descricao", ""), "fotos": fotos}
CAT = {"segmentos": M["segmentos"], "marcas": M["marcas"],
       "motas": [prep_mota(m) for m in MOTAS], "usados": [prep_usada(u) for u in USADAS]}
for x in CAT["motas"]: x["img"] = x["fotos"][0]["l"] if x["fotos"] else ""
STAND = "assets/fotos/stand.jpg"

DEALER = {
  "@context": "https://schema.org", "@type": "MotorcycleDealer",
  "name": "Moto S. Cristóvão", "foundingDate": "1943", "url": SITE,
  "telephone": TEL_LINK, "email": EMAIL,
  "image": SITE + STAND,
  "openingHours": ["Mo-Fr 09:00-20:00", "Sa 09:00-17:00"],
  "address": {"@type": "PostalAddress", "streetAddress": INFO["morada"], "addressLocality": "Rio Mau, Vila do Conde",
              "postalCode": "4480-430", "addressCountry": "PT"},
  "geo": {"@type": "GeoCoordinates", "latitude": 41.4018, "longitude": -8.682547},
  "brand": [{"@type": "Brand", "name": b} for b in CAT["marcas"]]
}
CSP = ("default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
       "font-src https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self'; "
       "frame-src https://maps.google.com https://www.google.com; form-action 'none'; "
       "base-uri 'self'; object-src 'none'; upgrade-insecure-requests")

def layout(page, title, desc, body, root="", path="", extra_ld=None, og_img=SITE + "assets/fotos/stand.jpg"):
    ld = [DEALER] + ([extra_ld] if extra_ld else [])
    nav = lambda p, href, label: f'<a href="{root}{href}" data-p="{p}">{label}</a>'
    robots = '<meta name="robots" content="noindex,nofollow">' if PREVIEW else '<meta name="robots" content="index,follow">'
    banner = '<div class="preview">Proposta de redesign — pré-visualização, não é o site oficial da Moto S. Cristóvão.</div>' if PREVIEW else ""
    return f"""<!DOCTYPE html>
<html lang="pt-PT">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
{robots}
<link rel="canonical" href="{SITE}{path}">
<meta property="og:type" content="website"><meta property="og:locale" content="pt_PT">
<meta property="og:site_name" content="Moto S. Cristóvão">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{SITE}{path}"><meta property="og:image" content="{og_img}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#2b2f34">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' fill='%23d71f26'/%3E%3Ctext x='16' y='23' font-size='17' font-family='Arial' font-weight='bold' font-style='italic' fill='white' text-anchor='middle'%3EMS%3C/text%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&family=Open+Sans:wght@400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}assets/style.css">
<script type="application/ld+json">{json.dumps(ld if len(ld)>1 else ld[0], ensure_ascii=False)}</script>
</head>
<body data-page="{page}" data-root="{root}">
<a class="skip" href="#conteudo">Saltar para o conteúdo</a>
{banner}
<div class="util"><div class="wrap">
  <div class="l"><span>☎ <a href="tel:{TEL_LINK}">{TEL}</a></span><span>Rua São Cristóvão 1146, Rio Mau — Vila do Conde</span><span>{INFO["horario_curto"]}</span></div>
  <div class="r">{f'<a href="{E(INFO["facebook"])}" target="_blank" rel="noopener">Facebook</a>' if INFO.get("facebook") else ""}{f'<a href="{E(INFO["instagram"])}" target="_blank" rel="noopener">Instagram</a>' if INFO.get("instagram") else ""}</div>
</div></div>
<header class="site"><div class="wrap hd">
  <a href="{root}index.html" class="logo"><span class="m">MOTO</span><span><span class="s">S. Cristóvão</span><small>Desde 1943</small></span></a>
  <nav class="main" aria-label="Menu principal"><ul>
    <li>{nav("inicio","index.html","Início")}</li>
    <li>{nav("novas","novas.html","Motas")}
      <ul class="sub">
        <li><a href="{root}novas.html">Motas novas</a></li>
        <li><a href="{root}usadas.html">Motas usadas</a></li>
        <li><a href="{root}novas.html?seg=Moto%204%20%2F%20UTV">Moto 4 / UTV</a></li>
      </ul></li>
    <li>{nav("oficina","oficina.html","Oficina")}</li>
    <li>{nav("empresa","empresa.html","Quem somos")}</li>
    <li>{nav("contactos","contactos.html","Contactos")}</li>
  </ul></nav>
  <button class="burger" aria-label="Abrir menu" aria-expanded="false">☰</button>
</div></header>
<main id="conteudo">
{body}
</main>
<footer class="site">
  <div class="wrap ft">
    <div><h2>Moto S. Cristóvão</h2><p>Comércio de motas e assistência técnica desde 1943.<br>Rua São Cristóvão 1146<br>4480-430 Rio Mau, Vila do Conde<br>☎ <a href="tel:{TEL_LINK}">{TEL}</a><br><a href="mailto:{EMAIL}">{EMAIL}</a><br>{INFO["horario_curto"]}</p></div>
    <div><h2>Marcas</h2><ul>{"".join(f'<li><a href="{root}novas.html?marca={b}">{b}</a></li>' for b in CAT["marcas"])}</ul></div>
    <div><h2>Motas</h2><ul><li><a href="{root}novas.html">Novas</a></li><li><a href="{root}usadas.html">Usadas</a></li><li><a href="{root}oficina.html">Oficina e acessórios</a></li></ul></div>
    <div><h2>Informação</h2><ul><li><a href="{root}empresa.html">Quem somos</a></li><li><a href="{root}contactos.html">Contactos</a></li><li><a href="{root}privacidade.html">Política de Privacidade</a></li></ul><a class="lr" href="https://www.livroreclamacoes.pt" target="_blank" rel="noopener">Livro de Reclamações</a></div>
  </div>
  <div class="fb"><span>© 2026 Moto S. Cristóvão. Todos os direitos reservados.</span><span>Imagens meramente ilustrativas. Preços e disponibilidade sob consulta.</span></div>
</footer>
<script src="{root}assets/config.js"></script>
<script src="{root}assets/data.js"></script>
<script src="{root}assets/app.js"></script>
</body>
</html>"""

def phead(title, sub="", crumb=""):
    return f'<div class="phead"><div class="wrap"><div class="crumb"><a href="index.html">Início</a>{crumb}</div><h1>{title}</h1>{f"<p>{sub}</p>" if sub else ""}</div></div>'


BRANDS = '<div class="brands"><div class="wrap">' + "".join(
    f'<a class="bcard" href="novas.html?marca={b}" aria-label="Ver motas {b}">' + (f'<img class="blogo" src="{v["logo"]}" alt="{b}" height="36">' if v.get("logo") else f'<span class="wordmark">{b}</span>') + f'<span class="t">{t}</span></a>'
    for b, v, t in [(k, CAT["marcas"][k], M["texto_marcas"].get(k, "")) for k in CAT["marcas"]]) + '</div></div>'

ICON = {
 "tool":'<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3 18l3 3 6.3-6.3a4 4 0 0 0 5.4-5.4l-2.5 2.5-2.4-.6-.6-2.4z"/></svg>',
 "tyre":'<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4"/></svg>',
 "helmet":'<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><path d="M4 15a8 8 0 0 1 16 0v3H4z"/><path d="M12 11h8"/></svg>',
}

pages = {}
DEST = [m["id"] for m in CAT["motas"] if m["destaque"]][:4] or [m["id"] for m in CAT["motas"]][:4]
_art = [m["id"] for m in CAT["motas"] if m["destaque"] and m["fotos"]] + [m["id"] for m in CAT["motas"] if m["fotos"]]
ART = [(_art or [""])[i % max(len(_art), 1)] for i in range(3)]

pages["index.html"] = layout("inicio", "Moto S. Cristóvão | Concessionário Keeway, Kymco, Benelli e Linhai em Vila do Conde",
 "Moto S. Cristóvão, desde 1943 em Rio Mau, Vila do Conde. Motas, scooters e moto 4 novas Benelli, Keeway, Kymco e Linhai. Usadas, oficina, pneus e acessórios.", f"""
<div class="slider" aria-roledescription="carrossel">
  <div class="slide" style="background-image:url('assets/fotos/stand.jpg')"><div class="wrap">
    <div><span class="tag">Concessionário oficial · Vila do Conde</span><h1>Encontre aqui a sua próxima mota</h1>
    <p>Motas, scooters e moto 4 novas Benelli, Keeway, Kymco e Linhai. Usadas, oficina própria, pneus e acessórios — há mais de 80 anos em Rio Mau.</p>
    <div class="ctas"><a href="novas.html" class="btn">Ver motas novas</a><a href="usadas.html" class="btn btn-white">Ver usadas</a></div></div>
    <div class="art" data-art="{ART[0]}"></div></div></div>
  <div class="slide"><div class="wrap">
    <div><span class="tag">Por encomenda</span><h2>Não temos o modelo em stand? Encomendamos</h2>
    <p>Toda a gama Keeway, Kymco, Benelli e Linhai está disponível por encomenda. Fale connosco para saber prazos e condições.</p>
    <div class="ctas"><a href="novas.html" class="btn">Ver gama completa</a><a href="tel:{TEL_LINK}" class="btn btn-white">Ligar {TEL}</a></div></div>
    <div class="art" data-art="{ART[1]}"></div></div></div>
  <div class="slide"><div class="wrap">
    <div><span class="tag">Oficina</span><h2>A sua mota em boas mãos</h2>
    <p>Revisões, reparações, pneus e acessórios para motas, scooters e moto 4 de todas as marcas.</p>
    <div class="ctas"><a href="tel:{TEL_LINK}" class="btn">Marcar revisão</a><a href="oficina.html" class="btn btn-white">Saber mais</a></div></div>
    <div class="art" data-art="{ART[2]}"></div></div></div>
  <div class="dots"></div>
</div>
{BRANDS}
<section><div class="wrap">
  <div class="title"><small>Destaques</small><h2>Modelos em destaque</h2><p>Uma seleção da nossa gama. Veja todos os modelos em stand e por encomenda.</p></div>
  <div class="grid" id="destaques" data-ids="{",".join(DEST)}"></div>
  <p style="margin-top:26px"><a class="btn btn-line" href="novas.html">Ver todas as motas novas</a></p>
</div></section>
<div class="promo"><div class="wrap"><div><h2>Financiamento e retoma</h2><p>Temos campanhas de financiamento e aceitamos a sua mota na troca. Consulte-nos.</p></div><a href="tel:{TEL_LINK}" class="btn btn-white">Ligar {TEL}</a></div></div>
<section style="background:var(--soft)"><div class="wrap">
  <div class="title"><small>Motas usadas</small><h2>Cada mota tem a sua história</h2><p>Usadas revistas na nossa oficina.</p></div>
  <div class="grid" id="usados" data-max="4"></div>
  <p style="margin-top:26px"><a class="btn btn-line" href="usadas.html">Ver todas as usadas</a></p>
</div></section>
<section><div class="wrap">
  <div class="title"><small>Pós-venda</small><h2>Oficina, pneus e acessórios</h2></div>
  <div class="tiles">
    <div class="tile">{ICON["tool"]}<div><h3>Oficina</h3><p>Revisões, manutenção e reparação de todas as marcas.</p><a href="contactos.html">Marcar revisão</a></div></div>
    <div class="tile">{ICON["tyre"]}<div><h3>Pneus</h3><p>Venda e montagem de pneus para motas, scooters e moto 4.</p><a href="contactos.html">Pedir orçamento</a></div></div>
    <div class="tile">{ICON["helmet"]}<div><h3>Acessórios</h3><p>Capacetes, vestuário, malas e equipamento. Também agro e jardim.</p><a href="oficina.html">Saber mais</a></div></div>
  </div>
</div></section>
<section class="about" style="background:var(--soft)"><div class="wrap">
  <div class="img" role="img" aria-label="Stand Moto S. Cristóvão"></div>
  <div><div class="title" style="margin-bottom:18px"><small>Quem somos</small><h2>Desde 1943 ao seu lado</h2></div>
  <p>Fundada em 1943, a Moto S. Cristóvão dedica-se ao comércio de motas e à assistência técnica em Rio Mau, Vila do Conde. Mais de oito décadas depois, somos concessionário oficial Keeway, Kymco, Benelli e Linhai.</p>
  <a href="empresa.html" class="btn btn-line">Conhecer a empresa</a></div>
</div></section>
<section class="reviews"><div class="wrap"><div class="revbox"><div><div class="g">O que dizem os nossos clientes</div><p style="color:var(--grey)">Leia as avaliações dos nossos clientes no Google.</p></div><a class="btn" target="_blank" rel="noopener" href="https://www.google.com/maps/search/?api=1&query=Moto+S.+Crist%C3%B3v%C3%A3o+Rio+Mau+Vila+do+Conde">Ver avaliações no Google</a></div></div></section>
""")

pages["novas.html"] = layout("novas", "Motas novas Keeway, Kymco, Benelli e Linhai | Moto S. Cristóvão",
 "Gama de motas, scooters e moto 4 novas Keeway, Kymco, Benelli e Linhai em Vila do Conde. Modelos em stand e por encomenda.",
 phead("Motas novas", "Gama oficial das marcas que representamos. Os modelos que não temos em stand podem ser encomendados.", " › Motas novas") + f"""
<section style="padding-top:34px"><div class="wrap">
  <div class="bar">
    <div class="tabs" id="tabs" role="group" aria-label="Marca"><button data-b="all">Todas</button>{"".join(f'<button data-b="{b}">{b}</button>' for b in CAT["marcas"])}</div>
    <div class="sels">
      <select id="fSeg" aria-label="Segmento"><option value="">Todos os segmentos</option>{"".join(f'<option>{s}</option>' for s in CAT["segmentos"])}</select>
      <select id="fCarta" aria-label="Carta"><option value="">Qualquer carta</option><option value="AM">AM / B (50 cc)</option><option value="A1">A1 / B (até 125 cc)</option><option value="A2">A2</option><option value="A">A</option></select>
      <select id="fDisp" aria-label="Disponibilidade"><option value="">Stand e encomenda</option><option value="stand">Em stand</option><option value="enc">Por encomenda</option></select>
    </div>
  </div>
  <p class="count" id="count" aria-live="polite"></p>
  <div id="catalogo"></div>
  <p class="small" style="font-size:.8rem;color:var(--grey);margin-top:24px">*A carta B permite conduzir motociclos até 125 cc, nas condições previstas na lei.</p>
</div></section>""", path="novas.html")


pages["usadas.html"] = layout("novas", "Motas usadas em Vila do Conde | Moto S. Cristóvão", "Motas usadas revistas na oficina da Moto S. Cristóvão, em Rio Mau, Vila do Conde. Peça mais fotografias, quilometragem e preço.",
 phead("Motas usadas", "Cada mota tem a sua história. Usadas revistas na nossa oficina — contacte-nos para mais fotografias, quilometragem e preço.", " › Motas usadas") + """
<section style="padding-top:34px"><div class="wrap"><div class="grid" id="usados"></div>
<div class="revbox" style="margin-top:34px"><div><div class="g">Quer vender ou trocar a sua mota?</div><p style="color:var(--grey)">Avaliamos a sua mota usada para retoma na compra de uma nova.</p></div><a class="btn" href="contactos.html">Pedir avaliação</a></div>
</div></section>""", path="usadas.html")


pages["oficina.html"] = layout("oficina", "Oficina, pneus e acessórios | Moto S. Cristóvão", "Oficina de motas em Vila do Conde: revisões, reparações, pneus e acessórios para motas, scooters e moto 4 de todas as marcas.",
 phead("Oficina, pneus e acessórios", "Pós-venda completo para motas, scooters e moto 4 de todas as marcas.", " › Oficina") + f"""
<section style="padding-top:40px"><div class="wrap">
  <div class="tiles">
    <div class="tile">{ICON["tool"]}<div><h2 class="osw" style="font-size:1.6rem;margin-bottom:6px">Assistência técnica</h2><p>Revisões periódicas, manutenção e reparações. Diagnóstico e preparação para inspeção.</p><a href="contactos.html">Contactar</a></div></div>
    <div class="tile">{ICON["tyre"]}<div><h2 class="osw" style="font-size:1.6rem;margin-bottom:6px">Pneus</h2><p>Venda e montagem de pneus para motas, scooters e moto 4. Peça orçamento para a sua medida.</p><a href="contactos.html">Pedir orçamento</a></div></div>
    <div class="tile">{ICON["helmet"]}<div><h2 class="osw" style="font-size:1.6rem;margin-bottom:6px">Acessórios e equipamento</h2><p>Capacetes, vestuário, luvas, malas e acessórios. Também máquinas e equipamentos agro e jardim.</p><a href="contactos.html">Pedir informação</a></div></div>
  </div>
</div></section>""", path="oficina.html")

pages["empresa.html"] = layout("empresa", "Quem somos | Moto S. Cristóvão — desde 1943", "A Moto S. Cristóvão vende motas e presta assistência técnica em Rio Mau, Vila do Conde, desde 1943. Concessionário Keeway, Kymco, Benelli e Linhai.",
 phead("Quem somos", "Desde 1943 ao serviço dos motociclistas de Vila do Conde.", " › Quem somos") + """
<section class="about"><div class="wrap">
  <div class="img" role="img" aria-label="Stand Moto S. Cristóvão"></div>
  <div><div class="title" style="margin-bottom:18px"><small>A nossa história</small><h2>Mais de 80 anos sobre duas rodas</h2></div>
  <p>Fundada em 1943, a Moto S. Cristóvão é uma empresa de comércio de motas e assistência técnica sediada em Rio Mau, Vila do Conde.</p>
  <p>Ao longo de várias gerações construímos uma vasta experiência no setor e tornámo-nos uma referência na região. Hoje somos concessionário oficial Keeway, Kymco, Benelli e Linhai, com venda de novos e usados, oficina própria, pneus e acessórios.</p>
  <div class="values"><div><h3>Experiência</h3><p>Mais de 80 anos no setor das duas rodas.</p></div><div><h3>Confiança</h3><p>Venda e oficina no mesmo sítio.</p></div><div><h3>Proximidade</h3><p>Aconselhamos a mota certa para si.</p></div></div></div>
</div></section>""" + BRANDS, path="empresa.html")

pages["contactos.html"] = layout("contactos", "Contactos | Moto S. Cristóvão, Rio Mau — Vila do Conde", "Contacte a Moto S. Cristóvão: Rua São Cristóvão 1146, 4480-430 Rio Mau, Vila do Conde. Telefone {TEL}.",
 f"""<section class="contact"><div class="wrap g">
  <div>
    <div class="title light"><small>Contactos</small><h1 class="osw" style="font-size:clamp(1.8rem,3.3vw,2.6rem)">Visite o nosso stand</h1><p>Estamos em Rio Mau, Vila do Conde.</p></div>
    <div class="ci">
      <div><small>Morada</small><b>Rua São Cristóvão 1146<br>4480-430 Rio Mau, Vila do Conde</b></div>
      <div><small>Telefone</small><b><a href="tel:{TEL_LINK}">{TEL}</a></b> <span style="font-size:.78rem;color:#b3b8bd">(chamada para a rede fixa nacional)</span></div>
      <div><small>Email</small><b><a href="mailto:{EMAIL}">{EMAIL}</a></b></div>
      <div><small>Horário</small><b>{"<br>".join(E(l) for l in INFO["horario"])}</b></div>
    </div>
    <div class="map"><iframe loading="lazy" title="Mapa: localização da Moto S. Cristóvão" src="https://maps.google.com/maps?q=41.4018,-8.682547&z=15&output=embed"></iframe></div>
  </div>
  <div class="f" style="background:#fff;color:var(--ink);padding:30px;display:grid;gap:14px;align-content:start;align-self:start">
    <h2 class="osw" style="font-size:1.55rem;color:var(--ant)">Fale connosco</h2>
    <p style="color:#45494e">Quer saber se um modelo está em stand, encomendar uma mota, marcar uma revisão ou ver uma usada? Ligue-nos ou passe pelo stand.</p>
    <a class="btn" href="tel:{TEL_LINK}">Ligar {TEL}</a>
    <a class="btn btn-line" data-mailto="Pedido de informação" href="#" hidden>Enviar email</a>
    <a class="btn btn-line" target="_blank" rel="noopener" href="https://www.google.com/maps/dir/?api=1&destination=41.4018,-8.682547">Como chegar</a>
  </div>
</div></section>""", path="contactos.html")

pages["privacidade.html"] = layout("", "Política de Privacidade | Moto S. Cristóvão", "Política de Privacidade e de cookies do site da Moto S. Cristóvão.",
 phead("Política de Privacidade", "", " › Privacidade") + f"""
<section><div class="wrap prose">
<h2>Responsável pelo tratamento</h2><p>Moto S. Cristóvão, Rua São Cristóvão 1146, 4480-430 Rio Mau, Vila do Conde. Telefone {TEL}. Email: {EMAIL}.</p>
<h2>Dados pessoais</h2><p>Este site não tem formulários nem áreas de cliente e não recolhe dados pessoais. Se nos contactar por telefone ou email, os seus dados são usados apenas para responder ao seu pedido e não são partilhados com terceiros sem o seu acordo.</p>
<h2>Os seus direitos</h2><p>Pode pedir acesso, retificação ou apagamento dos seus dados contactando-nos. Pode também apresentar reclamação à CNPD (www.cnpd.pt).</p>
<h2>Cookies</h2><p>O site usa armazenamento local apenas para guardar a aceitação do aviso de cookies. O mapa incorporado é fornecido pelo Google e pode usar cookies próprios.</p>
</div></section>""", path="privacidade.html")

pages["404.html"] = layout("", "Página não encontrada | Moto S. Cristóvão", "Página não encontrada.",
 phead("Página não encontrada", "A página que procura não existe ou foi movida.") + '<section><div class="wrap"><a class="btn" href="index.html">Voltar ao início</a> <a class="btn btn-line" href="novas.html">Ver motas novas</a></div></section>', path="404.html")

# Páginas de modelo
for x in CAT["motas"]:
    b = CAT["marcas"][x["b"]]
    same = [m for m in CAT["motas"] if m["seg"] == x["seg"] and m["id"] != x["id"]][:4] or [m for m in CAT["motas"] if m["b"] == x["b"] and m["id"] != x["id"]][:4] or [m for m in CAT["motas"] if m["id"] != x["id"]][:4]
    n = lambda v: str(v).replace(".", ",")
    pot = (f'{n(x["kw"])} kW ({n(x["cv"])} cv)' if x.get("kw") else f'{n(x["cv"])} cv') if x.get("cv") or x.get("kw") else None
    rows = [("Marca", x["b"]), ("Segmento", x["seg"]), ("Cilindrada", f'{x["cc"]} cc' if x["cc"] else None), ("Potência", pot),
            ("Peso", f'{x["peso"]} kg' if x.get("peso") else None), ("Depósito", f'{n(x["dep"])} L' if x.get("dep") else None),
            ("Altura do banco", f'{x["banco"]} mm' if x.get("banco") else None),
            ("Carta de condução", {"AM":"AM / B","A1":"A1 / B*","A2":"A2","A":"A"}.get(x["carta"], "Consultar")),
            ("Disponibilidade", "Em stand" if x["disp"] == "stand" else "Por encomenda")]
    rows = [r for r in rows if r[1]]
    name = f'{x["b"]} {x["m"]}'
    eurf = lambda v: f'{v:,} €'.replace(",", " ")
    price = f'PVP {eurf(x["preco"])}' if x["preco"] else "Preço sob consulta"
    price_note = ((f'+ {eurf(x["extra"])} de transporte e legalização. ' if x.get("extra") else "") +
                  ("Preço de venda recomendado pela marca, IVA incluído. Confirme o preço final e campanhas em vigor no stand." if x["preco"] else "Contacte-nos para saber o preço e as condições."))
    ld = {"@context":"https://schema.org","@type":"Product","name":name,"brand":{"@type":"Brand","name":x["b"]},"category":x["seg"],"description":x["desc"]}
    if x["img"]: ld["image"] = SITE + x["img"]
    if x["preco"]: ld["offers"] = {"@type":"Offer","price":x["preco"],"priceCurrency":"EUR","seller":{"@type":"MotorcycleDealer","name":"Moto S. Cristóvão"}}
    q = lambda a: f'../contactos.html?assunto={a}&modelo={name.replace(" ","%20")}'
    body = f"""<div class="phead" style="padding:18px 0"><div class="wrap"><div class="crumb" style="margin:0"><a href="../index.html">Início</a> › <a href="../novas.html">Motas novas</a> › <a href="../novas.html?marca={x["b"]}">{x["b"]}</a> › {E(x["m"])}</div></div></div>
<section style="padding-top:40px"><div class="wrap model">
  <div><div class="gallery" id="gal" data-kind="mota" data-id="{x["id"]}"></div>{f'<p class="note">Imagens do fabricante — cores e equipamento podem variar. Mais informação no <a style="text-decoration:underline" href="{E(x["fonte"])}" target="_blank" rel="noopener">site oficial {x["b"]}</a>.</p>' if x.get("fonte") else ""}</div>
  <div class="minfo">
    <span class="chip" style="background:{b["cor"]}">{x["b"]}</span>
    <h1>{E(x["m"])}</h1>
    <p class="lead">{E(x["desc"])}</p>
    <div class="price">{price}</div><p class="small">{price_note}</p>
    <table class="specs">{"".join(f'<tr><th scope="row">{k}</th><td><b>{v}</b></td></tr>' for k,v in rows)}</table>
    <p style="margin-bottom:12px;color:#45494e">{"Disponível no nosso stand — venha vê-la." if x["disp"]=="stand" else "Disponível por encomenda — contacte-nos para prazos e condições."}</p>
    <div class="acts">
      <a class="btn" href="tel:{TEL_LINK}">Ligar {TEL}</a>
      <a class="btn btn-line" data-mailto="Pedido de informação: {E(name)}" href="#" hidden>Pedir informação por email</a>
      <a class="btn btn-line" href="../contactos.html">Ver contactos</a>
    </div>
    {'<p class="small" style="margin-top:10px">*A carta B permite conduzir motociclos até 125 cc, nas condições previstas na lei.</p>' if x["carta"]=="A1" else ""}{'<p class="small" style="margin-top:10px">A carta B permite conduzir ciclomotores de 50 cc.</p>' if x["carta"]=="AM" else ""}
  </div>
</div></section>
<section style="background:var(--soft)"><div class="wrap">
  <div class="title"><small>{x["seg"]}</small><h2>Outros modelos que pode gostar</h2></div>
  <div class="grid" id="destaques" data-ids="{",".join(m["id"] for m in same)}"></div>
</div></section>"""
    pages[f'motas/{x["id"]}.html'] = layout("novas", f'{name} | Moto S. Cristóvão, Vila do Conde',
        f'{name} ({x["seg"]}{", "+str(x["cc"])+" cc" if x["cc"] else ""}{", PVP "+eurf(x["preco"]) if x["preco"] else ""}) na Moto S. Cristóvão, concessionário {x["b"]} em Vila do Conde. Em stand ou por encomenda.',
        body, root="../", path=f'motas/{x["id"]}.html', extra_ld=ld, og_img=(SITE + x["img"]) if x["img"] else SITE + "assets/fotos/stand.jpg")

# Páginas das usadas
for u in CAT["usados"]:
    eurf = lambda v: f'{v:,} €'.replace(",", " ")
    rows = [("Tipo", u["tipo"]), ("Ano", u["ano"]), ("Quilómetros", f'{u["km"]:,} km'.replace(",", " ") if isinstance(u["km"], (int, float)) else u["km"])]
    rows = [r for r in rows if r[1]]
    body = f"""<div class="phead" style="padding:18px 0"><div class="wrap"><div class="crumb" style="margin:0"><a href="../index.html">Início</a> › <a href="../usadas.html">Motas usadas</a> › {E(u["m"])}</div></div></div>
<section style="padding-top:40px"><div class="wrap model">
  <div class="gallery" id="gal" data-kind="usada" data-id="{u["id"]}"></div>
  <div class="minfo">
    <span class="chip" style="background:var(--ant)">Usada</span>
    <h1>{E(u["m"])}</h1>
    {f'<p class="lead">{E(u["desc"])}</p>' if u["desc"] else ""}
    <div class="price">{eurf(u["preco"]) if isinstance(u["preco"], (int, float)) and u["preco"] else "Preço sob consulta"}</div>
    {f'<table class="specs">{"".join(f"<tr><th scope=row>{k}</th><td><b>{E(str(v))}</b></td></tr>" for k, v in rows)}</table>' if rows else ""}
    <p style="margin:14px 0 12px;color:#45494e">Revista na nossa oficina. Venha vê-la ao stand ou ligue-nos para mais informações.</p>
    <div class="acts">
      <a class="btn" href="tel:{TEL_LINK}">Ligar {TEL}</a>
      <a class="btn btn-line" data-mailto="Mota usada: {E(u["m"])}" href="#" hidden>Pedir informação por email</a>
      <a class="btn btn-line" href="../usadas.html">Ver outras usadas</a>
    </div>
  </div>
</div></section>"""
    pages[f'usadas/{u["id"]}.html'] = layout("novas", f'{u["m"]} usada | Moto S. Cristóvão, Vila do Conde',
        f'{u["m"]} usada à venda na Moto S. Cristóvão, Rio Mau, Vila do Conde. Revista na nossa oficina.', body, root="../",
        path=f'usadas/{u["id"]}.html', og_img=SITE + (u["fotos"][0]["l"] if u["fotos"] else STAND))

# Escrita
data = {k: CAT[k] for k in ("segmentos", "marcas", "motas", "usados")}
(OUT / "assets/config.js").write_text("window.CFG=" + json.dumps({"email": EMAIL, "whatsapp": (lambda w: ("351" + w) if len(w) == 9 else w)(re.sub(r"\\D", "", INFO.get("whatsapp") or "")), "usadosCSV": ""}, ensure_ascii=False) + ";", encoding="utf-8")
(OUT / "assets/data.js").write_text("window.DATA=" + json.dumps(data, ensure_ascii=False) + ";", encoding="utf-8")
for p, h in pages.items():
    # páginas da raiz: links relativos já estão corretos; fixar o form "privacidade.html" nas subpastas
    if p.startswith(("motas/", "usadas/")): h = h.replace('href="privacidade.html"', 'href="../privacidade.html"')
    (OUT / p).write_text(h, encoding="utf-8")
HDR = {"X-Content-Type-Options": "nosniff", "X-Frame-Options": "DENY",
       "Referrer-Policy": "strict-origin-when-cross-origin", "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=()",
       "Strict-Transport-Security": "max-age=31536000; includeSubDomains"}
(OUT / "_headers").write_text("/*\n" + "".join(f"  {k}: {v}\n" for k, v in HDR.items()))   # Netlify
(OUT / "vercel.json").write_text(json.dumps({"headers": [{"source": "/(.*)", "headers": [{"key": k, "value": v} for k, v in HDR.items()]}]}, indent=2))
(OUT / "robots.txt").write_text(("User-agent: *\nDisallow: /\n" if PREVIEW else f"User-agent: *\nAllow: /\nSitemap: {SITE}sitemap.xml\n"))
urls = [p for p in pages if p != "404.html"]
(OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    "".join(f"  <url><loc>{SITE}{'' if p=='index.html' else p}</loc></url>\n" for p in urls) + "</urlset>\n")
print(f"{len(pages)} páginas geradas em {OUT}")
