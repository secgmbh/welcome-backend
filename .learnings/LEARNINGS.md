# Learnings

## [LRN-20260314-002] bug_found

**Logged**: 2026-03-14T19:50:00+01:00
**Priority**: medium
**Status**: pending
**Area**: frontend

### Summary
Memory Leaks in useEffect - setTimeout/fetch ohne Cleanup

### Details
Mehrere Komponenten haben useEffect Hooks ohne Cleanup-Funktionen:
- `AdminPage.jsx` - showToast setTimeout ohne Cleanup
- `DashboardPage.jsx` - fetch ohne AbortController
- `LiveFeedPage.jsx` - potentielle Intervalle ohne Cleanup

### Suggested Action
Cleanup-Funktionen in allen useEffect Hooks hinzufügen:
```javascript
useEffect(() => {
  let isMounted = true;
  const controller = new AbortController();
  // ... async operations
  return () => {
    isMounted = false;
    controller.abort();
  };
}, []);
```

### Metadata
- Source: qa_review
- Related Files: AdminPage.jsx, DashboardPage.jsx, LiveFeedPage.jsx
- Tags: memory_leak, useEffect, cleanup

---

## [LRN-20260314-001] correction

**Logged**: 2026-03-14T14:42:00+01:00
**Priority**: high
**Status**: fixed
**Area**: frontend

### Summary
Oberflächliche Browser-Checks übersehen visuelle Bugs

### Details
Ich habe mit `agent-browser snapshot` die Seiten schnell gecheckt und behauptet, alles sei okay. Aber ich habe NICHT:
- Screenshots visuell analysiert
- Mobile Viewport getestet
- Tatsächliche Interaktionen durchgeführt
- Nach duplizierten Elementen in der DOM-Tiefe gesucht

Der User hat recht: Ich sehe viele Fehler nicht, weil ich nicht ordentlich schaue.

### Suggested Action
1. IMMER Screenshots machen und visuell prüfen
2. Mobile Viewport testen (390x844)
3. Nach unten scrollen und Footer prüfen
4. Nach duplizierten Elementen suchen
5. Interaktionen testen (Buttons klicken, Formulare ausfüllen)

### Metadata
- Source: user_feedback
- Related Files: Layout.jsx, MobileBottomNav.jsx
- Tags: qa, testing, browser, mobile
- Pattern-Key: qa.superficial_check
- Recurrence-Count: 1
- First-Seen: 2026-03-14
- Last-Seen: 2026-03-14

---