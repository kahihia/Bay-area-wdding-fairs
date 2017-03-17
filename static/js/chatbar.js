var userData = {};
var chatContacts = {};
var chatContactNames = [];
var enableStatusCheck = false;

function loadOnlineStatus() {
    if (enableStatusCheck) {
        $('.userBarStatus').each(function (i, obj) {
            $.ajax({
                url: '/is_online/?user=' + $(this).attr('data-id'),
                type: 'GET',
                dataType: 'json'
            }).done(function (response) {
                if (response['is_online']) {
                    $(obj).text('(online)');
                }
                else {
                    $(obj).text('(offline)');
                }
            });
        });

        $('.status').each(function (i, obj) {
            $.ajax({
                url: '/is_online/?user=' + $(this).attr('data-id'),
                type: 'GET',
                dataType: 'json'
            }).done(function (response) {
                if (response['is_online']) {
                    $(obj).removeClass('vd_bg-grey').addClass('vd_bg-green');
                }
                else {
                    $(obj).removeClass('vd_bg-green').addClass('vd_bg-grey');
                }
            });
        });
    }
}

function notifyChatUser(sender, receiver, message) {
    var barApiKey, barSessionId, barToken, barNotifySession, BarTextSession;
    $.ajax({
        'url': '/get_notification_session/?user=' + receiver,
        'type': 'GET'
    }).done(function (res) {
        res = JSON.parse(res);
        barApiKey = res.apiKey;
        barSessionId = res.sessionId;
        barToken = res.token;
        barNotifySession = OT.initSession(barApiKey, barSessionId);

        barNotifySession.on("signal", function(event) {

        });

        barNotifySession.connect(barToken, function(error) {

        });

        setTimeout(function () {
            barNotifySession.signal(
                {
                    data: {
                        notification: 'You have a new message',
                        origin: 'chat',
                        target: '/online_message/',
                        message: message,
                        created_at: Date(),
                        sender: sender,
                        receiver: receiver
                    }
                },
                function (error) {

                }
            );
        }, 5000);
    });
}

function formatDateTime(datetime) {
    var DT = new Date(datetime)
    var m_names = new Array("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December");

    formattedDT = '' + DT.getHours();
    formattedDT += ':' + DT.getMinutes();
    formattedDT += ' on ' + DT.getDate();
    formattedDT += ' ' + m_names[DT.getMonth()];
    formattedDT += ' ' + DT.getFullYear();

    return formattedDT;
}

function loadChat(currentUserPic) {
    $.ajax({
        'url': '/get_chat_user_list/',
        'type': 'GET',
        'dataType': 'json',
        'async': false
    }).done(function (response) {
        var chatUserPic = '';

        html = '';
        for (var i = 0; i < response.length; i++) {
            html += '<li id="user' + response[i].id + '" class="chat-user" data-id="' + response[i].id + '" data-profile-id="' + response[i].profile_id + '"><a href="#" data-id="' + response[i].id + '" data-profile-id="' + response[i].profile_id + '">';
            html += '<div class="menu-icon"><img src="' + response[i].profile_pic + '" data-profile-id="' + response[i].profile_id + '"></div>';
            html += '<div class="menu-text" data-id="' + response[i].id + '" data-profile-id="' + response[i].profile_id + '">' + response[i].get_full_name + ' <span class="badge vd_bg-red" id="messageCount' + response[i].id + '"></span>';
            html += '<div class="menu-info"><span class="menu-date"></span></div>';
            html += '</div>';
            html += '<div class="menu-badge"><span class="badge status vd_bg-grey" data-id="' + response[i].id + '" data-profile-id="' + response[i].profile_id + '">&nbsp;</span></div>'
            html += '</a></li>';

            userData[response[i].id] = {
                'id': response[i].id,
                'get_full_name': response[i].get_full_name,
                'profile_pic': response[i].profile_pic,
                'load_messages': true
            }
            chatContactNames.push(response[i].get_full_name.toLowerCase());
            chatContacts[response[i].get_full_name.toLowerCase()] = 'user' + response[i].id;
        }
        $('#chatUserList').html(html);
    });
}

function loadUserMessages(id, currentUserPic, loadAll=false) {
    var message_html = '';
    if (loadAll) {
        var url = '/get_messages/?user=' + id + '&all=true';
    }
    else {
        message_html += '<li data-id="' + id + '" data-pic="' + currentUserPic + '" id="msgLoadAll"><a href="" data-id="' + id + '" data-pic="' + currentUserPic + '" class="text-center">Show all messages</a></li>';
        var url = '/get_messages/?user=' + id;
    }

    $.ajax({
        'url': url,
        'type': 'GET',
        'dataType': 'json',
        'async': false
    }).done(function (messages) {
        var chatUserId = id;
        for (var j = 0; j < messages.length; j++) {
            if (messages[j].sender == chatUserId) {
                message_html += '<li class="align-right"> <a href="#">';
                message_html += '<div class="menu-icon"><img src="' + userData[id]['profile_pic'] + '"></div>';
            }
            else {
                message_html += '<li class="align-left"> <a href="#">';
                message_html += '<div class="menu-icon"><img src="' + currentUserPic + '"></div>';
            }
            message_html += '<div class="menu-text">' + messages[j].message;
            message_html += '<div class="menu-info"><span class="menu-date">' + formatDateTime(messages[j].created_at) + '</span></div>';
            message_html += '</div>';
            message_html += '</a></li>';
        }
        userData[id]['messages'] = message_html;
    });

    if (loadAll) {
        $('#chatMessages').html(message_html);
    }
}

$(document).ready(function () {
    var currentUserPic = '';
    var loadChatList = true;

    $.ajax({
        'url': '/get_user_picture_url/?user=' + currentUserId,
        'type': 'GET',
        'dataType': 'text',
        'async': false,
    }).done(function (pic) {
        currentUserPic = pic;
    });

    $('#chatIcon').on('click', function(event) {
        event.preventDefault();
        if (loadChatList) {
            loadChat(currentUserPic);
            loadChatList = false;
        }
    });

    $('#chatText').bind("enterKey",function(e){
        text = $('#chatText').val();
        $('#chatText').val('');
        if (text) {
            var activeId = $('#chatText').attr('data-id');
            var html = '<li> <a href="#">';
            html += '<div class="menu-icon"><img src="' + currentUserPic + '"></div>';
            html += '<div class="menu-text">' + text;
            html += '<div class="menu-info"><span class="menu-date">' + formatDateTime(Date()) + '</span></div>'
            html += '</div>';
            html += '</a></li>';
            $('#chatMessages').append(html);
            userData[activeId]['messages'] += html;

            $.ajax({
                url: '/put_tchat_data/',
                type: 'POST',
                async: true,
                data: {
                    'message': text,
                    'user': activeId
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
                    }
                }
            });

            setTimeout(function(){
                $("#scrollbar_begins").mCustomScrollbar("scrollTo","bottom");
            }, 1000);

            notifyChatUser(currentUserId, activeId, text);
        }
    });

    $('#chatText').keyup(function(e){
        if(e.keyCode == 13) {
          $(this).trigger("enterKey");
        }
    });

    $('.video-call-icon').on('click', function (event) {
        link = $(event.target).attr('data-link');
        window.location = link;
    });

    $(document).on('click', '.chat-user', function (event) {
        event.preventDefault();

        $('#chatBox').show();
        var userId = $(event.target).attr('data-id');
        var userProfileId = $(event.target).attr('data-profile-id');

        $('#chatPaneCount').text('');
        $('#messageCount' + userId).text('')

        if (userData[userId]['load_messages']) {
            loadUserMessages(userId, currentUserPic);
            userData[userId]['load_messages']= false;
        }
        data = userData[userId];

        $('#chatUserName').text(data['get_full_name']);
        $('#chatUserName').attr('href', '/profile/' + userProfileId + '/')
        $('#userVideoLink').attr('data-link', '/online_message/?source=' + userId + '&video_call_init=true');
        $('#chatText').attr('data-id', userId);
        $('#chatMessages').attr('data-id', userId);
        $('#chatMessages').html(data['messages']);
        $('#chatText').val('');

        setTimeout(function(){
            $("#scrollbar_begins").mCustomScrollbar("scrollTo","bottom");
        }, 2000);
    });

    $('#closeBtn').on('click', function (event) {
        $('#chatBox').hide();
        $('#chatText').val('');
    });

    setInterval(loadOnlineStatus, 30000);

    $('#chatSearchTerm').on('input', function(event) {
        event.preventDefault();
        var term = $(event.target).val().toLowerCase();
        for (var i = 0; i < chatContactNames.length; i++) {
            if (chatContactNames[i].indexOf(term) > -1) {
                $('#' + chatContacts[chatContactNames[i]]).show();
            }
            else {
                $('#' + chatContacts[chatContactNames[i]]).hide();
            }
        }
    });

    $(document).on('click', '#msgLoadAll', function(event) {
        event.preventDefault();
        var id = $(event.target).attr('data-id');
        var pic = $(event.target).attr('data-pic');
        loadUserMessages(id, pic, true);
    });

    // Enables/disables online status check when chat menu icon is clicked.
    $('#top-menu-settings').on('click', function(event) {
        event.preventDefault();
        enableStatusCheck = !enableStatusCheck;
    });
});


/******************************************************************************
* Notification handlers.
******************************************************************************/

var notification_session;
var notifyTarget;

function makeOnline() {
    $.ajax({
        url: '/update_last_seen/',
        type: 'GET',
        dataType: 'text'
    }).done(function (response) {
        ;
    });
}


function initNotification() {
    $.get('/get_notification_session/?user=' + user, function (res) {
        res = JSON.parse(res);
        apiKey = res.apiKey;
        sessionId = res.sessionId;
        token = res.token;
        notification_session = OT.initSession(apiKey, sessionId);

        notification_session.on("signal", function(event) {
            if (currentUserId == event.data.sender) {

            }
            else {
                $.ajax({
                    'url': '/get_user_picture_url/?user=' + event.data.sender,
                    'type': 'GET',
                    'dataType': 'text',
                    'async': false
                }).done(function (pic) {
                    chatUserOnePic = pic;
                });

                var html = '<li  class="align-right"> <a href="#">';
                html += '<div class="menu-icon"><img src="' + chatUserOnePic + '"></div>';
                html += '<div class="menu-text">' + event.data.message;
                html += '<div class="menu-info"><span class="menu-date">' + formatDateTime(event.data.created_at) + '</span></div>'
                html += '</div>';
                html += '</a></li>';

                if ($("ul[data-id='" + event.data.sender + "']").length > 0) {
                    $("ul[data-id='" + event.data.sender + "']").append(html);
                }

                if (userData[event.data.sender]) {
                    userData[event.data.sender]['messages'] += html;
                }

                if($('#chatBox').css('display') == 'none') {
                    if($('#chatPaneCount').length) {
                        count = +$('#chatPaneCount').text();
                        count++;
                        $('#chatPaneCount').text(count);
                    }
                    else {
                        $('#chatIcon').append('<span class="badge vd_bg-red" id="chatPaneCount">1</span>');
                    }
                }

                if ($('#messageCount' + event.data.sender).text()) {
                    count = +$('#messageCount' + event.data.sender).text();
                    count++;
                    $('#messageCount' + event.data.sender).text(count);
                }
                else {
                    $('#messageCount' + event.data.sender).text(1);
                }
            }

            var chatPage = window.location.href.indexOf('online_message') > -1;
            var profilePage = window.location.href.indexOf('/profile/') > -1;
            if (chatPage) {
                if (!(event.data.sender == user2 && (event.data.origin == 'chat' || event.data.origin == 'video'))) {
                    if (event.data.origin == 'chat') {
                        if($('#messageCount').length) {
                            count = +$('#messageCount').text();
                            count++;
                            $('#messageCount').text(count);
                        }
                        else {
                            $('#messageNotification').append('<span class="badge vd_bg-red" id="messageCount">1</span>');
                        }

                        if($('#chatPaneCount').text()) {
                            count = +$('#chatPaneCount').text();
                            count++;
                            $('#chatPaneCount').text(count);
                        }
                        else {
                            $('#chatPaneCount').text(1);
                        }
                    }
                    else if (event.data.origin == 'video') {
                        $('#notifyMsg').text(event.data.notification);
                        $('#notificationModal').modal('show');
                        $('#notifyAction').text('Accept');
                        $('#notifyAction').attr('href', event.data.target);
                        notifyTarget = event.data.target;
                    }
                }
                else if (!(event.data.sender == user2 && event.data.origin == 'chat')) {
                    resMsg = '<li><div class="col-md-6 npl"><div class="vd_bg-grey reciever-chat-wrap">';
                    resMsg += '<div class="col-md-12">';
                    resMsg += '<p class="messages-content vd_white">' + event.data.senderName + 'is making a video call.</p>';
                    resMsg += '<button id="accept" class="btn btn-success" type="button" data-dismiss="modal"><i class="fa fa-phone img-rounded" aria-hidden="true"></i> Accept</button>';
                    resMsg += '&nbsp;&nbsp;<button id="ignore" class="btn btn-danger" type="button" data-dismiss="modal"><i class="fa fa-phone" aria-hidden="true"></i> Reject</button>';
                    resMsg += '</div>';
                    resMsg += '<div class="col-md-12"><div class="messages-from text-right"><span class="time-stamp vd_white chat-date">&nbsp;</span></div>';
                    resMsg += '</div><div class="clearfix"></div></div></div><div class="col-md-6 clearfix"></div></li>';
                    $('#chatBox').append(resMsg);
                }
            }
            else if (profilePage) {

            }
            else {
                if (event.data.origin == 'chat') {
                    if($('#messageCount').length) {
                        count = +$('#messageCount').text();
                        count++;
                        $('#messageCount').text(count);
                    }
                    else {
                        $('#messageNotification').append('<span class="badge vd_bg-red" id="messageCount">1</span>');
                    }
                }
                else if (event.data.origin == 'video') {
                    $('#notifyMsg').text(event.data.notification);
                    $('#notificationModal').modal('show');
                    $('#notifyAction').text('Accept');
                    $('#notifyAction').attr('href', event.data.target);
                    notifyTarget = event.data.target;
                }
            }

            setTimeout(function(){
                $("#scrollbar_begins").mCustomScrollbar("scrollTo","bottom");
            }, 2000);
        });

        notification_session.connect(token, function(error) {

        });
    });

    $('#notifyAction').on('click', function () {
        window.location.href = notifyTarget;
    });
}

$(document).ready(function() {
    if (!(navigator.userAgent.indexOf('Safari') != -1 && navigator.userAgent.indexOf('Chrome') == -1)) {
        initNotification();
    }

    makeOnline();

    setInterval(makeOnline, 45000);
});
