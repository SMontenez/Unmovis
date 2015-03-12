var iconBase = " https://storage.googleapis.com/support-kms-prod/"

var icons = {
    correct: { icon: iconBase + "SNP_2752068_en_v0" },
    uncertain: { icon: iconBase + "SNP_2752125_en_v0" },
    onLand: { icon: iconBase + "SNP_2752129_en_v0" },
    impJourney: { icon: iconBase + "SNP_2752264_en_v0" },
    outlier: { icon: iconBase + "SNP_2752063_en_v0" },
};

var correctIcon = "http://dri1.img.digitalrivercontent.net/Storefront/Site/mscommon/cm/images/common_images/middle_blue_dot.gif"

var darkRed = "B00202";
var darkRedPin = "http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|" + darkRed
var filteredMarker = new google.maps.MarkerImage(darkRedPin,
        new google.maps.Size(21, 34),
        new google.maps.Point(0,0),
        new google.maps.Point(10, 34));

var green = "038C15";
var greenPin = "http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|" + green
var onLandMarker = new google.maps.MarkerImage(greenPin,
        new google.maps.Size(21, 34),
        new google.maps.Point(0,0),
        new google.maps.Point(10, 34));

var orange = "FF6600";
var orangePin = "http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|" + orange
var outlierMarker = new google.maps.MarkerImage(orangePin,
        new google.maps.Size(21, 34),
        new google.maps.Point(0,0),
        new google.maps.Point(10, 34));

var red = "FF0000";
var redPin = "http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|" + red
var impJourneyMarker = new google.maps.MarkerImage(redPin,
        new google.maps.Size(21, 34),
        new google.maps.Point(0,0),
        new google.maps.Point(10, 34));
