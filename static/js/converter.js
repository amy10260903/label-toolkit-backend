function vwTOpx(value) {
    var w = window,
        d = document,
        e = d.documentElement,
        g = d.getElementsByTagName('body')[0],
        x = w.innerWidth || e.clientWidth || g.clientWidth,
        y = w.innerHeight|| e.clientHeight|| g.clientHeight;
    var result = (x*value)/100;
    return result;
}

function vhTOpx(value) {
    var w = window,
        d = document,
        e = d.documentElement,
        g = d.getElementsByTagName('body')[0],
        x = w.innerWidth || e.clientWidth || g.clientWidth,
        y = w.innerHeight|| e.clientHeight|| g.clientHeight;

    var result = (y*value)/100;
    return result;
}

function pxTOvw(value) {
    var w = window,
        d = document,
        e = d.documentElement,
        g = d.getElementsByTagName('body')[0],
        x = w.innerWidth || e.clientWidth || g.clientWidth,
        y = w.innerHeight|| e.clientHeight|| g.clientHeight;

    var result = (100*value)/x;
    return result;
}

function pxTOvh(value) {
    var w = window,
        d = document,
        e = d.documentElement,
        g = d.getElementsByTagName('body')[0],
        x = w.innerWidth || e.clientWidth || g.clientWidth,
        y = w.innerHeight|| e.clientHeight|| g.clientHeight;

    var result = (100*value)/y;
    return result;
}

function posTotime(value, length, unit='vw') {
    if (unit == 'vw') {
        return (parseFloat(value)/80) * length;
    } else if (unit == 'px') {
        return pxTOvw(parseFloat(value)/80) * length;
    }
}
export {
    vwTOpx,
    pxTOvw,
    posTotime,
}