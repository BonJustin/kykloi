/* admin/app.js - Dashboard Client Logic & Streaming IPC */
"use strict";

document.addEventListener("DOMContentLoaded", () => {
  const statusBadge = document.getElementById("app-status-badge");
  const statusText = document.getElementById("app-status-text");
  const consoleEl = document.getElementById("console-output");
  const runBuildBtn = document.getElementById("btn-run-build");
  const clearConsoleBtn = document.getElementById("btn-clear-console");
  const cleanCheckbox = document.getElementById("clean-build");
  const passwordInput = document.getElementById("build-passphrase");

  function setStatus(state, message) {
    statusBadge.className = "status-badge";
    if (state === "busy") statusBadge.classList.add("busy");
    if (state === "error") statusBadge.classList.add("error");
    statusText.textContent = message;
  }

  function appendConsole(text) {
    consoleEl.textContent += text;
    consoleEl.scrollTop = consoleEl.scrollHeight;
  }

  clearConsoleBtn.addEventListener("click", () => {
    consoleEl.textContent = "";
  });

  runBuildBtn.addEventListener("click", async () => {
    runBuildBtn.disabled = true;
    setStatus("busy", "Compiling Site...");
    appendConsole(`\n>>> [${new Date().toLocaleTimeString()}] Build job started...\n`);

    const payload = {
      clean: cleanCheckbox.checked,
      password: passwordInput.value.trim() || undefined,
      verbose: false,
    };

    try {
      const response = await fetch("/api/build", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status} from control daemon`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        const textChunk = decoder.decode(value, { stream: true });
        appendConsole(textChunk);
      }

      setStatus("idle", "Build Complete");
    } catch (err) {
      appendConsole(`\n[FATAL IPC ERROR] ${err.message}\n`);
      setStatus("error", "Execution Failed");
    } finally {
      runBuildBtn.disabled = false;
    }
  });
});
