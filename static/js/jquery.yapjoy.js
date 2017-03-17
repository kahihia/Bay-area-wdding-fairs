$(document).ready(function() {

    //When checkboxes have the same name, treat them as radio buttons.
    $('input[type="checkbox"]').on('change', function() {
        if(this.name == 'interests[]') return;
        $('input[name="' + this.name + '"]').not(this).prop('checked', false);
    });

    //AJAX requests
    $.xhrPool = [];

    var width = $(window).width(),
        height = $(window).height(),
        gifWidth = 300,
        gifHeight = 400;

    // Setup the beforeSend ajax functionality to show overlay and loading gif
    $.ajaxSetup({
        beforeSend: function(jqXHR) {
            $.xhrPool.push(jqXHR);
        },
        complete: function(jqXHR) {
            var index = $.xhrPool.indexOf(jqXHR);
            if (index > -1) {
                $.xhrPool.splice(index, 1);
            }
        },
        error: function(jqXHR) {
            bootbox.alert(jqXHR.responseText);
        }
    });
    var interval;
    $(document).ajaxStart(function() {
        $.xhrPool.abortAll = function() {
            $(this).each(function(idx, jqXHR) {
                jqXHR.abort();
            });
            $.xhrPool = [];
        };
        $("body").append("<div id=\"overlay-ajax\"></div>");
        $("#overlay-ajax").css({
            background: "rgba(255, 255, 255, 0.8)",
            position: "fixed",
            left: 0,
            top: 0,
            width: $(window).width(),
            height: $(window).height(),
            "z-index": 4000
        });

        $("body").append("<img id=\"loading-ajax\" src=\"/static/images/loading.gif\" />");
        $("#loading-ajax").css({
            position: "fixed",
            left: (($(window).width() / 2) - (gifWidth / 2)), // Calculate the center x-axis
            top: (($(window).height() / 2) - (gifHeight / 2)), // Calculate the center y-axis
            "z-index": 5000
        });
        $('body').append("<div id='timer'>Please Wait...</div>");
        $('#timer').css({
            position: 'fixed',
            top: (($(window).height() / 2) + (gifHeight) / 4),
            left: (($(window).width() / 2) - 50),
            'z-index': 5100,
            'font-weight': 'bold'
        });
        $('body').append("<a href=\"#\" id=\"cancel-ajax\" >&times;</a>");
        $("#cancel-ajax").css({
            position: "fixed",
            right: 10,
            top: 10,
            "z-index": 5000,
            'text-decoration': 'none',
            'font-size': 48
        });
        $('#cancel-ajax').on('click', function() {
            return cancelAjaxCall();
        });

        var seconds = 0;
        interval = setInterval(function() {
            seconds++;
            if (seconds >= 180) // 3 minutes
            {
                cancelAjaxCall();
                $.pnotify({
                    type: 'error',
                    title: 'Timed Out!',
                    text: 'The Ajax call has been automatically cancelled due to excessive time to process request. Double check to make sure your request did not actually process!'
                });
                clearInterval(interval);
            }
            $('#timer').html('Please Wait... ' + (180 - seconds));
        }, 1000);
    });

    // Remove the overlay and loading image on Ajax call completion
    $(document).ajaxComplete(function() {
        $("#loading-ajax").remove();
        $("#overlay-ajax").remove();
        $("#cancel-ajax").remove();
        $("#timer").remove();
        clearInterval(interval);
    });

});
