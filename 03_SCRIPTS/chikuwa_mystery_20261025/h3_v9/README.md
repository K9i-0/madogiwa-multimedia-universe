# H3 inserts for chikuwa mystery v9

Five image-reference shots, R2V / 480p Turbo / 864×480 / 24fps / 8 steps.
`ch01`–`ch04`: 124 frames each. `ch05`: 175 frames. A100, single worker, official Colab CLI OAuth2. Generated audio is always muted in the edit.

- ch01: forest contraction, species explanation.
- ch02: natural specimen versus inert reproduction, experiment punchline.
- ch03: closed T-company gate, attempted visit.
- ch04: laboratory droplet, repeating normal test results.
- ch05: production line, post-credits truth reveal (no credits card).

`ch02.png` is the newly generated reference; the other inputs symlink adopted repository images. Exact generation prompts are `ch*_prompt.txt`, ComfyUI graphs are `ch*.json`. `chapter_plan.json` records input sources. The submitted ZIP SHA and compute balance are in `job_local.json`.

The flat upload bundle contains the five graphs and images, chapter plan, `colab_batch.py`, and copies of `.claude/skills/minimax-h3-video/scripts/{setup_cuda,run_workflow}.py`. The batch performs one model setup, then five sequential jobs. Each remote job persists its prompt ID; do not blindly resubmit after disconnection.

Official CLI session: `mmu-chikuwa-v9-20261027`. `execute.py` bootstraps the uploaded bundle inside `/content/mmu-chikuwa-v9-20261027`.

```sh
colab --auth oauth2 download -s mmu-chikuwa-v9-20261027 /content/mmu-chikuwa-v9-20261027/results.zip results.zip
colab --auth oauth2 stop -s mmu-chikuwa-v9-20261027
```

Results/logs are kept locally in `results/`; generated videos are not Git assets. Verify `results/status.json` SHA-256 before adoption. `assets.json` links the original 480p MP4s into Remotion. Final scaling preserves aspect ratio; exact captions are rendered at 720p. No generated dialogue or generated text is used.
