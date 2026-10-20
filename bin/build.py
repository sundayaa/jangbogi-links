#!/usr/bin/env python3
"""든든한 장보기 링크 모음 페이지 생성기.

products.json -> index.html (GitHub Pages 배포용)
의존성 없음 (표준 라이브러리만 사용).
- 카테고리: products.json에 category가 없으면 상품명 키워드로 자동 분류.
- 쇼츠 링크: ../../upload-queue.json의 published_url을 EP로 매칭해 '영상 보기' 버튼 제공.
- 빈 상품명(placeholder)은 렌더에서 제외.
사용법: python3 bin/build.py
"""
import html
import json
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "products.json"
QUEUE = ROOT.parent / "upload-queue.json"
OUT = ROOT / "index.html"

# 카테고리 순서 (칩 표시 순)
CATEGORIES = ["식품", "간식", "주방", "생활", "뷰티", "기타"]

# 상품명 키워드 → 카테고리 (위에서부터 우선 매칭)
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
              "물", "음료", "주스", "된장", "간장", "참기름", "들기름", "만두", "교자"]),
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


def ep_shorts_urls():
    """upload-queue.json에서 EP → 한국어 쇼츠 URL 맵 생성."""
    try:
        q = json.loads(QUEUE.read_text(encoding="utf-8"))
    except Exception:
        return {}
    urls = {}
    for e in q.get("queue", []):
        ep, url = e.get("ep"), e.get("published_url")
        if ep and url:
            urls[ep] = url
    return urls


CARD = """  <article class="card" data-cat="{cat}" data-name="{name_lower}">
    {badges}
    {img}
    <h3>{name}</h3>
    <p class="meta">{meta}</p>
    <p class="price">{price} <span class="pnote">{pnote}</span></p>
    <div class="btns">
      {cta}
      {video}
    </div>
  </article>
"""

PAGE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>든든한 장보기 — 영상으로 소개한 상품 모음</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Noto Sans KR", "Apple SD Gothic Neo", sans-serif;
    font-size: 20px; line-height: 1.6; color: #1a1a1a; background: #f7f4ee;
  }}
  .wrap {{ max-width: 600px; margin: 0 auto; padding: 0 16px 48px; }}
  header.top {{
    background: #2e5d33; color: #fff; border-radius: 0 0 24px 24px;
    padding: 28px 20px 24px; text-align: center; margin: 0 -16px 20px;
  }}
  .brand {{ font-size: 32px; font-weight: 800; margin: 0 0 6px; }}
  .tagline {{ font-size: 21px; margin: 0 0 14px; }}
  .disclosure {{
    display: inline-block; background: rgba(255,255,255,.16);
    font-size: 16px; line-height: 1.5; border-radius: 12px; padding: 10px 14px; margin: 0;
  }}
  .howto {{
    background: #fff; border: 3px solid #2e5d33; border-radius: 20px;
    padding: 20px; margin-bottom: 24px;
  }}
  .howto h2 {{ font-size: 26px; margin: 0 0 12px; text-align: center; }}
  .howto ol {{ margin: 0; padding-left: 8px; list-style: none; }}
  .howto li {{ font-size: 22px; margin: 12px 0; display: flex; align-items: center; gap: 12px; }}
  .step {{
    flex: 0 0 auto; width: 52px; height: 52px; border-radius: 50%;
    background: #2e5d33; color: #fff; font-size: 28px; font-weight: 800;
    display: inline-flex; align-items: center; justify-content: center;
  }}
  .toolbar {{
    position: sticky; top: 0; z-index: 10;
    background: #f7f4ee; padding: 12px 0 10px; margin: 0 -4px;
  }}
  .search {{
    width: 100%; font-size: 22px; padding: 16px 20px;
    border: 3px solid #2e5d33; border-radius: 999px; background: #fff;
    outline: none; -webkit-appearance: none;
  }}
  .search:focus {{ border-color: #1565c0; }}
  .chips {{
    display: flex; gap: 8px; overflow-x: auto; padding: 12px 2px 4px;
    -webkit-overflow-scrolling: touch; scrollbar-width: none;
  }}
  .chips::-webkit-scrollbar {{ display: none; }}
  .chip {{
    flex: 0 0 auto; font-size: 20px; font-weight: 700; cursor: pointer;
    padding: 10px 20px; border-radius: 999px; border: 2px solid #2e5d33;
    background: #fff; color: #2e5d33;
  }}
  .chip.on {{ background: #2e5d33; color: #fff; }}
  .count {{ text-align: center; color: #666; font-size: 18px; margin: 6px 0 14px; }}
  .card {{
    background: #fff; border-radius: 24px; padding: 20px; margin-bottom: 24px;
    box-shadow: 0 3px 14px rgba(0,0,0,.10); border: 1px solid #e8e2d5;
    position: relative;
  }}
  .badges {{ display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }}
  .badge {{
    font-size: 16px; font-weight: 800; padding: 4px 12px; border-radius: 999px;
  }}
  .badge.new {{ background: #e53935; color: #fff; }}
  .badge.cat {{ background: #ece7d9; color: #555; }}
  .pimg {{
    width: 100%; height: auto; aspect-ratio: 4 / 3; object-fit: contain;
    background: #fff; border: 1px solid #eee; border-radius: 16px; display: block;
  }}
  .card h3 {{ font-size: 26px; margin: 14px 0 8px; line-height: 1.4; }}
  .meta {{ font-size: 20px; color: #555; margin: 0 0 6px; }}
  .price {{ font-size: 30px; font-weight: 800; color: #b3261e; margin: 8px 0 16px; }}
  .pnote {{ display: block; font-size: 16px; font-weight: 400; color: #777; }}
  .btns {{ display: flex; flex-direction: column; gap: 10px; }}
  .cta {{
    display: block; text-align: center; text-decoration: none;
    background: #1565c0; color: #fff; font-size: 24px; font-weight: 800;
    padding: 18px 16px; border-radius: 18px;
  }}
  .cta:active {{ background: #0d47a1; }}
  .cta.off {{
    background: #e8e2d5; color: #888; pointer-events: none;
  }}
  .video {{
    display: block; text-align: center; text-decoration: none;
    background: #fff; color: #c62828; font-size: 21px; font-weight: 700;
    padding: 14px 16px; border-radius: 18px; border: 2px solid #c62828;
  }}
  .empty {{
    display: none; text-align: center; background: #fff; border-radius: 20px;
    padding: 40px 20px; font-size: 22px; color: #555;
  }}
  footer {{ text-align: center; margin-top: 36px; }}
  footer .disclosure {{ background: #ece7d9; color: #333; }}
  .totop {{
    display: inline-block; margin-top: 20px; font-size: 20px; color: #2e5d33;
    font-weight: 700; text-decoration: none; padding: 14px 28px;
    border: 2px solid #2e5d33; border-radius: 999px; background: #fff;
  }}
  .updated {{ text-align: center; color: #888; font-size: 16px; margin-top: 24px; }}
</style>
</head>
<body id="top">
<div class="wrap">

  <header class="top">
    <p class="brand">🧺 든든한 장보기</p>
    <p class="tagline">영상으로 소개한 상품을 한 곳에 모았어요</p>
    <p class="disclosure">{disclosure}</p>
  </header>

  <section class="howto">
    <h2>📱 구매 방법 (두 단계)</h2>
    <ol>
      <li><span class="step">1</span><span>원하는 상품 아래의 <strong>파란 버튼</strong>을 누르세요</span></li>
      <li><span class="step">2</span><span>쿠팡 페이지가 열리면 평소대로 구매하시면 됩니다</span></li>
    </ol>
  </section>

  <div class="toolbar">
    <input class="search" id="q" type="search" placeholder="🔍 상품 이름으로 찾기 (예: 귤, 라면)" autocomplete="off">
    <div class="chips" id="chips">
      <button class="chip on" data-cat="전체">전체</button>
{chips}
    </div>
  </div>
  <p class="count" id="count"></p>
  <main id="list">
{cards}  </main>
  <div class="empty" id="empty">찾으시는 상품이 없어요 😢<br>다른 이름으로 검색해 보세요.</div>

  <footer>
    <p class="disclosure">{disclosure}</p>
    <br>
    <a class="totop" href="#top">맨 위로 올라가기 ↑</a>
    <p class="updated">마지막 업데이트: {updated}</p>
  </footer>

</div>
<script>
(function () {{
  var q = document.getElementById('q');
  var cards = Array.prototype.slice.call(document.querySelectorAll('.card'));
  var chips = Array.prototype.slice.call(document.querySelectorAll('.chip'));
  var count = document.getElementById('count');
  var empty = document.getElementById('empty');
  var cat = '전체';
  function apply() {{
    var term = q.value.trim().toLowerCase();
    var shown = 0;
    cards.forEach(function (c) {{
      var okCat = (cat === '전체' || c.dataset.cat === cat);
      var okTerm = (!term || c.dataset.name.indexOf(term) !== -1);
      var show = okCat && okTerm;
      c.style.display = show ? '' : 'none';
      if (show) shown++;
    }});
    count.textContent = '총 ' + shown + '개 상품';
    empty.style.display = shown ? 'none' : 'block';
  }}
  q.addEventListener('input', apply);
  chips.forEach(function (chip) {{
    chip.addEventListener('click', function () {{
      chips.forEach(function (c) {{ c.classList.remove('on'); }});
      chip.classList.add('on');
      cat = chip.dataset.cat;
      apply();
    }});
  }});
  apply();
}})();
</script>
<!-- Cloudflare Web Analytics (방문자 통계, 2026-10-03 추가) -->
<script type='module' src='https://static.cloudflareinsights.com/beacon.min.js'
  data-cf-beacon='{{"token": "954984c2c2444153b49c68c9112377fd"}}'></script>
<!-- End Cloudflare Web Analytics -->
</body>
</html>
"""


def render_card(p, shorts_urls, today):
    name = p.get("name") or p.get("product") or ""
    cat = categorize(p)
    meta_bits = []
    if p.get("reviews"):
        meta_bits.append("상품평 " + str(p["reviews"]))
    if p.get("rating"):
        meta_bits.append("별점 " + str(p["rating"]))
    meta = " · ".join(meta_bits) if meta_bits else "쿠팡에서 자세한 정보를 확인하세요"
    price = esc(p.get("price") or "가격은 쿠팡에서 확인")
    pnote = ""
    if p.get("price") and p.get("price_checked"):
        pnote = "(%s 확인 · 가격은 변동될 수 있어요)" % esc(p["price_checked"])
    elif p.get("price"):
        pnote = "(가격은 변동될 수 있어요)"

    badges = []
    pdate = str(p.get("date") or "")
    try:
        d = date.fromisoformat(pdate)
        if (today - d) <= timedelta(days=7):
            badges.append('<span class="badge new">NEW</span>')
    except ValueError:
        pass
    badges.append('<span class="badge cat">%s</span>' % esc(cat))
    badges_html = '<div class="badges">%s</div>' % "".join(badges)

    img = ""
    if p.get("image"):
        img = '<img class="pimg" src="%s" alt="%s" loading="lazy">' % (
            esc(p["image"]), esc(name))

    url = p.get("url") or p.get("affiliate_link") or ""
    if url and url != "#":
        cta = '<a class="cta" href="%s">쿠팡에서 상품 보기</a>' % esc(url)
    else:
        cta = '<span class="cta off">쿠팡 링크 준비 중</span>'

    video = ""
    vurl = shorts_urls.get(p.get("ep") or "")
    if vurl:
        video = '<a class="video" href="%s">▶ 영상으로 보기</a>' % esc(vurl)

    return CARD.format(
        cat=esc(cat),
        name_lower=esc(name.lower()),
        badges=badges_html,
        img=img,
        name=esc(name),
        meta=esc(meta),
        price=price,
        pnote=esc(pnote),
        cta=cta,
        video=video,
    )


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    today = date.today()
    shorts_urls = ep_shorts_urls()
    # 빈 상품명 placeholder 제외
    products = [p for p in data["products"] if (p.get("name") or p.get("product"))]
    cards = "".join(render_card(p, shorts_urls, today) for p in products)
    used_cats = [c for c in CATEGORIES if any(categorize(p) == c for p in products)]
    chips = "\n".join(
        '      <button class="chip" data-cat="%s">%s</button>' % (esc(c), esc(c))
        for c in used_cats
    )
    updated = today.isoformat()
    page = PAGE.format(
        cards=cards,
        chips=chips,
        disclosure=esc(data.get("disclosure", "")),
        updated=esc(updated),
    )
    OUT.write_text(page, encoding="utf-8")
    print("wrote", OUT, "(%d products, cats: %s)" % (
        len(products), ", ".join(used_cats)))


if __name__ == "__main__":
    main()
