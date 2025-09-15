# FastAPI: receives requests and handles logic
import csv
import io
from fastapi import FastAPI, Request, UploadFile
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


# Decorator: when user visits "/", run the function below
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload-csv")
async def upload_function(file: UploadFile):
    # assign contents as the variable to read the uploaded file to
    # file is of class type UploadFile which has a method called .read(), used to read the contents of that file 
    # await is to free the CPU for other computation for other users while the reading of that file is happening. For asycnhronous computation. 
    content = await file.read() # get the file content as bytes
    text_content = content.decode('utf-8') # convert bytes to string
    csv_file = io.StringIO(text_content) # convert strings to csv
    reader = csv.reader(csv_file)
    
    # Store the header seperately
    header = next(reader)

    # Initialize list for appending rows
    data = []

    # Intialize varible to count number if rows
    row_count = 0

    # append upto first 20 rows
    for row in reader:
        if row_count >= 20:
            break
        else:
            data.append(row)
            row_count += 1

    # create dict variable
    my_dict = {}

    # store header in key called 'header'
    my_dict["headers"] = header

    # store data, list of lists of strings, as the value for the key 'rows'
    my_dict["rows"] = data

    return my_dict



# If you run python main.py directly from the terminal
    # This statement will run
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)