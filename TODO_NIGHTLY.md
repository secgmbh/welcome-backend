# Welcome-Link Nightly Improvement Queue

Dies ist die Queue für Night Mode Runs (22:30-04:00, alle 30min).

## Priorisierte Tasks

### High Priority
1. **Backend Logging umstellen** - `print()` durch `logger` ersetzen (security-relevant)
2. **Error Boundary optimieren** - Integration mit Error Monitoring Service
3. **E-Mail Service** - SMTP Konfiguration finalisieren

### Medium Priority
4. **Performance Monitoring** - Lighthouse Scores verbessern
5. **Loading States** - Bessere Feedback beim Laden
6. **Error Messages** - Konsistentere Fehlermeldungen

### Low Priority
7. **Code Formatting** - Black/Ruff für Python, Prettier für JS
8. **Type Safety** - Mehr TypeScript in Frontend
9. **API Documentation** - OpenAPI Spec aktualisieren

## Nightly Checklist (vor jedem Run)

- [ ] Branch: nightly-improvements
- [ ] Lock File: Kein laufender Process
- [ ] Zeitfenster: 22:30-04:00
- [ ] Files changed: ≤10
- [ ] Build/lint: Keine Fehler
- [ ] Commit message: `nightly: <description>`

## Documentation
- See `HEARTBEAT.md` for execution rules
- See `nightly-lock.sh` for lock mechanism
