#!/usr/bin/env python3
"""든든한 장보기 링크 모음 페이지 생성기.

products.json -> index.html (GitHub Pages 배포용)
의존성 없음 (표준 라이브러리만 사용). JS 없음.
사용법: python3 bin/build.py
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "products.json"
OUT = ROOT / "index.html"


def esc(s):
    return html.escape(str(s or ""), quote=True)


CARD = """  <article class="card">
    <img class="pimg" src="{image}" alt="{name}" loading="lazy">
    <h3>{name}</h3>
    <p class="meta">{meta}</p>
    <p class="price">{price} <span class="pnote">{pnote}</span></p>
    <a class="cta" href="{url}">쿠팡에서 상품 보기</a>
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
    padding: 28px 20px 24px; text-align: center; margin: 0 -16px 24px;
  }}
  .brand {{ font-size: 32px; font-weight: 800; margin: 0 0 6px; }}
  .tagline {{ font-size: 21px; margin: 0 0 14px; }}
  .disclosure {{
    display: inline-block; background: rgba(255,255,255,.16);
    font-size: 16px; line-height: 1.5; border-radius: 12px; padding: 10px 14px; margin: 0;
  }}
  .howto {{
    background: #fff; border: 3px solid #2e5d33; border-radius: 20px;
    padding: 20px; margin-bottom: 28px;
  }}
  .howto h2 {{ font-size: 26px; margin: 0 0 12px; text-align: center; }}
  .howto ol {{ margin: 0; padding-left: 8px; list-style: none; }}
  .howto li {{ font-size: 22px; margin: 12px 0; display: flex; align-items: center; gap: 12px; }}
  .step {{
    flex: 0 0 auto; width: 52px; height: 52px; border-radius: 50%;
    background: #2e5d33; color: #fff; font-size: 28px; font-weight: 800;
    display: inline-flex; align-items: center; justify-content: center;
  }}
  h2.list-title {{ font-size: 28px; text-align: center; margin: 8px 0 20px; }}
  .card {{
    background: #fff; border-radius: 24px; padding: 20px; margin-bottom: 28px;
    box-shadow: 0 3px 14px rgba(0,0,0,.10); border: 1px solid #e8e2d5;
  }}
  .pimg {{
    width: 100%; height: auto; aspect-ratio: 4 / 3; object-fit: contain;
    background: #fff; border: 1px solid #eee; border-radius: 16px; display: block;
  }}
  .card h3 {{ font-size: 27px; margin: 16px 0 8px; line-height: 1.4; }}
  .meta {{ font-size: 20px; color: #555; margin: 0 0 6px; }}
  .price {{ font-size: 30px; font-weight: 800; color: #b3261e; margin: 8px 0 18px; }}
  .pnote {{ display: block; font-size: 16px; font-weight: 400; color: #777; }}
  .cta {{
    display: block; text-align: center; text-decoration: none;
    background: #1565c0; color: #fff; font-size: 24px; font-weight: 800;
    padding: 20px 16px; border-radius: 18px; min-height: 76px;
  }}
  .cta:active {{ background: #0d47a1; }}
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

  <h2 class="list-title">🛒 추천 상품 목록</h2>
  <main>
{cards}  </main>

  <footer>
    <p class="disclosure">{disclosure}</p>
    <br>
    <a class="totop" href="#top">맨 위로 올라가기 ↑</a>
    <p class="updated">마지막 업데이트: {updated}</p>
  </footer>

</div>
<!-- Cloudflare Web Analytics (방문자 통계, 2026-10-03 추가) -->
<script type='module' src='https://static.cloudflareinsights.com/beacon.min.js'
  data-cf-beacon='{{"token": "954984c2c2444153b49c68c9112377fd"}}'></script>
<!-- End Cloudflare Web Analytics -->
</body>
</html>
"""


def render_card(p):
    meta_bits = []
    if p.get("reviews"):
        meta_bits.append("상품평 " + p["reviews"])
    if p.get("rating"):
        meta_bits.append("별점 " + p["rating"])
    meta = " · ".join(meta_bits) if meta_bits else "쿠팡에서 자세한 정보를 확인하세요"
    price = esc(p.get("price") or "가격은 쿠팡에서 확인")
    pnote = ""
    if p.get("price") and p.get("price_checked"):
        pnote = "(%s 확인 · 가격은 변동될 수 있어요)" % esc(p["price_checked"])
    elif p.get("price"):
        pnote = "(가격은 변동될 수 있어요)"
    return CARD.format(
        image=esc(p.get("image", "")),
        name=esc(p.get("name", "상품")),
        meta=esc(meta),
        price=price,
        pnote=esc(pnote),
        url=esc(p.get("url", "#")),
    )


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    cards = "".join(render_card(p) for p in data["products"])
    page = PAGE.format(
        cards=cards,
        disclosure=esc(data.get("disclosure", "")),
        updated=esc(data.get("updated", "")),
    )
    OUT.write_text(page, encoding="utf-8")
    print("wrote", OUT, "(%d products)" % len(data["products"]))


if __name__ == "__main__":
    main()
