# PLAN.md — ai-html-tools (Plane Shooter v1)

## Goal
Build a kid-friendly **English-only** static web game: **Plane Shooter**.

## Scope (v1)
- Single page: `plane_shooter.html`
- Pure frontend: HTML + CSS + Vanilla JS
- Keyboard controls: `← →` move, `Space` shoot
- Enemy spawn + downward movement
- Bullet/enemy collision, score, lives, game over, restart
- No backend, no login, no cloud storage

## Milestones

### M1. Game Shell
- Canvas setup, game loop (update/render)
- State machine: `menu / playing / paused / gameover`
- English UI labels and hints

**Acceptance**
- Game opens and starts reliably
- Stable rendering and updates

### M2. Player + Shooting
- Player plane movement with boundary limits
- Space to shoot with fire-rate cooldown
- Bullet cleanup out of screen

**Acceptance**
- Controls feel responsive
- No uncontrolled bullet flood

### M3. Enemy System
- Timed enemy spawning
- Enemies move downward
- Difficulty scales gradually (speed/spawn)

**Acceptance**
- Continuous enemy waves
- Difficulty increases smoothly

### M4. Typing Hit Rules (Updated)
- Each enemy plane has one letter (A-Z)
- Press matching key => enemy explodes, score increases
- Wrong key => soft penalty (small score loss / streak reset)
- Enemy reaches bottom => lose life
- Lives reach 0 => game over

**Acceptance**
- Letter matching logic is correct
- Score/life logic is correct
- Restart works

### M5. Integrate + Docs
- Add homepage entry button
- Update README with game page and controls
- Keep all text in English

**Acceptance**
- GitHub Pages playable from home page
- New user understands controls in <10s

## Out of Scope (v1)
- Boss fights
- Online leaderboard
- Accounts/cloud sync
- Asset pipeline / frameworks

## Dev Notes
- Keep code simple and readable for iteration
- Prefer shapes on canvas (no external assets required)
- Commit by milestone when possible
