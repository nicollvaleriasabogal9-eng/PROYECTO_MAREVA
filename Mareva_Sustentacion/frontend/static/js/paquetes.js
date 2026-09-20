document.addEventListener("DOMContentLoaded", () => {
  const range = document.getElementById("precioRange");
  const value = document.getElementById("precioValor");
  const checks = [...document.querySelectorAll(".compare-select")];
  const bar = document.getElementById("compareBar");
  const count = document.getElementById("compareCount");
  const link = document.getElementById("compareLink");


  const updateCompare = () => {
    const selected = checks.filter(c => c.checked).map(c => c.value);
    checks.forEach(c => { if (!c.checked) c.disabled = selected.length >= 3; });
    if (bar) bar.hidden = selected.length === 0;
    if (count) count.textContent = `${selected.length}`;
    if (link) link.href = selected.length ? `/comparar?${selected.map(id => `id=${encodeURIComponent(id)}`).join("&")}` : "/comparar";
  };
  checks.forEach(c => c.addEventListener("change", updateCompare));
  updateCompare();
});
