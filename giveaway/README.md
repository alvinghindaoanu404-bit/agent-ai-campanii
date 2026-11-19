# Giveaway TikTok – Anne Maica (@anne.maica)

Site static (GitHub Pages), două secțiuni:
1. **Extrage comentariile** – lipești linkul TikTok; pagina pornește actorul Apify `clockworks/tiktok-scraper` direct din browser și aduce comentariile. Alternativ: încărcare manuală (text, CSV, JSON).
2. **Alege câștigătorul** – ruletă animată; câștigătorul e ales cu `crypto.getRandomValues` dintre **toți** participanții, iar banda se oprește pe el. „Re-extrage” scoate câștigătorul din listă și pornește din nou.

## Cheia Apify – important
GitHub Pages nu are server, deci cheia **nu** stă în cod (oricine ar putea s-o citească din sursa paginii și ți-ar consuma creditul). O introduci în pagină, la „🔑 Cheia Apify”; rămâne doar în browserul tău (localStorage, dacă bifezi „Ține minte”) și e trimisă doar la `api.apify.com`.

- Nu introduce cheia pe calculatoare străine. Dacă ai făcut-o, debifează „Ține minte” sau regenerează tokenul în Apify.
- Recomandat: în Apify Console creează un token separat doar pentru acest giveaway și șterge-l după.

## Publicare pe GitHub Pages
1. Repository-ul trebuie să fie **public** (Pages pe repo privat cere plan GitHub plătit).
2. Settings → Pages → **Source: GitHub Actions**.
3. Unește (merge) branch-ul în `main`. Workflow-ul `.github/workflows/pages.yml` publică automat doar folderul `giveaway/`.
4. Linkul apare în Settings → Pages (de forma `https://<utilizator>.github.io/<repo>/`).

## Cost (verificat pe pagina de prețuri Apify, nov. 2026)
~0,0037 $ pentru video + ~1,25 $ / 1.000 comentarii. Limita din câmpul „Număr maxim de comentarii” plafonează costul.
