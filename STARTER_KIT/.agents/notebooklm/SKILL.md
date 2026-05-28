# <instructions>

🚀 NotebookLM — Интеграция и Руководство (Gemini CLI / macOS)

Ты выступаешь как продвинутый оркестратор связки NotebookLM и Gemini CLI в рамках локального проекта (папки).
Текущая рабочая директория: `/Users/pavelsarko/Library/Mobile Documents/iCloud~md~obsidian/Documents/work-notes`

## 🛠 1. Настройка и Установка (Уже выполнено, справочная информация)
Если потребуется переустановить, обновить или починить интеграцию на macOS:
1. **Установка пакета:** `uv tool install notebooklm-mcp-server`
2. **Авторизация:** Завершить Chrome, затем выполнить `~/.local/bin/notebooklm-mcp-auth` (токены сохранятся в `~/.notebooklm-mcp/auth.json`).
3. **Конфигурация MCP:** Сервер прописан в `~/.gemini/antigravity/mcp_config.json` и локальном `amop_config.json`.
4. **Проверка работы:** Вызов инструмента `notebook_list` или `gemini mcp list`.

---

## 🧠 Brain.MD — Gemini CLI + NotebookLM: The Ultimate Combinations

The Brain + The Builder. NotebookLM researches, analyzes, and creates. Gemini CLI takes action, builds, automates, and manages your local markdown files. Together? Unstoppable.

---

### 🎓 Learning & Education

**The 30-Minute Course Creator**
Turn any topic into a sellable course — automatically.
- **Step 1:** `research_start` (deep) → 40+ sources on your topic
- **Step 2:** `source_get_content` → Extract key modules as markdown
- **Step 3:** `video_overview_create` → Intro videos for each module
- **Step 4:** `audio_overview_create` → Podcast-style audio lessons
- **Step 5:** `quiz_create` + `flashcards_create` → Student assessments
- **Step 6:** Gemini CLI → Build course platform / folder structure in Obsidian
💰 **Output:** Complete course structure locally in under 30 minutes.

**The Learning Accelerator**
Master any skill 10x faster with AI-generated curriculum.
- 📚 Deep research on skill + best resources
- 🗺️ Mind map showing learning path (`mind_map_create`)
- 📝 Study guide with key concepts
- 🎧 Audio briefings for commute learning
- ✅ Quizzes to test retention
- 📊 Gemini CLI builds a local dashboard tracking your progress in Markdown.

---

### 💼 Business & Agency

**Client Onboarding on Autopilot**
8 hours → 10 minutes.
- Input: Client's website / forms.
- NotebookLM deep-dives into their industry.
- Generates:
  → Video Overview: "Your Industry Landscape"
  → Infographic: Market opportunity map (`infographic_create`)
  → Data Table: Competitor comparison (`data_table_create`)
  → Slide Deck: Strategy presentation (`slide_deck_create`)
- Gemini CLI organizes these assets into a clean Obsidian client folder.

**Weekly Competitor Intelligence**
- Gemini CLI scrapes competitor websites / blogs via web-fetch.
- Feed content into NotebookLM (`notebook_add_text` / `notebook_add_url`).
- Generate trend report (`report_create`).
- Save directly to your Obsidian vault!

---

### 📰 Content Creation

**The Content Repurposing Engine**
One piece of research → 12 pieces of content.
Deep Research on Topic →
- 📝 Blog Post (`report_create`)
- 🎬 YouTube Script (`video_overview_create`)
- 🎙️ Podcast Episode (`audio_overview_create`)
- 📊 Infographic (`infographic_create`)
- 🎴 Slide Deck (`slide_deck_create`)
- 🗺️ Mind Map (`mind_map_create`)
- ❓ FAQ Document (`notebook_query`)
- Gemini CLI takes all outputs and formats them perfectly in your workspace.

**Podcast Show Prep**
- Deep research on guest's background + work.
- Generate briefing doc with key talking points.
- Create audio overview to listen before recording.
- Build question bank from their content themes.

---

### 🔬 Research & Analysis

**The Executive Briefing System**
- Executive Summary → Briefing Doc → 2-min read
- Audio Briefing → Deep Dive Podcast → Commute listening
- Visual Summary → Infographic → Share with team
- Deep Dive → Full Report → Reference doc

**Due Diligence System**
Input: Company name + website
- Research: Financials, news, competitors, leadership.
- Generate: Risk assessment briefing, Competitor positioning map, Leadership background table.
- Gemini CLI builds a local due diligence dashboard in Obsidian.

---

### 🏠 Personal Productivity (Для Obsidian / Тренерских заметок)

**Health & Fitness Research (Идеально для клиентов, например Салиха)**
1. Research: Latest studies on specific health goals.
2. Generate: Study guide with actionable insights.
3. Create: Meal plan data table (`data_table_create`).
4. Build: Gemini CLI integrates this into the client's `.md` profile.

**Book Club / Learning on Steroids**
- Add book as source (PDF or summary).
- Generate discussion questions (`notebook_query`).
- Create mind map of themes.
- Build audio overview as refresher.

---

### 🔧 Output Formats Reference

**Audio Overview Styles:**
`deep_dive` — Comprehensive two-host exploration
`brief` — Quick summary
`critique` — Critical analysis
`debate` — Multiple perspectives

**Video Overview Styles:**
`classic`, `whiteboard`, `kawaii`, `anime`, `watercolor`, `retro_print`, `heritage`, `paper_craft`

**Infographic Styles:**
`sketch-note`, `professional`, `bento-grid`, `editorial`, `instructional`, `bricks`, `clay`, `anime`, `kawaii`, `scientific`

---

### 💡 Pro Tips
- 🎯 **Token Savings:** Use `source_get_content` to extract only what you need before querying, or use `notebook_query` for precise extraction.
- 🎨 **Match Visual Style to Audience:** `kawaii` for Gen Z, `classic` for executives, `whiteboard` for education.
- 📊 **Stack Outputs:** Combine infographic + audio + data table for complete content packages and let Gemini CLI save them directly to your markdown notes!

---

**ЕСЛИ ЧТО-ТО ПОШЛО НЕ ТАК:**
Если Gemini CLI теряет доступ к NotebookLM, выполни в терминале:
`pkill -i "Google Chrome"`
`~/.local/bin/notebooklm-mcp-auth`

</instructions>