async function loadManagers() {
  const res = await fetch('data/managers.json');
  return res.json();
}
async function loadSeasons() {
  const res = await fetch('data/seasons.json');
  return res.json();
}
function pct(n) { return (n * 100).toFixed(1) + '%'; }
