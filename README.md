# BellRinger

BellRinger is a classroom bell-ringer app with teacher scheduling, student responses, and OpenAI-backed generation and grading.

## What is included

- Teacher sign-in with school email validation
- Teacher password check to protect teacher tools and gradebook access
- Teacher-created class page with a join code
- Kentucky standards picker for grades 5-8 with subject, grade, search, and multi-select filters
- Teacher calendar for selecting one school day, a range, or multiple individual dates
- OpenAI-backed KSA-style bell ringer generation for reading passages, source-based prompts, math problems, and science investigations
- Grade-level reading/source/problem text for generated bell ringers
- Student view hides standards and shows only the item content students need
- Batch publishing for multiple selected dates
- Student sign-in and date picker that blocks future dates
- OpenAI-backed auto-grading from 0-5 points with positive feedback and improvement suggestions
- Student running feedback
- Teacher gradebook with day, week, and month totals

## Run it

Install dependencies and start the Node server:

```bash
npm install
npm start
```

Then open `http://localhost:4174`.

For local AI generation and grading, create a `.env` file or set these environment variables before starting:

```bash
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4.1
PORT=4174
```

The app stores classroom prototype data in `localStorage`. A production school deployment should replace this with a real database.

## ChatGPT integration path

The browser calls backend endpoints so API keys are never exposed in student browsers:

- `POST /api/bellringers/generate`
- `POST /api/submissions/grade`

The backend uses OpenAI structured JSON output for predictable generated items and predictable grading responses. If `OPENAI_API_KEY` is not configured, the app falls back to the local demo generator/grader and displays a warning.

## Vercel Deployment

This folder includes `vercel.json` and Vercel serverless API routes under `api/`.

1. Push this project to GitHub.
2. In Vercel, import the GitHub repository as a new project.
3. Add these environment variables in Vercel project settings:
   - `OPENAI_API_KEY`
   - `OPENAI_MODEL` set to `gpt-4.1`
4. Deploy.

The local `server.js` is for development and non-Vercel Node hosting. Vercel uses the files in `api/` instead.

## Firebase Next Step

For real classroom use, Firebase should be added next:

- Firebase Authentication for teacher and student sign-in
- Firestore collections for teachers, classes, bell ringers, submissions, and gradebook rows
- Security rules so students can only read assigned bell ringers and write their own submissions
- Teacher-only rules for creating bell ringers and viewing gradebooks

Before real classroom use, add secure authentication, password hashing, sessions, role-based authorization, district-approved student privacy controls, a database, and the complete official Kentucky Academic Standards dataset.

## Demo teacher login

- Email: `ms.hart@fayette.kyschools.us`
- Password: `BellRinger2026!`

This prototype password is only for local demo behavior. A production app should use secure server-side authentication, password hashing, sessions, and role-based authorization.
