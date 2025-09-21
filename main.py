# FastAPI: receives requests and handles logic
import csv
import io
import os
from fastapi import FastAPI, Request, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from openai import OpenAI
import openAPIsecrets

all_rows = []

# FastAPI() cre`ates a new web application instance
# This web server/app handles HTTP requests and also creates a router which handles the function to call based on the endpoint of the url "/account" or "/homepage" etc. 
# Based on the endpoint and the corresponding function associated with that endpoint, we can route requests via GET/POST 
# This web app instance is accessed and called through "app" variable 
app = FastAPI(title="whisperData: Natural Language Data Transformation")

# hide the open ai key in secrets.py. A .gitignored python file
client = OpenAI(api_key=openAPIsecrets.OPENAI_API_KEY)

# Format the data from all_rows for the AI
def formatDataforAI(all_rows):
    headers = all_rows[0]
    rows = all_rows[1:]

    # Create formatted text
    formatted_text = "Headers: " + ", ".join(headers) + "\n"
    formatted_text += "Data:\n"

    for row in rows:
        formatted_text += ", ".join(row) + "\n"
    
    return formatted_text


# function to call the openAI
def askAI(command, all_rows):

    # format the data for the AI
    formattedData = formatDataforAI(all_rows)

    # Create the prompt
    prompt = f"""Here is my CSV data:
    {formattedData}

    User command: {command}

    Please transform the data according to the command and return it in the same format above (Headers: ... followed by Data: ...),
    then add an explanation starting with 'Explanation:' describing what you did."""

    response = client.chat.completions.create(
        model = "gpt-3.5-turbo",
        messages = [{"role": "user", "content": prompt}]
    )

    # store response in variable
    ai_response = response.choices[0].message.content

    # Parse the response
    parts = ai_response.split("Explanation:")
    data_part = parts[0].strip()
    # if there are more than 1 parts - both data and explanantion, then explanaation_part is the second index at 1st position
    if len(parts) > 1:
        explanation_part = parts[1].strip()
    # if parts =< 1, then only data was returned, then explanation_part - what is printed in explanantion text box in HTML is the string "No explanation ..."
    else:
        explanation_part = "No explanation provided"

    return data_part, explanation_part


# app.mount(): tells FastAPI to serve files from a directory
# "/scripts": serve the files from scripts folder when the the url path "/scripts" is executed
# StaticFiles(directory="scripts"): tells FastAPI which folder to serve the files from
app.mount("/static/scripts", StaticFiles(directory="static/scripts"), name="scripts")

# This tells jinja that the html files are in the templates folder
templates = Jinja2Templates(directory="templates")

# Decorator: when user visits "/", run the function below
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload-csv")
# UploadFile is the webstandard format for file uploads 
async def upload_function(file: UploadFile):
    # Esnure python references the global all_rows variable 
    global all_rows 

    # assign contents as the variable to read the uploaded file to
    # file is of class type UploadFile which has a method called .read(), used to read the contents of that file 
    # await is to free the CPU for other computation for other users while the reading of that file is happening. For asycnhronous computation. 
    content = await file.read() # get the file content as bytes
    text_content = content.decode('utf-8') # convert bytes to string
    csv_file = io.StringIO(text_content) # convert strings to csv
    reader = csv.reader(csv_file)

    all_rows = list(reader)
    
    # Store the header seperately
    header = all_rows[0]

    # Initialize list for appending rows
    data = []

    # append upto first 20 rows. check if totals rows < 20
    for i in range(1, min(21, len(all_rows))):
        data.append(all_rows[i])

    # create dict variable
    my_dict = {}

    # store header in key called 'header'
    my_dict["headers"] = header

    # store data, list of lists of strings, as the value for the key 'rows'
    my_dict["rows"] = data

    return my_dict


@app.post("/transform-data")
async def transform_data(command: str):
    global all_rows
    
    # Call AI
    aiResponse_data, aiResponse_explanation = askAI(command, all_rows)
    
    # Parse the AI response back into list format
    lines = aiResponse_data.strip().split('\n')
    
    # Extract headers (remove "Headers: " prefix)
    header_line = lines[0].replace("Headers: ", "")
    headers = []
    for h in header_line.split(','):
        headers.append(h.strip())
    
    # Extract data rows (skip "Headers:" line and "Data:" line)
    data_rows = []
    for line in lines[2:]:  # Skip first two lines (Headers and "Data:")
        if line.strip():  # Skip empty lines
            row = []
            for cell in line.split(','):
                row.append(cell.strip())
            data_rows.append(row)
    
    # Update global all_rows with transformed data
    all_rows = [headers] + data_rows
    
    # Prepare response for JavaScript (first 20 rows + explanation)
    display_rows = data_rows[:20]  # First 20 data rows for display
    
    response_dict = {
        "headers": headers,
        "rows": display_rows,
        "explanation": aiResponse_explanation
    }
    
    return response_dict



# If you run python main.py directly from the terminal
    # This statement will run
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)