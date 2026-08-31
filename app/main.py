from fastapi import FastAPI

app = FastAPI(
    title="ClauseIQ API",
    description="Contract & Policy Analyzer with Clause Intelligence",
    version="0.1.0",
)


@app.get("/")
def health_check():
    return {"status": "ok", "app": "ClauseIQ"}
