$(document).ready(function() {


    /**
    $(".add-friend").click(function(){
        var id = $(this).data('id');
        $.ajax({
            url: "/friends/create?id=" + id
        });
        $(this).remove();
        bootbox.alert('Friend Request Submitted');
    });
     **/

    var options = {
        target:        '#output1',   // target element(s) to be updated with server response
        beforeSubmit:  showRequestCallback,  // pre-submit callback
        success:       showResponseCallback,  // post-submit callback

        // other available options:
        url:       '/post/create',
        type:     'post',
        dataType:  'json',        // 'xml', 'script', or 'json' (expected server response type)
        clearForm: true,        // clear all form fields after successful submit
        resetForm: true        // reset the form after successful submit

        // $.ajax options can be used here too, for example:
        //timeout:   3000
    };

    // bind form using 'ajaxForm'
    $('#postform').ajaxForm(options);

    // pre-submit callback
    function showRequestCallback(formData, jqForm, options) {
        return true;
    }

    // post-submit callback
    function showResponseCallback(responseText, statusText, xhr, $form)  {
        $.fn.yiiListView.update("post-list");
    }


    $(".markTask").click(function(){
        var id = $(this).data('id');

        var element = $(this);

        var listElem = element.parent();
        var value = 1;
        if(listElem.hasClass('complete')){
            listElem.removeClass('complete');
            value = 0;
        } else {
            listElem.addClass('complete');
        }

        $.ajax({
            url: "/tasks/completed?id=" + id + "&value=" + value,
            type: "POST"
        });
    });

    $(document).on('click', '#nudge', function(){
        var id = $(this).attr('data-id');
        var name = $(this).attr('name');
        $.ajax({
            url: "/friends/nudge?id=" + id,
            type: "POST"
        }).success(function(data){
            data = jQuery.parseJSON(data);
            if(data.success){
                bootbox.alert('You nudged this person.');
            } else {
                bootbox.alert('You can only nudge the same person once every 24 hours.')
            }
        });
    });

    //handle delete   
    $(document).on('click', '.deletePostBtn', function(){
        var id = $(this).data('id');
        bootbox.confirm("Are you sure you wish to delete this post?", function(result) {
            if (!result) return;  
            $.ajax({
                url: "/post/delete?id=" + id,
                type: "POST"
            }).success(function (data) {
                $.fn.yiiListView.update("post-list");
            });
        });      
    });
    
    //Handle likes
    $(document).on('click', '.likeBtn', function(){
        var elem = $(this);
        var id = elem.data('id');
        var liked = $(this).data('liked');
        $.ajax({
            url: "/post/like?id=" + id,
            type: "POST"
        }).success(function (data) {
            if(liked == '1'){
                elem.html('Like (' + data + ')');
                elem.data('liked', 0);
            } else {
                elem.html('Unlike (' + data + ')');
                elem.data('liked', 1);
            }
        });
    });

    //Handle share
    $(document).on('click', '.shareBtn', function(){
        var id = $(this).data('id');
        $.ajax({
            url: "/post/share?id=" + id,
            type: "POST"
        }).success(function (data) {
            $.fn.yiiListView.update("post-list");
        });
    });

    //Handle favorites
    $(document).on('click', '.starBtn', function(){
        var id = $(this).data('id');
        var flagged = $(this).data('flagged');
        if(flagged == '1'){
            $(this).find('i').removeClass('fa-star').addClass('fa-star-o');
            $(this).data('flagged', 0);
        } else {
            $(this).find('i').removeClass('fa-star-o').addClass('fa-star');
            $(this).data('flagged', 1);
        }

        $.ajax({
            url: "/post/favorite?id=" + id,
            type: "POST"
        }).success(function (data) {

        });
    });

    //Handle comment
    $(document).on('keypress', '.commentInput', function(e){
        if (e.keyCode == 13) {
            var id = $(this).data('id');
            var text = $(this).val();
            $(this).val("");
            $.ajax({
                url: "/post/comment?id=" + id,
                data: {comment: text},
                type: "POST"
            }).success(function (data) {
                $.fn.yiiListView.update("post-list");
            });
        }
    });

});