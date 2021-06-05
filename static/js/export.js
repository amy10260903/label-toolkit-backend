function formatData(data, header, label) {
    let objArray = [];
    objArray.push(header);
    data.forEach((obj, id) => {
        let array = [];
        array.push(id);
        Object.keys(obj).forEach((key) => {
            array.push(obj[key]);
        });
        array.push(label);
        objArray.push(array);
    })
    return objArray;
}

function convertToCSV(objArray) {
    let str = '';
    objArray.forEach((array) => {
        let line = '';
        array.forEach((obj) => {
            if (line != '') line += ',';
            line += obj;
        });
        str += line + '\r\n';
    });
    return str;
}

function exportCSVFile(headers, data, label, fileTitle) {
    let items = formatData(data, headers, label);
    let csv = convertToCSV(items);
    let exportedFilename = fileTitle + '.csv' || 'export.csv';
    let blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    let link = document.createElement("a");
        if (link.download !== undefined) { // feature detection
            var url = URL.createObjectURL(blob);
            link.setAttribute("href", url);
            link.setAttribute("download", exportedFilename);
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
}

export {
    exportCSVFile,
}