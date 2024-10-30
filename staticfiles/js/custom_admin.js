// custom_admin.js

// You can initialize a date picker on the DateRangeFilter inputs
$(document).ready(function() {
    $(".date-range-filter input").datepicker({
        dateFormat: 'yy-mm-dd'  // Format to match Django's date format
    });
});
