from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
try:
    from wrapper import UltimateModerationWrapper
except ImportError:
    from api.wrapper import UltimateModerationWrapper
from pydantic import BaseModel
import uvicorn

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

wrapper = UltimateModerationWrapper()

@app.post("/api/process")
async def process_image(
    file: UploadFile = File(None),
    url: str = Form(None)
):
    try:
        input_source = None
        if file:
            input_source = await file.read()
        elif url:
            input_source = url
        else:
            raise HTTPException(status_code=400, detail="Must provide either file or url")

        result = wrapper.process(input_source)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
