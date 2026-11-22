"use strict";

// CyberQuest challenge activities.
// These helpers are educational and local-only. They never transmit input,
// never persist it, and never contact external services.

(function () {
  function byId(id) {
    return document.getElementById(id);
  }

  function renderSuggestions(container, messages) {
    container.replaceChildren();
    const list = document.createElement("ul");
    list.className = "cq-suggestion-list-items";
    messages.forEach(function (message) {
      const item = document.createElement("li");
      item.textContent = message;
      list.appendChild(item);
    });
    container.appendChild(list);
  }

  function initPasswordLab() {
    const input = byId("cq-password-input");
    const toggle = byId("cq-password-toggle");
    const fill = byId("cq-strength-fill");
    const label = byId("cq-strength-label");
    const suggestions = byId("cq-password-suggestions");
    if (!input || !toggle || !fill || !label || !suggestions) {
      return;
    }

    const COMMON_PATTERNS = [
      "password", "passw0rd", "qwerty", "letmein", "welcome", "admin",
      "iloveyou", "abc123", "123456", "monkey", "dragon", "cyberquest",
    ];
    const SEQUENCES = ["123", "234", "345", "456", "567", "678", "789", "abc", "bcd", "cde"];

    function analyse(value) {
      const lower = value.toLowerCase();
      const common = COMMON_PATTERNS.some(function (pattern) {
        return lower.includes(pattern);
      });
      const year = /(19|20)\d{2}/.test(value);
      const repeat = /(.)\1{2,}/.test(value);
      const sequence = SEQUENCES.some(function (item) {
        return lower.includes(item);
      });
      const classes = [
        /[a-z]/.test(value),
        /[A-Z]/.test(value),
        /\d/.test(value),
        /[^A-Za-z0-9]/.test(value),
      ].filter(Boolean).length;

      let score = 0;
      if (value.length >= 16) {
        score += 3;
      } else if (value.length >= 12) {
        score += 2;
      } else if (value.length >= 8) {
        score += 1;
      }

      if (classes >= 3) {
        score += 2;
      } else if (classes === 2) {
        score += 1;
      }

      if (!common && !year) {
        score += 1;
      } else {
        score -= 2;
      }

      if (!repeat && !sequence) {
        score += 1;
      } else {
        score -= 1;
      }

      score = Math.max(0, Math.min(8, score));

      let category = "Very Weak";
      let level = "very-weak";
      if (score >= 7) {
        category = "Strong";
        level = "strong";
      } else if (score >= 5) {
        category = "Moderate";
        level = "moderate";
      } else if (score >= 2) {
        category = "Weak";
        level = "weak";
      }

      const criteria = {
        length: value.length >= 12,
        variety: classes >= 3,
        patterns: !common && !year,
        repeats: !repeat && !sequence,
        unique: value.length >= 8 && !common && !year && !repeat && !sequence,
      };

      const tips = [];
      if (value.length < 12) {
        tips.push("Use a longer password — 12 or more characters is a better starting point.");
      }
      if (classes < 3) {
        tips.push("Mix character types where the service allows it, such as cases, numbers and symbols.");
      }
      if (common) {
        tips.push("Avoid common words and patterns such as password, qwerty or 123456.");
      }
      if (year) {
        tips.push("Avoid personal information such as birth years.");
      }
      if (repeat) {
        tips.push("Avoid repeated characters such as aaa.");
      }
      if (sequence) {
        tips.push("Avoid predictable sequences such as 123 or abc.");
      }
      if (criteria.unique) {
        tips.push("This sample looks varied. Remember to keep it unique to one account.");
      } else {
        tips.push("Use a unique password for each account.");
      }
      tips.push("Use a password manager to generate and remember strong unique passwords.");

      return { category: category, level: level, score: score, criteria: criteria, tips: tips };
    }

    function update() {
      const value = input.value;
      if (!value) {
        fill.className = "cq-strength-fill";
        fill.style.width = "0%";
        label.textContent = "Waiting for input";
        renderSuggestions(suggestions, ["Start typing a fictional example to see suggestions."]);
        document.querySelectorAll("[data-criterion]").forEach(function (item) {
          item.classList.remove("is-met");
        });
        return;
      }

      const result = analyse(value);
      fill.className = "cq-strength-fill level-" + result.level;
      fill.style.width = Math.max(8, result.score * 12.5) + "%";
      label.textContent = result.category;

      Object.keys(result.criteria).forEach(function (key) {
        document.querySelectorAll('[data-criterion="' + key + '"]').forEach(function (item) {
          item.classList.toggle("is-met", result.criteria[key]);
        });
      });

      renderSuggestions(suggestions, result.tips);
    }

    input.addEventListener("input", update);
    toggle.addEventListener("click", function () {
      const revealing = input.type === "password";
      input.type = revealing ? "text" : "password";
      toggle.textContent = revealing ? "Hide" : "Show";
      toggle.setAttribute("aria-pressed", String(revealing));
    });
    window.addEventListener("pagehide", function () {
      input.value = "";
    });
    update();
  }

  function initPassphraseBuilder() {
    const output = byId("cq-passphrase-output");
    const count = byId("cq-passphrase-count");
    const generate = byId("cq-passphrase-generate");
    const copy = byId("cq-passphrase-copy");
    if (!output || !count || !generate || !copy) {
      return;
    }

    const WORDS = [
      "amber", "badge", "canyon", "delta", "ember", "forest", "gadget", "harbor",
      "island", "jungle", "kite", "lantern", "meadow", "nebula", "ocean", "puzzle",
      "quartz", "river", "summit", "tunnel", "umber", "violet", "willow", "xenon",
      "yonder", "zebra", "compass", "drift", "falcon", "glacier",
    ];
    let current = "";

    function randomIndex(max) {
      if (window.crypto && window.crypto.getRandomValues) {
        const values = new Uint32Array(1);
        window.crypto.getRandomValues(values);
        return values[0] % max;
      }
      return Math.floor(Math.random() * max);
    }

    function build() {
      const words = [];
      for (let index = 0; index < 4; index += 1) {
        words.push(WORDS[randomIndex(WORDS.length)]);
      }
      current = words.join("-");
      output.textContent = current;
      count.textContent = "4 words";
      copy.textContent = "Copy sample";
    }

    generate.addEventListener("click", build);
    copy.addEventListener("click", function () {
      if (!current) {
        copy.textContent = "Generate first";
        return;
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(current).then(
          function () {
            copy.textContent = "Copied";
          },
          function () {
            copy.textContent = "Copy unavailable";
          }
        );
      } else {
        copy.textContent = "Copy unavailable";
      }
    });
    window.addEventListener("pagehide", function () {
      current = "";
      output.textContent = "Sample cleared.";
      count.textContent = "0 words";
    });
  }

  function initProfileInvestigator() {
    const investigate = byId("cq-investigate-profile");
    const panel = byId("cq-profile-risk-panel");
    const detail = byId("cq-profile-clue-detail");
    if (!investigate || !panel || !detail) {
      return;
    }

    document.querySelectorAll("[data-profile-clue]").forEach(function (button) {
      button.addEventListener("click", function () {
        detail.textContent = button.dataset.profileClue;
        button.classList.add("is-inspected");
      });
    });

    investigate.addEventListener("click", function () {
      panel.classList.add("is-visible");
      investigate.textContent = "Investigation complete";
      investigate.disabled = true;
    });
  }

  function initPrivacySettings() {
    const review = byId("cq-settings-review");
    const feedback = byId("cq-settings-feedback");
    if (!review || !feedback) {
      return;
    }

    function valueOf(id) {
      const element = byId(id);
      return element ? element.value : "";
    }

    review.addEventListener("click", function () {
      const messages = [];
      if (valueOf("cq-setting-visibility") === "public") {
        messages.push("Limit profile visibility so strangers cannot browse everything by default.");
      }
      if (valueOf("cq-setting-location") === "enabled") {
        messages.push("Disable location sharing unless a feature genuinely needs it.");
      }
      if (valueOf("cq-setting-followers") === "anyone") {
        messages.push("Approve followers so you control who can see future posts.");
      }
      if (valueOf("cq-setting-posts") === "public") {
        messages.push("Choose friends or private for personal posts.");
      }
      if (valueOf("cq-setting-apps") === "allow") {
        messages.push("Deny unnecessary app permissions and review allowed apps regularly.");
      }
      if (valueOf("cq-setting-data") === "allowed") {
        messages.push("Limit partner data sharing where the platform offers that choice.");
      }

      feedback.replaceChildren();
      const heading = document.createElement("p");
      heading.className = "fw-bold";
      heading.textContent = "Simulated privacy review";
      feedback.appendChild(heading);

      const list = document.createElement("ul");
      if (messages.length === 0) {
        const item = document.createElement("li");
        item.textContent = "Strong simulated setup. Keep checking settings after platform updates.";
        list.appendChild(item);
      } else {
        messages.forEach(function (message) {
          const item = document.createElement("li");
          item.textContent = message;
          list.appendChild(item);
        });
      }
      feedback.appendChild(list);

      const note = document.createElement("p");
      note.className = "cq-section-note mb-0";
      note.textContent = "Limiting visibility, location sharing and app permissions reduces unnecessary exposure. Privacy settings change, so review them regularly.";
      feedback.appendChild(note);
    });
  }

  function initNetworkDiagram() {
    const explanation = byId("cq-network-explanation");
    if (!explanation) {
      return;
    }
    document.querySelectorAll("[data-network-part]").forEach(function (button) {
      button.addEventListener("click", function () {
        explanation.textContent = button.dataset.explanation;
        document.querySelectorAll("[data-network-part]").forEach(function (item) {
          item.classList.remove("is-active");
        });
        button.classList.add("is-active");
      });
    });
  }

  function initWifiInvestigator() {
    const explanation = byId("cq-wifi-explanation");
    if (!explanation) {
      return;
    }
    document.querySelectorAll("[data-wifi]").forEach(function (button) {
      button.addEventListener("click", function () {
        explanation.textContent = button.dataset.explanation;
        document.querySelectorAll("[data-wifi]").forEach(function (item) {
          item.classList.remove("is-active");
        });
        button.classList.add("is-active");
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initPasswordLab();
    initPassphraseBuilder();
    initProfileInvestigator();
    initPrivacySettings();
    initNetworkDiagram();
    initWifiInvestigator();
  });
})();
