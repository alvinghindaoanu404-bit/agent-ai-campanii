# Giveaway TikTok – Anne Maica

Pagină cu două secțiuni:
1. **Extrage comentariile** – lipești linkul TikTok; serverul pornește un scraper Apify și aduce toate comentariile (sau le încarci manual: text, CSV, JSON).
2. **Alege câștigătorul** – ruletă animată; câștigătorul e ales cu `crypto.getRandomValues` dintre **toți** participanții, apoi banda se oprește pe el. „Re-extrage” scoate câștigătorul din listă și pornește din nou.

## Publicare pe Vercel
1. Fă cont pe https://apify.com → Settings → API & Integrations → copiază **API token**.
2. Pe https://vercel.com → Add New Project → importă repository-ul.
3. La **Root Directory** alege `giveaway`. Framework: *Other*. Fără build command.
4. La **Environment Variables** adaugă `APIFY_TOKEN` = tokenul tău. Opțional `APIFY_ACTOR` (implicit `clockworks~tiktok-comments-scraper`).
5. Deploy.

## Poza de fundal
Pune imaginea în `giveaway/assets/anne.png` (ideal PNG cu fundal transparent, portret). Dacă lipsește, pagina funcționează fără ea.

## Cost
Plata se face pe comentarii extrase, prin Apify. Verifică prețul actual pe pagina scraperului înainte de giveaway.
