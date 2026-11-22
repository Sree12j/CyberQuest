"use strict";

// CyberQuest homepage interactions.
// Everything on this page is local, unscored and fictional. No form data is
// collected, nothing is stored, and no network request is made by this file.

(function () {
  function prefersReducedMotion() {
    return window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }

  function initReveal() {
    const items = document.querySelectorAll("[data-reveal]");
    if (!items.length) {
      return;
    }

    document.body.classList.add("cq-home-js");

    if (prefersReducedMotion() || !("IntersectionObserver" in window)) {
      items.forEach(function (item) {
        item.classList.add("is-visible");
      });
      return;
    }

    function reveal(item) {
      item.classList.add("is-visible");
    }

    const observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            reveal(entry.target);
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1, rootMargin: "0px 0px -40px 0px" }
    );

    items.forEach(function (item) {
      // Reveal anything already on screen immediately. IntersectionObserver can
      // be delayed in background tabs, and no content should stay hidden.
      const bounds = item.getBoundingClientRect();
      if (bounds.top < window.innerHeight - 40 && bounds.bottom > 40) {
        reveal(item);
      } else {
        observer.observe(item);
      }
    });
  }

  function initHabitCheck() {
    const button = document.getElementById("cq-scan-button");
    const label = document.getElementById("cq-scan-button-label");
    const status = document.getElementById("cq-scan-status");
    const log = document.getElementById("cq-scan-log");
    if (!button || !label || !status || !log) {
      return;
    }

    const steps = [
      {
        status: "Reviewing password habits…",
        line: "Unique passwords and MFA make stolen credentials less useful.",
      },
      {
        status: "Reviewing sharing choices…",
        line: "Check the audience before you post a photo or personal detail.",
      },
      {
        status: "Reviewing network caution…",
        line: "Verify public Wi-Fi names and keep HTTPS enabled.",
      },
      {
        status: "Simulation complete",
        line: "Nice work. Explore a mission for guided practice.",
      },
    ];

    let index = -1;
    button.addEventListener("click", function () {
      index = (index + 1) % steps.length;
      status.textContent = steps[index].status;
      label.textContent = index === steps.length - 1 ? "Run Again" : "Next Check";

      const entry = document.createElement("li");
      entry.textContent = steps[index].line;
      log.prepend(entry);
      while (log.children.length > 3) {
        log.removeChild(log.lastElementChild);
      }
    });
  }

  function initQuickCheck() {
    const tabs = Array.from(document.querySelectorAll("[data-check-tab]"));
    const panels = Array.from(document.querySelectorAll("[data-check-panel]"));
    if (!tabs.length || !panels.length) {
      return;
    }

    function activate(key, moveFocus) {
      tabs.forEach(function (tab) {
        const isActive = tab.dataset.checkTab === key;
        tab.setAttribute("aria-selected", String(isActive));
        tab.tabIndex = isActive ? 0 : -1;
        if (isActive && moveFocus) {
          tab.focus();
        }
      });

      panels.forEach(function (panel) {
        panel.hidden = panel.dataset.checkPanel !== key;
      });
    }

    tabs.forEach(function (tab, position) {
      tab.addEventListener("click", function () {
        activate(tab.dataset.checkTab, false);
      });

      tab.addEventListener("keydown", function (event) {
        let next = null;
        if (event.key === "ArrowRight") {
          next = (position + 1) % tabs.length;
        } else if (event.key === "ArrowLeft") {
          next = (position - 1 + tabs.length) % tabs.length;
        }
        if (next !== null) {
          event.preventDefault();
          activate(tabs[next].dataset.checkTab, true);
        }
      });
    });

    document.querySelectorAll("[data-reveal-guidance]").forEach(function (button) {
      button.addEventListener("click", function () {
        const guidance = button.parentElement.querySelector(".cq-guidance");
        if (!guidance) {
          return;
        }
        const isRevealed = !guidance.hidden;
        guidance.hidden = isRevealed;
        button.textContent = isRevealed ? "Reveal guidance" : "Hide guidance";
      });
    });
  }

  function initTilt() {
    if (prefersReducedMotion() || !window.matchMedia || !window.matchMedia("(pointer: fine)").matches) {
      return;
    }

    document.querySelectorAll("[data-tilt]").forEach(function (card) {
      card.addEventListener("pointermove", function (event) {
        const rect = card.getBoundingClientRect();
        const x = (event.clientX - rect.left) / rect.width - 0.5;
        const y = (event.clientY - rect.top) / rect.height - 0.5;
        card.style.setProperty("--tilt-x", (-y * 4).toFixed(2) + "deg");
        card.style.setProperty("--tilt-y", (x * 4).toFixed(2) + "deg");
      });

      card.addEventListener("pointerleave", function () {
        card.style.setProperty("--tilt-x", "0deg");
        card.style.setProperty("--tilt-y", "0deg");
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initReveal();
    initHabitCheck();
    initQuickCheck();
    initTilt();
  });
})();
