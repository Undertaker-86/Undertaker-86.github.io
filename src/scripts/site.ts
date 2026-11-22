/**
 * The site's only global client code (~2 KB gz): theme toggle, scroll reveals,
 * hover/in-view video loops and an image/video lightbox. Re-binds after every view transition.
 */
const reduced = () => matchMedia('(prefers-reduced-motion: reduce)').matches;
const canHover = () => matchMedia('(hover: hover) and (pointer: fine)').matches;

function themeToggle() {
  document.querySelectorAll<HTMLButtonElement>('[data-theme-toggle]').forEach((b) => {
    if (b.dataset.bound) return;
    b.dataset.bound = '1';
    b.addEventListener('click', () => {
      const next = document.documentElement.dataset.theme === 'light' ? 'dark' : 'light';
      document.documentElement.dataset.theme = next;
      try {
        localStorage.setItem('theme', next);
      } catch {
        /* storage unavailable: theme still switches for this page view */
      }
    });
  });
}

let revealIO: IntersectionObserver | undefined;
function reveals() {
  revealIO?.disconnect();
  const els = document.querySelectorAll<HTMLElement>('.reveal:not(.in)');
  if (reduced() || !('IntersectionObserver' in window)) {
    els.forEach((e) => e.classList.add('in'));
    return;
  }
  revealIO = new IntersectionObserver(
    (entries) =>
      entries.forEach((en) => {
        if (en.isIntersecting) {
          en.target.classList.add('in');
          revealIO!.unobserve(en.target);
        }
      }),
    { rootMargin: '0px 0px -8% 0px' },
  );
  els.forEach((e) => revealIO!.observe(e));
}

/**
 * Videos with [data-loop] never preload. They play on hover (pointer devices) or while
 * mostly in view (touch devices / [data-autoplay]); they pause off-screen. Reduced motion: never autoplay.
 */
let videoIO: IntersectionObserver | undefined;
function videos() {
  videoIO?.disconnect();
  const vids = [...document.querySelectorAll<HTMLVideoElement>('video[data-loop]')];
  const play = (v: HTMLVideoElement) => {
    v.play().catch(() => {});
  };
  const autoplayInView = (v: HTMLVideoElement) => !reduced() && (v.dataset.autoplay !== undefined || !canHover());
  videoIO = new IntersectionObserver(
    (entries) =>
      entries.forEach((en) => {
        const v = en.target as HTMLVideoElement;
        if (en.isIntersecting && en.intersectionRatio > 0.55 && autoplayInView(v)) play(v);
        else if (!en.isIntersecting || en.intersectionRatio < 0.3) v.pause();
      }),
    { threshold: [0, 0.3, 0.55, 0.9] },
  );
  for (const v of vids) {
    videoIO.observe(v);
    if (v.dataset.bound) continue;
    v.dataset.bound = '1';
    v.addEventListener('playing', () => (v.style.opacity = '1'), { once: true });
    const host = (v.closest('[data-hover-host]') as HTMLElement) ?? v;
    host.addEventListener('pointerenter', () => {
      if (canHover() && !reduced()) play(v);
    });
    host.addEventListener('pointerleave', () => {
      if (canHover() && v.dataset.autoplay === undefined) v.pause();
    });
    host.addEventListener('focusin', () => !reduced() && play(v));
    host.addEventListener('focusout', () => v.pause());
  }
}

/** Lightbox: any element with [data-zoom] opens its image (or its video) full-screen in a <dialog>. */
let dlg: HTMLDialogElement | undefined;
function lightbox() {
  if (!dlg) {
    dlg = document.createElement('dialog');
    dlg.className = 'lightbox';
    dlg.setAttribute('aria-label', 'Enlarged media');
    dlg.addEventListener('click', (e) => {
      if (e.target === dlg || (e.target as HTMLElement).closest('[data-close]')) dlg!.close();
    });
    dlg.addEventListener('close', () => {
      dlg!.querySelector('video')?.pause();
      dlg!.replaceChildren();
    });
  }
  if (!dlg.isConnected) document.body.append(dlg);
  document.querySelectorAll<HTMLElement>('[data-zoom]').forEach((el) => {
    if (el.dataset.bound) return;
    el.dataset.bound = '1';
    el.addEventListener('click', (ev) => {
      ev.preventDefault();
      const fig = el.closest('figure');
      const cap = fig?.querySelector('figcaption')?.textContent ?? '';
      const vid = el.querySelector('video');
      let media: HTMLElement;
      if (vid) {
        const v = vid.cloneNode(true) as HTMLVideoElement;
        v.removeAttribute('data-loop');
        v.removeAttribute('data-bound');
        v.removeAttribute('aria-hidden');
        v.removeAttribute('tabindex');
        v.className = '';
        v.style.opacity = '1';
        v.controls = true;
        v.muted = true;
        v.preload = 'auto';
        v.autoplay = !reduced();
        media = v;
      } else {
        const src = el.getAttribute('href') ?? el.querySelector('img')?.currentSrc ?? '';
        const img = document.createElement('img');
        img.src = src;
        img.alt = el.querySelector('img')?.alt ?? '';
        media = img;
      }
      const close = document.createElement('button');
      close.type = 'button';
      close.dataset.close = '';
      close.className = 'lightbox-close';
      close.setAttribute('aria-label', 'Close');
      close.textContent = '×';
      const p = document.createElement('p');
      p.textContent = cap;
      dlg!.replaceChildren(close, media, p);
      dlg!.showModal();
      close.focus();
    });
  });
}

function init() {
  themeToggle();
  reveals();
  videos();
  lightbox();
}
document.addEventListener('astro:page-load', init);
document.addEventListener('astro:before-swap', () => {
  document.querySelectorAll('video').forEach((v) => v.pause());
});
