var tpj = jQuery;

var revapi30;

function get_information(event_id){
    $.ajax({
        url: "/our-events/",
        type: "POST",
        data: {
            'event_id': event_id,
        },

        success: function (data) {
            var obj = jQuery.parseJSON(data);
            console.log(obj.image)
            $('#show_reg_id').attr('href','{% url "index__bride_groom_registration" %}'+'?show='+obj.id)
            $('#updates').html(obj.description)
            $('#show-name').html(obj.name)
            $('#show-location').html(obj.date+' | '+obj.location)
            $('#location-id').html(obj.location)
            $('.map').attr('data-map-address',obj.location)
            $('#date-time-id').html(obj.date)
            $('#show-image').attr('src',obj.image)
            $('#grand').html(obj.description_grand)
            $('#modal-detail').modal('show')
        },

        error: function(error) {
            console.log("error: "+error.message);

        }
    })
}

$(document).ready(function(){
    $("#slider-carousel").owlCarousel({
        autoplayTimeout:20000
    });
});