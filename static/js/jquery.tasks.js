$(document).ready(function() {

    if($("#assigned_to_add").length > 0){
        $("#assigned_to_add").chosen();
    }

    //$(".add-task").click(function(){
    //    $.ajax({
    //        url: "/tasks/list",
    //        type: "POST"
    //    }).success(function(newOptions){
    //        var $el = $("#Task_task_list_id");
    //        $el.empty(); // remove old options
    //        newOptions = jQuery.parseJSON(newOptions);
    //        $el.append($("<option></option>").attr("value", '').text('Choose List'));
    //        $.each(newOptions, function(value,key) {
    //          $el.append($("<option></option>").attr("value", value).text(key));
    //        });
    //    });
    //});
    //
    //$(document).on('click', ".task-listen", function(){
    //    var id = $(this).data('id');
    //
    //    $.ajax({
    //        url: "/tasks/edit?id=" + id,
    //        type: "POST"
    //    }).success(function(response){
    //        $("#editTaskBody").html(response);
    //        $("#editTaskModal").modal('show');
    //    });
    //});
    //
    //$(document).on('click', "#editTaskSubmitBtn", function(){
    //    var formData = $("#editForm").serialize();
    //    var id = $("#editForm").data('id');
    //
    //    $.ajax({
    //        url: "/tasks/edit?id=" + id,
    //        data: formData,
    //        type: "POST"
    //    }).success(function(response){
    //
    //    });
    //
    //    $("#editTaskModal").modal('hide');
    //});
    //
    //$("#createTodoBtn").click(function(){
    //    var formData = $("#addTodoModalForm").serialize();
    //    //debug
    //    //patch4
    //    // console.log(formData);
    //    $.ajax({
    //        url: "/tasks/create",
    //        data: formData,
    //        type: "POST"
    //    }).success(function(){
    //        $(':input','#addTodoModalForm')
    //            .not(':button, :submit, :reset, :hidden')
    //            .val('')
    //            .removeAttr('checked')
    //            .removeAttr('selected');
    //        $.fn.yiiListView.update("task-list");
    //        $.fn.yiiListView.update("friend-list");
    //    });
    //})

//delete task functionality
//seth
//    $(document).on('click', ".deleteGroupBtn", function(){
//        var id = $(this).data('id');
//        var element = $(this);
//
//        bootbox.confirm("Are you sure you wish to delete this task ?", function(result) {
//            if (!result) return;
//            $.ajax({
//                url: "/tasks/deletelist?id=" + id,
//                type: "POST"
//            }).success(function(){
//                element.parents('.task').parent().remove();
//                $.fn.yiiListView.update("task-group-list");
//            });
//        });
//
//    });
////delete task functionality
////seth
//    $(document).on('click', ".markTask", function(){
//        var id = $(this).data('id');
//
//        var element = $(this);
//
//        var listElem = element.parent().parent();
//        var childElem = element.find('i');
//
//        var value = 1;
//        if(listElem.hasClass('complete')){
//            listElem.removeClass('complete');
//
//            childElem.removeClass('fa-check');
//            childElem.addClass('fa-circle-o');
//            value = 0;
//        } else {
//            listElem.addClass('complete');
//            childElem.removeClass('fa-circle-o');
//            childElem.addClass('fa-check');
//        }
//
//        $.ajax({
//            url: "/tasks/completed?id=" + id + "&value=" + value,
//            type: "POST"
//        });
//    });
//
//    $("#addTaskBtn").click(function(){
//        bootbox.prompt("Enter a name for your new task list.", function(result) {
//            if (!result) return;
//            $.ajax({
//                url: "/tasks/createGroup?name="+result,
//                type: "POST"
//            }).success(function(){
//                $.fn.yiiListView.update("task-group-list");
//            });
//        });
//
//    });


});
