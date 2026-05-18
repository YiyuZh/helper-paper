# Wrapper Skills

This directory contains the two wrapper skills installed with `helper-paper`:

- `gpt-academic/`: wrapper for a local `binary-husky/gpt_academic` checkout. It is the primary full-paper translation backend.
- `chatpaper/`: wrapper for a local `kaixindelele/ChatPaper` checkout. It provides summary, contribution, method, limitation, and Q&A review material.

Running the repository root `install.ps1` copies these wrappers to:

```text
C:\Users\<your-user>\.codex\skills\
```

Notes:

- This directory does not include the upstream `gpt_academic` or `ChatPaper` source code.
- Users should clone upstream tools into the directory configured by `HELPER_PAPER_EXTERNAL_TOOLS_ROOT`, or into `%USERPROFILE%\helper-paper-external-tools` by default.
- Other companion skills are not installed by this repository.
- Full installation, API, update, and GitHub publishing instructions live in the root [README.md](../README.md).
