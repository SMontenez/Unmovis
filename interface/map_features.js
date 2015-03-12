// All the Google Maps features : initialization of the map, creation or removal of certain elements (markers, arrows, infowindows)

var map;
var overlay;

var limitDates;
var markers;
var displayedMarkers;
var infoWindows;
var arrows;
var infoWindowsNb; // To count the number of opened infoWindows


// Initializes the map template
function initializeMap() {
    var mapOptions = {
        center: new google.maps.LatLng(50,0),
        zoom: 3,
        minZoom: 3,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        disableDefaultUI: true
    };

    overlay = new google.maps.OverlayView();
    var mapCanvas = document.getElementById("map-canvas");
    map = new google.maps.Map(mapCanvas, mapOptions);

    overlay.draw = function() {};
    overlay.setMap(map);
}

// Creates all the markers corresponding to the data locations and the users list according to the trustTable
function initialize(data, trustTable) {
    if (markers != undefined) {
        delete_elements();
        delete_arrows();
        $("#close-info").hide();
        $("#users-list>div").remove();
    }

    limitDates = [];
    markers = [];
    displayedMarkers = [];
    infoWindows = [];
    arrows = [];
    infoWindowsNb = 0; // To count the number of opened infoWindows

    create_users_list(trustTable);
    for (var num=0 ; num<data.length ; num++) create_marker(num, data[num], trustTable);

    replace_counts(true);

    return limitDates;
}


// Creates a marker corresponding to 1 location, but hide it from the map
function create_marker(chronoOrder, infos, trustDic){
    var id = infos[0];
    var user = infos[1];
    var date = infos[2];
    var urlPages = infos[3][1]["page"]
    var urlSources = infos[3][1]["source"]
    var loc = infos[5]
    var filters = infos[6]
    // To display several pictures
    /*var urlPages = [];
    var urlSources = [];
    for (var i=1 ; i<infos[3].length; i++) {
        urlPages.push(infos[3][i]["page"]);
        urlSources.push(infos[3][i]["source"]);
    }*/

    var pos = new google.maps.LatLng(loc[0], loc[1]);

    // We convert the data dates into the JS date format to 
    // prepare the future dates comparisons and then we keep the 
    // min and max dates into a 2 elements array for a future use
    var markerDate = $.datepicker.parseDate("yy-mm-dd", date.split(" ")[0]);
    if (limitDates.length == 0) {
        limitDates.push(markerDate, markerDate);
    }
    else {
        if (markerDate < limitDates[0]) limitDates[0] = markerDate;
        else if (markerDate > limitDates[1]) limitDates[1] = markerDate;
    }

    // We determine if the marker is more or less certain
    if (filters[0] == 0 && filters[1] == 0 && filters[2] == 0) {
        var typeOfMarker = "correct";
    }
    else {
        var typeOfMarker = "uncertain";
    }

    // We create the marker and give him all the important 
    // informations for future operations 
    var marker = new google.maps.Marker({
        position: pos,
        map: map,
        order: chronoOrder,
        rawDate: date,
        date: markerDate,
        icon: icons[typeOfMarker].icon,
        type: typeOfMarker,
        onLand: filters[0],
        impJourney: filters[1],
        outlier: filters[2],
        user: user["userID"],
        trust: trustDic[user["userID"]][0]
    });

    if (urlSources != []) {
        create_infowindow(id, urlPages, date);
    }
    else {
        $("<div>")
            .attr("id", id)
            .css("display", "none")
            .text("No image")
            .appendTo($("body"));
    }

    var info = new google.maps.InfoWindow({
        content : document.getElementById(id),
        map : map,
        position : pos
    });


    info.setMap(null);
    infoWindows.push(info);

    google.maps.event.addListener(marker, 'click', function(){
        infoWindowsNb += 1;
        info.setMap(map);

        if (urlSources != []) {
            $("#image" + id).attr("src", urlSources);
        }

        $("#" + id).show();

        if (infoWindowsNb >= 1 && $("#close-info").css("display") == "none") {
            $("#close-info").css("display", "block");
        }
    });
    google.maps.event.addListener(marker, 'mouseover', function(e){
        var projection = overlay.getProjection();
        var pixel = projection.fromLatLngToContainerPixel(this.getPosition());

        trustPercentage = (this.trust*100).toString() + "%";

        $("#username").text(user["username"]);
        $("#trust").text(trustPercentage);
        $("#marker-popup")
            .css("top", pixel.y-$("#marker-popup").outerHeight()-10)
            .css("left", pixel.x-($("#marker-popup").outerWidth()/2))
            .show();
    });
    google.maps.event.addListener(marker, 'mouseout', function(e){
        $("#marker-popup").hide(); 
    });

    // Here we put the marker of all the markers, this will be useful 
    // in order to replace the showed markers when options will be 
    // chosen by the user (especially when he changes the dates)
    displayedMarkers.push(marker.order);
    markers.push(marker);
}


function delete_elements() {
    for (var i=0 ; i<markers.length ; i++) {
        markers[i].setMap(null);
        markers[i] = null;
    }
    for (var i=0 ; i<infoWindows.length ; i++) {
        infoWindows[i].setMap(null);
        infoWindows[i] = null;
    }
}

// Create the arrows that represents the chronological order of the markers
function show_arrows() {
    var lineSymbol =  {
        path: 'M 0,-1 0,2',
        strokeOpacity: 1,
    };

    var arrowSymbol = {
        path: 'M -2,3 0,0 2,3',
        strokeOpacity: 1,
        scale: 4
    }


    for (var i=0 ; i<displayedMarkers.length-1 ; i++) {
        startMarker = markers[displayedMarkers[i]];
        endMarker = markers[displayedMarkers[i+1]];
        var lineCoordinates = [startMarker.position, endMarker.position];

        // Red arrows if the trajectory is far fetched, grey otherwise
        if (startMarker.impJourney != 0 && endMarker.impJourney != 0) var color = "#ED1C35";
        else var color = "#919191";

        var line = new google.maps.Polyline({
            path: lineCoordinates,
            strokeOpacity: 0,
            strokeColor: color,
            icons: [
              {
                icon: lineSymbol,
                offset: '0',
                repeat: '20px'
              }, {
                icon: arrowSymbol,
                offset: '100%'
              }
            ],
            map: map,
            startMark: startMarker,
            endMark: endMarker
        });

        // Write the position and dates of start and end markers
        google.maps.event.addListener(line, 'click', function() {
            modifyTrajData(this.startMark, this.endMark);
            show_window($("#traj-details"));
        });

        arrows.push(line);
    }
}


function delete_arrows() {
    while (arrows.length > 0) {
        arrow = arrows.shift();
        arrow.setMap(null);
        arrow = null;
    }
}


// This function closes all the infoWindows associated to the used markers
function remove_all_infoWindows() {
    for (var i=0 ; i<infoWindows.length ; i++) {
        infoWindows[i].setMap(null);
    }
}


function replace_markers(correctMarkers, filteredMarkers, dateMin, dateMax, showChrono, minTrust) {
    var MPreciseMarkers = 0;
    var LPreciseMarkers = 0;
    var markerMin = Math.min.apply(Math,displayedMarkers);
    var markerMax = Math.max.apply(Math,displayedMarkers);

    for (var i=0 ; i<markers.length ; i++) {
        var displayIcon = "";
        var user = "#" + markers[i].user.replace("@", "\\@");

        if (markers[i].date>=dateMin && markers[i].date<=dateMax && markers[i].trust >= minTrust && $(user).is(":checked")) {
            if (correctMarkers == true && markers[i].type == "correct") {
                displayIcon = icons["correct"].icon;
                MPreciseMarkers += 1;
            }
            else {
                if (filteredMarkers == "all" && markers[i].type == "uncertain") displayIcon = icons["uncertain"].icon;
                else if (filteredMarkers == "onLand" && markers[i].onLand > 0) displayIcon = icons["onLand"].icon;
                else if (filteredMarkers == "impJourney" && markers[i].impJourney != 0) displayIcon = icons["impJourney"].icon;
                else if (filteredMarkers == "outlier" && markers[i].outlier == 1) displayIcon = icons["outlier"].icon;
                LPreciseMarkers += 1;
            }
        }

        if (displayIcon != "") {
            if (markers[i].icon != displayIcon) markers[i].setIcon(displayIcon);
            if (markers[i].getMap() == null) { 
                markers[i]
                    markers[i].setMap(map);
                displayedMarkers.push(markers[i].order);
            }
        }
        else {
            if (markers[i].getMap() != null) {
                markers[i].setMap(null);
                infoWindows[i].setMap(null);
                remove_from_array(displayedMarkers, markers[i].order);
            }
        }
    }

    displayedMarkers.sort(intSort);

    if (showChrono == "shown") {
        delete_arrows();
        show_arrows();
    }
}
