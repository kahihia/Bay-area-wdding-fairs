// var notification_session;
// var notifyTarget;
//
// function makeOnline() {
//     $.ajax({
//         url: '/update_last_seen/',
//         type: 'GET',
//         dataType: 'text'
//     }).done(function (response) {
//         ;
//     });
// }
//
//
// function initNotification() {
//     $.get('/get_notification_session/?user=' + user, function (res) {
//         res = JSON.parse(res);
//         apiKey = res.apiKey;
//         sessionId = res.sessionId;
//         token = res.token;
//         notification_session = OT.initSession(apiKey, sessionId);
//
//         notification_session.on("signal", function(event) {
//             if (currentUserId == event.data.sender) {
//
//             }
//             else {
//                 $.ajax({
//                     'url': '/get_user_picture_url/?user=' + event.data.sender,
//                     'type': 'GET',
//                     'dataType': 'text',
//                     'async': false
//                 }).done(function (pic) {
//                     chatUserOnePic = pic;
//                 });
//
//                 var html = '<li  class="align-right"> <a href="#">';
//                 html += '<div class="menu-icon"><img src="' + chatUserOnePic + '"></div>';
//                 html += '<div class="menu-text">' + event.data.message;
//                 html += '<div class="menu-info"><span class="menu-date">' + formatDateTime(event.data.created_at) + '</span></div>'
//                 html += '</div>';
//                 html += '</a></li>';
//
//                 if ($("ul[data-id='" + event.data.sender + "']").length > 0) {
//                     $("ul[data-id='" + event.data.sender + "']").append(html);
//                 }
//
//                 userData[activeId]['messages'] += html;
//
//                 count = +$('#userOneCount').text();
//                 count++;
//                 $('#userOneCount').text(count);
//             }
//
//             var chatPage = window.location.href.indexOf('online_message') > -1;
//             var profilePage = window.location.href.indexOf('/profile/') > -1;
//             if (chatPage) {
//                 if (!(event.data.sender == user2 && (event.data.origin == 'chat' || event.data.origin == 'video'))) {
//                     if (event.data.origin == 'chat') {
//                         if($('#messageCount').length) {
//                             count = +$('#messageCount').text();
//                             count++;
//                             $('#messageCount').text(count);
//                         }
//                         else {
//                             $('#messageNotification').append('<span class="badge vd_bg-red" id="messageCount">1</span>');
//                         }
//
//                         if($('#chatPaneCount').text()) {
//                             count = +$('#chatPaneCount').text();
//                             count++;
//                             $('#chatPaneCount').text(count);
//                         }
//                         else {
//                             $('#chatPaneCount').text(1);
//                         }
//                     }
//                     else if (event.data.origin == 'video') {
//                         $('#notifyMsg').text(event.data.notification);
//                         $('#notificationModal').modal('show');
//                         $('#notifyAction').text('Accept');
//                         $('#notifyAction').attr('href', event.data.target);
//                         notifyTarget = event.data.target;
//                     }
//                 }
//                 else if (!(event.data.sender == user2 && event.data.origin == 'chat')) {
//                     resMsg = '<li><div class="col-md-6 npl"><div class="vd_bg-grey reciever-chat-wrap">';
//                     resMsg += '<div class="col-md-12">';
//                     resMsg += '<p class="messages-content vd_white">' + event.data.senderName + 'is making a video call.</p>';
//                     resMsg += '<button id="accept" class="btn btn-success" type="button" data-dismiss="modal"><i class="fa fa-phone img-rounded" aria-hidden="true"></i> Accept</button>';
//                     resMsg += '&nbsp;&nbsp;<button id="ignore" class="btn btn-danger" type="button" data-dismiss="modal"><i class="fa fa-phone" aria-hidden="true"></i> Reject</button>';
//                     resMsg += '</div>';
//                     resMsg += '<div class="col-md-12"><div class="messages-from text-right"><span class="time-stamp vd_white chat-date">&nbsp;</span></div>';
//                     resMsg += '</div><div class="clearfix"></div></div></div><div class="col-md-6 clearfix"></div></li>';
//                     $('#chatBox').append(resMsg);
//                 }
//             }
//             else if (profilePage) {
//
//             }
//             else {
//                 if (event.data.origin == 'chat') {
//                     if($('#messageCount').length) {
//                         count = +$('#messageCount').text();
//                         count++;
//                         $('#messageCount').text(count);
//                     }
//                     else {
//                         $('#messageNotification').append('<span class="badge vd_bg-red" id="messageCount">1</span>');
//                     }
//                 }
//                 else if (event.data.origin == 'video') {
//                     $('#notifyMsg').text(event.data.notification);
//                     $('#notificationModal').modal('show');
//                     $('#notifyAction').text('Accept');
//                     $('#notifyAction').attr('href', event.data.target);
//                     notifyTarget = event.data.target;
//                 }
//             }
//         });
//
//         notification_session.connect(token, function(error) {
//
//         });
//     });
//
//     $('#notifyAction').on('click', function () {
//         window.location.href = notifyTarget;
//     });
// }
//
// $(document).ready(function() {
//     if (!(navigator.userAgent.indexOf('Safari') != -1 && navigator.userAgent.indexOf('Chrome') == -1)) {
//         initNotification();
//     }
//
//     makeOnline();
//
//     setInterval(makeOnline, 45000);
// });
