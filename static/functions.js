// function to update time on each page
function updateTime() {
    const date = new Date();
    const dateString = date.toLocaleDateString("en-US", {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric"
    });
        document.getElementById("time").innerHTML = date.toLocaleTimeString("en-US", {
        hour12: false,
        hour: "numeric",
        minute: "2-digit",
        second: "2-digit"
    });
    document.getElementById("date").innerHTML = dateString;
}


// Function to expand the steps on how to login
function expand (){
    const content = document.getElementById('explanation');
    content.hidden = content.hidden === false;
}


//  change the class of current page link in nav bar to active
function setActive() {
    let aObj = document.getElementById('top-nav').getElementsByTagName('a');
    for(let i=0;i<aObj.length;i++) {
        if(document.location.href.indexOf(aObj[i].href)>=0) {
        aObj[i].className='active';
        }
    }
}


// Check new passwords for pattern and length as well as similarity in the confirmation of password
function check_passwords () {
    const password = document.getElementById("password");
    const confirmed = document.getElementById("confirm-password");
    const submitButton = document.getElementById("submit");
    const unmatched = document.getElementById("matching-password");
    const pattern = document.getElementById("password-pattern");
    const upperRegex = /[A-Z]/;
    const lowerRegex = /[a-z]/;
    const specialRegex = /[^\w\s]/;
    const numberRegex = /\d/;
    const lengthRegex = /^.{8,}$/;


    password.addEventListener("input", function () {
        document.getElementById("upper").checked = upperRegex.test(password.value);
        document.getElementById("lower").checked = lowerRegex.test(password.value);
        document.getElementById("special-character").checked = specialRegex.test(password.value);
        document.getElementById("number").checked = numberRegex.test(password.value);
        document.getElementById("length").checked = lengthRegex.test(password.value);
        const checkboxes = document.querySelectorAll('input[type="checkbox"]');
        let allChecked = true;
        checkboxes.forEach(function(checkbox) {
            if (!checkbox.checked) {
                allChecked = false;
            }
        });
        confirmed.disabled = !allChecked;
    });


    //listen to changes in the inputs
    password.addEventListener('input', checkValues);
    confirmed.addEventListener('input', checkValues);

    function checkValues() {
        const primaryValue = password.value;
        const secondaryValue = confirmed.value;
        pattern.hidden = false;
        if (primaryValue === secondaryValue){
            confirmed.style.borderColor = 'green';
            unmatched.hidden = true;
            submitButton.disabled = false;
        } else {
            confirmed.style.borderColor = 'red';
            unmatched.hidden = false;
            submitButton.disabled = true;
        }
    }
}

// Functions to deactivate/ reactivate a clerk
// Takes the checked clerk id, asks for a confirmation message and sends the data to flask for deactivation/ reactivation
function deactivate(){
    const action = "Deactivate";
    document.getElementById('deactivate').addEventListener('click', function () {
        event.preventDefault();
        select(action);
    });
}

function reactivate() {
    const action = "Reactivate";
    document.getElementById('reactivate').addEventListener('click', function () {
        event.preventDefault();
        select(action);
    });
}

function select(action) {
    const confirmBox = document.createElement("div");
    confirmBox.id = "confirm-box";

    const checkboxes = document.querySelectorAll('input[type="checkbox"]')
    checkboxes.forEach(function (checkbox) {
        if (checkbox.checked) {
            const selected_id = checkbox.value;
            confirmBox.innerHTML = "<p>Are you sure you want to " + action + " " + checkbox.value + "</p><button id='confirm-yes'>Yes</button><button id='confirm-no'>No</button>";
            document.body.appendChild(confirmBox);
            const confirmYes = document.getElementById("confirm-yes");
            const confirmNo = document.getElementById("confirm-no");
            confirmYes.addEventListener("click", function() {
                fetch('/deactivate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({value: selected_id})
                })
                .then(function(response) {
                      return response.text(); // Get the response text
                })
                    .then(function(text) {
                        // create a new div element
                        const alertBox = document.createElement("div");
                        alertBox.setAttribute("class", "custom-alert");

                        // add a message to the alert box
                        const message = document.createElement("p");
                        message.textContent = text;
                        alertBox.appendChild(message);

                        // add a close button to the alert box
                        const closeButton = document.createElement("button");
                        closeButton.setAttribute("class", "close-button");
                        closeButton.textContent = "OK";
                        closeButton.addEventListener("click", function() {
                          alertBox.style.display = "none";
                          window.location.reload();
                        });
                        alertBox.appendChild(closeButton);

                        // add the alert box to the body of the page
                        document.body.appendChild(alertBox);

                })
                    .catch(function(error) {
                        console.error('Error:', error);
                });
                document.body.removeChild(confirmBox);
            });
            confirmNo.addEventListener("click", function() {
                document.body.removeChild(confirmBox);
            });
        }
    });
}



// Function to add years in a select container for payroll generation
function addYear() {
    const values = document.getElementById('year');
    for (let year = 2020; year < 2040; year++) {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year;
        values.appendChild(option);
    }
}


// Reveal password as plain text when typing
function showPassword () {
    const checkbox = document.getElementById('visibility');
    const password = document.getElementById('password');
    if (checkbox.checked) {
        password.type = 'text';
    } else {
        password.type = 'password';
    }
}


// Show and hide logout button on click of user
function logout () {
    const user = document.getElementById('logged-user');
    const signout = document.getElementById('signout');
    user.addEventListener('click', function() {
       signout.hidden = signout.hidden === false;
    });
}


// scroll to top
function scroller () {
    const scrollButton = document.getElementById('scroll');
    const overlay = document.getElementById('overlay');
    overlay.addEventListener('scroll', function () {
        scrollButton.style.display = "block";
    });
}