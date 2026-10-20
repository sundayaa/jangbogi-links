#!/usr/bin/env python3
"""든든한 장보기 링크 모음 페이지 생성기 (v2 — 디자인/CTR 개편).

products.json -> index.html (GitHub Pages 배포용)
적용 라이브러리 (vendor/lib, SOURCES.md 참고):
  Pretendard(한글 폰트) · normalize.css · Animate.css · AOS(스크롤 등장) ·
  Swiper(인기 캐러셀) · GSAP(숫자 카운트업) · Fuse.js(퍼지 검색) ·
  lazysizes(지연 로딩) · Hover.css · MicroModal(빠른보기) ·
  Vanilla-tilt · noUiSlider(가격 필터) · Font Awesome(아이콘)
- 카테고리: products.json에 category가 없으면 상품명 키워드로 자동 분류.
- 쇼츠 링크: ../../upload-queue.json의 published_url을 EP로 매칭.
사용법: python3 bin/build.py
"""
import html
import json
import re
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "products.json"
QUEUE = ROOT.parent / "upload-queue.json"
OUT = ROOT / "index.html"
CHANNEL_URL = "https://www.youtube.com/@든든한장보기"
BLANK = "data:image/gif;base64,R0lGODlhAQABAAAAACw="

CATEGORIES = ["식품", "간식", "주방", "생활", "뷰티", "기타"]

KEYWORD_RULES = [
    ("뷰티", ["샴푸", "핸드크림", "크림", "로션", "클렌징", "마스크팩", "선크림", "세럼"]),
    ("주방", ["수세미", "거치대", "오일병", "양념병", "간장병", "키친타올", "주방",
              "도마", "냄비", "후라이팬", "프라이팬", "뚜껑", "실리콘", "밀폐용기"]),
    ("생활", ["화장지", "롤화장지", "물티슈", "세제", "욕실", "매트", "청소", "방향제",
              "섬유유연제", "휴지", "티슈", "쓰레기봉투"]),
    ("간식", ["빼빼로", "양파링", "꼬깔콘", "초코파이", "새우깡", "바나나킥", "카스타드",
              "에이스", "다이제", "메로나", "부라보콘", "맛동산", "고래밥", "호빵",
              "과자", "사이다", "커피믹스", "아이스크림", "젤리", "캔디", "초콜릿", "홈런볼"]),
    ("식품", ["귤", "감귤", "고추장", "고춧가루", "햇반", "백미", "쌀", "만두", "김치",
              "스팸", "참치", "두부", "우유", "삼다수", "사골곰탕", "라면", "너구리",
              "신라면", "진라면", "비빔면", "육개장", "옥수수수염차", "바나나", "단감",
              "사과", "고구마", "계란", "특란", "고등어", "김", "식용유", "콩기름",
              "물", "음료", "주스", "된장", "간장", "참기름", "들기름", "교자"]),
]


def esc(s):
    return html.escape(str(s or ""), quote=True)


def categorize(p):
    if p.get("category") in CATEGORIES:
        return p["category"]
    name = p.get("name") or p.get("product") or ""
    for cat, keywords in KEYWORD_RULES:
        if any(k in name for k in keywords):
            return cat
    return "기타"


def parse_reviews(p):
    raw = str(p.get("reviews") or "")
    m = re.search(r"([\d,.]+)\s*만", raw)
    if m:
        return int(float(m.group(1).replace(",", "")) * 10000)
    m = re.search(r"([\d,]+)", raw)
    return int(m.group(1).replace(",", "")) if m else 0


def parse_price(p):
    raw = str(p.get("price") or "")
    m = re.search(r"([\d,]+)", raw)
    return int(m.group(1).replace(",", "")) if m else None


def fmt_reviews(n):
    if n >= 10000:
        v = n / 10000
        return ("%.1f" % v).rstrip("0").rstrip(".") + "만 개"
    return "{:,}개".format(n)


def ep_shorts_urls():
    try:
        q = json.loads(QUEUE.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return {e["ep"]: e["published_url"] for e in q.get("queue", [])
            if e.get("ep") and e.get("published_url")}


def meta_text(p, reviews_n):
    bits = []
    if reviews_n:
        bits.append("상품평 " + fmt_reviews(reviews_n))
    elif p.get("reviews"):
        bits.append("상품평 " + str(p["reviews"]))
    if p.get("rating"):
        bits.append("별점 " + str(p["rating"]))
    return " · ".join(bits) if bits else "쿠팡에서 자세한 정보를 확인하세요"


def price_note(p):
    if p.get("price") and p.get("price_checked"):
        return "(%s 확인 · 가격은 변동될 수 있어요)" % esc(p["price_checked"])
    if p.get("price"):
        return "(가격은 변동될 수 있어요)"
    return ""


def badges_html(p, cat, today):
    out = []
    try:
        d = date.fromisoformat(str(p.get("date") or ""))
        if (today - d) <= timedelta(days=7):
            out.append('<span class="badge new animate__animated animate__pulse animate__infinite">NEW</span>')
    except ValueError:
        pass
    out.append('<span class="badge cat">%s</span>' % esc(cat))
    return '<div class="badges">%s</div>' % "".join(out)


def cta_html(p):
    url = p.get("url") or p.get("affiliate_link") or ""
    if url and url != "#":
        return ('<a class="cta hvr-grow" href="%s">'
                '<i class="fa-solid fa-cart-shopping"></i> 쿠팡에서 상품 보기</a>' % esc(url))
    return '<span class="cta off">쿠팡 링크 준비 중</span>'


def video_html(p, shorts_urls):
    vurl = shorts_urls.get(p.get("ep") or "")
    if vurl:
        return ('<a class="video" href="%s">'
                '<i class="fa-brands fa-youtube"></i> 영상으로 보기</a>' % esc(vurl))
    return ""


def render_card(p, shorts_urls, today):
    name = p.get("name") or p.get("product") or ""
    cat = categorize(p)
    rn = parse_reviews(p)
    pn = parse_price(p)
    img = ""
    if p.get("image"):
        img = ('<img class="pimg lazyload" data-src="%s" src="%s" alt="%s">'
               % (esc(p["image"]), BLANK, esc(name)))
    return """  <article class="card" data-cat="{cat}" data-name="{nl}" data-reviews="{rn}" data-price="{pn}" data-date="{dt}" data-aos="fade-up">
    {badges}
    <button class="imgbtn" data-qv aria-label="{name} 자세히 보기">{img}</button>
    <h3>{name}</h3>
    <p class="meta">{meta}</p>
    <p class="price">{price} <span class="pnote">{pnote}</span></p>
    <div class="btns">
      {cta}
      {video}
    </div>
  </article>
""".format(
        cat=esc(cat), nl=esc(name.lower()), rn=rn,
        pn=pn if pn is not None else "", dt=esc(p.get("date") or ""),
        badges=badges_html(p, cat, today), img=img, name=esc(name),
        meta=esc(meta_text(p, rn)), price=esc(p.get("price") or "가격은 쿠팡에서 확인"),
        pnote=price_note(p), cta=cta_html(p), video=video_html(p, shorts_urls),
    )


def render_slide(p, shorts_urls, rank):
    name = p.get("name") or p.get("product") or ""
    rn = parse_reviews(p)
    img = ""
    if p.get("image"):
        img = '<img class="simg" src="%s" alt="%s" loading="lazy">' % (
            esc(p["image"]), esc(name))
    return """      <div class="swiper-slide">
        <div class="slide-card" data-tilt>
          <span class="rank">%d위</span>
          %s
          <h3>%s</h3>
          <p class="meta"><i class="fa-solid fa-star"></i> 상품평 %s</p>
          <p class="price">%s</p>
          <div class="btns">%s%s</div>
        </div>
      </div>
""" % (rank, img, esc(name), esc(fmt_reviews(rn)),
       esc(p.get("price") or ""), cta_html(p), video_html(p, shorts_urls))


PAGE = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>든든한 장보기 — 영상으로 소개한 상품 모음</title>
<link rel="stylesheet" href="vendor/lib/normalize.css">
<link rel="stylesheet" href="vendor/lib/animate.min.css">
<link rel="stylesheet" href="vendor/lib/aos.css">
<link rel="stylesheet" href="vendor/lib/swiper-bundle.min.css">
<link rel="stylesheet" href="vendor/lib/hover-min.css">
<link rel="stylesheet" href="vendor/lib/all.min.css">
<link rel="stylesheet" href="vendor/lib/nouislider.min.css">
<style>
  @font-face {
    font-family: "Pretendard";
    src: url("vendor/lib/PretendardVariable.woff2") format("woff2");
    font-weight: 45 920; font-style: normal; font-display: swap;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; padding: 0 0 110px;
    font-family: "Pretendard", -apple-system, BlinkMacSystemFont, "Noto Sans KR", sans-serif;
    font-size: 20px; line-height: 1.6; color: #1a1a1a; background: #f7f4ee;
  }
  .wrap { max-width: 600px; margin: 0 auto; padding: 0 16px 48px; }
  header.top {
    background: linear-gradient(135deg, #2e5d33, #3d7a44); color: #fff;
    border-radius: 0 0 24px 24px; padding: 30px 20px 26px;
    text-align: center; margin: 0 -16px 20px;
  }
  .brand { font-size: 34px; font-weight: 800; margin: 0 0 6px; }
  .brand .basket { display: inline-block; }
  .tagline { font-size: 21px; margin: 0 0 14px; }
  .stats {
    display: flex; justify-content: center; gap: 22px; margin: 0 0 16px;
    font-size: 18px; font-weight: 700;
  }
  .stats b { font-size: 24px; }
  .disclosure {
    display: inline-block; background: rgba(255,255,255,.16);
    font-size: 16px; line-height: 1.5; border-radius: 12px; padding: 10px 14px; margin: 0;
  }
  .howto {
    background: #fff; border: 3px solid #2e5d33; border-radius: 20px;
    padding: 20px; margin-bottom: 24px;
  }
  .howto h2 { font-size: 26px; margin: 0 0 12px; text-align: center; }
  .howto ol { margin: 0; padding-left: 8px; list-style: none; }
  .howto li { font-size: 22px; margin: 12px 0; display: flex; align-items: center; gap: 12px; }
  .step {
    flex: 0 0 auto; width: 52px; height: 52px; border-radius: 50%;
    background: #2e5d33; color: #fff; font-size: 28px; font-weight: 800;
    display: inline-flex; align-items: center; justify-content: center;
  }
  h2.sec { font-size: 27px; margin: 26px 0 14px; }
  .swiper { padding: 4px 4px 34px; }
  .slide-card {
    background: #fff; border-radius: 24px; padding: 20px; position: relative;
    box-shadow: 0 4px 16px rgba(0,0,0,.12); border: 2px solid #ffb300;
  }
  .rank {
    position: absolute; top: 14px; left: 14px; z-index: 2;
    background: #e53935; color: #fff; font-weight: 800; font-size: 18px;
    padding: 4px 14px; border-radius: 999px;
  }
  .simg {
    width: 100%; aspect-ratio: 4/3; object-fit: contain; display: block;
    border-radius: 16px; background: #fff;
  }
  .slide-card h3 { font-size: 25px; margin: 12px 0 6px; line-height: 1.4; }
  .slide-card .price { font-size: 28px; }
  .swiper-pagination-bullet { width: 12px; height: 12px; }
  .swiper-pagination-bullet-active { background: #2e5d33; }
  .toolbar {
    position: sticky; top: 0; z-index: 20;
    background: #f7f4ee; padding: 12px 0 10px;
  }
  .search {
    width: 100%; font-size: 22px; padding: 16px 20px;
    border: 3px solid #2e5d33; border-radius: 999px; background: #fff;
    outline: none; -webkit-appearance: none;
  }
  .search:focus { border-color: #1565c0; }
  .chips {
    display: flex; gap: 8px; overflow-x: auto; padding: 12px 2px 4px;
    -webkit-overflow-scrolling: touch; scrollbar-width: none;
  }
  .chips::-webkit-scrollbar { display: none; }
  .chip {
    flex: 0 0 auto; font-size: 20px; font-weight: 700; cursor: pointer;
    padding: 10px 20px; border-radius: 999px; border: 2px solid #2e5d33;
    background: #fff; color: #2e5d33; font-family: inherit;
  }
  .chip.on { background: #2e5d33; color: #fff; }
  .row2 { display: flex; gap: 10px; margin-top: 10px; }
  .sortsel {
    flex: 1; font-size: 19px; padding: 12px 14px; font-family: inherit;
    border: 2px solid #bbb; border-radius: 14px; background: #fff;
  }
  .pfilter-btn {
    font-size: 19px; font-weight: 700; padding: 12px 16px; cursor: pointer;
    border: 2px solid #bbb; border-radius: 14px; background: #fff; font-family: inherit;
  }
  .pfilter { display: none; background: #fff; border-radius: 16px; padding: 20px 22px 14px; margin-top: 10px; }
  .pfilter.open { display: block; }
  .pfilter p { margin: 0 0 14px; font-size: 19px; font-weight: 700; }
  .noUi-connect { background: #2e5d33; }
  .count { text-align: center; color: #666; font-size: 18px; margin: 8px 0 14px; }
  .card {
    background: #fff; border-radius: 24px; padding: 20px; margin-bottom: 24px;
    box-shadow: 0 3px 14px rgba(0,0,0,.10); border: 1px solid #e8e2d5;
  }
  .badges { display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }
  .badge { font-size: 16px; font-weight: 800; padding: 4px 12px; border-radius: 999px; }
  .badge.new { background: #e53935; color: #fff; --animate-duration: 1.6s; }
  .badge.cat { background: #ece7d9; color: #555; }
  .imgbtn { display: block; width: 100%; padding: 0; border: 0; background: none; cursor: pointer; }
  .pimg {
    width: 100%; aspect-ratio: 4 / 3; object-fit: contain;
    background: #fff; border: 1px solid #eee; border-radius: 16px; display: block;
  }
  .card h3 { font-size: 26px; margin: 14px 0 8px; line-height: 1.4; }
  .meta { font-size: 20px; color: #555; margin: 0 0 6px; }
  .meta .fa-star { color: #ffb300; }
  .price { font-size: 30px; font-weight: 800; color: #b3261e; margin: 8px 0 16px; }
  .pnote { display: block; font-size: 16px; font-weight: 400; color: #777; }
  .btns { display: flex; flex-direction: column; gap: 10px; }
  .cta {
    display: block; text-align: center; text-decoration: none;
    background: #1565c0; color: #fff; font-size: 24px; font-weight: 800;
    padding: 18px 16px; border-radius: 18px;
  }
  .cta:active { background: #0d47a1; }
  .cta.off { background: #e8e2d5; color: #888; pointer-events: none; }
  .video {
    display: block; text-align: center; text-decoration: none;
    background: #fff; color: #c62828; font-size: 21px; font-weight: 700;
    padding: 14px 16px; border-radius: 18px; border: 2px solid #c62828;
  }
  .empty {
    display: none; text-align: center; background: #fff; border-radius: 20px;
    padding: 40px 20px; font-size: 22px; color: #555;
  }
  footer { text-align: center; margin-top: 36px; }
  footer .disclosure { background: #ece7d9; color: #333; }
  .totop {
    display: inline-block; margin-top: 20px; font-size: 20px; color: #2e5d33;
    font-weight: 700; text-decoration: none; padding: 14px 28px;
    border: 2px solid #2e5d33; border-radius: 999px; background: #fff;
  }
  .updated { text-align: center; color: #888; font-size: 16px; margin-top: 24px; }
  .stickybar {
    position: fixed; left: 0; right: 0; bottom: 0; z-index: 30;
    background: rgba(255,255,255,.96); border-top: 1px solid #ddd;
    padding: 10px 16px calc(10px + env(safe-area-inset-bottom));
    display: flex; justify-content: center;
  }
  .stickybar a {
    display: block; width: 100%; max-width: 568px; text-align: center;
    background: #c62828; color: #fff; text-decoration: none;
    font-size: 22px; font-weight: 800; padding: 15px; border-radius: 16px;
  }
  .modal { display: none; }
  .modal.is-open { display: block; }
  .modal__overlay {
    position: fixed; inset: 0; background: rgba(0,0,0,.55); z-index: 50;
    display: flex; align-items: flex-end; justify-content: center;
  }
  .modal__container {
    background: #fff; width: 100%; max-width: 600px; max-height: 88vh;
    overflow-y: auto; border-radius: 24px 24px 0 0; padding: 22px 20px 30px;
  }
  .modal__close {
    float: right; font-size: 22px; border: 0; background: #ece7d9;
    width: 48px; height: 48px; border-radius: 50%; cursor: pointer;
  }
  .modal__container img {
    width: 100%; aspect-ratio: 4/3; object-fit: contain; border-radius: 16px;
  }
  .modal__container h3 { font-size: 27px; margin: 14px 0 8px; line-height: 1.4; }
</style>
</head>
<body id="top">
<div class="wrap">

  <header class="top">
    <p class="brand animate__animated animate__fadeInDown"><span class="basket">🧺</span> 든든한 장보기</p>
    <p class="tagline">영상으로 소개한 상품을 한 곳에 모았어요</p>
    <p class="stats">
      <span>상품 <b id="stat-products">0</b>개</span>
      <span>누적 상품평 <b id="stat-reviews">0</b>개</span>
    </p>
    <p class="disclosure">%%DISCLOSURE%%</p>
  </header>

  <section class="howto">
    <h2>📱 구매 방법 (두 단계)</h2>
    <ol>
      <li><span class="step">1</span><span>원하는 상품 아래의 <strong>파란 버튼</strong>을 누르세요</span></li>
      <li><span class="step">2</span><span>쿠팡 페이지가 열리면 평소대로 구매하시면 됩니다</span></li>
    </ol>
  </section>

  <h2 class="sec">🔥 후기 많은 인기 상품</h2>
  <div class="swiper" id="featured">
    <div class="swiper-wrapper">
%%SLIDES%%    </div>
    <div class="swiper-pagination"></div>
  </div>

  <div class="toolbar">
    <input class="search" id="q" type="search" placeholder="🔍 상품 이름으로 찾기 (예: 귤, 라면)" autocomplete="off">
    <div class="chips" id="chips">
      <button class="chip on" data-cat="전체">전체</button>
%%CHIPS%%
    </div>
    <div class="row2">
      <select class="sortsel" id="sort">
        <option value="new">최신순</option>
        <option value="popular">후기 많은 순</option>
        <option value="cheap">가격 낮은 순</option>
        <option value="expensive">가격 높은 순</option>
      </select>
      <button class="pfilter-btn" id="pfilter-btn">💰 가격대</button>
    </div>
    <div class="pfilter" id="pfilter">
      <p>가격 범위: <span id="prange-label"></span></p>
      <div id="pslider"></div>
    </div>
  </div>
  <p class="count" id="count"></p>
  <main id="list">
%%CARDS%%  </main>
  <div class="empty" id="empty">찾으시는 상품이 없어요 😢<br>다른 이름으로 검색해 보세요.</div>

  <footer>
    <p class="disclosure">%%DISCLOSURE%%</p>
    <br>
    <a class="totop" href="#top">맨 위로 올라가기 ↑</a>
    <p class="updated">마지막 업데이트: %%UPDATED%%</p>
  </footer>

</div>

<div class="stickybar">
  <a href="%%CHANNEL%%"><i class="fa-brands fa-youtube"></i> 든든한 장보기 채널 영상 보기</a>
</div>

<div class="modal" id="qv" aria-hidden="true">
  <div class="modal__overlay" data-micromodal-close>
    <div class="modal__container" role="dialog" aria-modal="true">
      <button class="modal__close" data-micromodal-close aria-label="닫기">✕</button>
      <img id="qv-img" alt="">
      <h3 id="qv-name"></h3>
      <p class="meta" id="qv-meta"></p>
      <p class="price" id="qv-price"></p>
      <div class="btns" id="qv-btns"></div>
    </div>
  </div>
</div>

<script src="vendor/lib/aos.js"></script>
<script src="vendor/lib/swiper-bundle.min.js"></script>
<script src="vendor/lib/gsap.min.js"></script>
<script src="vendor/lib/lazysizes.min.js" async></script>
<script src="vendor/lib/micromodal.min.js"></script>
<script src="vendor/lib/vanilla-tilt.min.js"></script>
<script src="vendor/lib/nouislider.min.js"></script>
<script type="module">
import Fuse from "./vendor/lib/fuse.mjs";

var cards = Array.prototype.slice.call(document.querySelectorAll("#list .card"));
var list = document.getElementById("list");
var q = document.getElementById("q");
var count = document.getElementById("count");
var empty = document.getElementById("empty");
var chips = Array.prototype.slice.call(document.querySelectorAll(".chip"));
var cat = "전체";
var priceMin = null, priceMax = null;

var fuse = new Fuse(cards, {
  keys: [{ name: "name", getFn: function (c) { return c.dataset.name; } }],
  threshold: 0.35, ignoreLocation: true
});

function apply() {
  var term = q.value.trim();
  var matched = null;
  if (term) {
    matched = {};
    fuse.search(term.toLowerCase()).forEach(function (r) { matched[r.item.dataset.name + r.item.dataset.cat] = true; });
  }
  var shown = 0;
  cards.forEach(function (c) {
    var okCat = (cat === "전체" || c.dataset.cat === cat);
    var key = c.dataset.name + c.dataset.cat;
    var okTerm = (!matched || matched[key]);
    if (!okTerm && matched && c.dataset.name.indexOf(term.toLowerCase()) !== -1) okTerm = true;
    var p = parseInt(c.dataset.price || "", 10);
    var okPrice = true;
    if (priceMin !== null) {
      if (isNaN(p)) okPrice = false;
      else okPrice = (p >= priceMin && p <= priceMax);
    }
    var show = okCat && okTerm && okPrice;
    c.style.display = show ? "" : "none";
    if (show) shown++;
  });
  count.textContent = "총 " + shown + "개 상품";
  empty.style.display = shown ? "none" : "block";
  if (window.AOS) AOS.refresh();
}

q.addEventListener("input", apply);
chips.forEach(function (chip) {
  chip.addEventListener("click", function () {
    chips.forEach(function (c) { c.classList.remove("on"); });
    chip.classList.add("on");
    cat = chip.dataset.cat;
    apply();
  });
});

document.getElementById("sort").addEventListener("change", function () {
  var mode = this.value;
  var sorted = cards.slice().sort(function (a, b) {
    if (mode === "popular") return (parseInt(b.dataset.reviews) || 0) - (parseInt(a.dataset.reviews) || 0);
    if (mode === "cheap" || mode === "expensive") {
      var pa = parseInt(a.dataset.price || "", 10), pb = parseInt(b.dataset.price || "", 10);
      if (isNaN(pa)) return 1; if (isNaN(pb)) return -1;
      return mode === "cheap" ? pa - pb : pb - pa;
    }
    return (b.dataset.date || "").localeCompare(a.dataset.date || "");
  });
  sorted.forEach(function (c) { list.appendChild(c); });
  cards = sorted;
  apply();
});

/* 가격대 슬라이더 (noUiSlider) */
var prices = cards.map(function (c) { return parseInt(c.dataset.price || "", 10); }).filter(function (p) { return !isNaN(p); });
if (prices.length) {
  var lo = Math.floor(Math.min.apply(null, prices) / 1000) * 1000;
  var hi = Math.ceil(Math.max.apply(null, prices) / 1000) * 1000;
  var slider = document.getElementById("pslider");
  var label = document.getElementById("prange-label");
  noUiSlider.create(slider, {
    start: [lo, hi], connect: true, step: 1000, range: { min: lo, max: hi }
  });
  slider.noUiSlider.on("update", function (vals) {
    label.textContent = Number(vals[0]).toLocaleString() + "원 ~ " + Number(vals[1]).toLocaleString() + "원";
  });
  slider.noUiSlider.on("change", function (vals) {
    priceMin = Number(vals[0]); priceMax = Number(vals[1]);
    if (priceMin <= lo && priceMax >= hi) { priceMin = null; priceMax = null; }
    apply();
  });
}
document.getElementById("pfilter-btn").addEventListener("click", function () {
  document.getElementById("pfilter").classList.toggle("open");
});

/* 빠른보기 모달 (MicroModal) */
MicroModal.init();
cards.forEach(function (c) {
  var btn = c.querySelector("[data-qv]");
  if (!btn) return;
  btn.addEventListener("click", function () {
    var img = c.querySelector(".pimg");
    document.getElementById("qv-img").src = img ? (img.dataset.src || img.src) : "";
    document.getElementById("qv-name").textContent = c.querySelector("h3").textContent;
    document.getElementById("qv-meta").textContent = c.querySelector(".meta").textContent;
    document.getElementById("qv-price").textContent = c.querySelector(".price").textContent;
    var btns = document.getElementById("qv-btns");
    btns.innerHTML = "";
    c.querySelectorAll(".btns a, .btns span").forEach(function (a) {
      btns.appendChild(a.cloneNode(true));
    });
    MicroModal.show("qv");
  });
});

/* 캐러셀 (Swiper) + 틸트 */
if (document.querySelectorAll("#featured .swiper-slide").length) {
  new Swiper("#featured", {
    slidesPerView: 1.12, spaceBetween: 14, centeredSlides: false,
    pagination: { el: ".swiper-pagination", clickable: true }
  });
  if (window.matchMedia("(pointer: fine)").matches) {
    VanillaTilt.init(document.querySelectorAll("[data-tilt]"), { max: 6, speed: 300 });
  }
}

/* 헤더 통계 카운트업 (GSAP) */
AOS.init({ once: true, offset: 30, duration: 500 });
function countUp(id, target) {
  var el = document.getElementById(id);
  var obj = { v: 0 };
  gsap.to(obj, {
    v: target, duration: 1.4, ease: "power2.out",
    onUpdate: function () { el.textContent = Math.round(obj.v).toLocaleString(); }
  });
}
countUp("stat-products", %%N_PRODUCTS%%);
countUp("stat-reviews", %%TOTAL_REVIEWS%%);
gsap.to(".basket", { y: -8, duration: 0.9, repeat: -1, yoyo: true, ease: "sine.inOut" });

apply();
</script>
<!-- Cloudflare Web Analytics (방문자 통계, 2026-10-03 추가) -->
<script type='module' src='https://static.cloudflareinsights.com/beacon.min.js'
  data-cf-beacon='{"token": "954984c2c2444153b49c68c9112377fd"}'></script>
<!-- End Cloudflare Web Analytics -->
</body>
</html>
"""


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    today = date.today()
    shorts_urls = ep_shorts_urls()
    products = [p for p in data["products"] if (p.get("name") or p.get("product"))]
    # 인기 캐러셀: 링크 있는 상품 중 후기 많은 순 상위 5
    with_url = [p for p in products if (p.get("url") or p.get("affiliate_link"))]
    featured = sorted(with_url, key=parse_reviews, reverse=True)[:5]
    slides = "".join(render_slide(p, shorts_urls, i + 1)
                     for i, p in enumerate(featured))
    cards = "".join(render_card(p, shorts_urls, today) for p in products)
    used_cats = [c for c in CATEGORIES if any(categorize(p) == c for p in products)]
    chips = "\n".join(
        '      <button class="chip" data-cat="%s">%s</button>' % (esc(c), esc(c))
        for c in used_cats
    )
    page = (PAGE
            .replace("%%DISCLOSURE%%", esc(data.get("disclosure", "")))
            .replace("%%SLIDES%%", slides)
            .replace("%%CHIPS%%", chips)
            .replace("%%CARDS%%", cards)
            .replace("%%UPDATED%%", today.isoformat())
            .replace("%%CHANNEL%%", CHANNEL_URL)
            .replace("%%N_PRODUCTS%%", str(len(products)))
            .replace("%%TOTAL_REVIEWS%%", str(sum(parse_reviews(p) for p in products))))
    OUT.write_text(page, encoding="utf-8")
    print("wrote", OUT, "(%d products, featured %d)" % (len(products), len(featured)))


if __name__ == "__main__":
    main()
