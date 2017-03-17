var apiKey, sessionId, token, notify_session, text_session;
var msgObj = {};

function formatDateTime(datetime) {
    var DT = new Date(datetime)
    var m_names = new Array("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December");

    formattedDT = '' + DT.getHours();
    formattedDT += ':' + DT.getMinutes();
    formattedDT += ' on ' + DT.getDate();
    formattedDT += ' ' + m_names[DT.getMonth()];
    formattedDT += ' ' + DT.getFullYear();

    return formattedDT
}

function getUserMessages(user, user2, loadAll=false) {
    $('#chatBox').empty();
    var html = '';

    if (loadAll) {
        url = '/get_tchat_archive/?user=' + user2 + '&all=true';
    }
    else {
        url = '/get_tchat_archive/?user=' + user2;
        html = '<li data-id="' + user2 + '" id="chatLoadAll"><a href="" data-id="' + user2 + '" class="text-center">Show all messages</a></li>';
    }

    if (msgObj[user2] && !loadAll) {
        $('#chatBox').append(msgObj[user2]);
    }
    else {
        $.ajax({
            url: url,
            type: 'GET',
            dataType: 'json',
            aync: false,
        }).done(function (response) {
            var count = Object.keys(response).length;
            for(var i=0;i<count;i++) {
                if (response[i].fields.sender == user && response[i].fields.receiver == user2) {
                    resMsg = '<li><div class="col-md-6 clearfix"></div><div class="col-md-6 npr" id="sender_send_message"><div class="vd_bg-blue chat-wrap"><div class="col-md-12"><p class="messages-content vd_white">' + response[i].fields.message + '</p></div><div class="col-md-12"></div><div class="col-md-12"><div class="messages-from text-right"><p class="vd_white messages-content">' + formatDateTime(response[i].fields.created_at) + '</p></div></div><div class="clearfix"></div></div></li>';
                }
                else if (response[i].fields.sender == user2 && response[i].fields.receiver == user) {
                    resMsg = '<li><div class="col-md-6 npl"><div class="vd_bg-grey reciever-chat-wrap"><div class="col-md-12"><p class="messages-content vd_white">' + response[i].fields.message + '</p></div><div class="col-md-12"><div class="messages-from text-right"><p class="vd_white messages-content">' + formatDateTime(response[i].fields.created_at) + '</p></div></div><div class="clearfix"></div></div></div><div class="col-md-6 clearfix"></div></li>'
                }
                html += resMsg;
                msgObj[user2] = html;
            }
            $('#chatBox').append(html);
            setTimeout(function(){
                $("#scrollbar_begins").mCustomScrollbar("scrollTo","bottom");
            }, 3000);
        });
    }
}

function sendMessage(msg) {
    text_session.signal(
        {
            data: {
                message: msg,
                sender: user,
                receiver: user2
            }
        },
        function (error) {

        }
    );

    notify_session.signal(
        {
            data: {
                notification: name2 + ' send you a message',
                origin: 'chat',
                target: '/online_message/',
                message: msg,
                created_at: Date(),
                sender: user,
                receiver: user2
            }
        },
        function (error) {

        }
    );
}

function initOpentok() {
    $('#chatBox').empty();
    $('#chatBtn').off('click');
    $('#chatBox').append('<li id="waitMsg"><h3 class"lead text-center">Loading messages. Please wait.</h3></li>');
    // var notify_session;

    $.get('/get_notification_session/?user=' + user2, function (res) {
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

    $.get('/get_tchat_session/?user=' + user2, function(res) {
        res = JSON.parse(res);
        apiKey = res.apiKey;
        sessionId = res.sessionId;
        token = res.token;
        text_session = OT.initSession(apiKey, sessionId);

        text_session.on("signal", function(event) {
            if (event.data.sender == user && event.data.receiver == user2) {
                resMsg = '<li><div class="col-md-6 clearfix"></div><div class="col-md-6 npr" id="sender_send_message"><div class="vd_bg-blue chat-wrap"><div class="col-md-12"><p class="messages-content vd_white">' + event.data.message + '</p></div><div class="col-md-12"></div><div class="col-md-12"><div class="messages-from text-right"><p class="vd_white messages-content">' + formatDateTime(Date()) + '</p></div></div><div class="clearfix"></div></div></li>';
            }
            else if (event.data.sender == user2 && event.data.receiver == user) {
                resMsg = '<li><div class="col-md-6 npl"><div class="vd_bg-grey reciever-chat-wrap"><div class="col-md-12"><p class="messages-content vd_white">' + event.data.message + '</p></div><div class="col-md-12"><div class="messages-from text-right"><p class="vd_white messages-content">' + formatDateTime(Date()) + '</p></div></div><div class="clearfix"></div></div></div><div class="col-md-6 clearfix"></div></li>';
            }
            $('#chatBox').append(resMsg);
            setTimeout(function(){
                $("#scrollbar_begins").mCustomScrollbar("scrollTo","bottom");
            }, 1000);
        });

        text_session.connect(token, function(error) {

        });

        $('#chatBtn').on('click', function () {
            msg = $('#chatMsg').val();
            send = true;

            $.ajax({
                url: '/put_tchat_data/',
                type: 'POST',
                data: {
                    'message': msg,
                    'user': user2
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

            $('#chatMsg').val('');
        });
    });

    getUserMessages(user, user2);
}

$(document).ready(function() {
    if (!(navigator.userAgent.indexOf('Safari') != -1 && navigator.userAgent.indexOf('Chrome') == -1)) {
        initOpentok();
    }
    $("#search_result").hide();

    $(document).on('click', '#chatLoadAll', function(event) {
        event.preventDefault();
        var id = $(event.target).attr('data-id');
        getUserMessages(user, id, true);
    });

    $('#chatMsg').bind("enterKey",function(e){
        msg = $('#chatMsg').val();
        send = true;

        $.ajax({
            url: '/put_tchat_data/',
            type: 'POST',
            data: {
                'message': msg,
                'user': user2
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

        $('#chatMsg').val('');
    });

    $('#chatMsg').keyup(function(e){
        if(e.keyCode == 13) {
          $(this).trigger("enterKey");
        }
    });
});

$(document).click(function(event) {
    $('#search_result').hide();
});
