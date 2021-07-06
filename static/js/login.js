var username = document.querySelector("#username");
var password = document.querySelector("#password");

function checkUsername() {
    if(!username.value) {
            document.querySelector(".error").style.display = "block";
        document.querySelector(".error").innerHTML = "Enter Username";
        document.querySelector("#submit").disabled = true;
    }
    else {
        document.querySelector(".error").style.display = "none";
        document.querySelector("#submit").disabled = false;
    }
}

function checkPass() {
    password.addEventListener('focusout', function(){
        if(!password.value) {
            document.querySelector(".error").style.display = "block";
            document.querySelector(".error").innerHTML = "Enter Password";
            document.querySelector("#submit").disabled = true;
        }
        else if(password.value.length < 8) {
            document.querySelector(".error").style.display = "block";
            document.querySelector(".error").innerHTML = "Password must be more than 8 characters";
            document.querySelector("#submit").disabled = true;
        }
        else {
            document.querySelector(".error").style.display = "none";
            document.querySelector("#submit").disabled = false;
        }
    })
}
    
username.addEventListener('focusout', checkUsername);
password.addEventListener('focusin', checkPass);