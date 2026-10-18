# OpenCode Handoff — GitHub Push Remaining Commits

> **Written by:** Antigravity (2026-10-18)  
> **For:** OpenCode to pick up and complete the GitHub push autonomously

---

## Situation

| Item | Value |
|---|---|
| Repo CWD | `C:\Users\ptmth\Desktop\main project\mossev2` |
| Origin (target) | `https://github.com/Thairux/mossev2` (public) |
| Upstream (DO NOT PUSH) | `https://github.com/NousResearch/hermes-agent` |
| Local commits | **51,338** |
| GitHub currently has | **~5,000** (stuck since last night) |
| GitHub tip SHA | `2d59afd3da04812583ecbbf3be83539678a947c4` |
| Local HEAD SHA | `d6deae3afad8da00b276109b7028e8f31c6e82be` |
| Git config | `http.postBuffer=1GB`, `http.version=HTTP/1.1` ✅ already set |

---

## Checkpoint SHAs (push in this exact order)

| Chunk | Commit # | SHA |
|-------|----------|-----|
| 2 | 15,000 | `cb79518d4fbe1fc918f6833c3f955442dd57490f` |
| 3 | 25,000 | `b0af119963e36e045195c12a1f0c6552c85da468` |
| 4 | 35,000 | `3f521a02e9c9439d44364fc831a343ef3860259c` |
| 5 | 45,000 | `9903539c2f406cf0ea904af6e170abd97ae65b1f` |
| Final | 51,338 (HEAD) | `d6deae3afad8da00b276109b7028e8f31c6e82be` |

---

## Commands (PowerShell — use semicolons, not &&)

```powershell
# Get auth token once
$token = (gh auth token).Trim()

# Chunk 2 — commits 5001 to 15000
git push "https://Thairux:${token}@github.com/Thairux/mossev2.git" "cb79518d4fbe1fc918f6833c3f955442dd57490f:refs/heads/main"

# Chunk 3 — commits 15001 to 25000
git push "https://Thairux:${token}@github.com/Thairux/mossev2.git" "b0af119963e36e045195c12a1f0c6552c85da468:refs/heads/main"

# Chunk 4 — commits 25001 to 35000
git push "https://Thairux:${token}@github.com/Thairux/mossev2.git" "3f521a02e9c9439d44364fc831a343ef3860259c:refs/heads/main"

# Chunk 5 — commits 35001 to 45000
git push "https://Thairux:${token}@github.com/Thairux/mossev2.git" "9903539c2f406cf0ea904af6e170abd97ae65b1f:refs/heads/main"

# Final — commits 45001 to 51338 (HEAD)
git push origin main
```

---

## Verification (run after all 5 steps)

```powershell
gh api repos/Thairux/mossev2 --jq '.pushed_at,.size'
gh api "repos/Thairux/mossev2/commits?per_page=1" --jq '.[0].sha'
```

**Expected tip SHA:** `d6deae3afad8da00b276109b7028e8f31c6e82be`  
**Expected last commit message:** `feat(specs): enforce UI theme cohesion invariant across Kanban and BYO-Supabase cloud sync`

---

## After Success

1. `tkc_sync(force=true)` — push final state to Supabase
2. Post completion status to TKC board
3. Delete or archive this file (optional)

---

## Notes

- Each chunk takes **~10–20 min** depending on GitHub throughput
- **HTTP 408** = don't panic, retry the same SHA — git resumes from where it left off, does NOT restart from zero
- Run chunks **sequentially** — confirm exit code `0` before advancing to the next
- **Never push to `upstream`** (NousResearch/hermes-agent)
- Shell is **PowerShell** — `&&` is not valid, use `;` or separate lines
