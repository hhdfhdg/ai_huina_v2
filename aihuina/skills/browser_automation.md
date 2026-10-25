# Skill: Browser automation

Use Playwright to inspect pages, click controls, fill forms, choose options, wait for UI updates, and read visible page text. Use a compact sequence of up to 20 steps per call.

## Procedure
1. Open the requested URL and inspect title and visible text.
2. Identify stable CSS selectors (prefer labels, accessible roles, IDs, and data attributes).
3. Perform only the requested actions. After important actions, read visible text or inspect the resulting URL to confirm the state.
4. For tests, record the outcome of each step and distinguish pass, fail, and blocked.
5. Capture screenshots for model analysis only if the server has explicitly enabled image input and the actual measured generation speed is above 50 tokens/sec. A model-provided argument is not proof of speed or image capability.

Do not bypass authentication, access controls, CAPTCHA, rate limits, or site protections. Never submit purchases, payments, destructive actions, or public posts without explicit user authorization.
