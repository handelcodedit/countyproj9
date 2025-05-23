    // Function to sanitize input (removes < and > to prevent XSS)
function sanitizeInput(input) {
    return input.replace(/[<>]/g, "");
}




// Function to validate date format (YYYY-MM-DD)
function validateDateOfBirth(dob) {
    return /^\d{4}-\d{2}-\d{2}$/.test(dob);
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
    sanitizeFormInputs("editProfileForm"); // Sanitize before validation

    // Required fields
    const requiredFields = ['username', 'phone', 'fname', 'lname', 'dob', 'address', 'achievements', 'occupation', 'marital_status', 'education_level'];
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
   
    
    const dob = document.getElementById("dob").value.trim();
   
    const phone = document.getElementById("phone").value.trim();

   

    if (!validateDateOfBirth(dob)) {
        displayError('dob', 'Use format YYYY-MM-DD');
        isValid = false;
    } else {
        removeError('dob');
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
        document.getElementById("editProfileForm").submit(); // Submit form if valid
    }
}

// Attach validation to registration form
document.addEventListener("DOMContentLoaded", function () {
    const registrationForm = document.getElementById("editProfileForm");
    if (registrationForm) {
        registrationForm.addEventListener("submit", function (event) {
            validateForm(event);
        });
    }
});