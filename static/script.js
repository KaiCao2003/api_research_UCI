// Function to update the correct time
function updateCorrectTime() {
    var date = new Date();
    var correctTimeElement = document.getElementById("currentTime");
    correctTimeElement.textContent = "Current Time: " + date.toLocaleTimeString();
}

// Function to update the results
function updateResults(course_title, sectionTime, max_capacity, total_enrolled, course_status, whether_full) {
    console.log(course_title, max_capacity, total_enrolled, whether_full)
    var resultsElement = document.getElementById("results");
    resultsElement.innerHTML =  "<p>Course Title: " + course_title + "</p>" +
                                "<p>Section Time: " + sectionTime + "</p>" +
                                "<p>Max Capacity: " + max_capacity + "</p>" +
                                "<p>Total Enrolled: " + total_enrolled + "</p>" +
                                "<p>Course Status: " + course_status + "</p>" +
                                "<p>Whether Full: " + whether_full + "</p>";

    if (whether_full === true ) {
        document.getElementById('code').value = document.getElementById('content').value;
        document.getElementById('subscribeForm').style.display = 'block';
    } else {
        document.getElementById('subscribeForm').style.display = 'none';
    }
}

// Function to send the content to the server
function sendRequest() {
    var content = document.getElementById("content").value;
    $.post("/send", {content: content}, function(response) {
        updateResults(response.course_title, response.sectionTime, response.max_capacity, response.total_enrolled, response.course_status, response.whether_full);
    });
}

// Event listener for the send button
document.getElementById("sendBtn").addEventListener("click", function() {
    sendRequest();
});

// Update correct time every second
setInterval(updateCorrectTime, 1000);
