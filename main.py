# FastAPI: receives requests and handles logic
import csv
import io
import os
from fastapi import FastAPI, Request, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
import uvicorn
import anthropic
# import anthropicAPIsecret

from pydantic import BaseModel

class TransformRequest(BaseModel):
    command: str

all_rows = []

# FastAPI() cre`ates a new web application instance
# This web server/app handles HTTP requests and also creates a router which handles the function to call based on the endpoint of the url "/account" or "/homepage" etc. 
# Based on the endpoint and the corresponding function associated with that endpoint, we can route requests via GET/POST 
# This web app instance is accessed and called through "app" variable 
app = FastAPI(title="whisperData: Natural Language Data Transformation")

# hide the Anthropic key in secrets.py. A .gitignored python file
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
#client = anthropic.Anthropic(api_key=anthropicAPIsecret.ANTHROPIC_API_KEY)

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
    formatted_data = formatDataforAI(all_rows)
    
    prompt = f"""Here is my CSV data:
    {formatted_data}

    User command: {command}

    INSTRUCTIONS:
    1. First, determine if this is a QUESTION about the data or a TRANSFORMATION command:
    - QUESTIONS: "How many rows?", "What's the average?", "Show me statistics", "What columns exist?"
    - TRANSFORMATIONS: "Sort by age", "Filter rows where...", "Add a column", "Remove duplicates"

    2. If it's a QUESTION:
    - Return the ORIGINAL data unchanged
    - Answer the question in the explanation

    3. If it's a TRANSFORMATION:
    - Apply the transformation
    - When sorting numerical columns, treat them as numbers (2, 10, 100 not 10, 100, 2)
    - Return the modified data

    REQUIRED OUTPUT FORMAT (follow EXACTLY):
    Headers: [comma-separated header names]
    Data:
    [each row on new line, comma-separated values]

    Explanation: [Your answer or description of what you did]

    CRITICAL RULES:
    - Headers line must start with exactly "Headers: "
    - Data section must start with exactly "Data:"
    - Each data row must be comma-separated values only
    - Explanation must start with exactly "Explanation: "
    - If question about data, return original data unchanged
    - Never add extra formatting, quotes, or markdown
    - Never truncate data unless specifically asked

    EXAMPLES:

    Example 1 (Question):
    User: "How many customers are from New York?"
    Headers: Name, City, Age
    Data:
    John, NYC, 25
    Jane, Boston, 30
    Bob, NYC, 28
    Explanation: There are 2 customers from New York (NYC): John and Bob.

    Example 2 (Transformation):
    User: "Sort by age ascending"
    Headers: Name, City, Age
    Data:
    John, NYC, 25
    Bob, NYC, 28
    Jane, Boston, 30
    Explanation: Sorted the data by age in ascending order (25, 28, 30).

    Now process the user command above following these rules exactly."""

    response = client.messages.create(
        #model="claude-sonnet-4-20250514",
        model="claude-3-7-sonnet-20250219",  
        #model="claude-3-5-haiku-20241022",  
        max_tokens=2000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    ai_response = response.content[0].text
    
    # Parse the response (same as before)
    parts = ai_response.split("Explanation:")
    data_part = parts[0].strip()
    explanation_part = parts[1].strip() if len(parts) > 1 else "No explanation provided"
    
    return data_part, explanation_part

# Convert the all_rows data into a downloadable csv file
def convert_to_csv(all_rows):
    csv_lines = []
    for row in all_rows:
        # Join each row's items with commas
        csv_line = ",".join(row)
        csv_lines.append(csv_line)
    
    # Join all lines with newlines
    csv_content = "\n".join(csv_lines)
    return csv_content


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
async def transform_data(request: TransformRequest):
    global all_rows

    command = request.command
    
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


@app.get("/download-csv")
async def download_csv():
    global all_rows

    # Check if data exists
    if not all_rows:
        raise HTTPException(status_code=400, detail="No data available to download. Please upload a CSV file first.")
    
    # Convert to CSV format
    csv_content = convert_to_csv(all_rows)
    
    # Return as downloadable file
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transformed_data.csv",
                 "Content-Type": "text/csv"}
    )


# If you run python main.py directly from the terminal
    # This statement will run
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)