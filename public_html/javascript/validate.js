// Function to sanitize input (removes < and > to prevent XSS)
function sanitizeInput(input) {
    return input.replace(/[<>]/g, "");
}

// Function to validate email format
function validateEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// Function to validate password format
function validatePassword(password) {
    const hasLetter = /[a-zA-Z]/.test(password);
    const hasNumber = /\d/.test(password);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);
    return password.length >= 8 && hasLetter && hasNumber && hasSpecialChar;
}

// Function to validate date format (YYYY-MM-DD)
function validateDateOfBirth(dob) {
    return /^\d{4}-\d{2}-\d{2}$/.test(dob);
}

// Function to validate ID format (exactly 8 numeric characters)
function validateID(id) {
    return /^\d{8}$/.test(id);
}

// Function to validate Phone format (exactly 10 numeric characters)
function validatePhone(phone) {
    return /^\d{10}$/.test(phone);
}

// Function to validate dropdown selection
function validateDropdown(fieldId) {
    return document.getElementById(fieldId).value.trim() !== '';
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

// Function to sanitize all form inputs
function sanitizeFormInputs(formId) {
    const form = document.getElementById(formId);
    if (form) {
        const inputs = form.querySelectorAll("input, textarea");
        inputs.forEach(input => {
            input.value = sanitizeInput(input.value.trim());
        });
    }
}

// Function to validate and submit registration form
function validateForm(event) {
    let isValid = true;
    sanitizeFormInputs("registrationForm"); // Sanitize before validation

    // Required fields
    const requiredFields = ['id', 'username', 'email','phone', 'password', 'con_password', 'fname', 'lname', 'dob', 'address', 'achievements', 'occupation', 'marital_status', 'education_level'];
    requiredFields.forEach(field => {
        let value = document.getElementById(field).value.trim();
        if (value === '') {
            displayError(field, 'Required');
            isValid = false;
        } else {
            removeError(field);
        }
    });

    // Specific field validations
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();
    const confirmPassword = document.getElementById("con_password").value.trim();
    const dob = document.getElementById("dob").value.trim();
    const id = document.getElementById("id").value.trim();
    const phone = document.getElementById("phone").value.trim();

    if (!validateEmail(email)) {
        displayError('email', 'Invalid email format');
        isValid = false;
    } else {
        removeError('email');
    }

    if (!validatePassword(password)) {
        displayError('password', 'Password must be 8+ characters, contain letters, numbers, and a special character.');
        isValid = false;
    } else {
        removeError('password');
    }

    if (password !== confirmPassword) {
        displayError('con_password', 'Passwords do not match');
        isValid = false;
    } else {
        removeError('con_password');
    }

    if (!validateDateOfBirth(dob)) {
        displayError('dob', 'Use format YYYY-MM-DD');
        isValid = false;
    } else {
        removeError('dob');
    }

    if (!validateID(id)) {
        displayError('id', 'ID must be exactly 8 digits.');
        isValid = false;
    } else {
        removeError('id');
    }
    if (!validatePhone(phone)) {
        displayError('phone', 'Phone must be exactly 10 digits.');
        isValid = false;
    } else {
        removeError('phone');
    }

    // Validate dropdowns
    const dropdowns = ['county_id', 'role', 'gender', 'ward'];
    dropdowns.forEach(dropdown => {
        if (!validateDropdown(dropdown)) {
            displayError(dropdown, 'Please select an option.');
            isValid = false;
        } else {
            removeError(dropdown);
        }
    });

    if (!isValid) {
        event.preventDefault(); // Prevent submission only if validation fails
    } else {
        document.getElementById("registrationForm").submit(); // Submit form if valid
    }
}

// Attach validation to registration form
document.addEventListener("DOMContentLoaded", function () {
    const registrationForm = document.getElementById("registrationForm");
    if (registrationForm) {
        registrationForm.addEventListener("submit", function (event) {
            validateForm(event);
        });
    }
});

// Function to validate and submit login form
function validateLoginForm(event) {
    let isValid = true;
    sanitizeFormInputs("loginForm"); // Sanitize before validation

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    if (email === '') {
        displayError('email', 'Email is required');
        isValid = false;
    } else if (!validateEmail(email)) {
        displayError('email', 'Invalid email format');
        isValid = false;
    } else {
        removeError('email');
    }

    if (password === '') {
        displayError('password', 'Password is required');
        isValid = false;
    } else {
        removeError('password');
    }

    if (!isValid) {
        event.preventDefault();
    } else {
        document.getElementById("loginForm").submit();
    }
}

// Attach validation to login form
document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("loginForm");
    if (loginForm) {
        loginForm.addEventListener("submit", validateLoginForm);
    }
});

// Function to validate forgot password form
function validateForgotPassForm(event) {
    let isValid = true;
    sanitizeFormInputs("forgotpassForm"); // Sanitize before validation

    const email = document.getElementById("email").value.trim();
    if (email === '') {
        displayError('email', 'Email is required');
        isValid = false;
    } else if (!validateEmail(email)) {
        displayError('email', 'Invalid email format');
        isValid = false;
    } else {
        removeError('email');
    }

    if (!isValid) {
        event.preventDefault();
    } else {
        document.getElementById("forgotpassForm").submit();
    }
}

// Attach validation to forgot password form
document.addEventListener("DOMContentLoaded", function () {
    const forgotPassForm = document.getElementById("forgotpassForm");
    if (forgotPassForm) {
        forgotPassForm.addEventListener("submit", validateForgotPassForm);
    }
});

// Password visibility toggle
document.addEventListener("DOMContentLoaded", function () {
    const passwordField = document.getElementById("password");
    const confirmPasswordField = document.getElementById("con_password");

    if (passwordField) {
        const toggleButton = document.createElement("button");
        toggleButton.textContent = "Show";
        toggleButton.type = "button";
        toggleButton.style.marginLeft = "10px";

        passwordField.parentNode.insertBefore(toggleButton, passwordField.nextSibling);

        toggleButton.addEventListener("click", function () {
            if (passwordField.type === "password") {
                passwordField.setAttribute("type", "text");
                toggleButton.textContent = "Hide";
            } else {
                passwordField.setAttribute("type", "password");
                toggleButton.textContent = "Show";
            }
        });
    }

    if (confirmPasswordField) {
        const toggleButton2 = document.createElement("button");
        toggleButton2.textContent = "Show";
        toggleButton2.type = "button";
        toggleButton2.style.marginLeft = "10px";

        confirmPasswordField.parentNode.insertBefore(toggleButton2, confirmPasswordField.nextSibling);

        toggleButton2.addEventListener("click", function () {
            if (confirmPasswordField.type === "password") {
                confirmPasswordField.setAttribute("type", "text");
                toggleButton2.textContent = "Hide";
            } else {
                confirmPasswordField.setAttribute("type", "password");
                toggleButton2.textContent = "Show";
            }
        });
    }
});