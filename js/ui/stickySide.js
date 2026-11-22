/**
 * Keeps the laptop-layout form column (.app__side, position: sticky) usable at any window height.
 * Fits the window -> sticks under the header. Taller than the window -> --side-top goes negative,
 * so the column scrolls with the page until its bottom is visible, then sticks there.
 */
export function initStickySide(side = document.querySelector('.app__side')) {
  if (!side || typeof ResizeObserver === 'undefined') return;
  const root = document.documentElement;
  const header = document.querySelector('.site-header');

  const update = () => {
    const headerH = header?.offsetHeight ?? 0;
    const top = Math.min(headerH, window.innerHeight - side.offsetHeight);
    root.style.setProperty('--side-top', `${top}px`);
  };

  new ResizeObserver(update).observe(side);
  window.addEventListener('resize', update, { passive: true });
  update();
}
