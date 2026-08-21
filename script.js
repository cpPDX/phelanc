const navbar = document.getElementById('navbar');
const navToggle = document.getElementById('navToggle');
const navLinks = document.getElementById('navLinks');
const sections = document.querySelectorAll('main section[id]');

function setMenuOpen(isOpen) {
  if (!navToggle || !navLinks) return;

  navToggle.classList.toggle('open', isOpen);
  navLinks.classList.toggle('open', isOpen);
  navToggle.setAttribute('aria-expanded', String(isOpen));
  navToggle.setAttribute('aria-label', isOpen ? 'Close navigation menu' : 'Open navigation menu');
}

function highlightNavLink() {
  if (!sections.length) return;

  const scrollPosition = window.scrollY + 110;
  const isAtPageBottom = window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 4;
  let activeLink = null;

  sections.forEach((section, index) => {
    const link = document.querySelector(`.nav-links a[href="#${section.id}"]`);
    const isLastSection = index === sections.length - 1;
    const isActive = (isAtPageBottom && isLastSection)
      || (scrollPosition >= section.offsetTop
        && scrollPosition < section.offsetTop + section.offsetHeight);

    if (link && isActive) activeLink = link;
  });

  document.querySelectorAll('.nav-links a[href^="#"]').forEach((link) => {
    const isActive = link === activeLink;
    link.classList.toggle('active', isActive);
    if (isActive) {
      link.setAttribute('aria-current', 'location');
    } else {
      link.removeAttribute('aria-current');
    }
  });
}

function updateNavbar() {
  navbar?.classList.toggle('scrolled', window.scrollY > 20);
  highlightNavLink();
}

navToggle?.addEventListener('click', () => {
  setMenuOpen(navToggle.getAttribute('aria-expanded') !== 'true');
});

navLinks?.querySelectorAll('a').forEach((link) => {
  link.addEventListener('click', () => setMenuOpen(false));
});

document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') {
    setMenuOpen(false);
    navToggle?.focus();
  }
});

window.addEventListener('scroll', updateNavbar, { passive: true });
updateNavbar();

const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

document.querySelectorAll('.skills-grid, .edu-grid, .projects-grid, .contact-links, .about-highlights')
  .forEach((container) => {
    container.querySelectorAll('.reveal, .skill-pill, .highlight-card').forEach((child, index) => {
      child.classList.add('reveal');
      child.style.setProperty('--reveal-delay', `${index * 70}ms`);
    });
  });

if (prefersReducedMotion || !('IntersectionObserver' in window)) {
  document.querySelectorAll('.reveal').forEach((element) => element.classList.add('visible'));
} else {
  const revealObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;

      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    });
  }, {
    threshold: 0.1,
    rootMargin: '0px 0px -40px 0px',
  });

  document.querySelectorAll('.reveal').forEach((element) => revealObserver.observe(element));
}

window.clearTimeout(window.revealFallback);
