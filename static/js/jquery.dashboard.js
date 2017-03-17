$(document).ready(function() {

    // patch3
    // to create hyperlink
       hyperlink();

    // patch3

        if($("#getStarted").length > 0){
            $("#getStarted").click(function(){
                $("#getStarted").remove();
                $("#newUserModal").modal('show');
            });

            $("#updateSettingsBtn").click(function(){
                var data = $("#updateSettingsForm").serialize();
                $.ajax({
                    url: "/settings",
                    type: "POST",
                    data: data
                });
            });
        }

    $(document).on('change', '#iamModal', function(){
       if($(this).val() == 1 || $(this).val() == 2){
            $("#wedding_date").removeAttr('disabled');
       } else {
           $("#wedding_date").attr('disabled', 'disabled');
       }
    });

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
        var childElem = element.find('i');
        var value = 1;
        if(listElem.hasClass('complete')){
            listElem.removeClass('complete');

            childElem.removeClass('fa-check');
            childElem.addClass('fa-circle-o');
            value = 0;
        } else {
            listElem.addClass('complete');
            childElem.removeClass('fa-circle-o');
            childElem.addClass('fa-check');
        }

        $.ajax({
            url: "/tasks/completed?id=" + id + "&value=" + value,
            type: "POST"
        }).success(function (data) {


        });
    });

    //handle delete   
    //$(document).on('click', '.deletePostBtn', function(){
    //    var id = $(this).data('id');
    //    bootbox.confirm("Are you sure you wish to delete this post?", function(result) {
    //        if (!result) return;
    //        $.ajax({
    //            url: "/post/delete?id=" + id,
    //            type: "POST"
    //        }).success(function (data) {
    //            $.fn.yiiListView.update("post-list");
    //        });
    //    });
    //});
    
    //Handle likes
    //$(document).on('click', '.likeBtn', function(){
    //    var elem = $(this);
    //    var id = elem.data('id');
    //    var liked = $(this).data('liked');
    //    $.ajax({
    //        url: "/post/like?id=" + id,
    //        type: "POST"
    //    }).success(function (data) {
    //        if(liked == '1'){
    //            elem.html('Like (' + data + ')');
    //            elem.data('liked', 0);
    //        } else {
    //            elem.html('Unlike (' + data + ')');
    //            elem.data('liked', 1);
    //        }
    //    });
    //});

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

    //Handle comment
    //$(document).on('keypress', '.commentInput', function(e){
    //    if (e.keyCode == 13) {
    //        var id = $(this).data('id');
    //        var text = $(this).val();
    //        $(this).val("");
    //        $.ajax({
    //            url: "/post/comment?id=" + id,
    //            data: {comment: text},
    //            type: "POST"
    //        }).success(function (data) {
    //            $.fn.yiiListView.update("post-list");
    //        });
    //    }
    //});

    $(document).on('keypress', '#id_comment', function(e){
        if (e.keyCode == 13) {
            //console.log($(this));
            var id = $(this).attr('feed_id');
            //alert(id);

            //var $form = $('#commentForm_'+id);
            //$form.bind('submit',function() {
            //       $.post( $form.attr('action'), $form.serialize(), function(data) {
            //    //e.preventDefault()
            //        //console.log(data)
            //    //var csrftoken1 = "{% csrf_token %}";
            //    //var csrftoken2 = "{% csrf_token %}";
            //           alert('done')
            //            var post = "<div class='media re-post'><div class='media-left'><span class='profile-thumb profile-sm' style='background-image: url(/static/images/tempPhoto.png)'></span></div><div class='media-body'><h5 class='media-heading'><a href='#!'>"+data.user.first_name+" "+data.user.last_name+"</a> <span class='time-stamp'>Just now</span></h5>"+data.comment+"</div></div>";
            //            $('#new_comment_'+id).append(post);
            //           alert('done 2');
            //
            //        },'json');
            //       //return false;
            //    });
        }



    });



    //Handle favorites
    //$(document).on('click', '.starBtn', function(){
    //    var id = $(this).data('id');
    //    var flagged = $(this).data('flagged');
    //    if(flagged == '1'){
    //        $(this).find('i').removeClass('fa-star').addClass('fa-star-o');
    //        $(this).data('flagged', 0);
    //    } else {
    //        $(this).find('i').removeClass('fa-star-o').addClass('fa-star');
    //        $(this).data('flagged', 1);
    //    }
    //
    //    $.ajax({
    //        url: "/post/favorite?id=" + id,
    //        type: "POST"
    //    }).success(function (data) {
    //
    //    });
    //});

});

// patch3

//hyperlink post

function hyperlink(){
   //$('.items').each(function(){
   //     // Get the content
   //     var str = $(this).html();
   //     // Set the regex string
   //     var regex = /(https?:\/\/([-\w\.]+)+(:\d+)?(\/([\w\/_\.]*(\?\S+)?)?)?)/ig
   //     // Replace plain text links by hyperlinks
   //     var replaced_text = str.replace(regex, "<a href='$1' target='_blank'>$1</a>");
   //     // Echo link
   //     $(this).html(replaced_text);
   // });
}

// patch3