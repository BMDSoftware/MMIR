$(document).ready( function () {
    $('#table1').DataTable();

    addElements();
    addClassName();



    $( 'input[name="annotationType"]' ).click(function() {

         addElements();

         $('#annImage').change(function () {
                var annType = $( 'input[name="annotationType"]:checked' ).attr('value')

                if (annType == "image" ){
                    ValidateFile('#annImage', "#grpannImage", '#ValidannImage',"image");
                }else if(annType == "npz"){
                    ValidateFile('#annImage', "#grpannImage", '#ValidannImage', "npz");
                }else{
                    ValidateFile('#annImage', "#grpannImage", '#ValidannImage', "json");

                }


        });


        enableSaveButton()





    });




    $( "#more" ).click(function() {
       if(algoritmLength > cont+1){
            cont= cont + 1;
            var newId = "id='alg" + cont +"'"
            //array for validation of the algorithms options
            //contain all the options selected previosly for not used twice
            let arrVal = []
            for(i=0;i<cont;i++){
                valSelect = $("#" + "alg" + i + " option:selected").text();
                arrVal.push(valSelect);
            }

            //creation of new option values
            let options = []
            for(i = 0; i < arr.length; i++){
                if (!(arrVal.includes(arr[i]))){
                    options.push(arr[i]);

                }
            }

            let stringOptions = ""
            for (i=0; i < options.length; i++){
                stringOptions =  stringOptions + "<option>"+options[i]+"</option>"
            }



            $( "#Algorithms" ).append( "<div "+ newId +
                                    " class='input-group mb-3' > <span class='input-group-text' >Algorithm</span>"+
                                    " <select "+ "id='selectAl" + cont +"'"+  "name='alg" + cont +"'" +    "   class='form-select'> "+ stringOptions +"</select>" +
                                    "</div>" );

            $("#less").attr("disabled",false);
            $("#" + "selectAl" + (cont-1)).attr("disabled",true);

      }else{
        $(this).attr("disabled", true);
      }

       $("#algNum").val(cont);
    });

    $( "#less" ).click(function() {

        if (cont > 0) {

            $( "#alg"+ cont ).remove();
            cont= cont - 1;
            $("#" + "selectAl" + cont ).attr("disabled",false);
            if(algoritmLength > cont+1){
                $("#more").attr("disabled",false);
            }

        }else{
            $(this).attr("disabled", true);
        }

        $("#algNum").val(cont);

    });


    $('#savingNewProject').on('submit', function() {
        $('input, select').prop('disabled', false);
    });




    } );


    function addClassName(){


        $('#classesNames').empty();

        var nC =  $("#nClasses").val()
        console.log(nC)

        if(globalValidacion == 1){
            if (nC > 0){


                for(i=1;i<=nC;i++){
                    $( "#classesNames" ).append('<div class="col-md-6 p-1">'+
                                                              '<div class="input-group " id="grpnameclass'+i +' ">'+
                                                                '<span class="input-group-text" id="basic-addon1">Name of class '+ i +  '</span>'+
                                                                '<input name="nameclass'+i+'" id="nameclass'+i+'" type="text" class="form-control nclass" >'+

                                                               '</div>'+
                                                               '<div id="Validnameclass'+ i +'" ></div>'+
                                                 '</div>')

                }


                $('.nclass').change(function () {
                    idNc =  $(this).attr('id')
                    ValidateWithoutSpecial('#'+idNc, "#grp"+idNc, '#Valid'+idNc);
                    enableSaveButton()
                 });


            }
        }



    }



    function addElements(){



       $('#extraAnnInfo').empty();

       var annType = $( 'input[name="annotationType"]:checked' ).attr('value')



       if( annType == "image" | annType == "npz" ){

            $( "#extraAnnInfo" ).append('<div class="row p-3 ">'+
                                            '<div class="col-md-6 offset-md-3" id="grpnClasses">'+
                                                  '<div class="input-group ">'+
                                                      '<span class="input-group-text" id="basic-addon1">Number of classes</span>'+
                                                      '<input name="nClasses" id="nClasses" type="number" min="1" class="form-control" value="1">'+
                                                  '</div>'+
                                                  '<div id="ValidnClasses" ></div>'+
                                            '</div>'+
                                        '</div>'+
                                        '<div id="classesNames" class="row p-3"></div>')


            $( "#extraAnnInfo" ).append('<div id="grpannImage">'+
                "<label for='annImage' class='form-label '>Annotation file</label>"+
                "<input id='annImage' name ='annImage' class='form-control' type='file' >"+
                '<div id="ValidannImage" ></div>'+
                '</div>')

            addClassName();



       }else if(annType == "json"){

        $( "#extraAnnInfo" ).append('<div id="grpannImage">'+
                "<label for='annImage' class='form-label '>Annotation file</label>"+
                "<input id='annImage' name ='annImage' class='form-control' type='file' >"+
                '<div id="ValidannImage" ></div>'+
                '</div>')

       } else{


       }




       $("#nClasses").change(function(){


        ValidateInt('#nClasses', "#grpnClasses", '#ValidnClasses');

        addClassName()


         enableSaveButton()






        });



};

