# BellRinger Go-Live Path

BellRinger is ready for a Vercel beta once account secrets are added.

## Current State

- Frontend app is built in `index.html`, `styles.css`, and `app.js`.
- Local Node server is in `server.js`.
- Vercel serverless API routes are in `api/`.
- Shared OpenAI logic is in `lib/openai-service.js`.
- Vercel config is in `vercel.json`.

## Beta Deployment Steps

1. Create or choose a GitHub repository for BellRinger.
2. Push this folder to that repository.
3. In Vercel, import the GitHub repository.
4. Add environment variables in Vercel:
   - `OPENAI_API_KEY`
   - `OPENAI_MODEL=gpt-4.1`
5. Deploy.
6. Open `/api/health` on the deployed domain and confirm:

```json
{ "ok": true, "aiConfigured": true }
```

## What This Beta Can Test

- Real ChatGPT item generation quality
- Real ChatGPT grading/feedback quality
- Teacher scheduling workflow
- Student answering workflow
- General UI and classroom flow

## What Still Needs Firebase

The beta still stores classroom data in each browser. To let real teachers and students share classes, assignments, submissions, and grades across devices, add Firebase next.

Recommended Firebase pieces:

- Firebase Authentication
- Firestore database
- Firestore security rules
- Optional Firebase Hosting only if you decide not to use Vercel

Suggested Firestore collections:

- `users/{userId}`
- `classes/{classId}`
- `classes/{classId}/bellringers/{bellringerId}`
- `classes/{classId}/students/{studentId}`
- `classes/{classId}/submissions/{submissionId}`

Security rule shape:

- Teachers can create/update classes and bell ringers they own.
- Teachers can read submissions for their classes.
- Students can read published bell ringers for joined classes.
- Students can create/update only their own submissions.
- Students cannot read or write gradebook data for other students.
