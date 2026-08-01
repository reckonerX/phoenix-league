async function loadManagers() {
  const res = await fetch('data/managers.json');
  return res.json();
}
async function loadSeasons() {
  const res = await fetch('data/seasons.json');
  return res.json();
}
function pct(n) { return (n * 100).toFixed(1) + '%'; }
function ordinal(n) {
  if (n === null || n === undefined) return '—';
  const s = ['th', 'st', 'nd', 'rd'];
  const v = n % 100;
  return n + (s[(v - 20) % 10] || s[v] || s[0]);
}
function avatarHTML(m) {
  return m.photo
    ? `<img class="avatar" src="assets/photos/${m.photo}" alt="${m.display_name}">`
    : `<div class="avatar-placeholder">${m.display_name.charAt(0)}</div>`;
}
