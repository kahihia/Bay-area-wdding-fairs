var apiKey, sessionId, token, notify_session, text_session;

function pushMessage(msg) {
    text_session.signal(
        {
            data: {
                message: msg,
                sender: u,
                receiver: u2
            }
        },
        function (error) {

        }
    );

    notify_session.signal(
        {
            data: {
                notification: n + ' send you a message',
                origin: 'chat',
                target: '/online_message/',
                sender: u,
                receiver: u2
            }
        },
        function (error) {

        }
    );
}

function pushVideoCall() {

}

function initOpentok() {
    $.get('/get_notification_session/?user=' + u2, function (res) {
        res = JSON.parse(res);
        apiKey = res.apiKey;
        sessionId = res.sessionId;
        token = res.token;
        notify_session = OT.initSession(apiKey, sessionId);

        notify_session.on("signal", function(event) {

        });

        notify_session.connect(token, function(error) {

        });
    });

    $.get('/get_tchat_session/?user=' + u2, function(res) {
        res = JSON.parse(res);
        apiKey = res.apiKey;
        sessionId = res.sessionId;
        token = res.token;
        text_session = OT.initSession(apiKey, sessionId);

        text_session.on("signal", function(event) {

        });

        text_session.connect(token, function(error) {

        });

        $('#msgForm').on('submit', function (event) {
            event.preventDefault();
            msg = $('#id_message').val();

            $.ajax({
                url: '/put_tchat_data/',
                type: 'POST',
                data: {
                    'message': msg,
                    'user': u2
                },
                success: function (response) {
                    if (response.indexOf('Error') > -1) {
                        alert(response);
                    }
                    if (response.indexOf('Error') < 0) {
                        pushMessage(msg);

                        // Update credits display.
                        count = +$('#remCredits').text();
                        count--;
                        $('#remCredits').text(count);
                        countHead = +$('#credits').text();
                        countHead--;
                        $('#credits').text(countHead);

                    }
                }
            });

            $('#id_message').val('');
        });
    });
}

function setProfileStatus() {
    var id = $('#profileStatus').attr('data-id');
    $.ajax({
        url: '/is_online/?user=' + id,
        type: 'GET',
        dataType: 'json'
    }).done(function (response) {
        if (response['is_online']) {
            $('#profileStatus').text('Online');
        }
        else {
            $('#profileStatus').text('Offline');
        }
    });
}

$(document).ready(function() {
    if (!(navigator.userAgent.indexOf('Safari') != -1 && navigator.userAgent.indexOf('Chrome') == -1)) {
        initOpentok();
    }

    $('#videoCallBtn').on('click', function (event) {
        notify_session.signal(
            {
                data: {
                    notification: n + ' is making a video call',
                    origin: 'video',
                    target: '/online_message/?source=' + u,
                    sender: u,
                    senderName: n,
                    receiver: u2
                }
            },
            function (error) {

            }
        );
        window.location.href = '/online_message/?source=' + u2;
    });

    setInterval(setProfileStatus, 45000);

    $('#msgSendBtn').on('click', function(event) {
        event.preventDefault();
        $('#messageModal').modal('hide');
        msg = $('#msgText').val();
        send = true;

        $.ajax({
            url: '/put_tchat_data/',
            type: 'POST',
            data: {
                'message': msg,
                'user': u2
            },
            success: function (response) {
                if (response.indexOf('Error') > -1) {
                    alert(response);
                }
                else {
                    alert('Your message has been sent.');
                }
                if (response.indexOf('Error') < 0) {
                    count = +$('#credits').text();
                    count--;
                    $('#credits').text(count);
                    sendMessage(msg);
                }
            }
        });

        $('#msgText').val('');
    });
});
