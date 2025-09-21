console.log("JavaScript file loaded");

// Select the form which initiates the "/upload-csv" endpoint
const uploadButton = document.getElementById("submit")


// for the form submission, when the mouse is clicked, intercept the default event 
uploadButton.addEventListener('submit', function(submit) {
    submit.preventDefault();

    console.log("Form submission intercepted");

    // select the place in the form on index.html where the file is stored, before subission
    const file = document.getElementById("csvFile")
    // retrieve the file from the form
    csvfile = file.files[0]

    // FormData mimics the submission of the file with encoding type/enctype="multipart/form-data" to the main.py UploadFile object parameter
    const formData = new FormData();
    // FastAPI in main.py expects the input parameter to be called "file"
    formData.append('file', csvfile)

    // fetch() makes a request to an endpoint and fetches the response
    // sends the csvfile in the formData to the main.py upload-csv endpoint and retrieves the response (the file in JSON format)
    fetch('/upload-csv', {
        method: 'POST',
        body: formData
    })

    // Access the return value of fetch() - what /upload-csv main.py function returns to the fetch() call
    // wait for the fetch() to return the JSON formatted csvfile which main.py /upload-csv endpoint returns
    // JSON is returned from main.py /upload-csv function, so we must specify to treat the response as JSON data format
    .then(response => response.json())

    .then(jsonData => {
        // identify the div with id = "csvTable" in HTML. This is where the table will go.
        const csvTable = document.getElementById("csvTable")
        
        // Create a table element dynamically within the HTML <table>
        table = document.createElement("table")
        // Create the header file 

        // access the headers of the returned JSON data from main.py "/upload-csv"
        headers = jsonData["headers"]

        theadElement = document.createElement("thead")

        trElement = document.createElement("tr")

        for (element of headers)
        {
            const thElement = document.createElement("th")
            // add element into th
            thElement.textContent = element;
            
            // append each head cell into a row
            trElement.append(thElement)
        }

        // append the header row into the thead 
        theadElement.append(trElement)

        // append the header into the table
        table.append(theadElement)

        // access the rows from the JSON from main.py "/upload-csv" endpoint
        rows = jsonData["rows"]

        tbodyElement = document.createElement("tbody")

        for (row of rows)
        {
            // create a tr element 
            trElement = document.createElement("tr")
            
            for (cell of row)
            {
                // create a td element
                tdElement = document.createElement("td")
                
                // add the row data content into the tdElement
                tdElement.textContent = cell;
                
                // append each td element into the row
                trElement.append(tdElement)
            }

            // append each row data into the table
            tbodyElement.append(trElement)
        }
        table.append(tbodyElement)

        csvTable.append(table)
    })
})


// ✅ Intercept form submission
// ❓ Get the file data from the form
// ❓ Send it to your endpoint
// ❓ Receive the JSON response
// ❓ Create an HTML table