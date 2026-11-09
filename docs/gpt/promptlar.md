# GPT çizim promptları

Sohbet: `mma-arayuz` (gpt-ciz, tek sohbet). Görseller: `docs/gpt/mma-arayuz/`.

## Ortak içerik (her seçenekte aynı)

Sitenin bugünkü içeriği: başlık + alt başlık, Yıl/Ay/Kapsam filtreleri, sıklet sekmeleri (P4P + 8 erkek sıkleti),
liste başlığı, 6 sütunlu tablo (#, Dövüşçü, Puan, μ ± RD, Rekor, Son maç), "inaktif −N" etiketi, "≈" işareti, Yöntem bölümü.

## 1 — Seçenek A: editoryal spor gazetesi

```
I am designing a web page for a non-commercial MMA ratings site and want 5 visual style options from you, one per message, in this conversation (A, B, C, D, E). All five must show the SAME page content but each must be clearly, radically different in visual style from the others. Later I will pick one and we will design further screens in it, so keep each style internally consistent.

Make a realistic, high-fidelity desktop web page mockup (flat UI screenshot, 16:10 landscape, about 1440 px wide layout, no browser chrome, no device frame). All text must be crisp and legible. UI language is Turkish; keep these exact strings. No photos or portraits of real people; no logos of real organisations.

Page content (same in every option):
- Site name "MMA Rankings" with tagline "Matematiksel, şeffaf, geçmişe dönük sıralamalar."
- Filter row with three dropdowns: "Yıl: 2026", "Ay: Kasım", "Kapsam: Global (tüm organizasyonlar)".
- Division tabs: P4P, Heavyweight, Light Heavyweight, Middleweight, Welterweight, Lightweight (selected), Featherweight, Bantamweight, Flyweight.
- List title "Global · Lightweight · Kasım 2026" and a small note "Son güncelleme: 4 Kasım 2026".
- A ranking table with columns: # | Dövüşçü | Puan | μ ± RD | Rekor | Son maç. Ten rows:
  1 Islam Makhachev 1912 | 2061 ± 74 | 27-1 | Oca 2026
  2 Arman Tsarukyan 1868 | 2013 ± 72 | 22-3 | Eki 2026
  3 Charles Oliveira 1801 | 1958 ± 78 | 35-10 | Eyl 2026
  4 Ilia Topuria 1795 | 1972 ± 88 | 17-0 | Haz 2026
  5 Justin Gaethje 1742 | 1906 ± 82 | 26-6 | Mar 2026
  6 Dan Hooker 1731 | 1890 ± 79 | 24-12 | Ağu 2026
  7 Mateusz Gamrot 1720 | 1874 ± 77 | 25-3 | Tem 2026
  8 Paddy Pimblett 1712 | 1885 ± 86 | 23-3 | May 2026
  9 Beneil Dariush 1690 | 1871 ± 90 | 22-6 | Kas 2024, with a small tag "inaktif −40" next to the name
  10 Renato Moicano ≈ 1684 | 1850 ± 83 | 20-6 | Şub 2026 (the "≈" is a small marker after the name)
- Below the table, the top of a "Yöntem" section with two short bullet lines (Model: Glicko-1 …; Sıralama puanı: μ − 2·RD − inaktivite cezası).

Option A: EDITORIAL SPORTS NEWSPAPER. Think the sports section of a premium broadsheet: warm off-white paper background, black serif display headline, fine hairline rules between rows, small caps column labels, one restrained accent colour (deep red) for the rank numbers and the selected tab, generous margins, typographic hierarchy instead of boxes or cards. Elegant, authoritative, print-like.

## 2 — Seçenek B: veri terminali

```
Option B: DATA TERMINAL. Exactly the same page content, strings and table rows as option A, but radically different style: a dark, dense financial-terminal look (think a professional market-data terminal). Near-black background, monospaced type for all numbers and labels, compact row height, thin grid lines, amber as the main accent with green/red only for small up/down rating-change arrows next to the score, tabs as small bracketed keys, dropdowns as compact inline fields. Information-dense, precise, no decoration. Clearly different from option A.
```

## 3 — Seçenek C: dövüş afişi

```
Option C: FIGHT POSTER. Exactly the same page content, strings and table rows as option A, but radically different style: bold, loud fight-night poster energy. Heavy condensed uppercase sans-serif, black background with white type and one hot accent colour (signal red), huge outlined rank numbers, the top three fighters shown larger as a podium strip above the rest of the table, diagonal cut edges or a subtle halftone texture in the header. Still a usable web page with a readable table. Clearly different from options A and B.
```

## 4 — Seçenek D: modern ürün arayüzü

```
Option D: MODERN PRODUCT UI. Exactly the same page content, strings and table rows as option A, but radically different style: a clean, light, contemporary app interface. Soft light-grey background, white rounded cards with subtle shadows, a modern geometric sans-serif, segmented-control style division tabs, pill dropdowns, each table row with a tiny sparkline showing the fighter's rating over the last 3 years, one calm accent colour (indigo). Friendly, airy, polished. Clearly different from options A, B and C.
```

## 5 — Seçenek E: bilimsel / veri gazeteciliği

```
Option E: SCIENTIFIC DATA JOURNALISM. Exactly the same page content, strings and table rows as option A, but radically different style: a calm, research-grade data visualisation page (think a statistics-driven explainer site). White background, muted blue-grey palette, a humanist sans-serif, and the key idea: next to each fighter the uncertainty is drawn as a horizontal interval bar (μ − 2·RD to μ + 2·RD on a shared axis, with a dot at μ), so overlapping bars make it visible which ranks are statistically close. Small footnote-style annotations, a tiny legend explaining the bar. Clearly different from options A, B, C and D.
```

---

Kullanıcı A–E'nin hiçbirini beğenmedi; ikinci tur (F–J). Bu turda düzen de serbest (yalnızca içerik aynı).

## 6 — Seçenek F: koyu premium spor uygulaması

```
Feedback: the user did not like any of options A–E. Let's do a second round of 5 new options (F, G, H, I, J), one per message. They must be clearly different from A–E AND from each other. This time you may also change the LAYOUT (sidebar, cards, detail panel, hero area, vertical division list etc.), not only the colours and type; keep the same page content, Turkish strings and the ten table rows from option A (you may show extra derived elements if they fit, but no photos or portraits of real people, no real organisation logos). Same output format: realistic high-fidelity desktop web page mockup, 16:10 landscape, ~1440 px layout, no browser chrome, crisp legible text.

Option F: PREMIUM DARK SPORTS APP. A modern, high-end sports streaming / stats app feel: deep charcoal-navy background, subtle gradients and soft glows, rounded panels, a hero card for the #1 fighter (big name, score, a small rating-history line chart, monogram avatar circle with initials instead of a photo), the other nine as sleek list rows with monogram avatars, division selector as a horizontal scrolling chip bar, one vivid accent (electric teal). Cinematic but clean, not poster-like.
```

## 7 — Seçenek G: İsviçre tipografi stili

```
Option G: SWISS / INTERNATIONAL TYPOGRAPHIC STYLE. Strict modular grid, asymmetric layout, a neo-grotesque sans-serif only, huge bold rank numerals, black text on white with one solid colour block (pure signal orange) used structurally (e.g. a large block behind the page title and the selected division), divisions as a vertical list on the left, flush-left ragged-right text, no shadows, no rounded corners, no icons. Bauhaus-poster discipline applied to a data page. Clearly different from A–F.
```

## 8 — Seçenek H: neo-brutalist web

```
Option H: NEO-BRUTALIST WEB. Playful and bold: thick black 3 px outlines on every element, hard offset drop shadows (no blur), flat saturated colours (lemon yellow background, hot pink and cobalt blue blocks), chunky rounded sans-serif, buttons and dropdowns that look physically pressable, table rows as stacked outlined strips, small sticker-like tags ("inaktif −40"). Fun but still perfectly readable. Clearly different from A–G.
```

## 9 — Seçenek I: lüks minimal monokrom

```
Option I: LUXURY MINIMAL MONOCHROME. The restraint of a high-end fashion or watch brand website: pure white space everywhere, black text only plus thin warm-gold hairlines, an ultra-light large display serif for the title and fighter names paired with a tiny widely-tracked uppercase sans for labels, all ten rows must still fit on the page, numbers in elegant tabular figures. Quiet, expensive, gallery-like. Clearly different from A–H.
```

## 10 — Seçenek J: analiz panosu (üç sütun)

```
Option J: ANALYST DASHBOARD, THREE-COLUMN LAYOUT. Left: a slim vertical navigation with the filters (Yıl, Ay, Kapsam) and the division list. Middle: the ranking table (selected row "Arman Tsarukyan" highlighted). Right: a detail panel for the selected fighter: name with monogram avatar, Puan and μ ± RD as large figures, a rating-history line chart 2020–2026 with a shaded ±2·RD band, and a "Son 5 maç" mini list with W/L badges (W: KO, W: UD, L: SD, W: SUB, W: UD). Medium-dark slate theme with crisp light text and two accent colours (mint for wins, coral for losses). Functional, information-rich, like a pro analytics tool. Clearly different from A–I.
```

---

Kullanıcı F–J'yi de beğenmedi; üçüncü tur (K–O): GPT'ye serbest tasarım hakkı. Stil, düzen ve sayfanın ne göstereceği GPT'nin kararı.

## 11 — Serbest K

```
The user did not like options F–J either. New approach for the third round: you get full creative freedom. Forget my earlier style directions; I will only tell you what the project is and you decide everything — the concept, what the home page shows, the layout, the visual language, colours, type, whether it is a table at all. Surprise us; be genuinely imaginative. We will do 5 free designs (K, L, M, N, O), one per message, each a completely different idea of your own, and each clearly different from all ten earlier options.

The project:
- A non-commercial, Turkish-language MMA ratings website (name: "MMA Rankings"). Audience: Turkish MMA fans and stats-curious people.
- What makes it different from official rankings: ratings are purely mathematical (a Glicko rating system computed from every pro fight since the 1990s), fully transparent (the method is public), historical (you can see the ranking of any month in history, computed only from fights before that date), and honest about uncertainty (each rating has an uncertainty ± RD; the ranking score is μ − 2·RD, with a penalty for inactivity).
- Data the site really has: for every fighter a monthly rating history (μ and RD), record, division, organisations fought in, full fight history with opponent, date, method (KO/SUB/UD/SD…), and the rating change from each fight; rankings per division (Heavyweight … Flyweight) and per organisation, plus a P4P index; any month can be selected.
- Use real fighter names if you show fighters (e.g. Islam Makhachev, Arman Tsarukyan, Charles Oliveira, Ilia Topuria, Justin Gaethje); numbers can be illustrative.

Constraints: it must be buildable as a real website (HTML/CSS/JS) and readable; UI text in Turkish; no realistic photos or likenesses of real people (initials, abstract shapes or silhouettes are fine); no real organisation logos. Output: one high-fidelity desktop web page mockup, 16:10 landscape, no browser chrome, crisp legible text.

Now design K: your first free idea.
```

## 12–15 — Serbest L, M, N, O

```
Design <X>: another free idea of your own, a completely different concept and visual language from K…<previous> and from all ten earlier options. Same project, same constraints and output format.
```

---

Kullanıcı K–O'yu da beğenmedi; dördüncü tur (P–T): kullanıcının seçtiği referanslardan moodboard.
Referanslar (görseller repoya konmadı, telif başkalarının; yalnızca GPT'ye -i ile verildi):
- Behance 179198175 "Dashboard football manager" · Behance 257265389 "LensArt" (kullanıcı: "renk paletine aşık oldum")
- Behance 129472149 "Statistic Sports" · Dribbble 27312483 "Boxing Match Event Dashboard"
- Awwwards "Fighter Ready" · Awwwards "Williams Grand Prix Tech"
Kullanıcının istekleri: dövüşçü fotoğrafları; site ileride animasyonlu/dinamik olacak (taslakta değil).

## 16 — P (moodboard, ilk)

```
New direction. The user rejected K–O too, but now gave us a moodboard of references they love (attached images). Treat them as a MOODBOARD, not as screens to copy: LensArt (two images: the user is in love with this colour palette — near-black backgrounds, deep red atmospheric glow, one hot red accent, white type, muted grey secondary text, bracketed small labels like "[ 01 — about ]", pill-shaped outline buttons), a football manager dashboard (dark panels, hot accent, a person cut-out overlapping the UI), a sports statistics site (big hero match card with stadium atmosphere), a boxing event dashboard (huge fighter cut-out photos facing each other, giant condensed names behind them, dark warm tones, date strip), Fighter Ready (cinematic dark combat-sports site, huge condensed uppercase headlines, wide-tracked small nav labels, thin orange line accents), Williams Grand Prix Tech (premium, restrained, dramatic lighting, lots of dark negative space).

What the user wants:
1. FIGHTER PHOTOS are central: dramatic, cinematic cut-out photos of fighters (like the boxing reference). IMPORTANT: since the photos must not depict any real person, in these mockups use FICTIONAL fighters with fictional names (e.g. "Kerem Aydın", "Diego Valverde", "Malik Okafor", "Ivan Sorokin", "Tomás Herrera", "Rustam Aliev") and photorealistic but entirely invented, non-identifiable faces.
2. The LensArt colour palette as the base for every design.
3. The site will later be animated and dynamic (scroll animations, transitions), so cinematic layouts that would come alive with motion are welcome, but draw a still frame.

The project (unchanged): Turkish-language, non-commercial MMA ratings site "MMA Rankings": purely mathematical Glicko ratings from every pro fight since the 1990s, transparent method, historical (any month's ranking), honest about uncertainty (rating μ ± RD, ranking score μ − 2·RD, inactivity penalty). Data: ranking per division and organisation, P4P index, each fighter's monthly rating history, record, fight history with opponent, method and rating change. UI text in Turkish.

We will do 5 designs (P, Q, R, S, T), one per message, each a different concept within this moodboard and clearly different from each other. You decide concept and layout; be imaginative. Output: one high-fidelity desktop web page mockup, 16:10 landscape, no browser chrome, crisp legible text, no real organisation logos.

Now design P.
```

## 17–20 — Q, R, S, T

```
Design <X>: another concept within the same moodboard, palette and requirements (fictional fighters with cinematic cut-out photos, LensArt palette, Turkish UI), clearly different from P…<previous>.
```

---

Kullanıcı P–T'yi de beğenmedi (fotoğraflar gerçekçi değil, ilk ekranda ilk 15 görünmüyor). Serbest fotoğraf kaynaklarının kalitesi yetmediği için
listelerde fotoğraf yok kararı alındı. Beşinci tur (U–X), yeni sohbet: `mma-arayuz-2` (`mma-arayuz` 20 çizimde doldu).
Görseller: `docs/gpt/mma-arayuz-2/`. Referans: LensArt görselleri (-i, repoda değil).

## 21 — U: liste kahraman

```
Fifth design round for a non-commercial, Turkish-language MMA ratings website called "MMA Rankings". Earlier rounds (20 mockups) were all rejected. What we learned from that:
- The user LOVES the colour palette of the attached LensArt reference images: near-black background, deep red atmospheric glow, one hot red accent (#E8392B-ish), crisp white type, muted grey secondary text, small bracketed labels like "[ 01 — sıralama ]", pill-shaped outline buttons, thin hairline rules, a big bold grotesque display type with one word in red. Use this palette and its mood as the base. Treat the references as palette/mood only, do not copy their layout or content.
- NO PHOTOS of fighters anywhere on this page. We cannot get good photos legally, so the design must be dramatic and beautiful through TYPOGRAPHY, DATA and LIGHT alone: huge condensed numerals, red glow and gradients, hairlines, tiny charts, flags, motion-ready shapes. No silhouettes pretending to be photos, no illustrated faces either.
- The first screen must show the FULL TOP 15 of the selected list without scrolling (desktop 1440×900 viewport). A big cinematic hero that pushes the list below the fold was the main complaint. A compact header plus a strong #1 treatment is fine, as long as all 15 rows are visible.
- Later the site will be animated (numbers counting up, rows sliding in, glow pulsing), so shapes that would come alive with motion are welcome; draw a still frame.

The project: purely mathematical Glicko ratings computed from every pro MMA fight since the 1990s; transparent method; historical (any month can be selected, ranking computed only from earlier fights); honest about uncertainty (rating μ ± RD, ranking score μ − 2·RD, minus an inactivity penalty).

Page content to show (UI text in Turkish, keep these strings):
- Site name "MMA Rankings", nav: Sıralamalar · Dövüşçüler · Arşiv · Yöntem, a search field "Dövüşçü ara".
- Selectors: month "Kasım 2026" (with prev/next arrows), scope "Global", divisions P4P, Heavyweight, Light Heavyweight, Middleweight, Welterweight, Lightweight (selected), Featherweight, Bantamweight, Flyweight.
- List title "Lightweight · Kasım 2026", note "Son güncelleme: 4 Kasım 2026".
- 15 rows: rank, change vs last month (▲/▼/–), country flag, name, Puan (big), μ ± RD (small), Rekor, Son maç. Illustrative data:
  1 Islam Makhachev RUS 1912 | 2061 ± 74 | 27-1 | Oca 2026 | –
  2 Arman Tsarukyan ARM 1868 | 2013 ± 72 | 22-3 | Eki 2026 | ▲1
  3 Charles Oliveira BRA 1801 | 1958 ± 78 | 35-10 | Eyl 2026 | ▼1
  4 Ilia Topuria ESP 1795 | 1972 ± 88 | 17-0 | Haz 2026 | –
  5 Justin Gaethje USA 1742 | 1906 ± 82 | 26-6 | Mar 2026 | –
  6 Dan Hooker NZL 1731 | 1890 ± 79 | 24-12 | Ağu 2026 | ▲2
  7 Mateusz Gamrot POL 1720 | 1874 ± 77 | 25-3 | Tem 2026 | –
  8 Paddy Pimblett GBR 1712 | 1885 ± 86 | 23-3 | May 2026 | ▼2
  9 Beneil Dariush USA 1690 | 1871 ± 90 | 22-6 | Kas 2024 | ▼1, small tag "inaktif −40"
  10 Renato Moicano BRA 1684 | 1850 ± 83 | 20-6 | Şub 2026 | –, small "≈" marker after the name
  11 Rafael Fiziev AZE 1679 | 1846 ± 84 | 13-3 | Haz 2026 | ▲1
  12 Benoît Saint Denis FRA 1671 | 1838 ± 83 | 15-3 | Ağu 2026 | ▼1
  13 Mauricio Ruffy BRA 1664 | 1859 ± 97 | 12-1 | Eki 2026 | ▲4
  14 Michael Chandler USA 1652 | 1822 ± 85 | 23-10 | Nis 2026 | –
  15 Grant Dawson USA 1648 | 1810 ± 81 | 22-2 | Tem 2026 | ▲1
- Optional derived elements if they fit: a tiny rating-history sparkline per row, or an uncertainty bar (μ ± 2·RD on a shared axis).

We will do 4 options (U, V, W, X), one per message, all in this palette and all photo-free with 15 visible rows, but each a clearly different layout idea. Output: one high-fidelity desktop web page mockup, 16:10 landscape, no browser chrome, no device frame, crisp legible text, no real organisation logos.

Now design U: the list itself is the hero. A compact top bar, a slim left column with the division list and month selector, and the 15 rows filling the screen; the #1 row is taller and treated cinematically (huge red-glowing "01", the name in big condensed white type, the score as a giant numeral), rows 2–15 are tight, elegant hairline rows with right-aligned tabular numbers and a thin red sparkline.
```

## 22 — V: bölünmüş ekran

```
Good, U is on target (palette, no photos, 15 rows visible). Keep the same content, data, palette and constraints.

Now design V, a clearly different layout from U: a SPLIT SCREEN. Left ~40%: the #1 fighter as a typographic poster with no photo — a giant red-glowing "01", the name ISLAM MAKHACHEV stacked in huge condensed white type, the score 1912 as an enormous numeral, "μ 2061 ± 74 · 27-1 · Oca 2026" small below, and a large rating-history line chart 2018–2026 with a soft red ±2·RD band glowing behind it. Right ~60%: the division selector as a horizontal row of pill chips at the top, then rows 2–15 as a compact table (rank, change arrow, flag, name, Puan, μ ± RD, Rekor, Son maç), plus the "inaktif −40" tag and "≈" marker. Compact top bar with site name, nav and search; month selector "‹ Kasım 2026 ›" and "Global" near the list title.
```

## 23 — W: belirsizlik merdiveni

```
V is good too. Small fix for the rest: the name is "Arman Tsarukyan" (one r).

Now design W, clearly different from U and V: the UNCERTAINTY LADDER is the hero. Compact top bar (site name, nav, search), under it one line with the list title "Lightweight · Kasım 2026", "‹ Kasım 2026 ›", "Global" and the division chips. Then all 15 fighters as rows where the main visual is a horizontal glowing interval bar on ONE shared rating axis (1500 → 2250, axis labels at the top): the bar spans μ − 2·RD to μ + 2·RD, a bright white dot marks μ, and a small red tick marks the ranking score (Puan). Overlapping bars visibly show which ranks are statistically close; draw a subtle bracket on the right grouping ranks 2–4 with the label "[ istatistiksel olarak yakın ]". Left of each bar: rank, change arrow, flag, name; right: Puan (big), Rekor, Son maç. The #1 row slightly larger with a stronger red glow. A one-line legend at the bottom: "nokta = μ · çubuk = μ ± 2·RD · kırmızı çizgi = sıralama puanı".
```

## 24 — X: kademeli (ilk 3 kart + iki sütun)

```
Fixes for the rest: all visible text must be Turkish (no English headline like "Uncertainty Ladder"), and the first division chip is "P4P" (not "PAP").

Now design X, the last of this round, clearly different from U, V and W: a TIERED layout. Compact top bar (site name, nav, search), then one line with the list title "Lightweight · Kasım 2026", "‹ Kasım 2026 ›", "Global", "Son güncelleme: 4 Kasım 2026" and the division chips. Below: the top 3 as three wide side-by-side typographic cards (no photos) — each with a big glowing rank numeral ("01" in hot red, "02" and "03" in white), flag, name in large condensed type, Puan as a large numeral, μ ± RD, Rekor, Son maç and a small rating-history line; #1's card is a bit taller with a red atmospheric glow behind it. Under the cards: ranks 4–15 in TWO COLUMNS of six compact hairline rows each (rank, change arrow, flag, name, Puan, Rekor, Son maç, with the "inaktif −40" tag and "≈" marker). Everything from 1 to 15 must be visible on one 1440×900 screen.
```

---

Kullanıcı U + W karışımını seçti.

## 25 — UW: masaüstü liste

```
The user chose a MIX OF U AND W. From now on this is THE style; next we will draw the mobile version and the fighter profile page in it.

Draw the final desktop list page (1440×900, all 15 rows visible, same data, palette, Turkish strings, no photos):
- Structure from U: one single list is the hero. Compact top bar (site name "MMA Rankings" with "Rankings" in red, nav Sıralamalar · Dövüşçüler · Arşiv · Yöntem, search "Dövüşçü ara").
- Instead of U's left column, put the controls in one line above the list, as in V/W: title "Lightweight · Kasım 2026", "‹ Kasım 2026 ›", "Global ▾", "Son güncelleme: 4 Kasım 2026", and the division pill chips (P4P … Flyweight, Lightweight selected in red).
- The #1 row taller and cinematic as in U: huge red-glowing "01", ISLAM MAKHACHEV in big condensed white type, score 1912 as a giant numeral, soft red glow behind the row.
- Rows 2–15 tight hairline rows: rank, change arrow, flag, name (title case, not all caps, for readability), then — replacing U's identical sparklines — W's glowing uncertainty interval bar in a medium-width column on one shared axis (thin axis labels 1500 · 1800 · 2100 above the column): bar = μ ± 2·RD, white dot = μ, small red tick = ranking score. NO numeric labels on the bars (they appear on hover later). Then Puan (big tabular numeral), μ ± RD (small grey), Rekor, Son maç. Keep "inaktif −40" tag and "≈" marker.
- A subtle bracket at the bar column grouping ranks 2–4 labelled "[ başa baş ]".
- One-line legend at the bottom: "nokta = μ · çubuk = μ ± 2·RD · kırmızı çizgi = sıralama puanı" and "Puan = μ − 2·RD − inaktivite cezası".
```

## 26 — UW: mobil

```
This desktop page (25) is the chosen design. Keep exactly its style.

Now draw the SAME page on MOBILE: show three phone screens side by side on a dark background (each 390×844, iPhone-size, no device frame needed, just three tall screen rectangles with small gaps), all in this exact style and palette, Turkish UI, no photos:
1. Top of the list: compact header (logo "MMA Rankings", search icon, menu icon), title "Lightweight · Kasım 2026", a row with "‹ Kasım 2026 ›" and "Global ▾", a horizontally scrolling division chip bar (Lightweight selected in red, the others partially cut off at the right edge), then the #1 row as a compact cinematic block (red-glowing "01", flag, ISLAM MAKHACHEV, giant 1912, "2061 ± 74 · 27-1 · Oca 2026", the uncertainty bar under it), then rows 2–6.
2. Scrolled further: rows 5–15 as two-line rows — line 1: rank, change arrow, flag, name, Puan big on the right; line 2: the full-width thin uncertainty bar (shared axis) with "27-1 · Oca 2026"-style small grey text — so at least 10 rows fit on the screen. "[ başa baş ]" shown as a thin red side bracket on ranks 2–4 on screen 1. Keep the "inaktif −40" tag and "≈" marker.
3. One row tapped: a bottom sheet sliding up over the dimmed list, for Arman Tsarukyan: flag, name, Puan 1868, μ 2013 ± 72, Rekor 22-3, a small rating-history line 2018–2026 with a red ±2·RD band, the last 3 fights (G · KO · Eki 2026 · +18; G · UD · Mar 2026 · +9; M · SD · Eyl 2025 · −12), and a red pill button "Profili aç →".
```

## 27 — UW: profil

```
Mobile (26) is good. Same exact style for the last screen.

Now the FIGHTER PROFILE PAGE, desktop 1440×900, for Arman Tsarukyan, Turkish UI, same top bar as page 25 (with a small breadcrumb "Sıralamalar / Lightweight / Arman Tsarukyan").
- Header band: on the left a PORTRAIT PLACEHOLDER box (4:5, about 260×325 px) — it must NOT show a face: a dark box with a thin hairline border, a small camera icon and the text "Resmi portre" and "Getty Images · göstermek için tıklayın" (the official photo loads only on click, for privacy). Next to it: huge red-glowing "02" with "Lightweight · Global" label, the name ARMAN TSARUKYAN in big condensed white type, Armenian flag, "▲1 bu ay", and a stat row: Puan 1868 (giant numeral) · μ 2013 ± 72 · Rekor 22-3 · Son maç Eki 2026 · Organizasyonlar: UFC.
- Main area left (about 60%): the hero chart "[ puan geçmişi ]": rating μ line 2015–2026 glowing red, with the ±2·RD band as a soft red glow behind it, small dots for each fight on the line, a vertical hairline marker at a hovered fight with a tooltip "Eki 2026 · G · KO · +18".
- Main area right (about 40%): "[ maç geçmişi ]" — a compact table of the last 8 fights: tarih, rakip (with flag), sonuç badge (G in white on red outline, M in grey), yöntem (KO, UD, SD, SUB…), puan değişimi (+18 green-ish white, −12 red). Illustrative opponents: Mateusz Gamrot, Charles Oliveira, Beneil Dariush, Joaquim Silva, Damir Ismagulov, Christos Giagos, Mateusz Gamrot, Islam Makhachev (that one a loss: M · UD · −15).
- Small bottom row "[ benzer seviyede ]": three compact chips for Charles Oliveira 1801, Ilia Topuria 1795, Islam Makhachev 1912 each with a mini uncertainty bar.
```
