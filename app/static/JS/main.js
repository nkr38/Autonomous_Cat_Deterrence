document.getElementById("serialNumButton").addEventListener("click", function(){
    checkLogin();
})

function checkLogin(){
    input_number = $('#loginInput').val();
    data = {'serial_number': input_number}

    $.ajax({
        url: '/login',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(data),
        success: function(response) {
            window.location.href = "/monitor";
        },
        error: function(xhr, status, error) {
            const errorMsg = 'Error: Invalid Serial Number'
            console.error(errorMsg);
            $('#errorMessage').text(errorMsg);
            $('#errorModal').show();
        }
    });
}

$('.close').click(function() {
    $('#errorModal').hide();
});