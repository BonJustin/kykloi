/* admin/app.js - Kykloi Control Hub Client Engine */
"use strict";

document.addEventListener("DOMContentLoaded", () => {
  // =========================================================================
  // 1. DOM ELEMENT CACHE
  // =========================================================================
  const statusBadge = document.getElementById("app-status-badge");
  const statusText = document.getElementById("app-status-text");
  const consoleEl = document.getElementById("console-output");
  const runBuildBtn = document.getElementById("btn-run-build");
  const clearConsoleBtn = document.getElementById("btn-clear-console");
  const cleanCheckbox = document.getElementById("clean-build");
  const passwordInput = document.getElementById("build-passphrase");
  const openVaultBtn = document.getElementById("btn-open-vault");

  // =========================================================================
  // 2. STATE & UI HELPERS
  // =========================================================================
  function setStatus(state, message) {
    if (!statusBadge || !statusText) return;
    statusBadge.className = "status-badge";
    if (state === "busy") statusBadge.classList.add("busy");
    if (state === "error") statusBadge.classList.add("error");
    statusText.textContent = message;
  }

  function appendConsole(text) {
    if (!consoleEl) return;
    consoleEl.textContent += text;
    consoleEl.scrollTop = consoleEl.scrollHeight;
  }

  // =========================================================================
  // 3. TERMINAL CONSOLE ACTIONS
  // =========================================================================
  if (clearConsoleBtn && consoleEl) {
    clearConsoleBtn.addEventListener("click", () => {
      consoleEl.textContent = "";
    });
  }

  // =========================================================================
  // 4. COMPILATION IPC BRIDGE (POST /api/build)
  // =========================================================================
  if (runBuildBtn) {
    runBuildBtn.addEventListener("click", async () => {
      runBuildBtn.disabled = true;
      setStatus("busy", "Compiling Site...");
      appendConsole(`\n>>> [${new Date().toLocaleTimeString()}] Triggering build pipeline...\n`);

      const payload = {
        clean: cleanCheckbox ? cleanCheckbox.checked : false,
        password: passwordInput && passwordInput.value.trim() ? passwordInput.value.trim() : undefined,
        verbose: false,
      };

      try {
        const response = await fetch("/api/build", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });

        // 409: Server-side build lock active
        if (response.status === 409) {
          const errorText = await response.text();
          appendConsole(`\n[REJECTED] ${errorText}\n`);
          setStatus("busy", "Build Already Running");
          return;
        }

        if (!response.ok) {
          throw new Error(`HTTP ${response.status} from control daemon`);
        }

        // Process chunked stream in real time
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
  }

  // =========================================================================
  // 5. VAULT VIEWER ORCHESTRATION (POST /api/view)
  // =========================================================================
  if (openVaultBtn) {
    openVaultBtn.addEventListener("click", async () => {
      openVaultBtn.disabled = true;
      try {
        const res = await fetch("/api/view", { method: "POST" });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        appendConsole(`\n[Kykloi IPC] Static reader daemon confirmed active at ${data.url}\n`);
      } catch (err) {
        appendConsole(`\n[Kykloi IPC Error] Failed to launch vault viewer: ${err.message}\n`);
      } finally {
        openVaultBtn.disabled = false;
      }
    });
  }
});
