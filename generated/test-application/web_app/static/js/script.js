```javascript
// Import the necessary dependencies
import { generate_password } from "../../password_generator.py";
import { User } from "../../user.py";
import { Account } from "../../account.py";

// Get the necessary elements from the HTML
const passwordField = document.getElementById("passwordField");
const generateButton = document.getElementById("generateButton");
const accountForm = document.getElementById("accountForm");

// Add an event listener to generate a password when the generate button is clicked
generateButton.addEventListener("click", () => {
  const newPassword = generate_password();
  passwordField.value = newPassword;
});

// Add an event listener to create a new account
accountForm.addEventListener("submit", (event) => {
  event.preventDefault();
  
  // Get the values from the form
  const username = accountForm.elements["username"].value;
  const password = passwordField.value;
  
  // Create a new account with the username and password
  const newAccount = new Account(username, password);
  
  // Redirect to the main page
  window.location.href = "/";
});
```