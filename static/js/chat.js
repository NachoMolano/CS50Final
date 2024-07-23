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
        $('#messages').append($(`
            <div class="message" id="user_message">
                <div class="message-box">
                    <div class="message-content">
                        ${msg} 
                    </div>
                    <div class="message-timestamp">
                        now
                    </div>
                </div>
            </div>
            `))
    });

    $.getJSON('/messages', function(data) {
        let messages = data.messages
        let current = data.current_user

        messages.forEach(function(messages) {
            if (messages.user_id == current) {
                $('#messages').append($(`
                    <div class="message" id="user_message">
                        <div class="message-box">
                            <div class="message-content">
                                ${messages.content} 
                            </div>
                            <div class="message-timestamp">
                                ${messages.timestamp.slice(11, 16)}
                            </div>
                        </div>
                    </div>
                    `))
            }
            else {
                $('#messages').append($(`
                    <div class="message" id="other_message">
                        <div class="message-box">
                            <div class="message-header"> 
                            ${messages.username}
                            </div>
                            <div class="message-content">
                                ${messages.content} 
                            </div>
                            <div class="message-timestamp">
                                ${messages.timestamp.slice(11, 16)}
                            </div>
                        </div>
                    </div>
                    `))
            }
        }) 
    })

});

