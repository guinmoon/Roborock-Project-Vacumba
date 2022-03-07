


var joystick = nipplejs.create({
    zone: document.getElementById("right_joystic"),
    mode: "static",
    // mode: "dynamic",
    position: { right: "20%", top: "70%" },
    color: "green",
    size: 200
});

var Pad_Data = {};
var Video_H = 720;
var Video_W = 1280;

function prepare_pad_data() { }

function bindNipple() {
    joystick
        .on("start end", function (evt, data) {
            console.log(evt.type);
            console.log(data);
            if (evt.type == "end") {
                Pad_Data.frontPosition.x = 0;
                Pad_Data.frontPosition.y = 0;
                $.post("/move_pad", {
                    pad_data: JSON.stringify(Pad_Data)
                });
                Pad_Data = {};
            }
        })
        .on("move", function (evt, data) {
            Pad_Data = {
                force: data.force,
                frontPosition: data.instance.frontPosition
            };
        })
        // .on(
        //     "dir:up plain:up dir:left plain:left dir:down " +
        //         "plain:down dir:right plain:right",
        //     function(evt, data) {

        //     }
        // )
        .on("pressure", function (evt, data) { });
}

let post_pad_data_timer = setInterval(() => {
    if (Object.keys(Pad_Data).length !== 0) {
        $.post("/move_pad", {
            pad_data: JSON.stringify(Pad_Data)
        });
    }
}, 100);

var resize = function () {
    var a = 1;
    var wH = $(window).height();
    var wW = $(window).width();
    if (wH <= wW) {
        vH = wH - 5
        $("#bg_img").css("height", vH + "px");
    } else {
        vW = wW - 5
        $("#bg_img").css("width", vW + "px");
    }

    // console.log();
};


function start_bot() {
    $.post("/action", {
        action: "start_bot"
    });
}

function stop_bot() {
    $.post("/action", {
        action: "stop_bot"
    });
}

function home_bot() {
    $.post("/action", {
        action: "home_bot"
    });
}

window.onresize = function (event) {
    resize();
};

// function isFullScreen()
// {
//     return (document.fullScreenElement && document.fullScreenElement !== null)
//          || document.mozFullScreen
//          || document.webkitIsFullScreen;
// }


// function requestFullScreen(element)
// {
//     if (element.requestFullscreen)
//         element.requestFullscreen();
//     else if (element.msRequestFullscreen)
//         element.msRequestFullscreen();
//     else if (element.mozRequestFullScreen)
//         element.mozRequestFullScreen();
//     else if (element.webkitRequestFullscreen)
//         element.webkitRequestFullscreen();
// }

// function exitFullScreen()
// {
//     if (document.exitFullscreen)
//         document.exitFullscreen();
//     else if (document.msExitFullscreen)
//         document.msExitFullscreen();
//     else if (document.mozCancelFullScreen)
//         document.mozCancelFullScreen();
//     else if (document.webkitExitFullscreen)
//         document.webkitExitFullscreen();
// }

// function toggleFullScreen(element)
// {
//     if (isFullScreen())
//         exitFullScreen();
//     else
//         requestFullScreen(element || document.documentElement);
// }

// var goFS = document.getElementById("full_screen");
//   goFS.addEventListener("click", function() {
//       document.body.requestFullscreen();
//       document.webkitRequestFullscreen()
//   }, false);

resize();
bindNipple();
