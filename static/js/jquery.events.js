/**
 * Created by Robin on 8/25/2015.
 */
$(document).ready(function() {
    //$("#assigned_to").();

    //$(document).on('click', '.viewEvent', function() {
    //    var id= $(this).data('id');
    //    $.ajax({
    //        url: "/events/load?asModal=true&id="+id,
    //        type: "POST"
    //    }).success(function(result){
    //        $("#viewEventModalBody").html(result);
    //        $("#viewEventModal").modal('show');
    //
    //    });
    //});

    //$(".addEventBtn").click(function(){
    //    $("#addEventModal").modal('show');
    //    $(".fc").fullCalendar('refetchEvents');
    //});
    //
    //
    //$(".deleteEventBtn").click(function(){
    //    var id = $(this).data('id');
    //    var element=$(this);
    //
    //    bootbox.confirm("<h3>Are you sure you wish to delete this event?</h3>", function(result) {
    //        if (!result) return;
    //        element.parent().parent().remove();
    //        $.ajax({
    //            url: "/events/deleteEvent?id=" + id,
    //            type: "POST"
    //        }).success(function(result){
    //            $(".fc").fullCalendar('refetchEvents');
    //            $.fn.yiiListView.update("event-list");
    //        });
    //     });
    //  });


    //$(document).on('click', '#submitEditBtn', function(){
    //    var formData = $("#editEventForm").serialize();
    //
    //    $.ajax({
    //        url: "/events/edit",
    //        data: formData,
    //        type: "POST"
    //    }).success(function(result){
    //        $(".fc").fullCalendar('refetchEvents');
    //        $.fn.yiiListView.update("event-list");
    //    });
    //});


    //$(document).on('click', '#createEventButton', function(){
    //
    //    var formData = $("#createEventForm").serialize();
    //
    //    $.ajax({
    //        url: "/events/create?ajax=true",
    //        data: formData,
    //        type: "POST"
    //    }).success(function(result){
    //        $(".fc").fullCalendar('refetchEvents');
    //        $.fn.yiiListView.update("event-list");
    //    });
    //});



    //$('#calendar').fullCalendar({
    //    //events: source,
    //    header: {
    //        left: 'prev,next today',
    //        center: 'title',
    //        right: ''
    //    }
    //    //eventRender: function (event, element)
    //    //{
    //    //    element.attr('href', '#');
    //    //}
    //})


});

 function deleteEvent(id) {
         bootbox.confirm("<h3>Are you sure you wish to delete this event?</h3>", function(result) {
            if (!result) return;
             else {
                var formID = '#eventDeleteForm_' + id;
                $.ajax({
                    url: $(formID).attr('action'), // the endpoint
                    type: $(formID).attr('method'), // http method
                    data: $(formID).serialize(), // data sent with the post request

                    // handle a successful response
                    success: function (response) {
                        //alert("success"); // another sanity check
                        if (response == "success") {
                            $('#media_' + id).attr('hidden', 'hidden');
                            $('#calendar').fullCalendar('refetchEvents')
                        }

                    },

                    // handle a non-successful response
                    error: function (xhr, errmsg, err) {

                    }
                });
            }
        });


    };


//
//$(document).ready(function() {
//    $(".addEventBtn").click(function(){
//        $.ajax({
//            url: "/events/",
//            type: "POST"
//        }).success(function(newOptions){
//            var $el = $("#Event_event_list_id");
//            $el.empty(); // remove old options
//            newOptions = jQuery.parseJSON(newOptions);
//            $el.append($("<option></option>").attr("value", '').text('Choose List'));
//            $.each(newOptions, function(value,key) {
//              $el.append($("<option></option>").attr("value", value).text(key));
//            });
//        });
//    });
//
//
//    $(".add-calendar").click(function(){
//        $('#calendar').fullCalendar({
//            // put your options and callbacks here
//            weekends: false
//        })
//    });
//
//});