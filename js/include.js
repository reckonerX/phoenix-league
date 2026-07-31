async function includePartials() {
  const targets = document.querySelectorAll('[data-include]');
  await Promise.all(
    Array.from(targets).map(async (el) => {
      const file = el.getAttribute('data-include');
      const res = await fetch(file);
      el.innerHTML = await res.text();
    })
  );
  const current = document.body.getAttribute('data-page');
  if (current) {
    const link = document.querySelector(`nav a[data-nav="${current}"]`);
    if (link) link.setAttribute('aria-current', 'page');
  }
}
document.addEventListener('DOMContentLoaded', includePartials);
