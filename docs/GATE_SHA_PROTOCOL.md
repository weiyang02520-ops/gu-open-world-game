# Gate SHA Protocol

Git commits are content addressed. A commit cannot contain its own final SHA:
writing the SHA into a file changes the tree and therefore changes the SHA.

For this repository:

- `CURRENT_STATE.last_codex_commit` means the final **code-bearing
  implementation commit** for the active task.
- The Gate/report commit may update `status`, `next_actor`, evidence and
  review metadata, but it must not pretend to self-record its own SHA.
- The final remote HEAD is verified externally with:

```powershell
$local = (git rev-parse HEAD).Trim()
$remote = (git ls-remote origin refs/heads/main).Split("`t")[0].Trim()
if ($local -ne $remote) { throw "SHA mismatch" }
```

- `CODEX_REPORT.md` records both the code-bearing implementation SHA and the
  final Gate HEAD observed by that verification command.
- The final response also reports the exact remote HEAD. No endless sequence
  of self-referential bookkeeping commits is created.

This is the repository's truthful replacement for the impossible invariant
“a commit contains its own SHA”.
