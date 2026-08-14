function makeSortable(table) {
  const thead = table.querySelector('thead');
  const tbody = table.querySelector('tbody');
  if (!thead || !tbody) return;

  const ths = Array.from(thead.querySelectorAll('th'));
  let currentCol = null;
  let currentDir = 1;

  function cellValue(row, colIndex) {
    const cell = row.children[colIndex];
    if (!cell) return '';
    if (cell.dataset.sort !== undefined) return cell.dataset.sort;
    return cell.textContent.trim();
  }

  function sortBy(colIndex) {
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const dir = (currentCol === colIndex) ? -currentDir : 1;
    currentCol = colIndex;
    currentDir = dir;

    rows.sort((a, b) => {
      const av = cellValue(a, colIndex);
      const bv = cellValue(b, colIndex);
      const an = parseFloat(av);
      const bn = parseFloat(bv);
      let cmp;
      if (!isNaN(an) && !isNaN(bn)) {
        cmp = an - bn;
      } else {
        cmp = av.localeCompare(bv);
      }
      return cmp * dir;
    });

    rows.forEach(r => tbody.appendChild(r));

    ths.forEach((th, i) => {
      th.classList.remove('sort-asc', 'sort-desc');
      if (i === colIndex) th.classList.add(dir === 1 ? 'sort-asc' : 'sort-desc');
    });
  }

  ths.forEach((th, i) => {
    th.classList.add('sortable');
    th.addEventListener('click', () => sortBy(i));
  });
}

function wireFilter(inputEl, items, getText) {
  inputEl.addEventListener('input', () => {
    const q = inputEl.value.trim().toLowerCase();
    items.forEach(item => {
      const match = getText(item).toLowerCase().includes(q);
      item.style.display = match ? '' : 'none';
    });
  });
}
