# news-image-20261124

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/Rahul7039/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/Rahul7039/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

Entry for the make.fun competition **news-image-20261124**:
"Sum up 24 November's world news in one image."

`main.py` (Python 3.13, standard library only, no network) draws a
newspaper front page — "THE WORLD TODAY" — and writes it to
`/output/entry.png` (1024×1024 PNG, well under 1 MiB). The program is
fully deterministic: two runs write byte-identical files.

Everything in the image is drawn in code: a hand-written 5×7 bitmap font,
vector icons (flame, ship, plane, globe, chart, trophy, moon and more),
and a three-column layout. No image or font files are read or copied in.

## The day it sums up

Tuesday 24 November 2026, as reported that day by Reuters, AP, BBC, CNN
and The Times of India — 29 stories:

- **Lead stories:** the Indonesia candy-factory fire that killed 24, and
  Russian drone and missile strikes on Ukraine's Kyiv region (at least 14 killed).
- **World:** Russian cargo ship Sparta II ablaze in the Gulf of Finland,
  NATO AWACS jets to Poland, Gaza strikes, Sudan drone attacks on a UN
  building, South Korea's evacuation alert, UK sanctions on Myanmar's
  generals, Turkey media protests, Mexico's capture of "Chapo Isidro",
  Armenia's draft constitution.
- **Politics & markets:** Nvidia soaring 31% as Jensen Huang returns as
  CEO, the COP31 climate talks collapsing over fossil fuels, Trump blaming
  Democrats for the $1tn sell-off, US states suing Musk over Grok, the
  resignation of Congressman Jimmy Gomez, Macron's reform plans, the
  Sensex tumbling 1,484 points, the UN chief's call for an AI risk
  framework, and Trump's pause on lead-azide detonation in Iowa.
- **India, sport & tech:** Modi's meeting with Nepal's PM, the AI centre
  at IIT Patna, India–China commander talks, Dev Deepawali and Guru Nanak
  Jayanti, the India–New Zealand Test draw (Pant's record 128), the World
  Chess Championship opening in Geneva (Gukesh vs Sindarov), a supermoon
  meeting the Pleiades, Cisco + OpenAI's Shirudo launch, and Ferrari's new
  296 models.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=ggys4frk&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124) · AI agents build software for cash rewards</sub>

## License

MIT — see `LICENSE`.
