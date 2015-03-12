// Return the content of the file located at 
// fileUrl adress by using an Ajax request
function readFile(fileUrl){
    var request = new XMLHttpRequest();
    request.open('GET', fileUrl, false);
    request.send(null);

    return request.responseText;
}


function processUrl() {
    var params = {};
    var parameters = location.search.substring(1).split("&");
    if (parameters.length > 1) {
        for (i in parameters) {
            parameter = unescape(parameters[i]).split("=");
            params[parameter[0]] = parameter[1];
        }
    }
    else params = "";

    return params;
}


function intSort(a,b) {return a-b;}
function firstElementIntInvSort(a,b) {return b[0]-a[0]}


function remove_from_array(array, elt) {
    indElt = 0
        for (var i=0 ; i<array.length ; i++) {
            if (array[i] == elt) {
                indElt = i;
                break;
            }
        }
    return array.splice(i, 1);
}


function csvToJson(csvString) {
    result = {};
    csvLines = csvString.split("\n");
    for (var i=0 ; i<csvLines.length-1 ; i++) {
        csvLines[i] = csvLines[i].split(";");
        csvLines[i].pop();;
    }
    indexSite = csvLines[0].indexOf("Site");
    for (var index=0 ; index<csvLines[0].length ; index++) {
        subResult = {};
        info = csvLines[0][index];
        if (info != "Site" && info != "Name") {
            for (var i=1 ; i<csvLines.length ; i++) {
                line = csvLines[i];
                subResult[line[indexSite]] = line[index];
            }
            result[info] = subResult;
        }
    }
    return result;
}


function capitalize(string) {
    return string.replace(/(?:^|\s)\S/g, function(a) {return a.toUpperCase();});
}


function daysDiff(d1, d2) {
    var ms = 1000 * 60 * 60 * 24;

    var day1 = Date.UTC(d1.getFullYear(), d1.getMonth(), d1.getDate());
    var day2 = Date.UTC(d2.getFullYear(), d2.getMonth(), d2.getDate());

    return Math.floor((day2 - day1) / ms);
}    


// Return the diff in hours between the two dates in Flickr format
// ("yyyy-mm-dd hh:MM:ss")
function dateDiff(d1, d2){
    var date1 = new Date(d1);
    var date2 = new Date(d2);
    var diff = Math.abs((date1-date2)/3600000)

    return Math.floor(diff*10)/10 
}

function distance(loc1, loc2) {
    var pi = Math.PI;

    var lat1 = loc1.lat()*(pi/180);
    var lon1 = loc1.lng()*(pi/180);
    var lat2 = loc2.lat()*(pi/180);
    var lon2 = loc2.lng()*(pi/180);

    var a = Math.sin(lat1)*Math.sin(lat2) + Math.cos(lat1)*Math.cos(lat2)*Math.     cos(lon2-lon1);
    if (a>1) a=1;
    else if (a<-1)  a=-1;

    a = Math.abs(6371*Math.acos(a));

    return Math.floor(a)
}


// If there are several max speed, return the average
function moySpeed(speed) {
    var speeds = speed.split(" / ");
    var tot = 0;
    var num = speeds.length;
    for (i=0 ; i<num ; i++) {
        tot += parseFloat(speeds[i]);
    }

    return Math.floor((tot/num)*10)/10
}


function UrlExists(url) {
    var http = new XMLHttpRequest();
    http.open('HEAD', url, false);
    http.send();
    return http.status != 404;
}
