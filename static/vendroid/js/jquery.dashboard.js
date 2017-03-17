function completeTask(id){
          //  alert(id);

            $.ajax({
                        url: '/tasks/complete/', // the endpoint
                        type: 'post', // http method
                        data: {id:id}, // data sent with the post request

                        // handle a successful response
                        success: function (response) {
                            //alert("success"); // another sanity check
                            if (response == "success") {
                                var task_id = '#checkbox-'+id;
                                $(task_id).attr('checked','true')

                            }
                            if (response == "successFalse"){
                                var task_id = '#checkbox-'+id;
                                $(task_id).attr('checked','false')
                            }


                        },

                        // handle a non-successful response
                        error: function (xhr, errmsg, err) {
                        }
                    });

        }