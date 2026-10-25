# Skill: Create a rendered video from HTML

Use this skill when the user requests a video, animation, beat edit, title sequence, or visual loop.

## Workflow
1. Create a self-contained HTML/CSS/JavaScript scene with explicit canvas size, background, timing, and animation. Prefer deterministic animation driven by a known frame/time value rather than wall-clock timing.
2. Create a Python renderer script that loads the HTML using Playwright/Chromium and captures frames at a fixed FPS. If available, use Pillow or imageio/FFmpeg to assemble frames into MP4; check installed dependencies first.
3. Make the renderer accept `--html` and `--output` arguments because the `render_video` tool invokes it that way. The output path must be inside the workspace.
4. Execute the renderer with `render_video`. If dependencies are missing, report the exact missing package and provide a requirements file rather than claiming a video was rendered.
5. Verify the output exists, is non-empty, and has a plausible size. If ffprobe is installed, inspect duration, dimensions, and frame rate.
6. Send the final video file using `send_file` and also provide the HTML and Python source when useful.

## Important
- Never say the video is ready until the renderer confirms a non-empty output file.
- Do not rely on external network assets unless the user asks for them.
- Keep frame count and render time reasonable; for previews, use 720p and 24–30 FPS.
- Use an authorized browser context; do not evade logins, paywalls, or anti-abuse protections.
