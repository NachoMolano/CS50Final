function stepper(btn, input_id) {
    let myInput = document.getElementById(input_id)
    let id = btn.getAttribute('id');
    let min = myInput.getAttribute('min');
    let max = myInput.getAttribute('max');
    let step = myInput.getAttribute('step');
    let val = myInput.getAttribute('value');
    let calcStep = (id == 'increment') ? (step*1) : (step * -1);
    let newValue = parseInt(val) + calcStep

    if (newValue >= min && newValue <= max) {
        myInput.setAttribute("value", newValue)
    }
    
}

function deletePercentage(criteria, criteria_id, subject) {
    let deleteForm = document.getElementById('deleteForm');
    let deleteText = document.getElementById('deleteText');

    deleteText.innerText = `Delete ${criteria}`
    deleteForm.setAttribute('action', `../delete/${subject}/${criteria_id}`)
}

function deleteSubject(subject, id) {
    let deleteForm = document.getElementById('deleteForm')
    let deleteText = document.getElementById('deleteText')

    deleteText.innerText = `Delete ${subject}`
    deleteForm.setAttribute('action', `../delete/${parseInt(id)}`)
}

function gradeUrl(subject, criteria) {
    let form = document.getElementById("gradeForm")

    form.setAttribute('action', `../gradeAdd/${subject}/${criteria}`)
}

$(document).ready(function() {
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]')
    const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl))

    var popoverContent = $('#popoverContent').html();

    $('#popoverButton').popover({
        html: true,
        content: popoverContent,
        placement: 'left', 
        template: '<div class="popover-dark" role="tooltip"></h3><div class="popover-body"></div></div>'
    });
    $('.popover-body').addClass('text-bg-dark')

    $('#popoverButton').on('shown.bs.popover', function () {
        var popoverId = $(this).attr('aria-describedby');
        var $popover = $('#' + popoverId);
        $popover.find('.popover-body').html(popoverContent);
    });

    $(document).on('click', function(e){
        var target = $(e.target);

        // Check if the click was outside the popover and button
        if (!target.closest('#popoverButton').length && !target.closest('.popover').length) {
            $('#popoverButton').popover('hide');
        }
    })
});

