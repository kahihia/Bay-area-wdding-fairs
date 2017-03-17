var vApiKey, vSessionId, vToken, video_session;

function vChat() {
    if (source) {
        get_friend_name(source);
        $( "#lastColumn" ).slideToggle({duration: '1000', queue: false})
        $('#middleColumn').addClass('col-md-4').removeClass('col-md-8');
        $('#middleColumn').addClass('col-lg-4').removeClass('col-lg-8');
        $('#middleColumn').addClass('col-sm-4').removeClass('col-sm-8');
        $('#middleColumn').addClass('col-xs-4').removeClass('col-xs-8');
        $('#startVideoCall').attr('disabled', 'disabled');
        if (videoCallInit) {
            var nSession;
            $.get('/get_notification_session/?user=' + user2, function (res) {
                var res = JSON.parse(res);
                var apiKey = res.apiKey;
                var sessionId = res.sessionId;
                var token = res.token;
                nSession = OT.initSession(apiKey, sessionId);

                nSession.on("signal", function(event) {

                });

                nSession.connect(token, function(error) {

                });
            });
            setTimeout(function () {
                nSession.signal(
                    {
                        data: {
                            notification: name + ' is making a video call',
                            origin: 'video',
                            target: '/online_message/?source=' + user,
                            sender: user,
                            senderName: name,
                            receiver: user2
                        }
                    },
                    function (error) {

                    }
                );
            }, 10000)
        }
        initVideoChat();

        setTimeout(function () {
            find_friend_message(source)
        }, 5000);
    }

    $('#videoCloseX').on('click', function (event) {
        video_session.disconnect();
        $('#subscriber').empty();
        $('#publisher').empty();
    });
    $('#videoCloseBtn').on('click', function (event) {
        $("#lastColumn").fadeToggle({duration: '1000', queue: false})
        $('#middleColumn').addClass('col-lg-8').removeClass('col-lg-4');
        $('#middleColumn').addClass('col-md-8').removeClass('col-md-4');
        $('#middleColumn').addClass('col-sm-8').removeClass('col-sm-4');
        $('#middleColumn').addClass('col-xs-8').removeClass('col-xs-4');
        $('button#accept').removeAttr('disabled');
        video_session.disconnect();
        $('#subscriber').empty();
        $('#publisher').empty();
        $('#startVideoCall').removeAttr('disabled');
    });

    $(document).on("click", "#accept", function() {
        console.log( $( this ).text() );
        //$( "#lastColumn" ).slideToggle( "slow" );
        // $("#lastColumn").toggle("slide");
        $( "#lastColumn" ).slideToggle({duration: '1000', queue: false})
        $('#middleColumn').addClass('col-md-4').removeClass('col-md-8');
        $('#middleColumn').addClass('col-lg-4').removeClass('col-lg-8');
        $('#middleColumn').addClass('col-sm-4').removeClass('col-sm-8');
        $('#middleColumn').addClass('col-xs-4').removeClass('col-xs-8');
        $(this).attr("disabled", "true");
        initVideoChat();
        $('#startVideoCall').attr('disabled', 'disabled');
    });
    $(document).on("click", "#ignore", function() {
        console.log( $( this ).text() );
        //$( "#lastColumn" ).slideToggle( "slow" );
        //$("#lastColumn").toggle("slide");
        $("#lastColumn").fadeToggle({duration: '1000', queue: false})
        $('#middleColumn').addClass('col-md-8').removeClass('col-md-4');
        $('button#accept').removeAttr('disabled');
        video_session.disconnect();
        $('#subscriber').empty();
        $('#publisher').empty();
        $('#startVideoCall').removeAttr('disabled');
    });
}

$(document).ready(function() {
    if (!(navigator.userAgent.indexOf('Safari') != -1 && navigator.userAgent.indexOf('Chrome') == -1)) {
        vChat();
    }
});

function initVideoChat() {
    $.get('/get_vchat_session/?user=' + user2, function(res) {
        res = JSON.parse(res);
        vApiKey = res.apiKey;
        vSessionId = res.sessionId;
        vToken = res.token;
        initializeSession();
    });
}

function initializeSession() {
  video_session = OT.initSession(vApiKey, vSessionId);

  // Subscribe to a newly created stream
  video_session.on('streamCreated', function(event) {
    console.log('subscribe');
    video_session.subscribe(event.stream, 'subscriber', {
      insertMode: 'append',
      width: '100%',
      height: '100%'
    });
  });

  video_session.on('sessionDisconnected', function(event) {

  });

  // Connect to the session
  video_session.connect(vToken, function(error) {
    // If the connection is successful, initialize a publisher and publish to the session
    if (!error) {
      console.log('publish');
      var publisher = OT.initPublisher('publisher', {
        insertMode: 'append',
        width: '100%',
        height: '100%'
      });

      video_session.publish(publisher);
      $.get('/register_video_call/', function (res) {
        if (res.indexOf('Error') > -1) {
            alert(res);
            video_session.disconnect();
        }
      });
    } else {

    }
  });
}
