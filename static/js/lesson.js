"use strict";

// CyberQuest lesson classroom interactions.
// Narration uses the browser's local Web Speech API only. Knowledge checks post
// to the same Django origin with a CSRF token. Nothing is stored in the browser.

(function () {
  const shell = document.querySelector(".cq-classroom-shell");
  if (!shell) {
    return;
  }

  const tutor = document.getElementById("cq-questmate");
  let moodTimer = null;

  function setMood(mood, duration) {
    if (!tutor) {
      return;
    }
    if (moodTimer) {
      window.clearTimeout(moodTimer);
      moodTimer = null;
    }
    tutor.dataset.mood = mood;
    if (duration) {
      moodTimer = window.setTimeout(function () {
        tutor.dataset.mood = "idle";
        moodTimer = null;
      }, duration);
    }
  }

  function setButton(button, disabled) {
    if (button) {
      button.disabled = disabled;
    }
  }

  function initVideo() {
    const video = document.getElementById("cq-lesson-video");
    const status = document.getElementById("cq-video-status");
    const error = document.getElementById("cq-video-error");
    const speed = document.getElementById("cq-video-speed");
    const fullscreen = document.getElementById("cq-fullscreen-button");
    if (!video) {
      return;
    }

    function showLoading() {
      if (status) {
        status.hidden = false;
      }
      if (error) {
        error.hidden = true;
      }
    }

    function hideLoading() {
      if (status) {
        status.hidden = true;
      }
    }

    function showError() {
      hideLoading();
      if (error) {
        error.hidden = false;
      }
      setMood("encouraging", 2200);
    }

    video.addEventListener("waiting", showLoading);
    video.addEventListener("canplay", hideLoading);
    video.addEventListener("playing", hideLoading);
    video.addEventListener("error", showError);
    if (video.readyState >= 2) {
      hideLoading();
    }

    if (speed) {
      speed.addEventListener("change", function () {
        video.playbackRate = Number(speed.value) || 1;
      });
    }

    if (fullscreen) {
      fullscreen.addEventListener("click", function () {
        if (typeof video.requestFullscreen === "function") {
          video.requestFullscreen();
        } else if (typeof video.webkitRequestFullscreen === "function") {
          video.webkitRequestFullscreen();
        }
      });
    }
  }

  function initNarration() {
    const source = document.getElementById("cq-narration-source");
    const status = document.getElementById("cq-narration-status");
    const captionBox = document.getElementById("cq-caption-box");
    const play = document.getElementById("cq-narration-play");
    const pause = document.getElementById("cq-narration-pause");
    const resume = document.getElementById("cq-narration-resume");
    const stop = document.getElementById("cq-narration-stop");
    const speed = document.getElementById("cq-narration-speed");
    const speedValue = document.getElementById("cq-speed-value");
    const voiceSelect = document.getElementById("cq-voice-select");

    const supported =
      "speechSynthesis" in window && "SpeechSynthesisUtterance" in window;
    if (!supported || !source || !source.textContent.trim()) {
      if (!supported) {
        if (status) {
          status.textContent =
            "Narration is not supported in this browser. Use the transcript below.";
        }
        [play, pause, resume, stop].forEach(function (button) {
          setButton(button, true);
        });
      } else if (status) {
        status.textContent =
          "No narration script is assigned to this lesson yet. Use the transcript below.";
      }
      return;
    }

    const text = source.textContent.trim();
    const sentences = text.match(/[^.!?]+[.!?]+|[^.!?]+$/g) || [text];
    let ranges = [];
    let cursor = 0;

    if (captionBox) {
      captionBox.textContent = "";
      sentences.forEach(function (sentence) {
        const span = document.createElement("span");
        span.className = "cq-caption-sentence";
        span.textContent = sentence.trim();
        captionBox.appendChild(span);
        ranges.push({ start: cursor, end: cursor + sentence.length });
        cursor += sentence.length;
      });
    }
    const sentenceNodes = captionBox
      ? Array.from(captionBox.querySelectorAll(".cq-caption-sentence"))
      : [];

    function highlight(index) {
      sentenceNodes.forEach(function (node, nodeIndex) {
        node.classList.toggle("is-active", nodeIndex === index);
      });
    }

    function controlsState(state) {
      setButton(play, state === "playing" || state === "paused");
      setButton(pause, state !== "playing");
      setButton(resume, state !== "paused");
      setButton(stop, state === "idle");
    }

    function selectedVoice() {
      if (!voiceSelect || !voiceSelect.value) {
        return null;
      }
      const voices = window.speechSynthesis.getVoices();
      return voices.find(function (voice) {
        return voice.voiceURI === voiceSelect.value;
      }) || null;
    }

    function loadVoices() {
      if (!voiceSelect) {
        return;
      }
      const voices = window.speechSynthesis
        .getVoices()
        .filter(function (voice) {
          return voice.lang.toLowerCase().startsWith("en");
        });
      if (!voices.length) {
        return;
      }
      voiceSelect.textContent = "";
      const fallback = document.createElement("option");
      fallback.value = "";
      fallback.textContent = "Browser default";
      voiceSelect.appendChild(fallback);
      voices.forEach(function (voice) {
        const option = document.createElement("option");
        option.value = voice.voiceURI;
        option.textContent = voice.name;
        voiceSelect.appendChild(option);
      });
    }

    loadVoices();
    if ("onvoiceschanged" in window.speechSynthesis) {
      window.speechSynthesis.addEventListener("voiceschanged", loadVoices);
    }

    controlsState("idle");

    function start() {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      const voice = selectedVoice();
      if (voice) {
        utterance.voice = voice;
      }
      utterance.lang = voice ? voice.lang : "en-US";
      utterance.rate = speed ? Number(speed.value) || 1 : 1;
      utterance.pitch = 1;

      utterance.onstart = function () {
        if (status) {
          status.textContent = "QuestMate is speaking…";
        }
        highlight(0);
        setMood("speaking");
        controlsState("playing");
      };
      utterance.onboundary = function (event) {
        if (typeof event.charIndex !== "number") {
          return;
        }
        const index = ranges.findIndex(function (range) {
          return event.charIndex >= range.start && event.charIndex < range.end;
        });
        if (index >= 0) {
          highlight(index);
        }
      };
      utterance.onend = function () {
        if (status) {
          status.textContent = "Narration finished. Replay it any time.";
        }
        highlight(-1);
        setMood("idle");
        controlsState("idle");
      };
      utterance.onerror = function () {
        if (status) {
          status.textContent =
            "Narration is unavailable right now. The full transcript is shown below.";
        }
        setMood("encouraging", 1800);
        controlsState("idle");
      };

      // Reflect the action immediately; onstart may be delayed or suppressed by
      // browsers that have no speech engine available.
      if (status) {
        status.textContent = "QuestMate is speaking…";
      }
      setMood("speaking");
      controlsState("playing");
      window.speechSynthesis.speak(utterance);
    }

    if (play) {
      play.addEventListener("click", start);
    }
    if (pause && typeof window.speechSynthesis.pause === "function") {
      pause.addEventListener("click", function () {
        window.speechSynthesis.pause();
        if (status) {
          status.textContent = "Narration paused.";
        }
        setMood("idle");
        controlsState("paused");
      });
    }
    if (resume && typeof window.speechSynthesis.resume === "function") {
      resume.addEventListener("click", function () {
        window.speechSynthesis.resume();
        if (status) {
          status.textContent = "QuestMate is speaking…";
        }
        setMood("speaking");
        controlsState("playing");
      });
    }
    if (stop) {
      stop.addEventListener("click", function () {
        window.speechSynthesis.cancel();
        if (status) {
          status.textContent = "Narration stopped.";
        }
        highlight(-1);
        setMood("idle");
        controlsState("idle");
      });
    }
    if (speed) {
      speed.addEventListener("input", function () {
        if (speedValue) {
          speedValue.textContent = Number(speed.value).toFixed(1) + "×";
        }
      });
    }

    window.addEventListener("pagehide", function () {
      window.speechSynthesis.cancel();
    });
  }

  function csrfToken() {
    const input = shell.querySelector('input[name="csrfmiddlewaretoken"]');
    return input ? input.value : "";
  }

  function updateProgress(data) {
    const percent = Math.max(0, Math.min(100, Number(data.progress_percent) || 0));
    const fill = document.getElementById("cq-progress-fill");
    const label = document.getElementById("cq-progress-percent");
    const track = document.getElementById("cq-progress-track");
    const note = document.getElementById("cq-progress-note");

    if (fill) {
      fill.style.width = percent + "%";
    }
    if (label) {
      label.textContent = percent + "%";
    }
    if (track) {
      track.setAttribute("aria-valuenow", String(percent));
    }
    if (note) {
      const answered = Number(data.questions_answered) || 0;
      const total = Number(data.questions_total) || 0;
      note.textContent = data.completed
        ? "Completed · progress saved to your account"
        : total
          ? "Progress saves automatically · " + answered + " of " + total + " questions answered"
          : "Progress saves automatically when you answer questions";
    }
  }

  function renderFeedback(container, data) {
    container.textContent = "";

    const heading = document.createElement("strong");
    heading.textContent = data.correct ? "Correct!" : "Good try — review this one.";
    container.appendChild(heading);

    if (!data.correct && data.correct_answer) {
      const answer = document.createElement("span");
      answer.textContent = "Correct answer: " + data.correct_answer;
      container.appendChild(answer);
    }

    if (data.explanation) {
      const explanation = document.createElement("p");
      explanation.textContent = data.explanation;
      container.appendChild(explanation);
    }

    container.classList.toggle("is-correct", Boolean(data.correct));
    container.classList.toggle("is-review", !data.correct);
    container.hidden = false;
  }

  function initQuiz() {
    const forms = Array.from(shell.querySelectorAll(".cq-question-form"));
    if (!forms.length) {
      return;
    }

    forms.forEach(function (form) {
      form.addEventListener("submit", async function (event) {
        event.preventDefault();
        const card = form.closest(".cq-question-card");
        const feedback = card ? card.querySelector(".cq-question-feedback") : null;
        const button = form.querySelector('button[type="submit"]');
        const originalText = button ? button.textContent.trim() : "";
        const formData = new FormData(form);

        if (!formData.get("choice")) {
          setMood("encouraging", 1600);
          if (feedback) {
            feedback.textContent = "Choose one answer first.";
            feedback.hidden = false;
          }
          return;
        }

        setMood("thinking");
        if (button) {
          button.disabled = true;
          button.textContent = "Checking…";
        }

        try {
          const response = await fetch(shell.dataset.answerUrl, {
            method: "POST",
            body: formData,
            headers: {
              "X-CSRFToken": csrfToken(),
            },
          });

          if (response.redirected) {
            if (feedback) {
              feedback.textContent = "Sign in to submit answers and save progress.";
              feedback.hidden = false;
            }
            setMood("encouraging", 2200);
            return;
          }

          const data = await response.json();
          if (!response.ok) {
            throw new Error(data.error || "That answer could not be checked.");
          }

          if (feedback) {
            renderFeedback(feedback, data);
          }
          updateProgress(data);
          setMood(data.correct ? "happy" : "encouraging", 2400);
        } catch (error) {
          setMood("encouraging", 2200);
          if (feedback) {
            feedback.textContent =
              error.message || "That answer could not be checked. Please try again.";
            feedback.hidden = false;
          }
        } finally {
          if (button) {
            button.disabled = false;
            button.textContent = originalText;
          }
        }
      });
    });
  }

  function initCompletion() {
    const button = document.getElementById("cq-complete-button");
    if (!button) {
      return;
    }

    button.addEventListener("click", async function () {
      setMood("thinking");
      button.disabled = true;
      try {
        const response = await fetch(shell.dataset.completeUrl, {
          method: "POST",
          headers: {
            "X-CSRFToken": csrfToken(),
          },
        });
        const data = await response.json();
        if (!response.ok) {
          throw new Error("Completion could not be saved.");
        }
        updateProgress(data);
        setMood("happy", 2400);
        button.textContent = "Completed ✓";
      } catch (error) {
        setMood("encouraging", 2200);
        button.textContent = "Try again";
        button.disabled = false;
      }
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initVideo();
    initNarration();
    initQuiz();
    initCompletion();
  });
})();
