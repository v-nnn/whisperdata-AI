// Select the form which initiates the "/upload-csv" endpoint
const uploadButton = document.getElementById("submit")


// for the form submission, when the mouse is clicked, intercept the default event 
uploadButton.addEventListener('submit', function(submit) {
    submit.preventDefault();

    // select the place in the form on index.html where the file is stored, before subission
    const file = document.getElementById("file")
    // retrieve the file from the form
    csvfile = file.files[0]

    // FormData mimics the submission of the file with encoding type/enctype="multipart/form-data" to the main.py UploadFile object parameter
    const formData = new FormData();
    // FastAPI in main.py expects the input parameter to be called "file"
    formData.append('file', csvfile)

    // fetch() makes a request to an endpoint and fetches the response
    // sends the csvfile in the formData to the main.py upload-csv endpoint and retrieves the response (the file in JSON format)
    fetch('/upload-csv' {
        method: 'POST',
        body: formData
    })

    // Access the return value of fetch() - what /upload-csv main.py function returns to the fetch() call
    // wait for the fetch() to return the JSON formatted csvfile which main.py /upload-csv endpoint returns
    .then
    

})



// ✅ Intercept form submission
// ❓ Get the file data from the form
// ❓ Send it to your endpoint
// ❓ Receive the JSON response
// ❓ Create an HTML table