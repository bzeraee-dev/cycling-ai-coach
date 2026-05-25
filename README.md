# 🚴 Adaptive Cycling Coach

An automated AI-powered cycling coaching pipeline built with Python, Strava API, and Claude LLM.

## What it does
- Connects to Strava API and pulls your ride history automatically
- Calculates performance metrics and trends (distance, speed, elevation, fatigue)
- Sends your data to Claude LLM for personalized coaching analysis
- Delivers a formatted HTML coaching report to your inbox every month

## Architecture
Strava API → Data Pipeline → Metrics Engine → Claude LLM → Email Delivery

## Tech Stack
- **Python** — core pipeline
- **Strava API** — ride data ingestion with OAuth2 authentication
- **Claude API (Anthropic)** — LLM-powered coaching insights
- **Pandas** — data processing and trend analysis
- **SMTP / Gmail** — automated email delivery
- **Windows Task Scheduler** — monthly automation

## Setup
1. Clone the repo
2. Install dependencies: `pip install requests pandas anthropic`
3. Set your credentials in the environment variables section
4. Run: `python cycling-ai-coach.py`

## Collaboration
Built in collaboration with a PhD researcher at **Mila (Montreal Institute for Learning Algorithms)**.

Next phase: Fine-tuning a Gemma model using Coach-in-the-Loop methodology (SFT + DPO) for personalized cycling coaching.

## Author
Behzad Zeraee | [LinkedIn](https://www.linkedin.com/in/behzad-h-zeraee)