



flowchart TD
    U[User] --> A[LLM Agent]

    A --> T[Agent Tools]

    T --> C[Content Generator]
    T --> S[Slack Approval Tool]

    S --> SL[Slack Message<br/>Approve / Reject]
    SL --> W[Flask Webhook]

    W --> R[(Redis)]
    R -->|status| A

    A -->|approved| P[Posting Tool]
    P --> SM[Social Media APIs]

    A -->|rejected / timeout| X[Abort Task]
