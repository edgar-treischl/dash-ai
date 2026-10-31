# Usage Examples

Practical examples showing how to use Dash-AI for different tasks.

---

## Quick Examples

### 1. Ingest Personal Notes

You have Markdown notes you want to ask questions about.

**Setup:**
```bash
# Create a knowledge base from your notes
mkdir -p data/knowledge
cp ~/my_notes/*.md data/knowledge/

# Ingest all files
dash-ai ingest data/knowledge/
```

**Output:**
```
Ingesting documents...
✓ Imported 3 files
✓ Created 45 chunks
Ready to answer questions!
```

**Use it:**
```bash
dash-ai ask "What was I thinking about regarding project X?"
dash-ai ask "List all action items from my recent notes"
dash-ai ask "Summarize my meeting notes from last week"
```

---

### 2. Ask Questions About Code

You have a codebase's documentation and want to understand it.

**Setup:**
```bash
# Ingest code documentation
dash-ai ingest docs/
dash-ai ingest README.md
dash-ai ingest CONTRIBUTING.md
```

**Use it:**
```bash
# Learn the architecture
dash-ai ask "How does the authentication system work?"

# Understand specific components
dash-ai ask "What is the purpose of the middleware?"

# Get setup instructions
dash-ai ask "How do I set up the development environment?"

# Find examples
dash-ai ask "Show me an example of using the API"
```

---

### 3. Ingest Technical Documentation

You want to build a reference for a technology (e.g., Python, Django, etc.).

**Setup:**
```bash
# Get documentation (example with Python docs)
curl -o python_guide.md https://example.com/python-guide.md
dash-ai ingest python_guide.md

# Or add multiple sources
dash-ai ingest docs/stdlib/
dash-ai ingest docs/packages/
```

**Use it:**
```bash
dash-ai ask "How do I create a list comprehension?"
dash-ai ask "What's the difference between map and filter?"
dash-ai ask "How does context managers work?"
dash-ai ask "Best practices for exception handling"
```

---

### 4. Interactive Chatbot Workflow

Have a multi-turn conversation about specific topics.

**Setup:**
```bash
# Ingest company documentation
dash-ai ingest docs/company_handbook.md
dash-ai ingest docs/product_guide.md
```

**Use it (interactive mode):**
```bash
$ dash-ai chat
Starting interactive session...
Type 'exit' to quit.

> What is our company mission?
Answer: Our mission is to...

> Tell me more about our values
Answer: We value...

> How do we handle customer support?
Answer: We have a dedicated team...

> exit
Session ended. 3 questions asked in 12.5s.
```

---

### 5. Batch Processing with JSON Output

Automate questions and process results programmatically.

**Setup:**
```bash
# Create a questions file
cat > questions.txt << EOF
What is the main feature of Dash-AI?
How do I ingest documents?
What models does Dash-AI support?
EOF
```

**Use it (bash script):**
```bash
#!/bin/bash
# Script to batch ask questions and parse results

while IFS= read -r question; do
  echo "Question: $question"
  response=$(dash-ai ask "$question" --json)
  
  # Extract answer using jq
  answer=$(echo "$response" | jq -r '.answer')
  time=$(echo "$response" | jq -r '.generation_time_ms')
  
  echo "Answer: $answer"
  echo "Time: ${time}ms"
  echo "---"
done < questions.txt
```

**Output:**
```
Question: What is the main feature of Dash-AI?
Answer: Dash-AI is a local-first AI knowledge assistant...
Time: 3450ms
---

Question: How do I ingest documents?
Answer: Use `dash-ai ingest <path>` to add documents...
Time: 2890ms
---
```

---

### 6. Integration with Python Scripts

Use Dash-AI programmatically in your Python code.

**Setup:**
```bash
# Install in development mode
uv pip install -e .
```

**Use it (Python code):**
```python
from dash_ai import App

# Initialize the app
app = App()

# Ask a single question
answer = app.ask("What is Dash-AI?")
print(answer.text)
print(f"Sources: {answer.sources}")

# Run multiple questions
questions = [
    "What is the architecture?",
    "How does retrieval work?",
    "What models are supported?"
]

for q in questions:
    result = app.ask(q)
    print(f"Q: {q}")
    print(f"A: {result.text}\n")
```

---

### 7. Automate Documentation Analysis

Extract structured information from documentation.

**Setup:**
```bash
# Ingest API documentation
dash-ai ingest docs/api/reference.md
dash-ai ingest docs/api/examples.md
```

**Use it (structured prompts):**
```bash
# Extract all endpoints
dash-ai ask "List all API endpoints with their HTTP methods"

# Get authentication info
dash-ai ask "How do I authenticate API requests?"

# Find error codes
dash-ai ask "What are all the possible error codes and what do they mean?"

# Get examples
dash-ai ask "Show me example requests and responses"
```

---

### 8. Knowledge Base for Team

Create a shared knowledge base for your team.

**Setup:**
```bash
# Create team documentation directory
mkdir -p team_knowledge
cd team_knowledge

# Add team guidelines
echo "# Code Standards" > code_standards.md
echo "..." >> code_standards.md

# Add decision records
echo "# ADR-001: Use PostgreSQL" > adr_001.md

# Add FAQ
echo "# Frequently Asked Questions" > faq.md

# Ingest everything
dash-ai ingest .
```

**Team uses it:**
```bash
# Onboarding
dash-ai ask "What are our code standards?"
dash-ai ask "How do we handle error logging?"

# Decision lookup
dash-ai ask "Why do we use PostgreSQL instead of MySQL?"

# Troubleshooting
dash-ai ask "How do I debug a failing test?"
```

---

## Real-World Scenarios

### Scenario 1: Software Engineer Learning a Framework

**Goal:** Quickly learn a new framework (e.g., FastAPI).

**Process:**
```bash
# Step 1: Collect documentation
# - Download framework docs
# - Save tutorials
# - Get example code

# Step 2: Ingest to Dash-AI
mkdir -p fastapi_docs
# Copy all docs into fastapi_docs/
dash-ai ingest fastapi_docs/

# Step 3: Start learning
dash-ai chat
# Interactive conversation: "How do I create an endpoint?"
#                         "What are path parameters?"
#                         "How do I add authentication?"
```

**Benefits:**
- Faster learning curve
- Searchable knowledge base
- Keeps documentation context in mind
- Works offline after initial download

---

### Scenario 2: Research Paper Analysis

**Goal:** Analyze multiple research papers and extract insights.

**Process:**
```bash
# Step 1: Convert papers to markdown
# (Use PDF-to-markdown tools, e.g., pdf2md)
for pdf in papers/*.pdf; do
  pdf2md "$pdf" > "${pdf%.pdf}.md"
done

# Step 2: Ingest papers
dash-ai ingest papers/

# Step 3: Ask research questions
dash-ai ask "What are the common approaches to solving X?"
dash-ai ask "How do the methods compare?"
dash-ai ask "What are the limitations mentioned?"
dash-ai ask "What are the recommended future directions?"
```

---

### Scenario 3: Legal/Compliance Document Review

**Goal:** Quickly search and understand compliance requirements.

**Process:**
```bash
# Step 1: Ingest compliance docs
dash-ai ingest compliance_docs/

# Step 2: Ask specific questions
dash-ai ask "What is required for GDPR compliance?"
dash-ai ask "Which data retention policies apply to user data?"
dash-ai ask "What are the requirements for data breach notification?"
```

**Benefit:** Reduce time spent manually searching documents.

---

### Scenario 4: Internal Knowledge Transfer

**Goal:** Preserve institutional knowledge before team members leave.

**Process:**
```bash
# Step 1: Document everything
# - Create markdown guides for all processes
# - Document system architecture
# - Record decision history (ADRs)
# - Capture tribal knowledge

# Step 2: Ingest and share
dash-ai ingest knowledge_base/

# Step 3: New team members can learn from it
# And existing team can reference it anytime
dash-ai ask "How does the deployment pipeline work?"
dash-ai ask "What's our database migration process?"
```

---

### Scenario 5: Meeting Notes & Action Items

**Goal:** Track meeting notes and extract action items.

**Process:**
```bash
# Step 1: Store meeting notes in markdown
# meetings/2024-10-31-sprint-planning.md
# meetings/2024-10-31-architecture-review.md
# meetings/2024-10-31-retrospective.md

dash-ai ingest meetings/

# Step 2: Extract information
dash-ai ask "What action items were assigned to me?"
dash-ai ask "What decisions were made about architecture?"
dash-ai ask "What are the upcoming deadlines?"
```

---

## Advanced Usage

### Custom Analysis Pipeline

**Goal:** Process ingested documents through custom logic.

**Python script:**
```python
from dash_ai import App
import json

app = App()

# Define analysis questions
analyses = {
    "requirements": "List all requirements mentioned",
    "risks": "What risks or concerns are mentioned?",
    "dependencies": "What external dependencies are needed?"
}

results = {}
for key, question in analyses.items():
    result = app.ask(question)
    results[key] = {
        "question": question,
        "answer": result.text,
        "sources": [s.source_file for s in result.sources]
    }

# Save results
with open("analysis.json", "w") as f:
    json.dump(results, f, indent=2)
```

---

### Monitoring & Alerting

**Goal:** Use Dash-AI to monitor and analyze system documentation.

**Use case:**
```bash
# Regular checks
dash-ai ask "Are there any deprecation warnings in the latest docs?"
dash-ai ask "Have any security vulnerabilities been reported?"
dash-ai ask "What breaking changes are coming?"

# Feed into monitoring system
response=$(dash-ai ask "Any critical issues?" --json)
severity=$(echo "$response" | jq -r '.metadata.severity // "low"')

if [ "$severity" = "critical" ]; then
  # Alert team
  send_slack_alert "Critical update: $response"
fi
```

---

## Tips for Best Results

### 1. Structure Your Documents Well
```markdown
# Clear headings
## Use hierarchy
### Make sections searchable

- Use bullet points
- Keep paragraphs focused
- Include examples

> Use quotes for important notes
```

### 2. Ask Specific Questions
```bash
# ❌ Vague
dash-ai ask "Tell me about the system"

# ✅ Specific
dash-ai ask "How does the caching layer improve performance?"
```

### 3. Build Context Incrementally
```bash
# First question: high-level
dash-ai ask "What is the architecture?"

# Follow-up: dive deeper
dash-ai ask "Explain the database layer in detail"

# Interactive: continue conversation
dash-ai chat
```

### 4. Use JSON Output for Automation
```bash
# Extract structured data
dash-ai ask "List all environment variables" --json | jq '.answer'

# Parse and process
response=$(dash-ai ask "What are the API endpoints?" --json)
endpoints=$(echo "$response" | jq -r '.answer')
```

### 5. Organize Knowledge Base
```
data/knowledge/
├── architecture/
│   ├── overview.md
│   └── components.md
├── tutorials/
│   ├── getting_started.md
│   └── advanced_topics.md
└── reference/
    ├── api.md
    └── config.md
```

---

## Common Patterns

### Pattern 1: FAQ Database
```bash
# Create FAQ from markdown
dash-ai ingest faq.md

# Users can ask
dash-ai ask "What is the password policy?"
```

### Pattern 2: Change Log Analyzer
```bash
# Ingest all changelog files
dash-ai ingest CHANGELOG.md
dash-ai ingest release-notes/

# Ask about changes
dash-ai ask "What changed in version 2.0?"
```

### Pattern 3: Multi-Format Knowledge Base
```bash
# Mix different doc types (all converted to markdown)
dash-ai ingest docs/guides/        # Guides
dash-ai ingest docs/api/           # API reference
dash-ai ingest docs/examples/      # Code examples
dash-ai ingest docs/troubleshooting/ # Troubleshooting
```

### Pattern 4: Automated Report Generation
```bash
#!/bin/bash
# Generate report from knowledge base

echo "# System Analysis Report" > report.md
echo "Generated: $(date)" >> report.md

echo "## Architecture" >> report.md
dash-ai ask "Provide a comprehensive architecture overview" >> report.md

echo "## Performance Considerations" >> report.md
dash-ai ask "What are the main performance considerations?" >> report.md

echo "## Security" >> report.md
dash-ai ask "What security measures are in place?" >> report.md
```

---

**Last updated:** October 31, 2024  
**Applies to:** Phase 2+
