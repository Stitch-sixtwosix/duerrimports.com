(() => {
  const doc = document.documentElement;
  doc.classList.add('js');
  const yr = document.getElementById('yr');
  if (yr) yr.textContent = new Date().getFullYear();

  /* Staggered entrances: each section's parts rise in order, once. */
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const rise = [...document.querySelectorAll('[data-rise]')];
  document.querySelectorAll('section, footer').forEach(sec => {
    sec.querySelectorAll('[data-rise]').forEach((el, i) => el.style.setProperty('--i', Math.min(i, 8)));
  });
  if (reduce || !('IntersectionObserver' in window)) {
    rise.forEach(el => el.classList.add('in'));
  } else {
    const io = new IntersectionObserver(entries => {
      entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    rise.forEach(el => io.observe(el));
    // Safety net: never leave content hidden.
    setTimeout(() => { rise.forEach(el => el.classList.add('in')); doc.classList.add('rise-done'); }, 4000);
  }

  /* The bar takes the colour of the chapter beneath it. */
  const bar = document.getElementById('bar');
  const fields = [...document.querySelectorAll('[data-field]')].filter(el => el !== bar);
  const setBar = () => {
    const y = bar.offsetHeight + 1;
    let cur = fields[0];
    for (const f of fields) { if (f.getBoundingClientRect().top <= y) cur = f; }
    if (cur && bar.dataset.field !== cur.dataset.field) bar.dataset.field = cur.dataset.field;
  };
  addEventListener('scroll', setBar, { passive: true });
  setBar();

  /* The finder: pick a need, meet the company. Links still work without script. */
  const data = {
    proplexa: { field: 'bay', name: 'Proplexa', line: 'Property management solutions for owners and managers.', url: 'https://proplexa.ai/', label: 'Visit proplexa.ai',  },
    fastflip: { field: 'bay', name: 'FastFlip Realty', line: 'Sell your property quickly and simply.', url: 'https://fastflip.co/', label: 'Visit fastflip.co',  },
    medellin: { field: 'bay', name: 'Medellín Concierge', line: 'Rentals, real estate and property management in Medellín.', url: 'https://www.medellinconcierge.net/', label: 'Visit medellinconcierge.net',  },
    hostflow: { field: 'bay', name: 'HostFlow', line: 'Short-term rental management: revenue automation, owner portals, cleaner scheduling and compliance.', url: 'https://hostflow.in/', label: 'Visit hostflow.in',  },
    suero: { field: 'aqua', name: 'Suero Rapido', line: 'IV therapy to rehydrate and recover.', url: 'https://suerorapido.com/', label: 'Visit suerorapido.com',  },
    imports: { field: 'roast', name: 'Duerr Imports', line: 'Wholesale and white-label importing for cafés, offices and resellers.', url: '#imports', label: 'See imports',  }
  };
  const answer = document.getElementById('answer');
  const needs = [...document.querySelectorAll('.need')];
  needs.forEach(btn => {
    btn.setAttribute('role', 'button');
    btn.setAttribute('aria-pressed', 'false');
    btn.addEventListener('click', ev => {
      ev.preventDefault();
      const d = data[btn.dataset.co];
      if (!d) return;
      needs.forEach(n => n.setAttribute('aria-pressed', String(n === btn)));
      answer.dataset.field = d.field;
      document.getElementById('answer-name').textContent = d.name;
      document.getElementById('answer-line').textContent = d.line;
      const link = document.getElementById('answer-link');
      link.href = d.url; link.textContent = d.label;
      if (d.url.startsWith('http')) link.rel = 'noopener'; else link.removeAttribute('rel');
      answer.hidden = false;
      answer.classList.remove('pop'); void answer.offsetWidth; answer.classList.add('pop');
    });
  });

  /* Contact: compose a real email instead of a fake submit. */
  const form = document.getElementById('enquiry');
  form?.addEventListener('submit', ev => {
    ev.preventDefault();
    if (!form.reportValidity()) return;
    const f = new FormData(form);
    const subject = `Enquiry: ${f.get('about')}`;
    const body = `${f.get('message')}\n\n${f.get('name')}`;
    location.href = `mailto:contact@duerrimports.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
  });
})();
