from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn

# FastAPI() creates a new web application instance
# This web server/app handles HTTP requests and also creates a router which handles the function to call based on the endpoint of the url "/account" or "/homepage" etc. 
# Based on the endpoint and the corresponding function associated with that endpoint, we can route requests via GET/POST 
# This web app instance is accessed and called through "app" variable 
app = FastAPI(title="AI Data Workflow Generator")

# This tells jinja that the html files are in the templates folder
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# If you run python main.py directly from the terminal
    # This statement will run
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)