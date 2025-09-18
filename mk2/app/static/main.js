window.downloadInput = function() {
    const data = window.input_json;
    const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'input.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

window.uploadInputFile = function(input) {
    const inputFields = window.input_fields;
    console.log('uploadInputFile called', input);
    if (!input.files || !input.files[0]) {
        console.log('No file selected');
        return;
    }
    const file = input.files[0];
    console.log('Selected file:', file);
    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            console.log('File loaded, content:', e.target.result);
            const json = JSON.parse(e.target.result);
            console.log('Parsed JSON:', json);
            let missing = [];
            inputFields.forEach(function(field) {
                if (json.hasOwnProperty(field)) {
                    const el = document.getElementsByName(field)[0];
                    if (el) {
                        el.value = json[field];
                        console.log('Set value for', field, 'to', json[field]);
                    } else {
                        console.log('No input element found for', field);
                    }
                } else {
                    missing.push(field);
                }
            });
            if (missing.length > 0) {
                alert('Følgende felter mangler i filen: ' + missing.join(', '));
            }
        } catch (err) {
            alert('Kunne ikke lese JSON: ' + err);
            console.log('JSON parse error:', err);
        }
        input.value = '';
    };
    reader.readAsText(file);
}
