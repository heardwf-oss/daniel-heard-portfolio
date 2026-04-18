/* project.js — PDF viewer + lightbox */

/* ── Document viewer ────────────────────────────────────────────────────── */
const frames = Array.from(document.querySelectorAll(".document-frame"));

frames.forEach((frame) => {
  const documents = JSON.parse(frame.dataset.documents ?? "[]");
  if (!documents.length) return;

  const tabsRoot   = frame.querySelector('[data-role="tabs"]');
  const metaRoot   = frame.querySelector('[data-role="meta"]');
  const iframe     = frame.querySelector('[data-role="iframe"]');
  const openLink   = frame.querySelector('[data-role="open-link"]');
  const relatedBtns = Array.from(document.querySelectorAll("[data-view-document]"));
  let activeIndex  = 0;
  let loaded       = false;

  const update = (index) => {
    const doc = documents[index];
    if (!doc || !iframe || !openLink) return;

    activeIndex = index;

    // Show a brief loading state on the iframe
    iframe.style.opacity = "0.4";
    iframe.style.transition = "opacity 200ms";

    iframe.src = doc.url + "#view=FitH";
    openLink.href = doc.open_url;
    openLink.textContent = `Open ${doc.label}`;

    iframe.onload = () => {
      iframe.style.opacity = "1";
    };

    if (metaRoot) {
      metaRoot.innerHTML =
        `<strong>${doc.label}</strong> &mdash; ${doc.file_name} &mdash; ${doc.page_count} pages`;
    }

    tabsRoot?.querySelectorAll("button").forEach((btn, i) => {
      btn.classList.toggle("is-active", i === activeIndex);
      btn.setAttribute("aria-selected", i === activeIndex ? "true" : "false");
    });
  };

  // Build tabs
  if (tabsRoot) {
    tabsRoot.innerHTML = "";
    documents.forEach((doc, i) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "document-frame__tab";
      btn.textContent = doc.label;
      btn.setAttribute("role", "tab");
      btn.setAttribute("aria-selected", i === 0 ? "true" : "false");
      btn.addEventListener("click", () => update(i));
      tabsRoot.append(btn);
    });
  }

  // "View below" buttons on document cards
  relatedBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const idx = Number(btn.dataset.viewDocument ?? "0");
      update(idx);
      // Smooth scroll to viewer with a small offset
      setTimeout(() => {
        frame.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 80);
    });
  });

  update(0);
});

/* ── Lightbox ────────────────────────────────────────────────────────────── */
const previewLinks = Array.from(document.querySelectorAll("[data-lightbox]"));

if (previewLinks.length) {
  const overlay = document.createElement("div");
  overlay.className = "lightbox";
  overlay.hidden = true;
  overlay.setAttribute("role", "dialog");
  overlay.setAttribute("aria-modal", "true");
  overlay.setAttribute("aria-label", "Preview image");
  overlay.innerHTML = `
    <button class="lightbox__close" type="button" aria-label="Close preview">Close &times;</button>
    <figure class="lightbox__figure">
      <img class="lightbox__image" alt="">
      <figcaption class="lightbox__caption"></figcaption>
    </figure>
  `;

  document.body.append(overlay);

  const closeBtn = overlay.querySelector(".lightbox__close");
  const image    = overlay.querySelector(".lightbox__image");
  const caption  = overlay.querySelector(".lightbox__caption");

  const openLightbox = (src, alt, cap) => {
    if (!image || !caption) return;
    image.src = src;
    image.alt = alt;
    caption.textContent = cap;
    overlay.hidden = false;
    document.body.classList.add("is-lightbox-open");
    closeBtn?.focus();
  };

  const closeLightbox = () => {
    overlay.hidden = true;
    document.body.classList.remove("is-lightbox-open");
    if (image) image.src = "";
  };

  previewLinks.forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      openLightbox(
        link.href,
        link.dataset.caption ?? link.textContent ?? "Preview",
        link.dataset.caption ?? ""
      );
    });
  });

  closeBtn?.addEventListener("click", closeLightbox);
  overlay.addEventListener("click", (e) => { if (e.target === overlay) closeLightbox(); });

  // Keyboard: Escape to close, arrow keys to navigate
  const allGroupLinks = (link) => {
    const group = link.dataset.lightbox;
    return group
      ? Array.from(document.querySelectorAll(`[data-lightbox="${group}"]`))
      : [link];
  };

  let currentLink = null;

  previewLinks.forEach((link) => {
    link.addEventListener("click", () => { currentLink = link; });
  });

  window.addEventListener("keydown", (e) => {
    if (overlay.hidden) return;
    if (e.key === "Escape") { closeLightbox(); return; }

    if ((e.key === "ArrowRight" || e.key === "ArrowLeft") && currentLink) {
      const group = allGroupLinks(currentLink);
      const idx   = group.indexOf(currentLink);
      const next  = e.key === "ArrowRight"
        ? group[(idx + 1) % group.length]
        : group[(idx - 1 + group.length) % group.length];
      if (next) {
        currentLink = next;
        openLightbox(
          next.href,
          next.dataset.caption ?? "",
          next.dataset.caption ?? ""
        );
      }
    }
  });
}
