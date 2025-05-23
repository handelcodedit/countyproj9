// Function to validate confirm password
function validateConfirmPassword() {
    const password = document.getElementById("password").value.trim();
    const confirmPassword = document.getElementById("confirm_password").value.trim();
    let isValid = true;

    if (confirmPassword === '') {
        displayError('confirm_password', 'Confirm Password is required');
        isValid = false;
    } else if (password !== confirmPassword) {
        displayError('confirm_password', 'Passwords do not match');
        isValid = false;
    } else {
        removeError('confirm_password');
    }

    return isValid;
}

// Function to display error messages
function displayError(inputId, errorMessage) {
    let inputElement = document.getElementById(inputId);
    let errorElementId = inputId + '-error';
    let errorElement = document.getElementById(errorElementId);

    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.id = errorElementId;
        errorElement.style.color = 'red';
        errorElement.style.marginTop = '5px';
        inputElement.parentNode.insertBefore(errorElement, inputElement.nextSibling);
    }

    errorElement.textContent = errorMessage;
}

// Function to remove error messages
function removeError(inputId) {
    let errorElement = document.getElementById(inputId + '-error');
    if (errorElement) {
        errorElement.remove();
    }
}

// Attach event listener to register button
document.addEventListener("DOMContentLoaded", function () {
    const registerButton = document.getElementById("register_button");
    if (registerButton) {
        registerButton.addEventListener("click", function (event) {
            if (!validateConfirmPassword()) {
                event.preventDefault(); // Prevent form submission if validation fails
            }
        });
    }
});
