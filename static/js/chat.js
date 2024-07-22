$(document).ready(function() {
    var socket = io('/chat');

    $('#message-form').submit(function(event) {
        event.preventDefault();
        var message = $('#message-input').val();
        socket.send(message);
        $('#message-input').val('');
        return false;
    });

    socket.on('message', function(msg) {
        $('#messages').append($('<div>').text(msg));
    });

    $.getJSON('/messages', function(data) {
        let messages = data.messages
        let current = data.current_user

        messages.forEach(function(messages) {
            if (messages.user_id == current) {
                $('#messages').append($('<div id="user_message">').text(`${current}: ${messages.content}`))
            }
            else {
                $('#messages').append($('<div>').text(`${current}: ${messages.content}`))
            }
        }) 
    })

});

