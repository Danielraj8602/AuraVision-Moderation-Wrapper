from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import traceback

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.post("/api/process")
async def process_image(
    file: UploadFile = File(None),
    url: str = Form(None)
):
    try:
        # Defer import to catch initialization errors
        try:
            from wrapper import UltimateModerationWrapper
        except ImportError:
            try:
                from api.wrapper import UltimateModerationWrapper
            except ImportError as e:
                return {"error": "Import Error", "detail": str(e), "traceback": traceback.format_exc()}
        except Exception as e:
            return {"error": "Unknown Error on Import", "detail": str(e), "traceback": traceback.format_exc()}

        wrapper = UltimateModerationWrapper()

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
        traceback.print_exc()
        return {"error": "Execution Error", "detail": str(e), "traceback": traceback.format_exc()}
