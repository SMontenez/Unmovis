// Handles all the dynamic interactions that can happen between the user and the "display informations" interface


// Initializes the interface when the user performs the first search
function display_interface() {
    $(function() {
        $(".window button").click(function() {
            $(this).parent().hide(); 
            $(".overlay").hide();
            if ($(this).parent().attr("id") == "users-list") {
                alert("Recalculate without users");
            }
        });


        // ----------   VISUALISATION OPTIONS   -----------------

        $("#visu-options").css("top", $("#boat-and-date").offset().top + $("#boat-and-date").outerHeight(true) + 20).show();

        $(".hide").click(function() {
            if ($(this).val() == "shown") {
                $(this).parent().nextAll().hide();
                $(this).text("Show").val("hidden");
            }
            else {
                $(this).parent().nextAll().show();
                $(this).text("Hide").val("shown");
            }
        });

        var colors = {"all":"#B00202", "onLand":"#038C15", "outlier":"#F3FF85", "impJourney":"#FC9AF4"};

        $("#filter-choice").change(function() {
            var color = colors[$(this).find(":selected").attr("value")]
            $(this).css("background-color", color);
        refresh_visu();
        });

        $("#not-filtered").change(function() {
            refresh_visu();
        });

        $("#filtered").change(function() {
            filtered = $(this).is(":checked");
            $("#filter-choice").css("display", filtered?"inline":"none") 
            refresh_visu();
        });

        $("#chrono").click(function() {
            if ($(this).val() == "hidden") {
                $(this).text("Hide chronological order").val("shown");
                show_arrows();
            }
            else if ($(this).val() == "shown") {
                $(this).text("Show chronological order").val("hidden");
                delete_arrows();
            }
        });

        $("#close-info").click(function() {
            remove_all_infoWindows();
            $(this).hide();
            infoWindowsNb= 0;
        });


        // ------------   BOAT INFORMATIONS   ---------------

        $("#boat-infos").css("top", $("#boat-and-date").offset().top + $("#boat-and-date").outerHeight(true) + 20).show();

        $("#infos-name").hide();
        $("#infos-value").hide();

        $(".infos>div").mouseover(function(e) {
            id = "#complete-" + $(this).attr("class")
            $(id).show();
        });
        $(".infos>div").mousemove(function(e) {
            id = "#complete-" + $(this).attr("class")
            $(id).css({"top":e.pageY-$(id).outerHeight()-15, "left":e.pageX-($(id).outerWidth()/2)});
        });
        $(".infos>div").mouseout(function() {
            id = "#complete-" + $(this).attr("class")
            $(id).hide();
        });


        // ------------   USERS TRUST DISPLAY   ---------------

        $("#users-trust").css("display", "inline-block");

        $("#trust-slider").slider({
            range: "max",
            min: 0,
            max: 100,
            slide: function(event, ui) {
                $("#tooltip").text(ui.value + "%");
                refresh_visu();
            }
        });
        $("#trust-slider").on("slidechange", function(event, ui) {
            refresh_visu();
        });
        $("#tooltip").text($("#trust-slider").slider("value") + "%");

        setTrustPositions();

        $("#users-trust span").click(function() {
            show_window($("#users-list"));
            $("#users-list").css("width", $("#users-list>div").width() + $("#users-list").children("div").last().children("span").width() + 10);
        });

        $("#users-list>button").click(function() {
            $(".overlay").hide();
            $("#users-list").hide();
            refresh_visu();
        });
    });
}


// Initializes the date-slider with the min and max dates given as parameters
function display_date_choice(minDate, maxDate) {
    $(function() {

        $("#date-choice").show();

        $("#start-date")
        .datepicker({
            changeMonth: true,
            changeYear: true
        })
    .change(function() {
        syncSlider(minDate, maxDate);
        refresh_visu();
    });


    $("#end-date")
        .datepicker({
            changeMonth: true,
            changeYear: true
        })
    .change(function() {
        syncSlider(minDate, maxDate);
        refresh_visu();
    });

    var numberOfDays = daysDiff(minDate, maxDate);
    $("#dates-slider").slider({
        range: true,
        max: numberOfDays,
        values: [0, numberOfDays],
        slide: function(event, ui) {
            var date = new Date(minDate.getTime());
            date.setDate(date.getDate() + ui.values[0]);
            $('#start-date').val($.datepicker.formatDate('mm/dd/yy', date));
            date = new Date(minDate.getTime());
            date.setDate(date.getDate() + ui.values[1]);
            $('#end-date').val($.datepicker.formatDate('mm/dd/yy', date));
            refresh_visu();
        }
    });
    $("#dates-slider").on("slidechange", function(event, ui) {
        refresh_visu();
    });
    $('#start-date').val($.datepicker.formatDate('mm/dd/yy', minDate));
    $('#end-date').val($.datepicker.formatDate('mm/dd/yy', maxDate));

    setDatesPositions();

    });
}


// Fill the "General Information" window with the appropriate data given as parameter
function display_boat_infos(simpleInfos, completeInfos) {
    $(function(){
        // ----------   BOAT INFORMATIONS   -----------------

        for (var info in simpleInfos) {
            $("#" + info)
        .text(simpleInfos[info].join(" / "))
        }

        for (var info in completeInfos) {
            infoValues = completeInfos[info];
            for (var site in infoValues) {
                id = "#complete-" + info + " ." + site;
                value = infoValues[site];
                if (value != "") $(id).text(value);
                else $(id).text("-"); 
            }
        }
    });
}


    // Creates an infoWindows displaying the picture located at urlPage and its date
function create_infowindow(id, urlPage, date) {
    $("<div>")
        .attr("id", id)
        .attr("class", "infoW")
        .css("display", "none")
        .append($("<span>").attr("id", "loading" + id))
        .append($("<div>").append($("<a>").attr("id", "img-link" + id)))
        .append($("<span>").attr("id", "date" + id))
        .appendTo($("body")); 

    $("#loading" + id)
        .text("Loading image...")
        .css("font-size", "16px")
        .css("font-weight", "bold")
        .css("margin", "10px");

    $("#img-link" + id)
        .attr("href", urlPage)
        .attr("target", "_blank")
        .css("margin", "20px")
        .css("display", "none")
        .append($("<img>").attr("id", "image" + id));

    $("#date" + id)
        .text("Date : " + date)
        .css("display", "none")
        .css("font-weight", "bold");

    $("#image" + id).load( function(){
        $("#loading" + id).remove();
        $("#img-link" + id).show();
        $("#date" + id).show();
    });
}


// Configure the window that opens when the user clicks on "User trust score", it displays all the Flickr users concerned by the selected boat with their own trust score 
function create_users_list(trustTable) {
    var listUsers = [];
    for (var id in trustTable) {
        subList = trustTable[id];
        subList.push(id);
        listUsers.push(subList);
    }
    listUsers.sort(firstElementIntInvSort);

    var maxWidth = 0
        for (var i=0 ; i<listUsers.length ; i++) {
            user = listUsers[i];

            $("#users-list")
                .prepend($("<div>").attr("id", i.toString()).css("text-align", "left"));


            $("<input>")
                .attr("type", "checkbox")
                .attr("class", "user")
                .attr("id", user[2]) 
                .attr("checked", "checked")
                .css("margin", "10px 5px")
                .appendTo("#users-list #" + i.toString());

            $("#users-list #" + i.toString())
                .append(user[1]);

            $("<span>")
                .css("font-weight", "bold")
                .css("float", "right")
                .css("margin-top", "9px")
                .text((user[0]*100).toString() + "%")
                .appendTo("#users-list #" + i.toString());

        }

    if ($("#users-list").outerHeight() > 0.75*$(document).height()) {
        $("#users-list")
            .css("height", 0.75*$(document).height())
            .css("overflow-y", "auto"); 
    }

    $("#users-list .button").click
}


// Used when a modification for the markers visualisation happens (change of the date-slider, different filtering, contributor deselected, ...), get the new variables and calls the appropriate "map_features.js" functions 
function refresh_visu() {
    $(function() {
        var valDateMin = $.datepicker.parseDate("mm/dd/yy", $("#start-date").val());
        var valDateMax = $.datepicker.parseDate("mm/dd/yy", $("#end-date").val());

        var seeCorrectLoc = $("#not-filtered").is(":checked");
        if ($("#filtered").is(":checked") == true) var seeFilteredLoc = $("#filter-choice").val();
        else var seeFilteredLoc = false;

        var minTrust = $("#trust-slider").slider("value") / 100;

        setDatesPositions();
        setTrustPositions();

        replace_markers(seeCorrectLoc, seeFilteredLoc, valDateMin, valDateMax, $("#chrono").val(), minTrust);
        if (seeCorrectLoc == false || seeFilteredLoc == false) replace_counts(false);
        else replace_counts(true);
    });
}


// Synchronize the slider handles when the date is changed manually
function syncSlider(minDate, maxDate) {
    $(function() {
        var start = daysDiff(minDate, $("#start-date").datepicker('getDate') || minDate);
        var end = daysDiff(minDate, $("#end-date").datepicker('getDate') || maxDate);
        start = Math.min(start, end);
        $("#dates-slider").slider('values', 0, start);
        $("#dates-slider").slider('values', 1, end);

        $("#start-date").datepicker('option', 'maxDate', $("#end-date").datepicker('getDate') || maxDate);
        $("#end-date").datepicker('option', 'minDate', $("#start-date").datepicker('getDate') || minDate); 
    });
}


// Get the dates input tag and the count number to follow the handlers when they are moved
function setDatesPositions() {
    leftHandler = $("#dates-slider").children(".ui-slider-handle").first();
    rightHandler = $("#dates-slider").children(".ui-slider-handle").last();
    range = $("#dates-slider").children(".ui-slider-range");

    startDate = $("#start-date");
    endDate = $("#end-date");
    count = $("#number");

    // If the handlers are so close that the input tags get over each other
    if (rightHandler.offset().left < leftHandler.offset().left + startDate.width() + 10) {
        startDate.css("top", leftHandler.offset().top - startDate.outerHeight(true)/2);
        startDate.css("left", leftHandler.offset().left - startDate.width() - leftHandler.width());
    }
    // When the handlers are far away
    else {
        startDate.css("top", leftHandler.offset().top + startDate.outerHeight(true) - 10);
        startDate.css("left", leftHandler.offset().left - (startDate.width() - leftHandler.width())/2 - 15);
    }
    endDate.css("top", rightHandler.offset().top + endDate.outerHeight(true) - 10);
    endDate.css("left", rightHandler.offset().left - (endDate.width() - rightHandler.width())/2 - 15);


    // When the handlers are far away
    if (range.width() > count.outerWidth(true) + 25) count.css("top", range.offset().top + (range.height() - count.height())/2 - 15);
    //If the handlers are so close that the count number can't be siplayed between them
    else count.css("top", range.offset().top + (range.height() - count.height())/2 - 35);
    count.css("left", range.offset().left + (range.width() - count.outerWidth())/2 - 10);
}


// Creates the users trust interface
function setTrustPositions() {
    var slider = $("#trust-slider");
    var sliderPos = slider.offset();
    var handler = $("#trust-slider").children(".ui-slider-handle");
    var handlerPos = handler.offset();
    var relativePos = $("#users-trust").offset();

    $("#users-trust .legend")
        .css("top", sliderPos.top - relativePos.top - 3) 
        .css("left", sliderPos.left + slider.outerWidth() -  relativePos.left + 7);

    $("#tooltip")
        .css("top", handlerPos.top - relativePos.top + 2)
        .css("left", handlerPos.left - relativePos.left - ($("#tooltip").outerWidth() + handler.outerWidth()) + 5)
}


// Changes the counts accordingly to the system variables (if show is True then counts are displayed for less and more precise locations, if not only the total count is displayed on the date slider)
function replace_counts(show) {
    var total = displayedMarkers.length;
    if (show == true) {
        var M = 0;
        var L = 0;

        for (var i=0 ; i<total ; i++) {
            if (markers[displayedMarkers[i]].type == "correct") M += 1;
            else L += 1;
        }

        total = total.toString();
        M = M.toString();
        L = L.toString();

        $("#number").text(total);
        $("#not-filtered+span").text(M + " / " + total).show();
        $("#filtered+span").text(L + " / " + total).show();
    }
    else {
        $("#number").text(total.toString());
        $("#not-filtered+span").hide();
        $("#filtered+span").hide();
    }
}


// Modify the #traj-details div of the DOM according to the arrow clicked
function modifyTrajData(start, end){
    var fromVal = $("#start-marker").children().eq(2).children();
    var toVal = $("#end-marker").children().eq(2).children();
    var totals = $("#totals").children().eq(2).children();

    var startPos = start.position;
    var startDate = start.rawDate;
    var endPos = end.position;
    var endDate = end.rawDate;

    fromVal.eq(0).text(startPos);
    fromVal.eq(1).text(startDate);
    toVal.eq(0).text(endPos);
    toVal.eq(1).text(endDate);

    var dist = distance(startPos, endPos);
    var time = dateDiff(startDate, endDate);
    var reqSpeed = Math.floor(dist/time * 0.539956803);
    var maxSpeed = moySpeed($("#Speed").text());

    totals.eq(0).text(dist + " km");
    totals.eq(1).text(time + " hours");
    totals.eq(2).text("~ " + reqSpeed + " knots");
    totals.eq(3).text("~ " + maxSpeed + " knots");
}


// Take the div and displays it like a window centered on the screen, on top of an overlay that prevents any interaction with the system except with the div
function show_window(div) {
    // Get the screen height and width
    var maskHeight = $(document).height();
    var maskWidth = $(window).width();

    // Values for center alignment
    var dialogTop = (maskHeight - div.outerHeight())/2 ;
    var dialogLeft = (maskWidth - div.outerWidth())/2;

    $(".overlay").css({height:maskHeight, width:maskWidth}).show();
    div.css({"top":dialogTop, "left":dialogLeft}).show();
}
