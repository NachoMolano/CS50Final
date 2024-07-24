
document.getElementById('toggleSwitch').addEventListener('change', function() {
    var startTime = document.getElementById('startTime');
    var endTime = document.getElementById('endTime');

    if (this.checked) {
        startTime.disabled = true;
        endTime.disabled = true;
    } else {
        startTime.disabled = false;
        endTime.disabled = false;
    }
});

document.getElementById('startTime').addEventListener('input', function() {
    var startTime = this.value;
    document.getElementById('endTime').setAttribute('min', startTime);
});

document.getElementById('startDate').addEventListener('input', function() {
    var startTime = this.value;
    document.getElementById('endDate').setAttribute('min', startTime);
});

document.getElementById('endTime').addEventListener('input', function() {
    var startTime = document.getElementById('startTime').value;
    var startDate= document.getElementById('startDate');
    var endDate= document.getElementById('endDate');
    var endTime = this.value;
    if (endTime < startTime && (!endDate.value || endDate.value == startDate.value)) {
        alert(`End time must be later than start time. ${endDate.value}`);
        this.value = '';
    }
});

document.getElementById('addForm').addEventListener('submit', function(event) {
    // Update hidden inputs with the values of the corresponding inputs
    if (document.getElementById('startTime').disabled) {
        document.getElementById('startTime').disabled = false
        document.getElementById('endTime').disabled = false
        document.getElementById('hiddenAllDay').value = 'on'
    }
});