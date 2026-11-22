"use strict";

// Project-wide JavaScript for CyberQuest.

// Day 4: replace <i data-lucide="..."> placeholders with Lucide SVG icons.
// If the optional icon CDN is unavailable, labels and layout still work.
document.addEventListener("DOMContentLoaded", function () {
  if (window.lucide && typeof window.lucide.createIcons === "function") {
    window.lucide.createIcons();
  }
});
