# 18 November 2026 — The Whole Day on One Front Page

[![make.fun](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/sintaameliaa-mee/makefun-news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/sintaameliaa-mee/makefun-news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118)

Entry for the [news-image-20261118](https://make.fun/bounty/news-image-20261118)
bounty on make.fun: one image summing up the world news of Wednesday
18 November 2026. This is a v2 rebuild in a dense newspaper front-page
format — 44 stories across 6 continents, every one verified against
reporting dated 18 November 2026.

## The image

A 1024x1024 front page, drawn programmatically with crisp rendered text —
no AI-generated lettering. Masthead and date, a big-numbers strip, 3 large
illustrated stories, 10 illustrated cards, a world map with numbered pins,
and a numbered list of the remaining stories.

The three lead stories:

1. **Gulf escalation** — Iran strikes US bases in Kuwait and Bahrain after
   US jets hit an IRGC missile site on Qeshm Island.
2. **Shenzhen summit** — Xi and Putin meet at APEC; the first
   Trump–Xi–Putin trilateral is set for Thursday.
3. **Anthropic IPO** — final price set today ahead of Thursday's Nasdaq
   debut (ANT), valued at up to ~$1.4 trillion.

Plus Ebola in DR Congo (11,000+ cases), Cyclone Xavier (Category 5,
315 km/h gusts), the US losing measles-elimination status, a wave of US
tech outages, falling markets, Korea's 3.9% growth upgrade, UK inflation
at 3.6%, 'human' as Cambridge's word of the year, Fiji's drought disaster,
Cricket Australia's sandpapergate forum — and 31 more in the list.

## How it runs

`main.py` (Python 3.13, standard library only) copies `entry.png` to
`/output/entry.png` (or `$MAKEFUN_OUTPUT_DIR/entry.png` when set), byte for
byte, so both runs produce identical output. No network. The image is
rendered by `draw.py` (Pillow, build-time only), kept in this repo.

## License

MIT — see [LICENSE](LICENSE).
