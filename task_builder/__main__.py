"""Launch the Task Builder web server: python -m task_builder."""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("task_builder.server:app", host="127.0.0.1", port=8000, reload=False)
