# Capstone Idea to Specs

```
I need to find a product idea for my GEN AI capstone project. Here are the constraints:

ABOUT ME:
- My role: ml engineer, phd student, sportsman
- My interests/hobbies: ml, ai, grip sport, armwrestling, running, music, art
- My daily frustrations: I lose track of my training progress, I train without systematic approach, I struggle with new PhD papers ideas, I struggle with copying and adapting formulas from paper PDFs into my PhD dissertation
- Domain I know well: sports, healthcare, recommender systems

PRODUCT CONSTRAINTS:
- It must NOT be just a wrapper around ChatGPT — if a user can get the same result by pasting text into ChatGPT, it's not a product
- It must store and use MY data — the app needs a database and should get more valuable the more I use it
- It should solve a real problem that I or people around me actually have
- It should be buildable as an MVP with a basic frontend, a backend, and a database

TECHNICAL CONSTRAINTS:
- Must use at least one GenAI capability (LLM API) as a core part of the product, not a bolt-on
- Infrastructure as Code (e.g., Terraform/CDK): one-command deploy to AWS for capstone demo, one-command teardown — zero lingering resources
- Zero cost in steady state: use AWS Free Tier only (Lambda, DynamoDB, S3, API Gateway), no paid services running idle
- LLM API costs: use free-tier or budget-capped provider (e.g., Claude API with hard spend limit, or local model via Ollama for dev)
- Security: API rate limiting, auth on all endpoints, input validation to prevent prompt injection, usage caps per user to prevent abuse
- Must run locally for development without AWS dependency
- Must be implementable within 7 days using Claude Code ($20 plan)



TECHNICAL SCOPE, POSSIBILITIES:
- Multi-step AI agents with tool use and function calling
- RAG pipelines with vector stores (Pinecone, Chroma, pgvector, etc.)
- GenAI Data processing pipelines
- Multi-agent systems and orchestration
- Structured workflows with conditional logic
- Integration with external APIs and data sources
- Proper UI with state management

GOOD CAPSTONE PROJECT EXAMPLES
- A domain-specific research assistant that retrieves and synthesizes information from your own document corpus (RAG)
- An AI agent that automates a multi-step workflow in your field (e.g., code review pipeline, contract analysis, onboarding assistant)
- A multi-agent system where specialized agents collaborate (e.g., analyst + writer + reviewer)
- A tool-augmented assistant that can query databases, call APIs, and produce reports

EVALUATION CRITERIA:
- Can it be built as an MVP with a frontend, backend, database, and a single LLM API call?
- Does it store user data and get more valuable over time (not a stateless ChatGPT wrapper)?
- Does it solve a real problem I care about?
- Is the scope small enough to finish, but interesting enough to learn from?
- Does it use at least one advanced GenAI pattern (RAG, agents, tool use)?
- Does it solve a meaningful problem in your domain?
- Is it demonstrable — can you show it working end-to-end?
- Is the scope realistic for an individual project with the techniques you'll learn?

IDEA SEEDS (optional — use if you're stuck):
- "I track my spending in a spreadsheet but never learn from it. I want something that remembers my transactions and tells me where my money actually goes."
- "I'm applying to jobs and keep losing track of what I applied to and what I said. I want an app that keeps my history and helps me prep for each one."
- "I take notes every day but never review them. I want something that stores my notes and helps me see patterns or quiz myself later."
- "I cook the same 5 meals every week. I want something that remembers what I eat, learns my taste, and suggests new recipes based on what's in my fridge."
- "I'm learning a new language and keep forgetting vocabulary. I want an app that tracks the words I struggle with and generates practice exercises from my weak spots."
```
