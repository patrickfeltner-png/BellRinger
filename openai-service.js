const model = process.env.OPENAI_MODEL || "gpt-4.1";

const bellringerSchema = {
  type: "object",
  additionalProperties: false,
  required: ["items"],
  properties: {
    items: {
      type: "array",
      minItems: 1,
      items: {
        type: "object",
        additionalProperties: false,
        required: ["date", "studentPrompt", "answerKey", "rubric"],
        properties: {
          date: { type: "string" },
          studentPrompt: { type: "string" },
          answerKey: { type: "string" },
          rubric: { type: "string" }
        }
      }
    }
  }
};

const gradeSchema = {
  type: "object",
  additionalProperties: false,
  required: ["score", "whatWentWell", "suggestion", "feedback"],
  properties: {
    score: { type: "integer", minimum: 0, maximum: 5 },
    whatWentWell: { type: "string" },
    suggestion: { type: "string" },
    feedback: { type: "string" }
  }
};

async function generateBellringers(body) {
  return openaiJson({
    name: "bellringer_generation",
    schema: bellringerSchema,
    instructions: [
      "You are an expert Kentucky middle-grades assessment item writer.",
      "Create original BellRinger items similar in spirit to Kentucky Summative Assessment classroom practice, not copied from any secure or released test.",
      "Students must never see standard codes or standard wording.",
      "Every item must be on the selected grade reading level and appropriate for grades 5-8.",
      "For ELA, include an original passage and one question.",
      "For Social Studies, include an original source and one source-based question.",
      "For Math, include an original problem or scenario and one question.",
      "For Science, include an original source, data table, observation, or investigation description and one question.",
      "Use the teacherPrompt as the main topic, unit focus, or content direction whenever provided.",
      "Honor the selected questionType. For multiple choice, include answer choices A-D. For multiple select, include several choices and tell students to choose all that apply. For drag and drop, write it as a clear matching/sorting task that can be answered in text. For short answer or constructed response, require evidence or reasoning.",
      "Questions should require evidence, reasoning, or explanation based on the DOK setting.",
      "Return classroom-ready student text, a concise answer key, and a 0-5 point rubric."
    ].join(" "),
    input: {
      task: "Generate bell ringer items for the selected school days.",
      grade: body.grade,
      subject: body.subject,
      dok: body.dok,
      questionType: body.questionType,
      teacherPrompt: body.teacherPrompt || "",
      dates: body.dates,
      standards: body.standards
    }
  });
}

async function gradeSubmission(body) {
  return openaiJson({
    name: "bellringer_grade",
    schema: gradeSchema,
    instructions: [
      "You are a fair, encouraging Kentucky middle-grades teacher.",
      "Grade the student answer from 0 to 5 points.",
      "Reward accurate understanding, use of evidence, reasoning, and completeness.",
      "Feedback must first tell the student something specific they did right.",
      "Then give one specific suggestion for how to improve.",
      "Do not mention hidden standards or reveal teacher-only rubric details."
    ].join(" "),
    input: {
      question: body.question,
      answer: body.answer,
      subject: body.subject,
      grade: body.grade,
      dok: body.dok,
      questionType: body.questionType,
      standards: body.standards
    }
  });
}

async function openaiJson({ name, schema, instructions, input }) {
  if (!process.env.OPENAI_API_KEY) {
    const error = new Error("OPENAI_API_KEY is not configured");
    error.statusCode = 503;
    throw error;
  }

  const response = await fetch("https://api.openai.com/v1/responses", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${process.env.OPENAI_API_KEY}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      model,
      input: [
        { role: "developer", content: [{ type: "input_text", text: instructions }] },
        { role: "user", content: [{ type: "input_text", text: JSON.stringify(input) }] }
      ],
      text: {
        format: {
          type: "json_schema",
          name,
          strict: true,
          schema
        }
      }
    })
  });

  const data = await response.json();
  if (!response.ok) {
    const error = new Error(data.error?.message || "OpenAI request failed");
    error.statusCode = response.status;
    throw error;
  }

  const text = data.output_text || data.output?.flatMap((item) => item.content || [])
    .find((content) => content.type === "output_text")?.text;
  if (!text) throw new Error("OpenAI response did not include structured output text");
  return JSON.parse(text);
}

module.exports = {
  generateBellringers,
  gradeSubmission
};
