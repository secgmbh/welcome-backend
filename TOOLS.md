---
summary: "Workspace template for TOOLS.md"
read_when:
  - Bootstrapping a workspace manually
---

# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## Citedy SEO Agent

**API Key:** `citedy_agent_ZJcQHw2RyCkv3Onjni1INyq4hJFx8YQt`
**Agent:** Vadim-WelcomeLink
**Referral:** https://www.citedy.com/register?ref=CKV8PFZ7

### Quick Commands

**Check Status:**
```bash
curl -s https://www.citedy.com/api/agent/me \
  -H "Authorization: Bearer citedy_agent_ZJcQHw2RyCkv3Onjni1INyq4hJFx8YQt"
```

**Generate Article:**
```bash
curl -X POST https://www.citedy.com/api/agent/autopilot \
  -H "Authorization: Bearer citedy_agent_ZJcQHw2RyCkv3Onjni1INyq4hJFx8YQt" \
  -H "Content-Type: application/json" \
  -d '{"topic": "Topic here", "size": "mini", "language": "de"}'
```

---

Add whatever helps you do your job. This is your cheat sheet.