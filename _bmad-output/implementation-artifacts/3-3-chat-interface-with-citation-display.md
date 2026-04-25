# Story 3.3: Chat Interface with Citation Display

Status: review

## Story

As an **athlete**,
I want a conversational chat interface that displays dual-cited coaching responses with distinct citation styling,
so that I can ask questions naturally and verify the sources behind every recommendation.

## Acceptance Criteria

1. **Given** I navigate to the Chat tab **When** the page loads **Then** I see a ChatInputBar at the bottom with placeholder "Ask about your training..." and a send button (UX-DR8)

2. **Given** I type a question and tap send **When** the query is submitted **Then** my message appears as a user ChatBubble (right-aligned, Blue-500 bg, white text), a loading indicator shows "StrengthWise is thinking..." with pulsing dots (UX-DR14), and the AI response appears as an AI ChatBubble (left-aligned, Zinc-800 bg) when complete

3. **Given** an AI response contains personal data citations **When** the response renders **Then** PersonalCitation blocks appear with Blue-400 left border (3px), blue-tinted background (`rgba(96,165,250,0.08)`), "YOUR DATA" label in Blue-400 uppercase, showing session date and specific metrics (UX-DR4)

4. **Given** an AI response contains general knowledge citations **When** the response renders **Then** KnowledgeCitation blocks appear with Amber-400 left border (3px), amber-tinted background (`rgba(251,191,36,0.08)`), "TRAINING SCIENCE" label in Amber-400 uppercase, showing principle name and source (UX-DR4)

5. **Given** an AI response is displayed **When** I look below the response **Then** I see 2-3 FollowupChip components with suggested follow-up questions (pill-shaped, tappable to send as new query) (UX-DR7)

6. **Given** an AI response is displayed **When** I look at the response **Then** it includes a medical advice disclaimer: "StrengthWise provides training insights, not medical advice" (FR27)

7. **Given** I am a new user with fewer than 5 sessions **When** I open the Chat tab **Then** I see 3 starter prompt cards with sport-specific suggested questions and subtitle "The more sessions you log, the better my answers get." (UX-DR16)

8. **Given** the chat area has messages **When** a new AI response appears **Then** the chat area has `role="log"` with `aria-live="polite"` so screen readers announce it, and citation blocks have `aria-label` identifying source type (UX-DR20)

9. **Given** the daily rate limit is exhausted **When** I view the Chat tab **Then** the ChatInputBar is disabled with text "Daily limit reached. Resets at [time]." and the QueryCounter shows in Red-400 (UX-DR9, UX-DR23)

10. **Given** a network or API error occurs **When** a query is submitted **Then** an inline error message appears below the input: "I couldn't process that question right now. Please try again." — no raw error or crash (UX-DR19)

## Tasks / Subtasks

- [x] Task 1: Add `postQuery` to `frontend/src/api.js` (AC: #2)
  - [x] 1.1: Add `postQuery(queryText)` function to `api.js`:
    ```js
    export async function postQuery(queryText) {
      const url = `${BASE_URL}/query`
      const token = await getToken()
      const headers = { 'Content-Type': 'application/json' }
      if (token) headers['Authorization'] = `Bearer ${token}`
      const response = await fetch(url, {
        method: 'POST',
        headers,
        body: JSON.stringify({ query: queryText }),
      })
      if (response.status === 429) {
        const body = await response.json()
        throw Object.assign(new Error('RATE_LIMIT_EXCEEDED'), { code: 'RATE_LIMIT_EXCEEDED', detail: body.detail })
      }
      if (!response.ok) throw new Error('AI_UNAVAILABLE')
      return response.json()
    }
    ```
  - [x] 1.2: Do NOT call `apiFetch` for the query endpoint — rate limit 429 requires custom error parsing with `detail.resetAt`. Raw `apiFetch` throws on non-ok, losing the 429 body.

- [x] Task 2: Create `frontend/src/components/CitationBlock.jsx` (AC: #3, #4)
  - [x] 2.1: Single component accepting `type` prop (`"personal"` | `"knowledge"`) and `citation` object
  - [x] 2.2: PersonalCitation variant (`type="personal"`):
    - `style={{ borderLeft: '3px solid #60a5fa', background: 'rgba(96,165,250,0.08)' }}`
    - Label: `<span class="text-xs font-bold uppercase text-blue-400">YOUR DATA</span>`
    - Content: `{citation.sessionDate} — {citation.exercise}: {citation.detail}`
    - `aria-label="Personal training data citation"`
  - [x] 2.3: KnowledgeCitation variant (`type="knowledge"`):
    - `style={{ borderLeft: '3px solid #fbbf24', background: 'rgba(251,191,36,0.08)' }}`
    - Label: `<span class="text-xs font-bold uppercase text-amber-400">TRAINING SCIENCE</span>`
    - Content: `{citation.principle} — {citation.source}`
    - `aria-label="General knowledge citation"`
  - [x] 2.4: Common wrapper: `rounded-r-md p-3 mb-2 text-sm text-zinc-300` (border-radius on right only per UX spec — `border-radius: 0 6px 6px 0`)
  - [x] 2.5: Use inline `style` for the colored border+background (Tailwind can't handle dynamic rgba values safely)

- [x] Task 3: Create `frontend/src/components/ChatBubble.jsx` (AC: #2, #3, #4, #5, #6)
  - [x] 3.1: Props: `role` (`"user"` | `"ai"`), `message` (string), `citations` (object with `personal` and `knowledge` arrays), `followups` (array of strings)
  - [x] 3.2: User bubble: `flex justify-end` → inner div `bg-blue-500 text-white rounded-2xl rounded-tr-sm px-4 py-2 max-w-[90%] md:max-w-[70%] text-sm`
  - [x] 3.3: AI bubble wrapper: `flex flex-col gap-2 max-w-full`
  - [x] 3.4: AI bubble message: `bg-zinc-800 text-zinc-100 rounded-2xl rounded-tl-sm px-4 py-3 text-sm leading-relaxed`
  - [x] 3.5: After AI message text, render `citations.personal.map(c => <CitationBlock type="personal" citation={c} />)` then `citations.knowledge.map(c => <CitationBlock type="knowledge" citation={c} />)` inside the bubble
  - [x] 3.6: Medical disclaimer: below citations, always: `<p class="text-xs text-zinc-500 italic px-1">StrengthWise provides training insights, not medical advice.</p>` (FR27 — NEVER omit)
  - [x] 3.7: FollowupChips rendered below the AI bubble as a separate row (not inside the bubble box)
  - [x] 3.8: Skip citation rendering if `citations` is undefined/empty arrays — handle null defensively

- [x] Task 4: Create `frontend/src/components/FollowupChip.jsx` (AC: #5)
  - [x] 4.1: Props: `question` (string), `onSelect` (callback)
  - [x] 4.2: Render: pill button, `role="button"`, `aria-label={\`Ask follow-up: \${question}\`}`
  - [x] 4.3: Style: `text-xs px-3 py-1.5 rounded-full border border-zinc-700 text-zinc-400 bg-zinc-900 hover:border-blue-500 hover:text-blue-400 transition-colors cursor-pointer`
  - [x] 4.4: On click: call `onSelect(question)` which sets the input bar value and submits OR triggers a new query directly
  - [x] 4.5: Generate follow-up chips: The backend does NOT return follow-up suggestions. Derive 2-3 contextually-appropriate chips client-side based on `confidence` level returned from API:
    - low confidence: ["How can I improve my training consistency?", "What metrics matter most for beginners?", "How often should I train per week?"]
    - medium confidence: ["What patterns do you see in my recent sessions?", "How does my volume compare to recommendations?", "What should I focus on next?"]
    - high confidence: ["What trends have developed over my training history?", "Where am I plateauing and why?", "How does my current program compare to optimal?"]

- [x] Task 5: Create `frontend/src/components/QueryCounter.jsx` (AC: #9)
  - [x] 5.1: Props: `queriesRemaining` (number | null), `resetAt` (ISO string | null), `tierLimit` (number, default 3)
  - [x] 5.2: Color logic:
    - `queriesRemaining > 2` → `text-zinc-400`
    - `queriesRemaining <= 2 && queriesRemaining > 0` → `text-amber-400`
    - `queriesRemaining === 0` → `text-red-400`
  - [x] 5.3: Display: `"{queriesRemaining} of {tierLimit} queries remaining today"` when not exhausted
  - [x] 5.4: Display when exhausted: `"Daily limit reached. Resets at {formatted resetAt time}."` (format resetAt as local time HH:MM)
  - [x] 5.5: `aria-live="polite"` on the container so screen readers announce changes
  - [x] 5.6: If `queriesRemaining` is null (initial load), render nothing

- [x] Task 6: Create `frontend/src/components/StarterPromptCard.jsx` (AC: #7)
  - [x] 6.1: Props: `question` (string), `onSelect` (callback)
  - [x] 6.2: Style: `bg-zinc-800 rounded-xl p-4 cursor-pointer hover:bg-zinc-700 transition-colors border border-zinc-700 hover:border-blue-500 text-sm text-zinc-300`
  - [x] 6.3: On click: call `onSelect(question)` to populate input bar and submit
  - [x] 6.4: Accessibility: `role="button"`, `tabIndex={0}`, handle Enter key

- [x] Task 7: Build `frontend/src/pages/Chat.jsx` (AC: #1-#10)
  - [x] 7.1: State: `messages` (array of `{role, content, citations, confidence}`), `input` (string), `isLoading` (bool), `queriesRemaining` (number|null), `resetAt` (string|null), `sessionCount` (number|null), `error` (string|null)
  - [x] 7.2: On mount: fetch session count via `getSessions()` to determine if user is new (<5 sessions). Store count. Show starter prompts if count < 5 and messages.length === 0.
  - [x] 7.3: Send query flow:
    ```
    1. Append user message to messages array
    2. Clear input, set isLoading=true, clear error
    3. Call postQuery(inputText)
    4. On success: append AI message with citations, update queriesRemaining
    5. On 429 (RATE_LIMIT_EXCEEDED): set queriesRemaining=0, set resetAt, show error inline
    6. On other error: show inline error "I couldn't process that question right now. Please try again."
    7. Always: set isLoading=false
    ```
  - [x] 7.4: Chat area: `<div role="log" aria-live="polite" aria-label="Coaching conversation">` — scrollable, flex-col, auto-scroll to bottom on new message. Use `useRef` + `useEffect` on messages.
  - [x] 7.5: Loading indicator: when `isLoading`, show AI bubble with pulsing dots:
    ```jsx
    <div class="flex gap-1 items-center px-4 py-3 bg-zinc-800 rounded-2xl rounded-tl-sm w-fit">
      <span class="w-2 h-2 bg-zinc-400 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
      <span class="w-2 h-2 bg-zinc-400 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
      <span class="w-2 h-2 bg-zinc-400 rounded-full animate-bounce"></span>
    </div>
    ```
  - [x] 7.6: ChatInputBar layout: fixed at bottom inside chat page, above TabBar. Input: `textarea` (not `input`) — supports multi-line for program paste (max-height 200px, auto-expand). `aria-label="Ask a coaching question"`. Send button `aria-label="Send question"`. Disabled when `isLoading` or `queriesRemaining === 0`.
  - [x] 7.7: Enter key on desktop submits (not newline). Use `onKeyDown` — submit if `e.key === 'Enter' && !e.shiftKey`. Shift+Enter = newline.
  - [x] 7.8: Rate limit state: when `queriesRemaining === 0`, show `<QueryCounter>` in red, disable input bar, show message inside input: "Daily limit reached. Resets at [time]."
  - [x] 7.9: Starter prompts (shown when sessions < 5 AND messages.length === 0):
    - Subtitle: `"The more sessions you log, the better my answers get."`
    - 3 sport-agnostic starter prompts: `"Why might my strength be inconsistent between sessions?"`, `"How should I structure my weekly training??"`, `"What should I focus on to improve faster?"`
    - Tapping a starter prompt populates input AND submits immediately
  - [x] 7.10: FollowupChip `onSelect`: populate input with the question text AND auto-submit (same behavior as starter prompt tap)
  - [x] 7.11: After each API response, update `queriesRemaining` from `data.queriesRemaining`
  - [x] 7.12: HeaderBar: title "Chat", with `<QueryCounter>` displayed inline (compact header variant) when `queriesRemaining !== null` — QueryCounter shown above input bar (HeaderBar.jsx not modified per story constraints)

- [x] Task 8: Verify no regressions
  - [x] 8.1: Check that `api.js` existing functions (`getExercises`, `createSession`, `getSessions`, `getSession`) are UNCHANGED
  - [x] 8.2: Check that `TabBar.jsx`, `App.jsx`, routing still works with the new Chat page — build passes with 90 modules, Chat imports verified
  - [x] 8.3: Verify `getSessions()` is imported and called correctly in Chat.jsx (it's `{ redirectOn401: false }` — already set in api.js, do not change this)
  - [x] 8.4: `npm run build` passes cleanly (170ms, 90 modules). Dev server started at http://localhost:5173. No new lint errors in modified files.

## Dev Notes

### CRITICAL: This Story is Frontend-Only

The backend `/query` endpoint is **fully complete** from Story 3.2. Do NOT modify:
- `backend/` — any file. Zero backend changes.
- `backend/routers/query.py`, `backend/services/rag_service.py`, `backend/services/rate_limit_service.py` — all done.

### Existing Files — What to Reuse

- `frontend/src/api.js` — extend with `postQuery()`. Import pattern: `import { postQuery } from '../api'` from pages.
- `frontend/src/components/HeaderBar.jsx` — already built. Use `<HeaderBar title="Chat" />`. It accepts `onSignOut` but we don't need it here.
- `frontend/src/api.js::getSessions()` — already exists. Call it in `Chat.jsx` on mount to determine session count for new-user detection.
- `frontend/src/components/TabBar.jsx` — already built. Chat page renders within existing layout — do NOT add another TabBar.

### API Response Structure (from Story 3.2)

The `/query` endpoint returns exactly:
```json
{
  "data": {
    "response": "Coaching text with medical disclaimer included...",
    "citations": {
      "personal": [
        { "sessionDate": "2026-04-15", "exercise": "Gripper close", "detail": "4x3 @ 80kg, RPE 9" }
      ],
      "knowledge": [
        { "source": "grip_sport.md", "principle": "Gripper Training" }
      ]
    },
    "confidence": "low|medium|high",
    "queriesRemaining": 2
  }
}
```

All fields are camelCase (Pydantic `to_camel` aliasing). Access as `data.data.response`, `data.data.citations.personal`, `data.data.queriesRemaining`.

The `response` text from Claude **already includes** the medical disclaimer (it's in the prompt template). Do NOT add the disclaimer as a separate sentence in the prompt — it will appear twice. Render the disclaimer as a visual UI element (separate styled paragraph) to always be visible regardless of Claude's exact output.

### 429 Rate Limit Error Shape

When rate limited, the backend returns:
```json
{ "error": "Daily query limit reached", "code": "RATE_LIMIT_EXCEEDED", "detail": { "resetAt": "2026-04-26T00:00:00Z", "limit": 3 } }
```

The custom `postQuery` in `api.js` must parse this body before throwing. Store `resetAt` in Chat component state to display to the user.

### Tailwind Custom Colors (Check Existing Config)

The project uses Tailwind v4. Verify `frontend/src/index.css` or `vite.config.js` for any custom token definitions (e.g., `bg-surface`). The existing `HeaderBar` uses `bg-surface` — this is a custom token. For chat components, use the standard Tailwind palette: `zinc-900`, `zinc-800`, `blue-500`, `blue-400`, `amber-400`, `red-400`. Do NOT use custom tokens unless they already exist.

### Inline Style for Citation Colors

Tailwind v4 cannot reliably purge/include dynamic rgba values in class strings. Use inline `style` props for citation backgrounds:
```jsx
// PersonalCitation
style={{ borderLeft: '3px solid #60a5fa', background: 'rgba(96,165,250,0.08)', borderRadius: '0 6px 6px 0' }}

// KnowledgeCitation
style={{ borderLeft: '3px solid #fbbf24', background: 'rgba(251,191,36,0.08)', borderRadius: '0 6px 6px 0' }}
```

### Auto-Scroll Pattern

```jsx
const bottomRef = useRef(null)

useEffect(() => {
  bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
}, [messages, isLoading])

// Inside JSX, after last message:
<div ref={bottomRef} />
```

### Textarea Auto-Expand

```jsx
const textareaRef = useRef(null)

function handleInputChange(e) {
  setInput(e.target.value)
  const el = textareaRef.current
  if (el) {
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 200) + 'px'
  }
}
```

### FeedbackButtons — NOT in this story

FeedbackButtons (thumbs up/down) are **Story 5.1**. Do NOT implement them here. The `/feedback` endpoint does not exist yet. Do not add placeholder button rows that will need rework.

### Program Analysis — NOT in this story

The `POST /analyze` endpoint is **Story 3.4**. The ChatInputBar in this story only calls `/query`. Do NOT add analyze mode, mode detection, or a special "Evaluate this program" path.

### File Structure

Files to create:
```
frontend/src/
├── components/
│   ├── ChatBubble.jsx       ← NEW
│   ├── CitationBlock.jsx    ← NEW
│   ├── FollowupChip.jsx     ← NEW
│   ├── QueryCounter.jsx     ← NEW
│   └── StarterPromptCard.jsx ← NEW
└── pages/
    └── Chat.jsx             ← REWRITE (currently a stub)
```

Files to modify:
```
frontend/src/api.js           ← ADD postQuery() only. Touch nothing else.
```

Files NOT to touch:
```
backend/                      ← ZERO changes
frontend/src/components/TabBar.jsx
frontend/src/components/HeaderBar.jsx
frontend/src/api.js::apiFetch, getExercises, createSession, getSessions, getSession
frontend/src/pages/Dashboard.jsx, LogSession.jsx, History.jsx
```

### Layout Structure for Chat Page

The Chat page sits inside the existing App layout (which provides TabBar). The page itself must handle a persistent input bar:

```jsx
// Chat.jsx high-level structure
export default function Chat() {
  return (
    <div className="flex flex-col h-full">
      <HeaderBar title="Chat" rightContent={<QueryCounter ... />} />
      
      {/* Scrollable message area */}
      <div role="log" aria-live="polite" className="flex-1 overflow-y-auto p-4 flex flex-col gap-4">
        {/* starter prompts or messages */}
        <div ref={bottomRef} />
      </div>

      {/* Error display */}
      {error && <div className="px-4 pb-2 text-sm text-red-400">{error}</div>}

      {/* Persistent input bar */}
      <div className="p-3 border-t border-zinc-700 bg-zinc-900">
        {/* textarea + send button */}
      </div>
    </div>
  )
}
```

Check `App.jsx` to understand how pages receive height — the existing pages use `flex-1` within a flex container. Mirror this pattern exactly.

### Confidence→FollowupChips Mapping

The API returns `confidence: "low" | "medium" | "high"`. Use this to pick contextually-relevant follow-up chips. Define the chip sets as a const outside the component to avoid re-creation:

```js
const FOLLOWUP_CHIPS = {
  low: ["How can I improve my training consistency?", "What metrics matter most for beginners?", "How often should I train per week?"],
  medium: ["What patterns do you see in my recent sessions?", "How does my volume compare to recommendations?", "What should I focus on next?"],
  high: ["What trends have developed over my training history?", "Where am I plateauing and why?", "How does my current program compare to optimal?"],
}
```

### Session Count for New-User Detection

Call `getSessions()` on Chat mount. The return value is `{ data: [...sessions] }`. Use `data.data.length` (or the sessions array length) as the session count. If the call fails, default to assuming the user has sessions (show empty chat, not starter prompts) — fail safe.

```js
useEffect(() => {
  getSessions()
    .then(res => setSessionCount(res.data?.length ?? 99))
    .catch(() => setSessionCount(99))  // fail safe: don't show starters on error
}, [])
```

### Anti-Patterns to Avoid

- **DO NOT** call `apiFetch('/query', ...)` — 429 handling requires custom fetch logic. Use the `postQuery()` function defined in Task 1.
- **DO NOT** implement FeedbackButtons (Story 5.1) or Program Analysis mode (Story 3.4)
- **DO NOT** store JWT token in localStorage — `auth.js::getToken()` handles token retrieval from memory (already built)
- **DO NOT** add a new TabBar or navigation bar inside Chat.jsx — App.jsx provides the TabBar
- **DO NOT** put business logic in JSX — move chip generation, session count fetch, and error mapping to pure functions or useMemo hooks
- **DO NOT** skip the `role="log"` and `aria-live="polite"` on the message container — required for accessibility (NFR19, UX-DR20)
- **DO NOT** use `innerHTML` to render the AI response text — render as plain text within a `<p>` tag. The response is plain text, not HTML.
- **DO NOT** show starter prompts when there are already messages in the conversation — only when messages.length === 0 AND sessionCount < 5

### Previous Story Intelligence (Story 3.2 — RAG Pipeline)

From Story 3.2 completion notes:
- Backend `/query` POST is at `http://localhost:8080/query` locally (via `VITE_API_URL` env or proxy)
- The response field `queriesRemaining` is camelCase (Pydantic `to_camel`)
- QueryUsage DynamoDB SK attribute is `"date"` — but this is backend-only; no frontend concern
- The `sanitize_llm_input` is called server-side — frontend should NOT sanitize (server does it)
- 36 backend tests pass — this story adds zero backend code, so zero risk of regression there
- `apiFetch` wrapper already handles 401 (signOut + redirect) correctly

### References

- [Source: epics.md#Story 3.3] — All 8 acceptance criteria, FR27, FR8-FR11, UX-DR4, UX-DR7, UX-DR8, UX-DR14, UX-DR16, UX-DR20, UX-DR23
- [Source: architecture.md#Frontend Architecture] — React + Vite 8 + Tailwind v4, useState + fetch (no state lib), React Router v7, api.js fetch wrapper with JWT
- [Source: architecture.md#Format Patterns] — AI coaching response JSON structure
- [Source: architecture.md#API Boundaries] — POST /query is in query.py with rag_service
- [Source: architecture.md#Enforcement Guidelines] — Use api.js wrapper, put logic in services not components, camelCase JSON fields
- [Source: ux-design-specification.md#CitationBlock] — Blue-400/Amber-400 borders, rgba backgrounds, aria-labels, full-width within bubble
- [Source: ux-design-specification.md#FollowupChip] — pill-shape, Zinc-800 bg, hover Blue-500, role="button", 12px font
- [Source: ux-design-specification.md#ChatInputBar] — textarea, 40px height, send button 40px circle, Enter submits
- [Source: ux-design-specification.md#QueryCounter] — color states by remaining count, aria-live
- [Source: implementation-artifacts/3-2-dual-source-rag-pipeline.md#Completion Notes] — Response format confirmed, queriesRemaining field, 36 tests pass
- [Source: frontend/src/api.js] — existing apiFetch pattern, getSessions, getToken import from auth.js
- [Source: frontend/src/components/HeaderBar.jsx] — HeaderBar accepts title prop, uses bg-surface token

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

None — clean implementation, no debugging required.

### Completion Notes List

- Added `postQuery()` to `api.js` with custom 429 handling (raw fetch, not `apiFetch`) to preserve rate-limit error body
- Created `CitationBlock.jsx`: single component handling both `personal` (Blue-400) and `knowledge` (Amber-400) variants using inline styles for rgba backgrounds that Tailwind v4 can't purge safely
- Created `ChatBubble.jsx`: user (right-aligned Blue-500) and AI (left-aligned Zinc-800) variants; citations rendered inside AI bubble; medical disclaimer always present (FR27); followup chips rendered below bubble in a separate row
- Created `FollowupChip.jsx`: pill button with keyboard support; calls `onSelect(question)` which auto-submits in Chat.jsx
- Created `QueryCounter.jsx`: color logic (zinc→amber→red), `aria-live="polite"`, renders nothing when `queriesRemaining` is null
- Created `StarterPromptCard.jsx`: accessible card with `role="button"`, Enter/Space keyboard support
- Built `Chat.jsx`: full state machine (messages, loading, error, rate-limit), `role="log"` with `aria-live="polite"`, auto-scroll via `useRef`, textarea auto-expand, Enter submits/Shift+Enter newline, starter prompts when `sessionCount < 5 && messages.length === 0`, QueryCounter displayed above input bar (HeaderBar.jsx not modified per story constraints), `getSessions()` fail-safe defaults to sessionCount=99
- Used `-m-4` on Chat root div to negate App.jsx's `p-4` on `<main>`, enabling edge-to-edge chat layout with correct scrollable area
- `npm run build` passes cleanly (90 modules, no errors); all new files pass ESLint with zero issues

### File List

- `frontend/src/api.js` — MODIFIED (added `postQuery`)
- `frontend/src/components/CitationBlock.jsx` — NEW
- `frontend/src/components/ChatBubble.jsx` — NEW
- `frontend/src/components/FollowupChip.jsx` — NEW
- `frontend/src/components/QueryCounter.jsx` — NEW
- `frontend/src/components/StarterPromptCard.jsx` — NEW
- `frontend/src/pages/Chat.jsx` — REWRITTEN

## Change Log

- 2026-04-26: Story 3.3 created — Chat Interface with Citation Display. Frontend-only story. Backend fully complete from 3.2.
- 2026-04-26: Story 3.3 implemented — Added postQuery to api.js; created 5 new components (CitationBlock, ChatBubble, FollowupChip, QueryCounter, StarterPromptCard); rewrote Chat.jsx with full dual-cited chat UI, accessibility, rate-limit handling, and new-user starter prompts. All 10 ACs satisfied. Build passes cleanly.
