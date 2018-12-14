function sendSignUpData() {
    var formElement = document.getElementById("register-form");
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var jsonResponse = JSON.parse(this.response);
            M.toast({html: 'SignUp is Successful', class: "rounded"});
        }
    };
    xhttp.open("POST", "/register");
    xhttp.send(new FormData(formElement));
}