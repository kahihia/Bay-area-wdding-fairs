

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
            var link_bg_reg = '/bride-groom-registration/';
            $('#show_reg_id').attr('href',link_bg_reg+'?show='+obj.id)
            $('#updates').html(obj.description)
            $('#show-name').html(obj.name)
            $('#show-location').html(obj.date+' | '+obj.short_location)
            $('#location-id').html(obj.location)
            // $('#location-iframe').attr('src',obj.geo_location+"?api_key=AIzaSyB9cPOKyo2rN35p75FFb2CcF3iLlQkAE0I")
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
