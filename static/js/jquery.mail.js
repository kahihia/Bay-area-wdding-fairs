$(document).ready(function() {

    if($("#to").length > 0){
        $("#to").chosen();
    }

    $("#sendBtn").click(function(){
        $("#composeForm").submit();
    });

    $("#saveDraftBtn").click(function(){
        $("#draftField").val(1);
        $("#composeForm").submit();
    });

    $("#mark-all").click(function(){
        var list = [];
        $(".checkMailMessage").each(function(){
            var id = $(this).data('id');
            list.push(id);
        });

        $.ajax({
            url: "/mail/markread",
            data: {list: list},
            type: "POST"
        }).success(function(data){
            $.fn.yiiGridView.update("mail-list");
            updateUnreadCount();
        });

    });

    $("#delete-all").click(function(){
        var list = [];
        $(".checkMailMessage").each(function(){
            if($(this).is(':checked')){
                var id = $(this).data('id');
                list.push(id);
            }
        });

        $.ajax({
            url: "/mail/delete",
            data: {list: list},
            type: "POST"
        }).success(function(data){
            $.fn.yiiGridView.update("mail-list",{
                url: '/mail?ajax=mail-list'
            });
            updateUnreadCount();
        });
    });

});

function updateUnreadCount(){
    $.ajax({
        url: "/mail/unreadCount",
        type: "POST"
    }).success(function(count){
        count = jQuery.parseJSON(count);
        $("#unread-counter-mail").html(count.unreadCount);

        $("#rcount").html(count.unreadCount);
        $("#scount").html(count.sentCount);
        $("#draftcount").html(count.draftCount);
        $("#dcount").html(count.deletedCount);
    });
}