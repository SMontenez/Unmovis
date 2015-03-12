// Handles all the process that allows an user to select the object he wants to retrieves informations about (displays the options and process the user's choices)
function get_boat_selection() {
    $(function() {

        firstSearch = true;
        initializeMap();

        // AJAX request to get the boats name and put them into a list
        var boats = readFile("../data/listBoats.txt");
        boats = boats.split("\n");
        boats.pop();

        // For each boat we create an option tag that we append to the select tag
        for (var i=0 ; i<boats.length ; i++) {
            $("<option>").append(boats[i]).appendTo($("#boats-list"));
        };
        $("#boats-list").prop("selectedIndex", -1);

        // The "cross" button to delete what is written in the online search zone
        $("#choice-user").children().eq(1).click(function() {
            $(this).prev("input").val("").focusout();
        });


        // If the user has chosen a boat in the predefined list
        $("#boats-list").change(function() {
            boatName = $("#boats-list").val();
            get_informations(firstSearch, boatName);
            firstSearch = false;
        });

        // Behavior when a user starts to type a name for the online search
        $("#user-boat")
            .focus(function() {
                // A validation button appears to launch the search
                $("#validation")
                    .prop("disabled", false)
                    .css("visibility", "visible");
                // The predefined list isn't accessible until the focus goes out of the text area AND the tet area is empty
                $("#boats-list")
                    .prop("disabled", true)
                    .css("background-color", "gray");
            })
            .focusout(function() {
                if ($(this).val() == "") {
                    $("#validation")
                        .prop("disabled", true)
                        .css("visibility", "hidden");
                    $("#boats-list").prop("disabled", false).css("background-color", "buttonface");
            }
        });

        // When the user starts the online search, a configuration window is opened
        $("#validation").click(function() {
            show_window($("#search-options"))
        });

        // Once the user has chosen the options, the search begins (not implemented yet)
        $("#search-ok").click(search_ok);

        $("#search-valid").children().eq(0).click(start_search);
        $("#search-valid").children().eq(1).click(abort_search);
        $("#abort-ok").click(abort_search);

        /*if (firstSearch) {
          display_interface();
          firstSearch = false;
          }
          launch_research(parameters);
          get_informations(firtSearch, parameters["boat-name"]);
          firstSearch = False;*/
    });
}


function search_ok() {
    parameters = {"boatName": $("#user-boat").val(), "locations": $("#locations").is(":checked"), "details": $("#details").is(":checked")};

    // Ajax request, to search the number of result we can find with this boat name
    $.ajax({
        url: "/cgi-bin/get_estimation.py",
        type: "POST",
        data: parameters
    }).done(function(response){
        console.log("AJAX done, response : " + response + "---");
        $("#search-options").hide()
        if (response.indexOf("Abort") != -1) {
            show_window($("#search-aborted"));
        }
        else {
            show_window($("#search-validation"));
            $("#search-validation").children().eq(1).children().text(response);
            $("#search").children().eq(1).children().text(response);
        }
    });
}


function start_search() {
    $("#search-validation").hide();
    show_window($("#search"))

    infos = $("#search").children()

    var source = new EventSource("/unmovis/loc_extraction/test.py");
    source.onmessage = function(event) {
        data = event.data;
        if (data == "CLOSE") {
            source.close();
        }
        else {
            var child;
            if (event.lastEventId == "dedup") child = 2;
            else if (event.lastEventId == "onLand") child = 3;
            else if (event.lastEventId == "farFetched") child = 4;
            else if (event.lastEventId == "outlier") child = 5; 
            infos.eq(child).children().text(data);
        }
    }
}


function abort_search() {
        $("#search-aborted").hide();
        $("#search-validation").hide();
        $(".overlay").hide();
        $("#choice-user").children().eq(1).click();
}


// Get the boat name and if the search is the first one or not (if it is the interface has to be displayed, and if not it just has to be re-initialised)
function get_informations(firstSearch, boatName) {
    dataFilePath = "../data/" + boatName + ".json";
    completeInfosFilePath = "../data/" + boatName + ".csv";
    simpleInfosFilePath = "../data/" + boatName + "_simplified.json";

    var data = JSON.parse(readFile(dataFilePath));
    if (UrlExists(completeInfosFilePath))
        var completeInfos = csvToJson(readFile(completeInfosFilePath));
    else
        var completeInfos = {};
    if (UrlExists(simpleInfosFilePath))
        var simpleInfos = eval('(' + readFile(simpleInfosFilePath) + ')'); 
    else
        var simpleInfos = {};

    document.title = "Visualisation of " + boatName + " informations";

    var trustTable = determine_users_trust(data);

    limitDates = initialize(data, trustTable);
    display_date_choice(limitDates[0], limitDates[1]);
    if (firstSearch) display_interface(simpleInfos);
    display_boat_infos(simpleInfos, completeInfos);
}


// Give to each user a trust ratio according to the filtering of all the pictures he has posted
function determine_users_trust(listPics) {
    usersTable = {};

    for (var i=0 ; i<listPics.length ; i++) {
        var picInfos = listPics[i];
        userID = picInfos[1]["userID"];
        if ((userID in usersTable) == false) usersTable[userID] = ["", picInfos[1]["username"]];
        if (picInfos[picInfos.length-1].toString() == "0,0,0") usersTable[userID][0] += "1";
        else usersTable[userID][0] += "0"
    }

    for (var user in usersTable) {
        var trust = usersTable[user][0];
        var nbPicTotal = trust.length;
        var nbNotFilteredLoc = trust.split("1").length - 1;
        usersTable[user][0] = Math.round((nbNotFilteredLoc/nbPicTotal)*10)/10;
    }

    return usersTable
}
