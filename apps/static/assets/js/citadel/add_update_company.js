$(function () {
    var $us_states = {
        "AK": "Alaska", "AL": "Alabama", "AR": "Arkansas", "AS": "American Samoa", "AZ": "Arizona",
        "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DC": "District of Columbia",
        "DE": "Delaware", "FL": "Florida", "FM": "Federated States of Micronesia", "GA": "Georgia",
        "GU": "Guam", "HI": "Hawaii", "IA": "Iowa", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana",
        "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "MA": "Massachusetts", "MD": "Maryland",
        "ME": "Maine", "MH": "Marshall Islands", "MI": "Michigan", "MN": "Minnesota", "MO": "Missouri",
        "MP": "Northern Mariana Islands", "MS": "Mississippi", "MT": "Montana", "NC": "North Carolina",
        "ND": "North Dakota", "NE": "Nebraska", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico",
        "NV": "Nevada", "NY": "New York", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
        "PR": "Puerto Rico", "PW": "Palau", "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota",
        "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VA": "Virginia", "VI": "Virgin Islands", "VT": "Vermont",
        "WA": "Washington", "WI": "Wisconsin", "WV": "West Virginia", "WY": "Wyoming"
    };

    var $ca_states = {
        "AB": "Alberta", "BC": "British Columbia", "MB": "Manitoba", "NB": "New Brunswick",
        "NL": "Newfoundland", "NS": "Nova Scotia", "NT": "Northwest Territories", "NU": "Nunavut",
        "ON": "Ontario", "PE": "Prince Edward Island", "QC": "Quebec", "SK": "Saskatchewan", "YT": "Yukon"
    };

    var $validZipTest = /(^\d{5}$)|(^\d{5}-\d{4}$)/;

    function update_state_options($data_map) {
        var $address_state = $("#address_state");
        $address_state.empty();
        $option = $("<option></option>")
            .attr("value", "-1")
            .text("Choose State");
        $address_state.append($option)
        $.each($data_map, function (key, value) {
            $option = $("<option></option>")
                .attr("value", key)
                .text(value);
            $address_state.append($option)
        });
    }

    //Initialize Select2 Elements
    $('.select2bs4').select2({
        theme: 'bootstrap4'
    })

    // ZIP Code validator
    jQuery.validator.addMethod("zipCodeCheck", function (zip_code, element) {
        return this.optional(element) ||
            zip_code.match("^\\d{5}(-{0,1}\\d{4})?$") ||
            zip_code.match(/^[ABCEGHJ-NPRSTVXY]\d[ABCEGHJ-NPRSTV-Z][ -]?\d[ABCEGHJ-NPRSTV-Z]\d$/i);
    }, "Please provide the valid Address Zip code.");

    // Adding check for default value on select options
    jQuery.validator.addMethod("notEqual", function (value, element, param) {
        return this.optional(element) || value !== param;
    }, "Please choose a value!");

    var $validator = $('#add-update-company-form').validate({
        submitHandler: function (form) {
            form.submit();
        },
        rules: {
            full_name: {
                required: true,
            },
            short_name: {
                required: true,
            },
            address_street_name_line_1: {
                required: true,
            },
            address_country: {
                required: true,
                notEqual: "-1"
            },
            address_city: {
                required: true,
                notEqual: "-1"
            },
            address_state: {
                required: true,
            },
            address_zip: {
                required: true,
                zipCodeCheck: true
            },
        },
        messages: {
            full_name: {
                required: "Please provide the Company full name."
            },
            short_name: {
                required: "Please provide a short name for the Company."
            },
            address_street_name_line_1: {
                required: "Please provide the Street Address"
            },
            address_country: {
                required: "Please choose the Address Country.",
                notEqual: "Please choose the Address Country to populate the States List."
            },
            address_city: {
                required: "Please provide the Address City."
            },
            address_state: {
                required: "Please provide the Address State."
            },
            address_zip: {
                required: "Please provide the Address Zip."
            }
        },
        errorElement: 'span',
        errorPlacement: function (error, element) {
            error.addClass('invalid-feedback');
            element.closest('.form-group').append(error);
        },
        highlight: function (element, errorClass, validClass) {
            $(element).addClass('is-invalid');
        },
        unhighlight: function (element, errorClass, validClass) {
            $(element).removeClass('is-invalid');
        }
    });

    $("#reset-button").click(function () {
        $validator.resetForm();
        //reset the country and states fields
        $("#address_country").val("-1").change();
    });

    $("#address_country").on("change", function () {
        var $option = $(this).find('option:selected');
        var $country = $option.val();
        var $address_state = $("#address_state");
        if ($country == "US") {
            update_state_options($us_states)
        } else if ($country == "CA") {
            update_state_options($ca_states)
        } else {
            $address_state.empty();
        }
    });

    //update the form for state if the form is an update form
    if ($('#form_type').val() == "update") {
        $("#address_country").trigger("change");
        $selected_address_state_val = $("#address_state_option_value_for_update").val()
        $("#address_state option[value='" + $selected_address_state_val + "']").attr("selected", "selected");
    }

});

