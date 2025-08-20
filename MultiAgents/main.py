from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from agent import call_supervisor
import uvicorn

app = FastAPI()

async def streaming_response(prompt: str):
    # Simulate streaming by yielding chunks
    supervisor = call_supervisor()
    for chunk in supervisor.stream(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            },
            stream_mode='values',
            config={"configurable": {"thread_id": "1"}}
        ):
            # Ensure the tool outputs are properly validated
            print(chunk["messages"][-1].pretty_print())
            yield chunk["messages"][-1]


@app.post("/infer")
async def stream_response(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    return StreamingResponse(streaming_response(prompt), media_type="text/plain")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)