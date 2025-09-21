// Select the form which initiates the "/upload-csv" endpoint
const uploadForm = document.getElementById("submit")

const csvTable = document.getElementById("csvTable")
csvTable.innerHTML = '';

// for the form submission, when the mouse is clicked, intercept the default event 
uploadForm.addEventListener('submit', function(submit) {
    submit.preventDefault();

    // select the place in the form on index.html where the file is stored, before subission
    const file = document.getElementById("csvFile")
    // retrieve the file from the form
    const csvfile = file.files[0]
    if (!csvfile) return;

    // FormData mimics the submission of the file with encoding type/enctype="multipart/form-data" to the main.py UploadFile object parameter
    const formData = new FormData();
    // FastAPI in main.py expects the input parameter to be called "file"
    formData.append('file', csvfile)

    // identify the div with id = "csvTable" in HTML. This is where the table will go.
    const csvTable = document.getElementById("csvTable")
    
    // Clear the table immediately when upload starts
    csvTable.innerHTML = '';

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
        
        // Clear again just to be absolutely sure
        csvTable.innerHTML = '';
        
        // Create a table element dynamically within the HTML <table>
        const table = document.createElement("table")
        
        // Create the header file 
        // access the headers of the returned JSON data from main.py "/upload-csv"
        const headers = jsonData["headers"]

        const theadElement = document.createElement("thead")

        const trElement = document.createElement("tr")

        for (const element of headers)
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
        const rows = jsonData["rows"]

        const tbodyElement = document.createElement("tbody")

        for (const row of rows)
        {
            // create a tr element 
            const bodyRowElement = document.createElement("tr")
            
            for (const cell of row)
            {
                // create a td element
                const tdElement = document.createElement("td")
                
                // add the row data content into the tdElement
                tdElement.textContent = cell;
                
                // append each td element into the row
                bodyRowElement.append(tdElement)
            }

            // append each row data into the table
            tbodyElement.append(bodyRowElement)
        }
        table.append(tbodyElement)

        // Replace the entire content instead of appending
        csvTable.appendChild(table)
    })
})