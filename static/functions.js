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


function expand (){
    const content = document.getElementById('explanation');
    content.hidden = content.hidden === false;
}

function setActive() {
    let aObj = document.getElementById('top-nav').getElementsByTagName('a');
    for(let i=0;i<aObj.length;i++) {
        if(document.location.href.indexOf(aObj[i].href)>=0) {
        aObj[i].className='active';
        }
    }
}


function check_passwords () {
    const password = document.getElementById("password");
    const confirmed = document.getElementById("confirm-password");
    const submitButton = document.getElementById("register");
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

function select() {
    document.getElementById('deactivate').addEventListener('click', function() {
        const checkboxes = document.querySelectorAll('input[type="checkbox"]')
        checkboxes.forEach(function (checkbox) {
            if (checkbox.checked) {
                const selected_id = checkbox.value;
                if (confirm("Remove Clerk " + selected_id)) {
                    fetch('/deactivate', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({value: selected_id})
                    })
                    .then(function(response) {
                        return response.text();
                      })
                    .then(function(html) {
                        const parser = new DOMParser();
                        const doc = parser.parseFromString(html, 'text/html');
                        const element = doc.querySelector('body'); // Change this to select the desired element from the HTML
                        console.log('Received HTML:', element);
                        // do something with the rendered HTML...
                      })
                    .catch(function(error) {
                        console.error('Error:', error);
                      });
                }
            }
        });
    });
}