#!/usr/bin/env python3
"""Gera o blog da Curtamax.

Uso: python3 _blog/build_blog.py  (rodar na raiz do site)
- Cada artigo fica em _blog/posts/<slug>.html, com um bloco <!--meta ... --> no topo.
- O script gera blog/index.html, blog/<slug>/index.html, blog/blog.css e sitemap.xml.
- Agendamento: só entram no site os artigos com `date` igual ou anterior a hoje
  (horário de Brasília). O Netlify roda este script a cada deploy, e uma função
  agendada (netlify/functions/publicar-blog.mjs) dispara um deploy toda segunda às 9h.
- Para testar uma data: BLOG_TODAY=2026-11-30 python3 _blog/build_blog.py
"""
import html, os, re, shutil
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_blog"
OUT = ROOT / "blog"
SITE = "https://curtamax.netlify.app"
WA = "https://wa.me/5511998270485?text="
IG = "https://www.instagram.com/curtamax.ai/"

SYM = (SRC / "sym.svg").read_text()
WAFAB = (SRC / "wafab.html").read_text()
NL = (SRC / "nl_section.html").read_text()
PRIV = (SRC / "privacidade_body.html").read_text()
WA_ICON = re.search(r"<svg.*?</svg>", WAFAB, re.S).group(0).replace(' aria-hidden="true"', "")


def parse(p):
    raw = p.read_text()
    m = re.match(r"\s*<!--meta\n(.*?)-->\n", raw, re.S)
    meta = dict(l.split(": ", 1) for l in m.group(1).strip().splitlines())
    meta["body"] = raw[m.end():]
    return meta


def head(title, desc, url, image, depth, kind="website"):
    up = "../" * depth
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="{kind}">
<meta property="og:site_name" content="Curtamax arttech">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#031417">
<link rel="preload" href="{up}assets/fonts/Museo700-Regular.woff" as="font" type="font/woff" crossorigin>
<link rel="stylesheet" href="{up}blog/blog.css">
<link rel="stylesheet" href="{up}assets/newsletter.css">
<script src="{up}assets/newsletter.js" defer></script>
</head>
<body>
<header class="nav">
  <a class="brand" href="{up}" aria-label="Curtamax arttech, início">{SYM}<span class="wm">CURTA<b>MAX</b><small>arttech</small></span></a>
  <nav class="links">
    <a href="{up}">Site</a><a class="opt" href="{up}#portfolio">Portfólio</a><a class="on" href="{up}blog/">Blog</a><a href="{up}#contato">Contato</a>
  </nav>
</header>
<main>
"""


def foot():
    return f"""</main>
{WAFAB}
<footer class="foot">
  <div class="fl"><span class="fbrand">{SYM}<span class="wm">CURTA<b>MAX</b><small>arttech</small></span></span><span>© <span id="yr">2026</span> Curtamax arttech · Criatividade com propósito. Tecnologia com alma.</span><span><a href="{IG}" target="_blank" rel="noopener">Instagram</a> · <a href="https://www.linkedin.com/company/curtamax" target="_blank" rel="noopener">LinkedIn</a> · <a href="https://www.behance.net/johnatan-conce" target="_blank" rel="noopener">Behance</a> · <a href="/privacidade/">Privacidade</a> · CNPJ 66.039.234/0001-50</span></div>
</footer>
<script>document.getElementById('yr').textContent=new Date().getFullYear();
var c=document.querySelector('[data-copy]');if(c)c.addEventListener('click',function(){{try{{navigator.clipboard.writeText(location.href);c.textContent='Link copiado';}}catch(e){{}}}});</script>
</body>
</html>
"""


def cta(up, msg):
    return f"""<section class="cta">
  <div class="bg"></div>
  <span class="kick">Vamos conversar</span>
  <h2>Sua marca com <span class="mx">IA e alma</span></h2>
  <p>Direção de cinema, IA generativa, motion e som num só parceiro. Também levamos esse processo para treinamentos de times.</p>
  <div class="row">
    <a class="btn btn-c" href="{WA}{msg}" target="_blank" rel="noopener">{WA_ICON} Conversar no WhatsApp</a>
    <a class="btn btn-o" href="{IG}" target="_blank" rel="noopener">@curtamax.ai ↗</a>
  </div>
</section>
"""


def newsletter(up):
    return NL.replace("{{UP}}", up).replace("{{SYM}}", SYM) + "\n"


def today_br():
    if os.environ.get("BLOG_TODAY"):
        return date.fromisoformat(os.environ["BLOG_TODAY"])
    return (datetime.now(timezone.utc) - timedelta(hours=3)).date()


def build():
    hoje = today_br()
    todos = [parse(p) for p in (SRC / "posts").glob("*.html")]
    posts = sorted((m for m in todos if date.fromisoformat(m["date"]) <= hoje), key=lambda m: m["date"], reverse=True)
    agendados = sorted(m["date"] + " " + m["slug"] for m in todos if date.fromisoformat(m["date"]) > hoje)
    OUT.mkdir(exist_ok=True)
    # remove páginas de artigos que ainda não devem estar no ar
    publicados = {m["slug"] for m in posts}
    for d in OUT.iterdir():
        if d.is_dir() and d.name not in publicados:
            shutil.rmtree(d)
    shutil.copy(SRC / "blog.css", OUT / "blog.css")

    for m in posts:
        url = f"{SITE}/blog/{m['slug']}/"
        img = SITE + "/" + m["cover"].replace("../", "")
        msg = "Ol%C3%A1%2C%20Curtamax!%20Li%20o%20artigo%20do%20blog%20e%20quero%20conversar%20sobre%20um%20projeto."
        share_txt = (m["title"] + " " + url).replace(" ", "%20")
        page = head(m["title"] + " · Blog Curtamax", m["description"], url, img, 2, "article")
        page += f"""<article>
<section class="top">
  <div class="bg" style="background-image:url({m['cover']})"></div>
  <div class="wrap">
    <a class="chip" href="../">{m['category']}</a>
    <h1>{m['title']}</h1>
    <p class="sub">{m['description']}</p>
    <div class="meta"><span>Por <b>Johnatan Conce</b></span><span>{m['date_label']}</span><span>{m['read']}</span></div>
  </div>
</section>
<section class="art">
  <div class="prose">
{m['body']}
  </div>
  <div class="after">
    <div class="share">Compartilhar
      <a href="https://www.linkedin.com/sharing/share-offsite/?url={url}" target="_blank" rel="noopener">LinkedIn</a>
      <a href="https://wa.me/?text={share_txt}" target="_blank" rel="noopener">WhatsApp</a>
      <button type="button" data-copy>Copiar link</button>
    </div>
    <div class="author"><img src="../../assets/img/fundador.webp" alt="Johnatan Conce"><div><b>Johnatan Conce</b><span>Fundador e diretor criativo da Curtamax. Publicitário, com passagem por projetos para Philips, AOC, AGON e Unilever.</span></div></div>
    <a class="back" href="../">← Todos os artigos</a>
  </div>
</section>
</article>
"""
        page += newsletter("../../") + cta("../../", msg) + foot()
        page = page.replace("{{SYM}}", SYM)
        d = OUT / m["slug"]
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(page)

    # lista
    cards = "".join(f"""
  <a class="card" href="{m['slug']}/">
    <div class="th"><img src="{m['card']}" alt="" loading="lazy"><span class="chip">{m['category']}</span></div>
    <div class="tx"><h2>{m['title']}</h2><p>{m['description']}</p><div class="mm">{m['date_label']} · <span>{m['read']}</span></div></div>
  </a>""" for m in posts)
    desc = "Artigos da Curtamax sobre IA generativa, motion, som, direção e tecnologia com alma para marcas e agências."
    page = head("Blog · Curtamax arttech", desc, f"{SITE}/blog/", f"{SITE}/assets/img/tempestade.webp", 1)
    page += f"""<section class="top">
  <div class="bg" style="background-image:url(../assets/img/tempestade.webp)"></div>
  <div class="wrap">
    <span class="kick">Blog Curtamax</span>
    <h1>Arte, design e tecnologia <span class="mx">no mesmo set</span></h1>
    <p class="sub">Bastidores, cases e ideias sobre IA com alma, motion, som e direção para marcas e agências.</p>
  </div>
</section>
<section class="list"><div class="grid">{cards}
</div></section>
"""
    page += newsletter("../") + cta("../", "Ol%C3%A1%2C%20Curtamax!%20Vim%20pelo%20blog%20e%20quero%20conversar%20sobre%20um%20projeto.") + foot()
    (OUT / "index.html").write_text(page)

    # política de privacidade
    pdir = ROOT / "privacidade"; pdir.mkdir(exist_ok=True)
    pdesc = "Como a Curtamax cuida dos dados de quem assina a newsletter ou entra em contato, de acordo com a LGPD."
    page = head("Política de Privacidade · Curtamax arttech", pdesc, f"{SITE}/privacidade/", f"{SITE}/assets/img/tempestade.webp", 1)
    page += PRIV + foot()
    (pdir / "index.html").write_text(page)

    # sitemap
    urls = [f"{SITE}/", f"{SITE}/blog/", f"{SITE}/privacidade/"] + [f"{SITE}/blog/{m['slug']}/" for m in posts]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n"
    (ROOT / "sitemap.xml").write_text(sm)
    print(f"Hoje (Brasília): {hoje}. {len(posts)} artigo(s) no ar.")
    for a in agendados:
        print("  agendado:", a)


if __name__ == "__main__":
    build()
