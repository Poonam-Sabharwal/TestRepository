$(function () {

    // Function to toggle the right sidebar
    function toggleRightSidebar() {
        $('body').toggleClass('control-sidebar-open');
    }

    // util function to get row id from tr row
    function get_dt_row_id($button, $dataTable) {
        tr = $button.closest('tr');
        row = $dataTable.row(tr);
        data = row.data()
        if (!data) {
            // main row is possibly collapsed so try parent approach
            tr = tr.prev();
            row = $dataTable.row(tr);
            data = row.data()
        }
        return data.DT_RowId;
    }

    // util function to get row id from tr row
    function get_company_name($button, $dataTable) {
        tr = $button.closest('tr');
        row = $dataTable.row(tr);
        data = row.data()
        if (!data) {
            // main row is possibly collapsed so try parent approach
            tr = tr.prev();
            row = $dataTable.row(tr);
            data = row.data()
        }
        return data.short_name;
    }

    function handle_activate_delete_toggle_button_action($button, $dataTable, $action) {
        row_id = get_dt_row_id($button, $dataTable)
        short_name = get_company_name($button, $dataTable)
        console.log("Toggle action '" + $action + "', triggered for row id: " + row_id)
        if ($action == "")
            $action_name
        $.post("/citadel/api/company_toggle_activate_delete",
            {
                company_id: row_id,
                action: $action,
            }).done(function (result, status, xhr) {
                $dataTable.ajax.reload(null, false)
                console.log("Toggle action '" + $action + "', completed for row id: " + row_id + " and table updated.")
                show_toast_notification("success", "Success!", "Toggle action '" + $action + "', completed for company '" + short_name + "'' and table updated.")
            }).fail(function (xhr, status, error) {
                //$("#dbData").html("Result: " + status + " " + error + " " + xhr.status + " " + xhr.statusText)
            });
    }

    function show_toast_notification(toast_type, title, msg) {
        toast_class = ""
        if (toast_type == "success") {
            toast_class = "bg-success"
        } else if (toast_type == "error") {
            toast_class = "bg-warning"
        } else {
            toast_class = "bg-info"
        }
        $(document).Toasts('create', {
            title: title,
            class: toast_class,
            autohide: true,
            delay: 2100,
            body: msg,
        })
    }

    $dtable = $('#companies_list_table').DataTable({
        serverSide: true,
        processing: true,
        stateSave: true,
        'serverMethod': 'post',
        'ajax': {
            'url': '/citadel/api/get_companies_data'
        },
        'columns': [
            { data: 'full_name', searchable: true },
            { data: 'short_name', searchable: true },
            { data: 'address_state_city_country_zip' },
            { data: 'is_active' },
            { data: 'is_deleted' },
            {
                data: null,
                render: function (data, type, row, meta) {
                    $is_active = data.is_active
                    $is_deleted = data.is_deleted
                    $button_group = '<div class="btn-group">' +
                        '       <button type="button" id="row-edit-button" class="btn btn-info btn-sm" ' +
                        '               data-toggle="tooltip" title="Click to \'Edit\' this company.">' +
                        '           <i class="fa fa-edit"></i>' +
                        '       </button>' +
                        '       &nbsp;&nbsp;'

                    // activate or deactive button
                    if ($is_active.toUpperCase() == "YES") {
                        $button_group += '       <button type="button" id="is-active-toggle-button" class="btn btn-warning btn-sm" ' +
                            '                               data-toggle="tooltip" title="Click to \'De-Activate\' this company." >' +
                            '                       <i class="fas fa-toggle-on fa-lg"></i>'
                    } else {
                        $button_group += '       <button type="button" id="is-active-toggle-button" class="btn btn-warning btn-sm" ' +
                            '                               data-toggle="tooltip" title="Click to \'Activate\' this company." >' +
                            '                       <i class="fas fa-toggle-off fa-lg"></i>'
                    }
                    $button_group += '      </button>'
                    $button_group += '       &nbsp;&nbsp;'
                    // delete or undelete button
                    if ($is_deleted.toUpperCase() == "YES") {
                        $button_group += '       <button type="button" id="is-deleted-toggle-button" class="btn btn-danger btn-sm" ' +
                            '                               data-toggle="tooltip" title="Click to \'Restore\' this company." >' +
                            '                       <i class="fas fa-trash-restore"></i>'
                    } else {
                        $button_group += '       <button type="button" id="is-deleted-toggle-button" class="btn btn-danger btn-sm" ' +
                            '                               data-toggle="tooltip" title="Click to \'Soft Delete\' this company." >' +
                            '                       <i class="fas fa-trash"></i>'
                    }
                    $button_group += '   </button>'

                    return $button_group
                },
            },
        ],
        'lengthMenu': [
            [10, 20, 30, 50, 75],
            [10, 20, 30, 50, 75]
        ],
        'searching': true,
        'sort': false,
        'info': true,
        'autoWidth': false,
        'responsive': true,
    });

    // Logic to enable type ahead search after alteast 3 characters or
    // if the user hits enter
    $(".dataTables_filter input")
        .unbind() // Unbind previous default bindings
        .bind("input", function (e) { // Bind our desired behavior
            // If the length is 3 or more characters, or the user pressed ENTER, search
            if (this.value.length >= 3 || e.keyCode == 13) {
                // Call the API search function
                $dtable.search(this.value).draw();
            }
            // Ensure we clear the search if they backspace far enough
            if (this.value == "") {
                $dtable.search("").draw();
            }
            return;
        });

    // handle the row edit button click
    $('#companies_list_table tbody').on('click', 'button#row-edit-button', function () {
        row_id = get_dt_row_id($(this), $dtable);
        console.log("row-edit-button, selected row id: " + row_id)
        window.location.href = "/citadel/admin_add_update_company?row_id=" + row_id;
    });

    // handle the activate/deactivate button click
    $('#companies_list_table tbody').on('click', 'button#is-active-toggle-button', function () {
        handle_activate_delete_toggle_button_action($(this), $dtable, "is_active",)
    });

    // handle the delete/restore button click
    $('#companies_list_table tbody').on('click', 'button#is-deleted-toggle-button', function () {
        handle_activate_delete_toggle_button_action($(this), $dtable, "is_deleted")
    });

    // enable tooltips on action buttons
    $('[data-toggle="tooltip"]').tooltip();

    $('.toastsDefaultAutohide').click(function () {
        $(document).Toasts('create', {
            title: 'Toast Title',
            class: 'bg-success',
            autohide: true,
            delay: 1000,
            body: 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr.'
        })
    });

    // Event handler for the right sidebar toggle button
    $('#rightSidebarToggle').on('click', function (e) {
        e.preventDefault();
        toggleRightSidebar();
    });

    // Close the right sidebar when clicking outside of it
    $(".content-wrapper").on('click', function (e) {
        if (
            $(e.target).closest('.control-sidebar').length === 0 &&
            !$(e.target).is('#rightSidebarToggle')
        ) {
            if ($('body').hasClass('control-sidebar-open')) {
                toggleRightSidebar();
            }
        }
    });

    $('#clear_state').on('click', function (e) {
        $dtable.state.clear();
        window.location.reload();
    });

});

