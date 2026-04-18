const chips = Array.from(document.querySelectorAll(".filter-chip"));
const cards = Array.from(document.querySelectorAll(".project-card"));

if (chips.length && cards.length) {
  chips.forEach((chip) => {
    chip.addEventListener("click", () => {
      const filter = chip.dataset.filter ?? "all";

      chips.forEach((item) => item.classList.toggle("is-active", item === chip));

      cards.forEach((card) => {
        const tags = card.dataset.tags ?? "";
        const visible = filter === "all" || tags.includes(filter);
        card.classList.toggle("is-hidden", !visible);
      });
    });
  });
}
