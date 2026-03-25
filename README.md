# Meta × PyTorch OpenEnv Hackathon 2026

> Built for the **Meta PyTorch OpenEnv Hackathon x SST** — India's Biggest MEGA AI Hackathon.

## Overview

This repository contains a complete [OpenEnv](https://github.com/huggingface/openenv)-compliant environment that an AI agent can learn from through the standard `step()` / `reset()` / `state()` API.

## Environment Description

<!-- TODO: Describe your chosen environment here -->

## Action & Observation Spaces

<!-- TODO: Fill in after choosing your problem statement -->

### Action Space
```
{
  "action_type": str,
  ...
}
```

### Observation Space
```
{
  "state": ...,
  "reward": float,
  "done": bool
}
```

## Tasks

| Task | Difficulty | Score Range |
|------|-----------|-------------|
| Task 1 | Easy | 0.0 – 1.0 |
| Task 2 | Medium | 0.0 – 1.0 |
| Task 3 | Hard | 0.0 – 1.0 |

## Setup & Installation

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/meta-pytorch-openenv-hackathon.git
cd meta-pytorch-openenv-hackathon

# Install dependencies
pip install -r requirements.txt

# Run the environment
python scripts/run_baseline.py
```

## Running with Docker

```bash
docker build -t openenv-hackathon .
docker run -p 8000:8000 openenv-hackathon
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /reset` | Reset environment, returns initial state |
| `POST /step` | Execute an action, returns next state + reward |
| `GET /state` | Get current environment state |
| `GET /tasks` | List all tasks and action schemas |
| `GET /grader` | Get grader score after an episode |
| `GET /baseline` | Run baseline inference and return scores |

## Evaluation Criteria

- ✅ HF Space deploys and responds to `reset()`
- ✅ OpenEnv spec compliance (`openenv.yaml`, typed models)
- ✅ Dockerfile builds
- ✅ Baseline script runs without error
- ✅ 3+ tasks with graders (scores in 0.0–1.0 range)

## Submission Deadline

**7th April 2026, 11:59 PM**

## License

MIT
