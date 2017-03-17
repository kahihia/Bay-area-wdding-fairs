$(document).ready(function() {

    // $("#search").keypress(function (e) {
    //     if (e.which == 13) {
    //         updateForm();
    //     }
    // });
// patch2
  $("#search").keypress(function (e) {
        if (e.which == 13) {
var data = '&search=' + encodeURIComponent($('#search').val());

    if(data != ''){
        $.fn.yiiListView.update('friend-list', {
            url: "/friends?1=1&" + data
        });
    } else {
        $.fn.yiiListView.update('user-list');
    }        }
    });
// patch2

    $(document).on('click', '.deleteFriendBtn', function(){
        console.log('working delete friend');
        var id = $(this).data('id');
        var element = $(this);

        bootbox.confirm("<h3>Are you sure you wish to unfriend this friend?</h3>", function(result) {
            if (!result) return;
            element.parent().parent().parent().parent().remove();
            console.log('working delete friend');
            $.ajax({
                url: "/friends/delete/?id=" + id,
                type: "POST"
            }).success(function(resp){
                //var count = parseInt($("#friendCounter").html());
                //$("#friendCounter").html((count - 1));
                //$.fn.yiiListView.update("friend-list");
            });
        });

    });


    $(document).on('click', '#addFriendGroupBtn', function(){
        bootbox.prompt("Enter a name for your new group.", function(result) {
            if (!result) return;

            var count = parseInt($("#groupCounter").html());
            $("#groupCounter").html((count + 1));

            $.ajax({
                url: "/friends/createGroup?result="+result,
                type: "POST"
            }).success(function(){

                $.fn.yiiListView.update("friend-group-list");
            });
        });

    });

    $(document).on('click', '#addFriendBtn', function(){
        var data = $("#addFriendForm").serialize();

        $.ajax({
            url: "/friends/create",
            type: "POST",
            data: data
        }).success(function(){
            $(':input','#addFriendForm')
                .not(':button, :submit, :reset, :hidden')
                .val('')
                .removeAttr('checked')
                .removeAttr('selected');
            $.fn.yiiListView.update("friend-list");
            var count = parseInt($("#friendCounter").html());
            $("#friendCounter").html((count + 1));
        });
    });

    $(document).on('click', '#addFriendBtnGeneral', function(){
        var data = $("#addFriendFormGeneral").serialize();
        $.ajax({
            url: "/friends/create",
            type: "POST",
            data: data
        }).success(function(){
            $(':input','#addFriendFormGeneral')
                .not(':button, :submit, :reset, :hidden')
                .val('')
                .removeAttr('checked')
                .removeAttr('selected');
            $.fn.yiiListView.update("friend-group-list");
            var count = parseInt($("#friendCounter").html());
            $("#friendCounter").html((count + 1));
        });
    });

    $(document).on('click', '.deleteFriendGroupBtn', function(){
        var groupId = $(this).data('group-id');
        var friendId = $(this).data('id');
        var element = $(this);
        element.parent().parent().parent().remove();

        var count = parseInt($("#groupCounter").html());
        $("#groupCounter").html((count - 1));

        $.ajax({
            url: "/friends/remove?group="+groupId+"&friend="+friendId,
            type: "POST"
        }).success(function(){
        });
    });

    $(document).on('click', '.deleteGroupBtn', function(){
        var groupId = $(this).data('id');
        bootbox.confirm('Are you sure you want to delete this group? All friends in this group will no longer be assosciated with it.', function(e){
            if(e == 1){
                var count = parseInt($("#groupCounter").html());
                $("#groupCounter").html((count - 1));
                $.ajax({
                    url: "/friends/removeGroup?group="+groupId,
                    type: "POST"
                }).success(function(){
                    $.fn.yiiListView.update("friend-group-list");
                });
            }
        });
    });


});

function updateForm(){
    var data = '&search=' + encodeURIComponent($('#search').val());

    if(data != ''){
        $.fn.yiiListView.update('friend-list', {
            url: "/friends?1=1&" + data
        });
    } else {
        $.fn.yiiListView.update('user-list');
    }

}