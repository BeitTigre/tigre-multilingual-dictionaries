#!/usr/bin/env python3
"""Build a combined 'Tigre Dictionaries' site: one dictionary per target language."""
import pandas as pd, json, os, html, math, re, shutil, datetime
from collections import defaultdict

PARQUET = "/mnt/user-data/uploads/tigre-data-parallel-multilingual.parquet"
OUT = "/home/claude/multisite"
FAV = "/mnt/user-data/outputs/favicons"
PER_PAGE = 500
GLOSS_CAP = 15
BASE_URL = "https://USERNAME.github.io/REPO/"   # <-- edit before deploying
TODAY = datetime.date.today().isoformat()
ENGLISH_URL = "https://beittigre.github.io/tigre-english-dictionary/"  # existing site

LANGS = {
    "eng_Latn": dict(slug="english", name="English", native="English", iso="en",
                     rtl=False, arabicfont=False, col="English"),
    "ara_Arab": dict(slug="arabic", name="Arabic", native="العربية", iso="ar",
                     rtl=True, arabicfont=True, col="Arabic (العربية)"),
    "deu_Latn": dict(slug="german", name="German", native="Deutsch", iso="de",
                     rtl=False, arabicfont=False, col="German (Deutsch)"),
    "swe_Latn": dict(slug="swedish", name="Swedish", native="Svenska", iso="sv",
                     rtl=False, arabicfont=False, col="Swedish (Svenska)"),
}

# ---------- data ----------
df = pd.read_parquet(PARQUET)
df["src_text"] = df["src_text"].str.strip()
df["tgt_text"] = df["tgt_text"].str.strip()
df = df[(df.src_text != "") & (df.tgt_text != "") & (df.src_text != "tig")]

def norm(s):  # unicode-aware: keep letters of any script, drop punctuation
    return re.sub(r"[^\w\s]", "", s, flags=re.U).lower().strip()

def display_glosses(engs):
    best = {}
    for e in engs:
        k = norm(e)
        if not k:
            k = e.strip()
        def surf(s): return (s[:1].isupper(), s[-1:] in "!?.\u061f\u3002", -len(s))
        if k not in best or surf(e) > surf(best[k]):
            best[k] = e
    uniq = list(best.values())
    uniq.sort(key=lambda s: (0 if s[:1].isupper() else 1,
                             0 if s[-1:] in "!?.\u061f" else 1, abs(len(s) - 7), s.lower()))
    return uniq

def build_entries(code):
    sub = df[(df.src_lang == "tig_Ethi") & (df.tgt_lang == code)]
    pair = defaultdict(list)
    for s, e in zip(sub.src_text, sub.tgt_text):
        pair[s].append(e)
    ents = [(s, display_glosses(es)) for s, es in pair.items()]
    ents.sort(key=lambda x: x[0])
    return ents

# ---------- output dir ----------
if os.path.exists(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT)
for fn in ["favicon.ico", "favicon-16x16.png", "favicon-32x32.png",
           "favicon-48x48.png", "apple-touch-icon.png"]:
    shutil.copy(os.path.join(FAV, fn), os.path.join(OUT, fn))

def esc(s): return html.escape(s, quote=True)
def page_name(p): return f"page-{p:04d}.html"

# ---------- shared CSS ----------
CSS = r"""
:root{
  --paper:#f6efe0; --ink:#241c14; --ink-soft:#6f6150; --line:#dccbab;
  --accent:#a8431f; --accent-2:#1f5e54; --card:#fffdf8; --tig:#1d3a52; --mark:#ffe08a;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0; background:var(--paper);
  background-image:radial-gradient(900px 380px at 12% -6%, #fffaf0 0, rgba(255,250,240,0) 60%),
                   radial-gradient(700px 300px at 105% -4%, #ecd9b6 0, rgba(236,217,182,0) 55%);
  color:var(--ink); font-family:"Newsreader","Iowan Old Style",Georgia,serif;
  font-size:18px; line-height:1.55; -webkit-font-smoothing:antialiased;}
.wrap{max-width:1000px; margin:0 auto; padding:0 24px}
a{color:var(--accent); text-underline-offset:3px}
a:hover{color:var(--accent-2)}
header.site{border-bottom:2px solid var(--ink); padding:30px 0 20px; position:relative}
.kicker{font:600 13px/1 "Newsreader",serif; letter-spacing:.22em; text-transform:uppercase;
  color:var(--accent); margin:0 0 12px}
.kicker .ge{font-family:"Noto Serif Ethiopic","Noto Sans Ethiopic",serif}
.kicker a{color:var(--ink-soft)}
h1.title{font-family:"Fraunces","Newsreader",serif; font-weight:600;
  font-size:clamp(34px,6vw,58px); line-height:1.0; margin:0 0 8px; letter-spacing:-.015em}
h1.title .ge{font-family:"Noto Serif Ethiopic","Noto Sans Ethiopic",serif}
.sub{color:var(--ink-soft); font-size:18px; margin:8px 0 0; max-width:66ch}
.search-shell{margin:28px 0 6px; position:relative}
#q{width:100%; font-family:inherit; font-size:21px; color:var(--ink); background:var(--card);
  border:1.5px solid var(--ink); border-radius:12px; padding:16px 20px 16px 52px; outline:none}
#q:focus{border-color:var(--accent); box-shadow:0 0 0 4px rgba(168,67,31,.12)}
.search-shell::before{content:"\1F50D"; position:absolute; left:18px; top:50%;
  transform:translateY(-50%); font-size:19px; opacity:.5}
.metaline{display:flex; flex-wrap:wrap; gap:6px 26px; color:var(--ink-soft);
  font-size:15px; margin:13px 3px 6px; align-items:baseline}
.metaline span{white-space:nowrap}
.count{color:var(--ink-soft); font-size:15px; margin:10px 3px 0}
h2.sec{font-family:"Fraunces",serif; font-weight:600; font-size:24px; margin:34px 0 4px;
  display:flex; align-items:baseline; gap:12px; flex-wrap:wrap}
h2.sec small{font-family:"Newsreader",serif; font-weight:400; font-size:15px; color:var(--ink-soft)}
table.dict{width:100%; border-collapse:collapse; margin:12px 0 8px}
table.dict th{text-align:left; font:600 12px/1 "Newsreader",serif; letter-spacing:.14em;
  text-transform:uppercase; color:var(--ink-soft); border-bottom:2px solid var(--ink); padding:0 14px 9px}
table.dict td{border-bottom:1px solid var(--line); padding:12px 14px; vertical-align:top}
table.dict tr:target td{background:#fff1ce}
table.dict tr:hover td{background:#fffaef}
.tig{font-family:"Noto Serif Ethiopic","Noto Sans Ethiopic",serif; font-size:22px; color:var(--tig); width:40%}
.tig a{color:var(--tig); text-decoration:none}
.tig a:hover{color:var(--accent)}
.eng{font-size:18px}
.eng .v{color:var(--ink)}
.eng .sep{color:var(--line); padding:0 7px}
.more{color:var(--ink-soft); font-style:italic; font-size:15px}
mark{background:var(--mark); border-radius:3px; padding:0 1px}
[lang="ar"]{font-family:"Noto Naskh Arabic","Amiri",serif; font-size:20px}
.eng[dir="rtl"]{text-align:right; direction:rtl}
[lang="ti"]{font-family:"Noto Serif Ethiopic","Noto Sans Ethiopic",serif; font-size:21px}
.pagelinks{display:grid; grid-template-columns:repeat(auto-fill,minmax(70px,1fr)); gap:7px}
.pagelinks a{text-align:center; background:var(--card); border:1px solid var(--line);
  border-radius:7px; padding:9px 4px; font-size:14px; text-decoration:none; color:var(--ink)}
.pagelinks a:hover{border-color:var(--accent); color:var(--accent)}
nav.pager{display:flex; align-items:center; justify-content:space-between; gap:14px;
  margin:24px 0; padding:16px 0; border-top:1px solid var(--line); font-size:16px}
nav.pager .mid{color:var(--ink-soft)} nav.pager a{font-weight:600}
nav.pager .disabled{color:var(--line); pointer-events:none}
.langgrid{display:grid; grid-template-columns:repeat(auto-fill,minmax(230px,1fr)); gap:16px; margin:26px 0}
.langcard{display:block; background:var(--card); border:1px solid var(--line); border-radius:12px;
  padding:20px 22px; text-decoration:none; color:var(--ink); transition:border-color .15s}
.langcard:hover{border-color:var(--accent)}
.langcard .nm{font-family:"Fraunces",serif; font-size:23px; color:var(--ink)}
.langcard .nat{font-size:17px; color:var(--ink-soft); margin-top:2px}
.langcard .nat.ar{font-family:"Noto Naskh Arabic",serif}
.langcard .nat.ti{font-family:"Noto Serif Ethiopic",serif}
.langcard .ct{font-size:14px; color:var(--accent); margin-top:10px; letter-spacing:.04em}
footer.site{border-top:2px solid var(--ink); margin-top:42px; padding:22px 0 60px; color:var(--ink-soft); font-size:15px}
footer.site a{color:var(--accent)} footer.site strong{color:var(--ink)}
footer.site .ge{font-family:"Noto Serif Ethiopic",serif}
.hide{display:none}
@media(max-width:640px){ body{font-size:17px} .tig{font-size:20px; width:46%} table.dict td{padding:11px 9px} }
"""
open(os.path.join(OUT, "style.css"), "w").write(CSS)

def fonts(arabic=False):
    base = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link href="https://fonts.googleapis.com/css2?'
            'family=Fraunces:opsz,wght@9..144,500;9..144,600&'
            'family=Newsreader:ital,wght@0,400;0,600;1,400&'
            'family=Noto+Serif+Ethiopic:wght@400;600'
            + ('&family=Noto+Naskh+Arabic:wght@400;600' if arabic else '')
            + '&display=swap" rel="stylesheet">')
    return base

def head(title, desc, rel, arabic=False):
    return (f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">\n'
            f'<link rel="icon" href="{rel}favicon.ico" sizes="any">\n'
            f'<link rel="icon" type="image/png" sizes="32x32" href="{rel}favicon-32x32.png">\n'
            f'<link rel="icon" type="image/png" sizes="16x16" href="{rel}favicon-16x16.png">\n'
            f'<link rel="apple-touch-icon" href="{rel}apple-touch-icon.png">\n'
            f'<title>{esc(title)}</title>\n<meta name="description" content="{esc(desc)}">\n'
            f'<meta property="og:title" content="{esc(title)}">\n'
            f'<meta property="og:description" content="{esc(desc)}">\n'
            f'<meta property="og:type" content="website">\n{fonts(arabic)}\n'
            f'<link rel="stylesheet" href="{rel}style.css">\n</head>\n<body>\n')

def footer(rel):
    return ('<footer class="site"><div class="wrap">'
            f'<p><a href="{rel}index.html">&larr; All Tigre dictionaries</a></p>'
            '<p><strong>Source.</strong> Built from the open '
            '<a href="https://huggingface.co/datasets/BeitTigreAI/tigre-data-parallel-multilingual">'
            'BeitTigreAI/tigre-data-parallel-multilingual</a> dataset. Entries are sentence- and '
            'phrase-level parallel pairs grouped by the unique Tigre text; glosses are ordered to '
            'show the clearest translation first.</p>'
            f'<p>Generated {TODAY} &middot; data under its original dataset license &mdash; '
            'please retain attribution to BeitTigreAI.</p></div></footer>')

def render_eng(engs, cfg):
    dirattr = ' dir="rtl"' if cfg["rtl"] else ""
    shown = engs[:GLOSS_CAP]
    parts = '<span class="sep">&middot;</span>'.join(f'<span class="v">{esc(e)}</span>' for e in shown)
    if len(engs) > GLOSS_CAP:
        parts += f' <span class="more">(+{len(engs)-GLOSS_CAP} more)</span>'
    return parts, dirattr

def lang_header(cfg, rel):
    return ('<header class="site"><div class="wrap">'
            f'<p class="kicker"><a href="{rel}index.html">Tigre Dictionaries</a> &middot; '
            f'<span class="ge">ትግረ</span> &rarr; {esc(cfg["name"])}</p>'
            f'<h1 class="title">Tigre&ndash;{esc(cfg["name"])} <span class="ge">ትግረ</span> Dictionary</h1>'
            f'<p class="sub">A searchable parallel phrasebook from Tigre (a Semitic language of '
            f'Eritrea and eastern Sudan, in the Ge&rsquo;ez script) into {esc(cfg["name"])}.</p>'
            '</div></header>')

# ---------- build one language site ----------
summary = []
for code, cfg in LANGS.items():
    ents = build_entries(code)
    n = len(ents)
    pages = max(1, math.ceil(n / PER_PAGE))
    d = os.path.join(OUT, cfg["slug"])
    os.makedirs(d)
    rel = "../"
    colhead = f'<th>Tigre (ትግረ)</th><th>{esc(cfg["col"])}</th>'

    # entry pages
    for p in range(1, pages + 1):
        lo, hi = (p - 1) * PER_PAGE, min(p * PER_PAGE, n)
        rows = []
        for gi, (t, e) in enumerate(ents[lo:hi], start=lo):
            eng, dirattr = render_eng(e, cfg)
            rows.append(f'<tr id="entry-{gi}"><td class="tig" lang="tig">{esc(t)}</td>'
                        f'<td class="eng" lang="{cfg["iso"]}"{dirattr}>{eng}</td></tr>')
        prev_l = (f'<a href="{page_name(p-1)}">&larr; Previous</a>' if p > 1
                  else '<span class="disabled">&larr; Previous</span>')
        next_l = (f'<a href="{page_name(p+1)}">Next &rarr;</a>' if p < pages
                  else '<span class="disabled">Next &rarr;</span>')
        pager = (f'<nav class="pager">{prev_l}<span class="mid">Page {p} of {pages} &middot; '
                 f'entries {lo+1:,}\u2013{hi:,}</span>{next_l}</nav>')
        title = f"Tigre\u2013{cfg['name']} Dictionary \u2014 Page {p} of {pages}"
        desc = f"Tigre to {cfg['name']} translations, page {p}."
        b = (head(title, desc, rel, cfg.get("arabicfont")) + lang_header(cfg, rel) +
             '<main class="wrap">' + pager +
             f'<table class="dict"><thead><tr>{colhead}</tr></thead><tbody>' +
             "".join(rows) + '</tbody></table>' + pager +
             '<p><a href="index.html">&larr; Back to search</a></p></main>' +
             footer(rel) + '\n</body>\n</html>')
        open(os.path.join(d, page_name(p)), "w", encoding="utf-8").write(b)

    # dict.json
    idx = [[t, " \u00b7 ".join(e[:12]) + (f" (+{len(e)-12})" if len(e) > 12 else ""), gi]
           for gi, (t, e) in enumerate(ents)]
    json.dump(idx, open(os.path.join(d, "dict.json"), "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))

    # language index
    pagelinks = "".join(f'<a href="{page_name(p)}">{p}</a>' for p in range(1, pages + 1))
    bi = (head(f"Tigre\u2013{cfg['name']} Dictionary (ISO {cfg['iso']})",
              f"Searchable Tigre\u2013{cfg['name']} dictionary with {n:,} entries from the "
              "open BeitTigreAI parallel corpus.", rel, cfg.get("arabicfont")) +
          lang_header(cfg, rel) + '<main class="wrap">'
          '<div class="search-shell"><input id="q" type="search" autocomplete="off" '
          f'spellcheck="false" placeholder="Search Tigre (ትግረ) or {esc(cfg["name"])}\u2026" '
          'aria-label="Search"></div>'
          '<p class="metaline">'
          f'<span id="count">{n:,} entries \u2014 type to search.</span>'
          f'<span>{n:,} Tigre entries</span><span>{len(idx):,} entries indexed</span>'
          f'<span>{pages} browsable pages</span></p>'
          f'<table class="dict hide" id="results"><thead><tr>{colhead}</tr></thead>'
          '<tbody id="rbody"></tbody></table>'
          '<div id="default"><div class="browse"><h2 class="sec">Browse everything '
          '<small>every entry on a plain, link-friendly page</small></h2>'
          f'<div class="pagelinks">{pagelinks}</div></div></div></main>' + footer(rel))
    rtl_js = "true" if cfg["rtl"] else "false"
    bi += r"""
<script>
const PER=""" + str(PER_PAGE) + r""", ISO=" """ + cfg["iso"] + r""" ".trim(), RTL=""" + rtl_js + r""";
let DATA=null;
const q=document.getElementById('q'),rb=document.getElementById('rbody'),cnt=document.getElementById('count'),
      results=document.getElementById('results'),dflt=document.getElementById('default');
function pad(n){return String(n).padStart(4,'0');}
function esc(s){return s.replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
function hi(s,t){if(!t)return esc(s);const i=s.toLowerCase().indexOf(t);if(i<0)return esc(s);
  return esc(s.slice(0,i))+'<mark>'+esc(s.slice(i,i+t.length))+'</mark>'+esc(s.slice(i+t.length));}
function row(t,e,gi,term){const href='page-'+pad(Math.floor(gi/PER)+1)+'.html#entry-'+gi;
  const d=RTL?' dir="rtl"':'';
  return '<tr><td class="tig" lang="tig"><a href="'+href+'">'+hi(t,term)+'</a></td>'+
         '<td class="eng" lang="'+ISO+'"'+d+'>'+hi(e,term)+'</td></tr>';}
function show(s){results.classList.toggle('hide',!s);dflt.classList.toggle('hide',s);}
function run(){const term=q.value.trim().toLowerCase();
  if(!term){show(false);cnt.textContent=DATA?DATA.length.toLocaleString()+' entries \u2014 type to search.':'Browse the pages below.';return;}
  if(!DATA){cnt.textContent='Search index still loading\u2026 (or open on a web server).';return;}
  show(true);const out=[];let nn=0;
  for(const r of DATA){if(r[0].toLowerCase().includes(term)||r[1].toLowerCase().includes(term)){
    nn++;if(out.length<300)out.push(row(r[0],r[1],r[2],term));}}
  cnt.textContent=nn.toLocaleString()+' match'+(nn===1?'':'es')+(nn>300?' (showing first 300)':'');
  rb.innerHTML=out.join('')||'<tr><td colspan="2">No matches.</td></tr>';}
q.addEventListener('input',run);
fetch('dict.json').then(r=>r.json()).then(d=>{DATA=d;if(!q.value.trim())
  cnt.textContent=d.length.toLocaleString()+' entries \u2014 type to search.';else run();})
 .catch(()=>{cnt.textContent='Live search needs a web server; browse the pages below.';});
</script>
"""
    bi += '\n</body>\n</html>'
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(bi)
    summary.append((cfg, n, pages))
    print(f"  built {cfg['name']:18s} {n:>6,} entries / {pages} pages")

# ---------- landing page ----------
cards = ['<a class="langcard" href="%s/index.html"><div class="nm">%s</div>'
         '<div class="nat %s">%s</div><div class="ct">%s entries &rarr;</div></a>'
         % (cfg["slug"], esc(cfg["name"]),
            ("ar" if cfg.get("arabicfont") else ("ti" if cfg.get("ethiopic") else "")),
            esc(cfg["native"]), f"{n:,}")
         for cfg, n, pages in summary]

land = (head("Tigre Dictionaries \u2014 multilingual phrasebooks (ትግረ)",
             "Searchable Tigre dictionaries: Tigre to English, Arabic, German, Swedish, "
             "Norwegian and Tigrinya, from the open BeitTigreAI parallel corpus.", "", True) +
        '<header class="site"><div class="wrap">'
        '<p class="kicker">Tigre &middot; <span class="ge">ትግረ</span> &middot; ISO 639-3 tig</p>'
        '<h1 class="title">Tigre <span class="ge">ትግረ</span> Dictionaries</h1>'
        '<p class="sub">Searchable parallel phrasebooks from Tigre &mdash; a Semitic language of '
        'Eritrea and eastern Sudan written in the Ge&rsquo;ez script &mdash; into several languages. '
        'Choose a dictionary:</p></div></header>'
        '<main class="wrap"><div class="langgrid">' + "".join(cards) + '</div>'
        '<p class="count">Each dictionary has its own search and link-friendly pages. '
        'Built from the open BeitTigreAI parallel corpus.</p></main>' +
        '<footer class="site"><div class="wrap"><p><strong>Source.</strong> '
        '<a href="https://huggingface.co/datasets/BeitTigreAI/tigre-data-parallel-multilingual">'
        'BeitTigreAI/tigre-data-parallel-multilingual</a> &middot; please retain attribution.</p>'
        f'<p>Generated {TODAY}.</p></div></footer>\n</body>\n</html>')
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(land)

# ---------- sitemap + robots ----------
sm = ['<?xml version="1.0" encoding="UTF-8"?>',
      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
      f'<url><loc>{BASE_URL}index.html</loc><lastmod>{TODAY}</lastmod><priority>1.0</priority></url>']
for cfg, n, pages in summary:
    sm.append(f'<url><loc>{BASE_URL}{cfg["slug"]}/index.html</loc><lastmod>{TODAY}</lastmod>'
              f'<priority>0.8</priority></url>')
    for p in range(1, pages + 1):
        sm.append(f'<url><loc>{BASE_URL}{cfg["slug"]}/{page_name(p)}</loc>'
                  f'<lastmod>{TODAY}</lastmod><priority>0.5</priority></url>')
sm.append('</urlset>')
open(os.path.join(OUT, "sitemap.xml"), "w").write("\n".join(sm))
open(os.path.join(OUT, "robots.txt"), "w").write(
    f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}sitemap.xml\n")

total_pages = sum(p for _, _, p in summary)
print(f"TOTAL: {len(summary)} languages, {total_pages} entry pages + {len(summary)} indexes + landing")
