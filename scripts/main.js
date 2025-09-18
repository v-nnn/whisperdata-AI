// Select the form which initiates the "/upload-csv" endpoint
const uploadButton = document.getElementById("submit")


// for the form submission, when the mouse is clicked, intercept the default event 
uploadButton.addEventListener('submit', function(submit) {
    submit.preventDefault();
})