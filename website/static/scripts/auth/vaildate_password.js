$(document).ready(function(){
  // Checking that the password is not 8 charcters minimum
  // Function to validate password length
  function validatePassword() {
    let password = $('#Password').val();
     if (password.length < 8) {
       $('#msg1').html("Password must be at least 8 characters long").css("color", "red");
     } else {
       $('#msg1').html("");
     }
  }

  $('#Password').on('input', validatePassword);
  
  $("#ConfirmPassword").keyup(function(){
    if ($("#Password").val() != $("#ConfirmPassword").val()) {
      $("#msg").html("Password do not match").css("color","red");
    }else{
      $("#msg").html("Password matched").css("color","green");
    }
  });
});
