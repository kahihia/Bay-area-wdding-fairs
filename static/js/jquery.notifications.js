$(document).ready(function() {

    $(".notifiyListener").click(function(){
        var id = $(this).data('id');

        var element = $(this);

        var listElem = element.parent().parent();
        var value = 1;
        if(listElem.hasClass('complete')){
            listElem.removeClass('complete');
            value = 0;
        } else {
            listElem.addClass('complete');
        }

        $.ajax({
            url: "/notification/completed?id=" + id + "&value=" + value,
            type: "POST"
        });

        var oldNotify = parseInt($("#unread-counter").text());

        var newValue = oldNotify;
        newValue = (value == 0) ? newValue + 1 : newValue - 1;
        if(newValue > 0) {
            $("#unread-counter").text(newValue);
        } else {
            $("#unread-counter").remove();
        }
    });

// seth
// unread on click of accept or reject instead of tick
  $(".friendRequestLink, .friendRequestLinkReject").click(function(){
            var _this=$(this);
            var _check=_this.parents('li').find('.notifiyListener:first-child');
            _check.click();
           });




});