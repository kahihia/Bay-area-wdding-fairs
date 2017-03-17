$(document).ready(function() {

    if($("#searchmulti").length > 0){
        $("#searchmulti").chosen();
    }

    $(document).on('change', '#filterForm :input', function(){
        updateForm();
    });

    $("#searchField").keypress(function (e) {
        if (e.which == 13) {
            updateForm();
        }
    });
});

function updateForm(){
    var data = $("#filterForm").serialize();

    if(data != ''){
        $.fn.yiiListView.update('user-list', {
            url: "/directory?1=1&" + data
        });
    } else {
        $.fn.yiiListView.update('user-list');
    }

}