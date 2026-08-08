from fastapi import FastAPI
from fastapi.responses import RedirectResponse

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

@app.get("/")
def redirect_to_streamlit():
    return RedirectResponse(url="https://remienterprisesuite-3exqr8tuezumc9omtprvwn.streamlit.app/", status_code=307)

@app.get("/{path:path}")
def redirect_with_path(path: str):
    return RedirectResponse(url=f"https://remienterprisesuite-3exqr8tuezumc9omtprvwn.streamlit.app/{path}", status_code=307)
