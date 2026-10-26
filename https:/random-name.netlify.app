from flask import Flask, render_template_string, send_from_directory  # type: ignore[reportMissingImports]
import os

app = Flask(__name__)

# Шлях до картинки (етикетки)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

HTML = """
<!DOCTYPE html>
<html lang="uk">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Castacraftowe — Крафтове пиво з українською душею | Poznań</title>
  <meta name="description" content="Castacraftowe — власний крафт у Познані. Живе нефільтроване пиво: Jasne, Porter, Pszeniczne, Blanche, IPA. Затишний бар на Półwiejska 6." />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet" />
  <style>
    :root {
      --navy: #0a1628;
      --navy-light: #12233d;
      --gold: #d4a84b;
      --gold-light: #e8c87a;
      --cream: #f5f0e6;
      --text: #e8e4d9;
      --muted: #a8a194;
      --card: #15253f;
    }

    * { margin: 0; padding: 0; box-sizing: border-box; }
    html { scroll-behavior: smooth; }

    body {
      font-family: 'Inter', system-ui, sans-serif;
      background: var(--navy);
      color: var(--text);
      line-height: 1.6;
      overflow-x: hidden;
    }

    h1, h2, h3, .logo { font-family: 'Playfair Display', serif; }

    nav {
      position: fixed; top: 0; left: 0; right: 0; z-index: 100;
      display: flex; justify-content: space-between; align-items: center;
      padding: 1.1rem 5%;
      background: rgba(10, 22, 40, 0.92);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid rgba(212, 168, 75, 0.15);
      transition: padding 0.3s;
    }
    nav.scrolled { padding: 0.7rem 5%; }

    .logo {
      font-size: 1.45rem; font-weight: 700; color: var(--gold);
      letter-spacing: 0.04em; text-decoration: none;
    }
    .logo span { color: var(--cream); font-weight: 500; }

    .nav-links { display: flex; gap: 2rem; list-style: none; }
    .nav-links a {
      color: var(--text); text-decoration: none; font-size: 0.92rem;
      font-weight: 500; letter-spacing: 0.03em; transition: color 0.25s;
      position: relative;
    }
    .nav-links a::after {
      content: ''; position: absolute; bottom: -4px; left: 0;
      width: 0; height: 1.5px; background: var(--gold); transition: width 0.3s;
    }
    .nav-links a:hover { color: var(--gold); }
    .nav-links a:hover::after { width: 100%; }

    .nav-cta {
      background: var(--gold); color: var(--navy) !important;
      padding: 0.55rem 1.3rem; border-radius: 4px; font-weight: 600;
    }
    .nav-cta::after { display: none !important; }
    .nav-cta:hover { background: var(--gold-light); color: var(--navy) !important; }

    .burger {
      display: none; flex-direction: column; gap: 5px;
      cursor: pointer; background: none; border: none;
    }
    .burger span { width: 24px; height: 2px; background: var(--gold); }

    .hero {
      min-height: 100vh; display: grid; grid-template-columns: 1.1fr 0.9fr;
      align-items: center; padding: 8rem 5% 4rem; gap: 3rem;
      position: relative; overflow: hidden;
    }
    .hero::before {
      content: ''; position: absolute; inset: 0;
      background: 
        radial-gradient(ellipse 80% 60% at 70% 40%, rgba(212, 168, 75, 0.08) 0%, transparent 60%),
        radial-gradient(ellipse 50% 40% at 20% 80%, rgba(18, 50, 90, 0.4) 0%, transparent 50%);
      pointer-events: none;
    }
    .hero-content { position: relative; z-index: 2; }
    .hero-badge {
      display: inline-block; font-size: 0.78rem; letter-spacing: 0.18em;
      text-transform: uppercase; color: var(--gold);
      border: 1px solid rgba(212, 168, 75, 0.4);
      padding: 0.4rem 1rem; border-radius: 30px; margin-bottom: 1.5rem;
    }
    .hero h1 {
      font-size: clamp(2.6rem, 5vw, 4.2rem); line-height: 1.15;
      color: var(--cream); margin-bottom: 1.2rem;
    }
    .hero h1 em { font-style: normal; color: var(--gold); }
    .hero-desc {
      font-size: 1.15rem; color: var(--muted); max-width: 520px;
      margin-bottom: 2.2rem; font-weight: 300;
    }
    .hero-actions { display: flex; gap: 1rem; flex-wrap: wrap; }

    .btn {
      display: inline-flex; align-items: center; gap: 0.5rem;
      padding: 0.9rem 1.8rem; border-radius: 4px; font-weight: 600;
      font-size: 0.95rem; text-decoration: none; transition: all 0.25s;
      cursor: pointer; border: none;
    }
    .btn-primary { background: var(--gold); color: var(--navy); }
    .btn-primary:hover {
      background: var(--gold-light); transform: translateY(-2px);
      box-shadow: 0 8px 25px rgba(212, 168, 75, 0.25);
    }
    .btn-outline {
      background: transparent; color: var(--gold);
      border: 1.5px solid var(--gold);
    }
    .btn-outline:hover { background: rgba(212, 168, 75, 0.1); }

    .hero-stats {
      display: flex; gap: 2.5rem; margin-top: 3.5rem; padding-top: 2rem;
      border-top: 1px solid rgba(212, 168, 75, 0.2);
    }
    .stat strong {
      display: block; font-size: 1.8rem; color: var(--gold);
      font-family: 'Playfair Display', serif;
    }
    .stat span { font-size: 0.85rem; color: var(--muted); }

    .hero-visual {
      position: relative; z-index: 2;
      display: flex; justify-content: center; align-items: center;
    }
    .label-frame { position: relative; max-width: 420px; width: 100%; }
    .label-frame img {
      width: 100%; border-radius: 12px;
      box-shadow: 0 25px 60px rgba(0,0,0,0.5), 0 0 0 1px rgba(212, 168, 75, 0.2);
      transition: transform 0.4s;
    }
    .label-frame:hover img { transform: scale(1.02); }
    .label-glow {
      position: absolute; inset: -20px;
      background: radial-gradient(circle, rgba(212, 168, 75, 0.15) 0%, transparent 70%);
      z-index: -1; filter: blur(20px);
    }

    section { padding: 6rem 5%; }
    .section-header { text-align: center; max-width: 700px; margin: 0 auto 3.5rem; }
    .section-header .eyebrow {
      font-size: 0.8rem; letter-spacing: 0.2em; text-transform: uppercase;
      color: var(--gold); margin-bottom: 0.8rem;
    }
    .section-header h2 {
      font-size: clamp(2rem, 4vw, 2.8rem); color: var(--cream); margin-bottom: 1rem;
    }
    .section-header p { color: var(--muted); font-size: 1.05rem; }

    .about { background: var(--navy-light); }
    .about-grid {
      display: grid; grid-template-columns: 1fr 1fr; gap: 4rem;
      align-items: center; max-width: 1200px; margin: 0 auto;
    }
    .about-text h3 { font-size: 1.6rem; color: var(--gold); margin-bottom: 1.2rem; }
    .about-text p { color: var(--muted); margin-bottom: 1.2rem; font-size: 1.05rem; }
    .about-features {
      display: grid; grid-template-columns: 1fr 1fr; gap: 1.2rem; margin-top: 2rem;
    }
    .feature {
      background: var(--card); padding: 1.3rem; border-radius: 8px;
      border: 1px solid rgba(212, 168, 75, 0.12);
    }
    .feature strong { display: block; color: var(--gold); margin-bottom: 0.3rem; font-size: 0.95rem; }
    .feature span { font-size: 0.88rem; color: var(--muted); }

    .about-card {
      background: var(--card); border-radius: 12px; padding: 2rem;
      border: 1px solid rgba(212, 168, 75, 0.15);
    }
    .about-card h4 { color: var(--gold); margin-bottom: 1rem; font-size: 1.2rem; }
    .hours-list { list-style: none; }
    .hours-list li {
      display: flex; justify-content: space-between; padding: 0.6rem 0;
      border-bottom: 1px solid rgba(255,255,255,0.06); font-size: 0.95rem;
    }
    .hours-list li:last-child { border-bottom: none; }
    .hours-list .day { color: var(--muted); }
    .hours-list .time { color: var(--cream); font-weight: 500; }

    .beers { background: var(--navy); }
    .beer-grid {
      display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 1.8rem; max-width: 1200px; margin: 0 auto;
    }
    .beer-card {
      background: var(--card); border-radius: 12px; overflow: hidden;
      border: 1px solid rgba(212, 168, 75, 0.12);
      transition: transform 0.3s, box-shadow 0.3s;
    }
    .beer-card:hover {
      transform: translateY(-6px); box-shadow: 0 20px 40px rgba(0,0,0,0.3);
      border-color: rgba(212, 168, 75, 0.3);
    }
    .beer-header {
      padding: 1.6rem 1.6rem 1rem;
      border-bottom: 1px solid rgba(212, 168, 75, 0.1);
    }
    .beer-header h3 { font-size: 1.35rem; color: var(--cream); margin-bottom: 0.3rem; }
    .beer-meta { display: flex; gap: 1rem; font-size: 0.85rem; color: var(--gold); }
    .beer-body { padding: 1.2rem 1.6rem 1.6rem; }
    .beer-body p { color: var(--muted); font-size: 0.95rem; margin-bottom: 1rem; }
    .beer-tags { display: flex; flex-wrap: wrap; gap: 0.5rem; }
    .tag {
      font-size: 0.75rem; padding: 0.25rem 0.7rem;
      background: rgba(212, 168, 75, 0.12); color: var(--gold-light); border-radius: 20px;
    }

    .snacks { background: var(--navy-light); }
    .snacks-grid {
      display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
      gap: 1.5rem; max-width: 1000px; margin: 0 auto;
    }
    .snack-item {
      background: var(--card); padding: 1.5rem; border-radius: 10px;
      text-align: center; border: 1px solid rgba(212, 168, 75, 0.1);
      transition: border-color 0.3s;
    }
    .snack-item:hover { border-color: rgba(212, 168, 75, 0.35); }
    .snack-icon { font-size: 2rem; margin-bottom: 0.8rem; }
    .snack-item h4 { color: var(--cream); font-size: 1.05rem; margin-bottom: 0.3rem; }
    .snack-item p { font-size: 0.85rem; color: var(--muted); }

    .reviews { background: var(--navy); }
    .reviews-grid {
      display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
      gap: 1.8rem; max-width: 1200px; margin: 0 auto;
    }
    .review-card {
      background: var(--card); padding: 1.8rem; border-radius: 12px;
      border: 1px solid rgba(212, 168, 75, 0.12); position: relative;
    }
    .review-card::before {
      content: '"'; position: absolute; top: 0.8rem; left: 1.2rem;
      font-size: 4rem; font-family: 'Playfair Display', serif;
      color: rgba(212, 168, 75, 0.15); line-height: 1;
    }
    .review-stars { color: var(--gold); font-size: 0.95rem; margin-bottom: 1rem; letter-spacing: 2px; }
    .review-text { color: var(--text); font-size: 0.98rem; margin-bottom: 1.2rem; position: relative; z-index: 1; }
    .review-author { font-size: 0.88rem; color: var(--muted); }
    .review-author strong { color: var(--gold-light); }

    .analysis-box {
      max-width: 900px; margin: 3.5rem auto 0;
      background: linear-gradient(135deg, rgba(212, 168, 75, 0.08), rgba(18, 35, 63, 0.6));
      border: 1px solid rgba(212, 168, 75, 0.25); border-radius: 14px; padding: 2.2rem;
    }
    .analysis-box h3 { color: var(--gold); margin-bottom: 1rem; font-size: 1.3rem; }
    .analysis-box ul {
      list-style: none; display: grid; grid-template-columns: 1fr 1fr; gap: 0.8rem;
    }
    .analysis-box li {
      color: var(--muted); font-size: 0.95rem; padding-left: 1.4rem; position: relative;
    }
    .analysis-box li::before {
      content: '✦'; position: absolute; left: 0; color: var(--gold); font-size: 0.75rem;
    }

    .location { background: var(--navy-light); }
    .location-grid {
      display: grid; grid-template-columns: 1fr 1fr; gap: 3rem;
      max-width: 1100px; margin: 0 auto; align-items: start;
    }
    .location-info h3 { color: var(--gold); font-size: 1.4rem; margin-bottom: 1.2rem; }
    .info-row { display: flex; gap: 1rem; margin-bottom: 1.3rem; align-items: flex-start; }
    .info-icon {
      width: 40px; height: 40px; background: rgba(212, 168, 75, 0.12);
      border-radius: 8px; display: flex; align-items: center; justify-content: center;
      color: var(--gold); flex-shrink: 0; font-size: 1.1rem;
    }
    .info-text strong { display: block; color: var(--cream); margin-bottom: 0.2rem; }
    .info-text span, .info-text a {
      color: var(--muted); text-decoration: none; font-size: 0.95rem;
    }
    .info-text a:hover { color: var(--gold); }

    .map-container {
      border-radius: 12px; overflow: hidden;
      border: 1px solid rgba(212, 168, 75, 0.2); height: 360px; background: var(--card);
    }
    .map-container iframe {
      width: 100%; height: 100%; border: 0; filter: grayscale(0.3) contrast(1.05);
    }

    .cta {
      background: linear-gradient(180deg, var(--navy) 0%, #0d1c30 100%);
      text-align: center; padding: 5rem 5%;
    }
    .cta h2 { font-size: clamp(1.8rem, 3.5vw, 2.6rem); color: var(--cream); margin-bottom: 1rem; }
    .cta p { color: var(--muted); max-width: 500px; margin: 0 auto 2rem; }

    footer {
      background: #060e1a; padding: 3rem 5% 2rem;
      border-top: 1px solid rgba(212, 168, 75, 0.1);
    }
    .footer-inner {
      max-width: 1100px; margin: 0 auto; display: flex;
      justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1.5rem;
    }
    .footer-logo { font-family: 'Playfair Display', serif; font-size: 1.3rem; color: var(--gold); }
    .footer-links { display: flex; gap: 1.8rem; }
    .footer-links a { color: var(--muted); text-decoration: none; font-size: 0.9rem; transition: color 0.2s; }
    .footer-links a:hover { color: var(--gold); }
    .footer-copy {
      width: 100%; text-align: center; margin-top: 2rem; padding-top: 1.5rem;
      border-top: 1px solid rgba(255,255,255,0.05); font-size: 0.82rem; color: var(--muted);
    }

    @media (max-width: 900px) {
      .hero { grid-template-columns: 1fr; text-align: center; padding-top: 7rem; }
      .hero-desc { margin-left: auto; margin-right: auto; }
      .hero-actions { justify-content: center; }
      .hero-stats { justify-content: center; }
      .hero-visual { order: -1; max-width: 320px; margin: 0 auto; }
      .about-grid, .location-grid { grid-template-columns: 1fr; }
      .about-features { grid-template-columns: 1fr; }
      .analysis-box ul { grid-template-columns: 1fr; }
      .nav-links {
        display: none; position: absolute; top: 100%; left: 0; right: 0;
        background: var(--navy); flex-direction: column; padding: 1.5rem; gap: 1rem;
        border-bottom: 1px solid rgba(212, 168, 75, 0.15);
      }
      .nav-links.open { display: flex; }
      .burger { display: flex; }
    }
    @media (max-width: 600px) {
      .hero-stats { flex-direction: column; gap: 1.2rem; }
      section { padding: 4rem 5%; }
    }
  </style>
</head>
<body>

  <nav id="nav">
    <a href="#" class="logo">CASTA<span>CRAFTOWE</span></a>
    <ul class="nav-links" id="navLinks">
      <li><a href="#about">Про нас</a></li>
      <li><a href="#beers">Пиво</a></li>
      <li><a href="#snacks">Перекуси</a></li>
      <li><a href="#reviews">Відгуки</a></li>
      <li><a href="#location">Контакти</a></li>
      <li><a href="#location" class="nav-cta">Завітай</a></li>
    </ul>
    <button class="burger" id="burger" aria-label="Меню">
      <span></span><span></span><span></span>
    </button>
  </nav>

  <section class="hero">
    <div class="hero-content">
      <div class="hero-badge">Власний крафт • Poznań</div>
      <h1>Пиво з <em>українською</em><br>душею в серці Познані</h1>
      <p class="hero-desc">
        Живе, нефільтроване, зварене з любов’ю. 
        Castacraftowe — це місце, де класичні європейські традиції зустрічаються з українським характером.
      </p>
      <div class="hero-actions">
        <a href="#beers" class="btn btn-primary">Наше пиво</a>
        <a href="#location" class="btn btn-outline">Як нас знайти</a>
      </div>
      <div class="hero-stats">
        <div class="stat"><strong>4.6</strong><span>оцінка Google</span></div>
        <div class="stat"><strong>9+</strong><span>сортів пива</span></div>
        <div class="stat"><strong>2024</strong><span>рік заснування</span></div>
      </div>
    </div>
    <div class="hero-visual">
      <div class="label-frame">
        <div class="label-glow"></div>
        <img src="/static/beer-label.webp" alt="Castacraftowe Jasne" />
      </div>
    </div>
  </section>

  <section class="about" id="about">
    <div class="section-header">
      <div class="eyebrow">Про броварню</div>
      <h2>Свіже. Живе. Наше.</h2>
      <p>Броварня в Мосіні (15 км від Познані) і затишний бар у самому центрі міста.</p>
    </div>
    <div class="about-grid">
      <div class="about-text">
        <h3>Український дух + європейські традиції</h3>
        <p>Castacraftowe народилося з бажання варити справжнє крафтове пиво — без пастеризації, без зайвої фільтрації. Пиво «живе»: дріжджі продовжують працювати навіть після розливу.</p>
        <p>Ми спеціалізуємося на класичних стилях: Jasne, Porter, Pszeniczne, Blanche, а також експериментуємо з IPA, імбиром з медом і сидром.</p>
        <div class="about-features">
          <div class="feature"><strong>Нефільтроване</strong><span>Максимум смаку і аромату</span></div>
          <div class="feature"><strong>Свіже</strong><span>Зазвичай менше 30 днів</span></div>
          <div class="feature"><strong>Власне</strong><span>Варимо самі в Мосіні</span></div>
          <div class="feature"><strong>На кран</strong><span>Найкраще з кеги</span></div>
        </div>
      </div>
      <div class="about-visual">
        <div class="about-card">
          <h4>Години роботи</h4>
          <ul class="hours-list">
            <li><span class="day">Понеділок – Четвер</span><span class="time">14:00 – 22:00</span></li>
            <li><span class="day">П’ятниця</span><span class="time">12:00 – 00:00</span></li>
            <li><span class="day">Субота</span><span class="time">12:00 – 02:00</span></li>
            <li><span class="day">Неділя</span><span class="time">14:00 – 22:00</span></li>
          </ul>
          <p style="margin-top: 1.5rem; font-size: 0.9rem; color: var(--muted);">
            Адреса бару: <strong style="color: var(--cream);">Półwiejska 6, Poznań</strong>
          </p>
        </div>
      </div>
    </div>
  </section>

  <section class="beers" id="beers">
    <div class="section-header">
      <div class="eyebrow">Меню</div>
      <h2>Наше пиво</h2>
      <p>Класика та авторські рецепти. Усе зварено нами.</p>
    </div>
    <div class="beer-grid">
      <div class="beer-card">
        <div class="beer-header"><h3>Jasne</h3><div class="beer-meta"><span>4.5%</span><span>• Lager</span></div></div>
        <div class="beer-body"><p>Легке, освіжаюче світле пиво з делікатним смаком. Класика, яка підходить до всього.</p>
          <div class="beer-tags"><span class="tag">Бестселер</span><span class="tag">Легке</span></div></div>
      </div>
      <div class="beer-card">
        <div class="beer-header"><h3>Porter</h3><div class="beer-meta"><span>~6.8%</span><span>• Porter</span></div></div>
        <div class="beer-body"><p>Темне, оксамитове, з нотами кави та карамелі. Глибокий і насичений смак.</p>
          <div class="beer-tags"><span class="tag">Темне</span><span class="tag">Багато хто хвалить</span></div></div>
      </div>
      <div class="beer-card">
        <div class="beer-header"><h3>Pszeniczne</h3><div class="beer-meta"><span>~5–6%</span><span>• Wheat</span></div></div>
        <div class="beer-body"><p>М’яке пшеничне з легким банановим післясмаком. Сонце в келиху.</p>
          <div class="beer-tags"><span class="tag">Пшеничне</span><span class="tag">Свіже</span></div></div>
      </div>
      <div class="beer-card">
        <div class="beer-header"><h3>Blanche</h3><div class="beer-meta"><span>5%</span><span>• Witbier</span></div></div>
        <div class="beer-body"><p>Білий бельгійський стиль — легкий, фруктовий, з цитрусовими нотами.</p>
          <div class="beer-tags"><span class="tag">Witbier</span></div></div>
      </div>
      <div class="beer-card">
        <div class="beer-header"><h3>Wileńska IPA</h3><div class="beer-meta"><span>~6%</span><span>• IPA</span></div></div>
        <div class="beer-body"><p>Хмільна, ароматна IPA з характером. Для тих, хто любить гірчинку і цитрус.</p>
          <div class="beer-tags"><span class="tag">IPA</span><span class="tag">Хміль</span></div></div>
      </div>
      <div class="beer-card">
        <div class="beer-header"><h3>Imbir z Miodem</h3><div class="beer-meta"><span>~5%</span><span>• Specialty</span></div></div>
        <div class="beer-body"><p>Імбир + мед. Теплий, пряний, незвичайний — особливо добре взимку.</p>
          <div class="beer-tags"><span class="tag">Авторське</span><span class="tag">Мед</span></div></div>
      </div>
      <div class="beer-card">
        <div class="beer-header"><h3>Bursztynowe</h3><div class="beer-meta"><span>~4%</span><span>• Amber</span></div></div>
        <div class="beer-body"><p>Бурштиновий лагер з карамельними нотами солоду. Баланс і м’якість.</p>
          <div class="beer-tags"><span class="tag">Amber</span></div></div>
      </div>
      <div class="beer-card">
        <div class="beer-header"><h3>Cydr Fizz</h3><div class="beer-meta"><span>—</span><span>• Cider</span></div></div>
        <div class="beer-body"><p>Легкий ігристий сидр. Освіжає і добре йде як альтернатива пиву.</p>
          <div class="beer-tags"><span class="tag">Сидр</span></div></div>
      </div>
    </div>
  </section>

  <section class="snacks" id="snacks">
    <div class="section-header">
      <div class="eyebrow">До пива</div>
      <h2>Перекуси</h2>
      <p>Те, що ідеально пасує до келиха.</p>
    </div>
    <div class="snacks-grid">
      <div class="snack-item"><div class="snack-icon">🥜</div><h4>Горішки в паніровці</h4><p>BBQ, чилі, васабі, сирно-цибульні</p></div>
      <div class="snack-item"><div class="snack-icon">🐟</div><h4>Сушена риба</h4><p>Блєкіт, кальмар, краб-палички</p></div>
      <div class="snack-item"><div class="snack-icon">🦑</div><h4>Кальмар</h4><p>З кунжутом / перуанський сушений</p></div>
      <div class="snack-item"><div class="snack-icon">🧀</div><h4>Інше</h4><p>Різні закуски під настрій</p></div>
    </div>
  </section>

  <section class="reviews" id="reviews">
    <div class="section-header">
      <div class="eyebrow">Що кажуть гості</div>
      <h2>Відгуки та вибір клієнтів</h2>
      <p>На основі Google Maps, Untappd та інших джерел</p>
    </div>
    <div class="reviews-grid">
      <div class="review-card">
        <div class="review-stars">★★★★★</div>
        <p class="review-text">Найкраще пиво в Познані. Файний вибір і смачні перекуси. Пан з обслуги мега привітний.</p>
        <div class="review-author"><strong>Dominik</strong> · Google</div>
      </div>
      <div class="review-card">
        <div class="review-stars">★★★★★</div>
        <p class="review-text">Паб з кранами і крафтовим пивом. Мало таких місць у Познані, де можна випити добре пиво з крана!</p>
        <div class="review-author"><strong>Krzysztof K.</strong> · Google</div>
      </div>
      <div class="review-card">
        <div class="review-stars">★★★★★</div>
        <p class="review-text">Найкраще крафтове пиво в Познані!</p>
        <div class="review-author"><strong>Dima K.</strong> · Google</div>
      </div>
      <div class="review-card">
        <div class="review-stars">★★★★★</div>
        <p class="review-text">Живе, свіже, нефільтроване. Відчувається, що вариться з душею. Porter і Jasne — must try.</p>
        <div class="review-author"><strong>Гості</strong> · Untappd / відгуки</div>
      </div>
    </div>
    <div class="analysis-box">
      <h3>Аналіз вибору клієнтів</h3>
      <ul>
        <li><strong>Jasne</strong> — найпопулярніше «щоденне» пиво</li>
        <li><strong>Porter</strong> — часто хвалять за глибину і м’якість</li>
        <li><strong>Pszeniczne</strong> — люблять за свіжість і бананові ноти</li>
        <li><strong>IPA / Wileńska</strong> — для любителів хмелю</li>
        <li><strong>Imbir z Miodem</strong> — цікавий авторський вибір</li>
        <li>Цінують: свіжість, обслугу, ціни, атмосферу</li>
        <li>Часто повертаються саме за «живим» пивом з крана</li>
        <li>Багато хто бере на винос / додому</li>
      </ul>
    </div>
  </section>

  <section class="location" id="location">
    <div class="section-header">
      <div class="eyebrow">Контакти</div>
      <h2>Де нас знайти</h2>
    </div>
    <div class="location-grid">
      <div class="location-info">
        <h3>Castacraftowe</h3>
        <div class="info-row">
          <div class="info-icon">📍</div>
          <div class="info-text"><strong>Адреса</strong><span>Półwiejska 6, 61-887 Poznań<br>Stare Miasto</span></div>
        </div>
        <div class="info-row">
          <div class="info-icon">📞</div>
          <div class="info-text"><strong>Телефон</strong><a href="tel:+48797356568">+48 797 356 568</a></div>
        </div>
        <div class="info-row">
          <div class="info-icon">🍺</div>
          <div class="info-text"><strong>Броварня</strong><span>ul. Krasickiego 19-21, 62-050 Mosina<br>(~15 км від Познані)</span></div>
        </div>
        <div class="info-row">
          <div class="info-icon">🌐</div>
          <div class="info-text"><strong>Соцмережі</strong><a href="https://www.instagram.com/castacraftowe/" target="_blank" rel="noopener">Instagram @castacraftowe</a></div>
        </div>
        <div style="margin-top: 2rem;">
          <a href="https://www.google.com/maps/search/?api=1&query=Castacraftowe+Półwiejska+6+Poznań" target="_blank" rel="noopener" class="btn btn-primary">Відкрити в Google Maps</a>
        </div>
      </div>
      <div class="map-container">
        <iframe src="https://maps.google.com/maps?q=Castacraftowe%20P%C3%B3%C5%82wiejska%206%20Pozna%C5%84&t=&z=16&ie=UTF8&iwloc=&output=embed" allowfullscreen loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
      </div>
    </div>
  </section>

  <section class="cta">
    <h2>Заходь на свіже пиво</h2>
    <p>Живе крафтове з українською душею чекає на Półwiejska 6. До зустрічі в Castacraftowe!</p>
    <a href="tel:+48797356568" class="btn btn-primary">Зателефонувати</a>
  </section>

  <footer>
    <div class="footer-inner">
      <div class="footer-logo">CASTACRAFTOWE</div>
      <div class="footer-links">
        <a href="#about">Про нас</a>
        <a href="#beers">Пиво</a>
        <a href="#reviews">Відгуки</a>
        <a href="#location">Контакти</a>
        <a href="https://www.instagram.com/castacraftowe/" target="_blank" rel="noopener">Instagram</a>
      </div>
    </div>
    <div class="footer-copy">© 2024–2026 Castacraftowe · Polska-Live Sp. z o.o. · Пиво з характером</div>
  </footer>

  <script>
    const nav = document.getElementById('nav');
    window.addEventListener('scroll', () => {
      nav.classList.toggle('scrolled', window.scrollY > 40);
    });
    const burger = document.getElementById('burger');
    const navLinks = document.getElementById('navLinks');
    burger.addEventListener('click', () => navLinks.classList.toggle('open'));
    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => navLinks.classList.remove('open'));
    });
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(BASE_DIR, filename)

if __name__ == "__main__":
    # Переконайся, що beer-label.webp лежить поруч з app.py
    print("Запуск сервера: http://127.0.0.1:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
