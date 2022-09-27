var globalValidacion = 1;




var ShowError = function (grp, val, err) {
    $(grp).addClass("has-danger  has-feedback");
    $(val).html('<div class="alert alert-danger" role="alert"> ' + err + '</div>');
    globalValidacion = -1;

};

var ClearError = function (grp, val) {
    globalValidacion = 1;
    $(grp).removeClass("has-danger has-feedback");
    $(val).html('');

};



var ValidateInt = function (input_id, grp, val) {
        valorInt= $(input_id).val();
        pat = /(^[0-9]+$)/;
        result = valorInt.match(pat);

        $(val).html('');
    // If not pass the regex
    if (!result) {
        ShowError(grp, val, 'The value must be a integer number');
        $(input_id).val("");
    }else if(valorInt == 0){
        ShowError(grp, val, 'The value must be more than 0');
        $(input_id).val("");

    } else {
        ClearError(grp, val);
         $(val).html("");

    }
};




var ValidateWithoutSpecial = function (input_id, grp, val) {

        valtxt= $(input_id).val();
        pat = /(^[a-zA-Z0-9_ ]+$)/;
        result = valtxt.match(pat);

        $(val).html('');
    // If not pass the regex
    if (!result) {
        ShowError(grp, val, 'The value must be a text without special characters (except underscore) ');
        $(input_id).val("");
    }else if(valtxt == ""){
        ShowError(grp, val, 'The value must be a text without special characters (except underscore) ');
        $(input_id).val("");

    } else {
        ClearError(grp, val);
         $(val).html("");

    }

};

var ValidateEmptyInputs = function (){

    var isValid = []
    $("input").each(function() {

       var element = $(this);

       if (element.val() == "") {

           if(typeof element.attr('id') !== "undefined")
            {
              isValid.push( element.attr('id'));
            }
       }
    });

    return isValid

}


var enableSaveButton = function (){

        if (globalValidacion == 1){
            console.log(ValidateEmptyInputs())
            emptyArr= ValidateEmptyInputs().length
            if (emptyArr <= 0 ){
                $("#saveProj").attr("disabled",false);
            }else{
                $("#saveProj").attr("disabled",true);
            }

        }else{
            $("#saveProj").attr("disabled",true);
        }



}

var ValidateFile = function (input_id, grp, val,fileType) {

        valFile= $(input_id).val();
        if(fileType == "npz"){
            pat = /(^.*(\.npz|\.NPZ)$)/;

        }else if(fileType == "image"){
            pat = /(^.*(\.bmp|\.dib|\.jpeg|\.jpg|\.jpe|\.jp2|\.png|\.webp|\.pbm|\.pgm|\.ppm|\.pxm|\.pnm|\.pfm|\.sr|\.ras|\.tiff|\.tif|\.exr|\.hdr|\.pic|\.BMP|\.DIB|\.JPEG|\.JPG|\.JPE|\.JP2|\.PNG|\.WEBP|\.PBM|\.PGM|\.PPM|\.PXM|\.PNM|\.PFM|\.SR|\.RAS|\.TIFF|\.TIF|\.EXR|\.HDR|\.PIC)$)/;

        }else{
            pat = /(^.*(\.json|\.JSON)$)/;
        }

        result = valFile.match(pat);

        $(val).html('');
    // If not pass the regex
    if (!result) {
        ShowError(grp, val, 'The file format choosen is not supported');
        $(input_id).val("");
    }else if(valFile == ""){
        ShowError(grp, val, 'Please select an image');
        $(input_id).val("");

    } else {
        ClearError(grp, val);
         $(val).html("");

    }

};

$(document).ready(function () {

    $("#saveProj").attr("disabled",true);

    //ValidateWithoutSpecial('#pName', "#grppName", '#ValidpName');

    $('#pName').change(function () {
        ValidateWithoutSpecial('#pName', "#grppName", '#ValidpName');
     });

     $('#fImg').change(function () {
        ValidateFile('#fImg', "#grpfImg", '#ValidfImg',"image");
     });

     $('#mImg').change(function () {
        ValidateFile('#mImg', "#grpmImg", '#ValidmImg',"image");
     });

    $('#annImage').change(function () {
            var annType = $( 'input[name="annotationType"]:checked' ).attr('value')
            console.log(annType)
            if (annType == "image" ){
                ValidateFile('#annImage', "#grpannImage", '#ValidannImage',"image");
            }else if(annType == "npz"){
                ValidateFile('#annImage', "#grpannImage", '#ValidannImage', "npz");
            }else{
                ValidateFile('#annImage', "#grpannImage", '#ValidannImage', "json");

            }
    });


    $('#nClasses').change(function () {
        ValidateInt('#nClasses', "#grpnClasses", '#ValidnClasses');
     });


    $('.nclass').change(function () {
        idNc =  $(this).attr('id')
        ValidateWithoutSpecial('#'+idNc, "#grp"+idNc, '#Valid'+idNc);
    });


    $('input').change(function () {
        enableSaveButton()

     });







});