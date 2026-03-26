"""Rebuild docs/index.html — light-mode Olympic-themed design with LT translation."""
import os
ROOT = os.path.join(os.path.dirname(__file__), "..")
with open(os.path.join(ROOT, "docs", "_js_block.txt"), encoding="utf-8") as f:
    JS = f.read()

RINGS = '<span class="or"></span>' * 5

# ── Translation script — backtick template literals avoid all quote/apostrophe issues ──
TRANS_JS = """
<script>
var LANG = 'en';
var T = {
  en: {
    'nav-forecast':       `Forecast`,
    'nav-athletes':       `Athletes`,
    'nav-simulator':      `Simulator`,
    'nav-analysis':       `Analysis`,
    'nav-data':           `Data`,
    'nav-expected-lbl':   `Expected medals:`,
    'hero-title':         `Lithuania\u2005<span class="edition">LA\u00a02028</span><br>Olympic Medal Forecast`,
    'hero-tagline':       `Sport-by-sport prediction built from Olympedia historical data (1992\u20132024), the known athlete pipeline, and a correlated Monte Carlo simulation.`,
    'hero-datasrc':       `Olympedia 1992\u20132020 \u2022 IOC Paris 2024 \u2022 Bayesian shrinkage \u2022 10,000-run Monte Carlo \u2022 Gaussian copula \u03c1=0.15`,
    'sec-forecast':       `2028 Forecast`,
    'sub-forecast':       `Baseline scenario \u2014 use the Simulator below to adjust funding, athletes, and conditions`,
    'lbl-expected':       `Expected medals`,
    'lbl-range':          `Likely range`,
    'sub-range':          `P10 \u2013 P90`,
    'lbl-zero':           `Zero-medal risk`,
    'sub-zero-static':    `current settings`,
    'lbl-athletics':      `Athletics`,
    'sub-athletics':      `Alekna \u2014 gold favourite`,
    'lbl-paris':          `Paris 2024 actual`,
    'sub-paris':          `incl. Breaking silver`,
    'lbl-beet':           `\u0160altibar\u0161\u010diai Index`,
    'sub-beet':           `Post-medal ceremony probability`,
    'tbl-title':          `Sport-by-Sport Detail`,
    'sec-athletes':       `Key Athletes \u2014 LA 2028 Contenders`,
    'sub-athletes':       `Primary medal candidates driving the per-sport probabilities above`,
    'warn-breaking':      `<strong>Breaking is NOT on the LA 2028 programme.</strong> NICKA (Dominyka Banevic) won Silver at Paris 2024, but the IOC removed Breaking from the 2028 Games. Lithuania's 2028 forecast is calculated without this sport. <em style="opacity:.7">&nbsp; Source: IOC Programme Commission, 2023.</em>`,
    'sec-simulator':      `Interactive Simulator`,
    'sub-simulator':      `Adjust funding, athlete status, and conditions \u2014 charts update live. The forecast table above also updates.`,
    'ctrl-core':          `Core controls`,
    'lbl-funding':        `Funding multiplier`,
    'lbl-sports':         `Sports to include \u2014 click to toggle off / on`,
    'adv-title':          `Advanced Factors \u2014 athlete status, programme & external conditions`,
    'adv-ath-head':       `Athlete Status`,
    'adv-prog-head':      `Programme & Investment`,
    'adv-ext-head':       `External Conditions`,
    'lbl-alekna':         `Mykolas Alekna`,
    'lbl-meilutyte':      `Ruta Meilutyte`,
    'lbl-bball':          `3x3 Basketball roster`,
    'lbl-pipeline':       `Youth pipeline`,
    'lbl-focus':          `Focus mode`,
    'lbl-deleg':          `Delegation size`,
    'lbl-coaching':       `Coaching & support quality`,
    'lbl-peaking':        `Competition peaking`,
    'lbl-host':           `Host nation effect (LA 2028)`,
    'lbl-gdp':            `GDP & budget scenario`,
    'lbl-rho':            `Cross-sport correlation \u03c1`,
    'lbl-saltibarciai':   `\u0160altibar\u0161\u010diai protocol (+\u221e%)`,
    'chart-mc-title':     `Medal Count Distribution`,
    'chart-mc-cap':       `Exact Poisson-binomial probability at current settings`,
    'chart-hist-title':   `Historical Performance 1992\u20132024`,
    'chart-hist-cap':     `Red star = 2028 forecast with P10\u2013P90 error bar`,
    'chart-type-title':   `Medal Type Breakdown`,
    'chart-type-cap':     `Estimated gold / silver / bronze split per sport`,
    'chart-scen-title':   `Scenario Comparison`,
    'chart-scen-cap':     `Baseline, 2x & 3x funding vs current settings (red bar)`,
    'chart-peers-title':  `Peer Country Comparison \u2014 Paris 2024`,
    'chart-peers-cap':    `Lithuania vs similar small European nations`,
    'sec-analysis':       `Model Analysis`,
    'sub-analysis':       `How each probability is built \u2014 athlete decomposition and pipeline`,
    'chart-decomp-title': `Athlete Model vs Historical Rate`,
    'chart-decomp-cap':   `Grey = recency-weighted historical win rate \u2022 Blue = athlete ranking model \u2022 Red diamond = final blended estimate`,
    'pipe-title':         `Athlete Pipeline & World Rankings`,
    'pipe-cap':           `Event medal prob = rank_prob \u00d7 psych_factor \u00d7 age_factor. Union across contenders gives sport probability.`,
    'emerging-title':     `Emerging Athletes \u2014 Not in Current Model`,
    'emerging-cap':       `Competed at Paris 2024, prime age in 2028, no identified medal path yet.`,
    'breaststroke-title': `50m Breaststroke \u2014 Confirmed for LA 2028`,
    'breaststroke-cap':   `World Aquatics confirmed 50m breaststroke (+ backstroke + butterfly) for LA 2028 (Apr 2025). Meilutyte is the world record holder and 2023 World Champion. Her probability in this event alone is estimated at 42%.`,
    'footer-sources':     `Data sources:`,
    'footer-gen':         `Generated 2026-03-26`,
    'chart-sports-title': `Per-Sport Medal Probability`,
    'chart-sports-cap':   `Grey = historical win rate \u2022 Coloured = 2028 estimate \u2022 Updates with all simulator controls`,
    'th-sport':           `Sport`,
    'th-prob':            `2028 Prob`,
    'th-hist':            `Historical`,
    'th-years':           `Medal years`,
    'th-outlook':         `Outlook`,
    'th-notes':           `Notes`,
    'th-athlete':         `Athlete`,
    'th-event':           `Event`,
    'th-rank':            `Rank`,
    'th-age2028':         `Age 2028`,
    'th-factor':          `Factor`,
    'th-born':            `Born`,
    'th-status':          `Status`,
    'pill-gold':          `Gold contender`,
    'pill-realistic':     `Realistic`,
    'pill-possible':      `Possible`,
    'pill-darkhorse':     `Dark horse`,
    'sport-athletics':    `Athletics`,
    'sport-rowing':       `Rowing`,
    'sport-swimming':     `Swimming`,
    'sport-bball':        `3x3 Basketball`,
    'sport-pentathlon':   `Modern Pentathlon`,
    'sport-weightlifting':`Weightlifting`,
    'sport-wrestling':    `Wrestling`,
    'sport-shooting':     `Shooting`,
    'sport-canoe':        `Canoe Sprint`,
    'note-athletics':     `Mykolas Alekna (25 in 2028): Olympic silver 2024, world lead 74.35m. Top global gold favourite. Gudzius may also compete (Rio 2016 gold).`,
    'note-rowing':        `Viktorija Senkute (32 in 2028): Olympic bronze 2024 (W Single Sculls). Born 1996, near peak sculling age.`,
    'note-swimming':      `Ruta Meilutyte (31 in 2028): WR holder 50m breast, Olympic gold 2012, psych factor applied. Danas Rapsys (33): multiple Olympic A-finals.`,
    'note-bball':         `Olympic bronze 2024. Core roster ages 31\u201341 in 2028 \u2014 roster continuity uncertain.`,
    'note-pentathlon':    `Asadauskaite (44 in 2028): virtually certain to have retired. Venckauskaite (35\u201336) is the only pipeline.`,
    'note-weightlifting': `Aurimas Didzbalis bronze 2016. Programme affected by IWF sanctions era. No confirmed 2028 contender.`,
    'note-wrestling':     `Two medals in 2008 and 2012. Gabija Dilyte (25 in 2028) is a developing prospect.`,
    'note-shooting':      `Last medal: Daina Gudzineviciute, Trap Gold 2000. No current ISSF top-20 Lithuanian shooter identified.`,
    'note-canoe':         `2016 bronze (K2-200m). No confirmed 2028 contender identified yet.`,
    'acard1-sport':       `Athletics \u2014 Discus Throw`,
    'acard1-desc':        `Top global gold favourite. Olympic silver Paris 2024 aged 21. World lead 74.35m in 2024. Father Virgilijus won discus gold 2000 & 2004. Born Sept 2002 \u2014 will be 25 at LA 2028, absolute prime.`,
    'acard1-stat':        `Paris 2024: Silver \u2022 74.35m WL \u2022 Age in 2028: 25`,
    'acard2-sport':       `Rowing \u2014 Women's Single Sculls`,
    'acard2-desc':        `Olympic bronze Paris 2024. Born 1996, age 32 in 2028 \u2014 near peak sculling age. Consistent top-3 on World Cup circuit. Psych factor: normal (consistent Olympic performer).`,
    'acard2-stat':        `Paris 2024: Bronze \u2022 Born 1996 \u2022 Age in 2028: 32`,
    'acard3-sport':       `Swimming`,
    'acard3-desc':        `Meilutyte: 50m breast world record holder, Olympic gold 2012, still active at 31 in 2028. Psych discount applied (Olympic underperformer). Rapsys: 3 Olympic A-finals, age 33 in 2028.`,
    'acard3-stat':        `Meilutyte age: 31 \u2022 Rapsys age: 33 \u2022 Two podium paths`,
    'acard4-sport':       `3x3 Basketball \u2014 Men's Team`,
    'acard4-desc':        `Olympic bronze 2024. Core roster ages 31\u201341 in 2028 \u2014 roster continuity is the key uncertainty. Basketball is Lithuania's structural sport; FIBA 3x3 consistent global top-10.`,
    'acard4-stat':        `Paris 2024: Bronze \u2022 FIBA 3x3 World Ranking: top-10`,
    'acard5-sport':       `Modern Pentathlon`,
    'acard5-desc':        `Born 1992, age 35\u201336 in 2028 \u2014 late career. Same generation as Asadauskaite (born 1984, age 44, retired). No confirmed next-generation pentathlete identified.`,
    'acard5-stat':        `Born 1992 \u2022 Age in 2028: 35\u201336 \u2022 Asadauskaite: retired`,
    'factor-normal':      `Normal`,
    'factor-disc':        `Slight discount`,
    'factor-poor':        `Olympic underperformer`,
    'pe-discus':          `Discus Men`,
    'pe-sculls':          `W Single Sculls`,
    'pe-dsculls':         `M Double Sculls`,
    'pe-100breast':       `100m Breaststroke`,
    'pe-200free':         `200m Freestyle Men`,
    'pe-3x3':             `3x3 Basketball`,
    'pe-wpentathlon':     `Women's Pentathlon`,
    'pe-wwrestling':      `Women's Wrestling`,
    'pn-alekna':          `World #1 2024, 74.35m WL, Olympic silver 2024 (aged 21).`,
    'pn-senkute':         `Olympic bronze 2024, born 1996, age 32 in 2028.`,
    'pn-stankunas':       `Domantas & Dovydas, Paris 2024 participants.`,
    'pn-meilutyte':       `WR holder 50m breast, top-5 100m. Last medal: gold 2012.`,
    'pn-rapsys':          `European champion, 3 Olympic A-finals. Age 33 in 2028.`,
    'pn-bball':           `Olympic bronze 2024. Roster continuity uncertain.`,
    'pn-venckauskaite':   `Born 1992, age 35-36 in 2028 -- late career.`,
    'pn-dilyte':          `Born 2003, age 25 in 2028. Paris 2024 participant, developing.`,
    'pill-prime2028':     `Prime 2028`,
    'sport-bvolley':      `Beach Volleyball`,
    'sport-cycling':      `Cycling Track`,
    'scenario-box':       `<strong>Default model (50m breast confirmed):</strong> Swimming \u2248 44%<br><strong>100m breast only scenario:</strong> Swimming = 27%<br><strong>Source:</strong> World Aquatics confirmed Apr 2025<br><strong>Status:</strong> <span style="color:var(--green);font-weight:700">\u2713 CONFIRMED for LA 2028</span>`,
    'scenario-note':      `Psych factor 0.85 applied (Olympic underperformer vs world ranking). Last Olympic medal: gold 2012. Use the Meilutyte dropdown in Advanced Factors to switch back to 100m breast only scenario.`,
  },
  lt: {
    'nav-forecast':       `Prognoz\u0117`,
    'nav-athletes':       `Sportininkai`,
    'nav-simulator':      `Simuliatorius`,
    'nav-analysis':       `Analiz\u0117`,
    'nav-data':           `Duomenys`,
    'nav-expected-lbl':   `Tik\u0117tini medaliai:`,
    'hero-title':         `Lietuva\u2005<span class="edition">LA\u00a02028</span><br>olimpini\u0173 medali\u0173 prognoz\u0117`,
    'hero-tagline':       `Prognoz\u0117 kiekvienai sporto \u0161akai, pagrista Olympedia istoriniais duomenimis (1992\u20132024), \u017einomu sportinink\u0173 pajegumo vertinimu ir koreliuotu Monte Carlo modeliu.`,
    'hero-datasrc':       `Olympedia 1992\u20132020 \u2022 IOC Pary\u017eius 2024 \u2022 Bajeso susiaurimas \u2022 10\u00a0000 Monte Carlo band. \u2022 Gauso kopula \u03c1=0.15`,
    'sec-forecast':       `2028 Prognoz\u0117`,
    'sub-forecast':       `Bazinis scenarijus \u2014 naudokite simuliatoriumi \u017eemiau, kad keistum\u0117te finansavim\u0105, sportininkus ir s\u0105lygas`,
    'lbl-expected':       `Tik\u0117tini medaliai`,
    'lbl-range':          `Tik\u0117tinas diapazonas`,
    'sub-range':          `P10 \u2013 P90`,
    'lbl-zero':           `Nulio medali\u0173 rizika`,
    'sub-zero-static':    `dabartiniai nustatymai`,
    'lbl-athletics':      `Lengvoji atletika`,
    'sub-athletics':      `Alekna \u2014 auksinio medalio favoritas`,
    'lbl-paris':          `Pary\u017eius 2024 faktai`,
    'sub-paris':          `\u012fskaitant Breaking sidabr\u0105`,
    'lbl-beet':           `\u0160altibar\u0161\u010di\u0173 indeksas`,
    'sub-beet':           `Tikimyb\u0117 po medalio ceremonijos`,
    'tbl-title':          `Sporto \u0161ak\u0173 detalus pj\u016bvis`,
    'sec-athletes':       `Pagrindiniai sportininkai \u2014 LA 2028 pretendentai`,
    'sub-athletes':       `Pagrindiniai medalio pretendentai`,
    'warn-breaking':      `<strong>Breaking N\u0116RA LA 2028 program\u0173.</strong> NICKA (Dominyka Banevi\u010d) laimejo silver\u0105 Pary\u017eiuje 2024, ta\u010diau TOK pa\u0161alino Breaking i\u0161 2028 \u017eaidyni\u0173. Lietuva 2028 prognoz\u0117 skai\u010diuojama be \u0161ios sporto \u0161akos.`,
    'sec-simulator':      `Interaktyvus simuliatorius`,
    'sub-simulator':      `Keiskite finansavim\u0105, sportinink\u0173 status\u0105 ir s\u0105lygas \u2014 diagramos atnaujinamos realiuoju laiku.`,
    'ctrl-core':          `Pagrindiniai valdikliai`,
    'lbl-funding':        `Finansavimo koeficientas`,
    'lbl-sports':         `Sporto \u0161akos \u2014 spauskite nor\u0117dami \u012fjungti / i\u0161jungti`,
    'adv-title':          `Papildomi veiksniai \u2014 sportinink\u0173 statusas, programa ir i\u0161orin\u0117s s\u0105lynos`,
    'adv-ath-head':       `Sportinink\u0173 statusas`,
    'adv-prog-head':      `Programa ir investicijos`,
    'adv-ext-head':       `I\u0161orin\u0117s s\u0105lynos`,
    'lbl-alekna':         `Mykolas Alekna`,
    'lbl-meilutyte':      `R\u016bta Meilutyt\u0117`,
    'lbl-bball':          `3x3 krep\u0161inio rinktin\u0117`,
    'lbl-pipeline':       `Jaunimo programa`,
    'lbl-focus':          `Focus re\u017eimas`,
    'lbl-deleg':          `Delegacijos dydis`,
    'lbl-coaching':       `Treniravimo ir aptarnavimo kokyb\u0117`,
    'lbl-peaking':        `Var\u017eyb\u0173 forma`,
    'lbl-host':           `Kini\u0173 efektas (LA 2028)`,
    'lbl-gdp':            `BVP ir biud\u017eeto scenarijus`,
    'lbl-rho':            `Sporto koreliacijos koeficientas \u03c1`,
    'lbl-saltibarciai':   `\u0160altibar\u0161\u010di\u0173 protokolas (+\u221e%)`,
    'chart-mc-title':     `Medali\u0173 skai\u010diaus pasiskirstymas`,
    'chart-mc-cap':       `Tikslus Puasono-binominis pasiskirstymas esamomis s\u0105lynomis`,
    'chart-hist-title':   `Istoriniai rezultatai 1992\u20132024`,
    'chart-hist-cap':     `Raudona \u017evaigzd\u0117 = 2028 prognoz\u0117 su P10\u2013P90 paklaida`,
    'chart-type-title':   `Medali\u0173 tip\u0173 pasiskirstymas`,
    'chart-type-cap':     `Numatomas auksas / sidabras / bronza pagal sporto \u0161ak\u0105`,
    'chart-scen-title':   `Scenarijaus palyginimas`,
    'chart-scen-cap':     `Bazinis, 2x ir 3x finansavimas vs dabartiniai nustatymai`,
    'chart-peers-title':  `\u0160ali\u0173 palyginimas \u2014 Pary\u017eius 2024`,
    'chart-peers-cap':    `Lietuva vs pana\u0161ios ma\u017eosios Europos \u0161alys`,
    'sec-analysis':       `Modelio analiz\u0117`,
    'sub-analysis':       `Kaip kiekviena tikimyb\u0117 yra sukonstruota`,
    'chart-decomp-title': `Sportinink\u0173 modelis vs. istorinis rodiklis`,
    'chart-decomp-cap':   `Pilka = istorinis laimejimo rodiklis \u2022 M\u0117lyna = sportinink\u0173 modelis \u2022 Raudona = galutinis \u012fvertinimas`,
    'pipe-title':         `Sportinink\u0173 programa ir pasaulio reitingai`,
    'pipe-cap':           `Renginio medali\u0173 tikimyb\u0117 = rank_prob \u00d7 psych_factor \u00d7 age_factor.`,
    'emerging-title':     `Kylantys sportininkai \u2014 n\u0117ra dabartiniame modelyje`,
    'emerging-cap':       `Dalyvavo Pary\u017eiuje 2024, geriausi am\u017eiuje 2028, kol kas be medalio kelio.`,
    'breaststroke-title': `50 m kr\u016btine \u2014 patvirtinta LA 2028`,
    'breaststroke-cap':   `Pasaulio vandens sportas patvirtino 50 m kr\u016btine (+ nugaros, drugelio) LA 2028 (2025 bal.). Meilutyt\u0117 turi pasaulio rekord\u0105 ir laimejo 2023 m. pasaulio \u010dempionat\u0105. Tikimyb\u0117 \u0161iame renginyje atskirai \u2248 42%.`,
    'footer-sources':     `Duomen\u0173 \u0161altiniai:`,
    'footer-gen':         `Sugeneruota 2026-03-26`,
    'chart-sports-title': `Medal\u0173 tikimyb\u0117 pagal sporto \u0161ak\u0105`,
    'chart-sports-cap':   `Pilka = istorinis laim\u0117jim\u0173 rodiklis \u2022 Spalvota = 2028 \u012fvertinimas \u2022 Atnaujinama pagal simuliatoriaus nustatymus`,
    'th-sport':           `Sporto \u0161aka`,
    'th-prob':            `2028 Tikimyb\u0117`,
    'th-hist':            `Istorinis`,
    'th-years':           `Medal\u0173 metai`,
    'th-outlook':         `Perspektyva`,
    'th-notes':           `Pastabos`,
    'th-athlete':         `Sportininkas`,
    'th-event':           `Renginys`,
    'th-rank':            `Reitingas`,
    'th-age2028':         `Am\u017eius 2028`,
    'th-factor':          `Veiksnys`,
    'th-born':            `Gim\u0117`,
    'th-status':          `Statusas`,
    'pill-gold':          `Aukso pretendentas`,
    'pill-realistic':     `Realus`,
    'pill-possible':      `\u012emanoma`,
    'pill-darkhorse':     `Tamsus arklys`,
    'sport-athletics':    `Lengvoji atletika`,
    'sport-rowing':       `Irklavimas`,
    'sport-swimming':     `Plaukimas`,
    'sport-bball':        `3x3 krep\u0161inis`,
    'sport-pentathlon':   `\u0160iuolaikin\u0117 penkiakov\u0117`,
    'sport-weightlifting':`Sunkioji atletika`,
    'sport-wrestling':    `Imtyni\u0173 sportas`,
    'sport-shooting':     `\u0160audyba`,
    'sport-canoe':        `Baidar\u0117i\u0173 sportas`,
    'note-athletics':     `Mykolas Alekna (25 m. 2028): olimpinis sidabras 2024, pasaulio rekordas 74,35 m. Pagrindinis auksinio medalio favoritas pasaulyje. Gudzius taip pat gali dalyvauti (Rio 2016 auksas).`,
    'note-rowing':        `Viktorija Senkut\u0117 (32 m. 2028): olimpin\u0117 bronza 2024 (moter\u0173 vienviet\u0117 irklelė). Gimusi 1996 m., artimas piko am\u017eius.`,
    'note-swimming':      `R\u016bta Meilutyt\u0117 (31 m. 2028): 50 m kr\u016btine pasaulio rekordinink\u0117, olimpinis auksas 2012, taikytas psichologinis diskonto koeficientas. Danas Rapšys (33 m.): 3 olimpiniai A finalai.`,
    'note-bball':         `Olimpin\u0117 bronza 2024. Pagrindinio sudėties narių am\u017eius 31\u201341 m. 2028 \u2014 sudėties tęstinumas neaiškus.`,
    'note-pentathlon':    `Asadauskait\u0117 (44 m. 2028): beveik tikrai bus pasitraukusi. Venckauskaite (35\u201336 m.) yra vienintelis rezervas.`,
    'note-weightlifting': `Aurimas Didzbalis bronza 2016. Programa nukentėjo dėl TSF sankcijų eros. N\u0117ra patvirtinto 2028 pretendento.`,
    'note-wrestling':     `Du medaliai 2008 ir 2012 m. Gabija Dilyt\u0117 (25 m. 2028) yra perspektyvus jaunasis sportininkas.`,
    'note-shooting':      `Paskutinis medalis: Daina Gudzinevičiūtė, Trap auksas 2000 m. N\u0117ra identifikuoto dabartinio ISSF top-20 lietuvi\u0173 šaulio.`,
    'note-canoe':         `2016 bronza (K2-200 m). Kol kas n\u0117ra patvirtinto 2028 pretendento.`,
    'acard1-sport':       `Lengvoji atletika \u2014 disko metimas`,
    'acard1-desc':        `Pagrindinis auksinio medalio favoritas pasaulyje. Olimpinis sidabras Paryžiuje 2024 sulaukęs 21 metų. Pasaulio rekordas 74,35 m 2024 m. T\u0117vas Virgilijus laimojo disko auksą 2000 ir 2004 m. Gimęs 2002 rugsėjį \u2014 LA 2028 bus 25 metų, absoliutus piko amžius.`,
    'acard1-stat':        `Paryžius 2024: Sidabras \u2022 74,35 m PLR \u2022 Amžius 2028: 25`,
    'acard2-sport':       `Irklavimas \u2014 moter\u0173 vienviet\u0117 irklelė`,
    'acard2-desc':        `Olimpin\u0117 bronza Paryžiuje 2024. Gimusi 1996 m., 32 metų 2028 m. \u2014 artimas piko amžius irklavime. Nuoseklus top-3 Pasaulio taurės etapuose. Psichologinis veiksnys: normalus (nuoseklus olimpinis dalyvis).`,
    'acard2-stat':        `Paryžius 2024: Bronza \u2022 Gimusi 1996 \u2022 Amžius 2028: 32`,
    'acard3-sport':       `Plaukimas`,
    'acard3-desc':        `Meilutytė: 50 m krūtine pasaulio rekordininkė, olimpinis auksas 2012, vis dar aktyviai sportuoja, 31 metų 2028 m. Taikytas psichologinis diskonto koeficientas (olimpinis nepasirodė gerai). Rapšys: 3 olimpiniai A finalai, 33 metų 2028 m.`,
    'acard3-stat':        `Meilutytės amžius: 31 \u2022 Rapšio amžius: 33 \u2022 Du medalio keliai`,
    'acard4-sport':       `3x3 krep\u0161inis \u2014 vyrų komanda`,
    'acard4-desc':        `Olimpin\u0117 bronza 2024. Pagrindinio sudėties narių amžius 31\u201341 m. 2028 m. \u2014 sudėties tęstinumas yra pagrindinė neapibrėžtybė. Krepšinis yra Lietuvos struktūrinis sportas; FIBA 3x3 nuolat pasauliniame top-10.`,
    'acard4-stat':        `Paryžius 2024: Bronza \u2022 FIBA 3x3 pasaulio reitingas: top-10`,
    'acard5-sport':       `\u0160iuolaikin\u0117 penkiakovė`,
    'acard5-desc':        `Gimusi 1992 m., 35\u201336 metų 2028 m. \u2014 vėlyvoji karjera. Ta pati karta kaip Asadauskaitė (gimusi 1984 m., 44 metų, pasitraukusi). N\u0117ra patvirtinto kitos kartos penkiakovininkės.`,
    'acard5-stat':        `Gimusi 1992 \u2022 Am\u017eius 2028: 35\u201336 \u2022 Asadauskait\u0117: pasitraukusi`,
    'factor-normal':      `Normalus`,
    'factor-disc':        `Nedidelis diskonto koef.`,
    'factor-poor':        `Olimpi\u0161kai nepasirod\u0117 gerai`,
    'pe-discus':          `Disko metimas (vyrai)`,
    'pe-sculls':          `Mot. vienviet\u0117 irklelė`,
    'pe-dsculls':         `Vyr. dviviet\u0117 irklelė`,
    'pe-100breast':       `100 m kr\u016btine`,
    'pe-200free':         `200 m laisvuoju stiliumi (vyrai)`,
    'pe-3x3':             `3x3 krep\u0161inis`,
    'pe-wpentathlon':     `Mot. penkiakov\u0117`,
    'pe-wwrestling':      `Mot. imtyn\u0117s`,
    'pn-alekna':          `Pasaulio #1 2024, 74,35 m PLR, olimpinis sidabras 2024 (21 m.).`,
    'pn-senkute':         `Olimpin\u0117 bronza 2024, gimusi 1996, 32 m. 2028-aisiais.`,
    'pn-stankunas':       `Domantas ir Dovydas, Pary\u017eiaus 2024 dalyviai.`,
    'pn-meilutyte':       `50 m kr\u016btine pasaulio rekordinink\u0117, top-5 100 m. Paskutinis medalis: auksas 2012.`,
    'pn-rapsys':          `Europos \u010dempionas, 3 olimpiniai A finalai. 33 m. 2028-aisiais.`,
    'pn-bball':           `Olimpin\u0117 bronza 2024. Sud\u0117ties t\u0119stinumas neai\u0161kus.`,
    'pn-venckauskaite':   `Gimusi 1992, 35\u201336 m. 2028 \u2014 v\u0117lyvoji karjera.`,
    'pn-dilyte':          `Gimusi 2003, 25 m. 2028. Pary\u017eiaus 2024 dalyv\u0117, tobul\u0117janti.`,
    'pill-prime2028':     `Pikas 2028`,
    'sport-bvolley':      `Pap\u016bdimio tinklinis`,
    'sport-cycling':      `Dviratininkyst\u0117 (treko)`,
    'scenario-box':       `<strong>Numatytasis modelis (50 m kr\u016btine patvirtinta):</strong> Plaukimas \u2248 44%<br><strong>Tik 100 m kr\u016btine scenarijus:</strong> Plaukimas = 27%<br><strong>\u0160altinis:</strong> Pasaulio vandens sportas patvirtino 2025 bal.<br><strong>Statusas:</strong> <span style="color:var(--green);font-weight:700">\u2713 PATVIRTINTA LA 2028</span>`,
    'scenario-note':      `Taikytas psichologinis diskonto koef. 0,85 (olimpi\u0161kai nepasirod\u0117 gerai). Paskutinis olimpinis medalis: auksas 2012. Naudokite Meilutyt\u0117s i\u0161skleidim\u0105 Papildomuose veiksniuose nor\u0117dami gr\u012f\u017eti prie tik 100 m kr\u016btine scenarijaus.`,
  }
};

function setLang(l) {
  LANG = l;
  document.querySelectorAll('[data-i18n]').forEach(function(el) {
    var k = el.getAttribute('data-i18n');
    if (T[l] && T[l][k] !== undefined) el.textContent = T[l][k];
  });
  document.querySelectorAll('[data-i18n-html]').forEach(function(el) {
    var k = el.getAttribute('data-i18n-html');
    if (T[l] && T[l][k] !== undefined) el.innerHTML = T[l][k];
  });
  var btn = document.getElementById('lang-btn');
  if (btn) btn.textContent = (l === 'en') ? 'LT' : 'EN';
  if (typeof updateAll === 'function') updateAll();
  if (typeof renderStaticCharts === 'function') renderStaticCharts();
}
function toggleLang() { setLang(LANG === 'en' ? 'lt' : 'en'); }
</script>
"""

CSS = """
:root{
  --bg:#e8e3d8;
  --card:#ffffff;
  --card2:#edeae4;
  --border:#d4cec6;
  --text:#1c1a2a;
  --muted:#70688a;
  --gold:#a07800;
  --gold2:#c09010;
  --silver:#505870;
  --bronze:#7a4c18;
  --accent:#1e4eb8;
  --accent2:#2860d8;
  --green:#186038;
  --orange:#b85e10;
  --red:#a01818;
  --beet:#b02860;
  --r:12px;
  --rr:18px;
}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--text);
  font-family:'Segoe UI',system-ui,-apple-system,sans-serif;
  font-size:14px;line-height:1.5}

::-webkit-scrollbar{width:6px;height:6px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px}

/* ── OLYMPIC RINGS — proper 3-top / 2-bottom layout ─────────────────── */
.oring{position:relative;display:inline-block;vertical-align:middle}
.or{position:absolute;border-radius:50%;border-style:solid}
/* SM  d=14  s=16  v=9  total-w=46  h=23 */
.oring.sm{width:46px;height:23px}
.oring.sm .or{width:14px;height:14px;border-width:2px}
.oring.sm .or:nth-child(1){left:0;  top:0;  border-color:#0081c8}
.oring.sm .or:nth-child(2){left:16px;top:0; border-color:#6a6a80}
.oring.sm .or:nth-child(3){left:32px;top:0; border-color:#ee334e}
.oring.sm .or:nth-child(4){left:8px; top:9px;border-color:#fcb131}
.oring.sm .or:nth-child(5){left:24px;top:9px;border-color:#00a651}
/* MD  d=20  s=22  v=13  total-w=64  h=33 */
.oring.md{width:64px;height:33px}
.oring.md .or{width:20px;height:20px;border-width:2.5px}
.oring.md .or:nth-child(1){left:0;  top:0;   border-color:#0081c8}
.oring.md .or:nth-child(2){left:22px;top:0;  border-color:#6a6a80}
.oring.md .or:nth-child(3){left:44px;top:0;  border-color:#ee334e}
.oring.md .or:nth-child(4){left:11px;top:13px;border-color:#fcb131}
.oring.md .or:nth-child(5){left:33px;top:13px;border-color:#00a651}
/* LG  d=28  s=30  v=18  total-w=88  h=46 */
.oring.lg{width:88px;height:46px}
.oring.lg .or{width:28px;height:28px;border-width:3px}
.oring.lg .or:nth-child(1){left:0;  top:0;   border-color:#0081c8}
.oring.lg .or:nth-child(2){left:30px;top:0;  border-color:#6a6a80}
.oring.lg .or:nth-child(3){left:60px;top:0;  border-color:#ee334e}
.oring.lg .or:nth-child(4){left:15px;top:18px;border-color:#fcb131}
.oring.lg .or:nth-child(5){left:45px;top:18px;border-color:#00a651}

/* ── NAV ── */
.top-nav{
  position:sticky;top:0;z-index:200;
  background:rgba(245,243,239,.97);backdrop-filter:blur(16px);
  border-bottom:1px solid var(--border);
  display:flex;align-items:center;padding:0 36px;height:50px;gap:2px;
}
.nav-brand{
  display:flex;align-items:center;gap:10px;margin-right:24px;
  font-weight:700;font-size:.9rem;color:var(--gold);letter-spacing:-.2px;
  white-space:nowrap;text-decoration:none;
}
.top-nav a{
  color:var(--muted);text-decoration:none;font-size:.75rem;
  padding:5px 12px;border-radius:6px;transition:all .15s;white-space:nowrap;
}
.top-nav a:hover{color:var(--text);background:var(--card2)}
.nav-right{margin-left:auto;font-size:.72rem;color:var(--muted);display:flex;align-items:center;gap:10px}
.nav-right span{color:var(--gold);font-weight:600}
.lang-btn{
  background:none;border:1px solid var(--border);border-radius:6px;
  color:var(--muted);font-size:.72rem;padding:4px 10px;cursor:pointer;
  font-family:inherit;transition:all .15s;
}
.lang-btn:hover{color:var(--gold);border-color:var(--gold)}

/* ── PAGE WRAP ── */
.page-wrap{max-width:1360px;margin:0 auto;padding-bottom:60px}

/* ── HERO ── */
.hero{
  position:relative;overflow:hidden;
  background:linear-gradient(160deg,#eef0ff 0%,#f0f3ff 45%,#eaedff 100%);
  border-bottom:1px solid var(--border);
  padding:60px 48px 52px;text-align:center;
}
.hero::before{
  content:'';position:absolute;top:0;left:0;right:0;height:3px;
  background:linear-gradient(90deg,#fdb913 0 33%,#006a44 33% 66%,#c1272d 66% 100%);
}
.hero-glow{
  position:absolute;top:-80px;left:50%;transform:translateX(-50%);
  width:600px;height:400px;border-radius:50%;
  background:radial-gradient(ellipse,rgba(160,120,0,.05) 0%,transparent 70%);
  pointer-events:none;
}
.hero .flag{font-size:3rem;margin-bottom:14px;display:block;
  filter:drop-shadow(0 0 18px rgba(160,120,0,.2))}
.hero h1{
  font-size:clamp(2rem,4.5vw,3rem);font-weight:800;margin-bottom:10px;
  letter-spacing:-.8px;line-height:1.1;
}
.hero h1 .edition{
  background:linear-gradient(135deg,var(--gold2),var(--gold));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}
.hero .tagline{
  color:var(--muted);font-size:.96rem;max-width:600px;
  margin:0 auto 32px;line-height:1.7;
}
.hero-rings-row{display:flex;justify-content:center;margin-bottom:14px;opacity:.7}
.hero-datasrc{font-size:.68rem;color:#9090a8;margin-top:2px}

/* ── OVERVIEW ── */
.ovw-grid{
  display:grid;grid-template-columns:210px 1fr;gap:18px;
  padding:0 28px 18px;align-items:start;
}
@media(max-width:960px){.ovw-grid{grid-template-columns:1fr}}
.ovw-metrics{display:flex;flex-direction:column;gap:10px}
.ovw-table{padding:0 28px 18px}

/* ── METRIC CARDS ── */
.metric{
  background:var(--card);border:1px solid var(--border);border-radius:var(--r);
  padding:16px 18px;text-align:center;
  transition:border-color .2s,box-shadow .2s;
}
.metric:hover{border-color:rgba(160,120,0,.35);box-shadow:0 0 16px rgba(160,120,0,.07)}
.metric .val{
  font-size:1.85rem;font-weight:800;line-height:1;
  color:var(--gold);transition:all .3s;
}
.metric .lbl{font-size:.63rem;color:var(--muted);margin-top:5px;text-transform:uppercase;letter-spacing:.8px}
.metric .sub{font-size:.72rem;color:var(--text);margin-top:3px;transition:all .3s;opacity:.75}
#metric-expected .val{font-size:2.2rem}
.metric-gold .val{color:var(--gold)}
.metric-silver .val{color:var(--silver)}
.metric-beet .val{color:var(--beet)}
.metric-beet{border-color:rgba(176,40,96,.15)}
.metric-beet:hover{border-color:rgba(176,40,96,.35);box-shadow:0 0 16px rgba(176,40,96,.08)}

/* ── SECTION HEADER ── */
.sec-head{padding:32px 28px 14px}
.sec-head h2{
  font-size:1.2rem;font-weight:700;display:flex;align-items:center;gap:12px;
  letter-spacing:-.3px;
}
.sec-head h2 .sh-icon{
  width:32px;height:32px;border-radius:8px;
  background:linear-gradient(135deg,rgba(160,120,0,.12),rgba(160,120,0,.03));
  border:1px solid rgba(160,120,0,.18);
  display:flex;align-items:center;justify-content:center;
  font-size:.9rem;flex-shrink:0;
}
.sec-head .sec-sub{color:var(--muted);font-size:.79rem;margin-top:6px;padding-left:44px}
hr.divider{border:none;border-top:1px solid var(--border);margin:0 28px}

/* ── SIMULATOR BAR ── */
.sim-bar{
  background:var(--card2);border:1px solid var(--border);border-radius:var(--rr);
  margin:0 28px 18px;padding:22px 26px;
}
.sim-bar h3{
  font-size:.72rem;text-transform:uppercase;letter-spacing:1px;
  color:var(--muted);margin-bottom:16px;display:flex;align-items:center;gap:8px;
}
.sim-bar h3::after{content:'';flex:1;height:1px;background:var(--border)}
.sim-controls{display:flex;flex-wrap:wrap;gap:24px;align-items:flex-start}
.sim-block{flex:1;min-width:200px}
.sim-block label{font-size:.76rem;color:var(--muted);display:block;margin-bottom:7px}
.val-display{font-size:1.05rem;font-weight:700;color:var(--gold);float:right}
input[type=range]{
  width:100%;cursor:pointer;height:4px;
  -webkit-appearance:none;appearance:none;
  background:linear-gradient(to right,var(--gold) 0%,var(--gold) 22%,var(--border) 22%,var(--border) 100%);
  border-radius:2px;outline:none;
}
input[type=range]::-webkit-slider-thumb{
  -webkit-appearance:none;width:16px;height:16px;
  border-radius:50%;background:var(--gold);cursor:pointer;
  box-shadow:0 0 6px rgba(160,120,0,.4);
}
.range-ticks{display:flex;justify-content:space-between;font-size:.63rem;color:var(--muted);margin-top:5px}
.sport-toggles{display:flex;flex-wrap:wrap;gap:7px}
.sport-toggle{
  background:var(--card);border:1px solid var(--border);border-radius:20px;
  padding:4px 13px;font-size:.73rem;cursor:pointer;transition:all .2s;user-select:none;
}
.sport-toggle.active{background:rgba(160,120,0,.08);border-color:rgba(160,120,0,.35);color:var(--gold)}
.sport-toggle:hover{border-color:rgba(160,120,0,.3)}

/* ── ADVANCED PANEL ── */
.adv-panel{
  background:var(--card2);border:1px solid var(--border);border-radius:var(--rr);
  margin:0 28px 18px;padding:16px 26px;
}
.adv-panel summary{
  font-size:.72rem;text-transform:uppercase;letter-spacing:.9px;
  color:var(--muted);cursor:pointer;list-style:none;
  display:flex;align-items:center;gap:8px;
}
.adv-panel summary::-webkit-details-marker{display:none}
.adv-panel summary::before{content:"▶";font-size:.58rem;transition:transform .2s;color:var(--gold)}
details[open]>summary::before{transform:rotate(90deg)}
.adv-groups{display:grid;grid-template-columns:1fr 1fr 1fr;gap:24px;margin-top:18px}
@media(max-width:900px){.adv-groups{grid-template-columns:1fr}}
.adv-group h4{
  font-size:.68rem;text-transform:uppercase;letter-spacing:.9px;color:var(--gold);
  margin-bottom:12px;padding-bottom:7px;
  border-bottom:1px solid rgba(160,120,0,.18);
}
.adv-row{margin-bottom:10px}
.adv-row label{font-size:.74rem;color:var(--muted);display:block;margin-bottom:4px}
.val-disp{color:var(--gold);font-weight:700;float:right;font-size:.79rem}
.adv-row select{
  width:100%;background:var(--card);border:1px solid var(--border);
  border-radius:6px;color:var(--text);padding:6px 8px;
  font-size:.74rem;cursor:pointer;outline:none;transition:border-color .15s;
}
.adv-row select:focus{border-color:rgba(160,120,0,.4)}
.checkbox-row{
  display:flex;align-items:center;gap:8px;font-size:.74rem;
  color:var(--muted);margin-bottom:6px;cursor:pointer;
}
.checkbox-row input{accent-color:var(--gold);cursor:pointer}
.checkbox-row.beet-cb{color:var(--beet)}
.checkbox-row.beet-cb input{accent-color:var(--beet)}

/* ── GRID ── */
.grid{display:grid;gap:18px;padding:0 28px 18px}
.grid-2{grid-template-columns:1fr 1fr}
@media(max-width:960px){.grid-2{grid-template-columns:1fr}}

/* ── CARD ── */
.card{
  background:var(--card);border:1px solid var(--border);border-radius:var(--rr);
  padding:22px;transition:border-color .2s;
  box-shadow:0 1px 4px rgba(0,0,0,.04);
}
.card:hover{border-color:rgba(160,120,0,.2)}
.card h2{font-size:.93rem;font-weight:700;margin-bottom:5px;color:var(--text)}
.card .caption{font-size:.71rem;color:var(--muted);margin-bottom:14px;line-height:1.55}

/* ── TABLES ── */
table{width:100%;border-collapse:collapse;font-size:.79rem}
th{
  text-align:left;padding:9px 10px;color:var(--muted);font-weight:600;
  border-bottom:1px solid var(--border);
  font-size:.66rem;text-transform:uppercase;letter-spacing:.4px;
  background:var(--card2);
}
td{padding:10px 10px;border-bottom:1px solid var(--border);vertical-align:top;line-height:1.55}
tr:last-child td{border-bottom:none}
tr:hover td{background:#faf9f6}
.muted{color:var(--muted)}.small{font-size:.72rem}

/* ── PILLS ── */
.pill{
  display:inline-block;padding:2px 9px;border-radius:20px;
  font-size:.65rem;font-weight:600;white-space:nowrap;letter-spacing:.2px;
}
.pill.high{background:rgba(160,120,0,.1);color:#8a6000;border:1px solid rgba(160,120,0,.2)}
.pill.med{background:rgba(24,96,56,.08);color:#186038;border:1px solid rgba(24,96,56,.2)}
.pill.low{background:rgba(184,94,16,.08);color:#b85e10;border:1px solid rgba(184,94,16,.2)}
.pill.dark{background:rgba(160,24,24,.06);color:#a01818;border:1px solid rgba(160,24,24,.15)}

/* ── ATHLETE CARDS ── */
.athlete-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(255px,1fr));gap:16px}
.acard{
  background:var(--card);border:1px solid var(--border);border-radius:var(--rr);
  padding:20px;transition:all .2s;position:relative;overflow:hidden;
  box-shadow:0 1px 4px rgba(0,0,0,.05);
}
.acard::before{content:'';position:absolute;top:0;left:0;right:0;height:2px}
.acard.gold-tier::before{background:linear-gradient(90deg,var(--gold),var(--gold2))}
.acard.silver-tier::before{background:linear-gradient(90deg,#7080a0,var(--silver))}
.acard.bronze-tier::before{background:linear-gradient(90deg,var(--bronze),#c09060)}
.acard:hover{border-color:rgba(160,120,0,.3);transform:translateY(-2px);box-shadow:0 6px 24px rgba(0,0,0,.1)}
.acard .aname{font-size:.96rem;font-weight:700;margin-bottom:2px;padding-right:62px;color:var(--text)}
.acard .asport{font-size:.71rem;color:var(--muted);margin-bottom:12px;text-transform:uppercase;letter-spacing:.4px}
.acard .abadge{
  position:absolute;top:18px;right:18px;font-weight:800;font-size:.88rem;
  padding:4px 11px;border-radius:8px;
}
.acard.gold-tier   .abadge{background:rgba(160,120,0,.1);color:var(--gold);border:1px solid rgba(160,120,0,.25)}
.acard.silver-tier .abadge{background:rgba(80,88,112,.08);color:var(--silver);border:1px solid rgba(80,88,112,.2)}
.acard.bronze-tier .abadge{background:rgba(122,76,24,.08);color:#8a5820;border:1px solid rgba(122,76,24,.2)}
.acard p{font-size:.77rem;color:var(--muted);line-height:1.6}
.acard .astat{
  font-size:.71rem;color:var(--text);margin-top:10px;padding-top:10px;
  border-top:1px solid var(--border);opacity:.8;
}

/* ── PROBABILITY CELL ── */
.prob-cell strong{font-size:.9rem;font-weight:700;color:var(--gold)}

/* ── WARN ── */
.warn{
  background:rgba(160,24,24,.04);border:1px solid rgba(160,24,24,.18);
  border-radius:var(--r);padding:14px 20px;font-size:.8rem;
  color:#8a1818;margin:0 28px 20px;line-height:1.6;
}
.warn strong{color:#a01818}

/* ── SCENARIO BOX ── */
.scenario-box{
  background:rgba(24,96,56,.05);border:1px solid rgba(24,96,56,.2);
  border-radius:var(--r);padding:16px;font-size:.8rem;
  color:#186038;line-height:1.9;margin-top:8px;
}

/* ── SALTIBARCIAI TOAST ── */
.beet-toast{
  position:fixed;bottom:24px;right:24px;z-index:999;
  background:var(--beet);color:#fff;
  border-radius:12px;padding:14px 20px;font-size:.8rem;
  max-width:360px;box-shadow:0 4px 24px rgba(176,40,96,.25);
  line-height:1.6;animation:toastIn .3s ease;
}
@keyframes toastIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}

/* ── FOOTER ── */
.site-footer{
  text-align:center;color:var(--muted);font-size:.69rem;
  padding:32px 28px;border-top:1px solid var(--border);
  margin-top:16px;line-height:2;
}
.site-footer a{color:var(--gold);text-decoration:none;opacity:.9}
.site-footer a:hover{opacity:1}
.footer-rings-row{display:flex;justify-content:center;margin-bottom:18px}

/* ── PIPELINE FACTOR COLORS ── */
.f-good{color:var(--green);font-size:.72rem}
.f-disc{color:var(--gold);font-size:.72rem}
.f-poor{color:var(--orange);font-size:.72rem}
"""

BODY = f"""
<!-- NAV -->
<nav class="top-nav">
  <a href="#top" class="nav-brand">
    <div class="oring sm">{RINGS}</div>
    LT&nbsp;2028
  </a>
  <a href="#overview" data-i18n="nav-forecast">Forecast</a>
  <a href="#athletes" data-i18n="nav-athletes">Athletes</a>
  <a href="#simulator" data-i18n="nav-simulator">Simulator</a>
  <a href="#analysis" data-i18n="nav-analysis">Analysis</a>
  <a href="#data" data-i18n="nav-data">Data</a>
  <span class="nav-right">
    <span data-i18n="nav-expected-lbl">Expected medals:</span>&nbsp;<span id="nav-expected">2.22</span>
    <button class="lang-btn" id="lang-btn" onclick="toggleLang()">LT</button>
  </span>
</nav>

<div class="page-wrap">

<!-- ═══ HERO ═══ -->
<header class="hero" id="top">
  <div class="hero-glow"></div>
  <span class="flag">&#x1F1F1;&#x1F1F9;</span>
  <h1 data-i18n-html="hero-title">Lithuania&ensp;<span class="edition">LA&nbsp;2028</span><br>Olympic Medal Forecast</h1>
  <p class="tagline" data-i18n="hero-tagline">
    Sport-by-sport prediction built from Olympedia historical data (1992&ndash;2024),
    the known athlete pipeline, and a correlated Monte Carlo simulation.
  </p>
  <div class="hero-rings-row">
    <div class="oring lg">{RINGS}</div>
  </div>
  <p class="hero-datasrc" data-i18n="hero-datasrc">
    Olympedia 1992&ndash;2020 &bull; IOC Paris 2024 &bull; Bayesian shrinkage &bull;
    10,000-run Monte Carlo &bull; Gaussian copula &rho;=0.15
  </p>
</header>

<!-- ═══ FORECAST OVERVIEW ═══ -->
<section id="overview">
  <div class="sec-head">
    <h2><span class="sh-icon">&#127942;</span><span data-i18n="sec-forecast">2028 Forecast</span></h2>
    <p class="sec-sub" data-i18n="sub-forecast">Baseline scenario &mdash; use the Simulator below to adjust funding, athletes, and conditions</p>
  </div>

  <div class="ovw-grid">
    <div class="ovw-metrics">
      <div class="metric metric-gold" id="metric-expected">
        <div class="val" id="val-expected">2.22</div>
        <div class="lbl" data-i18n="lbl-expected">Expected medals</div>
        <div class="sub" id="sub-expected">P10&ndash;P90: 0&ndash;4</div>
      </div>
      <div class="metric">
        <div class="val" id="val-range">0&ndash;4</div>
        <div class="lbl" data-i18n="lbl-range">Likely range</div>
        <div class="sub" data-i18n="sub-range">P10 &ndash; P90</div>
      </div>
      <div class="metric">
        <div class="val" id="val-zero">13.2%</div>
        <div class="lbl" data-i18n="lbl-zero">Zero-medal risk</div>
        <div class="sub" id="sub-zero" data-i18n="sub-zero-static">current settings</div>
      </div>
      <div class="metric metric-gold">
        <div class="val" id="val-ath">58%</div>
        <div class="lbl" data-i18n="lbl-athletics">Athletics</div>
        <div class="sub" data-i18n="sub-athletics">Alekna &mdash; gold favourite</div>
      </div>
      <div class="metric metric-silver">
        <div class="val">4</div>
        <div class="lbl" data-i18n="lbl-paris">Paris 2024 actual</div>
        <div class="sub" data-i18n="sub-paris">incl. Breaking silver</div>
      </div>
      <div class="metric metric-beet" title="&#352;altibar&#353;&#269;iai: Lithuania's beloved cold pink beet soup. Widely considered the true source of Lithuanian athletic excellence.">
        <div class="val">100%</div>
        <div class="lbl" data-i18n="lbl-beet">&#352;altibar&#353;&#269;iai Index</div>
        <div class="sub" data-i18n="sub-beet">Post-medal ceremony probability</div>
      </div>
    </div>
    <div class="card">
      <h2 data-i18n="chart-sports-title">Per-Sport Medal Probability</h2>
      <p class="caption" data-i18n="chart-sports-cap">Grey = historical win rate &bull; Coloured = 2028 estimate &bull; Updates with all simulator controls</p>
      <div id="chart-sports"></div>
    </div>
  </div>

  <div class="ovw-table">
    <div class="card">
      <h2 style="margin-bottom:12px" data-i18n="tbl-title">Sport-by-Sport Detail</h2>
      <div style="overflow-x:auto">
      <table>
        <tr><th data-i18n="th-sport">Sport</th><th data-i18n="th-prob">2028 Prob</th><th data-i18n="th-hist">Historical</th><th data-i18n="th-years">Medal years</th><th data-i18n="th-outlook">Outlook</th><th data-i18n="th-notes">Notes</th></tr>
        <tr>
          <td><strong data-i18n="sport-athletics">Athletics</strong></td>
          <td class="prob-cell" data-sport="Athletics"><strong>58%</strong></td>
          <td class="muted small">7/9 Games (78%)</td>
          <td class="muted small">1992, 2000, 2004, 2008, 2012, 2016, 2024</td>
          <td><span class="pill high" data-i18n="pill-gold">Gold contender</span></td>
          <td class="muted small" data-i18n="note-athletics">Mykolas Alekna (25 in 2028): Olympic silver 2024, world lead 74.35m. Top global gold favourite. Gudzius may also compete (Rio 2016 gold).</td>
        </tr>
        <tr>
          <td><strong data-i18n="sport-rowing">Rowing</strong></td>
          <td class="prob-cell" data-sport="Rowing"><strong>38%</strong></td>
          <td class="muted small">3/9 Games (33%)</td>
          <td class="muted small">2000, 2016, 2024</td>
          <td><span class="pill med" data-i18n="pill-realistic">Realistic</span></td>
          <td class="muted small" data-i18n="note-rowing">Viktorija Senkute (32 in 2028): Olympic bronze 2024 (W Single Sculls). Born 1996, near peak sculling age.</td>
        </tr>
        <tr>
          <td><strong data-i18n="sport-swimming">Swimming</strong></td>
          <td class="prob-cell" data-sport="Swimming"><strong>27%</strong></td>
          <td class="muted small">1/9 Games (11%)</td>
          <td class="muted small">2012</td>
          <td><span class="pill med" data-i18n="pill-realistic">Realistic</span></td>
          <td class="muted small" data-i18n="note-swimming">Ruta Meilutyte (31 in 2028): WR holder 50m breast, Olympic gold 2012, psych factor applied. Danas Rapsys (33): multiple Olympic A-finals.</td>
        </tr>
        <tr>
          <td><strong data-i18n="sport-bball">3x3 Basketball</strong></td>
          <td class="prob-cell" data-sport="3x3 Basketball"><strong>25%</strong></td>
          <td class="muted small">1/2 Games (50%)</td>
          <td class="muted small">2024</td>
          <td><span class="pill med" data-i18n="pill-realistic">Realistic</span></td>
          <td class="muted small" data-i18n="note-bball">Olympic bronze 2024. Core roster ages 31&ndash;41 in 2028 &mdash; roster continuity uncertain.</td>
        </tr>
        <tr>
          <td><strong data-i18n="sport-pentathlon">Modern Pentathlon</strong></td>
          <td class="prob-cell" data-sport="Modern Pentathlon"><strong>20%</strong></td>
          <td class="muted small">4/9 Games (44%)</td>
          <td class="muted small">2004, 2008, 2012, 2020</td>
          <td><span class="pill low" data-i18n="pill-possible">Possible</span></td>
          <td class="muted small" data-i18n="note-pentathlon">Asadauskaite (44 in 2028): virtually certain to have retired. Venckauskaite (35&ndash;36) is the only pipeline.</td>
        </tr>
        <tr>
          <td><strong data-i18n="sport-weightlifting">Weightlifting</strong></td>
          <td class="prob-cell" data-sport="Weightlifting"><strong>15%</strong></td>
          <td class="muted small">1/6 Games (17%)</td>
          <td class="muted small">2016</td>
          <td><span class="pill low" data-i18n="pill-possible">Possible</span></td>
          <td class="muted small" data-i18n="note-weightlifting">Aurimas Didzbalis bronze 2016. Programme affected by IWF sanctions era. No confirmed 2028 contender.</td>
        </tr>
        <tr>
          <td><strong data-i18n="sport-wrestling">Wrestling</strong></td>
          <td class="prob-cell" data-sport="Wrestling"><strong>14%</strong></td>
          <td class="muted small">2/9 Games (22%)</td>
          <td class="muted small">2008, 2012</td>
          <td><span class="pill low" data-i18n="pill-possible">Possible</span></td>
          <td class="muted small" data-i18n="note-wrestling">Two medals in 2008 and 2012. Gabija Dilyte (25 in 2028) is a developing prospect.</td>
        </tr>
        <tr>
          <td><strong data-i18n="sport-shooting">Shooting</strong></td>
          <td class="prob-cell" data-sport="Shooting"><strong>12%</strong></td>
          <td class="muted small">1/7 Games (14%)</td>
          <td class="muted small">2000</td>
          <td><span class="pill dark" data-i18n="pill-darkhorse">Dark horse</span></td>
          <td class="muted small" data-i18n="note-shooting">Last medal: Daina Gudzineviciute, Trap Gold 2000. No current ISSF top-20 Lithuanian shooter identified.</td>
        </tr>
        <tr>
          <td><strong data-i18n="sport-canoe">Canoe Sprint</strong></td>
          <td class="prob-cell" data-sport="Canoe Sprint"><strong>11%</strong></td>
          <td class="muted small">1/9 Games (11%)</td>
          <td class="muted small">2016</td>
          <td><span class="pill dark" data-i18n="pill-darkhorse">Dark horse</span></td>
          <td class="muted small" data-i18n="note-canoe">2016 bronze (K2-200m). No confirmed 2028 contender identified yet.</td>
        </tr>
      </table>
      </div>
    </div>
  </div>
</section>

<hr class="divider">

<!-- ═══ ATHLETES ═══ -->
<section id="athletes">
  <div class="sec-head">
    <h2><span class="sh-icon">&#127941;</span><span data-i18n="sec-athletes">Key Athletes &mdash; LA 2028 Contenders</span></h2>
    <p class="sec-sub" data-i18n="sub-athletes">Primary medal candidates driving the per-sport probabilities above</p>
  </div>

  <div style="padding:0 28px 24px">
    <div class="athlete-grid">
      <div class="acard gold-tier">
        <span class="abadge">58%</span>
        <div class="aname">Mykolas Alekna</div>
        <div class="asport" data-i18n="acard1-sport">Athletics &mdash; Discus Throw</div>
        <p data-i18n="acard1-desc">Top global gold favourite. Olympic silver Paris 2024 aged 21. World lead 74.35m in 2024. Father Virgilijus won discus gold 2000 &amp; 2004. Born Sept 2002 &mdash; will be 25 at LA 2028, absolute prime.</p>
        <div class="astat" data-i18n="acard1-stat">Paris 2024: Silver &bull; 74.35m WL &bull; Age in 2028: 25</div>
      </div>
      <div class="acard silver-tier">
        <span class="abadge">38%</span>
        <div class="aname">Viktorija Senkute</div>
        <div class="asport" data-i18n="acard2-sport">Rowing &mdash; Women's Single Sculls</div>
        <p data-i18n="acard2-desc">Olympic bronze Paris 2024. Born 1996, age 32 in 2028 &mdash; near peak sculling age. Consistent top-3 on World Cup circuit. Psych factor: normal (consistent Olympic performer).</p>
        <div class="astat" data-i18n="acard2-stat">Paris 2024: Bronze &bull; Born 1996 &bull; Age in 2028: 32</div>
      </div>
      <div class="acard bronze-tier">
        <span class="abadge">27%</span>
        <div class="aname">Ruta Meilutyte &amp; Danas Rapsys</div>
        <div class="asport" data-i18n="acard3-sport">Swimming</div>
        <p data-i18n="acard3-desc">Meilutyte: 50m breast world record holder, Olympic gold 2012, still active at 31 in 2028. Psych discount applied (Olympic underperformer). Rapsys: 3 Olympic A-finals, age 33 in 2028.</p>
        <div class="astat" data-i18n="acard3-stat">Meilutyte age: 31 &bull; Rapsys age: 33 &bull; Two podium paths</div>
      </div>
      <div class="acard bronze-tier">
        <span class="abadge">25%</span>
        <div class="aname">Lithuania 3x3 Basketball</div>
        <div class="asport" data-i18n="acard4-sport">3x3 Basketball &mdash; Men's Team</div>
        <p data-i18n="acard4-desc">Olympic bronze 2024. Core roster ages 31-41 in 2028 -- roster continuity is the key uncertainty. Basketball is Lithuania's structural sport; FIBA 3x3 consistent global top-10.</p>
        <div class="astat" data-i18n="acard4-stat">Paris 2024: Bronze &bull; FIBA 3x3 World Ranking: top-10</div>
      </div>
      <div class="acard bronze-tier">
        <span class="abadge">20%</span>
        <div class="aname">Gintare Venckauskaite</div>
        <div class="asport" data-i18n="acard5-sport">Modern Pentathlon</div>
        <p data-i18n="acard5-desc">Born 1992, age 35-36 in 2028 -- late career. Same generation as Asadauskaite (born 1984, age 44, retired). No confirmed next-generation pentathlete identified.</p>
        <div class="astat" data-i18n="acard5-stat">Born 1992 &bull; Age in 2028: 35-36 &bull; Asadauskaite: retired</div>
      </div>
    </div>
  </div>

  <div class="warn" data-i18n-html="warn-breaking">
    <strong>Breaking is NOT on the LA 2028 programme.</strong>
    NICKA (Dominyka Banevic) won Silver at Paris 2024, but the IOC removed Breaking from the 2028 Games.
    Lithuania's 2028 forecast is calculated without this sport.
    <em style="opacity:.7">&nbsp; Source: IOC Programme Commission, 2023.</em>
  </div>
</section>

<hr class="divider">

<!-- ═══ SIMULATOR ═══ -->
<section id="simulator">
  <div class="sec-head">
    <h2><span class="sh-icon">&#9881;</span><span data-i18n="sec-simulator">Interactive Simulator</span></h2>
    <p class="sec-sub" data-i18n="sub-simulator">Adjust funding, athlete status, and conditions &mdash; charts update live. The forecast table above also updates.</p>
  </div>

  <div class="sim-bar">
    <h3 data-i18n="ctrl-core">Core controls</h3>
    <div class="sim-controls">
      <div class="sim-block" style="min-width:260px">
        <label><span data-i18n="lbl-funding">Funding multiplier</span>&nbsp;<span class="val-display" id="funding-display">1.00x</span></label>
        <input type="range" id="funding-slider" min="0" max="9" value="2" step="1">
        <div class="range-ticks">
          <span>0.5x (cut)</span><span>1.0x (baseline)</span><span>2.0x</span><span>4.0x</span>
        </div>
      </div>
      <div class="sim-block" style="flex:2;min-width:280px">
        <label data-i18n="lbl-sports">Sports to include &mdash; click to toggle off / on</label>
        <div class="sport-toggles" id="sport-toggles"></div>
      </div>
    </div>
  </div>

  <details class="adv-panel">
    <summary data-i18n="adv-title">Advanced Factors &mdash; athlete status, programme &amp; external conditions</summary>
    <div class="adv-groups">
      <div class="adv-group">
        <h4 data-i18n="adv-ath-head">Athlete Status</h4>
        <div class="adv-row">
          <label data-i18n="lbl-alekna">Mykolas Alekna</label>
          <select id="adv-alekna" onchange="updateAll()">
            <option value="peak" selected>Peak form (world #1)</option>
            <option value="uncertain">Minor injury / uncertain</option>
            <option value="out">Out / retired</option>
          </select>
        </div>
        <div class="adv-row">
          <label data-i18n="lbl-meilutyte">Ruta Meilutyte</label>
          <select id="adv-meilutyte" onchange="updateAll()">
            <option value="normal">Active (100m breast only)</option>
            <option value="confirmed_50m" selected>50m breast confirmed for LA 2028</option>
            <option value="retired">Retired by 2028</option>
          </select>
        </div>
        <div class="adv-row">
          <label data-i18n="lbl-bball">3x3 Basketball roster</label>
          <select id="adv-bball" onchange="updateAll()">
            <option value="full" selected>Full core roster (Paris 2024)</option>
            <option value="partial">2&ndash;3 core players remain</option>
            <option value="new">Mostly new / young squad</option>
            <option value="dnq">Fails to qualify</option>
          </select>
        </div>
        <div class="adv-row" style="margin-top:10px">
          <label style="margin-bottom:7px" data-i18n="lbl-pipeline">Youth pipeline</label>
          <label class="checkbox-row"><input type="checkbox" id="pipe-lukminas" onchange="updateAll()"> Lukminas (Athletics +2%)</label>
          <label class="checkbox-row"><input type="checkbox" id="pipe-dilyte" onchange="updateAll()"> Dilyte (Wrestling +5%)</label>
          <label class="checkbox-row"><input type="checkbox" id="pipe-navikonis" onchange="updateAll()"> Navikonis (Rowing +2%)</label>
          <label class="checkbox-row"><input type="checkbox" id="pipe-unknown" onchange="updateAll()"> Unknown breakout (+2.5%)</label>
          <label class="checkbox-row beet-cb"><input type="checkbox" id="pipe-saltibarciai" onchange="saltibarciai(this)"> <span data-i18n="lbl-saltibarciai">&#352;altibar&#353;&#269;iai protocol (+&infin;%)</span></label>
        </div>
      </div>
      <div class="adv-group">
        <h4 data-i18n="adv-prog-head">Programme &amp; Investment</h4>
        <div class="adv-row">
          <label data-i18n="lbl-focus">Focus mode</label>
          <select id="adv-focus" onchange="updateAll()">
            <option value="broad" selected>Broad (all sports)</option>
            <option value="top3">Focused &mdash; top 3 sports</option>
            <option value="top2">Elite &mdash; top 2 sports only</option>
          </select>
        </div>
        <div class="adv-row">
          <label><span data-i18n="lbl-deleg">Delegation size</span>&nbsp;<span class="val-disp" id="deleg-display">50</span></label>
          <input type="range" id="adv-deleg" min="25" max="80" value="50" step="5"
            oninput="document.getElementById('deleg-display').textContent=this.value;updateAll()">
        </div>
        <div class="adv-row">
          <label data-i18n="lbl-coaching">Coaching &amp; support quality</label>
          <select id="adv-coaching" onchange="updateAll()">
            <option value="low">Below average</option>
            <option value="normal" selected>Average (current)</option>
            <option value="high">Above average (+5%)</option>
            <option value="elite">Elite programme (+10%)</option>
          </select>
        </div>
        <div class="adv-row">
          <label data-i18n="lbl-peaking">Competition peaking</label>
          <select id="adv-peak" onchange="updateAll()">
            <option value="poor">Poor peaking</option>
            <option value="normal" selected>Normal</option>
            <option value="good">Good peaking (+3%)</option>
          </select>
        </div>
      </div>
      <div class="adv-group">
        <h4 data-i18n="adv-ext-head">External Conditions</h4>
        <div class="adv-row">
          <label data-i18n="lbl-host">Host nation effect (LA 2028)</label>
          <select id="adv-host" onchange="updateAll()">
            <option value="negative">Negative (crowd disadvantage)</option>
            <option value="neutral" selected>Neutral</option>
            <option value="positive">Positive (diaspora boost)</option>
          </select>
        </div>
        <div class="adv-row">
          <label data-i18n="lbl-gdp">GDP &amp; budget scenario</label>
          <select id="adv-gdp" onchange="updateAll()">
            <option value="recession">Recession (budget &minus;10%)</option>
            <option value="baseline" selected>Baseline (modest growth)</option>
            <option value="strong">Strong growth (+15%)</option>
          </select>
        </div>
        <div class="adv-row">
          <label data-i18n="lbl-rho">Cross-sport correlation &rho;</label>
          <select id="adv-rho" onchange="updateAll()">
            <option value="low">Low (0.05 &mdash; independent)</option>
            <option value="medium" selected>Medium (0.15 &mdash; default)</option>
            <option value="high">High (0.30 &mdash; shared luck)</option>
          </select>
        </div>
      </div>
    </div>
  </details>

  <div class="grid grid-2">
    <div class="card">
      <h2 data-i18n="chart-mc-title">Medal Count Distribution</h2>
      <p class="caption" data-i18n="chart-mc-cap">Exact Poisson-binomial probability at current settings</p>
      <div id="chart-mc"></div>
    </div>
    <div class="card">
      <h2 data-i18n="chart-hist-title">Historical Performance 1992&ndash;2024</h2>
      <p class="caption" data-i18n="chart-hist-cap">Red star = 2028 forecast with P10&ndash;P90 error bar</p>
      <div id="chart-hist"></div>
    </div>
  </div>

  <div class="grid grid-2">
    <div class="card">
      <h2 data-i18n="chart-type-title">Medal Type Breakdown</h2>
      <p class="caption" data-i18n="chart-type-cap">Estimated gold / silver / bronze split per sport</p>
      <div id="chart-type"></div>
    </div>
    <div class="card">
      <h2 data-i18n="chart-scen-title">Scenario Comparison</h2>
      <p class="caption" data-i18n="chart-scen-cap">Baseline, 2x &amp; 3x funding vs current settings (red bar)</p>
      <div id="chart-scen"></div>
    </div>
  </div>

  <div class="grid">
    <div class="card">
      <h2 data-i18n="chart-peers-title">Peer Country Comparison &mdash; Paris 2024</h2>
      <p class="caption" data-i18n="chart-peers-cap">Lithuania vs similar small European nations</p>
      <div id="chart-peers"></div>
    </div>
  </div>
</section>

<hr class="divider">

<!-- ═══ ANALYSIS ═══ -->
<section id="analysis">
  <div class="sec-head">
    <h2><span class="sh-icon">&#128202;</span><span data-i18n="sec-analysis">Model Analysis</span></h2>
    <p class="sec-sub" data-i18n="sub-analysis">How each probability is built &mdash; athlete decomposition and pipeline</p>
  </div>

  <div class="grid grid-2">
    <div class="card">
      <h2 data-i18n="chart-decomp-title">Athlete Model vs Historical Rate</h2>
      <p class="caption" data-i18n="chart-decomp-cap">Grey = recency-weighted historical win rate &bull; Blue = athlete ranking model (union of contenders) &bull; Red diamond = final blended estimate</p>
      <div id="chart-decomp"></div>
    </div>
    <div class="card">
      <h2 data-i18n="pipe-title">Athlete Pipeline &amp; World Rankings</h2>
      <p class="caption" data-i18n="pipe-cap">Event medal prob = rank_prob &times; psych_factor &times; age_factor. Union across contenders gives sport probability.</p>
      <div style="overflow-x:auto">
        <table>
          <tr><th data-i18n="th-athlete">Athlete</th><th data-i18n="th-event">Event</th><th data-i18n="th-rank">Rank</th><th data-i18n="th-age2028">Age 2028</th><th data-i18n="th-prob">Prob</th><th data-i18n="th-factor">Factor</th><th data-i18n="th-notes">Notes</th></tr>
          <tr>
            <td><strong>Mykolas Alekna</strong></td><td class="muted small" data-i18n="pe-discus">Discus Men</td>
            <td><strong>#1</strong></td><td>25</td><td><strong>58%</strong></td>
            <td class="f-disc" data-i18n="factor-disc">Slight discount</td>
            <td class="muted small" data-i18n="pn-alekna">World #1 2024, 74.35m WL, Olympic silver 2024 (aged 21).</td>
          </tr>
          <tr>
            <td><strong>Viktorija Senkute</strong></td><td class="muted small" data-i18n="pe-sculls">W Single Sculls</td>
            <td><strong>#3</strong></td><td>32</td><td><strong>37%</strong></td>
            <td class="f-good" data-i18n="factor-normal">Normal</td>
            <td class="muted small" data-i18n="pn-senkute">Olympic bronze 2024, born 1996, age 32 in 2028.</td>
          </tr>
          <tr>
            <td><strong>Stankunas twins</strong></td><td class="muted small" data-i18n="pe-dsculls">M Double Sculls</td>
            <td><strong>#14</strong></td><td>28</td><td><strong>6%</strong></td>
            <td class="f-good" data-i18n="factor-normal">Normal</td>
            <td class="muted small" data-i18n="pn-stankunas">Domantas &amp; Dovydas, Paris 2024 participants.</td>
          </tr>
          <tr>
            <td><strong>Ruta Meilutyte</strong></td><td class="muted small" data-i18n="pe-100breast">100m Breaststroke</td>
            <td><strong>#4</strong></td><td>31</td><td><strong>22%</strong></td>
            <td class="f-poor" data-i18n="factor-poor">Olympic underperformer</td>
            <td class="muted small" data-i18n="pn-meilutyte">WR holder 50m breast, top-5 100m. Last medal: gold 2012.</td>
          </tr>
          <tr>
            <td><strong>Danas Rapsys</strong></td><td class="muted small" data-i18n="pe-200free">200m Freestyle Men</td>
            <td><strong>#7</strong></td><td>33</td><td><strong>13%</strong></td>
            <td class="f-disc" data-i18n="factor-disc">Slight discount</td>
            <td class="muted small" data-i18n="pn-rapsys">European champion, 3 Olympic A-finals. Age 33 in 2028.</td>
          </tr>
          <tr>
            <td><strong>Lithuania 3x3 Men</strong></td><td class="muted small" data-i18n="pe-3x3">3x3 Basketball</td>
            <td><strong>#5</strong></td><td>35</td><td><strong>21%</strong></td>
            <td class="f-good" data-i18n="factor-normal">Normal</td>
            <td class="muted small" data-i18n="pn-bball">Olympic bronze 2024. Roster continuity uncertain.</td>
          </tr>
          <tr>
            <td><strong>Gintare Venckauskaite</strong></td><td class="muted small" data-i18n="pe-wpentathlon">Women's Pentathlon</td>
            <td><strong>#10</strong></td><td>36</td><td><strong>7%</strong></td>
            <td class="f-poor" data-i18n="factor-poor">Olympic underperformer</td>
            <td class="muted small" data-i18n="pn-venckauskaite">Born 1992, age 35-36 in 2028 -- late career.</td>
          </tr>
          <tr>
            <td><strong>Gabija Dilyte</strong></td><td class="muted small" data-i18n="pe-wwrestling">Women's Wrestling</td>
            <td><strong>#15</strong></td><td>25</td><td><strong>5%</strong></td>
            <td class="f-good" data-i18n="factor-normal">Normal</td>
            <td class="muted small" data-i18n="pn-dilyte">Born 2003, age 25 in 2028. Paris 2024 participant, developing.</td>
          </tr>
        </table>
      </div>
    </div>
  </div>

  <div class="grid grid-2">
    <div class="card">
      <h2 data-i18n="emerging-title">Emerging Athletes &mdash; Not in Current Model</h2>
      <p class="caption" data-i18n="emerging-cap">Competed at Paris 2024, prime age in 2028, no identified medal path yet. Worth tracking as 2028 approaches.</p>
      <table>
        <tr><th data-i18n="th-athlete">Athlete</th><th data-i18n="th-sport">Sport</th><th data-i18n="th-age2028">Age 2028</th><th data-i18n="th-born">Born</th><th data-i18n="th-status">Status</th></tr>
        <tr><td><strong>SAVICKAS Aleksas</strong></td><td data-i18n="sport-swimming">Swimming</td><td>25</td><td>2003</td><td><span class="pill med" data-i18n="pill-prime2028">Prime 2028</span></td></tr>
        <tr><td><strong>TETEREVKOVA Kotryna</strong></td><td data-i18n="sport-swimming">Swimming</td><td>26</td><td>2002</td><td><span class="pill med" data-i18n="pill-prime2028">Prime 2028</span></td></tr>
        <tr><td><strong>RIMKUTE Dovile</strong></td><td data-i18n="sport-rowing">Rowing</td><td>27</td><td>2001</td><td><span class="pill med" data-i18n="pill-prime2028">Prime 2028</span></td></tr>
        <tr><td><strong>KRALIKAITE Kamile</strong></td><td data-i18n="sport-rowing">Rowing</td><td>27</td><td>2001</td><td><span class="pill med" data-i18n="pill-prime2028">Prime 2028</span></td></tr>
        <tr><td><strong>RAUPELYTE Aine</strong></td><td data-i18n="sport-bvolley">Beach Volleyball</td><td>28</td><td>2000</td><td><span class="pill med" data-i18n="pill-prime2028">Prime 2028</span></td></tr>
        <tr><td><strong>BALEISYTE Olivija</strong></td><td data-i18n="sport-cycling">Cycling Track</td><td>30</td><td>1998</td><td><span class="pill med" data-i18n="pill-prime2028">Prime 2028</span></td></tr>
        <tr><td><strong>ZAGAINOVA Diana</strong></td><td data-i18n="sport-athletics">Athletics</td><td>31</td><td>1997</td><td><span class="pill med" data-i18n="pill-prime2028">Prime 2028</span></td></tr>
        <tr><td><strong>BIELIAUSKAS Giedrius</strong></td><td data-i18n="sport-rowing">Rowing</td><td>31</td><td>1997</td><td><span class="pill med" data-i18n="pill-prime2028">Prime 2028</span></td></tr>
        <tr><td><strong>MATUSEVICIUS Edis</strong></td><td data-i18n="sport-athletics">Athletics</td><td>32</td><td>1996</td><td><span class="pill med" data-i18n="pill-prime2028">Prime 2028</span></td></tr>
      </table>
    </div>
    <div class="card">
      <h2 data-i18n="breaststroke-title">50m Breaststroke &mdash; Conditional Scenario</h2>
      <p class="caption" data-i18n="breaststroke-cap">Meilutyte holds the 50m breast world record and won the 2023 World Championship. If confirmed for LA 2028, her probability in that event alone is estimated at 42%.</p>
      <div class="scenario-box" data-i18n-html="scenario-box">
        <strong>Current model (100m breast only):</strong> Swimming = 27%<br>
        <strong>If 50m breast confirmed for LA 2028:</strong> Swimming &asymp; 44&ndash;50%<br>
        <strong>Source:</strong> World Aquatics Programme Commission lobbying, 2024<br>
        <strong>Status:</strong> Pending IOC confirmation
      </div>
      <div style="margin-top:14px;font-size:.76rem;color:var(--muted);line-height:1.65" data-i18n="scenario-note">
        Psych factor 0.85 applied in current model (Olympic underperformer vs world ranking).
        Last Olympic medal: gold 2012. Use the Meilutyte dropdown in Advanced Factors
        to model the 50m confirmation scenario.
      </div>
    </div>
  </div>
</section>

<!-- ═══ FOOTER ═══ -->
<footer class="site-footer" id="data">
  <div class="footer-rings-row">
    <div class="oring md">{RINGS}</div>
  </div>
  <strong style="color:var(--text)" data-i18n="footer-sources">Data sources:</strong>
  Olympedia historical results 1992&ndash;2020 (Kaggle) &bull;
  Paris 2024 official results (IOC) &bull;
  World Athletics, FINA, FIBA 3x3, ICF, UIPM, ISSF rankings 2024 &bull;
  IOC Programme Commission 2023 (Breaking removal) &bull;
  Bayesian shrinkage on sports with &lt;5 Games of data &bull;
  Macro ensemble: XGBoost + RF trained on 137 countries 1960&ndash;2024
  <br>
  <span data-i18n="footer-gen">Generated 2026-03-26</span> &bull;
  <a href="https://github.com/yonathan-star/lt-olympic-forecast">GitHub</a>
</footer>

</div><!-- .page-wrap -->

<script>
// Mirror nav-expected counter from main metric ID
(function(){{
  var obs = new MutationObserver(function(){{
    var e = document.getElementById('val-expected');
    if(e){{ var ne=document.getElementById('nav-expected'); if(ne) ne.textContent=e.textContent; }}
  }});
  var m = document.getElementById('metric-expected');
  if(m) obs.observe(m, {{subtree:true, characterData:true, childList:true}});
}})();

// Saltibarciai Easter egg
function saltibarciai(cb) {{
  if (!cb.checked) return;
  var msg = LANG === 'lt'
    ? 'Skanu! Deja, TOK dar nepripa\u017e\u012fsta \u0161altibar\u0161\u010di\u0173 kaip sportin\u0117s veiklos gerinimo priemon\u0117. Tikimyb\u0117 nesikeit\u0117.'
    : 'Delicious. However, the IOC has not yet classified \u0161altibar\u0161\u010diai as a performance-enhancing substance. Probability unchanged.';
  var t = document.createElement('div');
  t.className = 'beet-toast';
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(function(){{ t.style.opacity='0'; t.style.transition='opacity .4s'; }}, 3600);
  setTimeout(function(){{ if(t.parentNode) t.parentNode.removeChild(t); cb.checked=false; }}, 4100);
}}
</script>
"""

FULL = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Lithuania LA 2028 Olympic Medal Forecast</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>{CSS}</style>
</head>
<body>
{BODY}
{TRANS_JS}
{JS}
</body>
</html>
"""

import re
out = os.path.join(ROOT, "docs", "index.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(FULL)
print(f"Written {len(FULL):,} bytes")

ids = re.findall(r'id="([\w-]+)"', FULL)
required = ['val-expected','sub-expected','val-range','val-zero','val-ath',
            'funding-slider','funding-display','sport-toggles',
            'adv-alekna','adv-meilutyte','adv-bball','adv-focus','adv-deleg',
            'adv-coaching','adv-peak','adv-host','adv-gdp','adv-rho',
            'pipe-lukminas','pipe-dilyte','pipe-navikonis','pipe-unknown',
            'chart-sports','chart-mc','chart-hist','chart-type','chart-scen',
            'chart-peers','chart-decomp','deleg-display','metric-expected']
missing = [r for r in required if r not in ids]
print("Missing IDs:", missing if missing else "none")
